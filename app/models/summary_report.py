from sqlalchemy import Integer, String, DateTime, Float, Boolean, JSON, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.db.base import Base


class SummaryReport(Base):
    __tablename__ = "summary_reports"

    id = mapped_column(Integer, primary_key=True, index=True)
    project_id = mapped_column(ForeignKey("projects.id"), nullable=False)

    report_date = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc))
    data = mapped_column(JSON, nullable=False)

    total_test_items = mapped_column(Integer, default=0)
    total_test_implementations = mapped_column(Integer, default=0)
    total_non_implementations = mapped_column(Integer, default=0)
    overall_coverage = mapped_column(Float, default=0.0)

    is_deleted = mapped_column(Boolean, default=False)
    deleted_at = mapped_column(DateTime(timezone=True), nullable=True)

    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="summary_reports")

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
