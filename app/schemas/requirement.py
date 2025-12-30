from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class RequirementBase(BaseModel):
    req_id: str
    description: str


class RequirementCreate(RequirementBase):
    pass


class RequirementResponse(RequirementBase):
    id: int
    project_id: int
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class TraceabilityMatrixRow(BaseModel):
    requirement_id: str
    requirement_description: str
    test_case_ids: List[str]
    test_statuses: List[Optional[str]]
