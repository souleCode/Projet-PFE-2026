
#!/usr/bin/bash

sudo rm -f /etc/nginx/sites-enabled/default
sudo rm -f /etc/nginx/sites-enabled/api

sudo cp /home/ubuntu/project-pfe-space/nginx/nginx.conf /etc/nginx/sites-available/api
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/api
sudo gpasswd -a www-data ubuntu
sudo nginx -t
sudo systemctl restart nginx

