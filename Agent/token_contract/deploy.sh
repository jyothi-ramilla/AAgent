#!/bin/bash

# Exit on error and print each command before executing
set -ex

# Define variables for the Dockerfile and image name
DOCKERFILE="Dockerfile"
IMAGE_NAME="deploy-erc20"

# Build the Docker image
echo "Building the Docker image..."
docker build -t $IMAGE_NAME .

# Run the container
echo "Running the deployment container..."
docker run --env-file .env $IMAGE_NAME
