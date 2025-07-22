.PHONY: tests lint format

tests:
	@uv run -m pytest --cov --cov-config=.coveragerc  --cov-report term --cov-report xml:./coverage-reports/coverage.xml -s tests/*

lint:
	@uvx ruff check --extend-select I --fix bigdata_briefs/ tests/

lint-check:
	@uvx ruff check --extend-select I bigdata_briefs/ tests/

format:
	@uvx ruff format bigdata_briefs/ tests/
