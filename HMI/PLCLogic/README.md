# PLC Control Logic

This directory contains PLC control logic for the VirtPLC system.

## Current Implementation - Simple ON/OFF Control with Real Sensor Data

### **PLC Programs (Structured Text)**

1. **`Conveyor1_Control_v2.st`** - Simple ON/OFF control
   - Reads running command from Ignition (Coil 00001)
   - Reads real RPM from Node-RED (Register 30001)
   - Outputs RPM to Ignition (Register 40001, 0 when stopped)

2. **`Conveyor2_Control.st`** - Simple ON/OFF control
   - Reads running command from Ignition (Coil 00002)
   - Reads real RPM from Node-RED (Register 30002)
   - Outputs RPM to Ignition (Register 40002, 0 when stopped)

3. **`ComponentAssembler_Control.st`** - Simple ON/OFF control
   - Reads running command from Ignition (Coil 00003)
   - Reads real position/status from Node-RED (Registers 30003-30004, Coils 00004-00005)
   - Outputs position/status to Ignition (Registers 40003-40004)

### **Modbus Register Map**

#### **Input Registers (3xxxx) - PLC Reads Real Data from Node-RED**
| Address | Type | Device | Data | Source |
|---------|------|--------|------|--------|
| **30001** | Input Reg | Conv1 | Real RPM from simulator | Node-RED writes |
| **30002** | Input Reg | Conv2 | Real RPM from simulator | Node-RED writes |
| **30003** | Input Reg | Machine1 | Real X position | Node-RED writes |
| **30004** | Input Reg | Machine1 | Real Y position | Node-RED writes |

#### **Coils (0xxxx) - PLC Reads Commands & Status**
| Address | Type | Device | Data | Direction |
|---------|------|--------|------|-----------|
| **00001** | Coil (Read/Write) | Conv1 | Running command & status | Ignition ↔ PLC |
| **00002** | Coil (Read/Write) | Conv2 | Running command & status | Ignition ↔ PLC |
| **00003** | Coil (Read/Write) | Machine1 | Running command & status | Ignition ↔ PLC |
| **00004** | Coil (Read) | Machine1 | Real ready status | Node-RED writes |
| **00005** | Coil (Read) | Machine1 | Real done status | Node-RED writes |

#### **Holding Registers (4xxxx) - PLC Writes to Ignition**
| Address | Type | Device | Data | Direction |
|---------|------|--------|------|-----------|
| **40001** | Holding Reg | Conv1 | RPM value (0 when stopped) | PLC → Ignition |
| **40002** | Holding Reg | Conv2 | RPM value (0 when stopped) | PLC → Ignition |
| **40003** | Holding Reg | Machine1 | X position | PLC → Ignition |
| **40004** | Holding Reg | Machine1 | Y position | PLC → Ignition |

### **Data Flow**

```
Simulator → MQTT → Node-RED → Modbus TCP → PLC (Input Registers)
Ignition HMI → Modbus TCP → PLC (Coil Commands)
PLC → Modbus TCP → Ignition (Holding Registers)
Ignition → MQTT → Node-RED → Unreal Engine
```

**Real-time synchronization:**
- PLC gets real sensor data from Node-RED via Modbus input registers
- PLC controls ON/OFF state based on Ignition commands
- PLC outputs processed data (RPM=0 when stopped) to Ignition
- Node-RED forwards commands to Unreal for visualization

### **Node-RED Integration**

Node-RED flow automatically:
1. Receives simulator data via MQTT (`plc/+` topics)
2. Maps sensor data to Modbus registers:
   - `motor_speed` → Input registers 30001/30002
   - `position_x/y` → Input registers 30003/30004
   - `is_ready/done` → Coils 00004/00005
3. Writes to PLC Modbus TCP server
4. Forwards Ignition commands to Unreal Engine

### **Testing**

```bash
# Test PLC reading real data
mbpoll -a 1 -r 30001 -c 4 -t 4 <PLC_IP>  # Read input registers

# Test PLC writing processed data  
mbpoll -a 1 -r 40001 -c 4 -t 4 <PLC_IP>  # Read holding registers

# Test coil commands
mbpoll -a 1 -r 1 -c 5 -t 0 <PLC_IP>      # Read coils
```

## Legacy Ladder Logic Programs

### Motor Control Logic

**Purpose**: Start/stop motor with safety interlocks

```
Program: Motor1_Control

Rung 1: Motor Start Logic
├─┤ Start_Button ├─┤ NOT Fault ├─┤ NOT E_Stop ├─( Motor1_Run )─
│
└─┤ Motor1_Run ├────────────────────────────┘ (Seal-in)

Rung 2: Motor Stop Logic  
├─┤ Stop_Button ├─( Reset Motor1_Run )─

Rung 3: Emergency Stop
├─┤ E_Stop ├─( Reset Motor1_Run )─

Rung 4: Speed Control
├─┤ Motor1_Run ├─[ MOV TargetSpeed → Motor1_Speed ]─

Rung 5: Overspeed Protection
├─┤ Motor1_Speed > 2200 ├─( Set Fault )─
├─────────────────────────┤ Reset Motor1_Run )─
```

### Conveyor Control Logic

```
Program: Conveyor1_Control

Rung 1: Start Conveyor
├─┤ Conv_Start ├─┤ Motor1_Run ├─┤ NOT E_Stop ├─( Conv1_Running )─
│
└─┤ Conv1_Running ├──────────────────────────┘ (Seal-in)

Rung 2: Stop Conveyor
├─┤ Conv_Stop ├─( Reset Conv1_Running )─

Rung 3: Emergency Stop  
├─┤ E_Stop ├─( Reset Conv1_Running )─

Rung 4: Item Counting
├─┤ Sensor1_Detected ├─┤ ONS ├─[ ADD Conv1_ItemCount, 1 ]─
```

## Structured Text Programs

### Motor Startup Sequence

```iecst
PROGRAM Motor_Startup
VAR
    StartCommand : BOOL;
    MotorReady : BOOL;
    Fault : BOOL;
    Step : INT := 0;
    Timer1 : TON;
END_VAR

(* Motor startup sequence with warm-up *)
CASE Step OF
    0: (* Idle state *)
        IF StartCommand AND NOT Fault THEN
            Step := 1;
        END_IF;
    
    1: (* Pre-start checks *)
        IF MotorReady AND Temperature < 80.0 THEN
            Step := 2;
        ELSIF Temperature >= 80.0 THEN
            Fault := TRUE;
            Step := 0;
        END_IF;
    
    2: (* Start motor at low speed *)
        TargetSpeed := 500.0;
        Motor1_Run := TRUE;
        Timer1(IN:=TRUE, PT:=T#5S);
        IF Timer1.Q THEN
            Step := 3;
            Timer1(IN:=FALSE);
        END_IF;
    
    3: (* Ramp to target speed *)
        IF CurrentSpeed > 400.0 THEN
            TargetSpeed := OperatorSetpoint;
            Step := 4;
        END_IF;
    
    4: (* Running *)
        IF NOT StartCommand OR Fault THEN
            Motor1_Run := FALSE;
            Step := 0;
        END_IF;
END_CASE;
END_PROGRAM
```

### Temperature Monitoring

```iecst
PROGRAM Temperature_Monitor
VAR
    MotorTemp : REAL;
    Warning : BOOL;
    Critical : BOOL;
    CooldownTimer : TON;
END_VAR

(* Monitor temperature and trigger actions *)
IF MotorTemp > 75.0 AND MotorTemp <= 85.0 THEN
    Warning := TRUE;
    (* Reduce speed by 10% *)
    TargetSpeed := TargetSpeed * 0.9;
ELSIF MotorTemp > 85.0 THEN
    Critical := TRUE;
    (* Emergency stop motor *)
    Motor1_Run := FALSE;
    (* Start cooldown timer *)
    CooldownTimer(IN:=TRUE, PT:=T#5M);
ELSE
    Warning := FALSE;
    Critical := FALSE;
END_IF;

(* Allow restart after cooldown *)
IF CooldownTimer.Q AND MotorTemp < 60.0 THEN
    Critical := FALSE;
    CooldownTimer(IN:=FALSE);
END_IF;
END_PROGRAM
```

### PID Speed Control

```iecst
PROGRAM Speed_Control
VAR
    PID_1 : PID;
    Setpoint : REAL;
    ProcessValue : REAL;
    Output : REAL;
    Kp : REAL := 1.5;
    Ki : REAL := 0.1;
    Kd : REAL := 0.05;
END_VAR

(* PID controller for motor speed *)
PID_1(
    SetPoint := Setpoint,
    ProcessValue := Motor1_Speed,
    Kp := Kp,
    Ki := Ki,
    Kd := Kd,
    Output => Output
);

(* Apply PID output to motor *)
Motor1_TargetSpeed := Output;

(* Clamp output to safe range *)
IF Motor1_TargetSpeed > 2500.0 THEN
    Motor1_TargetSpeed := 2500.0;
ELSIF Motor1_TargetSpeed < 0.0 THEN
    Motor1_TargetSpeed := 0.0;
END_IF;
END_PROGRAM
```

## Function Blocks

### Safety Interlock

```iecst
FUNCTION_BLOCK SafetyInterlock
VAR_INPUT
    EmergencyStop : BOOL;
    GuardClosed : BOOL;
    ResetButton : BOOL;
END_VAR
VAR_OUTPUT
    SafeToOperate : BOOL;
    FaultActive : BOOL;
END_VAR
VAR
    FaultLatch : BOOL;
END_VAR

(* Check safety conditions *)
IF EmergencyStop OR NOT GuardClosed THEN
    FaultLatch := TRUE;
    SafeToOperate := FALSE;
    FaultActive := TRUE;
END_IF;

(* Reset requires button press *)
IF ResetButton AND NOT EmergencyStop AND GuardClosed THEN
    FaultLatch := FALSE;
    FaultActive := FALSE;
END_IF;

(* Output safe to operate *)
SafeToOperate := NOT FaultLatch;
END_FUNCTION_BLOCK
```

## Integration with Ignition

These PLC programs can be simulated in Ignition using:

1. **Tag Event Scripts**: Implement logic in Python
2. **Gateway Timer Scripts**: Periodic execution
3. **Expression Tags**: Simple logic operations

### Example: Motor Control in Ignition

```python
# Tag: Motor1/Run
# Event: Value Changed

# Get current values
fault = system.tag.readBlocking(["[default]Motor1/Fault"])[0].value
eStop = system.tag.readBlocking(["[default]System/EmergencyStop"])[0].value

# Safety interlock
if fault or eStop:
    system.tag.writeBlocking(["[default]Motor1/Run"], [False])
    system.tag.writeBlocking(["[default]Motor1/TargetSpeed"], [0.0])
```

### Example: Temperature Monitor

```python
# Gateway Timer Script - runs every 1 second

# Read temperature
temp = system.tag.readBlocking(["[default]Motor1/Temp"])[0].value
running = system.tag.readBlocking(["[default]Motor1/Run"])[0].value

if running:
    if temp > 85.0:
        # Critical - stop motor
        system.tag.writeBlocking(["[default]Motor1/Run"], [False])
        system.perspective.sendMessage("alarm", {
            "message": "Motor 1 critical temperature!",
            "severity": "critical"
        })
    elif temp > 75.0:
        # Warning - reduce speed
        currentSpeed = system.tag.readBlocking(["[default]Motor1/TargetSpeed"])[0].value
        reducedSpeed = currentSpeed * 0.9
        system.tag.writeBlocking(["[default]Motor1/TargetSpeed"], [reducedSpeed])
```

## Testing

1. Import logic into PLC software or Ignition
2. Connect to OPC-UA test server
3. Verify interlocks work correctly
4. Test emergency stop functionality
5. Validate alarm conditions
6. Test startup/shutdown sequences

## Notes

- This logic is simplified for demonstration
- Production systems require more extensive safety logic
- Comply with relevant safety standards (IEC 61508, ISO 13849)
- Perform thorough HAZOP analysis
- Add comprehensive error handling
