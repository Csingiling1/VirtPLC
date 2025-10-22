# HMI Design Specification

## Overview

The VirtPLC HMI provides real-time monitoring and control of factory equipment through an intuitive web-based interface built with Ignition Perspective.

## Design Philosophy

- **Clean and Simple**: Minimal clutter, focus on essential information
- **Real-time Feedback**: Immediate visual response to state changes
- **Mobile-Friendly**: Responsive design for tablets and mobile devices
- **Role-Based**: Different views for operators, technicians, and managers

## Page Structure

### 1. Overview Dashboard (Home)

**Purpose**: High-level factory status at a glance

**Layout**:
```
+------------------+------------------+
|   Header Bar                        |
+------------------+------------------+
| Equipment Status | Live Metrics     |
| - Motor 1: OK    | Speed: 1500 RPM |
| - Motor 2: OK    | Temp: 45°C      |
| - Conveyor: RUN  | Items: 12       |
+------------------+------------------+
| Alarm Summary    | Quick Controls   |
| 0 Critical       | [EMERGENCY STOP] |
| 2 Warnings       | [System Reset]   |
+------------------+------------------+
```

**Components**:
- Equipment status indicators (color-coded)
- Key performance metrics (real-time)
- Active alarm count
- Emergency controls

### 2. Motor Control Page

**Purpose**: Detailed monitoring and control of motors

**Layout**:
```
+------------------------------------------+
| Motor 1                    Motor 2       |
|------------------------+-----------------|
| Speed: [======   ] 1500| Speed: [ ====  ]|
| Target: [1500] RPM     | Target: [1200] |
|                        |                 |
| Temperature: 45.2°C    | Temperature: 42.1|
| [Warning Threshold]    | [Normal]        |
|                        |                 |
| Status: RUNNING        | Status: RUNNING |
| [STOP] [RESET]         | [STOP] [RESET]  |
|                        |                 |
| Trend Chart (5 min):   | Trend Chart:    |
| [Speed & Temp Graph]   | [Speed & Temp]  |
+------------------------------------------+
```

**Components**:
- **Gauges**: RPM, Temperature (analog and digital display)
- **Sliders**: Speed setpoint control
- **Buttons**: Start, Stop, Reset
- **Status Indicators**: Running, Stopped, Fault
- **Trend Charts**: Historical speed and temperature

**Controls**:
- Click gauge to see detailed history
- Drag slider to change target speed
- Buttons require confirmation for safety

### 3. Conveyor System Page

**Purpose**: Monitor and control conveyor belt

**Layout**:
```
+------------------------------------------+
| Conveyor 1                               |
+------------------------------------------+
| Speed: 25 m/min     [=====  ] 0-50      |
| Status: RUNNING                          |
|                                          |
| Item Count: 12 items on belt            |
| Proximity Sensor: [DETECTED]            |
|                                          |
| Controls:                                |
| [START] [STOP] [EMERGENCY STOP]         |
|                                          |
| Animation: [Moving belt visual]         |
|                                          |
| History:                                 |
| [Chart: Items/hour, Speed over time]    |
+------------------------------------------+
```

**Components**:
- Belt speed indicator
- Item counter
- Sensor status indicators
- Animated conveyor visualization
- Control buttons
- Historical throughput chart

### 4. Sensor Dashboard

**Purpose**: Monitor all sensor data

**Layout**:
```
+------------------+------------------+
| Proximity Sensors| Temperature Sens.|
|                  |                  |
| Sensor 1: YES    | Sensor 2: 23.5°C |
| Distance: 45mm   | Humidity: 45%    |
|                  |                  |
| [LED Indicator]  | [Gauge Display]  |
+------------------+------------------+
| Trend Charts                        |
| [Combined sensor data over time]    |
+------------------+------------------+
```

### 5. Alarm & Events Page

**Purpose**: View and manage alarms

**Layout**:
```
+------------------------------------------+
| Active Alarms                            |
+------------------------------------------+
| Priority | Equipment | Alarm      | Time|
| CRITICAL | Motor1    | Overheat   |10:23|
| WARNING  | Conv1     | Low Speed  |10:20|
+------------------------------------------+
| [ACK] [CLEAR] [DETAILS]                  |
+------------------------------------------+
| Alarm History (Last 24h)                 |
| [Filterable table with all alarms]       |
+------------------------------------------+
```

## Component Library

### Custom Components

#### Motor Status Indicator
- Green circle: Running normally
- Yellow circle: Warning (temp high, speed deviation)
- Red circle: Fault/Stopped
- Gray circle: Offline/Disabled
- Animated spin when running

#### Speed Gauge
- Circular gauge 0-2500 RPM
- Color zones:
  - Green: 0-1800 RPM (normal)
  - Yellow: 1800-2200 RPM (high)
  - Red: 2200+ RPM (critical)
- Digital readout in center

#### Temperature Display
- Thermometer visual
- Color-coded background:
  - Blue: < 40°C
  - Green: 40-60°C
  - Orange: 60-75°C
  - Red: > 75°C

#### Control Button
- Large touch-friendly buttons
- Icons + text labels
- Confirmation dialog for critical actions
- Disabled state when action not available

### Standard Components Used

- **Flex Container**: Responsive layouts
- **Power Chart**: Historical trending
- **Label**: Text display with dynamic binding
- **LED Display**: Binary status indicators
- **Numeric Entry**: Setpoint input
- **Button**: Actions and commands
- **Table**: Alarm and event lists
- **Perspective Icon**: Equipment symbols

## Color Scheme

**Primary Colors**:
- Background: `#1a1a2e` (Dark blue-gray)
- Surface: `#16213e` (Slightly lighter)
- Primary: `#0f3460` (Deep blue)
- Accent: `#e94560` (Red for alerts)

**Status Colors**:
- Normal/Good: `#4caf50` (Green)
- Warning: `#ff9800` (Orange)
- Critical/Error: `#f44336` (Red)
- Offline/Disabled: `#9e9e9e` (Gray)

**Text**:
- Primary text: `#ffffff` (White)
- Secondary text: `#b0b0b0` (Light gray)

## Tag Bindings

### Motor 1 Components

| Component | Property | Tag Binding |
|-----------|----------|-------------|
| Speed Gauge | value | `[default]Motor1/Speed` |
| Speed Gauge | max | `[default]Motor1/MaxSpeed` |
| Temp Display | value | `[default]Motor1/Temp` |
| Status Indicator | value | `[default]Motor1/Run` |
| Start Button | enabled | `!{[default]Motor1/Run}` |
| Stop Button | enabled | `{[default]Motor1/Run}` |

### Button Actions

#### Start Button (Motor 1)
```python
# Tag write on click
system.tag.writeBlocking(["[default]Motor1/Run"], [True])
```

#### Stop Button (Motor 1)
```python
# Tag write with confirmation
result = system.perspective.confirm("Stop Motor 1?", "Are you sure?")
if result:
    system.tag.writeBlocking(["[default]Motor1/Run"], [False])
```

#### Speed Setpoint Slider
```python
# On value change
tag_path = "[default]Motor1/TargetSpeed"
system.tag.writeBlocking([tag_path], [self.props.value])
```

## Navigation

### Header Bar
- Logo/Title (left)
- Page navigation (center)
  - Overview
  - Motors
  - Conveyor
  - Sensors
  - Alarms
- User info and logout (right)

### Breadcrumb
- Shows current location
- Clickable navigation history

## Responsive Breakpoints

- **Desktop**: > 1200px (full layout)
- **Tablet**: 768-1200px (2-column layout)
- **Mobile**: < 768px (single column, stacked)

## Security & Permissions

### Roles

**Operator**:
- View all dashboards
- Control start/stop
- Acknowledge alarms
- Cannot change setpoints > 20%

**Technician**:
- All operator permissions
- Change setpoints fully
- Reset faults
- View diagnostic data

**Manager**:
- All technician permissions
- Configure alarms
- View reports
- User management

### Implementation
- Use Perspective security zones
- Bind button visibility to user roles
- Log all control actions with user ID

## Performance Considerations

1. **Update Rates**:
   - Critical data (motor speed): 500ms
   - Temperature: 1000ms
   - Status indicators: 250ms
   - Charts: 5 second history buffer

2. **Optimize**:
   - Use tag change scripts, not polling
   - Limit historical data query range
   - Implement lazy loading for charts
   - Cache static configuration

3. **Testing**:
   - Test on tablet devices
   - Verify touch interactions
   - Check network latency impact
   - Load test with multiple users

## Future Enhancements

- AR view integration with camera feed
- Mobile push notifications for critical alarms
- Voice control integration
- Predictive maintenance indicators
- Energy consumption tracking
- 3D equipment visualization (embedded Unreal view)
