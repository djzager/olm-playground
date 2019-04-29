#!/usr/bin/env bash

SCENARIO="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && basename $(pwd))"
REGISTRY="${REGISTRY:-docker.io/djzager}"

v1="${REGISTRY}/olm-playground-${SCENARIO}:v1"
v1a="${REGISTRY}/olm-playground-${SCENARIO}:v1-a"
v1b="${REGISTRY}/olm-playground-${SCENARIO}:v1-b"

docker build --no-cache -t $v1 -f olm-catalog/Dockerfile olm-catalog
docker push $v1

docker build --no-cache -t $v1a -f olm-catalog-a/Dockerfile olm-catalog-a
docker push $v1a

docker build --no-cache -t $v1b -f olm-catalog-b/Dockerfile olm-catalog-b
docker push $v1b
