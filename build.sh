#!/usr/bin/env bash
# exit on error

python src/manage.py collectstatic --no-input
python src/manage.py migrate