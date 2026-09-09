from fastapi.testclient import TestClient

from backend.api import research as research_api
from backend.main import app


client = TestClient(app)


def test_protected_research_endpoint(monkeypatch):
    email = "researcher@example.com"
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
    token = login.json()["access_token"]

    monkeypatch.setattr(
        research_api.research_graph,
        "invoke",
        lambda *args, **kwargs: {
            "question": "A valid test research question",
            "sub_questions": ["Sub question 1"],
            "research_results": [
                {
                    "question": "Sub question 1",
                    "title": "Example source",
                    "url": "https://example.com",
                    "content": "Example evidence",
                    "score": 0.9,
                    "credibility_label": "Web Source",
                    "credibility_score": 0.55,
                }
            ],
            "contradictions": [],
            "gaps": [],
            "iteration": 0,
            "final_answer": "Test answer [Source 1]",
        },
    )

    response = client.post(
        "/api/research",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "A valid test research question"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["answer"] == "Test answer [Source 1]"
    assert len(data["sources"]) == 1
