# Interview Guide

## 1. Explain the project

"I built a backend-first multi-step research agent using FastAPI and LangGraph. FastAPI handles authentication, validation and API requests, while LangGraph orchestrates decomposition, parallel web research, fact checking, conditional re-research and synthesis. Tavily provides current web evidence and OpenAI handles reasoning and synthesis. PostgreSQL stores user accounts, research sessions and sources. Streamlit consumes the API and displays live SSE progress."

## 2. Why LangGraph?

The workflow is not purely linear. It needs fan-out, shared state, conditional routing and bounded loops. LangGraph models those concepts directly.

## 3. Why FastAPI?

It decouples the AI workflow from the UI and makes the system reusable by other clients.

## 4. How is research parallelized?

The decomposition node creates a list of sub-questions. A conditional edge returns LangGraph `Send` objects, creating one research task per question.

## 5. How are loops controlled?

The graph stores an iteration counter. Once the configured maximum is reached, routing always goes to synthesis.

## 6. How do you handle conflicting evidence?

The fact-checker creates contradiction and gap lists. Those become targeted research queries for another pass.

## 7. What happens if Tavily fails?

The API catches graph exceptions, marks the research session failed, logs the request/session context and returns a generic 503 response instead of leaking provider errors.

## 8. How would you scale it?

Keep FastAPI stateless, put long-running graph executions behind a queue, run worker replicas, use Redis for shared rate limiting/cache, and use PostgreSQL for durable state.

## 9. How do you test an LLM application?

Unit-test routing and transformation logic. Mock provider calls for deterministic tests. Add integration tests separately with controlled API credentials and evaluation datasets.

## 10. What would you improve next?

- Better source ranking and corroboration
- Async provider clients
- Queue-backed execution
- Redis
- LangGraph checkpoint persistence
- OpenTelemetry
- LangSmith
- Evaluation/benchmark suite
- Human approval for high-impact research
