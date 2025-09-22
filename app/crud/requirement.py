from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.models.requirement import Requirement


def create_requirement(db: Session, project_id: int, req_id: str, description: str):
    req = Requirement(project_id=project_id, req_id=req_id,
                      description=description)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def get_requirement(db: Session, requirement_id: int, include_deleted: bool = False) -> Optional[Requirement]:
    query = db.query(Requirement).filter(Requirement.id == requirement_id)
    if not include_deleted:
        query = query.filter(Requirement.is_deleted == False)  # type: ignore
    return query.first()


def list_requirements(
    db: Session,
    project_id: Optional[int] = None,
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
    include_deleted: bool = False
) -> List[Requirement]:
    query = db.query(Requirement)
    if project_id:
        query = query.filter(Requirement.project_id == project_id)
    if not include_deleted:
        query = query.filter(Requirement.is_deleted == False)  # type: ignore

    if search:
        query = query.filter(
            or_(
                func.lower(Requirement.req_id).like(f"%{search.lower()}%"),
                func.lower(Requirement.description).like(f"%{search.lower()}%")
            )
        )
    return query.offset(offset).limit(limit).all()


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
