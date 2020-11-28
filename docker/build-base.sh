#!/bin/bash

CURRENT_DIR=${PWD##*/}

if [ "$CURRENT_DIR" != "docker" ] ; then
  echo "Run script from 'docker' directory." 
  exit 1
fi

DOCKERFILE="Dockerfile.base"
BASE_IMAGE_NAME="dragon-base"
docker build -f $DOCKERFILE -t $BASE_IMAGE_NAME .
