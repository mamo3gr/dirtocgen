SOURCE_DIR = ./dirtocgen

.PHONY: test
test:
	PYTHONPATH=$(SOURCE_DIR) poetry run coverage run -m unittest discover && \
	poetry run coverage report -m
