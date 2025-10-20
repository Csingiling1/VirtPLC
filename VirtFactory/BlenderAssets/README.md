# Blender Assets

This directory contains all source Blender files for the VirtPLC virtual factory.

## Directory Structure

- `Machines/` - Industrial equipment models (motors, conveyors, sensors)
- `Environment/` - Factory environment (floors, walls, structures)
- `Exports/` - FBX exports ready for Unreal Engine import

## Asset Requirements

### Modeling Guidelines

1. **Scale**: Use real-world scale (1 Blender unit = 1 meter)
2. **Origin**: Set origin to bottom-center of object
3. **Rotation**: Apply all rotations before export
4. **Normals**: Ensure all normals face outward
5. **Clean Geometry**: Remove doubles, dissolve unnecessary edges

### Polygon Budget

- Simple props: < 1,000 tris
- Machinery: 2,000 - 5,000 tris
- Large environment pieces: < 10,000 tris

### Materials and Textures

Use PBR workflow:
- Base Color
- Metallic
- Roughness
- Normal Map
- Ambient Occlusion (optional)

Texture resolutions:
- Hero assets: 2048x2048
- Standard assets: 1024x1024
- Background props: 512x512

## Export Process

### FBX Export Settings

```
Format: FBX 7.4 Binary
Scale: 1.0
Forward Axis: -Y Forward
Up Axis: Z Up

Geometry:
☑ Apply Modifiers
☑ Apply Transform
☑ Mesh
☐ Other object types (unless needed)

Armature:
☑ Include (only if asset is rigged)

Animation:
☐ Bake Animation (unless exporting animations)
```

### Export Checklist

Before exporting:
- [ ] Object is properly scaled (real-world size)
- [ ] Origin is set correctly
- [ ] All modifiers are applied
- [ ] Materials are PBR-compliant
- [ ] UVs are unwrapped without overlaps
- [ ] Normals are correct
- [ ] File is saved in appropriate subfolder
- [ ] Export settings match requirements above

## Asset Naming Convention

Format: `<Type>_<Name>_<Variant>`

Examples:
- `SM_Conveyor_01.blend` - First conveyor variant
- `SM_Motor_Industrial_A.blend` - Industrial motor variant A
- `SM_Sensor_Proximity_01.blend` - Proximity sensor
- `SM_Floor_Concrete_Large.blend` - Large concrete floor piece

## Integration with Unreal

1. Export FBX to `Exports/` folder
2. In Unreal, import from `BlenderAssets/Exports/`
3. Import destination: `Content/Meshes/Imported/`
4. Unreal import settings:
   - Combine Meshes: Yes (if multiple objects)
   - Generate Lightmap UVs: Yes
   - Import Materials: Yes
   - Import Textures: Yes

## Current Assets

### Machines
- Conveyor belt (planned)
- Industrial motor (planned)
- Proximity sensor (planned)
- Temperature sensor (planned)

### Environment
- Factory floor tiles (planned)
- Support columns (planned)
- Safety barriers (planned)

## Tips for Collaboration

1. Save often and commit Blender source files
2. Export FBX after each significant change
3. Test imports in Unreal immediately
4. Document any special requirements in asset description
5. Use consistent naming across all assets
