from fastapi import status


def test_login_success(client, test_user):
    payload = {"email": test_user.email, "password": "testpassword"}
    response = client.post("/api/v1/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    payload = {"email": test_user.email, "password": "wrongpass"}
    response = client.post("/api/v1/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
