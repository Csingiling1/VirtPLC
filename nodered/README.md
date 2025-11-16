# Node-RED MQTT to OPC-UA Bridge

This Node-RED instance acts as a bridge between MQTT messages from Unreal Engine and OPC-UA for the collector service.

## Purpose

- **Subscribe** to MQTT topics from Unreal Engine virtual factory
- **Transform** MQTT messages to OPC-UA writes
- **Publish** data to OPC-UA server for collector consumption

## MQTT Topics Subscribed

- `factory/+/speed` - Machine speed values
- `factory/+/temperature` - Machine temperature values
- `factory/+/running` - Machine running state
- `factory/+/fault` - Machine fault state

## OPC-UA Server

- **Endpoint**: `opc.tcp://nodered:4840/virtplc/`
- **Namespace**: Virtual PLC data
- **Security**: None (local network)

## Flow Structure

1. **MQTT Subscribers** - Listen to factory topics
2. **JSON Parsers** - Parse incoming MQTT payloads
3. **Topic Extractors** - Extract device ID and sensor type from topic
4. **OPC-UA Writers** - Write values to OPC-UA server
5. **Debug Logs** - Log all operations

## Configuration

The flow is pre-configured in `flows.json`. To modify:

1. Access Node-RED UI at `http://localhost:1880`
2. Import/modify the flow
3. Add more MQTT topics as needed
4. Configure OPC-UA node IDs for your collector

## Adding More Sensors

To add more sensors:

1. Add new MQTT subscriber node
2. Set topic pattern (e.g., `factory/+/pressure`)
3. Connect to JSON parser → topic extractor → OPC-UA writer
4. Configure the OPC-UA node ID in the writer

## Troubleshooting

- Check Node-RED logs: `docker logs virtplc-nodered`
- Verify MQTT broker connection
- Ensure OPC-UA security settings match collector expectations
- Use the debug nodes to monitor message flow