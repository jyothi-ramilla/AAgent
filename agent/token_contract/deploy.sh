#!/bin/bash

# Exit on error and print each command before executing
set -ex

# Define variables for the Dockerfile and image name
DOCKERFILE="Dockerfile"
IMAGE_NAME="deploy-erc20"
LOCAL_ARTIFACTS_DIR="./contracts/artifacts"  # Local directory for artifacts
CONTAINER_ARTIFACTS_DIR="/app/contracts/artifacts"  # Container directory for artifacts

# Ensure the local artifacts directory exists
echo "Ensuring local artifacts directory exists..."
mkdir -p $LOCAL_ARTIFACTS_DIR

# Build the Docker image
echo "Building the Docker image..."
docker build -f $DOCKERFILE -t $IMAGE_NAME .

# Run the container with volume mapping
echo "Running the deployment container with volume mapping..."
docker run --rm \
  --env-file .env \
  -v "$(pwd)/$LOCAL_ARTIFACTS_DIR:$CONTAINER_ARTIFACTS_DIR" \
  $IMAGE_NAME
