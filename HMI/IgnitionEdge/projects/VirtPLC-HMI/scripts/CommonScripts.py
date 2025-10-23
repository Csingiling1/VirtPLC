"""
Common utility scripts for VirtPLC HMI
"""

def getTagValue(tagPath):
    """
    Safely read a tag value with error handling
    
    Args:
        tagPath: Full tag path including provider (e.g., "[default]Motor1/Speed")
        
    Returns:
        Tag value or None if error
    """
    try:
        return system.tag.readBlocking([tagPath])[0].value
    except Exception as e:
        system.util.getLogger("CommonScripts").error("Error reading tag %s: %s" % (tagPath, str(e)))
        return None


def setTagValue(tagPath, value):
    """
    Safely write a tag value with error handling
    
    Args:
        tagPath: Full tag path including provider
        value: Value to write
        
    Returns:
        True if successful, False otherwise
    """
    try:
        system.tag.writeBlocking([tagPath], [value])
        return True
    except Exception as e:
        system.util.getLogger("CommonScripts").error("Error writing tag %s: %s" % (tagPath, str(e)))
        return False


def navigateToView(viewPath):
    """
    Navigate to a specific view with error handling
    
    Args:
        viewPath: Path to the view to navigate to
    """
    try:
        system.perspective.navigate(viewPath)
    except Exception as e:
        system.util.getLogger("CommonScripts").error("Error navigating to view %s: %s" % (viewPath, str(e)))


def showNotification(title, message, level="info"):
    """
    Display a notification to the user
    
    Args:
        title: Notification title
        message: Notification message
        level: Notification level (info, warn, error, success)
    """
    try:
        system.perspective.sendMessage(
            "notify",
            {
                "title": title,
                "message": message,
                "level": level
            }
        )
    except Exception as e:
        system.util.getLogger("CommonScripts").error("Error showing notification: %s" % str(e))


def formatTimestamp(timestamp, format="yyyy-MM-dd HH:mm:ss"):
    """
    Format a timestamp to a readable string
    
    Args:
        timestamp: Timestamp object
        format: Format string
        
    Returns:
        Formatted string
    """
    try:
        return system.date.format(timestamp, format)
    except Exception as e:
        system.util.getLogger("CommonScripts").error("Error formatting timestamp: %s" % str(e))
        return str(timestamp)
