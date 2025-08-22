from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import all models here for Alembic
from app.models.activity_log import ActivityLog
from app.models.otp import OTP
from app.models.user import User
from app.models.tokens import Token