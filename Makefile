.PHONY: install run-api run-ui test lint migrate docker-up docker-down

install:
	pip install -r requirements.txt

run-api:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	streamlit run frontend/app.py

test:
	pytest -q

migrate:
	alembic upgrade head

docker-up:
	docker compose up --build

docker-down:
	docker compose down
