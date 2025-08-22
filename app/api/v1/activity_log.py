from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud import activity_log as crud_activity
from app.schemas.activity_log import ActivityLogResponse
from app.models.user import User  
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/activity-logs", response_model=list[ActivityLogResponse])
def get_my_activity_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    from app.crud.activity_log import get_user_activity_logs
    return get_user_activity_logs(db, current_user.id, skip, limit)


@router.get("/", response_model=list[ActivityLogResponse])
def get_logs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    logs = crud_activity.list_logs(db, skip=skip, limit=limit)
    return logs
