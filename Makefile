#################################################################################
# VARIBLES
#################################################################################

PYTHON_INTERPRETER = python
PROJECT_VERSION:=$(shell grep "__version__" data_science_tools/__init__.py | grep -oEi '[0-9\.]+')
LAST_VERSION_TAG:=$(shell git describe --tags $(shell git rev-list --tags --max-count=1) | grep -oEi '[0-9\.]+')
PROJECT_ROOT_PATH:=$(shell git rev-parse --show-toplevel)
MIN_COVERAGE_PERCENT:=70

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
		svg_file = 'docs/badges/coverage.svg'; \
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

## Run mypy type check
type-check:
	mypy --config-file=${PROJECT_ROOT_PATH}/.mypy.ini .

	python -c "print('Generate mypy badge') ;\
		import lxml.html ;\
		report_path = 'docs/reports/mypy-report/index.html' ;\
		badge_path = 'docs/badges/mypy.svg' ;\
		'# Read report path' ;\
		page = lxml.html.parse(report_path) ;\
		text = page.xpath('//body//table[1]//tfoot//tr[1]//th[2]')[0].text ;\
		percentage, _, info = text.partition('%') ;\
		percentage = float(percentage) ;\
		text = format(percentage, '.0f') + _ + info ;\
		'# Read+update badge' ;\
		brightgreen, green, yellow, orange, red = '#4c1', '#97CA00', '#dfb317', '#fe7d37', '#e05d44' ;\
		color = brightgreen if (percentage > 99) else green if (percentage > 75) else yellow if (percentage > 50) else orange if (percentage > 25) else red ;\
		tree = lxml.etree.parse(badge_path) ;\
		ns = {'s': 'http://www.w3.org/2000/svg'} ;\
		tree.xpath('//s:g[2]//s:text', namespaces=ns)[2].attrib['fill'] = color ;\
		tree.xpath('//s:g[2]//s:text', namespaces=ns)[2].text = text ;\
		tree.xpath('//s:g[2]//s:text', namespaces=ns)[3].text = text ;\
		tree.write(badge_path) ;\
		print(text)"

## Run ci/cd checks
ci-cd: test lint type-check version_check

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
