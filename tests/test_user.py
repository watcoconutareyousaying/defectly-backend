def test_get_me(client):
    # Login first
    login_res = client.post("/api/v1/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = login_res.json()["access_token"]

    response = client.get("/api/v1/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == "test@example.com"
    assert user["name"] == "Test User"


def test_activity_logs(client):
    # Login first
    login_res = client.post("/api/v1/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = login_res.json()["access_token"]

    # Fetch activity logs
    response = client.get("/api/v1/activity-logs", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
    assert any("signup" in log["activity_type"] for log in logs)
    assert any("login" in log["activity_type"] for log in logs)


def test_logout(client):
    # Login first
    login_res = client.post("/api/v1/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = login_res.json()["access_token"]

    # Logout
    response = client.post("/api/v1/logout", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"
