#!/bin/bash

IMAGE_NAME="cloak:latest"

if ! command -v xfreerdp &> /dev/null; then
    echo "xfreerdp is not installed on the host. Install it with:"
    echo "sudo apt-get update && sudo apt-get install -y freerdp2-x11"
    exit 1
fi

echo "Granting X11 permissions to Docker..."
xhost +local:docker
if [ $? -ne 0 ]; then
    echo "Failed to grant X11 permissions. Ensure X11 is running and try again."
    exit 1
fi

if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
    echo "Docker image $IMAGE_NAME does not exist. Building the image..."
    docker buildx bake
    if [ $? -ne 0 ]; then
        echo "Failed to build the Docker image. Exiting."
        exit 1
    fi
    echo "Docker image $IMAGE_NAME built successfully."
else
    echo "Docker image $IMAGE_NAME already exists. Skipping build."
fi

echo "Running the Docker container..."
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    --network=host \
    "$IMAGE_NAME"

if [ $? -eq 0 ]; then
    echo "Docker container ran successfully."
else
    echo "Docker container encountered an error."
    exit 1
fi
