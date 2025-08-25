from sqlalchemy.orm import Session
from typing import List
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogCreate


def create_activity_log(db: Session, activity_log: ActivityLogCreate) -> ActivityLog:
    db_log = ActivityLog(**activity_log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_user_activity_logs(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ActivityLog]:
    return db.query(ActivityLog).filter(ActivityLog.user_id == user_id).offset(skip).limit(limit).all()
