(* 
   PLC LADDER LOGIC - MQTT Command Publisher
   Purpose: Monitor Ignition tag changes and publish MQTT commands to Unreal Engine
   Platform: IEC 61131-3 Structured Text
*)

PROGRAM MQTT_Command_Publisher
VAR
    (* Ignition Tag References *)
    Conveyor1_Running_Input : BOOL; (* From Ignition HMI *)
    Conveyor2_Running_Input : BOOL;
    Machine1_Running_Input  : BOOL;
    
    (* Previous State Memory *)
    Conveyor1_Running_Prev : BOOL := FALSE;
    Conveyor2_Running_Prev : BOOL := FALSE;
    Machine1_Running_Prev  : BOOL := FALSE;
    
    (* MQTT Client Instance *)
    MQTT_Client : MQTT_Publisher;
    
    (* Command Buffers *)
    MQTT_Topic   : STRING(255);
    MQTT_Payload : STRING(255);
    
    (* Status *)
    PublishError : BOOL := FALSE;
    MessageCount : UDINT := 0;
END_VAR

(*==============================================*)
(* RUNG 1: Conveyor 1 On/Off Command Detection *)
(*==============================================*)
IF Conveyor1_Running_Input <> Conveyor1_Running_Prev THEN
    (* Tag value changed - publish to MQTT *)
    MQTT_Topic := 'ignition/command/conveyor1/running';
    
    IF Conveyor1_Running_Input THEN
        MQTT_Payload := '{"value":true,"source":"ignition","timestamp":' + 
                       TO_STRING(CURRENT_TIME_MS()) + '}';
    ELSE
        MQTT_Payload := '{"value":false,"source":"ignition","timestamp":' + 
                       TO_STRING(CURRENT_TIME_MS()) + '}';
    END_IF;
    
    (* Publish to MQTT Broker *)
    PublishError := NOT MQTT_Client.Publish(
        Topic := MQTT_Topic,
        Payload := MQTT_Payload,
        QoS := 1,
        Retain := FALSE
    );
    
    IF NOT PublishError THEN
        MessageCount := MessageCount + 1;
    END_IF;
    
    (* Update previous state *)
    Conveyor1_Running_Prev := Conveyor1_Running_Input;
END_IF;

(*==============================================*)
(* RUNG 2: Conveyor 2 On/Off Command Detection *)
(*==============================================*)
IF Conveyor2_Running_Input <> Conveyor2_Running_Prev THEN
    MQTT_Topic := 'ignition/command/conveyor2/running';
    
    IF Conveyor2_Running_Input THEN
        MQTT_Payload := '{"value":true,"source":"ignition","timestamp":' + 
                       TO_STRING(CURRENT_TIME_MS()) + '}';
    ELSE
        MQTT_Payload := '{"value":false,"source":"ignition","timestamp":' + 
                       TO_STRING(CURRENT_TIME_MS()) + '}';
    END_IF;
    
    PublishError := NOT MQTT_Client.Publish(
        Topic := MQTT_Topic,
        Payload := MQTT_Payload,
        QoS := 1,
        Retain := FALSE
    );
    
    IF NOT PublishError THEN
        MessageCount := MessageCount + 1;
    END_IF;
    
    Conveyor2_Running_Prev := Conveyor2_Running_Input;
END_IF;

(*==============================================*)
(* RUNG 3: Machine 1 On/Off Command Detection  *)
(*==============================================*)
IF Machine1_Running_Input <> Machine1_Running_Prev THEN
    MQTT_Topic := 'ignition/command/machine1/running';
    
    IF Machine1_Running_Input THEN
        MQTT_Payload := '{"value":true,"source":"ignition","timestamp":' + 
                       TO_STRING(CURRENT_TIME_MS()) + '}';
    ELSE
        MQTT_Payload := '{"value":false,"source":"ignition","timestamp":' + 
                       TO_STRING(CURRENT_TIME_MS()) + '}';
    END_IF;
    
    PublishError := NOT MQTT_Client.Publish(
        Topic := MQTT_Topic,
        Payload := MQTT_Payload,
        QoS := 1,
        Retain := FALSE
    );
    
    IF NOT PublishError THEN
        MessageCount := MessageCount + 1;
    END_IF;
    
    Machine1_Running_Prev := Machine1_Running_Input;
END_IF;

END_PROGRAM


(*==============================================*)
(* FUNCTION BLOCK: MQTT Publisher               *)
(* Note: This is a placeholder - replace with   *)
(* your PLC's actual MQTT library               *)
(*==============================================*)
FUNCTION_BLOCK MQTT_Publisher
VAR_INPUT
    Topic   : STRING(255);
    Payload : STRING(255);
    QoS     : INT;      (* 0, 1, or 2 *)
    Retain  : BOOL;
END_VAR
VAR_OUTPUT
    Success : BOOL;
    Error   : BOOL;
END_VAR
VAR
    (* Internal MQTT client state *)
    Connected : BOOL := FALSE;
END_VAR

(* Pseudo-code - implement with your PLC's MQTT library *)
(* Examples:
   - Siemens: Use MQTT_CLIENT function block
   - Allen-Bradley: Use EMQX or Sparkplug libraries
   - Beckhoff: Use TcIoTcps_MqttClient
   - CODESYS: Use MQTT Client library
*)

Success := FALSE;
Error := FALSE;

(* Check connection *)
IF NOT Connected THEN
    (* Attempt connection to broker *)
    (* Connected := MQTT_Connect('mqtt://mqtt:1883'); *)
    RETURN;
END_IF;

(* Publish message *)
(* Success := MQTT_Publish_Internal(Topic, Payload, QoS, Retain); *)
(* Error := NOT Success; *)

END_FUNCTION_BLOCK
