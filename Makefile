SHELL := /bin/bash

define USAGE
Run commands for a project

Commands:
	coverage  Reports unit test coverage across python files
	format    Runs black and isort over all python files
	lint      Lint all python files using flake8 and lints `src/Dockerfile` using hadolint
	setup     Install Python dependencies with virtualenv
	test      Run linters, test db migrations and tests
	typehint  Run mypy over project and check for typehints
	update    Updates the requirements.txt using piptools from the requirements.in file

endef

export USAGE

help:
	@echo "$$USAGE"

.PHONY: lint
lint:
	@echo "Running flake8" && \
		flake8 \
		|| exit 1

.PHONY: format
format:
	@echo "Running black" && \
		black --check . && \
		echo "Running isort" && \
		isort . \
		|| exit 1
