from fastapi.testclient import TestClient
import pytest


def _auth_headers(client: TestClient, email: str = "rec_user@example.edu") -> dict[str, str]:
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Ada Lovelace",
            "password": "StrongPassword123!",
        },
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _setup_interest_profile(client: TestClient, headers: dict[str, str]) -> None:
    client.put(
        "/api/v1/profile",
        json={
            "education_level": "undergraduate",
            "degree_program": "B.Sc. Computer Science",
            "academic_background": "Coursework in machine learning, information retrieval, and NLP.",
            "technical_skills": ["PyTorch", "NLP", "Information Retrieval"],
            "programming_languages": ["Python", "SQL"],
            "preferred_research_domains": ["Natural Language Processing", "Machine Learning"],
            "research_experience_level": "beginner",
            "career_goals": "Build reliable scientific retrieval and language systems.",
            "weekly_hours_available": 12,
        },
        headers=headers,
    )

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

    assert (
        client.post(f"/api/v1/assessments/sessions/{session_id}/complete", headers=headers).status_code
        == 200
    )
    assert client.post("/api/v1/interests/analyze", headers=headers).status_code == 200


def test_recommendations_require_authentication(client: TestClient) -> None:
    assert client.post("/api/v1/recommendations/generate").status_code == 401
    assert client.get("/api/v1/recommendations/latest").status_code == 401
    assert client.get("/api/v1/recommendations/bookmarks").status_code == 401
    assert (
        client.post(
            "/api/v1/recommendations/bookmarks", json={"topic_id": "nlp_scientific_rag"}
        ).status_code
        == 401
    )
    assert (
        client.put(
            "/api/v1/recommendations/feedback/nlp_scientific_rag", json={"rating": 5}
        ).status_code
        == 401
    )


def test_generate_requires_interest_profile(client: TestClient) -> None:
    headers = _auth_headers(client, "no_interest@example.edu")
    assert client.get("/api/v1/recommendations/latest", headers=headers).status_code == 404
    assert client.post("/api/v1/recommendations/generate", headers=headers).status_code == 400


def test_generate_hybrid_recommendations_bookmarks_and_feedback(client: TestClient) -> None:
    headers = _auth_headers(client, "hybrid_rec@example.edu")
    _setup_interest_profile(client, headers)

    gen_res = client.post("/api/v1/recommendations/generate", headers=headers)
    assert gen_res.status_code == 200
    body = gen_res.json()

    assert "AI-assisted hybrid recommendations" in body["methodology_note"]
    results = body["results"]
    assert len(results) >= 25

    scores = [item["hybrid_score"] for item in results]
    assert scores == sorted(scores, reverse=True)
    for item in results:
        assert 0 <= item["hybrid_score"] <= 100
        bd = item["score_breakdown"]
        assert 0 <= bd["interest_alignment"] <= 100
        assert 0 <= bd["skill_feasibility"] <= 100
        assert 0 <= bd["methodology_fit"] <= 100
        assert 0 <= bd["semantic_similarity"] <= 100
        assert item["is_bookmarked"] is False
        assert item["user_rating"] is None

    top_three_domains = {tag for item in results[:3] for tag in item["domain_tags"]}
    assert "nlp" in top_three_domains or "ai_ml" in top_three_domains

    target_topic = results[0]["id"]

    # Bookmark add, list, and verify reflection in /latest
    bm_res = client.post(
        "/api/v1/recommendations/bookmarks",
        json={"topic_id": target_topic},
        headers=headers,
    )
    assert bm_res.status_code == 201
    assert bm_res.json()["topic_id"] == target_topic

    list_res = client.get("/api/v1/recommendations/bookmarks", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["topic_id"] == target_topic

    # Upsert feedback
    fb_res = client.put(
        f"/api/v1/recommendations/feedback/{target_topic}",
        json={"rating": 5, "comment": "Directly matches my thesis direction."},
        headers=headers,
    )
    assert fb_res.status_code == 200
    assert fb_res.json()["rating"] == 5

    # Update same feedback
    fb_update = client.put(
        f"/api/v1/recommendations/feedback/{target_topic}",
        json={"rating": 4, "comment": "Updated note."},
        headers=headers,
    )
    assert fb_update.status_code == 200
    assert fb_update.json()["rating"] == 4
    assert fb_update.json()["comment"] == "Updated note."

    latest_res = client.get("/api/v1/recommendations/latest", headers=headers)
    assert latest_res.status_code == 200
    first_latest = latest_res.json()["results"][0]
    assert first_latest["is_bookmarked"] is True
    assert first_latest["user_rating"] == 4

    # Remove bookmark
    del_res = client.delete(f"/api/v1/recommendations/bookmarks/{target_topic}", headers=headers)
    assert del_res.status_code == 204
    assert client.get("/api/v1/recommendations/bookmarks", headers=headers).json() == []

    # Unknown topic returns 404
    assert (
        client.post(
            "/api/v1/recommendations/bookmarks",
            json={"topic_id": "nonexistent_topic"},
            headers=headers,
        ).status_code
        == 404
    )


def test_topic_brief_requires_key_or_calls_gemini(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    headers = _auth_headers(client, "brief_user@example.edu")

    # Unknown topic -> 404
    assert (
        client.post("/api/v1/recommendations/unknown_topic/brief", headers=headers).status_code
        == 404
    )

    # Missing GEMINI_API_KEY -> 503
    class _NoKeySettings:
        gemini_api_key = None
        gemini_model = "gemini-2.5-flash"

    monkeypatch.setattr("app.services.brief_service.get_settings", lambda: _NoKeySettings())
    assert (
        client.post("/api/v1/recommendations/nlp_scientific_rag/brief", headers=headers).status_code
        == 503
    )

    # Configured GEMINI_API_KEY -> 200 with structured brief
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
                                        '{"problem_framing": "Ground RAG outputs in citations.",'
                                        ' "research_questions": ["RQ1: How to detect unsupported claims?"],'
                                        ' "suggested_methodology": "Evaluate on a small verified subset."}'
                                    )
                                }
                            ]
                        }
                    }
                ]
            }

    monkeypatch.setattr("app.services.brief_service.get_settings", lambda: _WithKeySettings())
    monkeypatch.setattr(
        "app.services.brief_service.httpx.post",
        lambda *args, **kwargs: _FakeGeminiResp(),
    )

    res = client.post("/api/v1/recommendations/nlp_scientific_rag/brief", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["topic_id"] == "nlp_scientific_rag"
    assert "AI-generated exploratory research brief" in body["ai_generated_notice"]
    assert body["research_questions"] == ["RQ1: How to detect unsupported claims?"]
