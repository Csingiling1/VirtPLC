# OPC-UA Variable Schema

This document defines the OPC-UA namespace and variables used for communication between the Unreal Engine virtual factory and the backend server.

## Connection Details

- **Endpoint**: `opc.tcp://backend:4840`
- **Namespace**: `http://virtplc.accenture.com/factory`
- **Namespace Index**: 2 (default application namespace)

## Variable Structure

All variables follow the hierarchical structure: `Equipment.Parameter`

## Motor Variables

### Motor1

| Node ID | Browse Path | Data Type | Access | Unit | Description |
|---------|-------------|-----------|--------|------|-------------|
| ns=2;s=Motor1.Speed | Motor1.Speed | Float | Read/Write | RPM | Current motor speed |
| ns=2;s=Motor1.Temp | Motor1.Temp | Float | Read | °C | Motor temperature |
| ns=2;s=Motor1.Run | Motor1.Run | Boolean | Read/Write | - | Motor run state |
| ns=2;s=Motor1.Fault | Motor1.Fault | Boolean | Read | - | Fault indicator |
| ns=2;s=Motor1.TargetSpeed | Motor1.TargetSpeed | Float | Write | RPM | Desired speed setpoint |

### Motor2

| Node ID | Browse Path | Data Type | Access | Unit | Description |
|---------|-------------|-----------|--------|------|-------------|
| ns=2;s=Motor2.Speed | Motor2.Speed | Float | Read/Write | RPM | Current motor speed |
| ns=2;s=Motor2.Temp | Motor2.Temp | Float | Read | °C | Motor temperature |
| ns=2;s=Motor2.Run | Motor2.Run | Boolean | Read/Write | - | Motor run state |
| ns=2;s=Motor2.Fault | Motor2.Fault | Boolean | Read | - | Fault indicator |

## Conveyor Variables

### Conveyor1

| Node ID | Browse Path | Data Type | Access | Unit | Description |
|---------|-------------|-----------|--------|------|-------------|
| ns=2;s=Conveyor1.Speed | Conveyor1.Speed | Float | Read/Write | m/min | Belt speed |
| ns=2;s=Conveyor1.Running | Conveyor1.Running | Boolean | Read/Write | - | Conveyor active state |
| ns=2;s=Conveyor1.ItemCount | Conveyor1.ItemCount | Int32 | Read | - | Items on belt |
| ns=2;s=Conveyor1.Emergency | Conveyor1.Emergency | Boolean | Write | - | Emergency stop trigger |

## Sensor Variables

### Sensor1 (Proximity Sensor)

| Node ID | Browse Path | Data Type | Access | Unit | Description |
|---------|-------------|-----------|--------|------|-------------|
| ns=2;s=Sensor1.Detected | Sensor1.Detected | Boolean | Read | - | Object detection state |
| ns=2;s=Sensor1.Distance | Sensor1.Distance | Float | Read | mm | Distance to object |

### Sensor2 (Temperature Sensor)

| Node ID | Browse Path | Data Type | Access | Unit | Description |
|---------|-------------|-----------|--------|------|-------------|
| ns=2;s=Sensor2.Temperature | Sensor2.Temperature | Float | Read | °C | Ambient temperature |
| ns=2;s=Sensor2.Humidity | Sensor2.Humidity | Float | Read | % | Relative humidity |

## System Control Variables

| Node ID | Browse Path | Data Type | Access | Unit | Description |
|---------|-------------|-----------|--------|------|-------------|
| ns=2;s=System.Reset | System.Reset | Boolean | Write | - | Reset all equipment |
| ns=2;s=System.EmergencyStop | System.EmergencyStop | Boolean | Read/Write | - | Global emergency stop |
| ns=2;s=System.Mode | System.Mode | Int32 | Read/Write | - | Operation mode (0=Manual, 1=Auto) |

## JSON Data Format

When sending test data to the backend, use this JSON structure:

```json
{
  "timestamp": "2025-10-19T10:30:00Z",
  "variables": [
    {
      "nodeId": "ns=2;s=Motor1.Speed",
      "value": 1500.0,
      "quality": "Good"
    },
    {
      "nodeId": "ns=2;s=Motor1.Temp",
      "value": 45.2,
      "quality": "Good"
    },
    {
      "nodeId": "ns=2;s=Motor1.Run",
      "value": true,
      "quality": "Good"
    }
  ]
}
```

## Update Rates

- **Motor Speed/Temp**: 500ms
- **Sensor Data**: 100ms
- **Conveyor Status**: 1000ms
- **System Control**: On change

## Implementation Notes

1. All floating-point values use IEEE 754 single precision
2. Timestamps use ISO 8601 format with UTC timezone
3. Quality codes follow OPC-UA standard (Good, Bad, Uncertain)
4. Boolean true = motor running/sensor triggered
5. Write operations should validate range limits before sending

## Adding New Variables

When adding new equipment or parameters:

1. Follow the `Equipment.Parameter` naming convention
2. Use namespace index 2
3. Update this document with complete specifications
4. Coordinate with backend team for server-side node creation
5. Add corresponding C++ or Blueprint logic in Unreal
