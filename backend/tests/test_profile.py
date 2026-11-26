from fastapi.testclient import TestClient


def _auth_headers(client: TestClient, email: str = "profile@example.edu") -> dict[str, str]:
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Alan Turing",
            "password": "StrongPassword123!",
        },
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_profile_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/profile").status_code == 401
    assert client.put("/api/v1/profile", json={}).status_code == 401


def test_get_profile_returns_404_when_missing(client: TestClient) -> None:
    headers = _auth_headers(client, "missing@example.edu")
    response = client.get("/api/v1/profile", headers=headers)
    assert response.status_code == 404


def test_upsert_and_read_academic_profile(client: TestClient) -> None:
    headers = _auth_headers(client, "upsert@example.edu")

    create_payload = {
        "education_level": "undergraduate",
        "degree_program": "  B.Sc. in Computer Science  ",
        "academic_background": "Completed algorithms, linear algebra, and databases.",
        "technical_skills": ["Machine Learning", "Data Analysis", "machine learning", "  "],
        "programming_languages": ["Python", "TypeScript", "python"],
        "preferred_research_domains": ["Natural Language Processing", "HCI"],
        "research_experience_level": "beginner",
        "research_experience_summary": "Assisted with a capstone literature review.",
        "career_goals": "Apply to CS Master's programs focused on applied NLP.",
        "weekly_hours_available": 15,
    }

    put_res = client.put("/api/v1/profile", json=create_payload, headers=headers)
    assert put_res.status_code == 200
    body = put_res.json()
    assert body["education_level"] == "undergraduate"
    assert body["degree_program"] == "B.Sc. in Computer Science"
    assert body["technical_skills"] == ["Machine Learning", "Data Analysis"]
    assert body["programming_languages"] == ["Python", "TypeScript"]
    assert body["preferred_research_domains"] == ["Natural Language Processing", "HCI"]
    assert body["weekly_hours_available"] == 15

    # Update existing profile
    update_payload = {
        **create_payload,
        "education_level": "masters",
        "weekly_hours_available": 25,
    }
    update_res = client.put("/api/v1/profile", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["education_level"] == "masters"
    assert update_res.json()["weekly_hours_available"] == 25

    get_res = client.get("/api/v1/profile", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == body["id"]
    assert get_res.json()["education_level"] == "masters"


def test_profile_validation_rejects_invalid_fields(client: TestClient) -> None:
    headers = _auth_headers(client, "invalid@example.edu")

    response = client.put(
        "/api/v1/profile",
        json={
            "education_level": "invalid_level",
            "degree_program": "CS",
            "research_experience_level": "beginner",
            "weekly_hours_available": 200,
        },
        headers=headers,
    )
    assert response.status_code == 422
