#!/bin/bash

docker build . -t ctf_bot
docker run --rm -it --name ctf_bot ctf_bot