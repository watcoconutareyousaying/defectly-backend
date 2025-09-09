from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.crud import requirement as req_crud
from app.schemas.requirement import TraceabilityMatrixRow


def create_requirement(db: Session, project_id: int, req_id: str, description: str):
    return req_crud.create_requirement(db, project_id, req_id, description)


def list_requirements(db: Session, project_id: int):
    return req_crud.list_requirements(db, project_id)


def get_requirement(db: Session, requirement_id: int, include_deleted: bool = False):
    req = req_crud.get_requirement(db, requirement_id, include_deleted)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
    return req


def soft_delete_requirement(db: Session, requirement_id: int):
    req = req_crud.get_requirement(db, requirement_id)
    if not req:
        return None
    return req_crud.soft_delete_requirement(db, req)


def permanently_delete_requirement(db: Session, requirement_id: int):
    req = get_requirement(db, requirement_id, include_deleted=True)
    req_crud.permanently_delete_requirement(db, req)
    return {"message": "Requirement permanently deleted"}


def get_traceability_matrix(db: Session, project_id: int) -> List[TraceabilityMatrixRow]:
    requirements = req_crud.list_requirements(
        db, project_id, include_deleted=False)
    matrix = []

    for req in requirements:
        case_ids = []
        statuses = []
        for case in req.cases:
            if case.is_deleted:
                continue
            case_ids.append(case.case_data.get("case_id", "N/A"))
            statuses.append(case.case_data.get("status", "N/A"))

        matrix.append(
            TraceabilityMatrixRow(
                requirement_id=req.req_id,
                requirement_description=req.description,
                test_case_ids=case_ids,
                test_statuses=statuses
            )
        )
    return matrix
