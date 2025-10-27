FROM python:3.11-slim

LABEL maintainer="VirtPLC Project"
LABEL description="Factory PLC Simulator with OPC-UA Server and Real-time Streaming"
LABEL version="2.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose ports
EXPOSE 4840 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/simulation/status || exit 1

# Run simulator in PLC server mode
CMD ["python", "main.py", "--mode", "plc-server", "--host", "0.0.0.0", "--port", "8080", "--opcua-endpoint", "opc.tcp://0.0.0.0:4840/virtplc/"]
