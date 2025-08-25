def test_login_success(client, test_user):
    response = client.post(
        "/api/v1/login",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    response = client.post(
        "/api/v1/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    detail = response.json()["detail"]
    assert "Incorrect email or password" in detail or "invalid" in detail.lower()


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/login",
        json={"email": "ghost@example.com", "password": "doesntmatter"},
    )
    assert response.status_code == 401
    detail = response.json()["detail"]
    assert "Incorrect email or password" in detail or "invalid" in detail.lower()
