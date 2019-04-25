#!/usr/bin/env bash

SCENARIO="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && basename $(pwd))"
REGISTRY="${REGISTRY:-docker.io/djzager}"

v1="${REGISTRY}/olm-playground-${SCENARIO}:v1"
v2="${REGISTRY}/olm-playground-${SCENARIO}:v2"

docker build --no-cache -t $v1 -f olm-catalog-v1/Dockerfile olm-catalog-v1
docker push $v1
docker build --no-cache -t $v2 -f olm-catalog-v2/Dockerfile olm-catalog-v2
docker push $v2
