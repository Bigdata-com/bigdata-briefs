.PHONY: tests lint format

tests:
	@uv run -m pytest -s tests/*

lint:
	@uvx ruff check --extend-select I --fix bigdata_briefs/

format:
	@uvx ruff format bigdata_briefs/
