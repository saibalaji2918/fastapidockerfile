from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import workmen, deleted_workmen, config

# Create database tables dynamically if they do not exist
# Note: In production, database migrations (e.g. via Alembic) are recommended.
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    # We log the exception but allow server to start, in case DB is not yet available at startup
    print(f"Database table creation failed/skipped: {e}")

# Initialize FastAPI App
app = FastAPI(
    title="FastAPI SQL Server Service",
    description="Development server setup with FastAPI and SQL Server for managing Workmen & Deleted Workmen.",
    version="1.0.0",
)

# Set up CORS middleware for dev client compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workmen.router)
app.include_router(deleted_workmen.router)
app.include_router(config.router)

@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to FastAPI Workmen Management API",
        "swagger_ui": "/docs",
        "redoc": "/redoc"
    }
