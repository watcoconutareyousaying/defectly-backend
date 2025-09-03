from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, get_client_ip, get_user_agent
from app.models.user import User
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate
from app.services import plan_service
from app.services.activity_log_service import log_activity

router = APIRouter(prefix="/projects", tags=["-plans"])


@router.post("/{project_id}/-plans", response_model=PlanResponse)
def create_plan_endpoint(
    project_id: int,
    payload: PlanCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if payload.plan_data:
        plan_data = payload.plan_data
    else:
        plan_data = payload.dict(exclude_unset=True, exclude={"plan_data"})
        extra = plan_data.pop("extra", None)
        if extra and isinstance(extra, dict):
            plan_data.update(extra)

    plan = plan_service.create_plan(db, project_id, current_user.id, plan_data)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="create__plan",
        description=f" plan (ID: {plan.id}) created for project (ID: {project_id})",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return plan


@router.get("/{project_id}/-plans", response_model=List[PlanResponse])
def list_plans_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plans = plan_service.list_plans_for_project(db, project_id)
    return plans


@router.get("/-plans/{plan_id}", response_model=PlanResponse)
def get_plan_endpoint(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = plan_service.get_plan_by_id(db, plan_id)
    return plan


@router.put("/-plans/{plan_id}", response_model=PlanResponse)
def update_plan_endpoint(
    plan_id: int,
    updates: PlanUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # prepare update dict
    update_dict = updates.dict(exclude_unset=True)
    plan = plan_service.update_plan(db, plan_id, update_dict, current_user.id)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="update_plan",
        description=f" plan (ID: {plan.id}) updated",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return plan


@router.delete("/-plans/{plan_id}", response_model=PlanResponse)
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
        description=f" plan (ID: {plan.id}) soft deleted at {plan.deleted_at}",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return plan


@router.delete("/-plans/{plan_id}/permanent", response_model=dict)
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
        description=f" plan (ID: {plan_id}) permanently deleted",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return result
