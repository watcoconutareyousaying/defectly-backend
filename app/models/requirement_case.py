from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.db.base import Base
from app.models.case import Case
from app.models.requirement import Requirement


class RequirementCase(Base):
    __tablename__ = "requirement_cases"

    id = mapped_column(Integer, primary_key=True, index=True)
    requirement_id = mapped_column(
        ForeignKey("requirements.id"), nullable=False)
    case_id = mapped_column(ForeignKey("cases.id"), nullable=False)

    requirement = relationship("Requirement", back_populates="cases")
    case = relationship("Case", back_populates="requirements")

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
