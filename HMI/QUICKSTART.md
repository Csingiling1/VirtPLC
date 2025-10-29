# 🚀 VirtPLC HMI - Getting Started

## TL;DR - Three Ways to Run

### 1️⃣ Quick Test (Simulator Only - No Docker)

**Fastest way to see it work:**

```bash
cd HMI/simulator
pip install asyncua fastapi uvicorn pyyaml
python simulator.py &
python web_api.py
```

Open: http://localhost:8080 ← **Beautiful web dashboard!**

### 2️⃣ Complete System (Docker - All-in-One)

**Full HMI with Ignition Edge:**

```bash
cd HMI
docker-compose up -d
```

Open: http://localhost:8088/data/perspective/client/VirtPLC-HMI

### 3️⃣ Production (Separated Backend + Edge Devices)

**For real deployments with tablets/phones:**

```bash
# Backend server:
cd HMI
docker-compose -f docker-compose.backend.yml up -d

# Edge device (tablet/PC):
cp .env.edge .env
nano .env  # Set BACKEND_SERVER_IP=<your-backend-ip>
docker-compose -f docker-compose.edge.yml up -d
```

Access from any device: `http://<edge-ip>:8088/data/perspective/client/VirtPLC-HMI`

---

## 📱 What You Get

### Web-Based HMI (Access from Anywhere!)
- ✅ **Phones** (iOS, Android)
- ✅ **Tablets** (iPad, Android, industrial tablets)
- ✅ **Laptops** (Windows, Mac, Linux)
- ✅ **Industrial PCs**

**No app installation required - just open a browser!**

### Factory Simulator (No Real PLC Needed!)
- ✅ **2 Motors** with realistic physics (temperature, speed, power)
- ✅ **1 Conveyor** with item counting
- ✅ **Emergency stop** system
- ✅ **Fault simulation** (overspeed, overtemp)
- ✅ **Beautiful web dashboard** (http://localhost:8080)

### Enterprise Features
- ✅ **Historical data** (TimeBase time-series database)
- ✅ **Alarms & notifications**
- ✅ **Monitoring** (Grafana + Prometheus)
- ✅ **Tests** (85+ unit/integration/E2E tests)
- ✅ **CI/CD** (GitHub Actions)

---

## 🎯 Architecture

### Option A: All-in-One (Development/Testing)

```
┌─────────────────────────────────┐
│     YOUR COMPUTER               │
│                                 │
│  All services in Docker:        │
│  • Ignition Edge (HMI)          │
│  • PLC Simulator                │
│  • TimeBase (history)           │
│  • PostgreSQL (data)            │
│  • Redis (cache)                │
│  • Grafana (monitoring)         │
└─────────────────────────────────┘
```

### Option B: Separated (Production)

```
┌──────────────────────────┐
│  BACKEND SERVER          │
│  (Cloud or On-Premise)   │
│                          │
│  • TimeBase              │
│  • PostgreSQL            │
│  • Redis                 │
│  • Grafana               │
│  • Prometheus            │
└────────┬─────────────────┘
         │ Network
    ┌────┴────┬─────┬─────┐
    │         │     │     │
┌───▼───┐ ┌──▼──┐ ┌▼──┐ ┌▼───┐
│TABLET │ │PC 1 │ │PC2│ │... │
│       │ │     │ │   │ │    │
│Ignit. │ │Ign. │ │Ig.│ │Ig. │
│+Sim.  │ │+Sim │ │+S │ │+S  │
└───┬───┘ └──┬──┘ └┬──┘ └┬───┘
    │        │     │     │
    └────────┴─────┴─────┘
            WiFi
             │
    ┌────────▼────────┐
    │ PHONES, TABLETS │
    │   LAPTOPS       │
    └─────────────────┘
```

---

## 📖 Documentation

| Document | What's Inside |
|----------|---------------|
| **[HOW_TO_USE.md](docs/HOW_TO_USE.md)** | 🌟 **START HERE!** Complete testing & usage guide |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | System design, hardware options, network config |
| **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** | Production deployment with examples |
| **[SETUP.md](docs/SETUP.md)** | Detailed installation steps |
| **[README.md](README.md)** | Full feature list and architecture |

---

## 🎮 Try It Now!

### Fastest Test (5 minutes)

```bash
# 1. Clone repo
git clone https://github.com/Dedzsinator/VirtPLC.git
cd VirtPLC/HMI/simulator

# 2. Install Python packages
pip install asyncua fastapi uvicorn pyyaml

# 3. Start simulator
python simulator.py &

# 4. Start web dashboard
python web_api.py

# 5. Open browser
open http://localhost:8080
```

**You'll see:**
- Live motor states (speed, temperature, power)
- Conveyor with item counting
- Emergency stop indicator
- Auto-updating every 2 seconds

### Full HMI Test (10 minutes)

```bash
cd VirtPLC/HMI

# 1. Copy environment file
cp .env.example .env

# 2. Start all services
docker-compose up -d

# 3. Wait for gateway startup (2-3 min)
docker-compose logs -f ignition-gateway

# 4. Open HMI
open http://localhost:8088/data/perspective/client/VirtPLC-HMI
```

**Login:** admin / password

**Test:**
- ✅ Navigate between views
- ✅ Start/stop motors
- ✅ Control conveyor
- ✅ View trends
- ✅ Check alarms

---

## 🔧 Hardware Requirements

### For Testing (Your Laptop)
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 10 GB
- **OS:** Linux, Windows 10+, macOS

### For Production Edge Device

**Budget Option:**
- **Raspberry Pi 4 (8GB)** - $80
- Perfect for testing and light loads

**Industrial Option:**
- **Panasonic Toughbook** - $2,000-3,000
- Rugged, IP-rated, perfect for factories

**Industrial PC:**
- **Advantech ARK-1123H** - $800-1,200
- Fanless, reliable, DIN-rail mountable

**Standard Laptop:**
- Any i5 with 8GB RAM works fine

### For Backend Server

**Cloud (Recommended):**
- **AWS t3.large** - ~$60/month
- **DigitalOcean Droplet** - ~$48/month

**On-Premise:**
- **Intel NUC** - $500-700
- **Dell PowerEdge R340** - $1,500

---

## 🎓 What's Inside

### 5 HMI Views
1. **Overview** - System status dashboard
2. **Motor Control** - Start/stop motors, adjust speed
3. **Conveyor Control** - Conveyor with item counting
4. **Alarms** - Alarm journal and acknowledgment
5. **Trends** - Historical data charts

### PLC Simulator Features
- **State machines** (STOPPED → STARTING → RUNNING)
- **Physics** (acceleration, temperature rise)
- **Faults** (overspeed, overtemperature)
- **Interlocks** (conveyor needs motor running)
- **OPC-UA server** (standard industrial protocol)

### Test Suite
- **50+ unit tests** (tag operations, control logic)
- **20+ integration tests** (config validation)
- **15+ E2E tests** (Selenium UI automation)
- **Coverage:** 70%+

---

## 📱 Mobile Access

### From Your Phone

1. **Find edge device IP:**
   ```bash
   hostname -I
   # Example: 192.168.1.50
   ```

2. **Open browser on phone:**
   ```
   http://192.168.1.50:8088/data/perspective/client/VirtPLC-HMI
   ```

3. **Add to home screen:**
   - iOS: Safari → Share → "Add to Home Screen"
   - Android: Chrome → Menu → "Add to Home screen"

**Works like a native app!**

---

## 🆘 Common Questions

### Q: Do I need real PLC hardware?

**A:** No! The simulator replaces real PLC hardware. Perfect for:
- ✅ Learning industrial automation
- ✅ Testing HMI designs
- ✅ Demonstrations
- ✅ Development

### Q: Can I access from my phone?

**A:** Yes! Open a web browser and navigate to the edge device's IP. Works on:
- ✅ iPhone/iPad (Safari, Chrome)
- ✅ Android (Chrome, Firefox)
- ✅ Tablets
- ✅ Any device with a browser

### Q: Do I need to install Ignition?

**A:** No (if using Docker). Just run `docker-compose up -d`.

**If you want native install:** Download from https://inductiveautomation.com/downloads/ignition

### Q: How much does Ignition Edge cost?

**A:** 
- **Free:** 2-hour runtime (resets every 24 hours)
- **Paid:** ~$500 for permanent license
- Perfect for testing with free version!

### Q: Can I use Raspberry Pi?

**A:** Yes! Raspberry Pi 4 (4GB or 8GB) works great. See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for configuration.

### Q: How do I connect multiple edge devices?

**A:** Deploy backend once, then deploy edge stack on each device. See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for examples.

---

## 🚀 Next Steps

1. **[Read HOW_TO_USE.md](docs/HOW_TO_USE.md)** - Detailed testing guide
2. **Test simulator** - `cd simulator && python simulator.py`
3. **Run Docker stack** - `docker-compose up -d`
4. **Deploy to production** - Follow [DEPLOYMENT.md](docs/DEPLOYMENT.md)
5. **Customize views** - Modify Perspective views for your needs

---

## 📊 Project Structure

```
HMI/
├── docker-compose.yml              # All-in-one deployment
├── docker-compose.backend.yml      # Backend services only
├── docker-compose.edge.yml         # Edge device only
├── IgnitionEdge/
│   ├── projects/VirtPLC-HMI/      # 5 Perspective views
│   ├── config/gateway.xml          # Gateway configuration
│   └── tags/tag-definitions.json   # OPC-UA tags
├── simulator/                      # PLC simulator (NEW!)
│   ├── simulator.py               # Main simulator
│   ├── web_api.py                 # Web dashboard
│   ├── config.yaml                # Configuration
│   └── Dockerfile                 # Docker image
├── PLCLogic/                      # PLC programs
│   ├── structured/                # IEC 61131-3 ST
│   └── ladder/                    # Ladder logic docs
├── TimeBaseDB/                    # Time-series database
│   └── config/                    # Schemas & retention
├── tests/                         # 85+ tests
│   ├── test_tag_operations.py
│   ├── test_integration.py
│   └── test_e2e.py
└── docs/                          # Documentation
    ├── HOW_TO_USE.md              ← START HERE!
    ├── ARCHITECTURE.md
    ├── DEPLOYMENT.md
    └── SETUP.md
```

---

## 🎉 Credits

**Built with:**
- Ignition Edge (HMI platform)
- asyncua (OPC-UA server)
- TimeBase (time-series database)
- FastAPI (web dashboard)
- Docker (containerization)
- GitHub Actions (CI/CD)

**License:** MIT

**Issues:** https://github.com/Dedzsinator/VirtPLC/issues

---

**Ready to start? → [docs/HOW_TO_USE.md](docs/HOW_TO_USE.md)** 🚀
