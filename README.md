# musiquarium

<!-- PROJECT LOGO -->
<!-- Not ready yet -->

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#general-installation-instructions)
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

This project was developed on the most recent version of ubuntu, 20.04/10. This is not guaranteed to work on other linux distributions but may be possible with some minor tweaks.

### Prerequisites

In a linux environment (we'll use ubuntu with the apt package manger as an example since that is what I've developed this application on), you will need:
* python3.8
```sh
[sudo] apt install python3
```
* pip3
* VirtualEnv (might be able to be installed using pip)
* FFmpeg

and several more apt/debian/ubuntu packages and PyPi packages. Thankfully, there is an included script which acquires and installs all of the packages needed to run musiquarium.

### General Installation Instructions

1. Clone the repo
```sh
git clone https://github.com/robarmstrong96/musiquarium
```
2. Execute the 'setup.sh' (using 'sudo setup.sh') script located in the git project directory. If the script is not executable, run
```sh
[sudo] chmod +x ./setup.sh
```
This should take a while as several libraries need to be downloaded to properly run musiquarium.

3. Before starting the server (and assuming the automated process finished successfully), you will need to activate the python environment manually. You can do this by simply entering the commands
```sh
source ./musiq_packages/bin/activate
```
from the git project directory. From there, you can run the server.

<!-- USAGE EXAMPLES -->
## Usage

To manually run the server, you should be able to use the command (making sure to replace the [ip address] with the address you wish to host the site from and the [port] you wish to communicate on. By default, 'runserver' will run on the localhost and port 8000; this is recommended if using musiquarium for the first time and are accessing the site ONLY from the device it is running on)
```sh
python3 mange.py runserver [ip address]:[port]
```

Once you've got the site running correctly and visit whatever address specified in the step above, you will be directed to create an account or login. Create an account (if it doesn't redirect you to the actual site, you entered some information incorrectly. Try again.).

Once logging in, you can begin following the instructions on the main page of musiquarium to begin analyzing and editing your media library collection. Keep in mind that the larger the library, the longer musiquarium may take to run. Audio fingerprinting, communicating with music database sites, etc..., takes a long time.

Once musiquarium has finished processing the specified library, you can view the songs that musiquarium has processed on the table page. You can make edits to CERTAIN metadata fields by simply double clicking it and typing in the desired value. Once finished, you can apply metadata edits from the Profile page.

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [Font Awesome](https://fontawesome.com)
* [MusicBrainz](https://musicbrainz.org/)
* [ACRCloud](https://www.acrcloud.com/)
* [Discogs](https://www.discogs.com/)
* [Mutagen](https://mutagen.readthedocs.io/en/latest/)
* [FFmpeg](https://ffmpeg.org/)
