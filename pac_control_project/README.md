# VirtPLC PAC Control Project - Conveyor & Assembler Control

## Files
- `virtplc_project.groov` - Main PAC Control project file (open this in PAC Control)
- `virtplc_strategy.csv` - Strategy export/import file
- `variables.txt` - Variable definitions for import

## Quick Start

### 1. Install PAC Control
- Download and install PAC Control from Opto 22 website
- Ensure you have a valid license

### 2. Open the Project
1. Launch PAC Control
2. File → Open Project
3. Navigate to `virtplc_project.groov`
4. Open the file

### 3. Import Variables (if needed)
1. In PAC Control: Tools → Import Variables
2. Select `variables.txt`
3. Import all variables

### 4. Configure I/O
The project uses these variable mappings:
- **Inputs (from HMI/Node-RED):**
  - Conv1_Run_Command (Boolean) - Conveyor 1 ON/OFF
  - Conv2_Run_Command (Boolean) - Conveyor 2 ON/OFF
  - Assembler_Run_Command (Boolean) - Assembler ON/OFF
  - Conv1_RPM_Sensor (Integer) - Conveyor 1 speed input
  - Conv2_RPM_Sensor (Integer) - Conveyor 2 speed input
  - Assembler_X_Sensor (Integer) - Assembler X position
  - Assembler_Y_Sensor (Integer) - Assembler Y position

- **Outputs (to HMI/Node-RED):**
  - Conv1_RPM_Output (Integer) - Conveyor 1 speed output
  - Conv2_RPM_Output (Integer) - Conveyor 2 speed output
  - Assembler_X_Output (Integer) - Assembler X output
  - Assembler_Y_Output (Integer) - Assembler Y output

### 5. Build and Download
1. Build → Build Strategy
2. If successful: Controller → Download Strategy
3. Select your Groov PLC and download

## Logic Description

The strategy implements simple ON/OFF control:

- **Conveyor 1:** When `Conv1_Run_Command` is ON, output = sensor input, else output = 0
- **Conveyor 2:** When `Conv2_Run_Command` is ON, output = sensor input, else output = 0
- **Assembler:** When `Assembler_Run_Command` is ON, X/Y outputs = sensor inputs, else outputs = 0

## Ignition Edge Integration

### 1. Add Modbus Device
- Device Type: Modbus TCP
- Host: [Your PLC IP Address]
- Port: 502 (default)
- Slave ID: 1

### 2. Create Tags
Create these tags in Ignition:

| Tag Name | Data Type | Modbus Address | Description |
|----------|-----------|----------------|-------------|
| Conv1_Run_Command | Boolean | 00001 | Conveyor 1 ON/OFF command |
| Conv2_Run_Command | Boolean | 00002 | Conveyor 2 ON/OFF command |
| Assembler_Run_Command | Boolean | 00003 | Assembler ON/OFF command |
| Conv1_RPM_Sensor | Integer | 30001 | Conveyor 1 RPM sensor |
| Conv2_RPM_Sensor | Integer | 30002 | Conveyor 2 RPM sensor |
| Assembler_X_Sensor | Integer | 30003 | Assembler X sensor |
| Assembler_Y_Sensor | Integer | 30004 | Assembler Y sensor |
| Conv1_RPM_Output | Integer | 40001 | Conveyor 1 RPM output |
| Conv2_RPM_Output | Integer | 40002 | Conveyor 2 RPM output |
| Assembler_X_Output | Integer | 40003 | Assembler X output |
| Assembler_Y_Output | Integer | 40004 | Assembler Y output |

### 3. Create HMI
- Add toggle buttons for the 3 command tags
- Add numeric displays for the output tags
- Bind buttons to write to command tags
- Bind displays to read output tags

## Node-RED Integration

### 1. Install Modbus Nodes
```bash
cd ~/.node-red
npm install node-red-contrib-modbus
```

### 2. Add Modbus Client
- Server: [Your PLC IP Address]
- Port: 502
- Unit ID: 1

### 3. Create Flow
- **Read coils** (commands): FC1, address 00001-00003
- **Read registers** (sensors): FC3, address 30001-30004
- **Write coils** (commands): FC5, address 00001-00003
- **Write registers** (outputs): FC6, address 40001-40004

### 4. Connect to Unreal Engine
Send the output register values to Unreal Engine via MQTT/WebSocket

## Testing

1. **PAC Control Test:**
   - Set input variables manually
   - Verify outputs change correctly

2. **Ignition Test:**
   - Toggle HMI buttons
   - Verify PLC variables update

3. **Node-RED Test:**
   - Send test values to PLC
   - Verify Unreal receives correct data

## Troubleshooting

- **Build Errors:** Check variable names match exactly
- **Download Errors:** Ensure PLC is connected and powered
- **Communication Issues:** Verify IP addresses and Modbus settings
- **HMI Not Updating:** Check tag bindings and Modbus addresses

## Support

This project provides basic ON/OFF control for conveyor belts and assembler. Modify the strategy logic as needed for your specific requirements.