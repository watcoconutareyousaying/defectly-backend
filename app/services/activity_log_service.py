from typing import Optional
from sqlalchemy.orm import Session
from app.crud.activity_log import create_activity_log
from app.schemas.activity_log import ActivityLogCreate


def log_activity(
    db: Session,
    user_id: Optional[int] = None,
    user_name: Optional[str] = None,
    activity_type: str = "",
    description: str = "",
    ip_address: str = "",
    user_agent: str = ""
):
    activity_log = ActivityLogCreate(
        user_id=user_id,
        user_name=user_name,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )
    return create_activity_log(db, activity_log)
