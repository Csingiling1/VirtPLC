# Python AI Service Dockerfile
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    postgresql-client \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code first
COPY src/ ./src/

# Generate protobuf files
COPY ./proto/ ./proto/
RUN python -m grpc_tools.protoc --python_out=./src/ --grpc_python_out=./src/ --proto_path=./proto/ ./proto/ai_service.proto

# Create models directory
RUN mkdir -p /app/models

# Create non-root user
RUN useradd -m -u 1000 aiservice && chown -R aiservice:aiservice /app
USER aiservice

# Expose ports
EXPOSE 3001 3002 9090 9091

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# Start application
ENV PYTHONPATH=/app
WORKDIR /app
CMD ["python", "-m", "src.main"]
