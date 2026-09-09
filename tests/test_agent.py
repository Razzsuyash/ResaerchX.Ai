from backend.agent.nodes import route_after_fact_check


def test_router_synthesizes_without_gaps():
    state = {
        "iteration": 0,
        "gaps": [],
        "contradictions": [],
    }
    assert route_after_fact_check(state) == "synthesize"


def test_router_researches_when_gap_exists():
    state = {
        "iteration": 0,
        "gaps": ["Need latest data"],
        "contradictions": [],
    }
    assert route_after_fact_check(state) == "research_again"


def test_router_stops_at_iteration_limit(monkeypatch):
    monkeypatch.setattr(
        "backend.agent.nodes.settings.max_research_iterations",
        2,
    )
    state = {
        "iteration": 2,
        "gaps": ["still missing"],
        "contradictions": [],
    }
    assert route_after_fact_check(state) == "synthesize"
