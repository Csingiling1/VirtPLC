# Setup Guide - Unreal Engine + Blender

## Prerequisites

### Software Requirements

1. **Unreal Engine 5.3+**
   - Download from Epic Games Launcher
   - Register for a free Epic Games account if needed

2. **Blender 4.0+**
   - Download from [blender.org](https://www.blender.org/download/)

3. **Development Tools**
   - **Windows**: Visual Studio 2022 with C++ Desktop Development workload
   - **Linux**: GCC 11+ or Clang 14+, build-essential
   - **macOS**: Xcode 14+ with Command Line Tools

4. **CMake 3.20+**
   - Required for building the OPC-UA plugin

### Library Dependencies

1. **open62541** (OPC-UA client library)
   ```bash
   # Linux (Ubuntu/Debian)
   sudo apt-get install libopen62541-1 libopen62541-dev
   
   # macOS
   brew install open62541
   
   # Windows
   # Download prebuilt binaries from https://open62541.org
   # Or build from source using CMake
   ```

## Step 1: Clone and Setup Repository

```bash
git clone <repository-url>
cd VirtPLC
git checkout feature/UEBlender
```

## Step 2: Build OPC-UA Plugin

### Linux/macOS

```bash
cd UnrealProject/Plugins/OPCUAClient
mkdir Build && cd Build
cmake ..
make
```

### Windows

```bash
cd UnrealProject\Plugins\OPCUAClient
mkdir Build && cd Build
cmake .. -G "Visual Studio 17 2022"
cmake --build . --config Release
```

## Step 3: Open Unreal Project

1. Navigate to `UnrealProject/`
2. Right-click `VirtualFactory.uproject` and select "Generate Visual Studio project files" (Windows) or "Generate Xcode project" (macOS)
3. Double-click `VirtualFactory.uproject` to open in Unreal Engine
4. If prompted, allow Unreal to rebuild missing modules

## Step 4: Configure OPC-UA Connection

1. In Unreal Editor, go to **Edit → Project Settings**
2. Search for "OPC UA"
3. Set the server endpoint: `opc.tcp://backend:4840`
4. For local testing, you can use `opc.tcp://localhost:4840`

## Step 5: Import Sample Assets

1. Open Blender
2. Load sample models from `BlenderAssets/Machines/`
3. Verify export settings:
   - Format: FBX
   - Scale: 1.0
   - Forward: -Y Forward
   - Up: Z Up
   - Apply Transform: Yes
4. Export to `BlenderAssets/Exports/`
5. In Unreal, drag FBX files from `BlenderAssets/Exports/` into Content Browser

## Step 6: Test OPC-UA Connection

1. In Unreal, open the test level: `Content/Maps/FactoryTest`
2. Play in Editor (PIE)
3. Open Output Log to see OPC-UA connection status
4. Check the debug UI widget for real-time variable values

## Troubleshooting

### Plugin fails to load
- Ensure open62541 libraries are in system PATH
- Rebuild the plugin from source
- Check Unreal Engine logs: `UnrealProject/Saved/Logs/`

### Can't connect to OPC-UA server
- Verify backend server is running
- Check firewall settings for port 4840
- Test connection with UAExpert or similar OPC-UA client

### Blender export issues
- Use Blender 4.0+ for best compatibility
- Check FBX export settings match Step 5
- Ensure mesh has no n-gons or loose vertices

## Next Steps

- Read `Development.md` for coding guidelines
- Review `OPC-UA-Schema.md` for variable definitions
- Check existing blueprints in `Content/Blueprints/`
