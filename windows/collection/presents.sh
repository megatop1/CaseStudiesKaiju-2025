#!/bin/bash

IMAGE_NAME="presents:latest"
REBUILD=false
SSH_KEY_DIR="$HOME/.ssh"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --rebuild)
            REBUILD=true
            ;;
        --keys)
            if [[ -n "$2" && ! "$2" =~ ^-- ]]; then
                SSH_KEY_DIR="$2"
                shift
            else
                echo "Error: --keys requires a directory argument."
                exit 1
            fi
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 [--rebuild] [--keys <ssh-key-directory>]"
            exit 1
            ;;
    esac
    shift
done

if ! command -v xfreerdp &> /dev/null; then
    echo "xfreerdp is not installed on the host. Install it with:"
    echo "sudo apt-get update && sudo apt-get install -y freerdp2-x11"
    exit 1
fi

if [ -n "$SSH_KEY_DIR" ]; then
    if [ ! -d "$SSH_KEY_DIR" ]; then
        echo "The provided directory does not exist: $SSH_KEY_DIR"
        exit 1
    fi
    echo "Using SSH key directory: $SSH_KEY_DIR"
fi

echo "Granting X11 permissions to Docker..."
xhost +local:docker
if [ $? -ne 0 ]; then
    echo "Failed to grant X11 permissions. Ensure X11 is running and try again."
    exit 1
fi

if $REBUILD || ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
    echo "Building the Docker image..."
    sudo docker buildx bake
    if [ $? -ne 0 ]; then
        echo "Failed to build the Docker image. Exiting."
        exit 1
    fi
    echo "Docker image $IMAGE_NAME built successfully."
else
    echo "Docker image $IMAGE_NAME already exists. Skipping build."
fi

echo "Running the Docker container..."
DOCKER_RUN_CMD=("sudo" "docker" "run" "-it" "--rm" "-e" "DISPLAY=$DISPLAY" "-v" "/tmp/.X11-unix:/tmp/.X11-unix" "--network=host")

if [ -n "$SSH_KEY_DIR" ]; then
    DOCKER_RUN_CMD+=("-v" "$SSH_KEY_DIR:/temp-ssh:ro")
fi

DOCKER_RUN_CMD+=("$IMAGE_NAME" "bash" "-c" "
    if [ -d /temp-ssh ]; then
        mkdir -p /root/.ssh
        cp /temp-ssh/* /root/.ssh/
        chmod 600 /root/.ssh/*
    fi
    exec python3 /app/presents.py
")

"${DOCKER_RUN_CMD[@]}"

# Check for errors
if [ $? -eq 0 ]; then
    echo "Docker container ran successfully."
else
    echo "Docker container encountered an error."
    exit 1
fi