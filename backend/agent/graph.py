from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from backend.agent.nodes import (
    decompose_node,
    fanout_gap_research,
    fanout_initial_research,
    fact_check_node,
    research_again_node,
    research_single_node,
    route_after_fact_check,
    synthesis_node,
)
from backend.agent.state import ResearchState


builder = StateGraph(ResearchState)

builder.add_node(
    "decompose",
    decompose_node,
    retry_policy=RetryPolicy(max_attempts=2),
)
builder.add_node(
    "research_single",
    research_single_node,
    retry_policy=RetryPolicy(max_attempts=2),
)
builder.add_node(
    "fact_check",
    fact_check_node,
    retry_policy=RetryPolicy(max_attempts=2),
)
builder.add_node("research_again", research_again_node)
builder.add_node(
    "synthesize",
    synthesis_node,
    retry_policy=RetryPolicy(max_attempts=2),
)

builder.add_edge(START, "decompose")

builder.add_conditional_edges(
    "decompose",
    fanout_initial_research,
    ["research_single"],
)

builder.add_edge("research_single", "fact_check")

builder.add_conditional_edges(
    "fact_check",
    route_after_fact_check,
    {
        "research_again": "research_again",
        "synthesize": "synthesize",
    },
)

builder.add_conditional_edges(
    "research_again",
    fanout_gap_research,
    ["research_single"],
)

builder.add_edge("synthesize", END)

research_graph = builder.compile()
