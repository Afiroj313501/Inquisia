from fastapi.testclient import TestClient
import httpx
import pytest


def _auth_headers(client: TestClient, email: str = "papers@example.edu") -> dict[str, str]:
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Rosalind Franklin",
            "password": "StrongPassword123!",
        },
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, object]) -> None:
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "Upstream error",
                request=httpx.Request("GET", "https://api.openalex.org/works"),
                response=httpx.Response(self.status_code),
            )

    def json(self) -> dict[str, object]:
        return self._payload


def test_papers_require_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/papers/search?query=rag").status_code == 401
    assert client.get("/api/v1/papers/saved").status_code == 401
    assert (
        client.post(
            "/api/v1/papers/saved",
            json={"openalex_id": "W123", "title": "Paper"},
        ).status_code
        == 401
    )


def test_search_papers_by_topic_id_and_save_lifecycle(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    headers = _auth_headers(client, "openalex_ok@example.edu")

    fake_openalex_payload = {
        "meta": {"count": 1},
        "results": [
            {
                "id": "https://openalex.org/W4200000001",
                "display_name": "Retrieval-Augmented Generation for Scientific Literature",
                "publication_year": 2024,
                "cited_by_count": 42,
                "doi": "https://doi.org/10.1234/rag.2024",
                "authorships": [
                    {"author": {"display_name": "Jane Doe"}},
                    {"author": {"display_name": "John Smith"}},
                ],
                "primary_location": {
                    "source": {"display_name": "ACL Findings"},
                    "landing_page_url": "https://aclanthology.org/example",
                },
                "open_access": {"oa_url": "https://arxiv.org/pdf/2401.00001"},
                "abstract_inverted_index": {
                    "We": [0],
                    "study": [1],
                    "citation-grounded": [2],
                    "retrieval.": [3],
                },
            }
        ],
    }

    captured_params: dict[str, object] = {}

    def fake_get(url: str, params: dict[str, object], timeout: float) -> _FakeResponse:
        captured_params.update(params)
        return _FakeResponse(200, fake_openalex_payload)

    monkeypatch.setattr("app.services.paper_service.httpx.get", fake_get)

    search_res = client.get(
        "/api/v1/papers/search?topic_id=nlp_scientific_rag&limit=5",
        headers=headers,
    )
    assert search_res.status_code == 200
    body = search_res.json()
    assert body["source"] == "OpenAlex"
    assert body["topic_id"] == "nlp_scientific_rag"
    assert "Citation-Grounded" in str(captured_params["search"])
    assert len(body["results"]) == 1

    paper = body["results"][0]
    assert paper["openalex_id"] == "W4200000001"
    assert paper["abstract"] == "We study citation-grounded retrieval."
    assert paper["venue"] == "ACL Findings"
    assert paper["is_saved"] is False

    # Save paper
    save_res = client.post(
        "/api/v1/papers/saved",
        json={
            "openalex_id": paper["openalex_id"],
            "topic_id": "nlp_scientific_rag",
            "title": paper["title"],
            "authors": paper["authors"],
            "publication_year": paper["publication_year"],
            "venue": paper["venue"],
            "cited_by_count": paper["cited_by_count"],
            "doi": paper["doi"],
            "url": paper["url"],
            "open_access_url": paper["open_access_url"],
            "abstract": paper["abstract"],
        },
        headers=headers,
    )
    assert save_res.status_code == 201
    saved_id = save_res.json()["id"]

    # Subsequent search marks paper as saved
    search_again = client.get(
        "/api/v1/papers/search?query=scientific+rag",
        headers=headers,
    )
    assert search_again.status_code == 200
    assert search_again.json()["results"][0]["is_saved"] is True

    # List & delete saved paper
    list_res = client.get("/api/v1/papers/saved", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    del_res = client.delete(f"/api/v1/papers/saved/{saved_id}", headers=headers)
    assert del_res.status_code == 204
    assert client.get("/api/v1/papers/saved", headers=headers).json() == []


def test_search_papers_handles_validation_and_upstream_errors(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    headers = _auth_headers(client, "openalex_err@example.edu")

    assert client.get("/api/v1/papers/search", headers=headers).status_code == 400
    assert (
        client.get("/api/v1/papers/search?topic_id=unknown_topic", headers=headers).status_code
        == 404
    )

    def failing_get(url: str, params: dict[str, object], timeout: float) -> _FakeResponse:
        raise httpx.ConnectError("Network unreachable")

    monkeypatch.setattr("app.services.paper_service.httpx.get", failing_get)
    err_res = client.get("/api/v1/papers/search?query=machine+learning", headers=headers)
    assert err_res.status_code == 502
