PROGRAM Conveyor1_Control
VAR
    Conv_Start: BOOL;
    Conv_Stop: BOOL;
    E_Stop: BOOL;
    Conv1_Running: BOOL;
    Conv1_Speed: REAL;
    Conv1_ItemCount: INT := 0;
    Conv1_Emergency: BOOL;
    
    (* Dependencies *)
    Motor1_Run: BOOL; (* Conveyor requires Motor1 to be running *)
    
    (* Internal variables *)
    StartInternal: BOOL;
    Sensor1_Detected: BOOL;
    Sensor1_Previous: BOOL;
    ONS_Trigger: BOOL; (* One-shot for item counting *)
    
    (* Constants *)
    TARGET_SPEED: REAL := 50.0; (* m/min *)
    RAMP_RATE: REAL := 2.0;
END_VAR

(* Rung 1: Start Conveyor Logic *)
StartInternal := Conv_Start AND Motor1_Run AND NOT E_Stop AND NOT Conv1_Emergency;
IF StartInternal OR (Conv1_Running AND NOT Conv_Stop AND Motor1_Run AND NOT E_Stop AND NOT Conv1_Emergency) THEN
    Conv1_Running := TRUE;
END_IF;

(* Rung 2: Stop Conveyor Logic *)
IF Conv_Stop OR E_Stop OR Conv1_Emergency OR NOT Motor1_Run THEN
    Conv1_Running := FALSE;
END_IF;

(* Rung 3: Speed Control *)
IF Conv1_Running THEN
    (* Ramp up to target speed *)
    IF Conv1_Speed < TARGET_SPEED THEN
        Conv1_Speed := Conv1_Speed + RAMP_RATE;
        IF Conv1_Speed > TARGET_SPEED THEN
            Conv1_Speed := TARGET_SPEED;
        END_IF;
    END_IF;
ELSE
    (* Ramp down when stopped *)
    IF Conv1_Speed > 0 THEN
        Conv1_Speed := Conv1_Speed - (RAMP_RATE * 1.5); (* Faster decel *)
        IF Conv1_Speed < 0 THEN
            Conv1_Speed := 0;
        END_IF;
    END_IF;
END_IF;

(* Rung 4: Item Counting with One-Shot *)
(* Simulate sensor detecting items when conveyor is running *)
IF Conv1_Running AND Conv1_Speed > 10.0 THEN
    (* Simulate item detection based on time/speed *)
    (* In real application, this would be a physical sensor input *)
    Sensor1_Detected := (Conv1_ItemCount MOD 100) < 10; (* Simple simulation *)
ELSE
    Sensor1_Detected := FALSE;
END_IF;

(* One-shot logic: trigger on rising edge *)
ONS_Trigger := Sensor1_Detected AND NOT Sensor1_Previous;
IF ONS_Trigger THEN
    Conv1_ItemCount := Conv1_ItemCount + 1;
END_IF;
Sensor1_Previous := Sensor1_Detected;

(* Rung 5: Emergency Stop Handling *)
IF Conv1_Emergency THEN
    Conv1_Running := FALSE;
    Conv1_Speed := 0; (* Immediate stop *)
END_IF;

(* Rung 6: Interlock with Motor1 *)
(* If Motor1 stops while conveyor is running, stop conveyor *)
IF Conv1_Running AND NOT Motor1_Run THEN
    Conv1_Running := FALSE;
END_IF;

END_PROGRAM
