import pytest

@pytest.mark.asyncio
async def test_forgot_password(client, test_user):
    payload = {"email": test_user.email}
    response = client.post("/api/v1/forgot-password", json=payload)
    assert response.status_code == 200
    assert "Password reset OTP sent" in response.json()["message"]
