import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.session import get_db
from alembic.config import Config
from alembic import command
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi.testclient import TestClient
import pytest



TEST_DATABASE_URL = os.getenv(
    "TEST_DB_URL",
    "sqlite:///:memory:"
)

# SQLALCHEMY_DATABASE_URL = "sqlite://./test_db:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {}
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    if TEST_DATABASE_URL.startswith("sqlite"):
        from app.db.base import Base
        from app.models import user, otp, activity_log
        Base.metadata.create_all(bind=engine)
    else:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    yield
    # Optional: clean up
    if not TEST_DATABASE_URL.startswith("sqlite"):
        command.downgrade(alembic_cfg, "base")


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
