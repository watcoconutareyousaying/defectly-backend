from fastapi import status


def test_signup_success(client):
    payload = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": "password123"
    }

    response = client.post("/api/v1/signup", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "user_id" in data
    assert "message" in data


def test_signup_existing_email(client, test_user):
    payload = {
        "name": test_user.name,
        "email": test_user.email,
        "password": "password123"
    }
    response = client.post("/api/v1/signup", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
