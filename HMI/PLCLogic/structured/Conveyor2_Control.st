PROGRAM Conveyor2_Control
VAR
    (* Modbus Inputs - Read from Ignition Edge *)
    Conv2_Command_Run AT %IX0.1: BOOL;      (* Coil 00002 - Command from Ignition *)
    
    (* Modbus Inputs - Read real sensor data from Node-RED *)
    Conv2_RPM_Sensor AT %IW1: INT;          (* Register 30002 - Real RPM from Node-RED *)
    
    (* Modbus Outputs - Write to Ignition Edge *)
    Conv2_Running AT %QX0.1: BOOL;          (* Coil 00002 - Running status *)
    Conv2_RPM AT %QW1: INT;                 (* Register 40002 - RPM value *)
    
    (* Internal variables *)
    Conv2_RunningInternal: BOOL := FALSE;
    Conv2_RPM_Value: INT := 0;
    Conv2_Prev_Command: BOOL := FALSE;
    Conv2_Command_Changed: BOOL := FALSE;
END_VAR

(* ==================================== *)
(* SIMPLE ON/OFF CONTROL                *)
(* ==================================== *)

(* Detect command change from Ignition *)
Conv2_Command_Changed := Conv2_Command_Run AND NOT Conv2_Prev_Command;
Conv2_Prev_Command := Conv2_Command_Run;

(* Set running state based on Ignition command *)
Conv2_RunningInternal := Conv2_Command_Run;

(* Use real sensor RPM value when running, 0 when stopped *)
IF Conv2_RunningInternal THEN
    Conv2_RPM_Value := Conv2_RPM_Sensor;  (* Real RPM from Node-RED *)
ELSE
    Conv2_RPM_Value := 0;                  (* 0 RPM when stopped *)
END_IF

(* Write outputs to Modbus registers *)
Conv2_Running := Conv2_RunningInternal;
Conv2_RPM := Conv2_RPM_Value;

END_PROGRAM
VAR
    (* Input signals *)
    Conv2_Start: BOOL;              (* Start button *)
    Conv2_Stop: BOOL;               (* Stop button *)
    E_Stop: BOOL;                   (* Emergency stop *)
    Conv2_Sensor_Entry: BOOL;       (* Entry sensor - item entering conveyor *)
    Conv2_Sensor_Exit: BOOL;        (* Exit sensor - item leaving conveyor *)
    Conv2_Photoeye: BOOL;           (* Presence detection *)
    
    (* Output signals *)
    Conv2_Running: BOOL;            (* Conveyor motor running *)
    Conv2_Speed: REAL := 0.0;       (* Current speed (m/min) *)
    Conv2_ItemCount: INT := 0;      (* Total items processed *)
    Conv2_ItemsOnBelt: INT := 0;    (* Items currently on belt *)
    Conv2_Emergency: BOOL;          (* Emergency condition *)
    Conv2_Fault: BOOL;              (* Fault condition *)
    Conv2_Status: INT := 0;         (* Status: 0=Stopped, 1=Starting, 2=Running, 3=Stopping, 4=Fault *)
    
    (* Configuration *)
    Conv2_TargetSpeed: REAL := 45.0;    (* Target speed (m/min) *)
    Conv2_MaxSpeed: REAL := 70.0;       (* Maximum allowed speed *)
    Conv2_MinSpeed: REAL := 10.0;       (* Minimum running speed *)
    Conv2_RampRate: REAL := 2.0;        (* Speed ramp rate *)
    Conv2_MaxItems: INT := 8;           (* Maximum items on belt *)
    
    (* Internal variables *)
    Conv2_StartInternal: BOOL;
    Conv2_EntryPrev: BOOL := FALSE;
    Conv2_ExitPrev: BOOL := FALSE;
    Conv2_EntryEdge: BOOL;
    Conv2_ExitEdge: BOOL;
    Conv2_Timer: TIME;
    Conv2_RunTime: TIME;
    
    (* MQTT/Communication tags *)
    Conv2_MQTT_Topic: STRING := 'plc/conveyor2';
    Conv2_LastUpdate: TIME;
END_VAR

(* ==================================== *)
(* MAIN CONTROL LOGIC                   *)
(* ==================================== *)

(* Status State Machine *)
CASE Conv2_Status OF
    0: (* STOPPED *)
        Conv2_Running := FALSE;
        Conv2_Speed := 0.0;
        IF Conv2_StartInternal THEN
            Conv2_Status := 1; (* STARTING *)
        END_IF;
    
    1: (* STARTING *)
        Conv2_Running := TRUE;
        IF Conv2_Speed >= Conv2_MinSpeed THEN
            Conv2_Status := 2; (* RUNNING *)
        END_IF;
    
    2: (* RUNNING *)
        Conv2_Running := TRUE;
        IF Conv2_Stop OR E_Stop OR Conv2_Emergency OR Conv2_Fault THEN
            Conv2_Status := 3; (* STOPPING *)
        END_IF;
    
    3: (* STOPPING *)
        Conv2_Running := FALSE;
        IF Conv2_Speed <= 0.0 THEN
            Conv2_Status := 0; (* STOPPED *)
        END_IF;
    
    4: (* FAULT *)
        Conv2_Running := FALSE;
        Conv2_Speed := 0.0;
END_CASE;

(* Start Logic *)
Conv2_StartInternal := Conv2_Start AND NOT E_Stop AND NOT Conv2_Emergency AND NOT Conv2_Fault;

(* Emergency Stop Override *)
IF E_Stop OR Conv2_Emergency THEN
    Conv2_Running := FALSE;
    Conv2_Status := 3; (* STOPPING *)
END_IF;

(* Speed Control with Ramping *)
IF Conv2_Running THEN
    IF Conv2_Speed < Conv2_TargetSpeed THEN
        Conv2_Speed := Conv2_Speed + Conv2_RampRate;
        IF Conv2_Speed > Conv2_TargetSpeed THEN
            Conv2_Speed := Conv2_TargetSpeed;
        END_IF;
    ELSIF Conv2_Speed > Conv2_TargetSpeed THEN
        Conv2_Speed := Conv2_Speed - Conv2_RampRate;
        IF Conv2_Speed < Conv2_TargetSpeed THEN
            Conv2_Speed := Conv2_TargetSpeed;
        END_IF;
    END_IF;
    
    (* Overspeed protection *)
    IF Conv2_Speed > Conv2_MaxSpeed THEN
        Conv2_Fault := TRUE;
        Conv2_Status := 4; (* FAULT *)
    END_IF;
ELSE
    IF Conv2_Speed > 0.0 THEN
        Conv2_Speed := Conv2_Speed - (Conv2_RampRate * 2.0);
        IF Conv2_Speed < 0.0 THEN
            Conv2_Speed := 0.0;
        END_IF;
    END_IF;
END_IF;

(* Item Counting - Entry Sensor *)
Conv2_EntryEdge := Conv2_Sensor_Entry AND NOT Conv2_EntryPrev;
IF Conv2_EntryEdge THEN
    Conv2_ItemsOnBelt := Conv2_ItemsOnBelt + 1;
    Conv2_ItemCount := Conv2_ItemCount + 1;
    
    IF Conv2_ItemsOnBelt > Conv2_MaxItems THEN
        Conv2_Fault := TRUE;
        Conv2_Status := 4;
    END_IF;
END_IF;
Conv2_EntryPrev := Conv2_Sensor_Entry;

(* Item Counting - Exit Sensor *)
Conv2_ExitEdge := Conv2_Sensor_Exit AND NOT Conv2_ExitPrev;
IF Conv2_ExitEdge THEN
    Conv2_ItemsOnBelt := Conv2_ItemsOnBelt - 1;
    IF Conv2_ItemsOnBelt < 0 THEN
        Conv2_ItemsOnBelt := 0;
    END_IF;
END_IF;
Conv2_ExitPrev := Conv2_Sensor_Exit;

(* Runtime Counter *)
IF Conv2_Running THEN
    Conv2_RunTime := Conv2_RunTime + T#100MS;
END_IF;

END_PROGRAM
