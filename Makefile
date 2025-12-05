.PHONY: build up down logs clean test example

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -f transcriptions.db

rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

test:
	curl http://localhost:8000/health

example:
	uv run python example_usage.py

install:
	python -m uv sync

dev:
	uv run uvicorn app.main:app --reload --port 8000
