# VirtPLC HMI - Enterprise Factory Control System

## Overview

Enterprise-grade HMI (Human-Machine Interface) system built on Ignition Edge for real-time factory monitoring and control. Features include motor and conveyor control, real-time data visualization, alarm management, and historical trending with TimescaleDB integration.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Ignition Edge Gateway                      │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │ Perspective│  │ OPC-UA     │  │ Tag History/Alarms   │  │
│  │ Module     │  │ Client     │  │                      │  │
│  └────────────┘  └────────────┘  └──────────────────────┘  │
└──────────┬──────────────┬────────────────┬──────────────────┘
           │              │                │
           │              │                │
    ┌──────▼──────┐  ┌───▼────────┐  ┌───▼──────────┐
    │ TimescaleDB │  │  Backend   │  │ PostgreSQL   │
    │ Time-Series │  │  OPC-UA    │  │ Relational   │
    │ Database    │  │  Server    │  │ Database     │
    └─────────────┘  └────────────┘  └──────────────┘
```

## Features

### ✅ Real-Time Monitoring
- Live motor speed and temperature monitoring
- Conveyor speed and item count tracking
- System status indicators
- Emergency stop functionality

### ✅ Interactive Control
- Start/stop motor controls with safety interlocks
- Target speed adjustment
- Conveyor control with item counting
- Emergency stop with system-wide shutdown

### ✅ Data Visualization
- Real-time trend charts for all metrics
- Historical data trending (30-90 days retention)
- Custom dashboard creation
- Alarm journal with filtering

### ✅ Safety & Interlocks
- Emergency stop protection
- Overspeed and over-temperature protection
- Fault detection and logging
- Safety interlocks between equipment

### ✅ Enterprise Features
- Role-based access control (planned)
- Alarm notification pipelines
- Historical data retention policies
- Automatic backup and recovery
- High availability configuration (planned)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- 4GB+ RAM available
- Ports 8088, 8043, 4840, 8011, 5432 available

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Dedzsinator/VirtPLC.git
   cd VirtPLC/HMI
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the HMI**
   - Open browser to: http://localhost:8088
   - Default credentials: admin / password (change in production!)
   - Navigate to: `/data/perspective/client/VirtPLC-HMI`

### First-Time Setup

1. **Configure OPC-UA Connection**
   - Navigate to Gateway → Connections → OPC UA
   - Verify Backend-OPC-UA connection is active
   - Test connection

2. **Verify Tag Provider**
   - Navigate to Gateway → Tags → default
   - Verify all tags are present (Motor1, Motor2, Conveyor1, System)
   - Check tag quality (should be Good)

3. **Configure Historical Data**
   - Navigate to Gateway → Tag History
   - Verify TimeBase storage provider is configured
   - Check that history is logging

4. **Test HMI Views**
   - Open Overview page
   - Navigate to Motor Control
   - Test Start/Stop buttons
   - Verify real-time updates

## Project Structure

```
HMI/
├── IgnitionEdge/
│   ├── config/
│   │   └── gateway.xml                 # Gateway configuration
│   ├── projects/
│   │   └── VirtPLC-HMI/
│   │       ├── project.json            # Project metadata
│   │       ├── views/                  # Perspective views
│   │       │   ├── Overview/
│   │       │   ├── MotorControl/
│   │       │   ├── ConveyorControl/
│   │       │   ├── Alarms/
│   │       │   └── Trends/
│   │       └── scripts/                # Python scripts
│   │           ├── CommonScripts.py
│   │           └── TagHelper.py
│   └── tags/
│       └── tag-definitions.json        # Tag configurations
├── PLCLogic/
│   ├── structured/                     # IEC 61131-3 ST programs
│   │   ├── Motor1_Control.st
│   │   ├── Motor2_Control.st
│   │   ├── Conveyor1_Control.st
│   │   └── System_Control.st
│   └── ladder/                         # Ladder logic documentation
│       └── Motor1_Control_Ladder.txt
├── TimeBaseDB/
│   └── config/
│       ├── timebase.yaml              # TimeBase configuration
│       └── schemas.xml                # Data schemas
├── tests/
│   ├── test_tag_operations.py         # Unit tests
│   ├── test_integration.py            # Integration tests
│   ├── test_e2e.py                    # End-to-end tests
│   └── requirements.txt               # Test dependencies
├── Dockerfile                          # HMI container image
├── docker-compose.yml                 # Multi-container setup
└── README.md                          # This file
```

## Views Description

### Overview
Main dashboard showing system status at a glance.

### Motor Control
Detailed motor control interface with:
- Real-time speed and temperature gauges
- Start/Stop/Reset buttons
- Target speed adjustment
- Fault indicators

### Conveyor Control
Conveyor monitoring and control with:
- Speed visualization
- Item count tracking
- Start/Stop controls
- Emergency stop button

### Alarms
Alarm journal with:
- Real-time alarm status
- Acknowledgment controls
- Filtering and search
- Alarm history

### Trends
Historical data visualization:
- Motor speed trends
- Temperature trends
- Conveyor metrics
- Configurable time ranges

## Development

### Running Tests

```bash
# Install test dependencies
cd HMI/tests
pip install -r requirements.txt

# Run all tests
cd ..
pytest tests/ -v

# Run specific test types
pytest tests/ -v -m unit           # Unit tests only
pytest tests/ -v -m integration    # Integration tests
pytest tests/ -v -m e2e           # End-to-end tests

# Run with coverage
pytest tests/ -v --cov --cov-report=html
```

### Adding New Views

1. Create view directory: `IgnitionEdge/projects/VirtPLC-HMI/views/NewView/`
2. Add `view.json` with view definition
3. Update `project.json` to register the view
4. Add navigation button in Overview or appropriate parent view

### Adding New Tags

1. Edit `IgnitionEdge/tags/tag-definitions.json`
2. Add tag definition with appropriate OPC path
3. Configure history and alarms if needed
4. Restart gateway or use tag import

### Modifying PLC Logic

1. Edit structured text programs in `PLCLogic/structured/`
2. Test logic changes
3. Update ladder logic documentation if applicable
4. Commit changes

## Configuration

### Gateway Settings

Edit `IgnitionEdge/config/gateway.xml`:

- **HTTP/HTTPS Ports**: Modify `<httpPort>` and `<httpsPort>`
- **Database Connections**: Update connection strings and credentials
- **OPC-UA Settings**: Configure endpoint URLs and security
- **Tag History**: Adjust retention periods and storage
- **Alarms**: Configure notification pipelines

### TimeBase Settings

Edit `TimeBaseDB/config/timebase.yaml`:

- **Retention Policies**: Set data retention periods per stream
- **Performance**: Adjust cache size and thread counts
- **Compression**: Enable/disable compression
- **Backup**: Configure backup schedule

### Database Schemas

Edit `TimeBaseDB/config/schemas.xml` to modify:

- Motor telemetry fields
- Conveyor data structure
- Alarm event schema
- AI prediction schema

## Deployment

### Development Environment

```bash
docker-compose up -d
```

### Production Deployment

1. **Configure SSL/TLS**
   ```bash
   # Generate certificates
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout certs/server.key -out certs/server.crt
   
   # Update .env
   SSL_ENABLED=true
   ```

2. **Set Strong Passwords**
   ```bash
   # Update .env with secure passwords
   GATEWAY_PASSWORD=<strong-password>
   POSTGRES_PASSWORD=<strong-password>
   ```

3. **Configure Backup**
   ```bash
   # Ensure backup volume is mounted to persistent storage
   # Configure backup schedule in gateway.xml
   ```

4. **Deploy with Resource Limits**
   ```bash
   docker-compose -f docker-compose.yml \
                  -f docker-compose.prod.yml up -d
   ```

5. **Configure Monitoring**
   - Access Grafana at http://localhost:3000
   - Import provided dashboards
   - Configure alerts

### High Availability Setup

For production high availability:

1. Enable gateway redundancy in `gateway.xml`
2. Deploy redundant gateway nodes
3. Configure shared database for both nodes
4. Set up load balancer for gateway access
5. Configure failover monitoring

See `docs/high-availability.md` for detailed instructions (planned).

## Monitoring

### Health Checks

All services include health checks:

```bash
# Check service health
docker-compose ps

# View gateway logs
docker-compose logs -f ignition-gateway

# Check TimeBase status
curl http://localhost:8011/health
```

### Metrics

Prometheus metrics available at:
- Gateway: http://localhost:8088/metrics
- TimeBase: http://localhost:9090/metrics

### Grafana Dashboards

Access Grafana at http://localhost:3000

Pre-configured dashboards:
- HMI Overview
- Tag Performance
- System Resources
- Alarm Statistics

## Troubleshooting

### Gateway Won't Start

```bash
# Check logs
docker-compose logs ignition-gateway

# Common issues:
# - Port 8088 already in use
# - Insufficient memory
# - Invalid configuration XML
```

### Tags Show Bad Quality

```bash
# Check OPC-UA connection
# 1. Verify backend OPC-UA server is running
docker-compose ps backend-opcua

# 2. Test connection from gateway
# Gateway → Connections → OPC UA → Backend-OPC-UA → Test Connection

# 3. Check firewall rules
```

### Historical Data Not Logging

```bash
# Check TimeBase connection
docker-compose logs timebase

# Verify tag history provider
# Gateway → Tag History → Providers → Check status

# Check disk space
df -h
```

### Performance Issues

```bash
# Increase resource limits in docker-compose.yml
# Monitor resource usage
docker stats

# Check database performance
docker-compose exec postgres pg_top

# Optimize TimeBase cache
# Edit TimeBaseDB/config/timebase.yaml
```

## Security

### Authentication

- Default gateway admin: `admin` / `password`
- **Change immediately in production!**
- Configure LDAP/AD integration for enterprise auth

### Network Security

- Use SSL/TLS for all connections in production
- Restrict network access with firewall rules
- Use VPN for remote access
- Enable gateway network encryption

### Data Security

- Encrypt database connections
- Enable backup encryption
- Configure audit logging
- Regular security patches

## Maintenance

### Backup

Automated backups run daily at 2 AM (configurable):

```bash
# Manual backup
docker-compose exec ignition-gateway \
  /usr/local/bin/ignition/gwcmd.sh --backup /backup/manual-backup.zip

# Restore from backup
docker-compose exec ignition-gateway \
  /usr/local/bin/ignition/gwcmd.sh --restore /backup/backup.zip
```

### Updates

```bash
# Update to new Ignition version
# 1. Backup current system
# 2. Update Dockerfile with new version
# 3. Rebuild image
docker-compose build ignition-gateway

# 4. Test in development
# 5. Deploy to production
docker-compose up -d ignition-gateway
```

### Database Maintenance

```bash
# PostgreSQL maintenance
docker-compose exec postgres psql -U virtplc -d virtplc

# Vacuum database
VACUUM ANALYZE;

# Check database size
SELECT pg_database_size('virtplc');
```

## Support

For issues, questions, or contributions:

- GitHub Issues: https://github.com/Dedzsinator/VirtPLC/issues
- Documentation: `/docs` directory
- Team Contact: [Add contact info]

## License

[Add license information]

## Contributors

- [Team members]

## Changelog

### Version 1.0.0 (2025-10-23)
- Initial release
- Complete HMI implementation with Ignition Edge
- Motor and conveyor control
- TimeBase integration
- Comprehensive test suite
- CI/CD pipeline
- Docker containerization
