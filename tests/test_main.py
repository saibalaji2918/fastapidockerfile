# pyrefly: ignore [missing-import]
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

# Create in-memory SQLite engine for tests with StaticPool to share connection
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLite does not support schemas like 'dbo'. We dynamically strip schemas before creating tables.
@event.listens_for(Base.metadata, "before_create")
def remove_schemas(target, connection, **kw):
    for table in target.tables.values():
        table.schema = None

# Create tables in the SQLite memory DB
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the database dependency in FastAPI
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to FastAPI Workmen Management API"

def test_create_workman():
    payload = {
        "Workman_ID": 12345,
        "Work_ID": 999,
        "Proj_Code": "P101",
        "Name": "John",
        "Surname": "Doe",
        "GatePassIssueDate": "2026-06-04T00:00:00",
        "GatePassValidFrom": "2026-06-04T08:00:00",
        "GatePassValidUpto": "2026-06-04T18:00:00",
        "Record_Disabled": False
    }
    response = client.post("/workmen", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["Workman_ID"] == 12345
    assert data["Name"] == "John"

def test_get_workman():
    response = client.get("/workmen/12345")
    assert response.status_code == 200
    assert response.json()["Surname"] == "Doe"

def test_get_workman_not_found():
    response = client.get("/workmen/99999")
    assert response.status_code == 404

def test_get_all_workmen():
    response = client.get("/workmen")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_update_workman():
    payload = {
        "Name": "Johnny"
    }
    response = client.put("/workmen/12345", json=payload)
    assert response.status_code == 200
    assert response.json()["Name"] == "Johnny"

def test_delete_workman():
    response = client.delete("/workmen/12345")
    assert response.status_code == 200
    
    # Verify it is deleted
    response = client.get("/workmen/12345")
    assert response.status_code == 404

def test_create_deleted_workman():
    payload = {
        "ID": 1,
        "Workman_ID": 12345,
        "Proj_Code": "P101",
        "Status": "Term",
        "Action_Date": "2026-06-04T12:00:00"
    }
    response = client.post("/deleted-workmen", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ID"] == 1
    assert data["Status"] == "Term"

def test_get_deleted_workmen():
    response = client.get("/deleted-workmen")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_get_deleted_workman_by_id():
    response = client.get("/deleted-workmen/1")
    assert response.status_code == 200
    assert response.json()["Workman_ID"] == 12345

def test_get_deleted_workman_not_found():
    response = client.get("/deleted-workmen/999")
    assert response.status_code == 404

def test_update_database_config(tmp_path):
    import app.routers.config as config_module

    # Back up the original path
    original_env_path = config_module.ENV_FILE_PATH

    # Setup temporary .env file
    temp_env = tmp_path / ".env.test"
    temp_env.write_text("ENGINE=sql_server\nHOST=localhost\n")
    config_module.ENV_FILE_PATH = str(temp_env)

    try:
        payload = {
            "ENGINE": "sql_server_test",
            "NAME": "test_db",
            "USER": "sa",
            "PASSWORD": "SecretPassword",
            "HOST": "127.0.0.1",
            "PORT": "1433",
            "DRIVER": "ODBC Driver 17 for SQL Server"
        }

        import unittest.mock as mock
        with mock.patch("app.routers.config.rebuild_database_session") as mock_rebuild, \
             mock.patch("app.routers.config.ensure_tables_created", return_value=(True, "Tables created/verified successfully.")) as mock_tables:
            response = client.put("/config/database", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["ENGINE"] == "sql_server_test"
            assert data["NAME"] == "test_db"
            assert data["PASSWORD_MASKED"] == "**************"
            assert data["HOST"] == "127.0.0.1"
            assert data["tables_created"] is True
            assert "Tables" in data["tables_message"]
            mock_rebuild.assert_called_once()
            mock_tables.assert_called_once()

            # Verify the written file content
            content = temp_env.read_text()
            assert "ENGINE=sql_server_test" in content
            assert "NAME=test_db" in content
            assert "PASSWORD=SecretPassword" in content
    finally:
        # Restore the original path
        config_module.ENV_FILE_PATH = original_env_path

