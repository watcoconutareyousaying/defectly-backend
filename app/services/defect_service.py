import io
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from fastapi import HTTPException, status
from app.crud import defect as defect_crud
from app.crud import requirement as req_crud
from app.crud import project as project_crud
from app.services.defect_export_service import export_defects_to_excel, export_project_defects_to_excel


def create_defect(db: Session, requirement_id: int, creator_id: int, payload: dict):
    try:
        return defect_crud.create_defect(db, requirement_id, creator_id, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


def list_defects_for_requirement(db: Session, requirement_id: int):
    return defect_crud.get_defects_for_requirement(db, requirement_id)


def get_defect_by_id(db: Session, defect_id: int):
    d = defect_crud.get_defect(db, defect_id)
    if not d:
        raise HTTPException(status_code=404, detail="Defect not found")
    return d


def update_defect(db: Session, defect_id: int, updates: dict, user_id: int):
    d = defect_crud.get_defect(db, defect_id, include_deleted=True)
    if not d:
        raise HTTPException(status_code=404, detail="Defect not found")
    if d.created_by != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if "defect_data" in updates:
        existing = d.defect_data or {}
        updates["defect_data"] = {**existing, **updates["defect_data"]}
    return defect_crud.update_defect(db, d, updates)


def soft_delete_defect(db: Session, defect_id: int, user_id: int):
    d = defect_crud.get_defect(db, defect_id, include_deleted=True)
    if not d:
        raise HTTPException(status_code=404, detail="Defect not found")
    if d.created_by != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return defect_crud.soft_delete_defect(db, d)


def permanent_delete_defect(db: Session, defect_id: int, user_id: int):
    d = defect_crud.get_defect(db, defect_id, include_deleted=True)
    if not d:
        raise HTTPException(status_code=404, detail="Defect not found")
    if d.created_by != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    defect_crud.permanently_delete_defect(db, d)
    return {"message": "Defect permanently deleted"}


def export_defects_for_requirement(db: Session, requirement_id: int):
    requirement = req_crud.get_requirement(db, requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    defects = [d for d in requirement.defects if not d.is_deleted]
    
    requirement_name = requirement.req_id.replace(" ", "_")[:50]
    wb = export_defects_to_excel(requirement_name, defects)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={requirement_name}-defects.xlsx"}
    )

def export_defects_for_project(db: Session, project_id: int):
    project = project_crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    requirements = req_crud.list_requirements(db, project_id, include_deleted=False)
    wb = export_project_defects_to_excel(requirements)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    project_name = project.name.replace(" ", "_")[:50]

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={project_name}-defects.xlsx"
        }
    )