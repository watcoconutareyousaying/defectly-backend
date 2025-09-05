from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import all models here for Alembic
from app.models.user import User
from app.models.otp import OTP
from app.models.tokens import Token
from app.models.activity_log import ActivityLog
from app.models.project import Project
from app.models.plan import Plan
from app.models.case import Case
from app.models.requirement import Requirement
from app.models.requirement_case import RequirementCase