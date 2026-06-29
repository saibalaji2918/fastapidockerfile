import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Declarative base class
Base = declarative_base()

def create_db_engine():
    # Force reload environment variables from the .env file
    load_dotenv(override=True)
    
    db_user = os.getenv("USER", "sa")
    db_password = os.getenv("PASSWORD", "")
    db_host = os.getenv("HOST", "localhost")
    db_port = os.getenv("PORT", "1433")
    db_name = os.getenv("NAME", "")
    db_driver = os.getenv("DRIVER", "ODBC Driver 17 for SQL Server")
    
    # URL-encode the password and driver to handle special characters like '@'
    encoded_password = urllib.parse.quote_plus(db_password)
    encoded_driver = urllib.parse.quote_plus(db_driver)
    
    # Construct connection URL for SQL Server
    database_url = f"mssql+pyodbc://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}?driver={encoded_driver}"
    
    # Create SQLAlchemy engine with connection pooling config
    return create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
        pool_pre_ping=True
    )

# Initialize engine and SessionLocal session factory
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def ensure_tables_created():
    """Creates all defined tables in the currently connected database if they do not exist."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables verified/created successfully on the new database.")
        return True, "Tables created/verified successfully."
    except Exception as e:
        error_msg = f"Table creation failed: {e}"
        print(error_msg)
        return False, error_msg

def rebuild_database_session():
    """Closes old connections, configures SessionLocal with a new database engine, and ensures tables exist."""
    global engine, SessionLocal
    try:
        engine.dispose()
    except Exception as e:
        print(f"Error disposing old engine: {e}")

    engine = create_db_engine()
    SessionLocal.configure(bind=engine)
    print("Database connection engine successfully rebuilt with new configurations.")

    # Automatically create tables in the new database
    ensure_tables_created()

# Dependency to get db session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
