import os
from fastapi import APIRouter, HTTPException, status
from app import schemas
from app.database import rebuild_database_session, ensure_tables_created

router = APIRouter(
    prefix="/config",
    tags=["Configuration"]
)

ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

@router.put("/database", response_model=schemas.DatabaseConfigResponse)
def update_database_config(config_update: schemas.DatabaseConfigUpdate):
    """
    Update database connection details in the .env file and dynamically apply the changes
    to the running SQLAlchemy engine pool.
    """
    # Initialize env file if it doesn't exist
    if not os.path.exists(ENV_FILE_PATH):
        try:
            with open(ENV_FILE_PATH, "w") as f:
                pass
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize .env file: {str(e)}"
            )

    # Read current env variables
    current_env = {}
    try:
        with open(ENV_FILE_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    current_env[key.strip()] = val.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read .env file: {str(e)}"
        )

    # Filter out None values from the request payload
    update_data = config_update.model_dump(exclude_unset=True)

    # Update configurations
    for key, val in update_data.items():
        if val is not None:
            current_env[key] = str(val)

    # Write updated variables back to .env file in-place
    try:
        with open(ENV_FILE_PATH, "w") as f:
            for key, val in current_env.items():
                f.write(f"{key}={val}\n")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write updates to .env file: {str(e)}"
        )

    # Rebuild database engine session dynamically to apply new connection parameters
    try:
        rebuild_database_session()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration saved to .env, but connection pool re-initialization failed: {str(e)}"
        )

    # Auto-create tables in the newly connected database
    tables_ok, tables_msg = ensure_tables_created()

    # Mask password for safety in response
    pwd = current_env.get("PASSWORD", "")
    masked_pwd = "*" * len(pwd) if pwd else ""

    return schemas.DatabaseConfigResponse(
        ENGINE=current_env.get("ENGINE", ""),
        NAME=current_env.get("NAME", ""),
        USER=current_env.get("USER", ""),
        PASSWORD_MASKED=masked_pwd,
        HOST=current_env.get("HOST", ""),
        PORT=current_env.get("PORT", ""),
        DRIVER=current_env.get("DRIVER", ""),
        message="Database connection parameters updated successfully and applied dynamically.",
        tables_created=tables_ok,
        tables_message=tables_msg
    )
