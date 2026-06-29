from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/workmen",
    tags=["Workmen Master"]
)

@router.post("", response_model=schemas.WorkmenMasterResponse, status_code=status.HTTP_201_CREATED)
def create_workman(workman: schemas.WorkmenMasterCreate, db: Session = Depends(get_db)):
    """Create a new workman record. Raises 400 if Workman_ID already exists."""
    db_workman = crud.get_workman(db, workman_id=workman.Workman_ID)
    if db_workman:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workman with ID '{workman.Workman_ID}' already exists."
        )
    return crud.create_workman(db=db, workman=workman)

@router.get("", response_model=List[schemas.WorkmenMasterResponse])
def read_workmen(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all workmen records with pagination."""
    return crud.get_workmen(db, skip=skip, limit=limit)

@router.get("/{workman_id}", response_model=schemas.WorkmenMasterResponse)
def read_workman(workman_id: int, db: Session = Depends(get_db)):
    """Get a specific workman record by Workman_ID."""
    db_workman = crud.get_workman(db, workman_id=workman_id)
    if db_workman is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workman with ID '{workman_id}' not found."
        )
    return db_workman

@router.put("/{workman_id}", response_model=schemas.WorkmenMasterResponse)
def update_workman(workman_id: int, workman: schemas.WorkmenMasterUpdate, db: Session = Depends(get_db)):
    """Update field values for a specific workman record."""
    db_workman = crud.update_workman(db, workman_id=workman_id, workman_update=workman)
    if db_workman is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workman with ID '{workman_id}' not found."
        )
    return db_workman

@router.delete("/{workman_id}", response_model=schemas.WorkmenMasterResponse)
def delete_workman(workman_id: int, db: Session = Depends(get_db)):
    """Delete a specific workman record."""
    db_workman = crud.delete_workman(db, workman_id=workman_id)
    if db_workman is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workman with ID '{workman_id}' not found."
        )
    return db_workman
