#!/bin/bash

set -e

(cd web; docker build -t web .)
docker build -t app .
