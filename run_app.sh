#!/bin/bash
source /opt/pocketflow/venv/bin/activate
cd /opt/pocketflow
export PYTHONPATH="${PYTHONPATH}:/opt/pocketflow/src"
exec python main.py
