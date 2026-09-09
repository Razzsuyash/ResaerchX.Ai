import logging
from typing import Literal

from langgraph.types import Send

from backend.agent.prompts import (
    DECOMPOSE_PROMPT,
    FACT_CHECK_PROMPT,
    SYNTHESIS_PROMPT,
)
from backend.core.config import settings
from backend.services.llm import ask_json, ask_llm
from backend.services.search import search_web
from backend.services.source_quality import assess_source

logger = logging.getLogger(__name__)


DECOMPOSE_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 5,
        }
    },
    "required": ["questions"],
    "additionalProperties": False,
}

FACT_CHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "contradictions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "gaps": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["contradictions", "gaps"],
    "additionalProperties": False,
}


def decompose_node(state):
    prompt = DECOMPOSE_PROMPT.format(question=state["question"])
    data = ask_json(
        prompt,
        name="research_plan",
        schema=DECOMPOSE_SCHEMA,
    )
    questions = [
        q.strip()
        for q in data["questions"]
        if q and q.strip()
    ][: settings.max_sub_questions]

    if not questions:
        raise ValueError("The planner returned no research questions.")

    logger.info("decomposition_completed sub_questions=%d", len(questions))
    return {"sub_questions": questions}


def fanout_initial_research(state):
    return [
        Send("research_single", {"query": question})
        for question in state["sub_questions"]
    ]


def research_single_node(state):
    query = state["query"]
    logger.info("research_started query=%s", query[:120])

    results = search_web(query)
    normalized = []

    for result in results:
        url = result.get("url", "")
        content = (
            result.get("content")
            or result.get("raw_content")
            or ""
        )
        quality_label, quality_score = assess_source(url)
        normalized.append(
            {
                "question": query,
                "title": result.get("title", "Untitled source"),
                "url": url,
                "content": content[: settings.max_content_chars],
                "score": result.get("score"),
                "credibility_label": quality_label,
                "credibility_score": quality_score,
            }
        )

    logger.info("research_completed query=%s results=%d", query[:80], len(normalized))
    return {"research_results": normalized}


def fact_check_node(state):
    # Deduplicate by URL before sending evidence to the model.
    seen = set()
    unique_results = []
    for item in state["research_results"]:
        url = item.get("url", "")
        key = url or f'{item.get("title","")}::{item.get("question","")}'
        if key in seen:
            continue
        seen.add(key)
        unique_results.append(item)

    unique_results = unique_results[: settings.max_sources_for_synthesis]

    research_text = "\n".join(
        f"""
[Source {i + 1}]
Question: {item['question']}
Title: {item['title']}
URL: {item['url']}
Evidence: {item['content']}
"""
        for i, item in enumerate(unique_results)
    )

    data = ask_json(
        FACT_CHECK_PROMPT.format(research=research_text),
        name="fact_check",
        schema=FACT_CHECK_SCHEMA,
    )

    logger.info(
        "fact_check_completed contradictions=%d gaps=%d",
        len(data["contradictions"]),
        len(data["gaps"]),
    )

    return {
        "contradictions": data["contradictions"],
        "gaps": data["gaps"],
    }


def route_after_fact_check(
    state,
) -> Literal["research_again", "synthesize"]:
    if state["iteration"] >= settings.max_research_iterations:
        return "synthesize"

    if state["gaps"] or state["contradictions"]:
        return "research_again"

    return "synthesize"


def research_again_node(state):
    logger.info("research_second_pass_started iteration=%d", state["iteration"] + 1)
    return {"iteration": state["iteration"] + 1}


def fanout_gap_research(state):
    queries = state["gaps"] or state["contradictions"]
    return [
        Send("research_single", {"query": query})
        for query in queries[: settings.max_sub_questions]
    ]


def synthesis_node(state):
    seen = set()
    unique_results = []

    for item in state["research_results"]:
        url = item.get("url", "")
        key = url or f'{item.get("title","")}::{item.get("question","")}'
        if key in seen:
            continue
        seen.add(key)
        unique_results.append(item)

    unique_results = unique_results[: settings.max_sources_for_synthesis]

    research_text = "\n".join(
        f"""
[Source {i + 1}]
Question: {item['question']}
Title: {item['title']}
URL: {item['url']}
Evidence: {item['content']}
"""
        for i, item in enumerate(unique_results)
    )

    answer = ask_llm(
        SYNTHESIS_PROMPT.format(
            question=state["question"],
            research=research_text,
        )
    )

    logger.info("synthesis_completed")
    return {"final_answer": answer}
