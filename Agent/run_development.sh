#!/bin/bash

# Exit on error and print each command before executing
set -ex

# Define variables for the Dockerfile and image name
DOCKERFILE="Dockerfile.dev"
IMAGE_NAME="agent-dev"

# Get the absolute path of the current working directory
PROJECT_DIR=$(pwd)

# Build the Docker image
echo "Building the development Docker image..."
docker build -f $DOCKERFILE -t $IMAGE_NAME .

# Run the container in the foreground to see logs in real-time
echo "Running the container and printing logs to the console..."
docker run --rm --env-file .env agent-dev
