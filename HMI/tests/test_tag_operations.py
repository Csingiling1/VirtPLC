"""
Unit tests for HMI Tag Operations
Tests tag reading, writing, and batch operations
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add HMI scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "HMI" / "IgnitionEdge" / "projects" / "VirtPLC-HMI" / "scripts"))


class TestTagOperations:
    """Test suite for tag operations"""
    
    @pytest.fixture
    def mock_system(self):
        """Create mock system module"""
        with patch('sys.modules', {'system': Mock(), 'system.tag': Mock(), 'system.util': Mock()}):
            import system
            yield system
    
    def test_read_single_tag(self, mock_system):
        """Test reading a single tag value"""
        # Setup mock
        mock_result = Mock()
        mock_result.value = 1500.0
        mock_system.tag.readBlocking.return_value = [mock_result]
        
        # Import and test
        from TagHelper import readTagBatch
        
        result = readTagBatch(["[default]Motor1/Speed"])
        
        assert "[default]Motor1/Speed" in result
        assert result["[default]Motor1/Speed"] == 1500.0
        mock_system.tag.readBlocking.assert_called_once()
    
    def test_write_single_tag(self, mock_system):
        """Test writing a single tag value"""
        from TagHelper import writeTagBatch
        
        tag_dict = {"[default]Motor1/Run": True}
        result = writeTagBatch(tag_dict)
        
        assert result == True
        mock_system.tag.writeBlocking.assert_called_once()
    
    def test_read_multiple_tags(self, mock_system):
        """Test batch tag reading"""
        # Setup mock results
        mock_results = [
            Mock(value=1500.0),
            Mock(value=65.5),
            Mock(value=True)
        ]
        mock_system.tag.readBlocking.return_value = mock_results
        
        from TagHelper import readTagBatch
        
        tag_paths = [
            "[default]Motor1/Speed",
            "[default]Motor1/Temp",
            "[default]Motor1/Run"
        ]
        
        result = readTagBatch(tag_paths)
        
        assert len(result) == 3
        assert result["[default]Motor1/Speed"] == 1500.0
        assert result["[default]Motor1/Temp"] == 65.5
        assert result["[default]Motor1/Run"] == True


class TestMotorControl:
    """Test suite for motor control logic"""
    
    @pytest.fixture
    def mock_system(self):
        """Create mock system module"""
        with patch('sys.modules', {'system': Mock(), 'system.tag': Mock(), 'system.util': Mock()}):
            import system
            system.util.getLogger.return_value = Mock()
            yield system
    
    def test_motor_start_success(self, mock_system):
        """Test successful motor start"""
        # Setup: no fault, no e-stop
        mock_system.tag.readBlocking.side_effect = [
            [Mock(value=False)],  # Fault check
            [Mock(value=False)]   # E-stop check
        ]
        
        from TagHelper import startMotor
        
        result = startMotor("Motor1")
        
        assert result == True
        assert mock_system.tag.writeBlocking.called
    
    def test_motor_start_with_fault(self, mock_system):
        """Test motor start blocked by fault"""
        # Setup: fault active
        mock_system.tag.readBlocking.side_effect = [
            [Mock(value=True)],   # Fault active
            [Mock(value=False)]   # E-stop check
        ]
        
        from TagHelper import startMotor
        
        result = startMotor("Motor1")
        
        assert result == False
    
    def test_motor_start_with_estop(self, mock_system):
        """Test motor start blocked by emergency stop"""
        # Setup: e-stop active
        mock_system.tag.readBlocking.side_effect = [
            [Mock(value=False)],  # No fault
            [Mock(value=True)]    # E-stop active
        ]
        
        from TagHelper import startMotor
        
        result = startMotor("Motor1")
        
        assert result == False
    
    def test_motor_stop(self, mock_system):
        """Test motor stop"""
        from TagHelper import stopMotor
        
        result = stopMotor("Motor1")
        
        assert result == True
        mock_system.tag.writeBlocking.assert_called_once()
    
    def test_get_motor_status(self, mock_system):
        """Test retrieving complete motor status"""
        # Setup mock results
        mock_results = [
            Mock(value=1500.0),   # Speed
            Mock(value=65.5),     # Temp
            Mock(value=True),     # Run
            Mock(value=False),    # Fault
            Mock(value=1800.0)    # TargetSpeed
        ]
        mock_system.tag.readBlocking.return_value = mock_results
        
        from TagHelper import getMotorStatus
        
        status = getMotorStatus("Motor1")
        
        assert status is not None
        assert status["speed"] == 1500.0
        assert status["temperature"] == 65.5
        assert status["running"] == True
        assert status["fault"] == False
        assert status["targetSpeed"] == 1800.0


class TestConveyorControl:
    """Test suite for conveyor control logic"""
    
    @pytest.fixture
    def mock_system(self):
        """Create mock system module"""
        with patch('sys.modules', {'system': Mock(), 'system.tag': Mock(), 'system.util': Mock()}):
            import system
            system.util.getLogger.return_value = Mock()
            yield system
    
    def test_get_conveyor_status(self, mock_system):
        """Test retrieving conveyor status"""
        # Setup mock results
        mock_results = [
            Mock(value=50.0),     # Speed
            Mock(value=True),     # Running
            Mock(value=1250),     # ItemCount
            Mock(value=False)     # Emergency
        ]
        mock_system.tag.readBlocking.return_value = mock_results
        
        from TagHelper import getConveyorStatus
        
        status = getConveyorStatus("Conveyor1")
        
        assert status is not None
        assert status["speed"] == 50.0
        assert status["running"] == True
        assert status["itemCount"] == 1250
        assert status["emergency"] == False


class TestCommonScripts:
    """Test suite for common utility scripts"""
    
    @pytest.fixture
    def mock_system(self):
        """Create mock system module"""
        with patch('sys.modules', {'system': Mock(), 'system.tag': Mock(), 'system.util': Mock(), 'system.date': Mock()}):
            import system
            system.util.getLogger.return_value = Mock()
            yield system
    
    def test_get_tag_value(self, mock_system):
        """Test safe tag reading"""
        mock_result = Mock()
        mock_result.value = 100.0
        mock_system.tag.readBlocking.return_value = [mock_result]
        
        from CommonScripts import getTagValue
        
        value = getTagValue("[default]Motor1/Speed")
        
        assert value == 100.0
    
    def test_get_tag_value_error_handling(self, mock_system):
        """Test tag reading error handling"""
        mock_system.tag.readBlocking.side_effect = Exception("Connection failed")
        
        from CommonScripts import getTagValue
        
        value = getTagValue("[default]Motor1/Speed")
        
        assert value is None
    
    def test_set_tag_value(self, mock_system):
        """Test safe tag writing"""
        from CommonScripts import setTagValue
        
        result = setTagValue("[default]Motor1/Run", True)
        
        assert result == True
        mock_system.tag.writeBlocking.assert_called_once()
    
    def test_set_tag_value_error_handling(self, mock_system):
        """Test tag writing error handling"""
        mock_system.tag.writeBlocking.side_effect = Exception("Write failed")
        
        from CommonScripts import setTagValue
        
        result = setTagValue("[default]Motor1/Run", True)
        
        assert result == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
