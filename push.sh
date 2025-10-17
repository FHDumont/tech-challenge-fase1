#!/bin/bash

CONTAINER_VERSION=1.0
DOCKER_DOMAIN=fernandodumont

docker buildx build --pull --push -t ${DOCKER_DOMAIN}/fiap-fase-1-api:${CONTAINER_VERSION} -o type=image --platform=linux/arm64,linux/amd64 -f Dockerfile.api .
docker buildx build --pull --push -t ${DOCKER_DOMAIN}/fiap-fase-1-dashboard:${CONTAINER_VERSION} -o type=image --platform=linux/arm64,linux/amd64 -f Dockerfile.dashboard .
