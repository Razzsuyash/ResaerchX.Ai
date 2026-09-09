from backend.agent import nodes


def test_research_single_normalizes_results(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "search_web",
        lambda query: [
            {
                "title": "Example",
                "url": "https://example.com",
                "content": "Evidence",
                "score": 0.9,
            }
        ],
    )

    result = nodes.research_single_node({"query": "test query"})

    assert len(result["research_results"]) == 1
    assert result["research_results"][0]["title"] == "Example"
    assert result["research_results"][0]["score"] == 0.9
