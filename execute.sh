#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="${PYTHONPATH}:${PWD}"
eval "./env/bin/python3 -u ${1} ${@:2}"