from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# --- WorkmenMaster Schemas ---

class WorkmenMasterBase(BaseModel):
    Work_ID: Optional[int] = Field(None, description="Work Identifier")
    Proj_Code: Optional[str] = Field(None, max_length=10, description="Project Code")
    Name: Optional[str] = Field(None, max_length=50, description="Workman First Name")
    Surname: Optional[str] = Field(None, max_length=50, description="Workman Surname")
    GatePassIssueDate: Optional[datetime] = Field(None, description="Gate Pass Issue Date")
    GatePassValidFrom: Optional[datetime] = Field(None, description="Gate Pass Valid From Date & Time")
    GatePassValidUpto: Optional[datetime] = Field(None, description="Gate Pass Valid Upto Date & Time")
    last_update_date: Optional[datetime] = Field(None, description="Last Record Update Timestamp")
    Record_Disabled: Optional[bool] = Field(False, description="Boolean Status Field")
    Record_Creation_Date: Optional[datetime] = Field(None, description="Record Creation Timestamp")

class WorkmenMasterCreate(WorkmenMasterBase):
    Workman_ID: int = Field(..., description="Integer Workman Identifier")
    Work_ID: int = Field(..., description="Work Identifier")

class WorkmenMasterUpdate(WorkmenMasterBase):
    pass

class WorkmenMasterResponse(WorkmenMasterBase):
    model_config = ConfigDict(from_attributes=True)
    Workman_ID: int


# --- DeletedWorkmen Schemas ---

class DeletedWorkmenBase(BaseModel):
    Workman_ID: int = Field(..., description="Integer Workman Identifier")
    Proj_Code: Optional[str] = Field(None, max_length=10, description="Project Code")
    Status: str = Field(..., max_length=7, description="Workman Status")
    Action_Date: Optional[datetime] = Field(None, description="Action Date")

class DeletedWorkmenCreate(DeletedWorkmenBase):
    ID: Optional[int] = Field(None, description="Unique Identifier (auto-incremented by database)")

class DeletedWorkmenResponse(DeletedWorkmenBase):
    model_config = ConfigDict(from_attributes=True)
    ID: int


# --- Database Configuration Schemas ---

class DatabaseConfigUpdate(BaseModel):
    ENGINE: Optional[str] = Field(None, description="Database type/engine (e.g. sql_server)")
    NAME: Optional[str] = Field(None, description="Database name")
    USER: Optional[str] = Field(None, description="Database username")
    PASSWORD: Optional[str] = Field(None, description="Database password")
    HOST: Optional[str] = Field(None, description="Database host server IP or hostname")
    PORT: Optional[str] = Field(None, description="Database port number")
    DRIVER: Optional[str] = Field(None, description="ODBC Driver name")

class DatabaseConfigResponse(BaseModel):
    ENGINE: str
    NAME: str
    USER: str
    PASSWORD_MASKED: str
    HOST: str
    PORT: str
    DRIVER: str
    message: str
    tables_created: bool = Field(False, description="Whether tables were created/verified successfully in the new database")
    tables_message: str = Field("", description="Details about the table creation result")
