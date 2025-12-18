PROGRAM Conveyor1_Control
VAR
    (* Modbus Inputs - Read from Ignition Edge *)
    Conv1_Command_Run AT %IX0.0: BOOL;      (* Coil 00001 - Command from Ignition *)
    
    (* Modbus Inputs - Read real sensor data from Node-RED *)
    Conv1_RPM_Sensor AT %IW0: INT;          (* Register 30001 - Real RPM from Node-RED *)
    
    (* Modbus Outputs - Write to Ignition Edge *)
    Conv1_Running AT %QX0.0: BOOL;          (* Coil 00001 - Running status *)
    Conv1_RPM AT %QW0: INT;                 (* Register 40001 - RPM value to Ignition *)
    
    (* Internal variables *)
    Conv1_RunningInternal: BOOL := FALSE;
    Conv1_RPM_Value: INT := 0;
    Conv1_Prev_Command: BOOL := FALSE;
    Conv1_Command_Changed: BOOL := FALSE;
END_VAR

(* ==================================== *)
(* SIMPLE ON/OFF CONTROL                *)
(* ==================================== *)

(* Detect command change from Ignition *)
Conv1_Command_Changed := Conv1_Command_Run AND NOT Conv1_Prev_Command;
Conv1_Prev_Command := Conv1_Command_Run;

(* Set running state based on Ignition command *)
Conv1_RunningInternal := Conv1_Command_Run;

(* Use real sensor RPM value when running, 0 when stopped *)
IF Conv1_RunningInternal THEN
    Conv1_RPM_Value := Conv1_RPM_Sensor;  (* Real RPM from Node-RED *)
ELSE
    Conv1_RPM_Value := 0;                  (* 0 RPM when stopped *)
END_IF

(* Write outputs to Modbus registers *)
Conv1_Running := Conv1_RunningInternal;
Conv1_RPM := Conv1_RPM_Value;
            Conv1_Status := 1; (* STARTING *)
        END_IF;
    
    1: (* STARTING *)
        Conv1_Running := TRUE;
        IF Conv1_Speed >= Conv1_MinSpeed THEN
            Conv1_Status := 2; (* RUNNING *)
        END_IF;
    
    2: (* RUNNING *)
        Conv1_Running := TRUE;
        IF Conv1_Stop OR E_Stop OR Conv1_Emergency OR Conv1_Fault THEN
            Conv1_Status := 3; (* STOPPING *)
        END_IF;
    
    3: (* STOPPING *)
        Conv1_Running := FALSE;
        IF Conv1_Speed <= 0.0 THEN
            Conv1_Status := 0; (* STOPPED *)
        END_IF;
    
    4: (* FAULT *)
        Conv1_Running := FALSE;
        Conv1_Speed := 0.0;
        (* Require manual reset *)
END_CASE;

(* Start Logic *)
Conv1_StartInternal := Conv1_Start AND NOT E_Stop AND NOT Conv1_Emergency AND NOT Conv1_Fault;

(* Emergency Stop Override *)
IF E_Stop OR Conv1_Emergency THEN
    Conv1_Running := FALSE;
    Conv1_Status := 3; (* STOPPING *)
END_IF;

(* Speed Control with Ramping *)
IF Conv1_Running THEN
    (* Ramp up to target speed *)
    IF Conv1_Speed < Conv1_TargetSpeed THEN
        Conv1_Speed := Conv1_Speed + Conv1_RampRate;
        IF Conv1_Speed > Conv1_TargetSpeed THEN
            Conv1_Speed := Conv1_TargetSpeed;
        END_IF;
    ELSIF Conv1_Speed > Conv1_TargetSpeed THEN
        Conv1_Speed := Conv1_Speed - Conv1_RampRate;
        IF Conv1_Speed < Conv1_TargetSpeed THEN
            Conv1_Speed := Conv1_TargetSpeed;
        END_IF;
    END_IF;
    
    (* Overspeed protection *)
    IF Conv1_Speed > Conv1_MaxSpeed THEN
        Conv1_Fault := TRUE;
        Conv1_Status := 4; (* FAULT *)
    END_IF;
ELSE
    (* Ramp down when stopped *)
    IF Conv1_Speed > 0.0 THEN
        Conv1_Speed := Conv1_Speed - (Conv1_RampRate * 2.0); (* Faster deceleration *)
        IF Conv1_Speed < 0.0 THEN
            Conv1_Speed := 0.0;
        END_IF;
    END_IF;
END_IF;

(* Item Counting - Entry Sensor Rising Edge *)
Conv1_EntryEdge := Conv1_Sensor_Entry AND NOT Conv1_EntryPrev;
IF Conv1_EntryEdge THEN
    Conv1_ItemsOnBelt := Conv1_ItemsOnBelt + 1;
    Conv1_ItemCount := Conv1_ItemCount + 1;
    
    (* Check for overload *)
    IF Conv1_ItemsOnBelt > Conv1_MaxItems THEN
        Conv1_Fault := TRUE;
        Conv1_Status := 4; (* FAULT - Overload *)
    END_IF;
END_IF;
Conv1_EntryPrev := Conv1_Sensor_Entry;

(* Item Counting - Exit Sensor Rising Edge *)
Conv1_ExitEdge := Conv1_Sensor_Exit AND NOT Conv1_ExitPrev;
IF Conv1_ExitEdge THEN
    Conv1_ItemsOnBelt := Conv1_ItemsOnBelt - 1;
    IF Conv1_ItemsOnBelt < 0 THEN
        Conv1_ItemsOnBelt := 0; (* Safety check *)
    END_IF;
END_IF;
Conv1_ExitPrev := Conv1_Sensor_Exit;

(* Runtime Counter *)
IF Conv1_Running THEN
    Conv1_RunTime := Conv1_RunTime + T#100MS; (* Update every scan *)
END_IF;

END_PROGRAM
