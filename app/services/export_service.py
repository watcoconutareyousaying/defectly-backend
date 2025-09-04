import io
import re
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.services import plan_service
from app.utils import file_export


FIELD_ORDER = [
    "project_name",
    "version",
    "prepared_by",
    "date",
    "module",
    "phase",
    "objective",
    "scope",
    "test_environment",
    "tools_used",
    "entry_criteria",
    "exit_criteria",
    "risks_and_mitigations",
]


def _sanitize_filename(name: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower())
    return safe


def export_single_plan(db: Session, plan_id: int, user_id: int):
    plan = plan_service.get_plan_by_id(db, plan_id)

    plan_dict = {
        "project_name": plan.plan_data.get("project_name"),
        "version": plan.plan_data.get("version"),
        "prepared_by": plan.plan_data.get("prepared_by") or plan.creator.name,
        "date": plan.plan_data.get("date"),
        "module": plan.plan_data.get("module"),
        "phase": plan.plan_data.get("phase"),
        "objective": plan.plan_data.get("objective"),
        "scope": plan.plan_data.get("scope"),
        "test_environment": plan.plan_data.get("test_environment"),
        "tools_used": plan.plan_data.get("tools_used"),
        "entry_criteria": plan.plan_data.get("entry_criteria"),
        "exit_criteria": plan.plan_data.get("exit_criteria"),
        "risks_and_mitigations": plan.plan_data.get("risks_and_mitigations"),
    }

    wb = file_export.export_plan_to_excel(plan_dict, FIELD_ORDER)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"{_sanitize_filename(plan.plan_data.get('project_name'))}-testplan.xlsx"

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def export_project_plans(db: Session, project_id: int):
    plans = plan_service.list_plans_for_project(db, project_id)

    plan_dicts = []
    for plan in plans:
        plan_dicts.append({
            "project_name": plan.plan_data.get("project_name"),
            "version": plan.plan_data.get("version"),
            "prepared_by": plan.plan_data.get("prepared_by") or plan.creator.name,
            "date": plan.plan_data.get("date"),
            "module": plan.plan_data.get("module"),
            "phase": plan.plan_data.get("phase"),
            "objective": plan.plan_data.get("objective"),
            "scope": plan.plan_data.get("scope"),
            "test_environment": plan.plan_data.get("test_environment"),
            "tools_used": plan.plan_data.get("tools_used"),
            "entry_criteria": plan.plan_data.get("entry_criteria"),
            "exit_criteria": plan.plan_data.get("exit_criteria"),
            "risks_and_mitigations": plan.plan_data.get("risks_and_mitigations"),
        })

    wb = file_export.export_multiple_plans_to_excel(plan_dicts, FIELD_ORDER)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    project_name = plans[0].plan_data.get(
        "project_name", f"project_{project_id}")
    filename = f"{_sanitize_filename(project_name)}-testplan.xlsx"

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
