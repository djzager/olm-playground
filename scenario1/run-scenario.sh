#!/usr/bin/env bash
set -e

if [ -z $DOCKER_ORG ]; then
	echo "Must specify DOCKER_ORG"
	exit 1
fi

ts="$(date +%s)"
# Build and push operator registry images
v1="docker.io/$DOCKER_ORG/olm-playground-scenario1:v1$ts"
v2="docker.io/$DOCKER_ORG/olm-playground-scenario1:v2$ts"
docker build --no-cache -t $v1 -f olm-catalog-v1/Dockerfile olm-catalog-v1
docker push $v1
docker build --no-cache -t $v2 -f olm-catalog-v2/Dockerfile olm-catalog-v2
docker push $v2

# Run the scenario
ansible-playbook playbook.yaml -e v1=$v1 -e v2=$v2
