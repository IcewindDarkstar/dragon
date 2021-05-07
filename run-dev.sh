#!/bin/bash

CURRENT_DIR=${PWD##*/}
SRC_DIR="src"
DOCKER_DIR="docker"
ENV_SHARED_FILE=".env.shared"
ENV_DEV_FILE=".env.dev"
BUILD_BASE_FILE="build-base.sh"

if [ "$CURRENT_DIR" != "dragon" ] ; then
  echo "Run script from project root directory 'dragon'." 
  exit 1
fi

if [ ! -d "$SRC_DIR" ] ; then
  echo "Directory '$SRC_DIR' does not exist."
  exit 1
fi

if [ ! -d "$DOCKER_DIR" ] ; then
  echo "Directory '$DOCKER_DIR' does not exist."
  exit 1
fi

if [[ ! -f "$DOCKER_DIR/$ENV_SHARED_FILE" || ! -f "$DOCKER_DIR/$ENV_DEV_FILE" ]] ; then
  echo "Files '$DOCKER_DIR/$ENV_SHARED_FILE' and/or '$DOCKER_DIR/$ENV_DEV_FILE' do not exist."
  exit 1
fi

DEV_ROOT="/tmp/dragon-dev"
DEV_SRC_DIR="$DEV_ROOT/src"
DEV_DATA_DIR="$DEV_ROOT/data"
TARGET_ENV_FILE="$DEV_ROOT/.env"
CONTAINER_NAME="dragon-dev"
BASE_IMAGE_NAME="dragon-base"

mkdir -p $DEV_ROOT
mkdir -p $DEV_SRC_DIR
mkdir -p $DEV_DATA_DIR

pushd $DOCKER_DIR
cat $ENV_SHARED_FILE $ENV_DEV_FILE > $TARGET_ENV_FILE

./$BUILD_BASE_FILE
popd

docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

cp -r $SRC_DIR/* $DEV_SRC_DIR

docker run -d --restart always --name $CONTAINER_NAME --env-file $TARGET_ENV_FILE --mount type=bind,source=$DEV_SRC_DIR,target=/src --mount type=bind,source=$DEV_DATA_DIR,target=/data $BASE_IMAGE_NAME python bot.py
