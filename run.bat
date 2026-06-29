@echo off
setlocal EnableDelayedExpansion
:: =============================================================================
::  OCM-4073 FastAPI Service - Windows Bootstrap Script
::  Usage (after extracting zip): Double-click run.bat
:: =============================================================================

title FastAPI SQL Server Service - Windows Deployer

echo.
echo ================================================
echo   FastAPI SQL Server Service - Windows Deployer
echo ================================================
echo.

:: ── 1. CHECK FOR ADMIN PRIVILEGES ─────────────────────────────────────────────
echo [1/5] Checking administrator privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [!] This script requires administrator privileges.
    echo     Right-click run.bat and select "Run as administrator".
    echo.
    pause
    exit /b 1
)
echo       OK - Running as administrator.

:: ── 2. CHECK / INSTALL DOCKER ─────────────────────────────────────────────────
echo.
echo [2/5] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('docker --version') do echo       Already installed: %%i
    goto :docker_ready
)

echo       Docker not found. Attempting to install via winget...
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo       Using winget to install Docker Desktop...
    winget install -e --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] winget installation failed. Please install Docker Desktop manually:
        echo         https://www.docker.com/products/docker-desktop/
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [!] Docker Desktop installed. Please:
    echo     1. Start Docker Desktop from the Start Menu
    echo     2. Wait for Docker to fully start (whale icon in system tray)
    echo     3. Run this script again
    echo.
    pause
    exit /b 0
) else (
    echo.
    echo [ERROR] winget not available. Please install Docker Desktop manually:
    echo         https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

:docker_ready

:: ── 3. VERIFY DOCKER DAEMON IS RUNNING ────────────────────────────────────────
echo.
echo [3/5] Verifying Docker daemon is running...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Docker is installed but not running.
    echo         Please start Docker Desktop and wait for it to fully initialize.
    echo         (Look for the whale icon in the Windows system tray)
    echo.
    pause
    exit /b 1
)
echo       Docker daemon is running.

:: ── 4. SET FOLDER PERMISSIONS ─────────────────────────────────────────────────
echo.
echo [4/5] Setting folder permissions...
set SCRIPT_DIR=%~dp0
icacls "%SCRIPT_DIR%" /grant "%USERNAME%":F /T /Q
if %errorlevel% equ 0 (
    echo       Permissions set on: %SCRIPT_DIR%
) else (
    echo [WARN] Could not set permissions. Continuing...
)

:: ── 5. BUILD AND LAUNCH VIA DOCKER COMPOSE ────────────────────────────────────
echo.
echo [5/5] Building image and starting service...
cd /d "%SCRIPT_DIR%"

docker compose version >nul 2>&1
if %errorlevel% equ 0 (
    docker compose up --build -d
) else (
    docker-compose up --build -d
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] docker compose failed. Check the output above for details.
    pause
    exit /b 1
)

:: ── 6. HEALTH CHECK — VALIDATE UVICORN IS RUNNING ────────────────────────────
echo.
echo Waiting for server to start...
set MAX_RETRIES=15
set COUNT=0

:health_loop
set /a COUNT+=1
if %COUNT% gtr %MAX_RETRIES% (
    echo.
    echo [ERROR] Server did not respond after %MAX_RETRIES% retries.
    echo         Check logs with: docker compose logs -f
    pause
    exit /b 1
)

curl -s -o nul -w "%%{http_code}" http://localhost:8000/ 2>nul | findstr /C:"200" >nul 2>&1
if %errorlevel% equ 0 goto :server_up

echo       Retrying... (%COUNT%/%MAX_RETRIES%)
timeout /t 3 /nobreak >nul
goto :health_loop

:server_up
echo.
echo ================================================
echo   ^>^>  Service is UP and HEALTHY!
echo.
echo   Swagger UI : http://localhost:8000/docs
echo   ReDoc      : http://localhost:8000/redoc
echo   Health     : http://localhost:8000/
echo.
echo   View logs  : docker compose logs -f
echo   Stop       : docker compose down
echo ================================================
echo.

pause
