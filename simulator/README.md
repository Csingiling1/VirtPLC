# VirtPLC Enhanced Simulator

A comprehensive factory simulation tool that can run as a CLI tool, web server, or OPC-UA server for industrial automation testing and development.

## Features

- **Multiple Operation Modes**: CLI tool, REST API server, OPC-UA server
- **Device Management**: CRUD operations for factory devices with configurable signals
- **Signal Generators**: Multiple distribution types (uniform, normal, exponential, poisson, sinusoidal, etc.)
- **File-based Persistence**: JSON database for device configurations
- **REST API**: Full REST API for device and signal management
- **OPC-UA Integration**: Industrial protocol support for PLC communication
- **Spring Boot Integration**: Backend service integration
- **Comprehensive Testing**: Unit and integration tests

## Installation

```bash
cd simulator
pip install -r requirements.txt
```

## Quick Start

### Create Sample Devices

```bash
python -m simulator.main --create-samples
```

### CLI Usage

```bash
# List all devices
python -m simulator.main list

# Create a new device
python -m simulator.main create motor1 "Main Drive Motor" --type motor --description "Primary conveyor motor"

# Add signals to device
python -m simulator.main add-signal motor1 speed RPM uniform --min-value 1000 --max-value 1800
python -m simulator.main add-signal motor1 temperature C normal --mean 45 --std-dev 5

# Get device details
python -m simulator.main get motor1

# Run simulation
python -m simulator.main --mode simulate --update-interval 1.0
```

### REST API Server

```bash
# Start REST API server
python -m simulator.main --mode web --host 0.0.0.0 --port 8000
```

### OPC-UA Server

```bash
# Start OPC-UA server
python -m simulator.main --mode opcua --opcua-endpoint "opc.tcp://0.0.0.0:4840/virtplc/"
```

## Device Model

Each factory device contains:

- **id**: Unique identifier
- **name**: Human-readable name
- **description**: Optional description
- **device_type**: Type classification (motor, conveyor, sensor, valve, etc.)
- **signals**: List of signal configurations
- **is_active**: Active status flag
- **created_at/updated_at**: Timestamps

### Signal Configuration

Each signal has:

- **name**: Signal identifier
- **unit**: Measurement unit (RPM, °C, bar, etc.)
- **value**: Current value
- **generator**: Signal generator type
- **is_running**: Active status
- **Generator parameters**: min_value, max_value, mean, std_dev, rate, frequency, amplitude, offset, step_size

## Signal Generators

### Available Generators

- **constant**: Fixed value
- **uniform**: Random values within min/max range
- **normal**: Gaussian distribution with mean and standard deviation
- **exponential**: Exponential distribution with rate parameter
- **poisson**: Poisson process with rate parameter
- **sinusoidal**: Sine wave with frequency, amplitude, and offset
- **triangular**: Triangular distribution
- **step**: Random step changes

### Examples

```bash
# Temperature sensor with normal distribution
python -m simulator.main add-signal temp_sensor temperature C normal --mean 25 --std-dev 2

# Pressure sensor with uniform distribution
python -m simulator.main add-signal pressure_sensor pressure bar uniform --min-value 1.0 --max-value 5.0

# Vibration sensor with exponential distribution
python -m simulator.main add-signal motor vibration "mm/s" exponential --rate 0.1

# Flow sensor with sinusoidal variation
python -m simulator.main add-signal pump flow "L/min" sinusoidal --frequency 0.001 --amplitude 10 --offset 50
```

## REST API Endpoints

### Devices

- `GET /devices` - List all devices
- `POST /devices` - Create new device
- `GET /devices/{device_id}` - Get device details
- `PUT /devices/{device_id}` - Update device
- `DELETE /devices/{device_id}` - Delete device

### Signals

- `GET /devices/{device_id}/signals` - Get all signals for device
- `POST /devices/{device_id}/signals` - Add signal to device
- `DELETE /devices/{device_id}/signals/{signal_name}` - Remove signal
- `GET /devices/{device_id}/signals/{signal_name}` - Get signal value
- `PUT /devices/{device_id}/signals/{signal_name}` - Set signal value

### Simulation

- `GET /simulation/status` - Get simulation status
- `POST /simulation/update` - Trigger simulation update

## Spring Boot Integration

The simulator integrates with the Spring backend through:

### Models

- `SimulatorDevice`: Device representation
- `SignalConfig`: Signal configuration
- `SimulatorService`: REST client service
- `SimulatorController`: REST endpoints

### Configuration

Add to `application.yml`:

```yaml
simulator:
  base-url: http://localhost:8000
```

### Usage Example

```java
@Autowired
private SimulatorService simulatorService;

// Get all devices
List<SimulatorDevice> devices = simulatorService.getAllDevices();

// Get signal value
Optional<Double> temp = simulatorService.getSignalValue("motor1", "temperature");

// Set signal value
simulatorService.setSignalValue("motor1", "speed", 1500.0);
```

## OPC-UA Integration

The simulator provides OPC-UA server for industrial protocol communication:

- **Endpoint**: `opc.tcp://0.0.0.0:4840/virtplc/`
- **Namespace**: Device signals are exposed as OPC-UA variables
- **Structure**: `VirtPLC/{DeviceName}/{SignalName}`

## Testing

Run the test suite:

```bash
cd simulator
python -m pytest test_simulator.py -v
```

### Test Coverage

- Signal generator functionality
- Device CRUD operations
- Database persistence
- Serialization/deserialization
- Integration tests

## Database Configuration

Devices are stored in `devices.json` by default. Configure with:

```bash
python -m simulator.main --db /path/to/devices.json
```

### Simulation Parameters

- **update_rate_hz**: Simulation update frequency (default: 10 Hz)
- **real_time_factor**: Speed multiplier (default: 1.0)
- **enable_random_faults**: Enable fault simulation (default: true)

## Docker Support

Build and run with Docker:

```bash
cd simulator
docker build -t virtplc-simulator .
docker run -p 8000:8000 virtplc-simulator --mode web
```

## Architecture

```text
simulator/
├── main.py              # CLI and main application
├── models.py            # Device and signal models
├── database.py          # File-based persistence
├── web_api.py           # REST API server
├── opcua_server.py     # OPC-UA server
├── test_simulator.py    # Comprehensive tests
├── requirements.txt     # Python dependencies
├── config.yaml          # Configuration file
└── __init__.py          # Package initialization
```

## Development

### Adding New Signal Generators

1. Add generator type to `SignalGenerator` enum
2. Implement generation logic in `SignalConfig.generate_value()`
3. Add CLI parameter handling
4. Update tests

### Extending Device Types

1. Define new device type in application logic
2. Add type-specific signals and behaviors
3. Update validation and serialization

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Port Conflicts**: Change default ports if needed
3. **Database Errors**: Check file permissions for JSON database
4. **OPC-UA Connection**: Verify endpoint configuration

### Logs

Enable debug logging:

```bash
export PYTHONPATH=/path/to/simulator
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

## License

VirtPLC Enhanced Simulator - Part of the VirtPLC Industrial Automation Platform

## TODO

- Test the simulator functionality, including CLI commands, REST API endpoints, OPC-UA server, and Spring backend integration.
