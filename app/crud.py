from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime

# --- Korba_WorkmenMaster CRUD ---

def get_workman(db: Session, workman_id: int):
    """Retrieve a single workman record by Workman_ID."""
    return db.query(models.WorkmenMaster).filter(models.WorkmenMaster.Workman_ID == workman_id).first()

def get_workmen(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve multiple workmen records with pagination."""
    return db.query(models.WorkmenMaster).offset(skip).limit(limit).all()

def create_workman(db: Session, workman: schemas.WorkmenMasterCreate):
    """Create a new workman record."""
    db_workman = models.WorkmenMaster(
        Workman_ID=workman.Workman_ID,
        Work_ID=workman.Work_ID,
        Proj_Code=workman.Proj_Code,
        Name=workman.Name,
        Surname=workman.Surname,
        GatePassIssueDate=workman.GatePassIssueDate,
        GatePassValidFrom=workman.GatePassValidFrom,
        GatePassValidUpto=workman.GatePassValidUpto,
        last_update_date=workman.last_update_date or datetime.now(),
        Record_Disabled=workman.Record_Disabled,
        Record_Creation_Date=workman.Record_Creation_Date or datetime.now()
    )
    db.add(db_workman)
    db.commit()
    db.refresh(db_workman)
    return db_workman

def update_workman(db: Session, workman_id: int, workman_update: schemas.WorkmenMasterUpdate):
    """Update an existing workman record."""
    db_workman = get_workman(db, workman_id)
    if not db_workman:
        return None
    
    # Exclude unset fields so only passed fields are updated
    update_data = workman_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_workman, key, value)
    
    db_workman.last_update_date = datetime.now()
    db.commit()
    db.refresh(db_workman)
    return db_workman

def delete_workman(db: Session, workman_id: int):
    """Delete a workman record."""
    db_workman = get_workman(db, workman_id)
    if not db_workman:
        return None
    db.delete(db_workman)
    db.commit()
    return db_workman


# --- Korba_DeletedWorkmen CRUD ---

def get_deleted_workman(db: Session, id: int):
    """Retrieve a single deleted workman record by ID."""
    return db.query(models.DeletedWorkmen).filter(models.DeletedWorkmen.ID == id).first()

def get_deleted_workmen(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve multiple deleted workmen records with pagination."""
    return db.query(models.DeletedWorkmen).offset(skip).limit(limit).all()

def create_deleted_workman(db: Session, deleted_workman: schemas.DeletedWorkmenCreate):
    """Create a new record in deleted workmen log."""
    db_deleted = models.DeletedWorkmen(
        Workman_ID=deleted_workman.Workman_ID,
        Proj_Code=deleted_workman.Proj_Code,
        Status=deleted_workman.Status,
        Action_Date=deleted_workman.Action_Date or datetime.now()
    )
    db.add(db_deleted)
    db.commit()
    db.refresh(db_deleted)
    return db_deleted
