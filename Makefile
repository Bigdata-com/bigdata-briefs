.PHONY: tests lint format

RUFF_VERSION := 0.15.22
TY_VERSION := 0.0.89

tests:
	@uv run -m pytest --cov --cov-config=.coveragerc  --cov-report term --cov-report xml:./coverage-reports/coverage.xml -s tests/*

lint:
	@uvx ruff@$(RUFF_VERSION) check --extend-select I --fix bigdata_briefs/ tests/

lint-check:
	@uvx ruff@$(RUFF_VERSION) check --extend-select I bigdata_briefs/ tests/

format:
	@uvx ruff@$(RUFF_VERSION) format bigdata_briefs/ tests/

type-check:
	@uvx ty@$(TY_VERSION) check bigdata_briefs/ tests/