from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.db.base import Base
from datetime import datetime, timedelta, timezone


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_owner_project_name"),
    )

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String(255), nullable=False)
    description = mapped_column(Text, nullable=True)
    owner_id = mapped_column(ForeignKey("users.id"), nullable=False)

    is_deleted = mapped_column(Boolean, default=False)
    deleted_at = mapped_column(DateTime(timezone=True), nullable=True)

    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", backref="projects")

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)

    def is_expired(self):
        if not self.deleted_at:
            return False
        return datetime.now(timezone.utc) > self.deleted_at + timedelta(days=30)
