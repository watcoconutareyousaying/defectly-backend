from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from typing import List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, get_client_ip, get_user_agent
from app.models.user import User
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate
from app.services import plan_service
from app.services.activity_log_service import log_activity
from app.services.export_service import export_project_plans, export_single_plan

router = APIRouter()


@router.post("/{project_id}/plans", response_model=PlanResponse)
def create_plan_endpoint(
    project_id: int,
    payload: PlanCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Convert payload to dict and merge all root fields into plan_data
    payload_dict = jsonable_encoder(payload, exclude_unset=True)

    # Extract plan_data or initialize empty
    plan_data = payload_dict.get("plan_data", {})

    # Merge all other fields from PlanBase (module, phase, etc.) into plan_data
    for key, value in payload_dict.items():
        if key != "plan_data":
            plan_data[key] = value

    # Create the plan
    plan = plan_service.create_plan(db, project_id, current_user.id, plan_data)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="create_plan",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) created a new plan "
            f"(Plan ID: {plan.id}) for Project (ID: {project_id}, "
            f"Name: {plan.plan_data.get('project_name')})."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return plan


@router.get("/{project_id}/plans", response_model=List[PlanResponse])
def list_plans_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plans = plan_service.list_plans_for_project(db, project_id)
    return plans


@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan_endpoint(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = plan_service.get_plan_by_id(db, plan_id)
    return plan


@router.put("/plans/{plan_id}", response_model=PlanResponse)
def update_plan_endpoint(
    plan_id: int,
    updates: PlanUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_plan = plan_service.get_plan_by_id(db, plan_id)
    old_data = existing_plan.plan_data.copy() if existing_plan.plan_data else {}

    update_dict = jsonable_encoder(updates, exclude_unset=True)

    plan_updates = update_dict.get("plan_data", {})
    for key, value in update_dict.items():
        if key != "plan_data" and key != "is_deleted":
            plan_updates[key] = value
    update_dict["plan_data"] = plan_updates

    plan = plan_service.update_plan(db, plan_id, update_dict, current_user.id)

    changes = []
    for field, new_value in plan_updates.items():
        old_value = old_data.get(field, "(empty)")
        if new_value != old_value:
            changes.append(f"{field}: '{old_value}' → '{new_value}'")

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="update_plan",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) updated Plan "
            f"(ID: {plan.id}, Project ID: {plan.project_id}); "
            f"Changes: {', '.join(changes) if changes else 'No changes'}"
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return plan


@router.delete("/plans/{plan_id}", response_model=PlanResponse)
def soft_delete_plan_endpoint(
    plan_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = plan_service.soft_delete_plan(db, plan_id, current_user.id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="soft_delete_plan",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) soft-deleted Plan (ID: {plan.id}, "
            f"Project ID: {plan.project_id}, Module: {plan.plan_data.get('module')}) "
            f"at {plan.deleted_at}."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return plan


@router.delete("/plans/{plan_id}/permanent", response_model=dict)
def permanent_delete_plan_endpoint(
    plan_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = plan_service.permanent_delete_plan(db, plan_id, current_user.id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="permanent_delete_plan",
        description=(
            f"User '{current_user.name}' (ID: {current_user.id}) permanently deleted Plan (ID: {plan_id})."
        ),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return result


@router.get("/plans/{plan_id}/export")
def export_single_plan_endpoint(
    plan_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        response = export_single_plan(db, plan_id, current_user.id)

        log_activity(
            db=db,
            user_id=current_user.id,
            user_name=current_user.name,
            activity_type="export_plan",
            description=(
                f"User '{current_user.name}' (ID: {current_user.id}) exported Plan (ID: {plan_id})."
            ),
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        return response

    except Exception as e:
        log_activity(
            db=db,
            user_id=current_user.id,
            user_name=current_user.name,
            activity_type="export_plan_failed",
            description=(
                f"User '{current_user.name}' (ID: {current_user.id}) failed to export Plan (ID: {plan_id}). "
                f"Error: {str(e)}"
            ),
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export plan: {str(e)}"
        )


@router.get("/{project_id}/plans/export")
def export_project_plans_endpoint(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        response = export_project_plans(db, project_id)

        log_activity(
            db=db,
            user_id=current_user.id,
            user_name=current_user.name,
            activity_type="export_project_plans",
            description=(
                f"User '{current_user.name}' (ID: {current_user.id}) exported all plans for Project (ID: {project_id})."
            ),
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        return response

    except Exception as e:
        log_activity(
            db=db,
            user_id=current_user.id,
            user_name=current_user.name,
            activity_type="export_project_plans_failed",
            description=(
                f"User '{current_user.name}' (ID: {current_user.id}) failed to export plans for Project (ID: {project_id}). "
                f"Error: {str(e)}"
            ),
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export project plans: {str(e)}"
        )
