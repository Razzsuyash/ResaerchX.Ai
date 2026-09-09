from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_register_and_login():
    email = "test@example.com"
    password = "password123"

    register = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )

    assert register.status_code == 201

    login = client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )

    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["access_token"]
