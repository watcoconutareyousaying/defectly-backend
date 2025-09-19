from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


class SummaryReportBase(BaseModel):
    project_id: int
    data: Dict[str, Any]


class SummaryReportCreate(SummaryReportBase):
    total_test_items: int
    total_test_implementations: int
    total_non_implementations: int
    overall_coverage: float


class SummaryReportResponse(SummaryReportBase):
    id: int
    report_date: datetime
    total_test_items: int
    total_test_implementations: int
    total_non_implementations: int
    overall_coverage: float
    is_deleted: bool

    class Config:
        orm_mode = True
