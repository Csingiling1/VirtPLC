# VirtPLC Testing Guide

This guide explains how to test VirtPLC services locally before deployment.

## Prerequisites

- Docker & Docker Compose installed
- At least 16GB RAM (for full stack with Ollama)
- 50GB free disk space
- Ports available: 3000, 8000, 8080, 8088, 5432, 6379-6382, 8086, 11434

## Quick Test - Individual Services

### 1. Test Backend Stack Only

```bash
cd backend/
docker compose up -d
docker compose logs -f

# Wait for services to start (check health)
docker compose ps

# Test endpoints
curl http://localhost:8080/actuator/health
curl http://localhost:5432  # PostgreSQL
curl http://localhost:8086/health  # InfluxDB
```

**Expected Services:**
- ✅ PostgreSQL on 5432
- ✅ InfluxDB on 8086
- ✅ Redis on 6382
- ✅ Java Backend on 8080
- ✅ PLC Simulator on 4840 (OPC-UA)
- ✅ Grafana on 3001

### 2. Test AI Service Stack

```bash
cd ai-service/
docker compose up -d
docker compose logs -f ollama-setup

# Wait for Ollama model to download (8GB, takes 5-10 min)
# Check Ollama status
curl http://localhost:11434/api/tags

# Test AI backend
curl http://localhost:8000/health
curl http://localhost:8000/docs  # FastAPI docs
```

**Expected Services:**
- ✅ Redis AI on 6381
- ✅ FastAPI on 8000
- ✅ Ollama on 11434 with llama3.2:8b-instruct-q8_0

**Ollama Model Info:**
- **8B Model**: `llama3.2:8b-instruct-q8_0` (default)
  - Size: ~8GB
  - Speed: ~50 tokens/sec (CPU), ~200+ tokens/sec (GPU)
  - Best for: Real-time inference, development

- **17B Model**: `llama3.2:17b-instruct-q8_0` (optional)
  - Size: ~17GB
  - Speed: ~20 tokens/sec (CPU), ~100+ tokens/sec (GPU)
  - Best for: Higher accuracy, production

### 3. Test Edge/HMI Stack

```bash
cd HMI/
docker compose up -d
docker compose logs -f

# Check Ignition Gateway
curl http://localhost:8088/StatusPing

# Access Ignition UI
open http://localhost:8088
# Login: admin / password (default)
```

**Expected Services:**
- ✅ Ignition Edge on 8088
- ✅ Redis Edge on 6379

### 4. Test Frontend Stack

```bash
cd frontend/
docker compose up -d
docker compose logs -f

# Check frontend
curl http://localhost:3000

# Open in browser
open http://localhost:3000
```

**Expected Services:**
- ✅ React App on 3000
- ✅ Redis Frontend on 6380

## Full Stack Test

### Start All Services

```bash
# From project root
./orchestrate.sh start

# Monitor startup
./orchestrate.sh logs backend -f
# Ctrl+C to stop following, then check others
./orchestrate.sh logs ai -f
./orchestrate.sh logs edge -f
./orchestrate.sh logs frontend -f
```

### Health Check All Services

```bash
./orchestrate.sh health
```

Expected output:
```
========================================
Health Check
========================================
ℹ Checking Backend (port 8080)...
✓ Backend is healthy
ℹ Checking AI Service (port 8000)...
✓ AI Service is healthy
ℹ Checking Ignition Edge (port 8088)...
✓ Ignition Edge is healthy
ℹ Checking Frontend (port 3000)...
✓ Frontend is healthy
ℹ Checking PostgreSQL (port 5432)...
✓ PostgreSQL is running
ℹ Checking InfluxDB (port 8086)...
✓ InfluxDB is healthy
```

### Verify Service Communication

```bash
# Test AI → Backend
docker exec ai-backend curl -f http://java-backend:8080/actuator/health

# Test AI → PostgreSQL
docker exec ai-backend nc -zv postgres 5432

# Test AI → InfluxDB
docker exec ai-backend curl -f http://influxdb:8086/health

# Test AI → Ollama
docker exec ai-backend curl -f http://ollama:11434/api/tags

# Test Frontend → Backend
docker exec frontend curl -f http://java-backend:8080/actuator/health

# Test Frontend → AI
docker exec frontend curl -f http://ai-backend:8000/health
```

## Testing Ollama AI Models

### Test 8B Model (Default)

```bash
# Basic completion test
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:8b-instruct-q8_0",
  "prompt": "Explain what a PLC (Programmable Logic Controller) does in one sentence.",
  "stream": false
}'

# Chat completion test
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2:8b-instruct-q8_0",
  "messages": [
    {"role": "user", "content": "What are common PLC communication protocols?"}
  ],
  "stream": false
}'
```

### Pull and Test 17B Model (Optional)

```bash
# Pull larger model (17GB download)
docker exec ollama ollama pull llama3.2:17b-instruct-q8_0

# Update AI service to use 17B
# Edit ai-service/.env:
# OLLAMA_MODEL=llama3.2:17b-instruct-q8_0

# Restart AI service
cd ai-service/
docker compose restart ai-backend

# Test 17B model
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:17b-instruct-q8_0",
  "prompt": "Analyze this PLC error code and suggest solutions...",
  "stream": false
}'
```

### Available Ollama Models

```bash
# List downloaded models
curl http://localhost:11434/api/tags

# Pull other models (examples)
docker exec ollama ollama pull llama3.2:8b-instruct-fp16   # Higher precision
docker exec ollama ollama pull codellama:7b                # Code generation
docker exec ollama ollama pull mistral:7b-instruct         # Alternative model
```

## Performance Testing

### Load Test Backend

```bash
# Install wrk (HTTP benchmarking tool)
# Linux: apt install wrk
# Mac: brew install wrk

# Test backend API
wrk -t4 -c100 -d30s http://localhost:8080/actuator/health

# Expected: 1000+ req/sec
```

### Load Test AI Service

```bash
# Test AI health endpoint
wrk -t4 -c50 -d30s http://localhost:8000/health

# Test AI inference (prepare request.lua)
cat > request.lua <<'EOF'
wrk.method = "POST"
wrk.body   = '{"prompt": "Test", "model": "llama3.2:8b-instruct-q8_0"}'
wrk.headers["Content-Type"] = "application/json"
EOF

wrk -t2 -c10 -d30s -s request.lua http://localhost:11434/api/generate

# Expected: 5-20 req/sec (depends on hardware)
```

### Monitor Resource Usage

```bash
# Watch all containers
docker stats

# Watch specific service
docker stats ai-backend ollama

# Check disk usage
docker system df -v
```

## Database Testing

### PostgreSQL

```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U virtplc -d virtplc

# Run test queries
\dt                          # List tables
\d+ users                    # Describe users table
SELECT COUNT(*) FROM users;  # Count records
\q                           # Quit
```

### InfluxDB

```bash
# Access InfluxDB CLI
docker exec -it influxdb influx

# Auth with token from .env
# Setup: Visit http://localhost:8086 and login
# Username: admin
# Password: changeme123

# Query data
# Use the InfluxDB UI at http://localhost:8086
```

### Redis

```bash
# Connect to Redis instances
docker exec -it redis-edge redis-cli
docker exec -it redis-frontend redis-cli -p 6379
docker exec -it redis-ai redis-cli -p 6379
docker exec -it redis-backend redis-cli -p 6379

# Test commands
PING                         # Should return PONG
KEYS *                       # List all keys
INFO memory                  # Memory usage
DBSIZE                       # Number of keys
```

## Integration Testing

### Test PLC → Backend → AI Flow

1. **Generate PLC data** (simulator)
```bash
# Check PLC simulator is running
docker exec plc-simulator curl http://localhost:8080/health

# View simulated data
curl http://localhost:8085/api/tags
```

2. **Backend receives data**
```bash
# Check backend OPC-UA connection
docker logs java-backend | grep -i "opc"

# Query backend API
curl http://localhost:8080/api/sensors
```

3. **AI analyzes data**
```bash
# Send data to AI for prediction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_data": {
      "temperature": 75.5,
      "pressure": 101.3,
      "vibration": 0.05
    }
  }'
```

4. **Frontend displays results**
```bash
# Open browser
open http://localhost:3000

# Login and check:
# - Live sensor data
# - AI predictions
# - HMI embedded view
```

## Troubleshooting Tests

### Services Won't Start

```bash
# Check logs
./orchestrate.sh logs backend

# Check ports
ss -tlnp | grep -E ':(3000|8000|8080|8088|5432|8086|11434)'

# Free up ports if needed
docker compose down  # In each service directory
```

### Ollama Model Download Fails

```bash
# Check disk space
df -h

# Check Ollama logs
docker logs ollama

# Manually pull model
docker exec -it ollama ollama pull llama3.2:8b-instruct-q8_0

# If network issues, increase timeout
docker exec -it ollama sh -c "OLLAMA_TIMEOUT=300 ollama pull llama3.2:8b-instruct-q8_0"
```

### Database Connection Errors

```bash
# Verify network
docker network inspect virtplc-shared

# Test connectivity
docker exec ai-backend ping -c 3 postgres
docker exec ai-backend nc -zv postgres 5432

# Check database is ready
docker exec postgres pg_isready -U virtplc
```

### Ollama Out of Memory

```bash
# Check available RAM
free -h

# Use smaller model
docker exec ollama ollama pull llama3.2:3b-instruct-q8_0

# Or enable quantization
# 8-bit quantization (q8_0) is already used, which is optimal
```

## Test Cleanup

### Stop All Services

```bash
./orchestrate.sh stop
```

### Remove All Containers (Keep Data)

```bash
./orchestrate.sh down
# Answer 'n' to keep network
```

### Complete Cleanup (Delete Data)

```bash
cd backend/
docker compose down -v  # Remove volumes

cd ../ai-service/
docker compose down -v

cd ../HMI/
docker compose down -v

cd ../frontend/
docker compose down -v

cd ..
docker network rm virtplc-shared
```

### Clean Docker System

```bash
# Remove unused images
docker image prune -a

# Remove build cache
docker builder prune

# Full cleanup (CAUTION: removes ALL unused Docker data)
docker system prune -a --volumes
```

## Test Success Criteria

✅ **All services healthy** via `./orchestrate.sh health`  
✅ **Frontend accessible** at http://localhost:3000  
✅ **Backend API responding** at http://localhost:8080  
✅ **AI service responding** at http://localhost:8000  
✅ **Ollama loaded** with llama3.2:8b-instruct-q8_0  
✅ **Ignition accessible** at http://localhost:8088  
✅ **All databases accepting connections**  
✅ **Inter-service communication working**  
✅ **No error logs** in any service  

## Next Steps

Once testing passes:
1. Review [DEPLOY.md](./DEPLOY.md) for production deployment
2. Configure environment variables for production
3. Set up monitoring and alerting
4. Implement backup strategies
5. Configure SSL/TLS certificates

---

**Test Duration**: 20-30 minutes (first time, including Ollama model download)  
**Subsequent Tests**: 5-10 minutes
