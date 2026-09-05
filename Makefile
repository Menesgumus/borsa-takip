.PHONY: lint test

lint:
	cd backend && uv run ruff check .
	cd backend && uv run mypy app
	cd frontend && pnpm lint

test:
	cd backend && uv run pytest --cov=app tests/
	cd frontend && pnpm vitest run
