SOURCE_DIR = ./dirtocgen

.PHONY: format
format:
	poetry run black .
	poetry run isort .

.PHONY: lint
lint:
	poetry run mypy .
	poetry run pflake8 . --statistics

.PHONY: test
test:
	PYTHONPATH=$(SOURCE_DIR) poetry run coverage run -m unittest discover && \
	poetry run coverage report -m
