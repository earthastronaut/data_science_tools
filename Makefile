#################################################################################
# VARIABLES
#################################################################################

SHELL=/bin/bash
PROJECT_VERSION:=$(shell head -n 1 data_science_tools/__version__)
# LAST_VERSION_TAG:=$(shell git describe --tags $(shell git rev-list --tags --max-count=1) | grep -oEi '[0-9\.]+')
GIT_TAG=$(shell git describe --abbrev=0 --tags)
GIT_STATUS_SUMMARY=$(shell git status --porcelain)

#################################################################################
# COMMANDS
#################################################################################

# Build distribution
build:
	@echo "Check that directory is clean. Please commit all changes."
	[ "${GIT_STATUS_SUMMARY}" = "" ]  # [ "$$(git status --porcelain)" = "" ]
	@echo 'Check that tag is current. Run `make git-tag` to add tag.'
	[ "${GIT_TAG}" = "${PROJECT_VERSION}" ]  # [ "$$(git describe --abbrev=0 --tags)" = "$$(make version)" ]
	source activate.sh && python setup.py sdist bdist_wheel


## Clean up python files and build artifacts
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "data_science_tools.egg-info" | xargs rm -r $1
	rm -rf .venv

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

## Display version
version:
	@echo ${PROJECT_VERSION}

## Create git tag with latest project version
version-tag:
	git tag $(PROJECT_VERSION)

#################################################################################
# Self Documenting Commands
#################################################################################

# Show this message
help:
	@echo ""
	@echo "Usage: make <target>\n"
	@echo "Targets:\n"
	@grep -E "^[a-z,A-Z,0-9,-]+:.*" Makefile | sort | cut -d : -f 1 | xargs printf '  %s\n'
	@echo ""

.DEFAULT_GOAL=help
.PHONY: build ci-cd clean help lint-bandit lint-black lint-flake8 lint-pylint lint requirements test type-check
# .PHONY: grep -E "^[a-z,A-Z,0-9,-]+:.*" Makefile | sort | cut -d : -f 1 | xargs 
