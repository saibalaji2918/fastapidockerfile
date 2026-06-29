#!/bin/bash
# =============================================================================
#  OCM-4073 FastAPI Service - Linux Bootstrap Script
#  Usage (after extracting zip):
#    chmod +x run.sh && ./run.sh
# =============================================================================

set -e

BLUE='\033[1;34m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m' # No Color

BANNER="${BLUE}
================================================
  FastAPI SQL Server Service - Linux Deployer
================================================${NC}"

echo -e "$BANNER"
echo ""

# ── 1. DETECT OS ─────────────────────────────────────────────────────────────
echo -e "${YELLOW}[1/6] Detecting operating system...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    OS_LIKE=$ID_LIKE
else
    echo -e "${RED}[ERROR] Cannot detect OS. /etc/os-release not found.${NC}"
    exit 1
fi
echo -e "       Detected OS: ${GREEN}$PRETTY_NAME${NC}"

# ── 2. INSTALL DOCKER (if not present) ───────────────────────────────────────
echo -e "${YELLOW}[2/6] Checking Docker installation...${NC}"
if command -v docker &>/dev/null; then
    DOCKER_VER=$(docker --version)
    echo -e "       Docker already installed: ${GREEN}$DOCKER_VER${NC}"
else
    echo -e "       Docker not found. Installing Docker..."
    case "$OS" in
        ubuntu|debian|linuxmint)
            sudo apt-get update -y
            sudo apt-get install -y ca-certificates curl gnupg lsb-release
            sudo install -m 0755 -d /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/${OS}/gpg | \
                sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            sudo chmod a+r /etc/apt/keyrings/docker.gpg
            echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
                https://download.docker.com/linux/${OS} $(lsb_release -cs) stable" | \
                sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update -y
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
        centos|rhel|fedora|rocky|almalinux)
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
        *)
            echo -e "${RED}[ERROR] Unsupported OS: $OS. Please install Docker manually.${NC}"
            echo "        Visit: https://docs.docker.com/engine/install/"
            exit 1
            ;;
    esac

    # Start and enable Docker service
    sudo systemctl start docker
    sudo systemctl enable docker
    echo -e "       ${GREEN}Docker installed successfully.${NC}"
fi

# ── 3. ADD CURRENT USER TO docker GROUP (avoids sudo for docker commands) ────
echo -e "${YELLOW}[3/6] Checking docker group membership...${NC}"
if groups "$USER" | grep -q "\bdocker\b"; then
    echo -e "       ${GREEN}User '$USER' is already in the docker group.${NC}"
else
    echo -e "       Adding '$USER' to docker group..."
    sudo usermod -aG docker "$USER"
    # Use newgrp to apply group within this session without needing re-login
    echo -e "       ${GREEN}Done. Permissions applied for this session.${NC}"
fi

# ── 4. CHECK / INSTALL DOCKER COMPOSE ────────────────────────────────────────
echo -e "${YELLOW}[4/6] Checking Docker Compose...${NC}"
if docker compose version &>/dev/null; then
    COMPOSE_CMD="docker compose"
    echo -e "       ${GREEN}Docker Compose (plugin) available.${NC}"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
    echo -e "       ${GREEN}docker-compose (standalone) available.${NC}"
else
    echo -e "       Installing Docker Compose standalone..."
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
    sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    COMPOSE_CMD="docker-compose"
    echo -e "       ${GREEN}Docker Compose installed: $COMPOSE_VERSION${NC}"
fi

# ── 5. SET FOLDER PERMISSIONS ─────────────────────────────────────────────────
echo -e "${YELLOW}[5/6] Setting folder permissions...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sudo chown -R "$USER":"$USER" "$SCRIPT_DIR"
chmod -R 755 "$SCRIPT_DIR"
chmod 600 "$SCRIPT_DIR/.env" 2>/dev/null || true   # Protect .env (read by owner only)
echo -e "       ${GREEN}Permissions set on: $SCRIPT_DIR${NC}"

# ── 6. BUILD AND LAUNCH VIA DOCKER COMPOSE ────────────────────────────────────
echo -e "${YELLOW}[6/6] Building image and starting service...${NC}"
cd "$SCRIPT_DIR"
sg docker -c "$COMPOSE_CMD up --build -d"

# ── 7. HEALTH CHECK — VALIDATE UVICORN IS RUNNING ────────────────────────────
echo ""
echo -e "${YELLOW}Waiting for server to start...${NC}"
MAX_RETRIES=15
COUNT=0
until curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200"; do
    COUNT=$((COUNT + 1))
    if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
        echo -e "${RED}[ERROR] Server did not start within expected time.${NC}"
        echo "        Check logs with:  $COMPOSE_CMD logs -f"
        exit 1
    fi
    echo -e "       Retrying... ($COUNT/$MAX_RETRIES)"
    sleep 3
done

echo ""
echo -e "${GREEN}================================================"
echo -e "  ✅  Service is UP and HEALTHY!"
echo -e ""
echo -e "  🌐  Swagger UI : http://localhost:8000/docs"
echo -e "  📋  ReDoc      : http://localhost:8000/redoc"
echo -e "  ❤️   Health     : http://localhost:8000/"
echo -e ""
echo -e "  📄  View logs  : $COMPOSE_CMD logs -f"
echo -e "  🛑  Stop       : $COMPOSE_CMD down"
echo -e "================================================${NC}"
echo ""
