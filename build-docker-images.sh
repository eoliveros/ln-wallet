#!/bin/bash

set -e

(cd web; docker build -t web .)
(cd clightning_bitcoin; docker build -t clightning_bitcoin .)
docker build -t app .
