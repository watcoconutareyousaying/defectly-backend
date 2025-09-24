from app.services.otp_service import create_otp

import pytest

@pytest.mark.asyncio
async def test_verify_otp_success(test_db, client, test_user):
    otp = create_otp(test_db, test_user.id)
    payload = {"email": test_user.email, "otp_code": otp.otp_code}
    response = client.post("/api/v1/verify-otp", json=payload)
    assert response.status_code == 200
    assert "Account verified successfully" in response.json()["message"]
