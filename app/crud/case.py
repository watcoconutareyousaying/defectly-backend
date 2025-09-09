from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.case import Case
from app.models.requirement import Requirement


def create_case(db: Session, requirement_id: int, creator_id: int, case_data: Dict[str, Any]):
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise ValueError(f"Requirement {requirement_id} not found")

    tc = Case(requirement_id=requirement_id, created_by=creator_id, case_data=case_data)
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return tc


def get_case(db: Session, case_id: int, include_deleted: bool = False):
    q = db.query(Case).filter(Case.id == case_id)
    if not include_deleted:
        q = q.filter(Case.is_deleted == False)  # type: ignore
    return q.first()


def get_cases_for_project(db: Session, requirement_id: int, include_deleted: bool = False):
    q = db.query(Case).filter(Case.requirement_id == requirement_id)
    if not include_deleted:
        q = q.filter(Case.is_deleted == False)  # type: ignore
    return q.all()


def update_case(db: Session, case: Case, updates: Dict[str, Any]):
    if "case_data" in updates and isinstance(updates["case_data"], dict):
        existing = dict(case.case_data or {})
        new_data = dict(updates["case_data"])
        merged = {**existing, **new_data}
        case.case_data = merged

    if "is_deleted" in updates:
        case.is_deleted = updates["is_deleted"]
    db.commit()
    db.refresh(case)
    return case


def soft_delete_case(db: Session, case: Case):
    case.soft_delete()
    db.commit()
    db.refresh(case)
    return case

def permanently_delete_case(db: Session, case: Case):
    db.delete(case)
    db.commit()