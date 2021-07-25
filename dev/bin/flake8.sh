#!/bin/bash
ROOT_PATH=$(git rev-parse --show-toplevel)
flake8 --config=${ROOT_PATH}/dev/config/flake8.ini $@
