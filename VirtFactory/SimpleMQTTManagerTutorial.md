# Simple MQTT Manager Tutorial

This tutorial will guide you through creating a simple MQTT Manager in Unreal Engine that connects to an MQTT broker, publishes random values, and displays received messages on screen.

## 🎯 What You'll Build
- **Simple MQTT Manager** that connects to a broker
- **Random value publishing** every few seconds
- **Message display** on screen when messages are received
- **Simulation mode** fallback

## 📋 Prerequisites
- **Unreal Engine 5.3+** installed
- **MQTT Broker** running (e.g., Mosquitto, or use a public test broker)
- **UnrealMQTT plugin** installed and enabled

---

# 🚀 Step 1: Project Setup

## 1.1 Create New Project
1. Open **Epic Games Launcher**
2. Click **Launch** → **Unreal Engine 5.3+**
3. Select **Games** → **Blank**
4. Choose **Blueprint** project type
5. Name: `SimpleMQTT`
6. Location: Choose your preferred folder
7. Click **Create**

## 1.2 Enable MQTT Plugin
1. Close Unreal Engine
2. Open `SimpleMQTT.uproject` in a text editor
3. Add to the `"Plugins"` section:
```json
{
    "Name": "UnrealMQTT",
    "Enabled": true
}
```
4. Save and reopen the project

---

# 🔗 Step 2: Create MQTT Manager Blueprint

## 2.1 Create Blueprint Class
1. Right-click in Content Browser → **Blueprint Class**
2. Select **Actor** as parent
3. Name: `BP_SimpleMQTTManager`
4. Double-click to open Blueprint Editor

## 2.2 Add Components
1. In **Components** panel, add:
   - **Scene** (name: Root)
   - **TextRender** (name: DisplayText)

2. Set component hierarchy:
   ```
   Root
   └── DisplayText (positioned in front of camera)
   ```

## 2.3 Create Variables
In **My Blueprint** panel → **Variables**:

| Variable Name | Type | Default Value | Description |
|---------------|------|---------------|-------------|
| BrokerURL | String | "tcp://test.mosquitto.org:1883" | MQTT broker URL |
| ClientID | String | "SimpleMQTTClient" | MQTT client ID |
| IsConnected | Boolean | false | Connection status |
| Topic | String | "simple/test" | MQTT topic to use |
| DisplayText | TextRender Component | None | Reference to display component |

---

# 📡 Step 3: Event Graph - Connection

## 3.1 Begin Play Event
```
Event Begin Play
├── Set DisplayText properties (size, color, position)
├── Attempt to connect to MQTT broker
├── Subscribe to the topic
├── Start publishing timer
└── Display connection status
```

**Step-by-step:**
1. Drag **Event Begin Play** from **Overrides**
2. Add **"MQTT Connect"** node
   - Broker URL: BrokerURL
   - Client ID: ClientID
3. Add **Branch** to check connection success
4. If connected:
   - Add **"MQTT Subscribe"** node with Topic
   - Set IsConnected = true
   - Update DisplayText to "Connected"
5. If failed:
   - Set IsConnected = false
   - Update DisplayText to "Connection Failed"

---

# 📤 Step 4: Publishing Random Values

## 4.1 Create Publish Timer Event
Create **Custom Event**: `Publish Random Value`

**Logic:**
```
Publish Random Value
├── Generate random float between 0 and 100
├── Convert to string
├── Use "MQTT Publish" node
│   ├── Topic: Topic
│   ├── Payload: random value string
├── Update DisplayText with "Published: {value}"
```

**Step-by-step:**
1. Create **Custom Event** named `PublishRandomValue`
2. Add **"Random Float in Range"** node (0 to 100)
3. Add **"Float to String"** node
4. Add **"MQTT Publish"** node
   - Topic: Topic variable
   - Payload: the string
5. Add **"Set Text"** on DisplayText to show published value

## 4.2 Start Publishing Timer
In **Begin Play**, after connection:
```
├── Add "Set Timer" node
│   ├── Function Name: PublishRandomValue
│   ├── Time: 2.0 seconds
│   ├── Looping: true
```

---

# 📥 Step 5: Receiving Messages

## 5.1 On Message Received Event
Create **Custom Event**: `On MQTT Message Received`

**Inputs:**
- Topic (String)
- Payload (String)

**Logic:**
```
On MQTT Message Received (Topic, Payload)
├── Update DisplayText with "Received: {Payload}"
├── Add debug print to screen
```

**Step-by-step:**
1. Create **Custom Event** named `OnMQTTMessageReceived`
2. Add inputs: Topic (String), Payload (String)
3. Add **"Set Text"** on DisplayText: "Received: " + Payload
4. Add **"Print String"** node for debugging

## 5.2 Bind Message Event
In **Begin Play**, after subscribing:
```
├── Add "Bind Event to OnMQTTMessageReceived" node
│   ├── Target: MQTT Subscribe result
│   ├── Event: OnMQTTMessageReceived
```

---

# 🎮 Step 6: Level Setup

## 6.1 Create Level
1. **File** → **New Level** → **Empty Level**
2. Save as `MQTTTestLevel`

## 6.2 Add MQTT Manager
1. Drag `BP_SimpleMQTTManager` into the level
2. Position at (0, 0, 0)

## 6.3 Add Camera
1. Add **Cine Camera Actor**
2. Position: Location (0, -500, 100)
3. Rotation: (0, 0, 0) - facing the text

---

# 🧪 Step 7: Testing

## 7.1 Play in Editor
1. Press **Play** (Alt+P)
2. Check the DisplayText for connection status
3. Watch for published values every 2 seconds
4. The text should update with received messages

## 7.2 Debug Tips
- Use **Print String** nodes to debug in the console
- Check MQTT broker logs for connection attempts
- Try different broker URLs if connection fails

---

# 🎯 Final Result

You now have a simple MQTT Manager that:
- ✅ Connects to an MQTT broker
- ✅ Publishes random values every 2 seconds
- ✅ Subscribes to messages and displays them
- ✅ Shows status on screen
- ✅ Works with simulation if needed

The manager will display "Connected" on success, publish random numbers, and show any received messages. Use a tool like MQTT Explorer to send messages to the topic and see them displayed!