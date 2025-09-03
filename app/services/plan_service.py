from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, Any
from app.crud import plan as tp_crud


def create_plan(db: Session, project_id: int, creator_id: int, plan_payload: Dict[str, Any]):
    try:
        return tp_crud.create_plan(db, project_id, creator_id, plan_payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


def list_plans_for_project(db: Session, project_id: int):
    return tp_crud.get_plans_for_project(db, project_id)


def get_plan_by_id(db: Session, test_plan_id: int):
    tp = tp_crud.get_plan(db, test_plan_id)
    if not tp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test plan not found")
    return tp


def update_plan(db: Session, test_plan_id: int, updates: Dict[str, Any], user_id: int):
    tp = tp_crud.get_plan(db, test_plan_id, include_deleted=True)
    if not tp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test plan not found")

    if tp.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if "plan_data" in updates and updates["plan_data"] is not None:
        existing_data = tp.plan_data or {}
        new_data = updates["plan_data"]

        merged_data = {**existing_data, **new_data}
        updates["plan_data"] = merged_data

    return tp_crud.update_plan(db, tp, updates)


def soft_delete_plan(db: Session, test_plan_id: int, user_id: int):
    tp = tp_crud.get_plan(db, test_plan_id, include_deleted=True)
    if not tp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test plan not found")
    if tp.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return tp_crud.soft_delete_plan(db, tp)


def permanent_delete_plan(db: Session, test_plan_id: int, user_id: int):
    tp = tp_crud.get_plan(db, test_plan_id, include_deleted=True)
    if not tp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test plan not found")
    if tp.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    tp_crud.permanently_delete_plan(db, tp)
    return {"message": "Test plan permanently deleted"}


def purge_expired_plans(db: Session, expiry_days: int = 30):
    tp_crud.permanently_delete_expired_plans(db, expiry_days=expiry_days)
