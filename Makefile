
#################################################################################
# VARIBLES
#################################################################################

PYTHON_INTERPRETER = python
PROJECT_VERSION:=$(shell grep "__version__" data_science_tools/__init__.py | grep -oEi '[0-9\.]+')
LAST_VERSION_TAG:=$(shell git describe --tags $(git rev-list --tags --max-count=1) | grep -oEi '[0-9\.]+')

#################################################################################
# COMMANDS
#################################################################################

requirements:
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

build: version_check
	$(PYTHON_INTERPRETER) -m pip install -e .

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "data_science_tools.egg-info" | xargs rm -r $1

test:
	$(PYTHON_INTERPRETER) -m unittest discover -v -s data_science_tools/tests

lint:
	pylint --verbose --rcfile=.pylintrc data_science_tools

version_check:
	echo "Project=$(PROJECT_VERSION) Tag=$(LAST_VERSION_TAG)"
ifneq ("$(PROJECT_VERSION)", "$(LAST_VERSION_TAG)")
	exit 1
endif

version_tag:
	git tag v$(PROJECT_VERSION)
