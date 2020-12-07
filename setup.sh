#!/bin/bash

apt update

apt install software-properties-common
apt install build-essential
apt install python3.8
apt install python3-pip
apt install python3-dev
apt install virtualenv
apt install ffmpeg
apt install libpcap-dev libpq-dev libffi-dev pkg-config libcairo2-dev
apt install python3-django
apt install libsystemd-dev libgirepository1.0-dev libdbus-glib-1-dev libpython3-dev

pip3 install virtualenv
python3 -m virtualenv musiq_packages
source ./musiq_packages/bin/activate
pip3 install testresources

pip3 install -r requirements.txt

python3 ./musiquarium/musiq_django_site/manage.py makemigrations
python3 ./musiquarium/musiq_django_site/manage.py migrate
