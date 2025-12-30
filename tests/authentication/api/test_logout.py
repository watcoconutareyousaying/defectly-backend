import pytest
from app.core.security import create_access_token
from datetime import datetime, timezone, timedelta
from app.crud import token as token_crud


def test_logout_success(client, test_db, test_user):
    jti = "test-jti"
    access_token = create_access_token(test_user.email, jti=jti)

    token_crud.create_token(
        db=test_db,
        jti=jti,
        user_id=test_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30)
    )

    client.headers.update({"Authorization": f"Bearer {access_token}"})

    response = client.post("/api/v1/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"

    db_token = token_crud.get_active_token(test_db, jti)
    assert db_token is None
