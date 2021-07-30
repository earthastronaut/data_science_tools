#################################################################################
# VARIABLES
#################################################################################

SHELL=/bin/bash
# PROJECT_VERSION:=$(shell head -n 1 data_science_tools/__version__)
# LAST_VERSION_TAG:=$(shell git describe --tags $(shell git rev-list --tags --max-count=1) | grep -oEi '[0-9\.]+')
VERSION=$(shell git describe --tags)
GIT_STATUS_SUMMARY=$(shell git status --porcelain)

#################################################################################
# COMMANDS
#################################################################################

# Build distribution
build:
	@echo "Check that directory is clean. Please commit all changes."
	[ "${GIT_STATUS_SUMMARY}" = "" ]  # [ "$$(git status --porcelain)" = "" ]
	@echo ${VERSION} > data_science_tools/__version__
	source activate.sh && python setup.py sdist bdist_wheel

## Clean up python files and build artifacts
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "data_science_tools.egg-info" | xargs rm -r $1
	rm -rf dist && true
	rm -rf build && true
	rm -rf .venv && true

## Run unit tests with coverage
test:
	source activate.sh && test-coverage.sh data_science_tools

## Run unit tests with dev
test-dev:
	source activate.sh && test.sh --pdb data_science_tools

## Run all linters on python files
lint:
	source activate.sh \
		&& pylint.sh data_science_tools \
		&& flake8.sh data_science_tools \
		&& black.sh --check data_science_tools

## Run mypy type check
type-check:
	source activate.sh && mypy.sh data_science_tools

## Check all
check: test lint type-check

## Display version
version:
	@echo ${VERSION}

#################################################################################
# Self Documenting Commands
#################################################################################

# Show this message
help:
	@echo ""
	@echo "Usage: make <target>"
	@echo "Targets:"
	@grep -E "^[a-z,A-Z,0-9,-]+:.*" Makefile | sort | cut -d : -f 1 | xargs printf '  %s\n'
	@echo ""

.DEFAULT_GOAL=help
.PHONY: build check clean help lint test-dev test type-check version
# echo .PHONY: $(grep -E "^[a-z,A-Z,0-9,-]+:.*" Makefile | sort | cut -d : -f 1 | xargs)
