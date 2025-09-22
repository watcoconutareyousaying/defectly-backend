from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.crud import project as project_crud
from app.models.project import Project


def create_new_project(db: Session, project_data: ProjectCreate, owner_id: int) -> Project:
    try:
        return project_crud.create_project(db, project_data, owner_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{project_data.name}' already exists for this user"
        )


def get_user_projects(
        db: Session,
        owner_id: int,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0):
    return project_crud.get_projects(db, owner_id, search, limit, offset)


def get_project_by_id(db: Session, project_id: int) -> Project:
    project = project_crud.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def update_existing_project(db: Session, project_id: int, updates: ProjectUpdate, owner_id: int) -> Project:
    project = get_project_by_id(db, project_id)
    if project.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        return project_crud.update_project(db, project, updates)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{updates.name}' already exists for this user"
        )


def soft_delete_existing_project(db: Session, project_id: int, owner_id: int):
    project = get_project_by_id(db, project_id)
    if project.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return project_crud.soft_delete_project(db, project)


def permanent_delete_existing_project(db: Session, project_id: int, owner_id: int) -> Project:
    project = get_project_by_id(db, project_id)
    if project.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    project_crud.permanently_delete_project(db, project)
    return project
