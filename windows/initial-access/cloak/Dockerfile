# Use official Python image as the base
FROM python:3.12-slim

# Install necessary tools
RUN apt-get update && apt-get install -y \
    sshpass \
    netcat-openbsd \
    openssh-client \
    curl \
    wget \
    && apt-get clean

# Install Chisel
RUN wget https://github.com/jpillora/chisel/releases/download/v1.10.1/chisel_1.10.1_linux_amd64.deb && \
    dpkg -i chisel_1.10.1_linux_amd64.deb && \
    rm -f chisel_1.10.1_linux_amd64.deb

# Copy the Python script into the container
COPY cloak.py /app/cloak.py
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir questionary

# Set environment variable for display (for X11 forwarding)
ENV DISPLAY=:0.0

# Default command to run the script
CMD ["python", "cloak.py"]
