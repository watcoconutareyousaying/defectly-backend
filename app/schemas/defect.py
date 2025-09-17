from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class DefectBase(BaseModel):
    defect_id: str
    module: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    bug_detected_date: Optional[str] = None
    fixed_date: Optional[str] = None
    reopen_date: Optional[str] = None
    remarks: Optional[str] = None


class DefectCreate(DefectBase):
    defect_data: Optional[Dict[str, Any]] = None


class DefectUpdate(BaseModel):
    module: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    bug_detected_date: Optional[str] = None
    fixed_date: Optional[str] = None
    reopen_date: Optional[str] = None
    remarks: Optional[str] = None


class DefectResponse(BaseModel):
    id: int
    requirement_id: int
    created_by: int
    defect_data: Dict[str, Any]
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
