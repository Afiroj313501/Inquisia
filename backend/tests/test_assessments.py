from fastapi.testclient import TestClient


def _auth_headers(client: TestClient, email: str = "assess@example.edu") -> dict[str, str]:
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Grace Hopper",
            "password": "StrongPassword123!",
        },
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_assessments_require_authentication(client: TestClient) -> None:
    assert client.post("/api/v1/assessments/sessions").status_code == 401
    assert client.get("/api/v1/assessments/sessions/latest").status_code == 401


def test_start_and_resume_session(client: TestClient) -> None:
    headers = _auth_headers(client, "resume@example.edu")

    start_res = client.post("/api/v1/assessments/sessions", headers=headers)
    assert start_res.status_code == 200
    session = start_res.json()
    assert session["status"] == "in_progress"
    assert session["progress"]["answered_count"] == 0
    assert session["progress"]["total_questions"] == 7

    # Resuming returns the same active session
    resume_res = client.post("/api/v1/assessments/sessions", headers=headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["id"] == session["id"]

    latest_res = client.get("/api/v1/assessments/sessions/latest", headers=headers)
    assert latest_res.status_code == 200
    assert latest_res.json()["id"] == session["id"]


def test_adaptive_followups_and_full_completion(client: TestClient) -> None:
    headers = _auth_headers(client, "adaptive@example.edu")
    session_id = client.post("/api/v1/assessments/sessions", headers=headers).json()["id"]

    # Selecting ai_ml unlocks q_followup_ai_nlp
    r1 = client.put(
        f"/api/v1/assessments/sessions/{session_id}/responses",
        json={"question_id": "q_domains_interest", "answer_value": ["ai_ml"]},
        headers=headers,
    )
    assert r1.status_code == 200
    q_ids = [q["id"] for q in r1.json()["questions"]]
    assert "q_followup_ai_nlp" in q_ids
    assert "q_followup_systems" not in q_ids

    # Rating math comfort >= 4 unlocks q_followup_math_rigor
    r2 = client.put(
        f"/api/v1/assessments/sessions/{session_id}/responses",
        json={"question_id": "q_math_comfort", "answer_value": 5},
        headers=headers,
    )
    assert r2.status_code == 200
    q_ids_2 = [q["id"] for q in r2.json()["questions"]]
    assert "q_followup_math_rigor" in q_ids_2
    assert r2.json()["progress"]["total_questions"] == 9

    # Cannot complete while questions remain unanswered
    premature_complete = client.post(
        f"/api/v1/assessments/sessions/{session_id}/complete",
        headers=headers,
    )
    assert premature_complete.status_code == 400

    # Answer remaining applicable questions
    remaining_answers = {
        "q_problem_solving_style": "empirical",
        "q_coding_comfort": 4,
        "q_scenario_ambiguity": "error_analysis",
        "q_technical_preference": "benchmark_dataset",
        "q_application_impact": 4,
        "q_followup_ai_nlp": "scientific_nlp",
        "q_followup_math_rigor": "balanced_applied",
    }
    for qid, ans in remaining_answers.items():
        res = client.put(
            f"/api/v1/assessments/sessions/{session_id}/responses",
            json={"question_id": qid, "answer_value": ans},
            headers=headers,
        )
        assert res.status_code == 200

    complete_res = client.post(
        f"/api/v1/assessments/sessions/{session_id}/complete",
        headers=headers,
    )
    assert complete_res.status_code == 200
    completed = complete_res.json()
    assert completed["status"] == "completed"
    assert completed["progress"]["progress_percent"] == 100
    assert completed["completed_at"] is not None

    # Completed sessions reject further edits
    locked_res = client.put(
        f"/api/v1/assessments/sessions/{session_id}/responses",
        json={"question_id": "q_math_comfort", "answer_value": 3},
        headers=headers,
    )
    assert locked_res.status_code == 400


def test_invalid_answer_returns_422(client: TestClient) -> None:
    headers = _auth_headers(client, "invalid_ans@example.edu")
    session_id = client.post("/api/v1/assessments/sessions", headers=headers).json()["id"]

    bad_rating = client.put(
        f"/api/v1/assessments/sessions/{session_id}/responses",
        json={"question_id": "q_math_comfort", "answer_value": 99},
        headers=headers,
    )
    assert bad_rating.status_code == 422

    bad_choice = client.put(
        f"/api/v1/assessments/sessions/{session_id}/responses",
        json={"question_id": "q_problem_solving_style", "answer_value": "nonexistent"},
        headers=headers,
    )
    assert bad_choice.status_code == 422
