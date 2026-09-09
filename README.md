DeepTrace AI

Agentic Research & Intelligence Platform

A production-oriented Agentic AI research platform that decomposes complex questions, performs parallel web research, validates evidence, detects contradictions and knowledge gaps, iteratively researches missing information, and generates citation-backed answers.









Overview

DeepTrace AI is a backend-first Agentic AI Research Platform built to solve complex research problems using a controlled multi-step AI workflow.

Instead of sending a complex question directly to an LLM, the platform:

Decomposes complex questions

Performs parallel research

Aggregates evidence

Checks facts

Detects contradictions

Identifies knowledge gaps

Performs additional research when required

Synthesizes evidence into a final answer

Preserves research sources

Streams execution progress in real time

Core principle:

LLMs should be components inside a controlled software system, not the entire system itself.

Problem Statement

Traditional LLM applications can depend on outdated knowledge, produce unsupported claims, miss important aspects of complex questions, fail to compare external sources, and provide limited visibility into how an answer was generated.

DeepTrace AI addresses these limitations through an agentic research pipeline.

Traditional Chatbot

User Question
      ↓
     LLM
      ↓
   Answer

DeepTrace AI

User Question
      ↓
Question Decomposition
      ↓
Parallel Research
      ↓
Evidence Collection
      ↓
Fact Checking
      ↓
Contradiction Detection
      ↓
Knowledge Gap Detection
      ↓
Additional Research
      ↓
Evidence Synthesis
      ↓
Citation-Backed Answer

Technology Stack

AI / Agentic AI

Python

LangGraph

OpenRouter

Tavily

Structured LLM outputs

Prompt engineering

Agentic workflows

Retrieval-augmented research

Backend

FastAPI

Pydantic

SQLAlchemy

JWT

Argon2

Server-Sent Events

SlowAPI

Database

PostgreSQL

SQLite for local development

Alembic migrations

Frontend

Streamlit

DevOps

Docker

Docker Compose

AWS deployment architecture

Environment-based configuration

Testing

Pytest

HTTPX

Architecture

                         ┌───────────────────────┐
                         │      Streamlit UI     │
                         │   Research Dashboard  │
                         └───────────┬───────────┘
                                     │
                                  HTTP/SSE
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │        FastAPI        │
                         │ REST API + Auth + SSE │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       LangGraph       │
                         │   Agent Orchestrator  │
                         └───────────┬───────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
                ▼                    ▼                    ▼
        Question Planner      Research Agents       Fact Checker
                                     │                    │
                                     ▼                    │
                                ┌─────────┐               │
                                │ Tavily  │◄──────────────┘
                                └────┬────┘
                                     │
                                     ▼
                            Evidence Collection
                                     │
                                     ▼
                                OpenRouter
                                     │
                                     ▼
                                Synthesis
                                     │
                                     ▼
                               PostgreSQL

Agent Workflow

START
  │
  ▼
Decompose Question
  │
  ▼
Parallel Research
  │
  ▼
Fact Check
  │
  ├───────────────┐
  │               │
  ▼               ▼
Research Again   Synthesis
  │               │
  │               ▼
  └────────────► END

1. Question Decomposition

Example:

What is the future of electric vehicles in India?

May become:

Q1 → What is the current EV adoption rate in India?
Q2 → What is the current charging infrastructure?
Q3 → What are the economic advantages and disadvantages?
Q4 → What government policies are affecting EV adoption?
Q5 → What is the expected future market trend?

Configuration:

MAX_SUB_QUESTIONS=5

2. Parallel Research

LangGraph's Send mechanism dynamically fans out independent research tasks.

                    Question
                       │
                  Decomposer
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Research Q1  Research Q2  Research Q3
          │            │            │
          ▼            ▼            ▼
        Tavily       Tavily       Tavily
          │            │            │
          └────────────┼────────────┘
                       ▼
                  Fact Checker

3. Web Research

Each branch:

Receives a sub-question

Executes web search

Retrieves relevant sources

Extracts useful content

Stores source metadata

Sends evidence to the next stage

MAX_SEARCH_RESULTS=5
MAX_CONTENT_CHARS=6000

4. Evidence Aggregation

The LangGraph state tracks:

question
sub_questions
research_results
contradictions
gaps
iteration
final_answer

5. Fact Checking

The fact-checking stage analyzes:

Contradictory claims

Missing evidence

Research gaps

Incomplete coverage

Conflicting source information

Example:

{
  "contradictions": [
    "Source A reports different figures than Source B."
  ],
  "gaps": [
    "Recent charging infrastructure data is missing."
  ]
}

6. Adaptive Research

Fact Check
    │
    ├── Evidence sufficient
    │          │
    │          ▼
    │      Synthesis
    │
    └── Evidence insufficient
               │
               ▼
        Generate New Queries
               │
               ▼
          Tavily Search
               │
               ▼
           Fact Check

7. Bounded Execution

MAX_RESEARCH_ITERATIONS=2
GRAPH_RECURSION_LIMIT=50

These limits help prevent infinite loops, excessive API usage, unexpected LLM costs, and runaway execution.

8. Final Synthesis

The synthesis stage receives:

Original Question
      +
Sub Questions
      +
Research Evidence
      +
Contradictions
      +
Knowledge Gaps

and generates:

Final Research Answer
      +
Source Attribution

LLM Architecture

DeepTrace AI uses OpenRouter through an OpenAI-compatible client interface.

The LLM layer is isolated behind service functions such as:

ask_llm()
ask_json()

Example:

OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=google/gemini-3.1-flash-lite

The model can be changed through configuration without rewriting the LangGraph workflow.

Structured Outputs

Structured JSON responses are used where predictable machine-readable output is required.

Benefits:

Predictable schema

Easier validation

Better error handling

Cleaner agent state

Reduced parsing failures

Retry Strategy

Important LangGraph nodes use retry policies.

Decomposition
Research
Fact Checking
Synthesis

Maximum attempts = 2

Source Quality

The platform includes heuristic source-quality scoring:

Government             → 0.95
Academic               → 0.95
Research Institution   → 0.90
Major News             → 0.85
General Web Source     → 0.55
Unknown                → 0.30

These values are heuristics and are not guarantees of factual accuracy.

FastAPI Backend

FastAPI provides the backend API boundary.

Responsibilities:

Authentication
Research APIs
Streaming
Database access
Validation
Rate limiting
Logging
Health checks
Error handling

API Endpoints

Authentication

POST /api/auth/register
POST /api/auth/login

Research

POST   /api/research
POST   /api/research/stream
GET    /api/research
GET    /api/research/{session_id}
DELETE /api/research/{session_id}

System

GET /health
GET /ready

Swagger:

http://localhost:8000/docs

Server-Sent Events

Research is a long-running workflow, so the backend exposes SSE streaming.

Example:

event: started

event: progress
data: {"node":"decompose","status":"completed"}

event: progress
data: {"node":"research_single","status":"completed"}

event: progress
data: {"node":"fact_check","status":"completed"}

event: progress
data: {"node":"research_again","status":"completed"}

event: progress
data: {"node":"synthesize","status":"completed"}

event: completed
data: {"status":"completed"}

This enables real-time progress monitoring.

Frontend

The Streamlit dashboard provides:

Registration and login

JWT session handling

Research input

Research history

Real-time progress

Final answer display

Sub-question inspection

Contradiction display

Knowledge-gap display

Source inspection

Source-quality information

LangGraph workflow visualization

Database

SQLAlchemy is used as the ORM.

Relationship:

Users
  │
  └──── Research Sessions
               │
               └──── Research Sources

Users

users
├── id
├── email
├── hashed_password
├── is_active
└── created_at

Research Sessions

research_sessions
├── id
├── user_id
├── question
├── status
├── answer
├── sub_questions
├── contradictions
├── gaps
├── iterations
├── error_message
├── created_at
└── completed_at

Research Sources

research_sources
├── id
├── session_id
├── question
├── title
├── url
├── content
├── score
├── credibility_label
└── credibility_score

Sources are persisted independently from the final answer to preserve research provenance.

Migrations

alembic upgrade head

Alembic provides version-controlled database schema changes.

Authentication & Authorization

Authentication uses:

JWT
+
Argon2
+
FastAPI dependencies

Flow:

Register
   ↓
Hash Password
   ↓
Store User
   ↓
Login
   ↓
Verify Password
   ↓
Generate JWT
   ↓
Authenticated Requests

Research sessions are associated with users so users can access only their own sessions.

Rate Limiting

SlowAPI is used for request rate limiting.

RATE_LIMIT_AUTH=5/minute
RATE_LIMIT_RESEARCH=10/minute

For multi-instance production deployments, use a shared Redis-backed rate limiter.

Logging & Error Handling

Requests receive identifiers for correlation across backend activity.

The API handles:

LLM timeouts
Tavily failures
Database failures
Invalid authentication
Rate-limit violations
Malformed requests
Agent execution failures

Failures are converted into controlled API responses.

Configuration

Example .env:

OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=google/gemini-3.1-flash-lite

TAVILY_API_KEY=your_tavily_key

DATABASE_URL=sqlite:///./research.db

JWT_SECRET_KEY=your_secret_key

MAX_RESEARCH_ITERATIONS=2
MAX_SUB_QUESTIONS=5
MAX_SEARCH_RESULTS=5
MAX_SOURCES_FOR_SYNTHESIS=20
MAX_CONTENT_CHARS=6000
GRAPH_RECURSION_LIMIT=50

Never commit real API keys or secrets.

Local Development

1. Clone

git clone <your-repository-url>
cd deep-research-agent

2. Create Virtual Environment

Python 3.11+ is recommended.

python3.12 -m venv venv

macOS / Linux:

source venv/bin/activate

Windows:

venv\Scriptsctivate

3. Install Dependencies

pip install -r requirements.txt

4. Configure Environment

cp .env.example .env

Add your OpenRouter and Tavily API keys.

5. Initialize Database

alembic upgrade head

6. Start Backend

uvicorn backend.main:app --reload

7. Start Frontend

In another terminal:

streamlit run frontend/app.py

Local URLs

Backend  → http://localhost:8000
Swagger  → http://localhost:8000/docs
Frontend → http://localhost:8501

Docker

Start the complete stack:

docker compose up --build

Services:

FastAPI      → localhost:8000
Streamlit    → localhost:8501
PostgreSQL   → localhost:5432

Stop:

docker compose down

Architecture:

Docker Compose
│
├── PostgreSQL
│
├── FastAPI
│    ├── LangGraph
│    ├── OpenRouter
│    └── Tavily
│
└── Streamlit

Project Structure

deep-research-agent/
│
├── backend/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   └── research.py
│   │
│   ├── agent/
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── prompts.py
│   │   └── state.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── rate_limit.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── init_db.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   └── services/
│       ├── auth.py
│       ├── llm.py
│       ├── repository.py
│       ├── search.py
│       └── source_quality.py
│
├── frontend/
│   └── app.py
│
├── tests/
│   ├── conftest.py
│   ├── test_agent.py
│   ├── test_auth.py
│   ├── test_health.py
│   ├── test_research_api.py
│   └── test_research_node.py
│
├── alembic/
│   ├── env.py
│   └── versions/
│
├── Dockerfile.api
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

Testing

Run:

pytest

Tests cover:

Health endpoints
Authentication
Agent graph
Research nodes
Research API

External LLM and search services should be mocked during unit testing.

Performance Benchmarking

The benchmark workflow measures:

P50 latency
P95 latency
P99 latency
Minimum latency
Average latency
Maximum latency
Requests / second
Success rate
Concurrent users
Total test duration

Example:

python benchmark.py   --token "YOUR_JWT_TOKEN"   --requests 5   --concurrency 1

Additional:

python benchmark.py   --token "YOUR_JWT_TOKEN"   --requests 10   --concurrency 2

Higher-load:

python benchmark.py   --token "YOUR_JWT_TOKEN"   --requests 20   --concurrency 5

Do not exceed the configured research rate limit during testing.

Performance Reporting

Only report measured numbers from actual load tests.

Recommended format:

Concurrent Users : N
Requests         : N
Success Rate     : X%
Requests/sec     : X
P50 Latency      : X sec
P95 Latency      : X sec
P99 Latency      : X sec

For AI workloads also measure:

Time to First SSE Event
LLM Latency
Search Latency
Total Agent Execution Time

Production Architecture

                         Internet
                            │
                            ▼
                    HTTPS Load Balancer
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
        FastAPI Replica 1           FastAPI Replica N
              │                           │
              └─────────────┬─────────────┘
                            ▼
                     Redis / Queue
                            │
                            ▼
                    Research Workers
                            │
                         LangGraph
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
             OpenRouter             Tavily
                  │                   │
                  └─────────┬─────────┘
                            ▼
                       PostgreSQL

AWS Deployment

Recommended AWS components:

ECS / Fargate       → Application containers
ALB                 → HTTPS + load balancing
RDS PostgreSQL      → Persistent database
ElastiCache Redis   → Cache / shared rate limiting
SQS                 → Research job queue
Secrets Manager     → API secrets
CloudWatch          → Logs and monitoring
ECR                 → Docker images

Queue-Based Scaling

Long-running research workloads can be moved to dedicated workers:

Client
  ↓
FastAPI
  ↓
Create Research Job
  ↓
Queue
  ↓
Worker
  ↓
LangGraph
  ↓
OpenRouter + Tavily
  ↓
PostgreSQL
  ↓
Client receives result

This prevents long-running AI workflows from blocking API workers.

Scaling Strategy

Initial

Client
  ↓
FastAPI
  ↓
LangGraph
  ↓
OpenRouter + Tavily
  ↓
PostgreSQL

Scaled

Client
  ↓
Load Balancer
  ↓
FastAPI Replicas
  ↓
Redis / Queue
  ↓
Research Workers
  ↓
LangGraph
  ├── OpenRouter
  └── Tavily
  ↓
PostgreSQL

Each layer can scale independently.

Caching Strategy

Redis can be introduced for:

Repeated search queries
Research result caching
Metadata caching
Distributed rate limiting
Job state
Distributed locks

Caching repeated research can reduce unnecessary external API calls.

Observability

Production monitoring should track:

Request ID
Session ID
Node execution time
LLM latency
Search latency
Token usage
Research iterations
Source count
Error rate
P50 latency
P95 latency
P99 latency

Potential tools:

OpenTelemetry
Prometheus
Grafana
Sentry
LangSmith
CloudWatch

Production Security Checklist

[ ] HTTPS enabled
[ ] Strong JWT secret
[ ] API keys stored securely
[ ] CORS restricted
[ ] Database credentials secured
[ ] Rate limiting enabled
[ ] Authentication enabled
[ ] Authorization verified
[ ] Request validation enabled
[ ] Database backups configured
[ ] Logging enabled
[ ] Monitoring enabled
[ ] Error tracking enabled
[ ] Dependency vulnerabilities scanned
[ ] Load testing completed
[ ] API costs monitored

Cost Control

Agentic systems can generate more API calls than traditional LLM applications.

DeepTrace AI controls cost through:

Maximum sub-question limit
Maximum search result limit
Maximum research iterations
Maximum synthesis sources
Maximum content length
LLM output token limits
API rate limiting
Retry limits

Reliability Design

Retry Policies
      +
Timeouts
      +
Bounded Agent Loops
      +
Structured Outputs
      +
Input Validation
      +
Rate Limiting
      +
Health Checks
      +
Database Persistence

Engineering Decisions

Why LangGraph?

The workflow requires stateful execution, parallel branches, conditional routing, iterative research, shared state, and controlled termination.

Why FastAPI?

FastAPI provides a clean backend boundary, validation, dependency injection, automatic OpenAPI documentation, and async support.

Why OpenRouter?

OpenRouter provides a unified model gateway and reduces tight coupling between the agent workflow and a specific LLM provider.

Why Tavily?

The system requires current external information. Tavily provides the retrieval layer while the LLM handles reasoning, verification, and synthesis.

Why PostgreSQL?

PostgreSQL provides durable persistence, relational integrity, transactions, structured querying, and production scalability.

Why SSE?

Research is a long-running workflow. SSE allows the frontend to receive progress updates without continuously polling the backend.

Why Structured Outputs?

Structured responses provide predictable schemas that improve validation, routing, reliability, and debugging.

Why Bounded Iterations?

Bounded iterations prevent infinite research loops and establish predictable execution and cost limits.

Engineering Challenges Solved

Complex Questions

Question Decomposition
+
Parallel Research

Conflicting Information

Fact Checker
+
Contradiction Detection

Missing Evidence

Gap Detection
+
Adaptive Research

Long-Running Requests

SSE Streaming

External API Failures

Retries
+
Timeouts
+
Controlled Error Handling

Infinite Agent Loops

Iteration Limits
+
Graph Recursion Limits

API Security

JWT
+
Argon2
+
Rate Limiting
+
Authorization

Persistent Research

PostgreSQL
+
SQLAlchemy
+
Alembic

RAG vs Agentic Research

Traditional RAG

Query
 ↓
Retriever
 ↓
Documents
 ↓
LLM
 ↓
Answer

DeepTrace AI

Complex Query
 ↓
Planner
 ↓
Multiple Research Tasks
 ↓
Parallel Retrieval
 ↓
Evidence Aggregation
 ↓
Fact Checker
 ↓
Contradiction Detection
 ↓
Gap Detection
 ↓
Additional Research
 ↓
Synthesis
 ↓
Citation-backed Answer

DeepTrace AI therefore demonstrates agentic orchestration rather than simple retrieval.

Example End-to-End Flow

POST /api/research
        │
        ▼
Authenticate User
        │
        ▼
Validate Request
        │
        ▼
Create Research Session
        │
        ▼
LangGraph START
        │
        ▼
Decompose
        │
        ▼
Parallel Research
        │
        ▼
Tavily
        │
        ▼
Aggregate Evidence
        │
        ▼
Fact Check
        │
        ├───────────────┐
        │               │
        ▼               ▼
    More Research    Synthesis
        │               │
        ▼               ▼
      Tavily         OpenRouter
        │               │
        └───────┬───────┘
                ▼
          Save Results
                │
                ▼
        Return Final Answer

Example Research

Input:

How will AI affect software engineering jobs over the next five years?

Possible decomposition:

1. Current AI adoption in software engineering
2. Impact on junior developer roles
3. Impact on senior engineering roles
4. AI productivity trends
5. Future hiring trends

Research branches gather evidence independently.

The fact checker evaluates:

Contradictions
Missing evidence
Conflicting statistics
Insufficient coverage

If required, another research cycle is triggered.

Final flow:

Evidence
   ↓
Synthesis
   ↓
Final Answer
   ↓
Sources

Current Configuration

Maximum sub-questions       : 5
Search results per branch   : 5
Maximum research iterations : 2
Sources for synthesis       : 20
Maximum content characters  : 6000
Graph recursion limit       : 50
Research rate limit         : 10/min
Authentication rate limit   : 5/min

Production Readiness

DeepTrace AI is production-oriented and deployable, but should not be described as fully production-certified.

Before significant production scale, add:

Advanced observability
Distributed rate limiting
Queue-based workers
Database backups
Secrets management
Load testing
Autoscaling
Network security
CI/CD
Dependency scanning
Disaster recovery
Cost monitoring

Future Improvements

[ ] Redis-based distributed rate limiting
[ ] SQS/Celery research workers
[ ] WebSocket support
[ ] React/Next.js frontend
[ ] Streaming token-level responses
[ ] Advanced source ranking
[ ] Semantic deduplication
[ ] Vector database
[ ] Research result caching
[ ] Multi-user organizations
[ ] Team workspaces
[ ] Usage analytics
[ ] LLM cost tracking
[ ] OpenTelemetry tracing
[ ] LangSmith tracing
[ ] Prometheus metrics
[ ] Grafana dashboards
[ ] Automated evaluation pipeline
[ ] Human feedback loop

Resume Positioning

Project

DeepTrace AI | Agentic Research & Intelligence Platform

Stack

Python, FastAPI, LangGraph, OpenRouter, Tavily,
SQLAlchemy, PostgreSQL, Docker, Streamlit,
JWT, SSE, Alembic

Resume Bullet 1

Engineered a production-oriented agentic research backend using FastAPI and LangGraph, decomposing complex queries into parallel research tasks and dynamically routing workflows based on evidence gaps and source conflicts.

Resume Bullet 2

Integrated Tavily and OpenRouter for web retrieval, structured fact checking, contradiction detection, iterative research, and citation-aware synthesis with bounded agent execution.

Resume Bullet 3

Built JWT authentication, PostgreSQL persistence, SSE streaming, rate limiting, health checks, retry policies, and Docker deployment, with a Streamlit dashboard for real-time research monitoring.

Short Version

Built DeepTrace AI, a LangGraph-powered agentic research platform using FastAPI, OpenRouter and Tavily for parallel web research, contradiction detection, iterative evidence gathering and citation-backed synthesis.

Interview Explanation

DeepTrace AI is an agentic research platform I built using FastAPI and LangGraph. Instead of sending a complex question directly to an LLM, the system first decomposes it into multiple research tasks and executes them in parallel using Tavily. The collected evidence is then passed through a fact-checking stage that detects contradictions and missing information. If gaps are identified, LangGraph dynamically routes the workflow back into another research cycle. Once sufficient evidence is available, OpenRouter is used to synthesize a citation-backed final response. I also added JWT authentication, PostgreSQL persistence, SSE streaming, rate limiting, retries, health checks, and Docker support to make the system backend and production oriented.

Skills Demonstrated

AI / GenAI

Agentic AI

LLM orchestration

LangGraph

Prompt engineering

Structured outputs

Retrieval-augmented workflows

Source verification

Multi-step reasoning

Backend

Python

FastAPI

REST APIs

Server-Sent Events

JWT

Pydantic

SQLAlchemy

PostgreSQL

API security

Rate limiting

Systems

Parallel task execution

Stateful workflows

Retry strategies

Bounded execution

Queue-based scaling

Caching strategy

Stateless API design

DevOps

Docker

Docker Compose

Alembic

CI/CD

Health checks

Production configuration

Observability architecture

Project Summary

DeepTrace AI demonstrates how to build a complete Agentic AI backend system rather than a simple LLM wrapper.

The system combines:

LLM Reasoning
      +
Web Retrieval
      +
Agent Orchestration
      +
Parallel Execution
      +
Evidence Verification
      +
Adaptive Research
      +
Backend APIs
      +
Authentication
      +
Database Persistence
      +
Real-Time Streaming
      +
Rate Limiting
      +
Docker
      +
Cloud Architecture

Final architecture:

Complex Question
       ↓
LangGraph Planner
       ↓
Parallel Research
       ↓
Tavily
       ↓
Evidence Aggregation
       ↓
Fact Checker
       ↓
Contradictions / Gaps
       ↓
Adaptive Research
       ↓
OpenRouter
       ↓
Citation-Backed Synthesis
       ↓
PostgreSQL
       ↓
FastAPI / SSE
       ↓
Streamlit

DeepTrace AI

Agentic Research & Intelligence Platform

Built with Python, FastAPI, LangGraph, OpenRouter, Tavily, PostgreSQL, SQLAlchemy, Docker, Streamlit, JWT, SSE and Alembic.

Research intelligently. Verify evidence. Detect contradictions. Adapt the workflow. Synthesize grounded answers