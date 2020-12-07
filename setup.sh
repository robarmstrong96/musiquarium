#!/bin/bash

apt update

apt install -y software-properties-common
apt install -y build-essential
apt install -y python3.8
apt install -y python3-pip
apt install -y python3-dev
apt install -y virtualenv
apt install -y ffmpeg
apt install -y libpcap-dev libpq-dev libffi-dev pkg-config libcairo2-dev
apt install -y python3-django
apt install -y libsystemd-dev libgirepository1.0-dev libdbus-glib-1-dev libpython3-dev libtag1-dev

pip3 install virtualenv
pip3 install environ
python3 -m virtualenv musiq_packages
source ./musiq_packages/bin/activate
pip3 install testresources

pip3 install -r requirements.txt

python3 ./musiquarium/musiq_django_site/manage.py makemigrations
python3 ./musiquarium/musiq_django_site/manage.py migrate
python3 ./musiquarium/musiq_django_site/manage.py collectstatic
chmod -R 777 ./musiquarium
