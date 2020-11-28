#!/bin/bash

CURRENT_DIR=${PWD##*/}

if [ "$CURRENT_DIR" != "docker" ] ; then
  echo "Run script from 'docker' directory." 
  exit 1
fi

DOCKERFILE="Dockerfile.prod"
PROD_IMAGE_NAME="dragon-prod"

pushd .. # to make 'src' directory available to docker build context
docker build -f ./docker/$DOCKERFILE -t $PROD_IMAGE_NAME .
popd
