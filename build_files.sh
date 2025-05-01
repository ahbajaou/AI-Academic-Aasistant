#!/bin/bash

# Exit on error
set -e

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Make migrations (optional, depends on your workflow and database setup)
# python manage.py migrate --noinput