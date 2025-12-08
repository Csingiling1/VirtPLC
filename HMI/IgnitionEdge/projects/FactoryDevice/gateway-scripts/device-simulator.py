"""
Factory Device Position Simulator Gateway Script
This script simulates device movement and updates tags in Ignition Edge
"""

import math
import time

# Configuration
TAG_PATH_PREFIX = "[default]Factory Device/"
DEVICE_ID = 1
UPDATE_INTERVAL = 1000  # milliseconds

# Simulation state
state = {
    'angle': 0.0,
    'radius': 50.0,
    'speed': 0.0,
    'active': True,
    'status': 'IDLE'
}

def updateDeviceTags():
    """Update device tags with simulated values"""
    
    # Calculate new position (circular motion)
    state['angle'] += 0.05  # Increment angle
    if state['angle'] > 2 * math.pi:
        state['angle'] = 0.0
    
    # Calculate X and Y coordinates
    center_x = 50.0
    center_y = 50.0
    x_pos = center_x + state['radius'] * math.cos(state['angle'])
    y_pos = center_y + state['radius'] * math.sin(state['angle'])
    
    # Calculate speed
    state['speed'] = state['radius'] * 0.05  # Angular velocity * radius
    
    # Determine status
    if state['speed'] > 0.1:
        state['status'] = 'MOVING'
    else:
        state['status'] = 'IDLE'
    
    # Write tags
    system.tag.writeBlocking(
        [
            TAG_PATH_PREFIX + "Device_ID",
            TAG_PATH_PREFIX + "Device_X_Position",
            TAG_PATH_PREFIX + "Device_Y_Position",
            TAG_PATH_PREFIX + "Device_Speed",
            TAG_PATH_PREFIX + "Device_Active",
            TAG_PATH_PREFIX + "Device_Status"
        ],
        [
            DEVICE_ID,
            x_pos,
            y_pos,
            state['speed'],
            state['active'],
            state['status']
        ]
    )

# Main execution - this runs every UPDATE_INTERVAL
try:
    updateDeviceTags()
except Exception as e:
    system.util.getLogger("DeviceSimulator").error("Error updating device tags: " + str(e))
