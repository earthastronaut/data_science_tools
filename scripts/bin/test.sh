#!/bin/bash
ROOT_PATH=$(git rev-parse --show-toplevel)
pytest --verbose -c=${ROOT_PATH}/scripts/config/coveragerc.ini $@
