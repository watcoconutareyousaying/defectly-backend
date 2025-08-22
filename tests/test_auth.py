import pytest
from app.crud.user import get_user_by_email
from app.models.otp import OTP
from conftest import TestingSessionLocal


def test_signup(client):
    response = client.post(
        "/api/v1/signup",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["message"].startswith("User registered successfully")


def test_verify_otp(client):
    db = TestingSessionLocal()
    user = get_user_by_email(db, 'test@example.com')
    assert user is not None

    otp = db.query(OTP).filter(OTP.user_id == user.id).first()
    assert otp is not None

    response = client.post("/api/v1/verify-otp", json={
        "email": "test@example.com",
        "otp_code": otp.otp_code
    })

    assert response.status_code == 200
    assert response.json()["message"] == "Account verified successfully"


def test_login(client):
    response = client.post("/api/v1/login", json={
        "email": "test@example.com",
        "password": "password123"
    })

    assert response.status_code == 200
    token_data = response.json()

    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
