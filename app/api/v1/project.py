from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services import project_service
from app.services.activity_log_service import log_activity
from app.api.deps import get_current_user, get_client_ip, get_user_agent
from app.models.user import User

router = APIRouter()


@router.post("/projects", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = project_service.create_new_project(
        db, project_data, current_user.id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="create_project",
        description=(
            f"User '{current_user.email}' (ID: {current_user.id}) created project "
            f"'{project.name}' (ID: {project.id})"
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return project


@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projects = project_service.get_user_projects(db, current_user.id)

    # Optional: log listing as read access
    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="list_projects",
        description=f"User '{current_user.email}' (ID: {current_user.id}) retrieved {len(projects)} projects",
        ip_address="",
        user_agent=""
    )

    return projects

@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    updates: ProjectUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # fetch project
    project = project_service.get_project_by_id(db, project_id)

    # snapshot original values BEFORE update
    old_name = project.name
    old_description = project.description

    # perform update
    project = project_service.update_existing_project(
        db, project_id, updates, current_user.id
    )

    # now compare with snapshot
    changes = []
    if updates.name is not None and updates.name != old_name:
        changes.append(f"name: '{old_name}' → '{updates.name}'")
    if updates.description is not None and updates.description != old_description:
        old_desc = old_description or "(empty)"
        new_desc = updates.description or "(empty)"
        changes.append(f"description: '{old_desc}' → '{new_desc}'")

    # log
    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="update_project",
        description=(
            f"User '{current_user.email}' (ID: {current_user.id}) updated project "
            f"'{project.name}' (ID: {project.id}); "
            f"Changes: {', '.join(changes) if changes else 'No changes detected'}"
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return project



@router.delete("/projects/{project_id}", response_model=ProjectResponse)
def delete_project(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = project_service.soft_delete_existing_project(
        db, project_id, current_user.id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="delete_project",
        description=(
            f"User '{current_user.email}' (ID: {current_user.id}) soft deleted project "
            f"'{project.name}' (ID: {project.id}) at {project.deleted_at}"
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return project


@router.delete("/projects/{project_id}/permanent", response_model=dict)
def permanent_delete_project(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = project_service.permanent_delete_existing_project(
        db, project_id, current_user.id
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="permanent_delete_project",
        description=(
            f"User '{current_user.email}' (ID: {current_user.id}) permanently deleted project "
            f"'{project.name}' (ID: {project.id})"
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return {"message": f"Project '{project.name}' (ID: {project.id}) permanently deleted"}
