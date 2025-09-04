from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.case import Case
from app.models.project import Project


def create_case(db: Session, project_id: int, creator_id: int, case_data: Dict[str, Any]):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    case_data = dict(case_data)
    case_data["project_name"] = project.name

    tc = Case(project_id=project_id, created_by=creator_id, case_data=case_data)
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return tc


def get_case(db: Session, case_id: int, include_deleted: bool = False):
    q = db.query(Case).filter(Case.id == case_id)
    if not include_deleted:
        q = q.filter(Case.is_deleted == False)  # type: ignore
    return q.first()


def get_cases_for_project(db: Session, project_id: int, include_deleted: bool = False):
    q = db.query(Case).filter(Case.project_id == project_id)
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