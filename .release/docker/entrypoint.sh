#!/bin/bash

python -m jupyter lab \
       --ip=0.0.0.0 \
       --port=8888 \
       --no-browser \
       --allow-root \
       --ServerApp.token= \
       --ServerApp.password= \
       --ServerApp.allow_origin=* \
       --ServerApp.allow_remote_access=True