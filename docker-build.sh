#!/bin/bash

docker build . -t ctf_bot
docker run --rm -it -v "$(pwd)"/objects:/app/objects --name ctf_bot ctf_bot