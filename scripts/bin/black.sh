#!/bin/bash
ROOT_PATH=$(git rev-parse --show-toplevel)
black --verbose --config=${ROOT_PATH}/scripts/config/black.toml $@
