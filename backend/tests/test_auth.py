from fastapi.testclient import TestClient


def _register_sample_user(client: TestClient, email: str = "researcher@example.edu") -> dict:
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Ada Lovelace",
            "password": "StrongPassword123!",
        },
    ).json()


def test_register_user_returns_token_and_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "Ada@Example.edu",
            "full_name": "Ada Lovelace",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and len(body["access_token"]) > 0
    assert body["user"]["email"] == "ada@example.edu"
    assert body["user"]["full_name"] == "Ada Lovelace"
    assert "hashed_password" not in body["user"]


def test_register_duplicate_email_returns_conflict(client: TestClient) -> None:
    _register_sample_user(client, "dup@example.edu")

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "DUP@example.edu",
            "full_name": "Another User",
            "password": "AnotherPassword123!",
        },
    )

    assert response.status_code == 409


def test_register_short_password_fails_validation(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "short@example.edu",
            "full_name": "Short Pass",
            "password": "123",
        },
    )

    assert response.status_code == 422


def test_login_success_and_invalid_password(client: TestClient) -> None:
    _register_sample_user(client, "login@example.edu")

    ok_res = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.edu", "password": "StrongPassword123!"},
    )
    assert ok_res.status_code == 200
    assert ok_res.json()["user"]["email"] == "login@example.edu"
    assert ok_res.json()["access_token"]

    bad_res = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.edu", "password": "WrongPassword"},
    )
    assert bad_res.status_code == 401


def test_protected_me_route_and_logout(client: TestClient) -> None:
    reg_body = _register_sample_user(client, "me@example.edu")
    token = reg_body["access_token"]

    unauth_res = client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401

    invalid_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert invalid_res.status_code == 401

    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "me@example.edu"

    logout_res = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_res.status_code == 200
    assert logout_res.json() == {"message": "Successfully logged out."}
