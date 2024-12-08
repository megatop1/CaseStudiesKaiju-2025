# Use official Python image as the base
FROM python:3.12-slim

# Install necessary tools
RUN apt-get update && apt-get install -y \
    sshpass \
    netcat-openbsd \
    openssh-client \
    curl \
    wget \
    software-properties-common \
    git \
    && apt-get clean

# Set working directory
WORKDIR /app

# Create Payloads directory inside /app
RUN mkdir /app/payloads

# Git Clone ShellcodeHide
RUN git clone https://github.com/SaadAhla/Shellcode-Hide.git /app/Shellcode-Hide

# Copy the Python script into the container
COPY puzzle.py /app/puzzle.py 

# Install Python Dependencies
RUN pip install --no-cache-dir pycryptodome questionary

# Default command to run the script
CMD ["python", "puzzle.py"]
