import io
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from fastapi import HTTPException, status
from app.crud import case as tc_crud
from app.services.case_export_service import export_cases_to_excel



def create_case(db: Session, project_id: int, creator_id: int, payload: dict):
    try:
        return tc_crud.create_case(db, project_id, creator_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


def list_cases_for_project(db: Session, project_id: int):
    return tc_crud.get_cases_for_project(db, project_id)


def get_case_by_id(db: Session, case_id: int):
    tc = tc_crud.get_case(db, case_id)
    if not tc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    return tc


def update_case(db: Session, case_id: int, updates: dict, user_id: int):
    tc = tc_crud.get_case(db, case_id, include_deleted=True)
    if not tc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    if tc.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if "case_data" in updates:
        existing_data = tc.case_data or {}
        new_data = updates["case_data"]
        updates["case_data"] = {**existing_data, **new_data}
    return tc_crud.update_case(db, tc, updates)


def soft_delete_case(db: Session, case_id: int, user_id: int):
    tc = tc_crud.get_case(db, case_id, include_deleted=True)
    if not tc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    if tc.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return tc_crud.soft_delete_case(db, tc)


def permanent_delete_case(db: Session, case_id: int, user_id: int):
    tc = tc_crud.get_case(db, case_id, include_deleted=True)
    if not tc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    if tc.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    tc_crud.permanently_delete_case(db, tc)
    return {"message": "Test case permanently deleted"}


def export_cases_for_project(db, project_id: int):
    cases = tc_crud.get_cases_for_project(db, project_id)
    wb = export_cases_to_excel(cases)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    
    project_name = cases[0].project.name if cases[0].project else f"project_{project_id}"
    safe_project_name = project_name.replace(" ", "_")
    
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={safe_project_name}-testcases.xlsx"}
    )