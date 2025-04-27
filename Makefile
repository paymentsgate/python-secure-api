FILES = paymentsgate


.PHONY: install format lint lint-typing


install:
	poetry config virtualenvs.create true
	poetry config virtualenvs.in-project true
	poetry install --no-interaction

format: install
	poetry run ruff check --fix --fix-only  ${FILES}
	poetry run ruff format ${FILES}

lint: install
	poetry run ruff check ${FILES}
	poetry run ruff format --check ${FILES}

lint-typing: install
	poetry run mypy ${FILES}

