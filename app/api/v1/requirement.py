from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.requirement import RequirementCreate, RequirementResponse, TraceabilityMatrixRow
from app.services import requirement_service, requirement_export_service
from app.services.activity_log_service import log_activity
from app.api.deps import get_current_user, get_client_ip, get_user_agent
from app.crud import project as project_crud

router = APIRouter()


@router.post("/projects/{project_id}/requirements", response_model=RequirementResponse)
def create_requirement_endpoint(
    project_id: int,
    payload: RequirementCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = requirement_service.create_requirement(
        db, project_id, payload.req_id, payload.description)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="create_requirement",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) created a new Requirement "
            f"(ID: {req.id}, Req ID: {req.req_id}) for Project ID {project_id}."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return req


@router.get("/projects/{project_id}/requirements", response_model=List[RequirementResponse])
def list_requirements_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return requirement_service.list_requirements(db, project_id)


@router.delete("/requirements/{requirement_id}", response_model=RequirementResponse)
def soft_delete_requirement_endpoint(
    requirement_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = requirement_service.soft_delete_requirement(db, requirement_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="soft_delete_requirement",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) soft-deleted Requirement '{req.req_id}'"
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return req


@router.delete("/requirements/{requirement_id}/permanent")
def permanent_delete_requirement_endpoint(
    requirement_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = requirement_service.permanently_delete_requirement(
        db, requirement_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="permanent_delete_requirement",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) permanently deleted Requirement ID {requirement_id}"
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return result


@router.get("/projects/{project_id}/traceability-matrix", response_model=List[TraceabilityMatrixRow])
def traceability_matrix_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return requirement_service.get_traceability_matrix(db, project_id)


@router.get("/projects/{project_id}/traceability-matrix/export")
def export_traceability_matrix_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    matrix_rows = requirement_service.get_traceability_matrix(db, project_id)

    project = project_crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_name = project.name

    return requirement_export_service.export_traceability_matrix_to_excel(matrix_rows, project_name=project_name)
