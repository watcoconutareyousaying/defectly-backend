from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from datetime import date


class PlanBase(BaseModel):
    version: Optional[str] = None
    module: Optional[str] = None
    prepared_by: Optional[str] = None
    date: date
    phase: Optional[str] = None
    objective: Optional[str] = None
    scope: Optional[str] = None
    test_environment: Optional[str] = None
    tools_used: Optional[str] = None
    entry_criteria: Optional[str] = None
    exit_criteria: Optional[str] = None
    risks_and_mitigations: Optional[str] = None


class PlanCreate(PlanBase):
    plan_data: Optional[Dict[str, Any]] = None


class PlanUpdate(BaseModel):
    version: Optional[str] = None
    module: Optional[str] = None
    prepared_by: Optional[str] = None
    date: Optional[date]
    phase: Optional[str] = None
    objective: Optional[str] = None
    scope: Optional[str] = None
    test_environment: Optional[str] = None
    tools_used: Optional[str] = None
    entry_criteria: Optional[str] = None
    exit_criteria: Optional[str] = None
    risks_and_mitigations: Optional[str] = None


class PlanResponse(BaseModel):
    id: int
    project_id: int
    created_by: int
    plan_data: Dict[str, Any]
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
