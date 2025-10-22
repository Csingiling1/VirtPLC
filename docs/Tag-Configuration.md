# Tag Configuration

Complete tag definitions for the VirtPLC HMI system.

## Tag Provider Structure

```
[default]
├── Motor1/
│   ├── Speed (Float)
│   ├── Temp (Float)
│   ├── Run (Boolean)
│   ├── Fault (Boolean)
│   ├── TargetSpeed (Float)
│   └── MaxSpeed (Float)
├── Motor2/
│   ├── Speed (Float)
│   ├── Temp (Float)
│   ├── Run (Boolean)
│   ├── Fault (Boolean)
│   ├── TargetSpeed (Float)
│   └── MaxSpeed (Float)
├── Conveyor1/
│   ├── Speed (Float)
│   ├── Running (Boolean)
│   ├── ItemCount (Int)
│   └── Emergency (Boolean)
├── Sensor1/
│   ├── Detected (Boolean)
│   └── Distance (Float)
├── Sensor2/
│   ├── Temperature (Float)
│   └── Humidity (Float)
└── System/
    ├── Reset (Boolean)
    ├── EmergencyStop (Boolean)
    └── Mode (Int)
```

## Motor 1 Tags

### Motor1/Speed

| Property | Value |
|----------|-------|
| Name | Speed |
| Data Type | Float |
| OPC Item Path | ns=2;s=Motor1.Speed |
| Access | Read/Write |
| Units | RPM |
| Min Value | 0.0 |
| Max Value | 2500.0 |
| History Enabled | Yes |
| History Provider | TimeBase-Historian |
| Sample Mode | On Change |
| Deadband | 10.0 |
| Alarm Config | High: 2000 RPM (Warning), 2200 RPM (Critical) |

### Motor1/Temp

| Property | Value |
|----------|-------|
| Name | Temp |
| Data Type | Float |
| OPC Item Path | ns=2;s=Motor1.Temp |
| Access | Read |
| Units | °C |
| Min Value | 0.0 |
| Max Value | 150.0 |
| History Enabled | Yes |
| History Provider | TimeBase-Historian |
| Sample Mode | Periodic (1000ms) |
| Deadband | 1.0 |
| Alarm Config | High: 75°C (Warning), 85°C (Critical) |

### Motor1/Run

| Property | Value |
|----------|-------|
| Name | Run |
| Data Type | Boolean |
| OPC Item Path | ns=2;s=Motor1.Run |
| Access | Read/Write |
| History Enabled | Yes |
| History Provider | TimeBase-Historian |
| Sample Mode | On Change |
| Documentation | True = Motor running, False = Motor stopped |

### Motor1/Fault

| Property | Value |
|----------|-------|
| Name | Fault |
| Data Type | Boolean |
| OPC Item Path | ns=2;s=Motor1.Fault |
| Access | Read |
| History Enabled | Yes |
| History Provider | TimeBase-Historian |
| Sample Mode | On Change |
| Alarm Config | True = Critical Alarm |
| Alarm Priority | Critical |

### Motor1/TargetSpeed

| Property | Value |
|----------|-------|
| Name | TargetSpeed |
| Data Type | Float |
| OPC Item Path | ns=2;s=Motor1.TargetSpeed |
| Access | Write |
| Units | RPM |
| Min Value | 0.0 |
| Max Value | 2500.0 |
| Default Value | 1500.0 |
| History Enabled | No |

### Motor1/MaxSpeed

| Property | Value |
|----------|-------|
| Name | MaxSpeed |
| Data Type | Float |
| Access | Memory (constant) |
| Value | 2500.0 |
| Units | RPM |
| Documentation | Maximum rated speed for Motor 1 |

## Motor 2 Tags

Motor 2 follows the same structure as Motor 1 with corresponding OPC paths:
- `ns=2;s=Motor2.Speed`
- `ns=2;s=Motor2.Temp`
- `ns=2;s=Motor2.Run`
- `ns=2;s=Motor2.Fault`

## Conveyor 1 Tags

### Conveyor1/Speed

| Property | Value |
|----------|-------|
| Name | Speed |
| Data Type | Float |
| OPC Item Path | ns=2;s=Conveyor1.Speed |
| Access | Read/Write |
| Units | m/min |
| Min Value | 0.0 |
| Max Value | 50.0 |
| History Enabled | Yes |
| Sample Mode | On Change |
| Deadband | 0.5 |

### Conveyor1/Running

| Property | Value |
|----------|-------|
| Name | Running |
| Data Type | Boolean |
| OPC Item Path | ns=2;s=Conveyor1.Running |
| Access | Read/Write |
| History Enabled | Yes |
| Sample Mode | On Change |

### Conveyor1/ItemCount

| Property | Value |
|----------|-------|
| Name | ItemCount |
| Data Type | Int32 |
| OPC Item Path | ns=2;s=Conveyor1.ItemCount |
| Access | Read |
| Min Value | 0 |
| Max Value | 100 |
| History Enabled | Yes |
| Sample Mode | On Change |
| Alarm Config | High: 80 (Warning), 95 (Critical) |

### Conveyor1/Emergency

| Property | Value |
|----------|-------|
| Name | Emergency |
| Data Type | Boolean |
| OPC Item Path | ns=2;s=Conveyor1.Emergency |
| Access | Write |
| Documentation | Emergency stop trigger |

## Sensor Tags

### Sensor1/Detected

| Property | Value |
|----------|-------|
| Name | Detected |
| Data Type | Boolean |
| OPC Item Path | ns=2;s=Sensor1.Detected |
| Access | Read |
| History Enabled | Yes |
| Sample Mode | On Change |
| Documentation | Proximity sensor detection state |

### Sensor1/Distance

| Property | Value |
|----------|-------|
| Name | Distance |
| Data Type | Float |
| OPC Item Path | ns=2;s=Sensor1.Distance |
| Access | Read |
| Units | mm |
| Min Value | 0.0 |
| Max Value | 100.0 |
| History Enabled | Yes |
| Sample Mode | Periodic (500ms) |

### Sensor2/Temperature

| Property | Value |
|----------|-------|
| Name | Temperature |
| Data Type | Float |
| OPC Item Path | ns=2;s=Sensor2.Temperature |
| Access | Read |
| Units | °C |
| Min Value | -20.0 |
| Max Value | 100.0 |
| History Enabled | Yes |
| Sample Mode | Periodic (2000ms) |
| Deadband | 0.5 |

### Sensor2/Humidity

| Property | Value |
|----------|-------|
| Name | Humidity |
| Data Type | Float |
| OPC Item Path | ns=2;s=Sensor2.Humidity |
| Access | Read |
| Units | % |
| Min Value | 0.0 |
| Max Value | 100.0 |
| History Enabled | Yes |
| Sample Mode | Periodic (2000ms) |
| Deadband | 2.0 |
| Alarm Config | High: 80% (Warning), 90% (Critical) |

## System Tags

### System/Reset

| Property | Value |
|----------|-------|
| Name | Reset |
| Data Type | Boolean |
| OPC Item Path | ns=2;s=System.Reset |
| Access | Write |
| Documentation | Reset all equipment to default state |

### System/EmergencyStop

| Property | Value |
|----------|-------|
| Name | EmergencyStop |
| Data Type | Boolean |
| OPC Item Path | ns=2;s=System.EmergencyStop |
| Access | Read/Write |
| History Enabled | Yes |
| Sample Mode | On Change |
| Alarm Config | True = Critical Alarm (highest priority) |
| Alarm Priority | Critical |
| Documentation | Global emergency stop state |

### System/Mode

| Property | Value |
|----------|-------|
| Name | Mode |
| Data Type | Int32 |
| OPC Item Path | ns=2;s=System.Mode |
| Access | Read/Write |
| History Enabled | Yes |
| Sample Mode | On Change |
| Documentation | 0=Manual, 1=Automatic |

## Tag Export/Import

### Export Tags to JSON

In Ignition Designer:
1. Select tag folder
2. Right-click → Export Tags
3. Choose JSON format
4. Save to `IgnitionEdge/tags/tag-definitions.json`

### Import Tags from JSON

1. In Gateway Config → Tags
2. Click More → Import Tags
3. Select JSON file
4. Review and Import

## Tag Naming Conventions

- Use PascalCase for tag names
- Group tags by equipment
- Use descriptive names (not abbreviations)
- Document units in tag configuration
- Prefix system-wide tags with "System/"

## History Configuration

### Retention Policies

| Tag Group | Retention | Compression |
|-----------|-----------|-------------|
| Motor Speed/Temp | 30 days | Dead-band |
| Status tags | 90 days | On-change |
| Alarms | 1 year | None |
| Sensor data | 7 days | Dead-band |

### Storage Calculation

Estimated storage per day:
- Motors (2): ~50MB
- Conveyor: ~20MB
- Sensors: ~30MB
- Total: ~100MB/day = 3GB/month

## Scripting with Tags

### Read Tag Value

```python
# Single tag
value = system.tag.readBlocking(["[default]Motor1/Speed"])[0].value

# Multiple tags
paths = ["[default]Motor1/Speed", "[default]Motor1/Temp"]
values = system.tag.readBlocking(paths)
speed = values[0].value
temp = values[1].value
```

### Write Tag Value

```python
# Single write
system.tag.writeBlocking(["[default]Motor1/Run"], [True])

# Multiple writes
paths = ["[default]Motor1/TargetSpeed", "[default]Motor2/TargetSpeed"]
values = [1500.0, 1200.0]
system.tag.writeBlocking(paths, values)
```

### Tag Change Script

Attach to Motor1/Fault tag:

```python
# When fault occurs, stop motor
if newValue.value == True:
    system.tag.writeBlocking(["[default]Motor1/Run"], [False])
    system.perspective.sendMessage("alarm", {
        "message": "Motor 1 Fault Detected",
        "severity": "critical"
    })
```

## Performance Optimization

1. **Deadbands**: Use appropriate deadband values to reduce unnecessary updates
2. **Sample Rates**: Match to data volatility (fast=motors, slow=ambient sensors)
3. **History Pruning**: Regular cleanup of old data
4. **Tag Groups**: Organize tags for efficient browsing
5. **Caching**: Enable tag cache for frequently read tags

## Security

- **Read-Only**: Sensor tags should be read-only
- **Write Protection**: Control tags require operator role
- **Audit Trail**: Enable for all write operations
- **Emergency Stop**: Accessible to all users (no restriction)
