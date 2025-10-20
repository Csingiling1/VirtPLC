# Development Guidelines

## Code Organization

### C++ Code Structure

```
Source/VirtualFactory/
├── Public/
│   ├── VirtualFactoryGameMode.h
│   ├── Equipment/
│   │   ├── MotorActor.h
│   │   ├── ConveyorActor.h
│   │   └── SensorActor.h
│   └── OPC/
│       ├── OPCUAManager.h
│       └── OPCUADataTypes.h
└── Private/
    ├── VirtualFactoryGameMode.cpp
    ├── Equipment/
    │   ├── MotorActor.cpp
    │   ├── ConveyorActor.cpp
    │   └── SensorActor.cpp
    └── OPC/
        ├── OPCUAManager.cpp
        └── OPCUADataTypes.cpp
```

### Blueprint Organization

```
Content/
├── Blueprints/
│   ├── Equipment/
│   │   ├── BP_Motor
│   │   ├── BP_Conveyor
│   │   └── BP_Sensor
│   ├── UI/
│   │   ├── WBP_DebugPanel
│   │   └── WBP_OPCStatus
│   └── Core/
│       └── BP_FactoryGameMode
├── Maps/
│   ├── FactoryTest.umap
│   └── MainFactory.umap
├── Materials/
│   └── Equipment/
└── Meshes/
    └── Imported/
```

## Coding Standards

### C++ Guidelines

1. **Naming Conventions**
   - Classes: `PascalCase` with appropriate prefix (A for Actor, U for Object)
   - Functions: `PascalCase`
   - Variables: `camelCase`
   - Member variables: `camelCase` or use `m_` prefix
   - Constants: `UPPER_SNAKE_CASE`

2. **Header Guards**
   ```cpp
   #pragma once
   
   #include "CoreMinimal.h"
   // other includes
   #include "MotorActor.generated.h"
   ```

3. **Documentation**
   ```cpp
   /**
    * Motor actor that synchronizes with OPC-UA Motor variables
    * Updates speed and temperature in real-time
    */
   UCLASS()
   class VIRTUALFACTORY_API AMotorActor : public AActor
   {
       GENERATED_BODY()
   };
   ```

4. **OPC-UA Integration Pattern**
   ```cpp
   // Subscribe to OPC-UA variable changes
   void AMotorActor::BeginPlay()
   {
       Super::BeginPlay();
       
       if (OPCManager)
       {
           OPCManager->SubscribeToNode("Motor1.Speed", this, 
               &AMotorActor::OnSpeedChanged);
       }
   }
   
   void AMotorActor::OnSpeedChanged(float NewSpeed)
   {
       CurrentSpeed = NewSpeed;
       UpdateMotorRotation();
   }
   ```

### Blueprint Guidelines

1. **Commenting**: Add comment boxes for major logic sections
2. **Organization**: Group related nodes, use reroute nodes for clarity
3. **Event Graph**: Keep simple, delegate complex logic to functions
4. **Variables**: 
   - Use descriptive names
   - Set appropriate categories
   - Add tooltips for public variables

### Blender Asset Guidelines

1. **Polygon Count**
   - Simple props: < 1,000 triangles
   - Machinery: 2,000 - 5,000 triangles
   - Environment: < 10,000 triangles per asset

2. **Naming Convention**
   - `SM_<AssetName>` for static meshes (e.g., `SM_Motor_01`)
   - `SK_<AssetName>` for skeletal meshes
   - `T_<AssetName>` for textures

3. **Materials**
   - Use PBR workflow (Base Color, Metallic, Roughness, Normal)
   - Texture resolution: 2K max for hero assets, 1K for standard
   - Pack textures when possible (ARM: AO+Roughness+Metallic)

4. **Export Settings**
   ```
   Format: FBX 7.4 Binary
   Scale: 1.0
   Forward: -Y Forward
   Up: Z Up
   Apply: All Transforms
   Geometry: Mesh only
   Armature: Include if rigged
   ```

## OPC-UA Development

### Creating New Variables

1. Define in `OPC-UA-Schema.md`
2. Implement C++ handler:
   ```cpp
   void UOPCUAManager::CreateMotorNodes()
   {
       CreateNode("Motor1.Speed", UA_TYPES_FLOAT, true, true);
       CreateNode("Motor1.Temp", UA_TYPES_FLOAT, true, false);
   }
   ```

3. Subscribe in equipment actor:
   ```cpp
   OPCManager->SubscribeToNode("Motor1.Speed", this, &AMotorActor::OnSpeedChanged);
   ```

4. Test with debug UI widget

### Testing OPC-UA Communication

1. Use the debug widget (`WBP_DebugPanel`)
2. Monitor Unreal Output Log for connection status
3. Test with external OPC-UA client (UAExpert recommended)
4. Verify data in backend TimeBaseDB

## Git Workflow

### Commit Messages

Follow conventional commits format:

```
feat: add conveyor belt OPC-UA integration
fix: correct motor rotation speed calculation
docs: update OPC-UA schema with new sensor
asset: add factory floor 3D model
refactor: optimize OPC-UA subscription handling
```

### Branch Strategy

- Work on `feature/UEBlender` branch
- Commit often (every significant change)
- Push to remote regularly
- Create detailed commit messages

### What to Commit

**DO commit:**
- C++ source files
- Blueprint files (.uasset)
- Configuration files
- Documentation
- Blender source files (.blend)
- FBX exports (if < 10MB)

**DON'T commit:**
- Compiled binaries (Binaries/, Intermediate/)
- Built plugins
- Large texture files (use Git LFS if needed)
- Temporary files
- User-specific settings (Saved/ folder)

## Testing Checklist

Before committing major changes:

- [ ] Project compiles without errors
- [ ] Blueprints have no errors (check Blueprint Compiler Results)
- [ ] OPC-UA connection establishes successfully
- [ ] Test data flows to/from backend
- [ ] No runtime errors in Output Log
- [ ] Debug UI shows correct values
- [ ] FPS remains above 60 in editor
- [ ] Asset import has no warnings

## Performance Guidelines

1. **Tick Functions**: Disable if not needed every frame
2. **OPC-UA Updates**: Use subscription callbacks, not polling
3. **Mesh LODs**: Create for complex machinery
4. **Materials**: Minimize texture samples, use instancing
5. **Collision**: Use simple collision shapes

## Resources

- [Unreal Engine Documentation](https://docs.unrealengine.com/)
- [open62541 Documentation](https://www.open62541.org/doc/current/)
- [OPC-UA Specification](https://opcfoundation.org/developer-tools/specifications-unified-architecture)
- [Blender FBX Export Guide](https://docs.blender.org/manual/en/latest/addons/import_export/scene_fbx.html)

## Getting Help

1. Check existing documentation in `Docs/`
2. Review OPC-UA schema for variable definitions
3. Look at example implementations in `Source/` and `Content/`
4. Ask team members on the project communication channel
