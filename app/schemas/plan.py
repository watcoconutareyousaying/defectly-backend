from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class PlanBase(BaseModel):
    module: Optional[str] = None
    prepared_by: Optional[str] = None
    date: Optional[datetime] = None
    phase: Optional[str] = None
    objective: Optional[str] = None
    scope: Optional[str] = None
    test_environment: Optional[str] = None
    tools_used: Optional[str] = None
    entry_criteria: Optional[str] = None
    exit_criteria: Optional[str] = None
    risks_and_mitigations: Optional[str] = None

    extra: Optional[Dict[str, Any]] = None


class PlanCreate(PlanBase):
    plan_data: Optional[Dict[str, Any]] = None


class PlanUpdate(BaseModel):
    plan_data: Optional[Dict[str, Any]] = None
    is_deleted: Optional[bool] = None


class PlanResponse(BaseModel):
    id: int
    project_id: int
    created_by: int
    project_name: Optional[str] = None
    plan_data: Dict[str, Any]
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
