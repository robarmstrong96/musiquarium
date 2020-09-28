#!/bin/sh

docker-compose -f ./musiquarium_site/Dockerfile -t musiquarium_site:latest ./musiquarium_site up -d
