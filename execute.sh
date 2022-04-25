#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="${PYTHONPATH}:${PWD}"
eval "./env/bin/streamlit run ${1} ${@:2}"