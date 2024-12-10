#!/bin/bash

IMAGE_NAME="puzzle:latest"
REBUILD=false
HOST_PAYLOADS_DIR="./payloads"
CONTAINER_PAYLOADS_DIR="/app/payloads"

# Create Payloads Directory
mkdir payloads/

# Ensure the payloads directory exists on the host
if [ ! -d "$HOST_PAYLOADS_DIR" ]; then
    echo "Creating payloads directory: $HOST_PAYLOADS_DIR"
    mkdir -p "$HOST_PAYLOADS_DIR"
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --rebuild)
            REBUILD=true
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 [--rebuild]"
            exit 1
            ;;
    esac
    shift
done

# Build the Docker image if necessary
if $REBUILD || ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
    echo "Building the Docker image..."
    sudo docker build -t "$IMAGE_NAME" .
    if [ $? -ne 0 ]; then
        echo "Failed to build the Docker image. Exiting."
        exit 1
    fi
    echo "Docker image $IMAGE_NAME built successfully."
else
    echo "Docker image $IMAGE_NAME already exists. Skipping build."
fi

echo "Running the Docker container..."
DOCKER_RUN_CMD=(
    "sudo" "docker" "run"
    "-it" "--rm"
    "-v" "$HOST_PAYLOADS_DIR:$CONTAINER_PAYLOADS_DIR"
    "$IMAGE_NAME"
)

# Run the Docker container
"${DOCKER_RUN_CMD[@]}"

# Check for errors
if [ $? -eq 0 ]; then
    echo "Docker container ran successfully."
else
    echo "Docker container encountered an error."
    exit 1
fi
