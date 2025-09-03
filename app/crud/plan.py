from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.plan import Plan
from app.models.project import Project
from app.models.user import User


def create_plan(db: Session, project_id: int, creator_id: int, plan_data: Dict[str, Any]):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    plan_data = dict(plan_data)
    plan_data["project_name"] = project.name

    tp = Plan(project_id=project_id, created_by=creator_id, plan_data=plan_data)
    db.add(tp)
    db.commit()
    db.refresh(tp)
    return tp


def get_plan(db: Session, test_plan_id: int, include_deleted: bool = False):
    q = db.query(Plan).filter(Plan.id == test_plan_id)
    if not include_deleted:
        q = q.filter(Plan.is_deleted == False)  # type: ignore
    return q.first()


def get_plans_for_project(db: Session, project_id: int, include_deleted: bool = False):
    q = db.query(Plan).filter(Plan.project_id == project_id)
    if not include_deleted:
        q = q.filter(Plan.is_deleted == False)  # type: ignore
    return q.all()


def get_plans_for_user(db: Session, user_id: int, include_deleted: bool = False):
    q = db.query(Plan).filter(Plan.created_by == user_id)
    if not include_deleted:
        q = q.filter(Plan.is_deleted == False)  # type: ignore
    return q.all()


def update_plan(db: Session, test_plan: Plan, updates: Dict[str, Any]):
    if "plan_data" in updates and isinstance(updates["plan_data"], dict):
        existing = test_plan.plan_data or {}
        existing.update(updates["plan_data"])
        test_plan.plan_data = existing
    # allow toggling is_deleted via explicit update (rare)
    if "is_deleted" in updates and isinstance(updates["is_deleted"], bool):
        test_plan.is_deleted = updates["is_deleted"]
    db.commit()
    db.refresh(test_plan)
    return test_plan


def soft_delete_plan(db: Session, test_plan: Plan):
    test_plan.soft_delete()
    db.commit()
    db.refresh(test_plan)
    return test_plan


def permanently_delete_plan(db: Session, test_plan: Plan):
    db.delete(test_plan)
    db.commit()


def permanently_delete_expired_plans(db: Session, expiry_days: int = 30):
    expired = db.query(Plan).filter(Plan.is_deleted == True).all()  # type: ignore
    for tp in expired:
        if tp.is_expired(days=expiry_days):
            db.delete(tp)
    db.commit()
