from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class CaseBase(BaseModel):
    case_id: str
    module: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    precondition: Optional[str] = None
    steps: Optional[str] = None
    data: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    status: Optional[str] = None  # e.g., Passed, Failed, Blocked
    remarks: Optional[str] = None


class CaseCreate(CaseBase):
    case_data: Optional[Dict[str, Any]] = None


class CaseUpdate(BaseModel):
    module: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    precondition: Optional[str] = None
    steps: Optional[str] = None
    data: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class CaseResponse(BaseModel):
    id: int
    requirement_id: int
    created_by: int
    case_data: Dict[str, Any]
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
