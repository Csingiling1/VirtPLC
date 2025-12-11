# VirtPLC Data Pipeline Deployment Guide

## Overview
This guide covers the complete deployment of the bidirectional data pipeline:
```
Unreal Engine ⟷ MQTT Broker ⟷ Node-RED ⟷ Ignition Edge HMI
                                    ↓
                              Collector → TimescaleDB
```

## Architecture Components

### 1. Data Flow (Unreal → Ignition + TimescaleDB)
- **Unreal Engine** publishes sensor data to MQTT topics:
  - `unreal/factory/conveyor1/rpm` - Conveyor 1 RPM value
  - `unreal/factory/conveyor2/rpm` - Conveyor 2 RPM value
  - `unreal/factory/machine1/position` - Machine position {x, y}
  - `unreal/factory/machine1/status` - Machine status {isReady, isDone}

- **Node-RED** subscribes to `unreal/factory/#` and routes data to:
  - **Ignition Edge**: Publishes to `ignition/tag/write` with tag path mappings
  - **Collector**: Publishes to `collector/ingest` with device metadata

- **Collector** subscribes to `collector/ingest` and stores in **TimescaleDB**

### 2. Command Flow (Ignition → Unreal)
- **Ignition HMI**: Toggle switches bound to tags (`[default]Conveyor1/Running`, etc.)
- **PLC Logic**: Detects tag changes and publishes to `ignition/command/{component}/{command}`
- **Node-RED**: Subscribes to `ignition/command/#` and routes to Unreal Engine
- **Unreal Engine**: Receives commands on `unreal/command/{component}/{action}`

## MQTT Topic Structure

### Data Topics (Unreal → System)
| Topic | Payload Example | Description |
|-------|----------------|-------------|
| `unreal/factory/conveyor1/rpm` | `1500` | Conveyor 1 RPM (0-2000) |
| `unreal/factory/conveyor2/rpm` | `1800` | Conveyor 2 RPM (0-2000) |
| `unreal/factory/machine1/position` | `{"x": 10.5, "y": 20.3}` | Machine position |
| `unreal/factory/machine1/status` | `{"isReady": true, "isDone": false}` | Machine status |

### Command Topics (Ignition → Unreal)
| Topic | Payload Example | Description |
|-------|----------------|-------------|
| `ignition/command/conveyor1/running` | `{"state": true, "timestamp": 1234567890}` | Start Conveyor 1 |
| `ignition/command/conveyor2/running` | `{"state": false, "timestamp": 1234567890}` | Stop Conveyor 2 |
| `ignition/command/machine1/running` | `{"state": true, "timestamp": 1234567890}` | Start Machine |

### System Topics
| Topic | Purpose |
|-------|---------|
| `ignition/tag/write` | Node-RED → Ignition tag updates |
| `collector/ingest` | Node-RED → Collector data ingestion |
| `nodered/heartbeat` | Node-RED health status (every 10s) |

## Tag Mapping

### Ignition Edge Tag Structure
```
[default]
├── Conveyor1
│   ├── Running (Boolean) - Read/Write
│   └── RPM (Float4) - Read Only
├── Conveyor2
│   ├── Running (Boolean) - Read/Write
│   └── RPM (Float4) - Read Only
└── Machine1
    ├── Running (Boolean) - Read/Write
    ├── IsReady (Boolean) - Read Only
    ├── IsDone (Boolean) - Read Only
    ├── X (Float4) - Read Only
    └── Y (Float4) - Read Only
```

### Node-RED Mapping Logic
```javascript
// Unreal → Ignition
unreal/factory/conveyor1/rpm → [default]Conveyor1/RPM
unreal/factory/conveyor2/rpm → [default]Conveyor2/RPM
unreal/factory/machine1/position → [default]Machine1/X, Machine1/Y
unreal/factory/machine1/status → [default]Machine1/IsReady, IsDone

// Ignition → Unreal
ignition/command/conveyor1/running → unreal/command/conveyor1/start|stop
ignition/command/conveyor2/running → unreal/command/conveyor2/start|stop
ignition/command/machine1/running → unreal/command/machine1/start|stop
```

## Deployment Steps

### Prerequisites
- Docker and Docker Compose installed
- Access to remote PLC/Ignition machine (via AnyDesk or SSH)
- MQTT broker credentials: `virtplc/virtplc123`
- Unreal Engine project with MQTT integration

### Step 1: Deploy Docker Services

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults are configured)
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Verify service health:**
   ```bash
   docker-compose ps
   # Check: mqtt, nodered, collector, timescale, ignition-edge
   ```

4. **Check Node-RED logs:**
   ```bash
   docker logs virtplc-nodered
   # Should show MQTT connection successful
   ```

5. **Verify MQTT broker:**
   ```bash
   docker exec virtplc-mqtt mosquitto_passwd -U /mosquitto/config/passwd
   # Should show virtplc user exists
   ```

### Step 2: Deploy Ignition Edge HMI (Remote PLC)

#### Option A: Gateway Web Interface (Recommended)
1. Access Ignition Gateway at `http://PLC_IP:8088`
2. Login with credentials (default: admin/password)
3. Navigate to **Config → Tags → Tag Browser**
4. Click **Import/Export → Import Tags → JSON**
5. Upload `/HMI/IgnitionEdge/tags/tag-definitions.json`
6. Verify tags appear in `[default]` folder
7. Navigate to **Config → Projects → VirtPLC-HMI**
8. Go to **Views → ControlPanel**
9. Right-click view → **Import View → JSON**
10. Upload `/HMI/IgnitionEdge/projects/VirtPLC-HMI/views/ControlPanel/view.json`

#### Option B: Manual File Transfer (If no web access)
1. **Connect via AnyDesk to remote PLC**
2. **Copy files to Ignition data directory:**
   ```
   Source: /HMI/IgnitionEdge/tags/tag-definitions.json
   Destination: C:\Program Files\Inductive Automation\Ignition\data\tags\tag-definitions.json
   
   Source: /HMI/IgnitionEdge/projects/VirtPLC-HMI/views/ControlPanel/view.json
   Destination: C:\Program Files\Inductive Automation\Ignition\data\projects\VirtPLC-HMI\views\ControlPanel\view.json
   
   Source: /HMI/IgnitionEdge/projects/VirtPLC-HMI/views/ControlPanel/resource.json
   Destination: C:\Program Files\Inductive Automation\Ignition\data\projects\VirtPLC-HMI\views\ControlPanel\resource.json
   ```

3. **Restart Ignition Gateway service:**
   - Windows: Services → Ignition Gateway → Restart
   - Or via Gateway web interface: Config → System → Gateway Control → Restart

4. **Verify deployment:**
   - Open browser to `http://localhost:8088/data/perspective/client/VirtPLC-HMI`
   - Should see ControlPanel view with conveyors and machine controls

### Step 3: Configure MQTT Integration in Ignition

1. **Install MQTT Engine Module (if not installed):**
   - Config → System → Modules
   - Install MQTT Engine from Ignition Exchange

2. **Configure MQTT Transmission:**
   - Config → MQTT Engine → Settings
   - Add Broker:
     - **URL**: `tcp://DOCKER_HOST_IP:1883`
     - **Username**: `virtplc`
     - **Password**: `virtplc123`
     - **Client ID**: `ignition-edge`

3. **Configure Tag Change Scripts (for command publishing):**
   - This requires the PLC logic to be deployed (see Step 4)

### Step 4: Deploy PLC Logic (MQTT Command Publisher)

The PLC logic detects Ignition tag changes and publishes MQTT commands.

#### For Siemens TIA Portal:
1. Import `/HMI/PLCLogic/ladder/MQTT_Command_Publisher_Ladder.txt` as reference
2. Create MQTT_Publisher function block using MQTT_CLIENT library
3. Map tags:
   - `%I0.0` ← Ignition `[default]Conveyor1/Running`
   - `%I0.1` ← Ignition `[default]Conveyor2/Running`
   - `%I0.2` ← Ignition `[default]Machine1/Running`
4. Configure MQTT connection to broker at `DOCKER_HOST_IP:1883`

#### For Allen-Bradley/Rockwell:
1. Import `/HMI/PLCLogic/structured/MQTT_Command_Publisher.st` as reference
2. Use EMQX or MSG instruction for MQTT publish
3. Configure edge detection logic for each tag

#### For CODESYS/Beckhoff:
1. Import structured text from `/HMI/PLCLogic/structured/MQTT_Command_Publisher.st`
2. Use TcIoTcps_MqttClient library
3. Configure MQTT client connection

### Step 5: Configure Unreal Engine MQTT Integration

1. **Install MQTT Plugin for Unreal Engine**
   - Use MQTTCore or similar plugin

2. **Configure MQTT Connection:**
   ```cpp
   // Broker: DOCKER_HOST_IP:1883
   // Username: virtplc
   // Password: virtplc123
   ```

3. **Publish Sensor Data:**
   ```cpp
   // Conveyor RPM
   PublishMQTT("unreal/factory/conveyor1/rpm", FString::Printf(TEXT("%d"), RPMValue));
   
   // Machine Position
   FString Payload = FString::Printf(TEXT("{\"x\": %.2f, \"y\": %.2f}"), PosX, PosY);
   PublishMQTT("unreal/factory/machine1/position", Payload);
   
   // Machine Status
   FString Status = FString::Printf(TEXT("{\"isReady\": %s, \"isDone\": %s}"), 
       bIsReady ? TEXT("true") : TEXT("false"),
       bIsDone ? TEXT("true") : TEXT("false"));
   PublishMQTT("unreal/factory/machine1/status", Status);
   ```

4. **Subscribe to Commands:**
   ```cpp
   SubscribeMQTT("unreal/command/#");
   
   // In message handler:
   void OnMQTTMessage(FString Topic, FString Payload) {
       if (Topic == "unreal/command/conveyor1/start") {
           StartConveyor1();
       } else if (Topic == "unreal/command/conveyor1/stop") {
           StopConveyor1();
       }
       // ... similar for other components
   }
   ```

### Step 6: Verify Complete Data Pipeline

1. **Test Unreal → Ignition:**
   ```bash
   # Publish test data from terminal
   docker exec virtplc-mqtt mosquitto_pub -h mqtt -u virtplc -P virtplc123 \
       -t unreal/factory/conveyor1/rpm -m "1500"
   
   # Check Ignition HMI - Conveyor1 RPM gauge should show 1500
   ```

2. **Test Unreal → Collector → TimescaleDB:**
   ```bash
   # Check Collector logs
   docker logs virtplc-collector | grep "Successfully processed"
   
   # Query TimescaleDB
   docker exec virtplc-timescale psql -U virtplc -d virtplc_ts \
       -c "SELECT * FROM plc_data ORDER BY timestamp DESC LIMIT 5;"
   ```

3. **Test Ignition → Unreal:**
   - Toggle Conveyor1 switch in Ignition HMI
   - Monitor MQTT topic:
     ```bash
     docker exec virtplc-mqtt mosquitto_sub -h mqtt -u virtplc -P virtplc123 \
         -t "unreal/command/#" -v
     ```
   - Should see: `unreal/command/conveyor1/running {"state": true, "timestamp": ...}`

4. **Monitor Node-RED Flow:**
   - Access Node-RED UI at `http://DOCKER_HOST_IP:1880`
   - Login with credentials (default: admin/admin)
   - View flow execution in debug panel

## Troubleshooting

### MQTT Connection Issues
```bash
# Test MQTT broker connectivity
docker exec virtplc-mqtt mosquitto_sub -h mqtt -u virtplc -P virtplc123 -t "#" -v

# Check mosquitto logs
docker logs virtplc-mqtt

# Verify password file
docker exec virtplc-mqtt cat /mosquitto/config/passwd
```

### Node-RED Not Routing Data
```bash
# Check Node-RED logs
docker logs virtplc-nodered

# Verify MQTT connection in Node-RED UI
# MQTT nodes should show "connected" status

# Enable debug nodes in Node-RED flow
# Check debug panel for message flow
```

### Collector Not Storing Data
```bash
# Check Collector logs
docker logs virtplc-collector

# Verify TimescaleDB connection
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts -c "\dt"

# Check plc_data table schema
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts -c "\d plc_data"
```

### Ignition Tags Not Updating
1. Verify MQTT Engine module is running
2. Check MQTT broker connection status in Ignition
3. Ensure tag paths match Node-RED mapping
4. Check Ignition Gateway logs: `C:\Program Files\Inductive Automation\Ignition\logs\wrapper.log`

### PLC Commands Not Publishing
1. Verify PLC MQTT client connection
2. Check tag mappings in PLC program
3. Test edge detection logic with manual tag changes
4. Monitor `ignition/command/#` topic for published messages

## Performance Tuning

### MQTT QoS Levels
- Data publishing: QoS 0 (fire and forget) - acceptable for high-frequency sensor data
- Command publishing: QoS 1 (at least once) - ensures command delivery
- Configure in Node-RED MQTT nodes and PLC MQTT client

### TimescaleDB Retention Policy
```sql
-- Keep data for 90 days (configured in docker-compose via cleanup cronjob)
SELECT add_retention_policy('plc_data', INTERVAL '90 days');
```

### Node-RED Flow Optimization
- Use `rate limit` nodes to throttle high-frequency data
- Batch multiple tag writes into single MQTT publish
- Enable Node-RED persistent context for restart resilience

## Security Considerations

### Production Deployment Checklist
- [ ] Change default MQTT password (`virtplc123`)
- [ ] Change Ignition Gateway admin password
- [ ] Enable MQTT TLS/SSL encryption
- [ ] Configure firewall rules for MQTT port (1883/8883)
- [ ] Use environment variables for sensitive credentials
- [ ] Enable Ignition HTTPS (port 8043)
- [ ] Implement network segmentation (OT vs IT networks)
- [ ] Regular backup of Ignition projects and TimescaleDB

## File Reference

### HMI Files
- `/HMI/IgnitionEdge/projects/VirtPLC-HMI/views/ControlPanel/view.json` - Perspective view definition
- `/HMI/IgnitionEdge/projects/VirtPLC-HMI/views/ControlPanel/resource.json` - View metadata
- `/HMI/IgnitionEdge/tags/tag-definitions.json` - Tag definitions

### PLC Logic Files
- `/HMI/PLCLogic/structured/MQTT_Command_Publisher.st` - Structured Text logic
- `/HMI/PLCLogic/ladder/MQTT_Command_Publisher_Ladder.txt` - Ladder Diagram documentation

### Integration Files
- `/nodered/flows/flows.json` - Node-RED flow definitions
- `/nodered/settings.js` - Node-RED configuration
- `/mqtt/config/mosquitto.conf` - MQTT broker configuration
- `/mqtt/config/passwd` - MQTT user credentials

### Infrastructure Files
- `/docker-compose.yml` - Service orchestration
- `/.env.example` - Environment variable template
- `/collector/main.go` - Collector service implementation

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f [service-name]`
2. Review MQTT topic structure and payload format
3. Verify network connectivity between services
4. Consult Ignition Gateway logs and Node-RED debug panel
