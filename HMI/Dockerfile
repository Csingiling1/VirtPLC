FROM inductiveautomation/ignition:8.1.28

LABEL maintainer="VirtPLC Team"
LABEL description="Ignition Edge HMI for VirtPLC Factory Control System"

# Environment variables
ENV IGNITION_EDITION=edge
ENV GATEWAY_ADMIN_USERNAME=admin
ENV GATEWAY_ADMIN_PASSWORD=password
ENV ACCEPT_IGNITION_EULA=Y

# Install additional system dependencies
USER root
RUN apt-get update && apt-get install -y \
    curl \
    vim \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Create required directories
RUN mkdir -p /backup/gateway \
    && mkdir -p /timebase/data \
    && chown -R ignition:ignition /backup /timebase

# Copy gateway configuration
COPY IgnitionEdge/config/gateway.xml /usr/local/bin/ignition/data/gateway.xml

# Copy tag definitions
COPY IgnitionEdge/tags/ /usr/local/bin/ignition/data/tags/

# Copy project files
COPY IgnitionEdge/projects/VirtPLC-HMI /usr/local/bin/ignition/data/projects/VirtPLC-HMI

# Set permissions
RUN chown -R ignition:ignition /usr/local/bin/ignition/data

# Switch back to ignition user
USER ignition

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8088/StatusPing || exit 1

# Expose ports
EXPOSE 8088 8043 8060

# Gateway starts automatically from base image
