FROM ubuntu:latest

# Install necessary tools
RUN apt-get update && apt-get install -y \
    sshpass \
    netcat-openbsd \
    openssh-client \
    curl \
    wget \
    && apt-get clean

# Add chisel installation if required
RUN wget https://github.com/jpillora/chisel/releases/download/v1.10.1/chisel_1.10.1_linux_amd64.deb && \
    dpkg -i chisel_1.10.1_linux_amd64.deb && \
    rm -f chisel_1.10.1_linux_amd64.deb

# Set environment variable for display (for X11 forwarding)
ENV DISPLAY=:0.0

# Default command
CMD ["bash"]
