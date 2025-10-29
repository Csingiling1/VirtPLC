PROGRAM Motor1_Control
VAR
    Start_Button: BOOL;
    Stop_Button: BOOL;
    E_Stop: BOOL;
    Motor1_Run: BOOL;
    Motor1_Speed: REAL;
    Motor1_Temp: REAL;
    Motor1_Fault: BOOL;
    TargetSpeed: REAL := 1500.0;
    
    (* Internal variables *)
    StartInternal: BOOL;
    StopInternal: BOOL;
    FaultTimer: TON;
    OverspeedCount: INT := 0;
    
    (* Constants *)
    MAX_SPEED: REAL := 2200.0;
    MAX_TEMP: REAL := 85.0;
    FAULT_DELAY: TIME := T#2S;
END_VAR

(* Rung 1: Motor Start Logic with Seal-in *)
StartInternal := Start_Button AND NOT Motor1_Fault AND NOT E_Stop;
IF StartInternal OR (Motor1_Run AND NOT Stop_Button AND NOT E_Stop AND NOT Motor1_Fault) THEN
    Motor1_Run := TRUE;
END_IF;

(* Rung 2: Motor Stop Logic *)
IF Stop_Button OR E_Stop OR Motor1_Fault THEN
    Motor1_Run := FALSE;
    StopInternal := TRUE;
ELSE
    StopInternal := FALSE;
END_IF;

(* Rung 3: Speed Control *)
IF Motor1_Run THEN
    (* Ramp speed to target *)
    IF Motor1_Speed < TargetSpeed THEN
        Motor1_Speed := Motor1_Speed + 10.0; (* Acceleration rate *)
    ELSIF Motor1_Speed > TargetSpeed THEN
        Motor1_Speed := Motor1_Speed - 10.0; (* Deceleration rate *)
    END_IF;
ELSE
    (* Motor stopped - ramp down *)
    IF Motor1_Speed > 0 THEN
        Motor1_Speed := Motor1_Speed - 20.0; (* Faster deceleration when stopping *)
        IF Motor1_Speed < 0 THEN
            Motor1_Speed := 0;
        END_IF;
    END_IF;
END_IF;

(* Rung 4: Temperature Simulation *)
IF Motor1_Run THEN
    (* Temperature increases with speed *)
    Motor1_Temp := 25.0 + (Motor1_Speed / MAX_SPEED) * 50.0;
    IF Motor1_Speed > 2000.0 THEN
        Motor1_Temp := Motor1_Temp + 10.0; (* Extra heat at high speed *)
    END_IF;
ELSE
    (* Cool down when stopped *)
    IF Motor1_Temp > 25.0 THEN
        Motor1_Temp := Motor1_Temp - 0.5;
    END_IF;
END_IF;

(* Rung 5: Overspeed Protection *)
IF Motor1_Speed > MAX_SPEED THEN
    OverspeedCount := OverspeedCount + 1;
    IF OverspeedCount > 5 THEN (* Fault after 5 consecutive overspeed readings *)
        Motor1_Fault := TRUE;
        Motor1_Run := FALSE;
    END_IF;
ELSE
    OverspeedCount := 0;
END_IF;

(* Rung 6: Over-temperature Protection *)
IF Motor1_Temp > MAX_TEMP THEN
    FaultTimer(IN := TRUE, PT := FAULT_DELAY);
    IF FaultTimer.Q THEN
        Motor1_Fault := TRUE;
        Motor1_Run := FALSE;
    END_IF;
ELSE
    FaultTimer(IN := FALSE);
END_IF;

(* Rung 7: Fault Reset Logic *)
(* Fault can only be reset when motor is stopped and conditions are safe *)
IF NOT Motor1_Run AND Motor1_Speed < 10.0 AND Motor1_Temp < MAX_TEMP THEN
    (* External reset signal would clear fault *)
    (* Motor1_Fault := FALSE; - This would be triggered by reset button *)
END_IF;

END_PROGRAM
