from sqlalchemy import Column, String, Integer, DateTime, Boolean
from app.database import Base

class WorkmenMaster(Base):
    __tablename__ = "Korba_WorkmenMaster"
    __table_args__ = {"schema": "dbo"}

    Workman_ID = Column(Integer, primary_key=True, index=True)
    Work_ID = Column(Integer, nullable=False)
    Proj_Code = Column(String(10), nullable=True)
    Name = Column(String(50), nullable=True)
    Surname = Column(String(50), nullable=True)
    GatePassIssueDate = Column(DateTime, nullable=True)
    GatePassValidFrom = Column(DateTime, nullable=True)
    GatePassValidUpto = Column(DateTime, nullable=True)
    last_update_date = Column(DateTime, nullable=True)
    Record_Disabled = Column(Boolean, nullable=True, default=False)
    Record_Creation_Date = Column(DateTime, nullable=True)

class DeletedWorkmen(Base):
    __tablename__ = "Korba_DeletedWorkmen"
    __table_args__ = {"schema": "dbo"}

    ID = Column(Integer, primary_key=True)
    Workman_ID = Column(Integer, nullable=False)
    Proj_Code = Column(String(10), nullable=True)
    Status = Column(String(7), nullable=False)
    Action_Date = Column(DateTime, nullable=True)
