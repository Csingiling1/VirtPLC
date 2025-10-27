# VirtPLC Complete System with Enhanced Simulator

This document explains how to run the complete VirtPLC system using Docker Compose, including the enhanced PLC simulator with real-time data streaming.

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)
```bash
# Make the script executable
chmod +x start_virtplc.sh

# Start all services
./start_virtplc.sh
```

### Option 2: Manual Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 📋 Services Overview

| Service | Port | Description |
|---------|------|-------------|
| **Enhanced Simulator** | 5000, 24840, 5001 | PLC replacement with OPC-UA, REST API, and monitoring |
| **Spring Backend** | 18080, 14840, 8000 | Main backend with OPC-UA server and MCP |
| **React Frontend** | 3000 | Web-based HMI interface |
| **AI Service** | 3001, 3002, 9090 | AI analysis and WebSocket streaming |
| **Ollama LLM** | 11434 | Local LLM for AI processing |
| **PostgreSQL** | 15432 | Relational database |
| **TimescaleDB** | 15433 | Time-series database |
| **Redis** | 6379 | Caching and sessions |
| **Simulator Monitor** | 5001 | Real-time monitoring dashboard |

## 🔌 Enhanced Simulator Features

The enhanced simulator now acts as a complete PLC replacement with:

### Real-time Data Streaming
- **REST API**: `http://localhost:5000/api/stream/latest`
- **WebSocket**: `ws://localhost:5000/ws/data`
- **Time-series**: `http://localhost:5000/api/stream/timeseries`

### Device Management
- **CLI Tool**: Full device and signal management
- **REST API**: CRUD operations for devices and signals
- **OPC-UA**: Industrial protocol support

### Monitoring
- **Dashboard**: `http://localhost:5001`
- **Health Checks**: Automatic service monitoring
- **Logs**: Real-time logging and debugging

## 🛠️ Management Commands

### Simulator Management
```bash
# Access simulator CLI
docker-compose exec simulator python cli_manager.py list

# Create a device
docker-compose exec simulator python cli_manager.py create Motor1 "Main Motor" --type motor

# Add signals
docker-compose exec simulator python cli_manager.py add-signal Motor1 Speed RPM --generator uniform --min-value 1000 --max-value 1800

# Monitor real-time data
docker-compose exec simulator python cli_manager.py monitor

# Show system status
docker-compose exec simulator python cli_manager.py status
```

### Service Management
```bash
# View all services
docker-compose ps

# View logs for specific service
docker-compose logs -f simulator
docker-compose logs -f backend
docker-compose logs -f ai-service

# Restart a service
docker-compose restart simulator

# Stop all services
docker-compose down

# Stop and remove volumes (clean reset)
docker-compose down -v
```

### Database Access
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U virtplc -d virtplc

# Access TimescaleDB
docker-compose exec timescale psql -U virtplc -d virtplc_ts

# Access Redis
docker-compose exec redis redis-cli
```

## 🌐 API Endpoints

### Simulator API
- **Latest Data**: `GET http://localhost:5000/api/stream/latest`
- **Time-series**: `GET http://localhost:5000/api/stream/timeseries`
- **Devices**: `GET http://localhost:5000/devices`
- **Simulation Status**: `GET http://localhost:5000/simulation/status`
- **WebSocket**: `ws://localhost:5000/ws/data`

### Backend API
- **Health Check**: `GET http://localhost:18080/api/data/health`
- **Latest Data**: `GET http://localhost:18080/api/data/latest`
- **Data Range**: `GET http://localhost:18080/api/data/range`

### AI Service API
- **Health**: `GET http://localhost:3001/health`
- **Analysis**: `POST http://localhost:3001/analyze`
- **WebSocket**: `ws://localhost:3002`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
JWT_SECRET=your-super-secret-jwt-key-change-in-production-min-256-bits
POSTGRES_PASSWORD=changeme
TIMESCALE_PASSWORD=changeme
REDIS_PASSWORD=
OLLAMA_MODEL=llama3:8b
```

### Simulator Configuration
The simulator uses `simulator/simulator_config.yaml` for configuration:
```yaml
server:
  host: "0.0.0.0"
  port: 8080
  update_interval: 1.0

opcua:
  enabled: true
  endpoint: "opc.tcp://0.0.0.0:4840/virtplc/"

streaming:
  websocket_enabled: true
  broadcast_interval: 1.0
```

## 📊 Data Flow

```
Simulator (Python) → Spring Backend → TimescaleDB
     ↓                    ↓
  OPC-UA Server      REST API
     ↓                    ↓
  Industrial        Frontend (React)
  Protocols              ↓
                    AI Service
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using ports
   netstat -tulpn | grep :5000
   
   # Stop conflicting services
   sudo systemctl stop [service-name]
   ```

2. **Service Not Starting**
   ```bash
   # Check logs
   docker-compose logs simulator
   
   # Check health
   docker-compose ps
   ```

3. **Database Connection Issues**
   ```bash
   # Check database status
   docker-compose exec postgres pg_isready -U virtplc
   docker-compose exec timescale pg_isready -U virtplc
   ```

4. **Simulator Not Responding**
   ```bash
   # Test simulator API
   curl http://localhost:5000/simulation/status
   
   # Check simulator logs
   docker-compose logs -f simulator
   ```

### Health Checks

```bash
# Check all services
docker-compose ps

# Test simulator
curl http://localhost:5000/simulation/status

# Test backend
curl http://localhost:18080/api/data/health

# Test AI service
curl http://localhost:3001/health
```

## 🚀 Development

### Adding New Devices
```bash
# Access simulator CLI
docker-compose exec simulator python cli_manager.py

# Create device
create Motor2 "Secondary Motor" motor "Backup motor system"

# Add signals
add-signal Motor2 Speed RPM --generator uniform --min-value 800 --max-value 1500
add-signal Motor2 Temperature "°C" --generator normal --mean 40 --std-dev 3
```

### Custom Signal Generators
1. Edit `simulator/models.py`
2. Add new generator to `SignalGenerator` enum
3. Implement generation logic in `SignalConfig.generate_value()`
4. Restart simulator: `docker-compose restart simulator`

### Monitoring and Debugging
```bash
# Real-time logs
docker-compose logs -f

# Simulator monitoring dashboard
open http://localhost:5001

# Check resource usage
docker stats
```

## 📈 Performance Tuning

### Simulator Performance
- Adjust `UPDATE_INTERVAL` in docker-compose.yml
- Modify `broadcast_interval` in simulator_config.yaml
- Scale with multiple simulator instances

### Database Performance
- Adjust TimescaleDB chunk intervals
- Configure retention policies
- Monitor query performance

### Memory Usage
```bash
# Check memory usage
docker stats

# Limit memory per service
# Add to docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

## 🔒 Security

### Production Deployment
1. Change all default passwords
2. Use strong JWT secrets
3. Enable HTTPS/TLS
4. Configure firewall rules
5. Use secrets management

### Network Security
- Use internal networks for service communication
- Expose only necessary ports
- Implement authentication for APIs

## 📚 Additional Resources

- [Simulator Documentation](simulator/README_ENHANCED.md)
- [Backend API Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
- [AI Service Documentation](ai-service/README.md)

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review service logs
3. Check GitHub issues
4. Create a new issue with detailed information
