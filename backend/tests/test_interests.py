from fastapi.testclient import TestClient
import pytest


def _auth_headers(client: TestClient, email: str = "interest@example.edu") -> dict[str, str]:
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Katherine Johnson",
            "password": "StrongPassword123!",
        },
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _complete_sample_assessment(client: TestClient, headers: dict[str, str]) -> int:
    session_id = client.post("/api/v1/assessments/sessions", headers=headers).json()["id"]
    answers = {
        "q_domains_interest": ["ai_ml", "nlp_ir"],
        "q_problem_solving_style": "empirical",
        "q_math_comfort": 4,
        "q_coding_comfort": 5,
        "q_scenario_ambiguity": "error_analysis",
        "q_technical_preference": "benchmark_dataset",
        "q_application_impact": 4,
        "q_followup_ai_nlp": "scientific_nlp",
        "q_followup_math_rigor": "balanced_applied",
    }
    for qid, val in answers.items():
        res = client.put(
            f"/api/v1/assessments/sessions/{session_id}/responses",
            json={"question_id": qid, "answer_value": val},
            headers=headers,
        )
        assert res.status_code == 200

    comp_res = client.post(
        f"/api/v1/assessments/sessions/{session_id}/complete",
        headers=headers,
    )
    assert comp_res.status_code == 200
    return session_id


def test_interests_require_authentication(client: TestClient) -> None:
    assert client.post("/api/v1/interests/analyze").status_code == 401
    assert client.get("/api/v1/interests/latest").status_code == 401


def test_analyze_requires_completed_assessment(client: TestClient) -> None:
    headers = _auth_headers(client, "no_assess@example.edu")

    assert client.get("/api/v1/interests/latest", headers=headers).status_code == 404
    assert client.post("/api/v1/interests/analyze", headers=headers).status_code == 400


def test_analyze_and_fetch_explainable_interest_profile(client: TestClient) -> None:
    headers = _auth_headers(client, "full_interest@example.edu")

    # Save academic profile to verify profile signals are included
    client.put(
        "/api/v1/profile",
        json={
            "education_level": "undergraduate",
            "degree_program": "B.Sc. Computer Science",
            "technical_skills": ["PyTorch", "NLP"],
            "programming_languages": ["Python", "SQL"],
            "preferred_research_domains": ["Natural Language Processing"],
            "research_experience_level": "intermediate",
            "weekly_hours_available": 15,
        },
        headers=headers,
    )

    session_id = _complete_sample_assessment(client, headers)

    analyze_res = client.post("/api/v1/interests/analyze", headers=headers)
    assert analyze_res.status_code == 200
    body = analyze_res.json()

    assert body["session_id"] == session_id
    assert "limitations_note" in body and "not scientifically validated" in body["limitations_note"]
    assert "nlp" in body["top_domains"]
    assert "ai_ml" in body["top_domains"]

    nlp_entry = next(d for d in body["domain_scores"] if d["key"] == "nlp")
    assert nlp_entry["score"] > 0
    assert any(c["source"] == "academic_profile" for c in nlp_entry["contributions"])
    assert any(c["source"].startswith("assessment:") for c in nlp_entry["contributions"])

    assert body["skill_confidence"]["math_comfort"] == 4
    assert body["skill_confidence"]["coding_comfort"] == 5
    assert body["skill_confidence"]["experience_level"] == "intermediate"
    assert body["skill_confidence"]["overall_confidence"] > 0

    latest_res = client.get("/api/v1/interests/latest", headers=headers)
    assert latest_res.status_code == 200
    assert latest_res.json()["id"] == body["id"]


def test_niche_summary_generation_and_caching(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    headers = _auth_headers(client, "niche_user@example.edu")

    # Requires an interest profile first
    assert client.post("/api/v1/interests/niche-summary", headers=headers).status_code == 400
    assert client.get("/api/v1/interests/niche-summary", headers=headers).status_code == 404

    _complete_sample_assessment(client, headers)
    assert client.post("/api/v1/interests/analyze", headers=headers).status_code == 200

    class _WithKeySettings:
        gemini_api_key = "test-gemini-key"
        gemini_model = "gemini-2.5-flash"

    class _FakeGeminiResp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{"niche_title": "Empirical Scientific NLP Systems",'
                                        ' "summary": "Combines NLP and empirical ML evaluation.",'
                                        ' "example_directions": ["Citation-grounded retrieval"]}'
                                    )
                                }
                            ]
                        }
                    }
                ]
            }

    calls = 0

    def _counting_post(*args: object, **kwargs: object) -> _FakeGeminiResp:
        nonlocal calls
        calls += 1
        return _FakeGeminiResp()

    monkeypatch.setattr("app.services.brief_service.get_settings", lambda: _WithKeySettings())
    monkeypatch.setattr("app.services.brief_service.httpx.post", _counting_post)

    res = client.post("/api/v1/interests/niche-summary", headers=headers)
    assert res.status_code == 200
    assert res.json()["niche_title"] == "Empirical Scientific NLP Systems"
    assert calls == 1

    # Second POST hits cache
    assert client.post("/api/v1/interests/niche-summary", headers=headers).status_code == 200
    assert calls == 1

    # GET returns cached
    assert client.get("/api/v1/interests/niche-summary", headers=headers).status_code == 200
