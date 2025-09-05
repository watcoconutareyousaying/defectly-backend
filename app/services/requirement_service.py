from sqlalchemy.orm import Session
from typing import List
from app.crud import requirement as req_crud
from app.schemas.requirement import TraceabilityMatrixRow


def create_requirement(db: Session, req_id: str, description: str):
    return req_crud.create_requirement(db, req_id, description)


def list_requirements(db: Session):
    return req_crud.list_requirements(db)


def get_requirement(db: Session, requirement_id: int, include_deleted: bool = False):
    return req_crud.get_requirement(db, requirement_id, include_deleted)


def link_case_to_requirement(db: Session, requirement_id: int, case_id: int):
    return req_crud.link_case(db, requirement_id, case_id)


def unlink_case_from_requirement(db: Session, requirement_id: int, case_id: int):
    return req_crud.unlink_case(db, requirement_id, case_id)


def soft_delete_requirement(db: Session, requirement_id: int):
    req = req_crud.get_requirement(db, requirement_id)
    if not req:
        return None
    return req_crud.soft_delete_requirement(db, req)


def permanently_delete_requirement(db: Session, requirement_id: int):
    req = req_crud.get_requirement(db, requirement_id, include_deleted=True)
    if not req:
        return None
    return req_crud.permanently_delete_requirement(db, req)


def get_traceability_matrix(db: Session) -> List[TraceabilityMatrixRow]:
    requirements = req_crud.list_requirements(db, include_deleted=False)
    matrix = []
    for req in requirements:
        case_ids = []
        statuses = []
        for rc in req.cases:
            if rc.is_deleted:
                continue
            case_ids.append(rc.case.case_data.get("case_id"))
            statuses.append(rc.case.case_data.get("status"))
        matrix.append(
            TraceabilityMatrixRow(
                requirement_id=req.req_id,
                requirement_description=req.description,
                test_case_ids=case_ids,
                test_statuses=statuses
            )
        )
    return matrix
