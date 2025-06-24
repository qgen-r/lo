#!/usr/bin/env bash
set -e

# 1) Install dependencies
pip install -r requirements.txt

# 2) Create any new migrations for your 'loc' app
python manage.py makemigrations loc --noinput

# 3) Apply all migrations
python manage.py migrate --noinput

# 4) Create the Django superuser (uses DJANGO_SUPERUSER_* env vars)
python manage.py createsuperuser --noinput || true

# 5) Collect static files
python manage.py collectstatic --noinput
