#!/usr/bin/env bash
source '../envs/$$$PROJECT_NAME$$$/bin/activate'
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
