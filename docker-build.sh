#!/bin/bash

docker build . -t ctf_bot
docker run --rm -it -v objects:objects --name ctf_bot ctf_bot