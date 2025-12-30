from fastapi import APIRouter, Depends, Request, Query
from fastapi.encoders import jsonable_encoder
from typing import List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.defect import DefectCreate, DefectResponse, DefectUpdate
from app.services import defect_service
from app.services.activity_log_service import log_activity
from app.api.deps import get_current_user, get_client_ip, get_user_agent

router = APIRouter()


@router.post("/requirements/{requirement_id}/defects", response_model=DefectResponse)
def create_defect_endpoint(
    requirement_id: int,
    payload: DefectCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payload_dict = jsonable_encoder(payload, exclude_unset=True)
    defect_data = payload_dict.get("defect_data", {})
    for key, value in payload_dict.items():
        if key != "defect_data":
            defect_data[key] = value

    d = defect_service.create_defect(
        db, requirement_id, current_user.id, defect_data)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="create_defect",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) created Defect "
            f"(ID: {d.id}, Defect ID: {d.defect_data.get('defect_id')}) "
            f"for Requirement ID: {requirement_id}."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return d


@router.get("/requirements/{requirement_id}/defects", response_model=List[DefectResponse])
def list_defects_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: str | None = Query(
        None, description="Search in title or description"),
    status: str | None = Query(
        None, description="Filter by status: Open, Fixed, In Progress"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Number of cases to return"),
    offset: int = Query(0, ge=0, description="Number of cases to skip")
):
    return defect_service.list_defects_for_requirement(db, requirement_id, status=status, search=search, limit=limit, offset=offset)


@router.get("/project/{project_id}/defects", response_model=List[DefectResponse])
def list_defects_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: str | None = Query(
        None, description="Search in title or description"),
    status: str | None = Query(
        None, description="Filter by status: Open, Fixed, In Progress"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Number of cases to return"),
    offset: int = Query(0, ge=0, description="Number of cases to skip")
):
    return defect_service.list_defects_for_project(db, project_id, status=status, search=search, limit=limit, offset=offset)


@router.get("/defects/{defect_id}", response_model=DefectResponse)
def get_defect_endpoint(
    defect_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return defect_service.get_defect_by_id(db, defect_id)


@router.put("/defects/{defect_id}", response_model=DefectResponse)
def update_defect_endpoint(
    defect_id: int,
    updates: DefectUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_dict = jsonable_encoder(updates, exclude_unset=True)
    defect_data = update_dict.get("defect_data", {})
    for key, value in update_dict.items():
        if key != "defect_data":
            defect_data[key] = value
    update_dict["defect_data"] = defect_data

    existing_defect = defect_service.get_defect_by_id(db, defect_id)
    old_data = existing_defect.defect_data.copy() if existing_defect.defect_data else {}

    d = defect_service.update_defect(
        db, defect_id, update_dict, current_user.id)

    changes = []
    for field, new_value in defect_data.items():
        old_value = old_data.get(field, "(empty)")
        if new_value != old_value:
            changes.append(f"{field}: '{old_value}' → '{new_value}'")

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="update_defect",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) updated Defect "
            f"(ID: {d.id}, Defect ID: {d.defect_data.get('defect_id')}, Requirement ID: {d.requirement_id}); "
            f"Changes: {', '.join(changes) if changes else 'No changes'}"
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return d


@router.delete("/defects/{defect_id}", response_model=DefectResponse)
def soft_delete_defect_endpoint(
    defect_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    d = defect_service.soft_delete_defect(db, defect_id, current_user.id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="soft_delete_defect",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) soft-deleted Defect "
            f"(ID: {d.id}, Defect ID: {d.defect_data.get('defect_id')}, Requirement ID: {d.requirement_id})."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return d


@router.delete("/defects/{defect_id}/permanent", response_model=dict)
def permanent_delete_defect_endpoint(
    defect_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = defect_service.permanent_delete_defect(
        db, defect_id, current_user.id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="permanent_delete_defect",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) permanently deleted Defect "
            f"(ID: {defect_id})."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return result


@router.get("/requirements/{requirement_id}/defects/export")
def export_requirement_defects_endpoint(
    requirement_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    response = defect_service.export_defects_for_requirement(
        db, requirement_id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="export_defects",
        description=(
            f"User '{current_user.name}' exported all defects for Requirement ID: {requirement_id}."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return response


@router.get("/projects/{project_id}/defects/export")
def export_all_defects_endpoint(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    response = defect_service.export_defects_for_project(db, project_id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="export_project_defects",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) exported all defects for Project ID: {project_id}."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return response
