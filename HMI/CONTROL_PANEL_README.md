# VirtPLC HMI - Control Panel View

This directory contains the Ignition Edge Perspective HMI project with a comprehensive control panel for conveyor belts and machine monitoring.

## What's Included

### Control Panel View (`ControlPanel`)
A complete HMI interface featuring:

#### Two Conveyor Belt Controls
- **On/Off Toggle Buttons**: Interactive buttons to start/stop each conveyor
- **Speed Gauges**: Real-time RPM/meter-per-minute displays
- **Visual Indicators**: Color-coded status (green=running, red=stopped)
- **Speed Labels**: Numeric display of current speed values

#### Machine Control & Monitoring
- **On/Off Toggle Button**: Control machine power state
- **Status Indicators**:
  - **Is Ready**: Amber indicator when machine is prepared
  - **Is Done**: Green indicator when operation completes
- **Position Display**:
  - **X,Y Coordinate System**: Visual representation on a 2D plane
  - **Real-time Position Marker**: Red dot showing current machine position
  - **Numeric Coordinates**: Precise X,Y values in millimeters
  - **Range Display**: Shows coordinate limits (-200/+200mm X, -100/+100mm Y)

## Tag Structure

The following tags are used by the Control Panel:

### Conveyor1
- `Conveyor1/Running` (Boolean) - Conveyor power state
- `Conveyor1/Speed` (Float4) - Current speed in m/min

### Conveyor2
- `Conveyor2/Running` (Boolean) - Conveyor power state
- `Conveyor2/Speed` (Float4) - Current speed in m/min

### Machine1
- `Machine1/Running` (Boolean) - Machine power state
- `Machine1/IsReady` (Boolean) - Ready status indicator
- `Machine1/IsDone` (Boolean) - Completion status indicator
- `Machine1/PositionX` (Float4) - X coordinate in mm
- `Machine1/PositionY` (Float4) - Y coordinate in mm

## How to Import

### Method 1: Import Project
1. Open Ignition Edge Designer
2. Go to **File → Import Project**
3. Select the `VirtPLC-HMI` project folder
4. Import the project

### Method 2: Import Individual View
1. Open Ignition Edge Designer
2. Navigate to your project
3. Go to **Project Browser → Views**
4. Right-click and select **Import View**
5. Import `ControlPanel/view.json`

### Method 3: Copy View Content
1. Open the `ControlPanel/view.json` file
2. Copy the JSON content
3. In Designer, create a new view called "ControlPanel"
4. Paste the JSON into the view

## Testing the HMI

### Option 1: Manual Tag Testing
1. Import the project/tags
2. Manually set tag values in the Tag Browser
3. Open the ControlPanel view in a Perspective session
4. Toggle buttons and observe changes

### Option 2: Use Tag Simulator
1. Run the tag simulator script:
   ```bash
   cd /home/deginandor/Documents/Programming/VirtPLC/HMI
   python3 tag_simulator.py
   ```
2. The script will continuously update tag values
3. Open ControlPanel view to see real-time simulation

### Option 3: Connect to Live PLC
1. Configure your PLC to write to these tag paths
2. Ensure proper data types match
3. Test button writes back to PLC

## View Features

### Interactive Elements
- **Toggle Buttons**: Click to change conveyor/machine states
- **Real-time Updates**: All displays update automatically
- **Color Coding**:
  - Green: Running/Active/True states
  - Red: Stopped/Inactive/False states
  - Amber: Ready states
  - Gray: Default/Unknown states

### Visual Design
- **Responsive Layout**: Scales to different screen sizes
- **Professional Styling**: Clean, industrial appearance
- **Clear Labeling**: All controls clearly identified
- **Status Indicators**: Easy-to-read status displays

### Coordinate System
- **Range**: X: -200 to +200mm, Y: -100 to +100mm
- **Visual Marker**: Red dot shows current position
- **Real-time Updates**: Position updates smoothly
- **Numeric Display**: Precise coordinate values

## Customization

### Modifying Ranges
Edit the gauge properties in the view JSON:
```json
"props": {
  "max": 50,    // Change max speed
  "min": 0,     // Change min speed
  "units": "m/min"  // Change units
}
```

### Changing Colors
Update the style bindings in the view JSON:
```json
"props.style.backgroundColor": {
  "binding": {
    "config": { "path": "TagPath" },
    "transforms": [{
      "fallback": "#defaultColor",
      "input": { "value": true },
      "output": { "value": "#activeColor" },
      "type": "map"
    }]
  }
}
```

### Adding More Conveyors
1. Copy the Conveyor1 section in the JSON
2. Rename to Conveyor3
3. Update tag bindings
4. Add corresponding tags to tag-definitions.json
5. Adjust positioning

## Troubleshooting

### View Not Loading
- Check that all required tags exist
- Verify tag data types match
- Ensure proper JSON formatting

### Buttons Not Working
- Check tag write permissions
- Verify tag paths are correct
- Test tag writes manually

### Displays Not Updating
- Check tag quality in Tag Browser
- Verify binding paths
- Test with manual tag value changes

### Coordinate System Issues
- Check PositionX/PositionY tag values
- Verify they are within expected ranges
- Test with manual coordinate changes

## Integration Notes

### PLC Integration
- Map your PLC outputs to the display tags
- Map button actions to PLC inputs
- Ensure data type compatibility

### SCADA Systems
- Use MQTT or OPC-UA to connect
- Configure bidirectional communication
- Test all control loops

### Database Logging
- Configure tag history for trending
- Set up alarms for critical states
- Create reports for production data

## Files Modified/Created

- `tag-definitions.json` - Added Conveyor2 and Machine1 tags
- `project.json` - Added ControlPanel to resources
- `views/ControlPanel/view.json` - New comprehensive control view
- `tag_simulator.py` - Python script for testing tag values

## Next Steps

1. Import the project into Ignition Edge
2. Test with the tag simulator
3. Connect to your actual PLC system
4. Customize colors/ranges as needed
5. Add additional controls or displays

---

**Ready to import?** The ControlPanel view is fully self-contained and ready to use!