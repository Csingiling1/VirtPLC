# VirtPLC - How to Test and Use

## Table of Contents

1. [Quick Test (No Installation)](#quick-test-no-installation)
2. [Understanding the Architecture](#understanding-the-architecture)
3. [Testing the PLC Simulator](#testing-the-plc-simulator)
4. [Testing with Ignition Edge](#testing-with-ignition-edge)
5. [Accessing HMI on Devices](#accessing-hmi-on-devices)
6. [Ignition Edge Setup Guide](#ignition-edge-setup-guide)

---

## Quick Test (No Installation)

### Test the PLC Simulator (Fastest Way)

**No Docker, no Ignition - just Python:**

```bash
# 1. Install Python dependencies
cd HMI/simulator
pip install asyncua fastapi uvicorn pyyaml

# 2. Start simulator (Terminal 1)
python simulator.py

# 3. Start web dashboard (Terminal 2)
python web_api.py

# 4. Open web dashboard
open http://localhost:8080

# 5. Test OPC-UA connection (Terminal 3)
python -c "from asyncua import Client; c=Client('opc.tcp://localhost:4840/virtplc/'); c.connect(); print('Connected OK'); c.disconnect()"
```

**What you'll see:**
- Real-time factory simulation with motors and conveyors
- Beautiful web dashboard showing all equipment states
- Temperature, speed, current, power simulation
- Realistic physics (acceleration, deceleration, faults)

---

## Understanding the Architecture

### Architecture Option 1: All-in-One (Development)

```
┌─────────────────────────────────────────┐
│        YOUR COMPUTER                    │
│                                         │
│  ┌────────────────────────────────┐     │
│  │  Docker Compose (All Services) │     │
│  │                                │     │
│  │  • Ignition Edge               │     │
│  │  • PLC Simulator               │     │
│  │  • TimeBase                    │     │
│  │  • PostgreSQL                  │     │
│  │  • Redis                       │     │
│  │  • Grafana + Prometheus        │     │
│  └────────────────────────────────┘     │
└─────────────────────────────────────────┘
          ↓ Access via browser
    http://localhost:8088
```

**Use this for:** Testing, development, learning

**Command:**
```bash
docker-compose up -d
```

### Architecture Option 2: Separated (Production)

```
┌──────────────────────────────┐
│  BACKEND SERVER              │
│  (Cloud or On-Premise)       │
│                              │
│  • TimeBase (historical)     │
│  • PostgreSQL (data)         │
│  • Redis (cache)             │
│  • Grafana (monitoring)      │
│  • Prometheus (metrics)      │
└──────────────────────────────┘
         ↑ Network Connection
         │
    ┌────┴────┬────────┬────────┐
    │         │        │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐
│EDGE 1 │ │EDGE 2│ │EDGE 3│ │EDGE N│
│       │ │      │ │      │ │      │
│Ignit. │ │Ignit.│ │Ignit.│ │Ignit.│
│+Sim.  │ │+Sim. │ │+Sim. │ │+Sim. │
└───┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
    │        │        │        │
    │ WiFi   │        │        │
    ↓        ↓        ↓        ↓
┌────────────────────────────────┐
│  PHONES, TABLETS, LAPTOPS      │
│  Access HMI via Web Browser    │
└────────────────────────────────┘
```

**Use this for:** Production, multiple locations, scalability

**Commands:**
```bash
# Backend server:
docker-compose -f docker-compose.backend.yml up -d

# Each edge device:
docker-compose -f docker-compose.edge.yml up -d
```

---

## Testing the PLC Simulator

### What is the PLC Simulator?

The simulator **replaces real PLC hardware** with a realistic software simulation:

- ✅ **State machines** for motors (STOPPED → STARTING → RUNNING → STOPPING)
- ✅ **Physics simulation** (acceleration, temperature, electrical load)
- ✅ **Fault conditions** (overspeed, overtemperature, random faults)
- ✅ **Interlocks** (conveyor requires motor to be running)
- ✅ **OPC-UA server** (standard industrial protocol)
- ✅ **Web dashboard** for monitoring

### Running Simulator Standalone

```bash
cd HMI/simulator

# Install dependencies
pip install -r requirements.txt

# Run simulator
python simulator.py &

# Run web dashboard (in another terminal)
python web_api.py

# Open dashboard
open http://localhost:8080
```

### Simulator Web Dashboard Features

Navigate to `http://localhost:8080`:

1. **Real-time Equipment Cards**
   - Motor 1 & Motor 2 with live data
   - Conveyor 1 with item counting
   - Emergency stop indicator

2. **Live Metrics** (updates every 2 seconds)
   - Speed (RPM or m/min)
   - Temperature (°C)
   - Current (A)
   - Power (kW)
   - Vibration (mm/s)
   - State (STOPPED/RUNNING/FAULTED)

3. **Color Coding**
   - 🟢 Green: Running normally
   - ⚪ Gray: Stopped
   - 🔴 Red: Fault or emergency stop

### Testing Simulator via OPC-UA

The simulator exposes OPC-UA tags at `opc.tcp://localhost:4840/virtplc/`

**Test with Python:**
```python
from asyncua import Client
import asyncio

async def test():
    client = Client("opc.tcp://localhost:4840/virtplc/")
    await client.connect()
    
    # Read motor speed
    node = client.get_node("ns=2;s=Motor1.Speed")
    speed = await node.read_value()
    print(f"Motor1 Speed: {speed} RPM")
    
    # Write start command
    start_node = client.get_node("ns=2;s=Motor1.StartCommand")
    await start_node.write_value(True)
    print("Motor1 start command sent")
    
    # Wait and check running
    await asyncio.sleep(3)
    running = await client.get_node("ns=2;s=Motor1.Running").read_value()
    print(f"Motor1 Running: {running}")
    
    await client.disconnect()

asyncio.run(test())
```

### Simulator Configuration

Edit `simulator/config.yaml` to customize:

```yaml
motors:
  - name: Motor1
    max_speed: 2200.0  # Change max speed
    acceleration: 50.0  # Change acceleration rate
    
simulation:
  update_rate_hz: 10  # Simulation speed
  fault_probability: 0.01  # 1% fault chance
```

---

## Testing with Ignition Edge

### What is Ignition Edge?

**Ignition Edge** is a lightweight industrial HMI/SCADA platform that:

- ✅ Runs on edge devices (tablets, PCs, Raspberry Pi)
- ✅ Provides **web-based HMI** (access from any browser)
- ✅ Connects to PLCs via **OPC-UA**
- ✅ Logs data to **databases**
- ✅ Has a **2-hour runtime** that resets every 24 hours (free!)

### Installing Ignition Edge (Option A: Docker)

**Easiest method:**

```bash
cd HMI

# All-in-one (testing)
docker-compose up -d

# Wait for startup (2-3 minutes)
docker-compose logs -f ignition-gateway

# Access gateway
open http://localhost:8088
```

**Login:**
- Username: `admin`
- Password: `password` (or from .env)

### Installing Ignition Edge (Option B: Native)

**Download from Inductive Automation:**

1. Visit: https://inductiveautomation.com/downloads/ignition
2. Select: **Ignition Edge (8.1.x)**
3. Choose your platform: **Linux, Windows, or macOS**
4. Download installer

**Install on Linux:**
```bash
# Download (example)
wget https://files.inductiveautomation.com/release/ia/8.1.28/Ignition-edge-linux-64-8.1.28.run

# Make executable
chmod +x Ignition-edge-linux-64-8.1.28.run

# Install
sudo ./Ignition-edge-linux-64-8.1.28.run

# Start service
sudo systemctl start ignition

# Access gateway
open http://localhost:8088
```

**Install on Windows:**
1. Run `.exe` installer
2. Follow wizard (default options)
3. Access: `http://localhost:8088`

**Install on Raspberry Pi:**
```bash
# Download ARM version
wget https://files.inductiveautomation.com/release/ia/8.1.28/Ignition-edge-linux-armhf-32-8.1.28.run

# Install
chmod +x Ignition-edge-linux-armhf-32-8.1.28.run
sudo ./Ignition-edge-linux-armhf-32-8.1.28.run

# Reduce memory usage
sudo nano /usr/local/bin/ignition/data/ignition.conf
# Change: wrapper.java.maxmemory=256

# Start
sudo systemctl start ignition
```

### Configuring Ignition Edge

After installation, configure via web interface:

1. **First-Time Setup Wizard**
   - Navigate to: `http://localhost:8088`
   - Create admin user
   - Accept license (2-hour runtime)
   - Set time zone

2. **Install Perspective Module**
   - Config → Modules
   - Install → Perspective
   - Restart gateway

3. **Configure OPC-UA Connection**
   - Config → OPC UA → Connections
   - Add Device Connection
   - Name: `Backend-OPC-UA`
   - Endpoint URL: `opc.tcp://localhost:4840/virtplc/`
   - Security: None (or configure certificates)
   - Test connection

4. **Import VirtPLC Project**
   - Config → Projects
   - Import Project
   - Upload: `IgnitionEdge/projects/VirtPLC-HMI/` (zip it first)
   - OR use Docker volume mount (auto-loads)

5. **Configure Database**
   - Config → Databases → Connections
   - Add connection
   - Name: `virtplc`
   - JDBC URL: `jdbc:postgresql://localhost:5432/virtplc`
   - Username: `virtplc`
   - Password: (from .env)
   - Test connection

### Testing HMI Views

Navigate to: `http://localhost:8088/data/perspective/client/VirtPLC-HMI`

**Test Overview View:**
- Shows all 4 equipment cards
- Click each card to navigate

**Test Motor Control:**
- Click "START" on Motor 1
- Watch speed gauge increase
- Watch temperature rise
- Adjust target speed
- Click "STOP"

**Test Conveyor:**
- Ensure Motor 1 is running first (interlock)
- Click "START CONVEYOR"
- Watch item count increase
- Click "STOP"

**Test Emergency Stop:**
- Click "EMERGENCY" button
- All equipment stops immediately
- System enters E-STOP state

**Test Alarms:**
- Navigate to Alarms view
- Trigger fault (e.g., overspeed)
- See alarm appear in journal
- Acknowledge alarm

**Test Trends:**
- Navigate to Trends view
- Select time range
- View historical data charts
- Zoom and pan

---

## Accessing HMI on Devices

### From PC/Laptop (Same Network)

```
http://<edge-device-ip>:8088/data/perspective/client/VirtPLC-HMI
```

**Example:**
```
http://192.168.1.50:8088/data/perspective/client/VirtPLC-HMI
```

### From Tablet

1. **Find Edge Device IP:**
   ```bash
   # On edge device
   hostname -I
   ```

2. **Open Browser on Tablet:**
   - Chrome, Safari, or Firefox
   - Navigate to HMI URL
   - Bookmark for quick access

3. **Add to Home Screen (iOS/Android):**
   - Open in Safari/Chrome
   - Tap Share → "Add to Home Screen"
   - Icon appears like a native app

### From Phone

Same as tablet, but:
- Portrait mode supported
- Landscape mode recommended for better view
- Touch controls work natively

### From Multiple Devices Simultaneously

Ignition Perspective supports **multiple concurrent sessions**:
- Each device gets its own session
- Changes on one device don't affect others
- Sessions persist (remembers your view)

---

## Ignition Edge Setup Guide

### Licensing

**Free 2-Hour Runtime:**
- Runs for 2 hours continuously
- Resets every 24 hours
- Perfect for testing and demos
- No license key needed

**Paid License:**
- ~$500 for permanent Edge license
- Unlimited runtime
- Contact Inductive Automation sales

### Resource Requirements

**Minimum:**
- CPU: 1 core
- RAM: 512 MB
- Disk: 2 GB

**Recommended:**
- CPU: 2 cores
- RAM: 1 GB
- Disk: 5 GB

### Security Configuration

**Change Default Password:**
```
Config → Security → Users → admin → Edit
```

**Enable HTTPS:**
```
Config → Web Server → HTTPS Settings
- Upload SSL certificate
- Enable "Force HTTPS Redirect"
```

**Configure Firewall:**
```bash
# Allow Ignition ports
sudo ufw allow 8088/tcp  # HTTP
sudo ufw allow 8043/tcp  # HTTPS
sudo ufw allow 8060/tcp  # Gateway Network
```

### Backup Configuration

**Manual Backup:**
```
Config → System → Backup/Restore → Create Backup
```

**Automatic Backup:**
```
Config → System → Backup/Restore → Schedule
- Daily at 2:00 AM
- Keep 7 days
```

### Troubleshooting

**Gateway Won't Start:**
```bash
# Check logs
tail -f /usr/local/bin/ignition/logs/wrapper.log

# Check port conflicts
sudo netstat -tlnp | grep 8088

# Restart service
sudo systemctl restart ignition
```

**Out of Memory:**
```bash
# Increase Java heap
sudo nano /usr/local/bin/ignition/data/ignition.conf
# Change: wrapper.java.maxmemory=1024

sudo systemctl restart ignition
```

**License Expired (2-hour runtime):**
- Wait 24 hours for automatic reset
- OR restart gateway: `sudo systemctl restart ignition`

---

## Complete Testing Workflow

### Step 1: Test Simulator Only

```bash
cd HMI/simulator
pip install -r requirements.txt
python simulator.py &
python web_api.py
open http://localhost:8080
```

**Verify:**
- ✅ Motors and conveyors visible
- ✅ Dashboard updates every 2 seconds
- ✅ OPC-UA server running on port 4840

### Step 2: Add Ignition Edge (Docker)

```bash
cd HMI
docker-compose up -d
docker-compose logs -f ignition-gateway
# Wait for "Gateway started successfully"
```

**Verify:**
- ✅ Gateway accessible at http://localhost:8088
- ✅ Can login with admin credentials
- ✅ Perspective module installed

### Step 3: Test HMI

```
open http://localhost:8088/data/perspective/client/VirtPLC-HMI
```

**Verify:**
- ✅ All views load
- ✅ Motor control works
- ✅ Conveyor control works
- ✅ Tags update in real-time

### Step 4: Test from Other Devices

**Find IP Address:**
```bash
hostname -I
# Example: 192.168.1.50
```

**Access from Phone/Tablet:**
```
http://192.168.1.50:8088/data/perspective/client/VirtPLC-HMI
```

**Verify:**
- ✅ HMI loads on mobile
- ✅ Touch controls work
- ✅ Layout responsive

### Step 5: Production Deployment

**Deploy Backend:**
```bash
# On server
docker-compose -f docker-compose.backend.yml up -d
```

**Deploy Edge:**
```bash
# On tablet/PC
cp .env.edge .env
nano .env  # Set BACKEND_SERVER_IP
docker-compose -f docker-compose.edge.yml up -d
```

**Verify:**
- ✅ Edge connects to backend
- ✅ Data logging works
- ✅ Grafana shows metrics

---

## Summary

You now have **3 ways to test**:

1. **Simulator Only** - Fastest, no dependencies
   ```bash
   cd simulator && python simulator.py
   ```

2. **All-in-One Docker** - Complete stack, one machine
   ```bash
   docker-compose up -d
   ```

3. **Separated Deployment** - Production-ready, multiple devices
   ```bash
   # Backend:
   docker-compose -f docker-compose.backend.yml up -d
   
   # Edge:
   docker-compose -f docker-compose.edge.yml up -d
   ```

**Access HMI from any device:**
```
http://<edge-ip>:8088/data/perspective/client/VirtPLC-HMI
```

**Monitor simulator:**
```
http://<edge-ip>:8080
```

---

## Next Steps

1. ✅ Test simulator (10 minutes)
2. ✅ Deploy with Docker (15 minutes)
3. ✅ Access from mobile (5 minutes)
4. ✅ Customize views (30 minutes)
5. ✅ Deploy to production (1 hour)

**Questions?** Check `/docs` for more detailed guides!
