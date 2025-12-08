# Ignition Edge Device Monitor - Quick Setup Guide

## Overview

This package provides a complete, drag-and-drop Ignition Edge project for monitoring factory device position (X, Y coordinates) with:
- Pre-configured tags
- Real-time visualization
- MQTT publishing to Node-RED
- Built-in device simulator
- Professional HMI interface

## What's Included

```
HMI/IgnitionEdge/
├── projects/FactoryDevice/          # Main project
│   ├── project.json                 # Project configuration
│   ├── views/DeviceMonitor.json     # HMI visualization
│   ├── gateway-scripts/             # Automation scripts
│   │   └── device-simulator.py      # Device position simulator
│   └── mqtt-config.json             # MQTT transmission settings
└── tags/device_tags.json            # Tag definitions
```

## Features

### Tags
- **Device_X_Position** (Float) - X coordinate in meters
- **Device_Y_Position** (Float) - Y coordinate in meters  
- **Device_Speed** (Float) - Movement speed in m/s
- **Device_Active** (Boolean) - Device active status
- **Device_Status** (String) - IDLE, MOVING, or ERROR
- **Device_ID** (Int) - Unique device identifier
- **Last_Update** (DateTime) - Auto-updated timestamp
- **Distance_From_Origin** (Float) - Calculated distance from (0,0)

### HMI View
- Real-time status display
- Position data panel
- X/Y coordinate scatter chart
- LED indicators
- Professional styling

### MQTT Publishing
- Auto-publishes tag changes to MQTT
- Topic format: `unreal/factory/{tagName}`
- JSON payload with value, quality, timestamp
- Compatible with Node-RED bridge

## Installation

### Method 1: Manual Import (Recommended)

#### Step 1: Import Tags
1. Open Ignition Gateway web interface (http://localhost:8088)
2. Go to **Config → Tags → Designer**
3. Launch Designer
4. In Designer Tag Browser, right-click on **[default]**
5. Select **Import Tags → Import JSON**
6. Select file: `HMI/IgnitionEdge/tags/device_tags.json`
7. Click **Import**

#### Step 2: Create Project
1. In Designer, go to **File → New → Perspective Project**
2. Name: **Factory Device Monitor**
3. Click **Create**

#### Step 3: Import View
1. In Project Browser, right-click **views** folder
2. Select **Import**
3. Navigate to `HMI/IgnitionEdge/projects/FactoryDevice/views/DeviceMonitor.json`
4. Rename to **DeviceMonitor** if needed
5. Click **Import**

#### Step 4: Set as Default View
1. In Project Browser, expand **Perspective**
2. Double-click **perspective-session.json**
3. Under **props → primary → defaultViewId**, enter: **DeviceMonitor**
4. Save the project

#### Step 5: Add Gateway Script (Device Simulator)
1. In Gateway web interface, go to **Config → Scripting → Gateway Event Scripts**
2. Click **Add New Script**
3. Select **Timer** event type
4. Set **Fixed Rate** to **1000** milliseconds (1 second)
5. Copy content from `gateway-scripts/device-simulator.py`
6. Paste into script editor
7. Enable the script
8. Click **Save**

#### Step 6: Configure MQTT (Optional)
1. Install MQTT Transmission module if not already installed
2. Go to **Config → MQTT Transmission → Transmitters**
3. Click **Create new MQTT Transmitter**
4. Use settings from `mqtt-config.json`:
   - Name: **Factory Device MQTT**
   - Server URL: **tcp://localhost:1883**
   - Client ID: **ignition-factory-device**
5. Go to **Settings → Tag Groups**
6. Add tag group:
   - Name: **DevicePosition**
   - Tag paths: All device tags
   - Topic: **unreal/factory/{tagName}**
7. Click **Save Changes**

### Method 2: Quick Copy (For Docker Setup)

If using Docker Compose:

```bash
# Copy project files to Ignition volume
docker cp HMI/IgnitionEdge/projects/FactoryDevice \
  virtplc-ignition-edge:/usr/local/bin/ignition/data/projects/

docker cp HMI/IgnitionEdge/tags/device_tags.json \
  virtplc-ignition-edge:/usr/local/bin/ignition/data/tags/

# Restart Ignition to pick up changes
docker restart virtplc-ignition-edge
```

Then complete Steps 4-6 from Method 1.

## Testing the Setup

### 1. Verify Tags
1. In Designer Tag Browser, expand **[default] → Factory Device**
2. You should see all 8 tags
3. Watch **Device_X_Position** and **Device_Y_Position** - they should update every second
4. Values should change in a circular pattern (0-100 range)

### 2. Test HMI View
1. In Designer, select **DeviceMonitor** view
2. Click **Preview Mode** (play button)
3. You should see:
   - Device status updating
   - X/Y positions changing
   - Blue dot moving in circular pattern on chart
   - Distance from origin calculated
   - Speed displayed

### 3. Test MQTT Publishing
If you configured MQTT:

```bash
# Subscribe to device topics
mosquitto_sub -h localhost -t "unreal/factory/#" -v

# You should see messages like:
# unreal/factory/Device_X_Position {"tagName":"Device_X_Position","value":75.32,"quality":"GOOD","timestamp":"2025-12-05T10:00:00Z","deviceId":1}
# unreal/factory/Device_Y_Position {"tagName":"Device_Y_Position","value":50.15,"quality":"GOOD","timestamp":"2025-12-05T10:00:00Z","deviceId":1}
```

### 4. Access the HMI
1. Open web browser
2. Navigate to: `http://localhost:8088/data/perspective/client/Factory_Device_Monitor`
3. Login with Ignition credentials
4. You should see the live device monitor

## Customization

### Change Device Movement Pattern

Edit the gateway script to modify behavior:

```python
# Linear motion instead of circular
x_pos = (state['counter'] % 100)
y_pos = 50.0

# Random motion
import random
x_pos = random.uniform(0, 100)
y_pos = random.uniform(0, 100)

# Follow a path
path = [(10,10), (90,10), (90,90), (10,90)]
point_index = (state['counter'] // 100) % len(path)
x_pos, y_pos = path[point_index]
```

### Add More Tags

In Designer:
1. Right-click **Factory Device** folder
2. Select **New Tag → Memory Tag**
3. Configure datatype and properties
4. Add to MQTT transmitter if needed

Example new tags:
- **Temperature** - Device temperature
- **Pressure** - System pressure
- **Power_Consumption** - Power usage
- **Error_Code** - Last error code

### Modify HMI Layout

In Designer:
1. Open **DeviceMonitor** view
2. Drag components from Component Palette
3. Bind properties to tags using **Binding** icon
4. Customize colors, sizes, fonts in **Props** panel

### Connect to Real PLC

Instead of using the simulator:

1. **Disable Gateway Script** (in Config → Scripting)
2. **Add OPC UA Device Connection**:
   - Config → OPC UA → Connections
   - Add new connection to your PLC
3. **Change Tag Source**:
   - Edit each tag
   - Change **Value Source** from `memory` to `opc`
   - Set **OPC Server** and **OPC Item Path**

Example for real PLC:
```
Tag: Device_X_Position
Value Source: OPC
OPC Server: Siemens_S7
OPC Item Path: ns=2;s=PLC.Position.X
```

## Integration with VirtPLC Stack

### Stage2/Production Setup

Once Node-RED is running on the PLC:

1. **Configure MQTT Broker** in Ignition:
   ```
   Server URL: tcp://<PLC_IP>:1883
   ```

2. **Node-RED receives** the MQTT messages automatically (see `nodered/flows/mqtt-opcua-bridge.json`)

3. **Collector reads** OPC-UA from Node-RED:
   ```
   opc.tcp://<PLC_IP>:4840/
   ```

4. **Data flows** to TimescaleDB for storage and AI analysis

### Data Flow Diagram
```
Ignition Edge → MQTT → Node-RED → OPC-UA → Collector → TimescaleDB
(Device Tags)    1883   (Bridge)   4840     (Go)        5432
```

## Troubleshooting

### Tags Not Updating
- Check Gateway Script is **enabled** and **no errors** in Gateway logs
- Verify script execution interval (should be 1000ms)
- Check tag paths are correct: `[default]Factory Device/...`

### HMI View Not Showing Data
- Verify tag bindings in view components
- Check browser console for errors (F12)
- Ensure tags have quality = GOOD

### MQTT Not Publishing
- Check MQTT Transmission module is installed
- Verify broker is running: `docker ps | grep mqtt`
- Test broker connectivity: `mosquitto_pub -h localhost -t test -m "hello"`
- Check transmitter status in Gateway web interface

### Circular Motion Not Working
- Verify Python math library is available
- Check for errors in Gateway → Status → Diagnostics → Logs
- Restart Gateway if needed

## Performance Tips

- **Update Rate**: Default 1000ms is good for visualization. Increase for higher performance.
- **History**: Enable Tag History for trending (requires SQL Bridge module)
- **Alarms**: Adjust alarm thresholds in tag configuration as needed
- **MQTT QoS**: Use QoS 0 for high-frequency data, QoS 1 for reliability

## Next Steps

1. **Add more devices**: Copy tag structure for Device 2, Device 3, etc.
2. **Create trends**: Add time-series charts for historical data
3. **Set up alarms**: Configure email notifications for out-of-bounds conditions
4. **Build dashboards**: Create overview screen with multiple devices
5. **Connect real hardware**: Replace simulator with actual PLC tags

## Support

- **Ignition Documentation**: https://docs.inductiveautomation.com/
- **VirtPLC Docs**: `/docs` directory
- **Tag Structure**: See `device_tags.json` for complete schema
- **MQTT Format**: See `mqtt-config.json` for message structure

---

**Version**: 1.0  
**Last Updated**: December 5, 2025  
**Compatible With**: Ignition Edge 8.1+, VirtPLC Stage2/Production profiles
