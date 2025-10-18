# 🤖 Ollama Setup Guide for VirtPLC

## Overview

VirtPLC uses Ollama to run Llama3 (8B or 17B) locally for AI-powered factory analysis. Ollama is included in the Docker Compose setup and runs as a containerized service.

---

## Quick Start

### 1. Start Ollama with Docker Compose

```bash
# Start all services including Ollama
docker-compose up -d

# Or start just Ollama
docker-compose up -d ollama
```

### 2. Pull Llama3 Model

After Ollama container is running, pull the model:

```bash
# Pull Llama3 8B (recommended for most systems)
docker exec -it virtplc-ollama ollama pull llama3:8b

# OR pull Llama3 70B (requires more resources)
docker exec -it virtplc-ollama ollama pull llama3:70b

# OR pull Llama3.1 8B (latest version)
docker exec -it virtplc-ollama ollama pull llama3.1:8b
```

### 3. Verify Installation

```bash
# Check Ollama is running
curl http://localhost:11434/

# List installed models
docker exec -it virtplc-ollama ollama list

# Test the model
docker exec -it virtplc-ollama ollama run llama3:8b "Hello, how are you?"
```

---

## Model Options

### Llama3 8B (Recommended)
- **RAM Required**: 8GB
- **Model Size**: ~4.7GB
- **Best for**: Most development and production environments
- **Command**: `ollama pull llama3:8b`

### Llama3 70B (High Performance)
- **RAM Required**: 48GB+
- **Model Size**: ~39GB
- **Best for**: High-end servers with lots of RAM
- **Command**: `ollama pull llama3:70b`

### Llama3.1 8B (Latest)
- **RAM Required**: 8GB
- **Model Size**: ~4.7GB
- **Best for**: Latest features and improvements
- **Command**: `ollama pull llama3.1:8b`

---

## Configuration

### Update Model in Docker Compose

Edit `docker-compose.yml`:

```yaml
ai-service:
  environment:
    - OLLAMA_MODEL=llama3:8b  # Change to llama3:70b or llama3.1:8b
```

### Update Model in .env

Edit `.env` file:

```bash
OLLAMA_MODEL=llama3:8b  # or llama3:70b, llama3.1:8b
```

---

## GPU Acceleration (Optional)

### NVIDIA GPU Support

If you have an NVIDIA GPU, Docker Compose is already configured to use it:

```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

**Requirements:**
- NVIDIA GPU with CUDA support
- NVIDIA Container Toolkit installed

**Install NVIDIA Container Toolkit:**

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Without GPU

If you don't have a GPU, remove the GPU section from `docker-compose.yml`:

```yaml
ollama:
  image: ollama/ollama:latest
  # Remove this section:
  # deploy:
  #   resources:
  #     reservations:
  #       devices:
  #         - driver: nvidia
  #           count: all
  #           capabilities: [gpu]
```

---

## Performance Tuning

### Resource Limits

Edit `docker-compose.prod.yml` to adjust Ollama resources:

```yaml
ollama:
  deploy:
    resources:
      limits:
        cpus: '4'      # Adjust based on your CPU
        memory: 8G     # Adjust based on model size
      reservations:
        cpus: '2'
        memory: 4G
```

### Memory Requirements by Model

| Model | Minimum RAM | Recommended RAM |
|-------|-------------|-----------------|
| llama3:8b | 8GB | 16GB |
| llama3:70b | 48GB | 64GB |
| llama3.1:8b | 8GB | 16GB |

---

## Troubleshooting

### Ollama Container Won't Start

```bash
# Check logs
docker logs virtplc-ollama

# Restart container
docker-compose restart ollama
```

### Model Download Fails

```bash
# Check disk space
df -h

# Pull model manually
docker exec -it virtplc-ollama ollama pull llama3:8b

# Check Ollama version
docker exec -it virtplc-ollama ollama --version
```

### AI Service Can't Connect to Ollama

```bash
# Check Ollama health
curl http://localhost:11434/

# Check network
docker network inspect virtplc-network

# Verify AI service config
docker logs virtplc-ai
```

### Out of Memory Errors

```bash
# Use smaller model
docker exec -it virtplc-ollama ollama pull llama3:8b

# Increase Docker memory limit
# Docker Desktop -> Settings -> Resources -> Memory
```

---

## API Usage

### Test Ollama API

```bash
# Generate completion
curl http://localhost:11434/api/generate -d '{
  "model": "llama3:8b",
  "prompt": "Analyze this factory sensor data: temperature=75°C, vibration=0.5mm/s",
  "stream": false
}'

# Chat completion
curl http://localhost:11434/api/chat -d '{
  "model": "llama3:8b",
  "messages": [
    {
      "role": "user",
      "content": "What indicates a motor might need maintenance?"
    }
  ]
}'
```

### AI Service Integration

The AI service automatically uses Ollama:

```bash
# Get AI analysis
curl -X POST http://localhost:3001/api/analysis/analyze

# Get predictive maintenance
curl http://localhost:3001/api/analysis/predict-maintenance

# WebSocket for real-time analysis
wscat -c ws://localhost:3002
```

---

## Model Management

### List All Models

```bash
docker exec -it virtplc-ollama ollama list
```

### Remove a Model

```bash
docker exec -it virtplc-ollama ollama rm llama3:70b
```

### Update Models

```bash
# Pull latest version
docker exec -it virtplc-ollama ollama pull llama3:8b
```

### Check Model Info

```bash
docker exec -it virtplc-ollama ollama show llama3:8b
```

---

## Production Deployment

### Best Practices

1. **Pre-pull models** before deployment:
   ```bash
   docker exec -it virtplc-ollama ollama pull llama3:8b
   ```

2. **Use persistent volumes** (already configured):
   ```yaml
   volumes:
     - ollama-data:/root/.ollama
   ```

3. **Set resource limits** in production:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

4. **Monitor performance**:
   ```bash
   docker stats virtplc-ollama
   ```

### Health Checks

Ollama health check is configured:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:11434/"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 60s
```

---

## Alternative: External Ollama

If you prefer to run Ollama outside Docker:

1. **Install Ollama** on host:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Update docker-compose.yml**:
   ```yaml
   ai-service:
     environment:
       - OLLAMA_HOST=http://host.docker.internal:11434
     extra_hosts:
       - "host.docker.internal:host-gateway"
   ```

3. **Remove Ollama service** from docker-compose.yml

---

## Resources

- **Ollama Documentation**: https://ollama.com/docs
- **Llama3 Model Card**: https://ollama.com/library/llama3
- **Docker Hub**: https://hub.docker.com/r/ollama/ollama
- **GitHub**: https://github.com/ollama/ollama

---

## Summary

✅ Ollama runs as a Docker service  
✅ Llama3 8B recommended for most use cases  
✅ GPU acceleration optional but recommended  
✅ Models persist in Docker volume  
✅ Integrated with AI service automatically  

**First time setup:**
```bash
docker-compose up -d
docker exec -it virtplc-ollama ollama pull llama3:8b
```

🚀 **Ready to use AI-powered factory analysis!**
