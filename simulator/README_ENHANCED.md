# VirtPLC Enhanced Simulator

A comprehensive PLC replacement server with real-time data streaming, device management, and Spring backend integration.

## 🚀 Features

### Core Functionality
- **PLC Replacement Server**: Acts as a complete PLC replacement with OPC-UA and REST API
- **Real-time Data Streaming**: WebSocket and REST endpoints for live data
- **Device Management**: Full CRUD operations for factory devices
- **Signal Generation**: Multiple signal types (constant, uniform, normal, exponential, etc.)
- **Spring Backend Integration**: Compatible data format for TimescaleDB storage

### Communication Protocols
- **OPC-UA Server**: Industrial protocol support (port 4840)
- **REST API**: HTTP/HTTPS endpoints for data access and device management
- **WebSocket**: Real-time data streaming for live monitoring
- **Time-series Data**: Optimized for TimescaleDB integration

### Management Tools
- **CLI Manager**: Command-line tool for device management
- **Interactive CLI**: User-friendly interactive interface
- **Web Dashboard**: Real-time monitoring dashboard
- **Docker Support**: Easy deployment with Docker and Docker Compose

## 📋 Quick Start

### Using Docker (Recommended)

1. **Start the simulator**:
   ```bash
   docker-compose up -d
   ```

2. **Access the services**:
   - Web API: http://localhost:8080
   - OPC-UA Server: opc.tcp://localhost:4840/virtplc/
   - Monitor Dashboard: http://localhost:8081

3. **Manage devices**:
   ```bash
   # List devices
   python cli_manager.py list

   # Create a motor
   python cli_manager.py create Motor1 "Main Motor" --type motor --description "Primary drive motor"

   # Add signals
   python cli_manager.py add-signal Motor1 Speed RPM --generator uniform --min-value 1000 --max-value 1800
   python cli_manager.py add-signal Motor1 Temperature "°C" --generator normal --mean 45 --std-dev 5

   # Monitor real-time data
   python cli_manager.py monitor
   ```

### Manual Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the PLC server**:
   ```bash
   python main.py --mode plc-server --host 0.0.0.0 --port 8080
   ```

3. **Use the CLI manager**:
   ```bash
   python cli_manager.py --help
   ```

## 🔧 Configuration

### Server Modes

- `plc-server`: Full PLC replacement with OPC-UA and REST API (recommended)
- `server`: Basic server with OPC-UA and web API
- `web`: Web API only
- `opcua`: OPC-UA server only
- `interactive`: Interactive CLI mode
- `cli`: Command-line mode

### Environment Variables

- `PYTHONUNBUFFERED=1`: Enable real-time logging
- `SIMULATOR_HOST`: Server host (default: 0.0.0.0)
- `SIMULATOR_PORT`: Server port (default: 8080)
- `OPCUA_ENDPOINT`: OPC-UA endpoint (default: opc.tcp://0.0.0.0:4840/virtplc/)

## 📡 API Endpoints

### REST API

#### Device Management
- `GET /devices` - List all devices
- `POST /devices` - Create new device
- `GET /devices/{id}` - Get device details
- `PUT /devices/{id}` - Update device
- `DELETE /devices/{id}` - Delete device

#### Signal Management
- `GET /devices/{id}/signals` - List device signals
- `POST /devices/{id}/signals` - Add signal to device
- `DELETE /devices/{id}/signals/{name}` - Remove signal

#### Real-time Data
- `GET /api/stream/latest` - Get latest data (Spring backend compatible)
- `GET /api/stream/timeseries` - Get time-series data
- `GET /simulation/status` - Get simulation status

#### WebSocket
- `ws://localhost:8080/ws/data` - Real-time data streaming
- `ws://localhost:8080/ws/control` - Device control commands

### Spring Backend Integration

The simulator provides data in a format compatible with your Spring backend's `SensorData` model:

```json
{
  "timestamp": 1703123456789,
  "motor1Speed": 1500.0,
  "motor1Temp": 45.2,
  "motor1Run": true,
  "motor1Fault": false,
  "motor2Speed": 1200.0,
  "motor2Temp": 42.1,
  "motor2Run": true,
  "motor2Fault": false,
  "conveyor1Speed": 30.5,
  "conveyor1Run": true,
  "sensor1Value": 75.3,
  "sensor2Value": true,
  "systemStatus": "Running"
}
```

## 🛠️ CLI Management

### Device Operations

```bash
# List all devices
python cli_manager.py list

# List with details
python cli_manager.py list --detailed

# Filter by type
python cli_manager.py list --type motor

# Show only active devices
python cli_manager.py list --active-only
```

### Device Creation

```bash
# Create a motor
python cli_manager.py create Motor1 "Main Motor" --type motor --description "Primary drive motor"

# Create a conveyor
python cli_manager.py create Conveyor1 "Main Conveyor" --type conveyor --description "Production line conveyor"

# Create a sensor
python cli_manager.py create Sensor1 "Temperature Sensor" --type sensor --description "Oven temperature monitoring"
```

### Signal Management

```bash
# Add uniform signal
python cli_manager.py add-signal Motor1 Speed RPM --generator uniform --min-value 1000 --max-value 1800

# Add normal distribution signal
python cli_manager.py add-signal Motor1 Temperature "°C" --generator normal --mean 45 --std-dev 5

# Add exponential signal
python cli_manager.py add-signal Motor1 Vibration "mm/s" --generator exponential --rate 0.1

# Add sinusoidal signal
python cli_manager.py add-signal Sensor1 Value "°C" --generator sinusoidal --frequency 0.001 --amplitude 50 --offset 200
```

### Monitoring

```bash
# Show system status
python cli_manager.py status

# Monitor real-time data
python cli_manager.py monitor

# Monitor with custom interval
python cli_manager.py monitor --interval 0.5

# Monitor for specific duration
python cli_manager.py monitor --duration 60
```

## 🔌 OPC-UA Integration

The simulator provides OPC-UA nodes for industrial communication:

### Node Structure
```
Factory/
├── System/
│   ├── EmergencyStop (Boolean, Writable)
│   └── SystemReset (Boolean, Writable)
├── Motor1/
│   ├── Speed (Double)
│   ├── TargetSpeed (Double, Writable)
│   ├── Running (Boolean)
│   ├── Fault (Boolean)
│   ├── Temperature (Double)
│   ├── Current (Double)
│   ├── Voltage (Double)
│   ├── Power (Double)
│   ├── Vibration (Double)
│   ├── StartCommand (Boolean, Writable)
│   ├── StopCommand (Boolean, Writable)
│   └── ResetCommand (Boolean, Writable)
├── Conveyor1/
│   ├── Speed (Double)
│   ├── TargetSpeed (Double, Writable)
│   ├── Running (Boolean)
│   ├── ItemCount (Integer)
│   ├── StartCommand (Boolean, Writable)
│   └── StopCommand (Boolean, Writable)
└── Sensor1/
    └── Value (Double)
```

## 🐳 Docker Deployment

### Using Docker Compose

```yaml
version: '3.8'
services:
  virtplc-simulator:
    build: .
    ports:
      - "8080:8080"  # Web API
      - "4840:4840"  # OPC-UA
    volumes:
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

### Using Docker

```bash
# Build the image
docker build -t virtplc-simulator .

# Run the container
docker run -d \
  --name virtplc-simulator \
  -p 8080:8080 \
  -p 4840:4840 \
  -v $(pwd)/data:/app/data \
  virtplc-simulator
```

## 📊 Monitoring Dashboard

Access the real-time monitoring dashboard at http://localhost:8081 (when using Docker Compose).

Features:
- Real-time data visualization
- System status monitoring
- Device health indicators
- Live log streaming
- WebSocket-based updates

## 🔧 Development

### Project Structure

```
simulator/
├── main.py                 # Main entry point
├── cli_manager.py         # CLI management tool
├── web_api.py            # FastAPI web server
├── opcua_server.py       # OPC-UA server
├── database.py           # Device database
├── models.py             # Data models
├── interactive_cli.py    # Interactive CLI
├── simulator_config.yaml # Configuration
├── requirements.txt      # Dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose
└── monitor.html         # Monitoring dashboard
```

### Adding New Signal Generators

1. Add generator type to `SignalGenerator` enum in `models.py`
2. Implement generation logic in `SignalConfig.generate_value()`
3. Update CLI help text in `cli_manager.py`

### Adding New Device Types

1. Define device type in device creation
2. Add mapping logic in `web_api.py` for Spring backend compatibility
3. Update OPC-UA node structure in `opcua_server.py`

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8080 and 4840 are available
2. **WebSocket connection**: Check firewall settings for WebSocket connections
3. **OPC-UA connection**: Verify OPC-UA client configuration
4. **Docker issues**: Check Docker logs with `docker logs virtplc-simulator`

### Logs

- **Docker**: `docker logs virtplc-simulator`
- **Local**: Check console output or `simulator.log`

### Health Checks

- **Web API**: `curl http://localhost:8080/simulation/status`
- **OPC-UA**: Use OPC-UA client to connect to `opc.tcp://localhost:4840/virtplc/`

## 📝 License

This project is part of the VirtPLC system. See the main project README for license information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue in the project repository
