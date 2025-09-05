from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.case import CaseCreate, CaseResponse, CaseUpdate
from app.services import case_service
from app.services.activity_log_service import log_activity
from app.api.deps import get_current_user, get_client_ip, get_user_agent

router = APIRouter()


@router.post("/{project_id}/cases", response_model=CaseResponse)
def create_case_endpoint(
    project_id: int,
    payload: CaseCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payload_dict = jsonable_encoder(payload, exclude_unset=True)
    case_data = payload_dict.get("case_data", {})
    for key, value in payload_dict.items():
        if key != "case_data":
            case_data[key] = value
    tc = case_service.create_case(db, project_id, current_user.id, case_data)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="create_case",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) created a new Test Case "
            f"(ID: {tc.id}, Test Case ID: {tc.case_data.get('case_id')}) "
            f"for Project (ID: {project_id}, Name: {tc.case_data.get('project_name')})."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return tc


@router.get("/{project_id}/cases", response_model=List[CaseResponse])
def list_cases_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return case_service.list_cases_for_project(db, project_id)


@router.get("/cases/{case_id}", response_model=CaseResponse)
def get_case_endpoint(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return case_service.get_case_by_id(db, case_id)


@router.put("/cases/{case_id}", response_model=CaseResponse)
def update_case_endpoint(
    case_id: int,
    updates: CaseUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_dict = jsonable_encoder(updates, exclude_unset=True)
    case_data = update_dict.get("case_data", {})
    for key, value in update_dict.items():
        if key != "case_data":
            case_data[key] = value
    update_dict["case_data"] = case_data

    existing_case = case_service.get_case_by_id(db, case_id)
    old_data = existing_case.case_data.copy() if existing_case.case_data else {}

    tc = case_service.update_case(db, case_id, update_dict, current_user.id)

    changes  = []
    for field, new_value in case_data.items():
        old_value = old_data.get(field, "(empty)")
        if new_value != old_value:
            changes.append(f"{field}: '{old_value}' → '{new_value}'")

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="update_case",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) updated Test Case "
            f"(ID: {tc.id}, Test Case ID: {tc.case_data.get('case_id')}, Project ID: {tc.project_id}); "
            f"Changes: {', '.join(changes) if changes else 'No changes'}"
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return tc


@router.delete("/cases/{case_id}", response_model=CaseResponse)
def soft_delete_case_endpoint(
    case_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tc = case_service.soft_delete_case(db, case_id, current_user.id)
    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="soft_delete_case",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) soft-deleted Test Case "
            f"(ID: {tc.id}, Test Case ID: {tc.case_data.get('case_id')}, "
            f"Project ID: {tc.project_id}) at {tc.deleted_at}."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return tc


@router.delete("/cases/{case_id}/permanent", response_model=dict)
def permanent_delete_case_endpoint(
    case_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = case_service.permanent_delete_case(db, case_id, current_user.id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="permanent_delete_case",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) permanently deleted Test Case "
            f"(ID: {case_id})."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return result


@router.get("/{project_id}/cases/export")
def export_cases_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return case_service.export_cases_for_project(db, project_id)
