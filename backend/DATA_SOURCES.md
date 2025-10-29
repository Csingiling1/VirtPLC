# Data Source Configuration

The VirtPLC backend supports flexible data source switching between simulator and real PLC hardware through dependency injection.

## 🎯 **Quick Switch**

### **Development/Testing (Simulator)**
```bash
# Use simulator as data source
export DATA_SOURCE=simulator
docker-compose up -d
```

### **Production (Real PLC)**
```bash
# Use real PLC as data source
export DATA_SOURCE=plc
docker-compose up -d
```

## 🔧 **Configuration Options**

### **Environment Variables**
```bash
# Data source selection
DATA_SOURCE=simulator  # or 'plc'

# Simulator configuration
SIMULATOR_API_URL=http://simulator:8080
SIMULATOR_NAME=VirtPLC Simulator

# PLC configuration
PLC_NAME=Production PLC
OPCUA_CLIENT_ENDPOINT=opc.tcp://plc-server:4840/production
```

### **Spring Profiles**
```bash
# Simulator profile
java -jar app.jar --spring.profiles.active=simulator

# PLC profile
java -jar app.jar --spring.profiles.active=plc

# Hybrid profile (both available)
java -jar app.jar --spring.profiles.active=hybrid
```

## 📊 **Data Source Services**

### **SimulatorApiService** (Default)
- **Purpose**: Development and testing
- **Data Source**: REST API from VirtPLC Simulator
- **Advantages**: 
  - Flexible device structure
  - Easy to modify and test
  - No hardware dependencies
  - Real-time data streaming

### **PlcDataSourceService** (Production)
- **Purpose**: Production with real PLC hardware
- **Data Source**: OPC-UA from actual PLC
- **Advantages**:
  - Real production data
  - Industrial protocol support
  - Production-ready reliability

## 🚀 **Usage Examples**

### **Development Setup**
```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - DATA_SOURCE=simulator
      - SIMULATOR_API_URL=http://simulator:8080
```

### **Production Setup**
```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - DATA_SOURCE=plc
      - OPCUA_CLIENT_ENDPOINT=opc.tcp://plc-server:4840/production
```

### **Hybrid Setup** (Both Available)
```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - DATA_SOURCE=simulator  # Primary
      - SIMULATOR_API_URL=http://simulator:8080
      - OPCUA_CLIENT_ENDPOINT=opc.tcp://plc-server:4840/production
```

## 🔄 **Switching at Runtime**

### **Via Environment Variable**
```bash
# Switch to PLC
docker-compose exec backend sh -c 'export DATA_SOURCE=plc && java -jar app.jar'

# Switch to Simulator
docker-compose exec backend sh -c 'export DATA_SOURCE=simulator && java -jar app.jar'
```

### **Via Configuration File**
```bash
# Edit application.properties
echo "data.source=plc" >> application.properties

# Restart backend
docker-compose restart backend
```

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Source   │    │  DataService     │    │   TimescaleDB   │
│   Interface     │◄───┤  (Flexible)      │───►│   (Storage)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼───┐
│Simulator│ │  PLC  │
│Service  │ │Service│
└────────┘ └───────┘
```

## 🔍 **Monitoring**

### **Check Current Data Source**
```bash
# Check logs
docker-compose logs backend | grep "data source"

# Check API
curl http://localhost:18080/api/data/health
```

### **Data Source Status**
```bash
# Simulator status
curl http://localhost:5000/simulation/status

# PLC status (if available)
# Check OPC-UA connection logs
```

## 🛠️ **Adding New Data Sources**

1. **Create Service Class**:
```java
@Service
@ConditionalOnProperty(name = "data.source", havingValue = "custom")
public class CustomDataSourceService implements DataSourceService {
    // Implementation
}
```

2. **Add Configuration**:
```yaml
data:
  source: custom
custom:
  name: Custom Data Source
  # ... other config
```

3. **Update Docker Compose**:
```yaml
environment:
  - DATA_SOURCE=custom
  - CUSTOM_CONFIG=value
```

## 🎯 **Best Practices**

1. **Development**: Always use `simulator` data source
2. **Testing**: Use `simulator` with different device configurations
3. **Production**: Use `plc` data source with real hardware
4. **Hybrid**: Use `simulator` as primary with `plc` as fallback
5. **Monitoring**: Always check data source availability
6. **Logging**: Enable debug logs to track data source usage

## 🚨 **Troubleshooting**

### **Data Source Not Available**
```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs backend | grep -i "data source"

# Test connectivity
curl http://localhost:5000/simulation/status  # Simulator
```

### **OPC-UA Connection Issues**
```bash
# Check OPC-UA server
docker-compose logs simulator | grep -i opcua

# Test OPC-UA endpoint
opcua-client opc.tcp://localhost:24840/virtplc/
```

### **Configuration Issues**
```bash
# Check environment variables
docker-compose exec backend env | grep DATA_SOURCE

# Check Spring profiles
docker-compose exec backend java -jar app.jar --spring.profiles.active=simulator
```
