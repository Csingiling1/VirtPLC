# Sample User Questions for AI Assistant

Test these questions in the AI chat interface to visualize your PLC data!

## Basic Queries - Latest Data

### Show Recent Readings
```
Show me the latest 50 sensor readings
```

```
What are the current sensor values?
```

```
Display the most recent data from all sensors
```

## Device-Specific Queries

### Motor Data
```
Show motor speed for the last 100 readings
```

```
Display motor temperature over time
```

```
Show me motor speed data for the last 24 hours
```

```
Create a chart of motor temperature trends
```

### Pressure and Flow
```
Show pressure readings from the last hour
```

```
Display flow rate data
```

```
Visualize pressure and flow rate trends
```

### Vibration and Power
```
Show vibration sensor data
```

```
Display power consumption over time
```

```
Create a chart showing vibration levels
```

## Time-Based Queries

### Last Hour
```
Show all sensor data from the last hour
```

```
Display temperature readings from the past hour
```

### Last 24 Hours
```
Show motor data for the last 24 hours
```

```
Visualize sensor trends over the past day
```

```
Display all readings from the last 24 hours
```

### Custom Time Ranges
```
Show sensor data from the last 6 hours
```

```
Display readings from the past 12 hours
```

## Multi-Device Comparisons

```
Compare motor speeds across all devices
```

```
Show temperature readings from all motors
```

```
Display vibration levels for all sensors
```

```
Compare power consumption between devices
```

## Specific Devices by Location

```
Show data from New York PLC devices
```

```
Display readings from PLC-NY-001
```

```
Show sensor data from Los Angeles factory
```

## Chart Type Suggestions

### Time Series (Line Charts)
```
Create a time series chart of motor speed
```

```
Show temperature trends over time
```

```
Visualize sensor data as a line chart
```

### Latest Values
```
Show current values for all sensors
```

```
Display latest readings in a chart
```

## Advanced Queries

### Multiple Sensors
```
Show motor speed, temperature, and vibration together
```

```
Compare speed and temperature readings
```

```
Display all motor-related sensors
```

### Performance Monitoring
```
Show motor performance metrics
```

```
Display system health indicators
```

```
Visualize operational parameters
```

## Quick Tests

Use these to quickly test if the AI is working:

1. **Simple**: `Show latest sensor data`
2. **Medium**: `Display motor temperature for the last 100 readings`
3. **Complex**: `Compare motor speeds across all devices over the last 24 hours`

## Expected Behavior

When you send these queries, the AI will:
1. 🤔 Analyze what data you need
2. 📊 Fetch real data from the database
3. 🎨 Generate a React visualization
4. 📈 Display an interactive chart

All charts will include:
- Real-time data from your PLC systems
- Multiple devices on separate colored lines
- Interactive tooltips
- Timestamp formatting
- Legends for device identification

## Tips for Best Results

- **Be specific**: "Show motor speed" works better than just "show data"
- **Include time ranges**: "last 100 readings" or "last 24 hours"
- **Name the sensor**: "motor temperature", "vibration", "pressure"
- **Multiple sensors**: You can ask for several at once

## Example Conversation

**You**: Show motor speed for the last 50 readings

**AI**: [Fetches data and generates chart showing motor speed over time with multiple device lines]

**You**: Now show temperature too

**AI**: [Generates chart with both motor speed and temperature data]
