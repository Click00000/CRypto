#!/bin/bash
set -e
pip install -r requirements.txt
alembic upgrade head || echo "Migrations may have already been run"
