PROGRAM Motor2_Control
VAR
    Start_Button: BOOL;
    Stop_Button: BOOL;
    E_Stop: BOOL;
    Motor2_Run: BOOL;
    Motor2_Speed: REAL;
    Motor2_Temp: REAL;
    Motor2_Fault: BOOL;
    TargetSpeed: REAL := 1800.0;
    
    (* Internal variables *)
    StartInternal: BOOL;
    StopInternal: BOOL;
    
    (* Constants *)
    MAX_SPEED: REAL := 2500.0;
    MAX_TEMP: REAL := 80.0;
END_VAR

(* Rung 1: Motor Start Logic with Seal-in *)
StartInternal := Start_Button AND NOT Motor2_Fault AND NOT E_Stop;
IF StartInternal OR (Motor2_Run AND NOT Stop_Button AND NOT E_Stop AND NOT Motor2_Fault) THEN
    Motor2_Run := TRUE;
END_IF;

(* Rung 2: Motor Stop Logic *)
IF Stop_Button OR E_Stop OR Motor2_Fault THEN
    Motor2_Run := FALSE;
    StopInternal := TRUE;
ELSE
    StopInternal := FALSE;
END_IF;

(* Rung 3: Speed Control *)
IF Motor2_Run THEN
    (* Ramp speed to target *)
    IF Motor2_Speed < TargetSpeed THEN
        Motor2_Speed := Motor2_Speed + 15.0; (* Slightly faster acceleration *)
    ELSIF Motor2_Speed > TargetSpeed THEN
        Motor2_Speed := Motor2_Speed - 15.0;
    END_IF;
ELSE
    (* Motor stopped - ramp down *)
    IF Motor2_Speed > 0 THEN
        Motor2_Speed := Motor2_Speed - 25.0;
        IF Motor2_Speed < 0 THEN
            Motor2_Speed := 0;
        END_IF;
    END_IF;
END_IF;

(* Rung 4: Temperature Simulation *)
IF Motor2_Run THEN
    Motor2_Temp := 25.0 + (Motor2_Speed / MAX_SPEED) * 45.0;
ELSE
    IF Motor2_Temp > 25.0 THEN
        Motor2_Temp := Motor2_Temp - 0.7; (* Faster cooling *)
    END_IF;
END_IF;

(* Rung 5: Protection *)
IF Motor2_Speed > MAX_SPEED OR Motor2_Temp > MAX_TEMP THEN
    Motor2_Fault := TRUE;
    Motor2_Run := FALSE;
END_IF;

END_PROGRAM
