# VirtPLC - Unreal Engine + Blender Integration

An Accenture Challenge

This branch contains the virtual factory simulation built with Unreal Engine 5 and assets created in Blender.

## Overview

The virtual factory provides real-time 3D visualization of industrial equipment with live OPC-UA data integration.

## Project Structure

```
UnrealProject/          # Unreal Engine 5 project root
├── Config/             # UE5 configuration files
├── Content/            # All UE5 content (blueprints, materials, levels)
├── Plugins/            # Custom plugins including OPC-UA client
└── Source/             # C++ source code

BlenderAssets/          # Source Blender files
├── Machines/           # Machine models (conveyor, motors, sensors)
├── Environment/        # Factory environment assets
└── Exports/            # FBX exports for UE5

Docs/                   # Documentation
├── Setup.md            # Initial setup instructions
├── OPC-UA-Schema.md    # Variable schema for backend integration
└── Development.md      # Development guidelines
```

## Requirements

- **Unreal Engine 5.3+** (or latest stable)
- **Blender 4.0+**
- **Visual Studio 2022** (for C++ compilation on Windows) or **Clang** (Linux/Mac)
- **CMake 3.20+** (for building OPC-UA plugin)
- **open62541** library (OPC-UA client implementation)

## Quick Start

1. Clone this repository and checkout this branch
2. Follow `Docs/Setup.md` for detailed setup instructions
3. Open the Unreal project: `UnrealProject/VirtualFactory.uproject`
4. Configure OPC-UA connection in project settings

## OPC-UA Integration

The project connects to the backend OPC-UA server at `opc.tcp://backend:4840`.

### Exposed Variables

See `Docs/OPC-UA-Schema.md` for the complete variable schema.

Example variables:
- `Motor1.Speed` (read/write, float)
- `Motor1.Temp` (read-only, float)
- `Motor1.Run` (read/write, boolean)
- `Conveyor1.Speed` (read/write, float)

## Development Workflow

1. Create/modify assets in Blender
2. Export to FBX format
3. Import into Unreal Content folder
4. Set up blueprints or C++ logic
5. Test OPC-UA communication
6. Commit often with clear messages

## Contributing

- Commit often with clear messages
- Keep Blender source files in `BlenderAssets/`
- Export only optimized meshes to `BlenderAssets/Exports/`
- Document any new OPC-UA variables in the schema file
