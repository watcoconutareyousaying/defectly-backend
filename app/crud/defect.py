from sqlalchemy import or_, func, String, cast, text
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.defect import Defect
from app.models.requirement import Requirement


def create_defect(db: Session, requirement_id: int, creator_id: int, defect_data: Dict[str, Any]):
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id).first()
    if not requirement:
        raise ValueError(f"Requirement {requirement_id} not found")

    d = Defect(requirement_id=requirement_id,
               created_by=creator_id, defect_data=defect_data)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def get_defect(db: Session, defect_id: int, include_deleted: bool = False):
    q = db.query(Defect).filter(Defect.id == defect_id)
    if not include_deleted:
        q = q.filter(Defect.is_deleted == False)  # type: ignore
    return q.first()


def get_defects_for_requirement(
    db: Session,
    requirement_id: int,
    include_deleted: bool = False,
    search: str | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0
):
    q = db.query(Defect).filter(Defect.requirement_id == requirement_id)

    if not include_deleted:
        q = q.filter(Defect.is_deleted == False)  # type: ignore

    if status:
        q = q.filter(
            func.lower(
                text("(defect_data->>'status')")
            ) == status.lower()
        )

    if search:
        search_pattern = f"%{search.lower()}%"
        q = q.filter(
            or_(
                func.lower(cast(Defect.defect_data['module'], String)).like(
                    search_pattern),
                func.lower(cast(Defect.defect_data['description'], String)).like(
                    search_pattern)
            )
        )
    return q.offset(offset).limit(limit).all()


def get_defects_for_project(
    db: Session,
    project_id: int,
    include_deleted: bool = False,
    search: str | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0
):
    q = db.query(Defect).join(Requirement).filter(
        Requirement.project_id == project_id)

    if not include_deleted:
        q = q.filter(Defect.is_deleted == False)  # type: ignore

    if status:
        q = q.filter(
            func.lower(
                text("(defect_data->>'status')")
            ) == status.lower()
        )

    if search:
        search_pattern = f"%{search.lower()}%"
        q = q.filter(
            or_(
                func.lower(cast(Defect.defect_data['module'], String)).like(
                    search_pattern),
                func.lower(cast(Defect.defect_data['description'], String)).like(
                    search_pattern)
            )
        )
    return q.offset(offset).limit(limit).all()


def update_defect(db: Session, defect: Defect, updates: Dict[str, Any]):
    if "defect_data" in updates and isinstance(updates["defect_data"], dict):
        existing = dict(defect.defect_data or {})
        new_data = dict(updates["defect_data"])
        defect.defect_data = {**existing, **new_data}
    if "is_deleted" in updates:
        defect.is_deleted = updates["is_deleted"]
    db.commit()
    db.refresh(defect)
    return defect


def soft_delete_defect(db: Session, defect: Defect):
    defect.soft_delete()
    db.commit()
    db.refresh(defect)
    return defect


def permanently_delete_defect(db: Session, defect: Defect):
    db.delete(defect)
    db.commit()
