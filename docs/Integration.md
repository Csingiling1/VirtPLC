# Integration Guide

## System Integration Overview

This document describes how the HMI subsystem integrates with other VirtPLC components.

## Architecture

```
┌─────────────────┐
│  Unreal Engine  │ (Virtual Factory)
│  (UEBlender)    │
└────────┬────────┘
         │ OPC-UA
         ▼
┌─────────────────┐
│  Spring Boot    │ (Backend Server)
│  OPC-UA Server  │
│    (Web)        │
└────────┬────────┘
         │ OPC-UA
         ├─────────────┐
         ▼             ▼
┌─────────────────┐   ┌──────────────┐
│ Ignition Edge   │   │ TimeBaseDB   │
│     (HMI)       │   │  (Storage)   │
└─────────────────┘   └──────────────┘
```

## OPC-UA Integration

### Connection to Backend

The HMI connects to the Spring Boot backend OPC-UA server:

**Endpoint**: `opc.tcp://backend:4840`

**Configuration in Ignition**:
1. Navigate to Config → OPC UA → Connections
2. Create connection with name `Backend-OPC-UA`
3. Set endpoint URL
4. Configure security (None for development)
5. Set subscription parameters

### Tag Mapping

All HMI tags are bound to OPC-UA nodes on the backend server.

| HMI Tag | OPC-UA Node | Direction |
|---------|-------------|-----------|
| Motor1/Speed | ns=2;s=Motor1.Speed | Read/Write |
| Motor1/Temp | ns=2;s=Motor1.Temp | Read |
| Motor1/Run | ns=2;s=Motor1.Run | Read/Write |
| Conveyor1/Speed | ns=2;s=Conveyor1.Speed | Read/Write |
| System/EmergencyStop | ns=2;s=System.EmergencyStop | Read/Write |

### Data Flow

1. **Unreal → Backend**: Virtual factory sends telemetry
2. **Backend → HMI**: OPC-UA server publishes data
3. **HMI → Backend**: Operator commands written to OPC-UA nodes
4. **Backend → Unreal**: Commands forwarded to virtual factory

## TimeBaseDB Integration

### Historian Connection

The Ignition Tag Historian writes to TimeBaseDB for long-term storage.

**JDBC Connection**: `dts://timebase:8011`

### Data Storage Flow

```
Tag Value Change
  ↓
Tag Historian (Ignition)
  ↓
Store & Forward Buffer
  ↓
TimeBaseDB JDBC Driver
  ↓
TimeBaseDB Stream (factory_data)
```

### Historical Query Access

**From HMI**:
- Power Chart component queries TimeBaseDB
- System queries via `system.tag.queryTagHistory()`

**From Backend API**:
- REST endpoints query TimeBaseDB
- Data served to React frontend

## Real-Time Data Synchronization

### Subscription Model

OPC-UA uses a publish-subscribe model:

1. Ignition creates subscription on backend OPC-UA server
2. Backend notifies Ignition of data changes
3. Ignition updates tag values
4. Tag change triggers:
   - HMI component updates
   - Historian writes
   - Alarm evaluations
   - Event scripts

### Update Rates

| Data Type | Update Rate | Reason |
|-----------|-------------|--------|
| Motor Speed | 500ms | Fast-changing, critical |
| Temperature | 1000ms | Slower changes |
| Status Booleans | On Change | Immediate notification |
| Sensor Data | 250ms | Proximity detection |

## Control Command Flow

### Example: Start Motor 1

1. Operator clicks **Start** button in HMI
2. Button onClick script executes:
   ```python
   system.tag.writeBlocking(["[default]Motor1/Run"], [True])
   ```
3. Ignition writes to OPC-UA node `ns=2;s=Motor1.Run`
4. Backend OPC-UA server receives write
5. Backend forwards command to Unreal Engine
6. Virtual motor starts in 3D environment
7. Unreal sends updated speed telemetry
8. Backend publishes speed to OPC-UA
9. HMI receives speed update
10. Speed gauge animates to new value

## API Integration (Optional)

While the primary integration is via OPC-UA, REST APIs can be used for:

### HMI → Backend API

```python
# In Ignition script
import system.net

url = "http://backend:8080/api/data/latest"
response = system.net.httpGet(url)

if response.good:
    data = system.util.jsonDecode(response.text)
    # Use data in HMI
```

### Embedded React Dashboard

The HMI can embed the React frontend in an iframe:

```html
<!-- In Perspective Iframe component -->
<iframe src="http://backend:3000/dashboard" 
        width="100%" 
        height="800px"
        frameborder="0">
</iframe>
```

## Security Integration

### Authentication

**Ignition**:
- Internal user source
- LDAP/Active Directory (production)
- Role-based permissions

**Backend**:
- JWT authentication
- Token validation

**Integration**:
- Ignition can pass user context to backend APIs
- Backend verifies permissions for OPC-UA writes

### Example: Authenticated API Call

```python
# Get user token from Ignition
user = system.security.getUsername()
token = system.tag.readBlocking(["[default]System/AuthToken"])[0].value

# Call backend API with auth
headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json"
}

response = system.net.httpPost(
    "http://backend:8080/api/command/motor/start",
    headers=headers,
    data='{"motorId": "Motor1"}'
)
```

## Alarm Integration

### Alarm Sources

1. **Local Alarms**: Configured in Ignition tags
2. **Backend Alarms**: Received via OPC-UA
3. **AI Predictions**: Received via WebSocket from AI module

### Alarm Routing

```
Alarm Occurs
  ↓
Ignition Alarm Pipeline
  ↓
├─ On-Screen Notification
├─ Email/SMS (via Notification Profile)
├─ Write to TimeBaseDB (alarms_events stream)
└─ Forward to Backend (via REST API)
```

## WebSocket Integration (AI Module)

For real-time AI predictions:

```python
# In Ignition gateway script
import system.util.sendRequest

# Subscribe to AI predictions
ws_url = "ws://ai-service:3001/predictions"

def onPrediction(message):
    data = system.util.jsonDecode(message)
    
    # Update tag with AI prediction
    system.tag.writeBlocking(
        ["[default]AI/NextFailure"],
        [data["prediction"]]
    )
    
    # Show alert in HMI
    if data["confidence"] > 0.8:
        system.perspective.sendMessage("prediction", {
            "message": data["message"],
            "severity": "warning"
        })

# Connection logic would go here
```

## Testing Integration

### Test OPC-UA Connection

```python
# In Ignition script console
from com.inductiveautomation.opcua.client import OPCUAClient

client = system.opc.getOPCUAClient("Backend-OPC-UA")
if client.isConnected():
    print "Connected successfully"
else:
    print "Connection failed"
```

### Test Tag Read/Write

```python
# Read test
speed = system.tag.readBlocking(["[default]Motor1/Speed"])[0]
print "Speed:", speed.value, "Quality:", speed.quality

# Write test  
result = system.tag.writeBlocking(["[default]Motor1/TargetSpeed"], [1500.0])
if result[0].quality.isGood():
    print "Write successful"
else:
    print "Write failed:", result[0].quality
```

### Test TimeBase Historian

```python
# Query last hour of data
import system.date

endDate = system.date.now()
startDate = system.date.addHours(endDate, -1)

data = system.tag.queryTagHistory(
    paths=["[default]Motor1/Speed"],
    startDate=startDate,
    endDate=endDate,
    returnSize=100
)

print "Retrieved", data.getRowCount(), "samples"
```

## Docker Networking

When running in Docker containers:

```yaml
# docker-compose.yml (on develop branch)
services:
  backend:
    ports:
      - "4840:4840"  # OPC-UA
      - "8080:8080"  # REST API
    networks:
      - virtplc-network
  
  hmi:
    ports:
      - "8088:8088"  # Ignition Gateway
    environment:
      - OPCUA_ENDPOINT=opc.tcp://backend:4840
    networks:
      - virtplc-network
    depends_on:
      - backend
      - timebase
  
  timebase:
    ports:
      - "8011:8011"
    networks:
      - virtplc-network

networks:
  virtplc-network:
    driver: bridge
```

## Troubleshooting Integration

### OPC-UA Connection Issues

1. Check endpoint URL: `opc.tcp://backend:4840` or `opc.tcp://localhost:4840`
2. Verify backend OPC-UA server is running
3. Check firewall rules for port 4840
4. Review Ignition logs: Config → Status → Diagnostics → Logs
5. Test with UAExpert client

### TimeBase Not Storing Data

1. Verify JDBC connection in Ignition
2. Check TimeBase service status
3. Ensure tags have `historyEnabled = true`
4. Review store-and-forward buffer
5. Check TimeBase logs

### Data Not Syncing

1. Check OPC-UA subscription status
2. Verify tag quality indicators
3. Review network latency
4. Check backend server logs
5. Verify data types match between systems

## Performance Considerations

### Optimize OPC-UA

- Use appropriate subscription rates
- Enable dead-band filtering
- Group related tags in same subscription
- Monitor bandwidth usage

### Optimize Historian

- Set appropriate sample rates
- Use dead-band on analog values
- Implement store-and-forward for reliability
- Regular data pruning per retention policy

### Optimize HMI

- Limit active components per page
- Use session caching
- Optimize chart queries (time ranges)
- Minimize simultaneous WebSocket connections

## Next Steps

1. Verify all endpoints are accessible
2. Test OPC-UA connection and tag reads/writes
3. Configure TimeBaseDB historian
4. Test alarm propagation
5. Set up monitoring and logging
6. Conduct integration testing with all modules
