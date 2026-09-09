import operator
from typing import Annotated, TypedDict


class ResearchState(TypedDict):
    question: str
    sub_questions: list[str]
    research_results: Annotated[list[dict], operator.add]
    contradictions: list[str]
    gaps: list[str]
    iteration: int
    final_answer: str


class ResearchWorkerState(TypedDict):
    query: str
