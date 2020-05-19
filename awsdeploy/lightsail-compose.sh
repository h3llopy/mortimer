#!/bin/bash

# install latest version of docker the lazy way
curl -sSL https://get.docker.com | sh

# make it so you don't need to sudo to run docker commands
usermod -aG docker ubuntu

# install docker-compose
curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# copy the dockerfile into /srv/docker 
# if you change this, change the systemd service file to match
# WorkingDirectory=[whatever you have below]
mkdir /srv/docker
sudo curl -o /srv/docker/Dockerfile https://raw.githubusercontent.com/amcgeough/mortimer/master/awsdeploy/Dockerfile
sudo curl -o /srv/docker/docker-compose.yml https://raw.githubusercontent.com/amcgeough/mortimer/master/awsdeploy/docker-compose.yml

# copy in systemd unit file and register it so our compose file runs 
# on system restart
sudo curl -o /etc/systemd/system/docker-compose-app.service https://raw.githubusercontent.com/amcgeough/mortimer/master/awsdeploy/docker-compose-app.service
systemctl enable docker-compose-app

# zip -r disable_odoo_online.zip disable_odoo_online
# copy and unzip addons folder
sudo curl -o /srv/docker/addons.zip -L https://github.com/amcgeough/mortimer/raw/master/awsdeploy/addons_zip/addons.zip
sudo apt install unzip
sudo unzip /srv/docker/addons.zip -d /srv/docker
sudo rm -f /srv/docker/addons.zip

# sudo curl -o /srv/docker/addons/sh_barcode_scanner_adv.zip -L https://github.com/amcgeough/mortimer/raw/master/awsdeploy/addons_zip/sh_barcode_scanner_adv.zip
# sudo unzip /srv/docker/addons/sh_barcode_scanner_adv.zip -d /srv/docker/addons
# sudo rm -f /srv/docker/addons/sh_barcode_scanner_adv.zip

# get nginx.conf file
sudo curl -o /srv/docker/nginx.conf https://raw.githubusercontent.com/amcgeough/mortimer/master/awsdeploy/nginx.conf

# start up the application via docker-compose
sudo docker-compose -f /srv/docker/docker-compose.yml up -d
