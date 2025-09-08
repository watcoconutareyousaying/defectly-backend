from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.requirement import RequirementCreate, RequirementResponse, TraceabilityMatrixRow, RequirementCaseLinkResponse
from app.services import requirement_service
from app.services.activity_log_service import log_activity
from app.api.deps import get_current_user, get_client_ip, get_user_agent

router = APIRouter()


@router.post("/", response_model=RequirementResponse)
def create_requirement_endpoint(
    req: RequirementCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requirement = requirement_service.create_requirement(
        db, req.req_id, req.description)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="create_requirement",
        description=f"User '{current_user.name}' (ID: {current_user.id}) created Requirement '{req.req_id}'",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return requirement


@router.get("/", response_model=List[RequirementResponse])
def list_requirements_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return requirement_service.list_requirements(db)


@router.post("/{requirement_id}/cases/{case_id}")
def link_case_endpoint(
    requirement_id: int,
    case_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = requirement_service.link_case_to_requirement(
        db, requirement_id, case_id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="link_case_to_requirement",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) linked Test Case ID {case_id} "
            f"to Requirement ID {requirement_id}"
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return RequirementCaseLinkResponse(
        requirement_id=requirement_id,
        case_id=case_id,
        linked=True
    )


@router.delete("/{requirement_id}/cases/{case_id}")
def unlink_case_endpoint(
    requirement_id: int,
    case_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = requirement_service.unlink_case_from_requirement(
        db, requirement_id, case_id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="unlink_case_from_requirement",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) unlinked Test Case ID {case_id} "
            f"from Requirement ID {requirement_id}"
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return RequirementCaseLinkResponse(
        requirement_id=requirement_id,
        case_id=case_id,
        linked=False
    )


@router.delete("/{requirement_id}", response_model=RequirementResponse)
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


@router.delete("/{requirement_id}/permanent")
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


@router.get("/traceability-matrix", response_model=List[TraceabilityMatrixRow])
def traceability_matrix_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return requirement_service.get_traceability_matrix(db)
