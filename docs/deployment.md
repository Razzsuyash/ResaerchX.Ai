# Deployment

## Local

```bash
cp .env.example .env
# add OPENAI_API_KEY, TAVILY_API_KEY and JWT_SECRET_KEY

alembic upgrade head

uvicorn backend.main:app --host 0.0.0.0 --port 8000
streamlit run frontend/app.py
```

## Docker

```bash
cp .env.example .env
docker compose up --build
```

## Production checklist

- [ ] Use managed PostgreSQL.
- [ ] Store secrets in a secret manager.
- [ ] Use HTTPS.
- [ ] Set a strong random JWT secret.
- [ ] Restrict `ALLOWED_ORIGINS`.
- [ ] Run `alembic upgrade head` during deployment.
- [ ] Configure database backups.
- [ ] Configure API and worker autoscaling.
- [ ] Configure request/LLM/search timeouts.
- [ ] Add Redis-backed rate limiting for multiple replicas.
- [ ] Add centralized logs.
- [ ] Add metrics and tracing.
- [ ] Add CI/CD.
- [ ] Add dependency/security scanning.
- [ ] Add queue-backed workers for long research jobs.
- [ ] Configure health and readiness checks.
- [ ] Configure a reverse proxy/load balancer.

## AWS

Recommended production components:

- ECS/Fargate for API and worker containers
- RDS PostgreSQL
- ElastiCache Redis
- Application Load Balancer
- Secrets Manager
- CloudWatch
- ECR
- S3 for optional exports/artifacts

Do not expose PostgreSQL publicly.
