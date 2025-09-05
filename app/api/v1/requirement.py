from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.requirement import RequirementCreate, RequirementResponse, TraceabilityMatrixRow
from app.services import requirement_service

router = APIRouter(prefix="/requirements", tags=["Requirements"])


@router.post("/", response_model=RequirementResponse)
def create_requirement_endpoint(req: RequirementCreate, db: Session = Depends(get_db)):
    return requirement_service.create_requirement(db, req.req_id, req.description)


@router.get("/", response_model=List[RequirementResponse])
def list_requirements_endpoint(db: Session = Depends(get_db)):
    return requirement_service.list_requirements(db)


@router.post("/{requirement_id}/cases/{case_id}")
def link_case_endpoint(requirement_id: int, case_id: int, db: Session = Depends(get_db)):
    return requirement_service.link_case_to_requirement(db, requirement_id, case_id)


@router.delete("/{requirement_id}/cases/{case_id}")
def unlink_case_endpoint(requirement_id: int, case_id: int, db: Session = Depends(get_db)):
    return requirement_service.unlink_case_from_requirement(db, requirement_id, case_id)


@router.delete("/{requirement_id}", response_model=RequirementResponse)
def soft_delete_requirement_endpoint(requirement_id: int, db: Session = Depends(get_db)):
    req = requirement_service.soft_delete_requirement(db, requirement_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
    return req


@router.delete("/{requirement_id}/permanent")
def permanent_delete_requirement_endpoint(requirement_id: int, db: Session = Depends(get_db)):
    result = requirement_service.permanently_delete_requirement(
        db, requirement_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
    return result


@router.get("/traceability-matrix", response_model=List[TraceabilityMatrixRow])
def traceability_matrix_endpoint(db: Session = Depends(get_db)):
    return requirement_service.get_traceability_matrix(db)
