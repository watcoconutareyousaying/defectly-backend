from datetime import datetime, timedelta, timezone
from app.models.otp import OTP
from app.models.user import User


def test_signup_success(client, test_db, monkeypatch):
    email = "newuser@example.com"

    async def mock_send_otp_email(*a, **kw):
        return True
    
    monkeypatch.setattr(
        "app.services.auth_service.send_otp_email", mock_send_otp_email)

    response = client.post(
        "/api/v1/signup",
        json={
            "name": "New User",
            "email": email,
            "password": "newpassword123"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "User registered successfully" in data["message"]

    user = test_db.query(User).filter_by(email=email).first()
    assert user is not None

    otp = OTP(
        user_id=user.id,
        otp_code="123456",
        is_used=False,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),)
    test_db.add(otp)
    test_db.commit()

    monkeypatch.setattr(
        "app.services.otp_service.send_welcome_email", lambda *a, **kw: None)

    response = client.post(
        "/api/v1/verify-otp",
        json={"email": email, "otp_code": "123456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Account verified successfully" in data["message"]


def test_signup_duplicate_email(client, test_user):
    response = client.post(
        "/api/v1/signup",
        json={
            "name": "Another User",
            "email": test_user.email,
            "password": "somepassword"
        },
    )
    assert response.status_code == 400
    data = response.json()
    assert "already registered" in data["detail"] or "already exists" in data["detail"]


def test_signup_missing_fields(client):
    response = client.post(
        "/api/v1/signup",
        json={
            "name": "Broken User",
            "email": "broken@example.com"
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert "password" in str(data)
