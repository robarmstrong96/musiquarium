#!/bin/bash

apt update

apt install python3.8
apt install pip3
apt install virtualenv
apt install ffmpeg

python3 -m virtualenv musiq_packages

source ./musiq_packages/bin/activate

pip3 install -r requirements.txt

python3 ./musiquarium/musiq_django_site/manage.py makemigrations
python3 ./musiquarium/musiq_django_site/manage.py migrate
