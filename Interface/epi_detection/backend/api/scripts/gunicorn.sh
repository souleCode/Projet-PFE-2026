#!/usr/bin/bash
sudo cp /home/ubuntu/project-pfe-space/gunicorn/gunicorn.socket  /etc/systemd/system/gunicorn.socket
sudo cp /home/ubuntu/project-pfe-space/gunicorn/gunicorn.service  /etc/systemd/system/gunicorn.service

sudo systemctl daemon-reload
sudo systemctl enable gunicorn.socket gunicorn.service
sudo systemctl restart gunicorn.socket
sudo systemctl restart gunicorn.service
