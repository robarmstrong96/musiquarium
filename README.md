# musiquarium

<!-- PROJECT LOGO -->
<!-- Not ready yet -->

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Acknowledgements](#acknowledgements)

<!-- ABOUT THE PROJECT -->
## About The Project

Musiquarium is a web application music manager designed to manage a collection of music with customizability suited for a variety of different user preferences. Musiquarium natively offers a wider-range of options for characterising the music inside the library compared to other media managers, allowing for user's to customize certain aspects to how Musiquarium  collects, stores, and characterizes their music.

This web application will be capable of what most music library managers can do, just with some added configurability. While this application is intended for anyone, the added configurability is meant for those wanting to fine-tune certain aspects to their library management experience (metadata source, choice of media recognization, etc...) when wanted while still keeping the simplicity for when they might not. Also, this application will be specifically designed for a linux-server environment for user's hoping to manage server stored music through a web-gui (but may be usable in a normal desktop setup). Because of this, this application is targeted mainly for those possessing a media server, with some basic server-environment knowledge (unix permissions, linux command line commands, secure shell, networking, etc...) you will be able to:
* Create a library through stored music
* Choose more than one music recognition method
* Choose where music information/metadata is pulled from
* Configure the automated library creation process
* Customize library through a web GUI, viewing and making changes where needed

### Built With
* [Bootstrap](https://getbootstrap.com)
* [Django](https://www.djangoproject.com/)

<!-- GETTING STARTED -->
## Getting Started

The detailed setup process for testing this project is not officially ready yet, but should be doable with some tweaking.

### Prerequisites

In a linux environment (we'll use ubuntu with the apt package manger as an example), you will need:
* python3
```sh
apt install python3
```
* pip3
* VirtualEnv (might be able to be installed using pip)
* PostgreSQL (subject to change)

### General Installation Instructions
##### (This will be automated [to some extent] in the future)

Once again, these instructions are not ready yet (placeholder)
1. Clone the repo
```sh
git clone https://github.com/robarmstrong96/musiquarium
```
2. Install packages/prerequisites
3. Setup VirtualEnv
```sh
python3 -m virtualenv <name_of_temp_venv>
```
or
```sh
python -m virtualenv <name_of_temp_venv>
```
4. Activate previously created virtual environment, i.e.
```sh
source <venv_folder>/bin/activate in shell
```
5. Install python requirements with the 'requirements.txt' file
```sh
pip3 install -r requirements.txt
```
or
```sh
pip install -r requirements.txt
```
6. go to the directory which contains 'manage.py' (this should be in ./musiquarium/musiq_django_site/manage.py if starting from the root git project directory)
7. in the settings.py file which should be in the musiq_django_site project directory, use https://miniwebtool.com/django-secret-key-generator/ to generate a secret key for django to use when hosting the website. Set 'SECRET_KEY' in settings.py with your newly generated django secret key from the previously mentioned website.
8. assuming postgresql has been installed correctly, you should run
```sh
python3 manage.py makemigrations
```
```sh
python3 manage.py migrate
```
and finally
```sh
python3 manage.py runserver
```
which makes the site viewable on the localhost port 8000, so http://127.0.0.1:8000

<!-- USAGE EXAMPLES -->
## Usage

Not ready yet.

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [Font Awesome](https://fontawesome.com)
