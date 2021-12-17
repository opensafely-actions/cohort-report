SHELL := /bin/bash

define USAGE
Run commands for a project

Commands:
	check    	Runs black, isort, and flake8 over all Python files but does not make changes
	dev_setup  	Sets up development environment
	fix      	Runs black and isort over all Python files and makes changes
	test		Runs tests
	typehint  	Runs mypy over code base with --ignore-missing-imports flag
	update		Updates environment. Must be passed either dev or prod as the argument

endef

export USAGE

help:
	@echo "$$USAGE"

.PHONY: check
check:
	@echo "Checking Python files" && \
		sh scripts/check \
		|| exit 1

.PHONY: dev_setup
dev_setup:
	@echo "Setting up dev environment" && \
		sh scripts/dev_setup \
		|| exit 1

.PHONY: fix
fix:
	@echo "Fixing Python files" && \
		sh scripts/fix \
		|| exit 1

.PHONY: test
test:
	@echo "Running tests" && \
		sh scripts/test \
		|| exit 1

.PHONY: update
update:
	@echo "Updating environment" && \
		sh scripts/update $(filter-out $@,$(MAKECMDGOALS)) \
		|| exit 1

.PHONY: typehint
typehint:
	mypy --ignore-missing-imports --exclude='$(VIRTUAL_ENV)' ./
