from sqlalchemy import Integer, String, Text, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.db.base import Base


class Requirement(Base):
    __tablename__ = "requirements"

    id = mapped_column(Integer, primary_key=True, index=True)
    req_id = mapped_column(String(50), unique=True, index=True)
    description = mapped_column(Text, nullable=False)

    is_deleted = mapped_column(Boolean, default=False)
    deleted_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True)

    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    cases = relationship("RequirementCase", back_populates="requirement")

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
