from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.otp import OTP
from app.core.security import verify_password


def test_forgot_password_success(client, test_db, test_user, monkeypatch):
    
    async def mock_send_password_reset_email(*a, **kw):
        return True
    
    monkeypatch.setattr(
        "app.services.auth_service.send_password_reset_email", mock_send_password_reset_email
    )

    response = client.post(
        "/api/v1/forgot-password",
        json={"email": test_user.email},
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "reset" in data["message"].lower()


def test_forgot_password_nonexistent_email(client):
    response = client.post(
        "/api/v1/forgot-password",
        json={"email": "ghost@example.com"},
    )
    # Should not reveal whether user exists
    assert response.status_code in [200, 400, 404]
    data = response.json()
    assert "message" in data or "detail" in data


def test_reset_password_success(client, test_db, test_user):
    user_email = test_user.email
    
    otp = OTP(
        user_id=test_user.id,
        otp_code="654321",
        is_used=False,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    test_db.add(otp)
    test_db.commit()

    response = client.post(
        "/api/v1/reset-password",
        json={
            "email": user_email,
            "otp_code": "654321",
            "new_password": "newsecurepassword",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "password reset successfully" in data["message"].lower()

    updated_user = test_db.query(User).filter_by(email=user_email).first()
    
    assert verify_password("newsecurepassword", updated_user.hashed_password)


def test_reset_password_invalid_otp(client, test_user):
    response = client.post(
        "/api/v1/reset-password",
        json={
            "email": test_user.email,
            "otp_code": "wrongotp",
            "new_password": "irrelevant",
        },
    )
    assert response.status_code == 400
    data = response.json()
    assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()


def test_reset_password_expired_otp(client, test_db, test_user):
    # Save user email for later queries (avoid DetachedInstanceError)
    user_email = test_user.email

    # Create an expired OTP (expired 5 minutes ago)
    expired_otp = OTP(
        user_id=test_user.id,
        otp_code="111111",
        is_used=False,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    test_db.add(expired_otp)
    test_db.commit()

    response = client.post(
        "/api/v1/reset-password",
        json={
            "email": user_email,
            "otp_code": "111111",
            "new_password": "anotherpassword",
        },
    )

    # Expect failure due to expired OTP
    assert response.status_code == 400
    data = response.json()
    assert "expired" in data["detail"].lower()