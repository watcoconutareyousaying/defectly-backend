from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.summary_report import SummaryReportResponse
from app.services import summary_report as sr_service
from app.services.summary_export_report import export_summary_reports_to_excel
from app.services.activity_log_service import log_activity
from app.api.deps import get_current_user, get_client_ip, get_user_agent

router = APIRouter()

# Generate and store summary report


@router.post("/projects/{project_id}/summary-reports/generate", response_model=SummaryReportResponse)
def generate_summary_report_endpoint(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sr = sr_service.generate_and_store_project_summary(db, project_id)
    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="generate_summary_report",
        description=f"User '{current_user.name}' generated a summary report for Project ID {project_id}",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return sr

# List stored summary reports


@router.get("/projects/{project_id}/summary-reports", response_model=List[SummaryReportResponse])
def list_summary_reports_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return sr_service.list_summary_reports(db, project_id)

# Soft delete report


@router.delete("/summary-reports/{report_id}")
def soft_delete_summary_report_endpoint(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sr = sr_service.soft_delete_summary_report(db, report_id)
    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="soft_delete_summary_report",
        description=f"User '{current_user.name}' soft-deleted summary report ID {report_id}",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return sr

# Permanent delete


@router.delete("/summary-reports/{report_id}/permanent")
def permanent_delete_summary_report_endpoint(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = sr_service.permanently_delete_summary_report(db, report_id)
    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="permanent_delete_summary_report",
        description=f"User '{current_user.name}' permanently deleted summary report ID {report_id}",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    return result


@router.get("/summary-reports/{report_id}/export")
def export_summary_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = sr_service.get_summary_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Summary report not found")
    
    project_name = report.project.name if report.project else f"Project_{report.project_id}"
    return export_summary_reports_to_excel([report], project_name=project_name)
