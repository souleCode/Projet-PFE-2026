### Si vous modifiez le code Python/Django :

cd /home/ubuntu/Projet-PFE-2026/Interface/epi_detection/backend/api
git pull  # si vous utilisez git
sudo systemctl restart gunicorn


### Si vous modifiez la config nginx :
sudo nginx -t
sudo systemctl restart nginx