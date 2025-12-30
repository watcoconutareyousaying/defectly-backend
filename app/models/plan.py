from sqlalchemy import Integer, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta, timezone

from app.db.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id = mapped_column(Integer, primary_key=True, index=True)
    project_id = mapped_column(ForeignKey('projects.id'), nullable=False)
    created_by = mapped_column(ForeignKey('users.id'), nullable=False)

    plan_data = mapped_column(JSON, nullable=False)

    is_deleted = mapped_column(Boolean, default=False)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", backref="plans")
    creator = relationship("User", backref="plans")

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)

    def is_expired(self, days: int = 30) -> bool:
        if not self.deleted_at:
            return False
        return datetime.now(timezone.utc) > self.deleted_at + timedelta(days=days)