from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/deleted-workmen",
    tags=["Deleted Workmen"]
)

@router.post("", response_model=schemas.DeletedWorkmenResponse, status_code=status.HTTP_201_CREATED)
def create_deleted_workman(deleted_workman: schemas.DeletedWorkmenCreate, db: Session = Depends(get_db)):
    """Create a new entry logging a deleted workman."""
    return crud.create_deleted_workman(db=db, deleted_workman=deleted_workman)

@router.get("", response_model=List[schemas.DeletedWorkmenResponse])
def read_deleted_workmen(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all deleted workmen logs with pagination."""
    return crud.get_deleted_workmen(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=schemas.DeletedWorkmenResponse)
def read_deleted_workman(id: int, db: Session = Depends(get_db)):
    """Get a specific deleted workman log by auto-increment ID."""
    db_deleted = crud.get_deleted_workman(db, id=id)
    if db_deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deleted workman record with ID {id} not found."
        )
    return db_deleted
