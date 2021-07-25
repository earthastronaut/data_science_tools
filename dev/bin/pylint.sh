#!/bin/bash
ROOT_PATH=$(git rev-parse --show-toplevel)
pylint --verbose --rcfile=${ROOT_PATH}/dev/config/pylintrc.ini $@
