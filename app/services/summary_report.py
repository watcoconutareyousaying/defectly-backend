from sqlalchemy.orm import Session
from datetime import datetime
from app.services import requirement_service
from app.crud import summary_report as sr_crud


def generate_and_store_project_summary(db: Session, project_id: int):

    requirements = requirement_service.list_requirements(db, project_id)

    summary_data = []
    total_items = total_implemented = total_non_implemented = 0

    for req in requirements:
        test_cases = [c for c in req.cases if not c.is_deleted]
        feature_name = f"{req.req_id}: {req.description[:50]}"

        no_of_items = len(test_cases)
        implemented = sum(
            1 for c in test_cases if c.case_data.get("status") is not None)
        non_implemented = no_of_items - implemented
        ok = sum(1 for c in test_cases if c.case_data.get("status") == "Pass")
        not_ok = sum(1 for c in test_cases if c.case_data.get(
            "status") != "Pass")

        coverage = 100.0 if no_of_items == 0 else round(
            (implemented / no_of_items) * 100, 2)

        summary_data.append({
            "feature_name": feature_name,
            "total_items": no_of_items,
            "implemented": implemented,
            "non_implemented": non_implemented,
            "ok": ok,
            "not_ok": not_ok,
            "coverage": coverage
        })

        total_items += no_of_items
        total_implemented += implemented
        total_non_implemented += non_implemented

    overall_coverage = 0.0 if total_items == 0 else round(
        (total_implemented / total_items) * 100, 2)

    report = sr_crud.create_summary_report(
        db=db,
        project_id=project_id,
        data=summary_data,
        total_items=total_items,
        total_implementations=total_implemented,
        total_non_implementations=total_non_implemented,
        coverage=overall_coverage
    )

    return report


def list_summary_reports(db: Session, project_id: int):
    return sr_crud.list_summary_reports(db, project_id)


def get_summary_report(db: Session, report_id: int):
    report = sr_crud.get_summary_report(db, report_id)
    if not report:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Summary report not found")
    return report


def soft_delete_summary_report(db: Session, report_id: int):
    report = sr_crud.get_summary_report(db, report_id)
    if not report:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Summary report not found")
    return sr_crud.soft_delete_summary_report(db, report)


def permanently_delete_summary_report(db: Session, report_id: int):
    report = sr_crud.get_summary_report(db, report_id)
    if not report:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Summary report not found")
    sr_crud.permanently_delete_summary_report(db, report)
    return {"message": "Summary report permanently deleted"}
