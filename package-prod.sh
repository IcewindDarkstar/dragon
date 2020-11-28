#!/bin/bash

CURRENT_DIR=${PWD##*/}
DOCKER_DIR="docker"
ENV_SHARED_FILE=".env.shared"
ENV_PROD_FILE=".env.prod"
BUILD_BASE_FILE="build-base.sh"
BUILD_PROD_FILE="build-prod.sh"

if [ "$CURRENT_DIR" != "dragon" ] ; then
  echo "Run script from project root directory 'dragon'." 
  exit 1
fi

if [ ! -d "$DOCKER_DIR" ] ; then
  echo "Directory '$DOCKER_DIR' does not exist."
  exit 1
fi

if [[ ! -f "$DOCKER_DIR/$ENV_SHARED_FILE" || ! -f "$DOCKER_DIR/$ENV_PROD_FILE" ]] ; then
  echo "Files '$DOCKER_DIR/$ENV_SHARED_FILE' or '$DOCKER_DIR/$ENV_PROD_FILE' do not exist."
  exit 1
fi

if [[ ! -f "$DOCKER_DIR/$BUILD_BASE_FILE" || ! -f "$DOCKER_DIR/$BUILD_PROD_FILE" ]] ; then
  echo "Files '$DOCKER_DIR/$BUILD_BASE_FILE' or '$DOCKER_DIR/$BUILD_PROD_FILE' do not exist."
  exit 1
fi

BASE_IMAGE_NAME="dragon-base"
PROD_IMAGE_NAME="dragon-prod"
PACKAGE_ROOT="/tmp/dragon-prod"
TARGET_ENV_FILE=".env"
TARGET_RUN_SCRIPT="run-prod.sh"
TARGET_IMAGES="dragon-prod-images.tar"
PACKAGE="dragon-prod.tar.gz"

mkdir -p $PACKAGE_ROOT

pushd $DOCKER_DIR
cat $ENV_SHARED_FILE $ENV_PROD_FILE > $PACKAGE_ROOT/$TARGET_ENV_FILE

cp $TARGET_RUN_SCRIPT.template $PACKAGE_ROOT/$TARGET_RUN_SCRIPT
chmod u+x $PACKAGE_ROOT/$TARGET_RUN_SCRIPT

./$BUILD_BASE_FILE
./$BUILD_PROD_FILE
popd

docker save -o $PACKAGE_ROOT/$TARGET_IMAGES $BASE_IMAGE_NAME $PROD_IMAGE_NAME

pushd $PACKAGE_ROOT
tar -czvf $PACKAGE --remove-files $TARGET_ENV_FILE $TARGET_RUN_SCRIPT $TARGET_IMAGES
popd
