"""
Tag helper utilities for batch operations and monitoring
"""

def readTagBatch(tagPaths):
    """
    Read multiple tags at once
    
    Args:
        tagPaths: List of tag paths
        
    Returns:
        Dictionary mapping tag paths to values
    """
    try:
        results = system.tag.readBlocking(tagPaths)
        return {path: result.value for path, result in zip(tagPaths, results)}
    except Exception as e:
        system.util.getLogger("TagHelper").error("Error reading tag batch: %s" % str(e))
        return {}


def writeTagBatch(tagDict):
    """
    Write multiple tags at once
    
    Args:
        tagDict: Dictionary mapping tag paths to values
        
    Returns:
        True if all successful, False otherwise
    """
    try:
        tagPaths = tagDict.keys()
        values = tagDict.values()
        system.tag.writeBlocking(tagPaths, values)
        return True
    except Exception as e:
        system.util.getLogger("TagHelper").error("Error writing tag batch: %s" % str(e))
        return False


def getMotorStatus(motorName):
    """
    Get complete status of a motor
    
    Args:
        motorName: Name of motor (e.g., "Motor1")
        
    Returns:
        Dictionary with motor status data
    """
    basePath = "[default]%s" % motorName
    tagPaths = [
        "%s/Speed" % basePath,
        "%s/Temp" % basePath,
        "%s/Run" % basePath,
        "%s/Fault" % basePath,
        "%s/TargetSpeed" % basePath
    ]
    
    try:
        results = system.tag.readBlocking(tagPaths)
        return {
            "speed": results[0].value,
            "temperature": results[1].value,
            "running": results[2].value,
            "fault": results[3].value,
            "targetSpeed": results[4].value
        }
    except Exception as e:
        system.util.getLogger("TagHelper").error("Error getting motor status: %s" % str(e))
        return None


def getConveyorStatus(conveyorName):
    """
    Get complete status of a conveyor
    
    Args:
        conveyorName: Name of conveyor (e.g., "Conveyor1")
        
    Returns:
        Dictionary with conveyor status data
    """
    basePath = "[default]%s" % conveyorName
    tagPaths = [
        "%s/Speed" % basePath,
        "%s/Running" % basePath,
        "%s/ItemCount" % basePath,
        "%s/Emergency" % basePath
    ]
    
    try:
        results = system.tag.readBlocking(tagPaths)
        return {
            "speed": results[0].value,
            "running": results[1].value,
            "itemCount": results[2].value,
            "emergency": results[3].value
        }
    except Exception as e:
        system.util.getLogger("TagHelper").error("Error getting conveyor status: %s" % str(e))
        return None


def startMotor(motorName):
    """
    Start a motor with safety checks
    
    Args:
        motorName: Name of motor
        
    Returns:
        True if started successfully
    """
    try:
        # Check for faults and emergency stop
        faultPath = "[default]%s/Fault" % motorName
        eStopPath = "[default]System/EmergencyStop"
        
        fault = system.tag.readBlocking([faultPath])[0].value
        eStop = system.tag.readBlocking([eStopPath])[0].value
        
        if fault:
            system.util.getLogger("TagHelper").warn("Cannot start %s - Fault active" % motorName)
            return False
            
        if eStop:
            system.util.getLogger("TagHelper").warn("Cannot start %s - Emergency stop active" % motorName)
            return False
        
        # Start motor
        runPath = "[default]%s/Run" % motorName
        system.tag.writeBlocking([runPath], [True])
        return True
        
    except Exception as e:
        system.util.getLogger("TagHelper").error("Error starting motor: %s" % str(e))
        return False


def stopMotor(motorName):
    """
    Stop a motor
    
    Args:
        motorName: Name of motor
        
    Returns:
        True if stopped successfully
    """
    try:
        runPath = "[default]%s/Run" % motorName
        system.tag.writeBlocking([runPath], [False])
        return True
    except Exception as e:
        system.util.getLogger("TagHelper").error("Error stopping motor: %s" % str(e))
        return False
