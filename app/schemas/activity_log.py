from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ActivityLogBase(BaseModel):
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    activity_type: str
    description: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLogResponse(ActivityLogBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
