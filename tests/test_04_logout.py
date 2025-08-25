import pytest
from fastapi.testclient import TestClient
from app.models.user import User
from app.db.session import get_db
from sqlalchemy.orm import Session


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_logout_success(client: TestClient, test_db: Session, test_user: User):
    token = login_and_get_token(client, test_user.email, "testpassword")

    response = client.post(
        "/api/v1/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "logged out successfully" in data["message"].lower()


def test_logout_with_invalid_token(client: TestClient):
    response = client.post(
        "/api/v1/logout",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    data = response.json()
    assert "invalid token" in data["detail"].lower()
