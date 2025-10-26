FROM python:3.11-slim

LABEL maintainer="VirtPLC Project"
LABEL description="Factory PLC Simulator with OPC-UA Server"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 4840 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 4840)); s.close()" || exit 1

# Run simulator
CMD ["python", "main.py", "--mode", "server", "--port", "8080"]
