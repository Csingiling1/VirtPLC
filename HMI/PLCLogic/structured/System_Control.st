PROGRAM System_Control
VAR
    System_Reset: BOOL;
    System_EmergencyStop: BOOL;
    System_Mode: INT := 0; (* 0=Manual, 1=Auto, 2=Maintenance *)
    
    (* All motor and conveyor run states *)
    Motor1_Run: BOOL;
    Motor2_Run: BOOL;
    Conv1_Running: BOOL;
    
    (* All faults *)
    Motor1_Fault: BOOL;
    Motor2_Fault: BOOL;
    
    (* Internal variables *)
    ResetPulse: R_TRIG;
    EStopPrevious: BOOL;
    AllStopped: BOOL;
END_VAR

(* Rung 1: Emergency Stop Logic *)
IF System_EmergencyStop THEN
    (* Stop all equipment immediately *)
    Motor1_Run := FALSE;
    Motor2_Run := FALSE;
    Conv1_Running := FALSE;
END_IF;

(* Rung 2: System Reset Logic *)
ResetPulse(CLK := System_Reset);
IF ResetPulse.Q THEN
    (* Clear all faults if equipment is stopped *)
    AllStopped := NOT Motor1_Run AND NOT Motor2_Run AND NOT Conv1_Running;
    
    IF AllStopped THEN
        Motor1_Fault := FALSE;
        Motor2_Fault := FALSE;
        System_EmergencyStop := FALSE;
    END_IF;
END_IF;

(* Rung 3: Mode Control *)
(* Mode changes only allowed when all equipment is stopped *)
(* Mode 0 = Manual (HMI control) *)
(* Mode 1 = Auto (sequence control) *)
(* Mode 2 = Maintenance (all interlocks bypassed - use with caution) *)

IF System_Mode = 1 THEN
    (* Auto mode logic would go here *)
    (* For now, just ensure safety *)
    IF System_EmergencyStop THEN
        (* Fall back to manual mode on E-stop *)
        System_Mode := 0;
    END_IF;
END_IF;

(* Rung 4: Watchdog/Heartbeat *)
(* Could implement system heartbeat monitoring here *)

END_PROGRAM
