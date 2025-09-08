from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.models.requirement import Requirement
from app.models.requirement_case import RequirementCase


def create_requirement(db: Session, req_id: str, description: str):
    req = Requirement(req_id=req_id, description=description)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def get_requirement(db: Session, requirement_id: int, include_deleted: bool = False) -> Optional[Requirement]:
    query = db.query(Requirement).filter(Requirement.id == requirement_id)
    if not include_deleted:
        query = query.filter(Requirement.is_deleted == False)  # type: ignore
    return query.first()


def list_requirements(db: Session, include_deleted: bool = False) -> List[Requirement]:
    query = db.query(Requirement)
    if not include_deleted:
        query = query.filter(Requirement.is_deleted == False)  # type: ignore
    return query.all()


def link_case(db: Session, requirement_id: int, case_id: int):
    existing = db.query(RequirementCase).filter_by(
        requirement_id=requirement_id, case_id=case_id).first()
    if existing:
        return existing
    link = RequirementCase(requirement_id=requirement_id, case_id=case_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def unlink_case(db: Session, requirement_id: int, case_id: int):
    rc = db.query(RequirementCase).filter_by(
        requirement_id=requirement_id, case_id=case_id).first()
    if rc:
        db.delete(rc)
        db.commit()
        return {"message": "Unlinked successfully"}
    return {"message": "Link not found"}


def soft_delete_requirement(db: Session, requirement: Requirement):
    requirement.is_deleted = True
    requirement.deleted_at = datetime.now(timezone.utc)  # type: ignore
    # Soft delete linked RequirementCases
    for rc in requirement.cases:
        rc.is_deleted = True
        rc.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(requirement)
    return requirement


def permanently_delete_requirement(db: Session, requirement: Requirement):
    # Delete linked RequirementCases first
    for rc in requirement.cases:
        db.delete(rc)
    db.delete(requirement)
    db.commit()
    return {"message": "Requirement permanently deleted"}
