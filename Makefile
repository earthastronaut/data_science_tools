#################################################################################
# VARIBLES
#################################################################################

PYTHON_INTERPRETER = python
PROJECT_VERSION:=$(shell grep "__version__" data_science_tools/__init__.py | grep -oEi '[0-9\.]+')
LAST_VERSION_TAG:=$(shell git describe --tags $(shell git rev-list --tags --max-count=1) | grep -oEi '[0-9\.]+')
PROJECT_ROOT_PATH:=$(shell git rev-parse --show-toplevel)
MIN_COVERAGE_PERCENT:=78

#################################################################################
# COMMANDS
#################################################################################

## Install pip python requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Build package into current python
build: version_check
	$(PYTHON_INTERPRETER) -m pip install -e .

## Clean up python files and build artifacts
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "data_science_tools.egg-info" | xargs rm -r $1

## Run unit tests with coverage
test:
	coverage run --rcfile=${PROJECT_ROOT_PATH}/.coveragerc.ini -m unittest discover -v -s data_science_tools
	coverage html --rcfile=${PROJECT_ROOT_PATH}/.coveragerc.ini
	coverage report --rcfile=${PROJECT_ROOT_PATH}/.coveragerc.ini > .coverage.report
	cat .coverage.report
	
	# check coverage and update badge
	echo ${MIN_COVERAGE_PERCENT} | python -c "min_percentage = int(input('')); \
		from xml.etree.ElementTree import ElementTree; \
		percentage = int(open('.coverage.report').read().split('\n')[-2].split()[-1].strip('%')); \
		brightgreen, green, yellow, orange, red = '#4c1', '#97CA00', '#dfb317', '#fe7d37', '#e05d44'; \
		color = brightgreen if (percentage > 99) else green if (percentage > 75) else yellow if (percentage > 50) else orange if (percentage > 25) else red; \
		svg_file = 'docs/coverage.svg'; \
		ns = {'s': 'http://www.w3.org/2000/svg'}; \
		tree = ElementTree(file=svg_file); \
		tree.findall('s:g', ns)[0].findall('s:path', ns)[1].attrib['fill'] = color; \
		tree.findall('s:g', ns)[1].findall('s:text', ns)[2].text = str(percentage) + '%'; \
		tree.findall('s:g', ns)[1].findall('s:text', ns)[3].text = str(percentage) + '%'; \
		tree.write(svg_file); \
		assert percentage >= min_percentage, 'Total {}% less than minimum {}%, please add test coverage'.format(percentage, min_percentage); \
		print('\n\nTests passed with coverage {}% >= {}%'.format(percentage, min_percentage)); \
		"


## Run pylint
lint-pylint:
	pylint --verbose --rcfile=${PROJECT_ROOT_PATH}/.pylintrc.ini ${PROJECT_ROOT_PATH}/data_science_tools

## Run flake8
lint-flake8:
	flake8 --config=${PROJECT_ROOT_PATH}/.flake8.ini ${PROJECT_ROOT_PATH}/data_science_tools

## Run black formatting check
lint-black:
	black --verbose --config=${PROJECT_ROOT_PATH}/.black.toml --check ${PROJECT_ROOT_PATH}/data_science_tools

## Run bandit security check
lint-bandit:
	bandit --verbose --configfile=${PROJECT_ROOT_PATH}/.bandit.yml -r ${PROJECT_ROOT_PATH}/data_science_tools

## Run all linters on python files
lint: lint-pylint lint-flake8 lint-black lint-bandit


mypy:
	echo "TODO: Add type checking via mypy"

## Check project version vs last git tag version
version_check:
	echo "Project=$(PROJECT_VERSION) Tag=$(LAST_VERSION_TAG)"
ifneq ("$(PROJECT_VERSION)", "$(LAST_VERSION_TAG)")
	exit 1
endif

## Create git tag with latest project version
version_tag:
	git tag v$(PROJECT_VERSION)

#################################################################################
# Self Documenting Commands
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
