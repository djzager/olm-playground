#!/usr/bin/env bash

SCENARIO="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && basename $(pwd))"
REGISTRY="${REGISTRY:-docker.io/djzager}"

v1="${REGISTRY}/olm-playground-${SCENARIO}:v1"

docker build --no-cache -t $v1 -f olm-catalog/Dockerfile olm-catalog
docker push $v1
