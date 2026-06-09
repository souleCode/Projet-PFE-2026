#!/usr/bin/bash

WORK_DIR=/home/ubuntu/project-pfe-space
VENV=/home/ubuntu/env/bin

cd $WORK_DIR

# Apply migrations and collect static using the venv Python
$VENV/python manage.py migrate --noinput
$VENV/python manage.py collectstatic --noinput

sudo systemctl restart gunicorn.service
sudo systemctl restart nginx
