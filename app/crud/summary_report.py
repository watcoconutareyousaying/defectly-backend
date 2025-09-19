import json
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timezone
from app.models.summary_report import SummaryReport


def create_summary_report(
    db: Session,
    project_id: int,
    data: List[Dict],
    total_items: int,
    total_implementations: int,
    total_non_implementations: int,
    coverage: float
) -> SummaryReport:
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            data = []
            
    report = SummaryReport(
        project_id=project_id,
        data=data,
        total_test_items=total_items,
        total_test_implementations=total_implementations,
        total_non_implementations=total_non_implementations,
        overall_coverage=coverage
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_summary_report(db: Session, report_id: int, include_deleted: bool = False) -> SummaryReport | None:
    query = db.query(SummaryReport).filter(SummaryReport.id == report_id)
    if not include_deleted:
        query = query.filter(SummaryReport.is_deleted == False) # type: ignore
    return query.first()


def list_summary_reports(db: Session, project_id: int, include_deleted: bool = False) -> List[SummaryReport]:
    query = db.query(SummaryReport).filter(
        SummaryReport.project_id == project_id)
    if not include_deleted:
        query = query.filter(SummaryReport.is_deleted == False) # type: ignore
    return query.all()


def soft_delete_summary_report(db: Session, report: SummaryReport) -> SummaryReport:
    report.is_deleted = True
    report.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(report)
    return report


def permanently_delete_summary_report(db: Session, report: SummaryReport):
    db.delete(report)
    db.commit()
    return {"message": "Report has been permanently deleted"}
