# VirtPLC Architecture Guide

## System Architecture

### Overview

The VirtPLC system uses a **client-server architecture** where:

1. **Backend Server** - Centralized services (databases, monitoring)
2. **Edge Devices** - Ignition Edge gateways (can be tablets, industrial PCs, Raspberry Pi)
3. **Web Clients** - Any browser can access the HMI (phone, tablet, laptop)

```
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND SERVER                          │
│  (Cloud, On-Premise Data Center, or Local Server)          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  TimeBase    │  │ PostgreSQL   │  │   Redis      │    │
│  │  (Time-Series│  │ (Relational  │  │   (Cache)    │    │
│  │   Database)  │  │   Database)  │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │  Grafana     │  │  Prometheus  │                       │
│  │ (Monitoring) │  │  (Metrics)   │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Network (LAN/WAN/VPN)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ EDGE DEVICE 1 │   │ EDGE DEVICE 2 │   │ EDGE DEVICE N │
│               │   │               │   │               │
│ ┌───────────┐ │   │ ┌───────────┐ │   │ ┌───────────┐ │
│ │ Ignition  │ │   │ │ Ignition  │ │   │ │ Ignition  │ │
│ │   Edge    │ │   │ │   Edge    │ │   │ │   Edge    │ │
│ └───────────┘ │   │ └───────────┘ │   │ └───────────┘ │
│       ▲       │   │       ▲       │   │       ▲       │
│       │       │   │       │       │   │       │       │
│ ┌───────────┐ │   │ ┌───────────┐ │   │ ┌───────────┐ │
│ │PLC/OPC-UA │ │   │ │PLC/OPC-UA │ │   │ │PLC/OPC-UA │ │
│ │ Simulator │ │   │ │ Simulator │ │   │ │ Simulator │ │
│ └───────────┘ │   │ └───────────┘ │   │ └───────────┘ │
│               │   │               │   │               │
│ Tablet/Phone/ │   │ Industrial PC │   │ Raspberry Pi  │
│    Laptop     │   │               │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ WEB BROWSERS  │
                    │               │
                    │ - Phone       │
                    │ - Tablet      │
                    │ - Laptop      │
                    │ - Desktop     │
                    └───────────────┘
```

## Deployment Scenarios

### Scenario 1: Development/Testing (Single Machine)

All services run on one machine for development:

```bash
# Start everything locally
docker-compose -f docker-compose.dev.yml up
```

**Use Case:** Local development, testing, demonstration

### Scenario 2: Production with Separate Backend (Recommended)

Backend server runs centralized services, edge devices run Ignition Edge:

```bash
# On backend server (cloud/on-premise)
docker-compose -f docker-compose.backend.yml up -d

# On edge device 1 (tablet/industrial PC)
docker-compose -f docker-compose.edge.yml up -d

# On edge device 2
docker-compose -f docker-compose.edge.yml up -d
```

**Use Case:** Production deployment, multiple locations, scalability

### Scenario 3: Cloud Backend + Local Edge

Backend in cloud (AWS, Azure, GCP), edge devices on-premise:

```bash
# On cloud server
docker-compose -f docker-compose.backend.yml up -d

# On local factory floor devices
docker-compose -f docker-compose.edge.yml up -d
```

**Use Case:** Remote monitoring, centralized data, distributed factories

## Hardware Requirements

### Backend Server

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 100 GB SSD
- Network: 1 Gbps

**Recommended:**
- CPU: 8+ cores
- RAM: 16+ GB
- Disk: 500 GB NVMe SSD with RAID
- Network: 10 Gbps

### Edge Device Options

#### Option 1: Industrial Tablet
- **Example:** Panasonic Toughbook, Dell Latitude Rugged
- CPU: 2 cores
- RAM: 4 GB
- Storage: 32 GB
- **Cost:** $1,000 - $3,000

#### Option 2: Industrial PC
- **Example:** Advantech ARK-1000, Siemens SIMATIC IPC
- CPU: 4 cores
- RAM: 8 GB
- Storage: 64 GB SSD
- **Cost:** $500 - $2,000

#### Option 3: Raspberry Pi 4/5
- CPU: 4 cores (ARM)
- RAM: 4-8 GB
- Storage: 32 GB MicroSD
- **Cost:** $50 - $100

#### Option 4: Standard Laptop/PC
- Any modern laptop works for testing
- CPU: 2+ cores
- RAM: 4+ GB
- **Cost:** Free (reuse existing)

## Network Configuration

### Port Mapping

**Backend Server:**
```yaml
TimeBase:     8011  # Historical database
PostgreSQL:   5432  # Relational database
Redis:        6379  # Cache
Grafana:      3000  # Monitoring UI
Prometheus:   9090  # Metrics
```

**Edge Device:**
```yaml
Ignition Gateway:  8088  # Web interface
Ignition HTTPS:    8043  # Secure web interface
OPC-UA Simulator:  4840  # Equipment data
```

### Firewall Rules

**Backend Server** (allow incoming):
- TCP 8011 from edge devices (TimeBase)
- TCP 5432 from edge devices (PostgreSQL)
- TCP 6379 from edge devices (Redis)
- TCP 3000 from admin network (Grafana)

**Edge Device** (allow incoming):
- TCP 8088 from local network (HMI access)
- TCP 8043 from local network (HTTPS HMI)

### Network Latency Considerations

| Connection | Max Latency | Recommended |
|------------|-------------|-------------|
| Edge → Backend DB | 100ms | < 50ms |
| Browser → Edge Gateway | 200ms | < 100ms |
| Edge → TimeBase | 500ms | < 200ms |

## Data Flow

### Real-Time Data Path

```
PLC/Simulator → OPC-UA → Ignition Edge → Web Browser
     (1ms)      (10ms)       (50ms)       (100ms)
```

### Historical Data Path

```
PLC/Simulator → OPC-UA → Ignition Edge → TimeBase (Backend)
     (1ms)      (10ms)       (50ms)         (1s)
                                              ↓
                                         PostgreSQL
                                              ↓
                                          Grafana ← Web Browser
```

## Ignition Edge vs Ignition Gateway

### Ignition Edge

**Use Case:** Local device (tablet, industrial PC, edge server)

**Features:**
- Lightweight (< 500 MB RAM)
- Perspective Module (web HMI)
- OPC-UA client
- Tag history forwarding
- 2-hour runtime license (resets every 24 hours)

**Limitations:**
- No SCADA clients
- Limited to 50 tags (or based on license)
- Cannot be redundant master

**Pricing:**
- Free 2-hour reset license
- ~$500 for permanent license

### Ignition Gateway (Full)

**Use Case:** Central server, full SCADA system

**Features:**
- Unlimited tags
- Vision + Perspective modules
- Redundancy support
- Full reporting
- EAM (Asset Management)

**Pricing:**
- ~$8,500+ depending on modules

## Security Considerations

### Network Segmentation

```
Internet
    ↓
[Firewall]
    ↓
DMZ (Backend Services)
    ↓
[Firewall]
    ↓
OT Network (Edge Devices)
    ↓
[Firewall]
    ↓
PLC Network (Process Control)
```

### Best Practices

1. **Use VPN** for remote access
2. **Enable SSL/TLS** on all connections
3. **Firewall rules** - whitelist only necessary ports
4. **Strong passwords** - no defaults
5. **Regular updates** - patch vulnerabilities
6. **Network isolation** - separate OT from IT
7. **Backup strategy** - automated daily backups

## Accessing the HMI

### From Same Network as Edge Device

```
http://<edge-device-ip>:8088/data/perspective/client/VirtPLC-HMI
```

Example:
```
http://192.168.1.100:8088/data/perspective/client/VirtPLC-HMI
```

### From Internet (with proper security)

```
https://hmi.yourcompany.com/data/perspective/client/VirtPLC-HMI
```

### Mobile Access

1. Open mobile browser (Chrome, Safari, Firefox)
2. Navigate to edge device URL
3. HMI automatically adapts to screen size (Perspective is responsive)
4. Bookmark for quick access

### Offline Support

Perspective sessions can cache data for offline operation:
- Configure in Project Properties → Perspective → Session
- Enable "Store and Forward" for critical data

## Scaling Strategies

### Horizontal Scaling (Multiple Edge Devices)

```
Backend Server (1x)
    ↑
    ├─ Edge Device 1 → Factory Line 1
    ├─ Edge Device 2 → Factory Line 2
    ├─ Edge Device 3 → Factory Line 3
    └─ Edge Device N → Factory Line N
```

### Vertical Scaling (More Powerful Backend)

```
Increase backend resources:
- More CPU cores
- More RAM
- Faster storage (NVMe)
- Database replication
```

### Geographic Distribution

```
                Cloud Backend
                      ↑
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   Factory USA   Factory EU   Factory APAC
   (Edge Devices) (Edge Devices) (Edge Devices)
```

## Monitoring and Maintenance

### Health Checks

```bash
# Backend health
curl http://backend-server:8011/health  # TimeBase
curl http://backend-server:3000/health  # Grafana

# Edge device health
curl http://edge-device:8088/StatusPing  # Ignition
```

### Automated Monitoring

All services include Prometheus metrics:
- CPU/Memory usage
- Response times
- Error rates
- Connection states

Access Grafana dashboards:
```
http://backend-server:3000
```

### Backup Strategy

**Backend (Daily):**
- TimeBase snapshots
- PostgreSQL dumps
- Configuration backups

**Edge Device (Weekly):**
- Gateway backups (.gwbk)
- Project exports

## Cost Analysis

### Small Deployment (1 Edge Device)

| Component | Cost |
|-----------|------|
| Backend Server (VPS) | $50/month |
| Raspberry Pi 4 | $75 one-time |
| Ignition Edge License | $500 one-time (or free 2hr) |
| **Total First Year** | **$1,175** |

### Medium Deployment (5 Edge Devices)

| Component | Cost |
|-----------|------|
| Backend Server (Dedicated) | $200/month |
| Industrial Tablets (5x) | $10,000 one-time |
| Ignition Edge Licenses (5x) | $2,500 one-time |
| **Total First Year** | **$14,900** |

### Large Deployment (20+ Edge Devices)

Contact Inductive Automation for enterprise pricing.

## Next Steps

1. **Choose Deployment Model** (dev vs production)
2. **Provision Backend Server** (cloud or on-premise)
3. **Select Edge Devices** (tablet, PC, or Raspberry Pi)
4. **Configure Network** (VPN, firewall rules)
5. **Deploy Services** (follow deployment guides)
6. **Test Connection** (verify edge → backend)
7. **Go Live** (train operators)

See [SETUP.md](SETUP.md) for detailed installation instructions.
