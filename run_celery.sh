#!/usr/bin/env bash
source '../envs/$$$PROJECT_NAME$$$/bin/activate'
export DJANGO_CONFIGURATION=Dev
celery worker -A wodify -l info -B
