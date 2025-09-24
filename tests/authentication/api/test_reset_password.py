import pytest
from app.services.otp_service import create_otp

@pytest.mark.asyncio
async def test_reset_password(client, test_user, test_db):
    otp = create_otp(test_db, test_user.id)
    payload = {
        "email": test_user.email,
        "otp_code": otp.otp_code,
        "new_password": "newpassword123"
    }
    response = client.post("/api/v1/reset-password", json=payload)
    assert response.status_code == 200
    assert "Password reset successfully" in response.json()["message"]
