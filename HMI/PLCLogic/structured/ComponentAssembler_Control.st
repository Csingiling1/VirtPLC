PROGRAM ComponentAssembler_Control
VAR
    (* Modbus Inputs - Read from Ignition Edge *)
    Machine1_Command_Run AT %IX0.2: BOOL;   (* Coil 00003 - Command from Ignition *)
    
    (* Modbus Inputs - Read real sensor data from Node-RED *)
    Machine1_X_Sensor AT %IW2: INT;         (* Register 30003 - Real X position from Node-RED *)
    Machine1_Y_Sensor AT %IW3: INT;         (* Register 30004 - Real Y position from Node-RED *)
    Machine1_IsReady_Sensor AT %IX0.3: BOOL; (* Coil 00004 - Real ready status from Node-RED *)
    Machine1_IsDone_Sensor AT %IX0.4: BOOL; (* Coil 00005 - Real done status from Node-RED *)
    
    (* Modbus Outputs - Write to Ignition Edge *)
    Machine1_Running AT %QX0.2: BOOL;       (* Coil 00003 - Running status *)
    Machine1_IsReady AT %QX0.3: BOOL;       (* Coil 00004 - Ready status *)
    Machine1_IsDone AT %QX0.4: BOOL;        (* Coil 00005 - Done status *)
    Machine1_X AT %QW2: INT;                (* Register 40003 - X position *)
    Machine1_Y AT %QW3: INT;                (* Register 40004 - Y position *)
    
    (* Internal variables *)
    Machine1_RunningInternal: BOOL := FALSE;
    Machine1_X_Value: INT := 0;
    Machine1_Y_Value: INT := 0;
    Machine1_IsReady_Value: BOOL := FALSE;
    Machine1_IsDone_Value: BOOL := FALSE;
    Machine1_Prev_Command: BOOL := FALSE;
    Machine1_Command_Changed: BOOL := FALSE;
END_VAR

(* ==================================== *)
(* SIMPLE ON/OFF CONTROL                *)
(* ==================================== *)

(* Detect command change from Ignition *)
Machine1_Command_Changed := Machine1_Command_Run AND NOT Machine1_Prev_Command;
Machine1_Prev_Command := Machine1_Command_Run;

(* Set running state based on Ignition command *)
Machine1_RunningInternal := Machine1_Command_Run;

(* Use real sensor values from Node-RED *)
Machine1_X_Value := Machine1_X_Sensor;
Machine1_Y_Value := Machine1_Y_Sensor;
Machine1_IsReady_Value := Machine1_IsReady_Sensor;
Machine1_IsDone_Value := Machine1_IsDone_Sensor;

(* Write outputs to Modbus registers *)
Machine1_Running := Machine1_RunningInternal;
Machine1_IsReady := Machine1_IsReady_Value;
Machine1_IsDone := Machine1_IsDone_Value;
Machine1_X := Machine1_X_Value;
Machine1_Y := Machine1_Y_Value;

END_PROGRAM
VAR
    (* Input signals *)
    Assembler_Start: BOOL;          (* Start assembly process *)
    Assembler_Stop: BOOL;           (* Stop assembly process *)
    Assembler_Reset: BOOL;          (* Reset fault/counters *)
    E_Stop: BOOL;                   (* Emergency stop *)
    
    (* Station sensors *)
    Station1_PartPresent: BOOL;     (* Part present at station 1 *)
    Station2_PartPresent: BOOL;     (* Part present at station 2 *)
    Station3_PartPresent: BOOL;     (* Part present at assembly station *)
    
    (* Position sensors *)
    Gripper1_Extended: BOOL;        (* Gripper 1 fully extended *)
    Gripper1_Retracted: BOOL;       (* Gripper 1 fully retracted *)
    Gripper2_Extended: BOOL;        (* Gripper 2 fully extended *)
    Gripper2_Retracted: BOOL;       (* Gripper 2 fully retracted *)
    
    (* Process sensors *)
    Assembly_Complete: BOOL;        (* Assembly process complete sensor *)
    Quality_Check_OK: BOOL;         (* Quality inspection passed *)
    
    (* Output signals *)
    Assembler_Running: BOOL;        (* System running *)
    Assembler_Status: INT := 0;     (* 0=Idle, 1=Loading, 2=Assembling, 3=Unloading, 4=Fault *)
    Assembler_Fault: BOOL;          (* Fault condition *)
    Assembler_Emergency: BOOL;      (* Emergency condition *)
    
    (* Actuator outputs *)
    Gripper1_Extend: BOOL;          (* Extend gripper 1 *)
    Gripper1_Grab: BOOL;            (* Activate gripper 1 vacuum/clamp *)
    Gripper2_Extend: BOOL;          (* Extend gripper 2 *)
    Gripper2_Grab: BOOL;            (* Activate gripper 2 vacuum/clamp *)
    
    Assembly_Motor: BOOL;           (* Assembly motor/tool *)
    Assembly_Speed: REAL := 0.0;    (* Assembly speed (RPM) *)
    
    Reject_Gate: BOOL;              (* Activate reject gate for bad parts *)
    Accept_Gate: BOOL;              (* Activate accept gate for good parts *)
    
    (* Process counters *)
    Parts_Assembled: INT := 0;      (* Total parts assembled *)
    Parts_Rejected: INT := 0;       (* Total parts rejected *)
    Parts_InProcess: INT := 0;      (* Parts currently in assembly *)
    Cycle_Count: INT := 0;          (* Total cycles *)
    
    (* Timing *)
    Assembly_CycleTime: TIME;       (* Current cycle time *)
    Assembly_AvgCycleTime: TIME;    (* Average cycle time *)
    Step_Timer: TON;                (* Timer for step delays *)
    Timeout_Timer: TON;             (* Watchdog timer *)
    
    (* Configuration *)
    Assembly_TargetSpeed: REAL := 1500.0;  (* Target RPM *)
    Assembly_Duration: TIME := T#5S;       (* Assembly operation duration *)
    Gripper_Timeout: TIME := T#3S;         (* Max time for gripper operation *)
    Quality_Timeout: TIME := T#2S;         (* Max time for quality check *)
    
    (* State machine *)
    Current_Step: INT := 0;         (* Current step in sequence *)
    Step_Complete: BOOL;            (* Current step completed *)
    
    (* MQTT/Communication *)
    Assembler_MQTT_Topic: STRING := 'plc/assembler';
    Assembler_LastUpdate: TIME;
    
    (* Conveyor integration *)
    Conv1_ItemsOnBelt: INT;         (* From Conveyor 1 *)
    Conv2_ItemsOnBelt: INT;         (* From Conveyor 2 *)
    Request_Conv1_Part: BOOL;       (* Request part from Conv1 *)
    Request_Conv2_Part: BOOL;       (* Request part from Conv2 *)
END_VAR

(* ==================================== *)
(* MAIN STATE MACHINE                   *)
(* ==================================== *)

CASE Assembler_Status OF
    
    0: (* IDLE - Waiting for start *)
        Assembler_Running := FALSE;
        Current_Step := 0;
        
        (* Reset all outputs *)
        Gripper1_Extend := FALSE;
        Gripper1_Grab := FALSE;
        Gripper2_Extend := FALSE;
        Gripper2_Grab := FALSE;
        Assembly_Motor := FALSE;
        Assembly_Speed := 0.0;
        
        IF Assembler_Start AND NOT E_Stop AND NOT Assembler_Fault THEN
            Assembler_Status := 1; (* LOADING *)
            Assembler_Running := TRUE;
            Current_Step := 0;
        END_IF;
    
    1: (* LOADING - Pick parts from conveyors *)
        Assembler_Running := TRUE;
        
        CASE Current_Step OF
            0: (* Request parts from conveyors *)
                Request_Conv1_Part := TRUE;
                Request_Conv2_Part := TRUE;
                
                IF Station1_PartPresent AND Station2_PartPresent THEN
                    Current_Step := 1;
                END_IF;
            
            1: (* Pick part 1 with Gripper 1 *)
                Gripper1_Extend := TRUE;
                Step_Timer(IN := TRUE, PT := Gripper_Timeout);
                
                IF Gripper1_Extended THEN
                    Gripper1_Grab := TRUE;
                    Step_Timer(IN := FALSE);
                    Current_Step := 2;
                END_IF;
                
                IF Step_Timer.Q THEN
                    Assembler_Fault := TRUE;
                    Assembler_Status := 4; (* FAULT *)
                END_IF;
            
            2: (* Retract Gripper 1 *)
                Gripper1_Extend := FALSE;
                Step_Timer(IN := TRUE, PT := Gripper_Timeout);
                
                IF Gripper1_Retracted THEN
                    Step_Timer(IN := FALSE);
                    Current_Step := 3;
                END_IF;
                
                IF Step_Timer.Q THEN
                    Assembler_Fault := TRUE;
                    Assembler_Status := 4;
                END_IF;
            
            3: (* Pick part 2 with Gripper 2 *)
                Gripper2_Extend := TRUE;
                Step_Timer(IN := TRUE, PT := Gripper_Timeout);
                
                IF Gripper2_Extended THEN
                    Gripper2_Grab := TRUE;
                    Step_Timer(IN := FALSE);
                    Current_Step := 4;
                END_IF;
                
                IF Step_Timer.Q THEN
                    Assembler_Fault := TRUE;
                    Assembler_Status := 4;
                END_IF;
            
            4: (* Retract Gripper 2 *)
                Gripper2_Extend := FALSE;
                Step_Timer(IN := TRUE, PT := Gripper_Timeout);
                
                IF Gripper2_Retracted THEN
                    Step_Timer(IN := FALSE);
                    Parts_InProcess := 2;
                    Assembler_Status := 2; (* ASSEMBLING *)
                    Current_Step := 0;
                END_IF;
                
                IF Step_Timer.Q THEN
                    Assembler_Fault := TRUE;
                    Assembler_Status := 4;
                END_IF;
        END_CASE;
    
    2: (* ASSEMBLING - Perform assembly operation *)
        CASE Current_Step OF
            0: (* Position parts *)
                (* Move grippers to assembly position *)
                Gripper1_Extend := TRUE;
                Gripper2_Extend := TRUE;
                
                IF Gripper1_Extended AND Gripper2_Extended THEN
                    Current_Step := 1;
                END_IF;
            
            1: (* Start assembly motor *)
                Assembly_Motor := TRUE;
                Assembly_Speed := Assembly_TargetSpeed;
                Step_Timer(IN := TRUE, PT := Assembly_Duration);
                
                IF Step_Timer.Q THEN
                    Step_Timer(IN := FALSE);
                    Current_Step := 2;
                END_IF;
            
            2: (* Stop assembly motor *)
                Assembly_Motor := FALSE;
                Assembly_Speed := 0.0;
                
                IF Assembly_Complete THEN
                    Current_Step := 3;
                END_IF;
            
            3: (* Release grippers *)
                Gripper1_Grab := FALSE;
                Gripper2_Grab := FALSE;
                
                IF NOT Gripper1_Grab AND NOT Gripper2_Grab THEN
                    Current_Step := 4;
                END_IF;
            
            4: (* Retract grippers *)
                Gripper1_Extend := FALSE;
                Gripper2_Extend := FALSE;
                
                IF Gripper1_Retracted AND Gripper2_Retracted THEN
                    Parts_InProcess := 1;
                    Cycle_Count := Cycle_Count + 1;
                    Assembler_Status := 3; (* UNLOADING *)
                    Current_Step := 0;
                END_IF;
        END_CASE;
    
    3: (* UNLOADING - Quality check and eject *)
        CASE Current_Step OF
            0: (* Quality inspection *)
                Step_Timer(IN := TRUE, PT := Quality_Timeout);
                
                IF Quality_Check_OK THEN
                    Step_Timer(IN := FALSE);
                    Current_Step := 1;
                ELSIF Step_Timer.Q THEN
                    (* Timeout - reject part *)
                    Step_Timer(IN := FALSE);
                    Current_Step := 2;
                END_IF;
            
            1: (* Accept part *)
                Accept_Gate := TRUE;
                Parts_Assembled := Parts_Assembled + 1;
                Parts_InProcess := 0;
                
                Step_Timer(IN := TRUE, PT := T#1S);
                IF Step_Timer.Q THEN
                    Accept_Gate := FALSE;
                    Step_Timer(IN := FALSE);
                    Assembler_Status := 0; (* Return to IDLE *)
                    Current_Step := 0;
                END_IF;
            
            2: (* Reject part *)
                Reject_Gate := TRUE;
                Parts_Rejected := Parts_Rejected + 1;
                Parts_InProcess := 0;
                
                Step_Timer(IN := TRUE, PT := T#1S);
                IF Step_Timer.Q THEN
                    Reject_Gate := FALSE;
                    Step_Timer(IN := FALSE);
                    Assembler_Status := 0; (* Return to IDLE *)
                    Current_Step := 0;
                END_IF;
        END_CASE;
    
    4: (* FAULT - Error condition *)
        Assembler_Running := FALSE;
        Assembly_Motor := FALSE;
        Assembly_Speed := 0.0;
        
        (* Hold all grippers in current state until reset *)
        
        IF Assembler_Reset AND NOT Assembler_Start THEN
            Assembler_Fault := FALSE;
            Assembler_Status := 0; (* Return to IDLE *)
            Current_Step := 0;
            
            (* Release all grippers *)
            Gripper1_Grab := FALSE;
            Gripper2_Grab := FALSE;
            Gripper1_Extend := FALSE;
            Gripper2_Extend := FALSE;
        END_IF;
END_CASE;

(* Emergency Stop Override *)
IF E_Stop OR Assembler_Emergency THEN
    Assembler_Running := FALSE;
    Assembler_Fault := TRUE;
    Assembler_Status := 4;
    Assembly_Motor := FALSE;
    Assembly_Speed := 0.0;
END_IF;

(* Stop Button *)
IF Assembler_Stop THEN
    Assembler_Running := FALSE;
    Assembler_Status := 0;
END_IF;

END_PROGRAM
