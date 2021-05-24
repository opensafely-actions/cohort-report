SHELL := /bin/bash

define USAGE
Run commands for a project

Commands:
	format    Runs black and isort over all python files
	lint      Lint all python files using flake8

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
