#!/bin/bash

# Exit on error
set -e

echo "Building the test Docker image..."
docker build -f Dockerfile.test -t agent-tests .

echo "Running the test container..."
docker run --rm agent-tests
echo "All tests executed successfully."
