
#################################################################################
# VARIBLES
#################################################################################

PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS
#################################################################################

requirements:
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

build:
	$(PYTHON_INTERPRETER) -m pip install -e .

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "data_science_tools.egg-info" | xargs rm -r $1

test:
	$(PYTHON_INTERPRETER)  -m unittest discover -s data_science_tools/tests
