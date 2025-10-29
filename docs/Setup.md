# Setup Guide - Ignition Edge HMI

## Prerequisites

### Software Requirements

1. **Ignition Edge** (latest stable version)
   - Download from [Inductive Automation](https://inductiveautomation.com/downloads/)
   - Free maker edition is sufficient for development

2. **Java Runtime** (Required for Ignition)
   - Java 11 or later
   - Download from [Adoptium](https://adoptium.net/)

3. **TimeBaseDB** (Time-series database)
   - Download from [TimeBase Documentation](https://kb.timebase.info/)
   - Or use Docker image: `deltixinc/timebase`

4. **Web Browser**
   - Chrome, Firefox, or Edge (latest versions)
   - For accessing Ignition Designer and HMI

## Step 1: Install Ignition Edge

### Linux

```bash
# Download installer
wget https://files.inductiveautomation.com/release/ia/8.1.X/Ignition-linux-64-8.1.X.sh

# Make executable
chmod +x Ignition-linux-64-8.1.X.sh

# Run installer
sudo ./Ignition-linux-64-8.1.X.sh

# Start service
sudo systemctl start ignition
sudo systemctl enable ignition
```

### Windows

1. Run the `.exe` installer
2. Follow the installation wizard
3. Choose "Service" installation mode
4. Start the Ignition Gateway service

### macOS

```bash
# Run the .dmg installer
# Follow installation prompts
# Start Ignition from Applications
```

## Step 2: Initial Gateway Configuration

1. Open browser to `http://localhost:8088`
2. Complete the commissioning wizard:
   - Set admin username and password
   - Configure Gateway name: `VirtPLC-HMI`
   - Skip initial project creation (we'll import ours)

## Step 3: Install Required Modules

In Gateway Config → System → Modules:

1. **Perspective Module** (for HMI design)
2. **Tag Historian Module** (for TimeBaseDB integration)
3. **OPC UA Module** (should be pre-installed)
4. **Alarm Notification Module**

Download and install if not present.

## Step 4: Configure OPC-UA Connection

1. Go to **Config → OPC UA → Connections**
2. Click **Create new OPC-UA Connection**
3. Configure:
   - **Name**: `Backend-OPC-UA`
   - **Endpoint URL**: `opc.tcp://backend:4840`
   - **Security Policy**: None (for development)
   - **Session Timeout**: 120000 ms
   - **Subscription Rate**: 1000 ms
4. For local testing, use `opc.tcp://localhost:4840`
5. Click **Save** and verify connection status is **Connected**

## Step 5: Import Tag Configuration

1. Go to **Config → Tags → All Providers**
2. Click **More → Import Tags**
3. Select JSON file from `IgnitionEdge/tags/tag-definitions.json`
4. Review imported tags and click **Import**

Alternative: Manual tag binding
1. Browse OPC-UA server in Tag Browser
2. Drag OPC-UA nodes to create tags
3. Configure historian settings for each tag

## Step 6: Configure TimeBaseDB Connection

### Start TimeBaseDB

```bash
# Using Docker
docker run -d \
  --name timebasedb \
  -p 8011:8011 \
  -v $(pwd)/TimeBaseDB/config:/timebase/config \
  deltixinc/timebase

# Or install standalone and start service
```

### Configure Historian in Ignition

1. Go to **Config → Database → Connections**
2. Create new database connection:
   - **Name**: `TimeBaseDB`
   - **Connect URL**: `dts://localhost:8011`
   - **Driver**: TimeBase JDBC Driver (may need to install separately)
   - **Username/Password**: (if configured)
3. Test connection

4. Go to **Config → Tag Historian → Historian Providers**
5. Create new provider:
   - **Name**: `TimeBase-Historian`
   - **Database**: Select `TimeBaseDB` connection
   - **Partition**: `factory_data`
   - **Store and Forward**: Enabled
6. Save configuration

## Step 7: Import HMI Project

1. Go to **Config → Projects**
2. Click **Import Project**
3. Select `IgnitionEdge/projects/VirtFactory-HMI.zip`
4. Review import settings
5. Click **Import**
6. Set project as **Published**

## Step 8: Configure Tag History

For each tag that should be historized:

1. Navigate to **Config → Tags**
2. Select tag (e.g., `Motor1/Speed`)
3. Edit tag properties
4. **History** tab:
   - Enable **History**
   - Provider: `TimeBase-Historian`
   - Sample Mode: `On Change`
   - Max Time Between Samples: `1 second`
5. Save

## Step 9: Test HMI

1. Open browser to `http://localhost:8088/data/perspective/client/VirtFactory-HMI`
2. Login with gateway credentials
3. Verify:
   - Tags show live values from OPC-UA
   - Controls can write to OPC-UA nodes
   - Charts display historical data
   - Alarms trigger correctly

## Step 10: Configure Alarms (Optional)

1. Go to **Config → Alarming → Notification**
2. Configure notification profiles (email, SMS, etc.)
3. In tag configuration, set alarm thresholds:
   - `Motor1/Temp` > 80°C = High alarm
   - `Motor1/Speed` > 2000 RPM = Warning
   - Any fault tags = Critical alarm

## Troubleshooting

### OPC-UA Connection Fails

- Verify backend server is running
- Check endpoint URL is correct
- Test with UAExpert client first
- Check firewall settings for port 4840
- Review Gateway logs: `Config → Status → Diagnostics → Logs`

### Tags Not Updating

- Check OPC-UA connection status
- Verify tag browse path matches server nodes
- Check subscription quality in tag diagnostics
- Review tag quality indicators in Designer

### TimeBaseDB Connection Issues

- Ensure TimeBase service is running
- Verify port 8011 is accessible
- Check JDBC driver is correctly installed
- Review database connection logs

### HMI Not Loading

- Clear browser cache
- Check project is Published
- Verify Perspective module is installed
- Check browser console for JavaScript errors

## Next Steps

- Read `HMI-Design.md` for dashboard layout details
- Review `Tag-Configuration.md` for complete tag list
- See `Integration.md` for backend synchronization
- Test all control functions before deployment
