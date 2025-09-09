from sqlalchemy import Integer, ForeignKey, DateTime, JSON, Boolean, String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from app.db.base import Base


class Case(Base):
    __tablename__ = "cases"

    id = mapped_column(Integer, primary_key=True, index=True)
    requirement_id = mapped_column(ForeignKey("requirements.id"), nullable=False)
    created_by = mapped_column(ForeignKey("users.id"), nullable=False)

    case_data = mapped_column(JSON, nullable=False)

    is_deleted = mapped_column(Boolean, default=False)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    creator = relationship("User", backref="cases")
    requirement = relationship("Requirement", back_populates="cases")

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
