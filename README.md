# FastAPI SQL Server Service — OCM-4073

A FastAPI backend integrated with Microsoft SQL Server for managing Workmen & Deleted Workmen records.

---

## 🚀 One-Click Deployment (Docker)

No Python, no pip, no venv needed. Just Docker.

### ✅ Windows Server / Windows PC

> Requires: Windows 10/11 or Windows Server 2019+

1. Extract the ZIP file
2. Edit `.env` with your database credentials (optional — can be changed via API later)
3. Right-click `run.bat` → **Run as Administrator**

The script will automatically:
- Check for administrator privileges
- Install Docker Desktop (via `winget`) if not installed
- Verify Docker daemon is running
- Set folder permissions
- Build the Docker image (installs all Python dependencies + ODBC Driver 17)
- Start the server
- Run a health check to confirm Uvicorn is running

---

### ✅ Linux Server (Ubuntu / Debian / CentOS / RHEL / Fedora)

> Requires: Any modern Linux with `curl` and `sudo` access

```bash
# After extracting the ZIP:
chmod +x run.sh && ./run.sh
```

The script will automatically:
- Detect the Linux distribution (Ubuntu/Debian/CentOS/RHEL/Fedora)
- Install Docker CE & Docker Compose if not present
- Add your user to the `docker` group
- Set proper file permissions (`.env` protected at 600)
- Build the Docker image
- Start the server in detached (background) mode
- Run a health check against the Uvicorn endpoint

---

## 🔧 Configuration — `.env` File

Edit this file before running, or use the **Config API** to update it while the server is running:

```env
ENGINE=mssql
NAME=your_database_name
USER=sa
PASSWORD=your_password
HOST=10.10.20.243
PORT=1433
DRIVER=ODBC Driver 17 for SQL Server
```

> ⚠️ If your SQL Server is running on the host machine (not a remote server), use `host.docker.internal` instead of `localhost` for the `HOST` value.

---

## 🔄 Dynamic Database Config Update (No Restart Required)

You can update the database connection live via the API:

```http
PUT http://localhost:8000/config/database
Content-Type: application/json

{
  "HOST": "10.10.20.244",
  "NAME": "new_database",
  "USER": "sa",
  "PASSWORD": "NewPassword@123"
}
```

The server will:
1. Update the `.env` file on disk
2. Rebuild the SQLAlchemy connection pool
3. **Auto-create tables** in the new database
4. Return a response confirming tables were created

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check / welcome |
| GET | `/docs` | Swagger UI (interactive API docs) |
| GET | `/redoc` | ReDoc documentation |
| POST | `/workmen` | Create a new workman |
| GET | `/workmen` | List all workmen |
| GET | `/workmen/{id}` | Get workman by ID |
| PUT | `/workmen/{id}` | Update workman |
| DELETE | `/workmen/{id}` | Delete workman |
| POST | `/deleted-workmen` | Log a deleted workman |
| GET | `/deleted-workmen` | List all deleted workmen |
| GET | `/deleted-workmen/{id}` | Get deleted workman by ID |
| PUT | `/config/database` | Update DB connection config (live) |

---

## 🗄️ Database Tables

### `dbo.Korba_WorkmenMaster`
| Column | Type |
|--------|------|
| Workman_ID | INT (PK) |
| Work_ID | INT |
| Proj_Code | VARCHAR(10) |
| Name | VARCHAR(50) |
| Surname | VARCHAR(50) |
| GatePassIssueDate | DATETIME |
| GatePassValidFrom | DATETIME |
| GatePassValidUpto | DATETIME |
| last_update_date | DATETIME |
| Record_Disabled | BIT |
| Record_Creation_Date | DATETIME |

### `dbo.Korba_DeletedWorkmen`
| Column | Type |
|--------|------|
| ID | INT (IDENTITY PK) |
| Workman_ID | INT |
| Proj_Code | VARCHAR(10) |
| Status | VARCHAR(7) |
| Action_Date | DATETIME |

---

## 📁 Project Structure

```
OCM-4073/
├── app/
│   ├── main.py          ← FastAPI app entry point
│   ├── database.py      ← SQLAlchemy engine, session, table creation
│   ├── models.py        ← SQLAlchemy ORM models
│   ├── schemas.py       ← Pydantic request/response schemas
│   ├── crud.py          ← Database CRUD operations
│   └── routers/
│       ├── workmen.py        ← Workmen CRUD endpoints
│       ├── deleted_workmen.py← Deleted workmen endpoints
│       └── config.py         ← DB config update endpoint
├── tests/
│   └── test_main.py     ← Pytest unit tests (SQLite in-memory)
├── Dockerfile           ← Container build (Python + ODBC Driver 17)
├── docker-compose.yml   ← Service orchestration + .env volume mount
├── .dockerignore        ← Excludes .venv, __pycache__, etc.
├── .env                 ← Database connection credentials
├── requirements.txt     ← Python dependencies
├── run.bat              ← Windows one-click bootstrap script
└── run.sh               ← Linux one-click bootstrap script
```

---

## 🛠️ Useful Docker Commands

```bash
# View real-time application logs
docker compose logs -f

# Stop the running service
docker compose down

# Restart the service
docker compose restart

# Rebuild and restart (after code changes)
docker compose up --build -d
```

---

## ✅ Running Tests (Development Only)

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1     # Windows PowerShell
source .venv/bin/activate       # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest -v
```

# for development mode in windows

#RUN uvicorn app.main:app --reload"# fastapidockerfile" 
