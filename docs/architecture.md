# Architecture

## Request path

```text
Streamlit
   |
   | POST /api/research/stream
   v
FastAPI
   |
   +-- JWT authentication
   +-- Pydantic validation
   +-- rate limiting
   |
   v
LangGraph
   |
   +--> decompose
   |
   +--> parallel research_single workers
   |       |
   |       +--> Tavily
   |
   +--> fact_check
   |
   +--> conditional route
   |       |
   |       +--> research_again
   |       |
   |       +--> synthesize
   |
   v
PostgreSQL
```

## Why this design?

- FastAPI is transport/API infrastructure.
- LangGraph owns agent orchestration.
- Service modules isolate external providers.
- SQLAlchemy isolates persistence.
- Streamlit is only a client.
- PostgreSQL gives durable research history.
- SSE exposes graph progress without coupling UI to LangGraph internals.

## Scaling path

```text
                 Load Balancer
                       |
                 FastAPI replicas
                       |
                    Redis
                  /       \
            rate limit    queue
                           |
                       workers
                           |
                       LangGraph
                       /       \
                   OpenAI     Tavily
                           |
                       PostgreSQL
```
