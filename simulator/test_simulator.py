"""
Tests for VirtPLC Enhanced Simulator
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from datetime import datetime

from .models import FactoryDevice, SignalConfig, SignalGenerator
from .database import DeviceDatabase


class TestSignalConfig:
    """Test signal configuration and generators"""

    def test_constant_generator(self):
        """Test constant signal generator"""
        signal = SignalConfig(name="test", unit="V", value=5.0, generator="constant")
        assert signal.generate_value() == 5.0

    def test_uniform_generator(self):
        """Test uniform distribution generator"""
        signal = SignalConfig(
            name="test", unit="V", generator="uniform",
            min_value=0.0, max_value=10.0
        )
        for _ in range(100):
            value = signal.generate_value()
            assert 0.0 <= value <= 10.0

    def test_normal_generator(self):
        """Test normal distribution generator"""
        signal = SignalConfig(
            name="test", unit="°C", generator="normal",
            mean=25.0, std_dev=2.0
        )
        values = [signal.generate_value() for _ in range(1000)]
        avg = sum(values) / len(values)
        assert 20.0 <= avg <= 30.0  # Rough check

    def test_exponential_generator(self):
        """Test exponential distribution generator"""
        signal = SignalConfig(
            name="test", unit="s", generator="exponential", rate=0.1
        )
        for _ in range(100):
            value = signal.generate_value()
            assert value >= 0.0

    def test_sinusoidal_generator(self):
        """Test sinusoidal generator"""
        signal = SignalConfig(
            name="test", unit="V", generator="sinusoidal",
            frequency=1.0, amplitude=5.0, offset=10.0
        )
        value = signal.generate_value()
        assert 5.0 <= value <= 15.0  # Should be within range

    def test_stopped_signal(self):
        """Test that stopped signals don't change"""
        signal = SignalConfig(name="test", unit="V", value=5.0, is_running=False)
        original_value = signal.value
        signal.generate_value()
        assert signal.value == original_value


class TestFactoryDevice:
    """Test factory device functionality"""

    def test_device_creation(self):
        """Test device creation"""
        device = FactoryDevice(id="test_device", name="Test Device")
        assert device.id == "test_device"
        assert device.name == "Test Device"
        assert device.is_active == True
        assert len(device.signals) == 0

    def test_add_signal(self):
        """Test adding signals to device"""
        device = FactoryDevice(id="test", name="Test Device")
        signal = SignalConfig(name="temp", unit="°C", value=25.0)
        device.signals.append(signal)

        assert len(device.signals) == 1
        assert device.signals[0].name == "temp"

    def test_get_signal_value(self):
        """Test getting signal values"""
        device = FactoryDevice(id="test", name="Test Device")
        signal = SignalConfig(name="temp", unit="°C", value=25.0)
        device.signals.append(signal)

        assert device.get_signal_value("temp") == 25.0
        assert device.get_signal_value("nonexistent") is None

    def test_set_signal_value(self):
        """Test setting signal values"""
        device = FactoryDevice(id="test", name="Test Device")
        signal = SignalConfig(name="temp", unit="°C", value=25.0)
        device.signals.append(signal)

        device.set_signal_value("temp", 30.0)
        assert device.get_signal_value("temp") == 30.0

    def test_update_signals(self):
        """Test updating all signals"""
        device = FactoryDevice(id="test", name="Test Device")
        signal = SignalConfig(
            name="temp", unit="°C", generator="uniform",
            min_value=20.0, max_value=30.0
        )
        device.signals.append(signal)

        original_value = signal.value
        device.update_signals()

        # Value should have changed (or at least been generated)
        assert signal.value >= 20.0 and signal.value <= 30.0

    def test_serialization(self):
        """Test device serialization"""
        device = FactoryDevice(
            id="test",
            name="Test Device",
            device_type="sensor",
            description="Test sensor"
        )
        signal = SignalConfig(name="temp", unit="°C", value=25.0)
        device.signals.append(signal)

        # Test to_dict
        data = device.to_dict()
        assert data["id"] == "test"
        assert data["name"] == "Test Device"
        assert data["device_type"] == "sensor"
        assert len(data["signals"]) == 1

        # Test from_dict
        device2 = FactoryDevice.from_dict(data)
        assert device2.id == device.id
        assert device2.name == device.name
        assert len(device2.signals) == 1


class TestDeviceDatabase:
    """Test device database functionality"""

    def setup_method(self):
        """Set up test database"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False)
        self.temp_file.close()
        self.db_path = self.temp_file.name
        self.db = DeviceDatabase(self.db_path)

    def teardown_method(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_create_device(self):
        """Test creating devices in database"""
        device = FactoryDevice(id="test1", name="Test Device 1")
        created = self.db.create_device(device)

        assert created.id == "test1"
        assert self.db.get_device("test1") is not None

    def test_create_duplicate_device(self):
        """Test creating duplicate devices raises error"""
        device1 = FactoryDevice(id="test", name="Test Device")
        device2 = FactoryDevice(id="test", name="Another Test Device")

        self.db.create_device(device1)
        with pytest.raises(ValueError):
            self.db.create_device(device2)

    def test_get_device(self):
        """Test getting devices from database"""
        device = FactoryDevice(id="test", name="Test Device")
        self.db.create_device(device)

        retrieved = self.db.get_device("test")
        assert retrieved is not None
        assert retrieved.id == "test"

        # Test non-existent device
        assert self.db.get_device("nonexistent") is None

    def test_update_device(self):
        """Test updating devices"""
        device = FactoryDevice(id="test", name="Original Name")
        self.db.create_device(device)

        updates = {"name": "Updated Name", "is_active": False}
        updated = self.db.update_device("test", updates)

        assert updated.name == "Updated Name"
        assert updated.is_active == False

    def test_delete_device(self):
        """Test deleting devices"""
        device = FactoryDevice(id="test", name="Test Device")
        self.db.create_device(device)

        assert self.db.delete_device("test") == True
        assert self.db.get_device("test") is None
        assert self.db.delete_device("nonexistent") == False

    def test_get_devices_by_type(self):
        """Test filtering devices by type"""
        device1 = FactoryDevice(id="motor1", name="Motor 1", device_type="motor")
        device2 = FactoryDevice(id="sensor1", name="Sensor 1", device_type="sensor")
        device3 = FactoryDevice(id="motor2", name="Motor 2", device_type="motor")

        self.db.create_device(device1)
        self.db.create_device(device2)
        self.db.create_device(device3)

        motors = self.db.get_devices_by_type("motor")
        assert len(motors) == 2
        assert all(d.device_type == "motor" for d in motors)

        sensors = self.db.get_devices_by_type("sensor")
        assert len(sensors) == 1
        assert sensors[0].device_type == "sensor"

    def test_get_active_devices(self):
        """Test getting active devices"""
        device1 = FactoryDevice(id="active", name="Active Device", is_active=True)
        device2 = FactoryDevice(id="inactive", name="Inactive Device", is_active=False)

        self.db.create_device(device1)
        self.db.create_device(device2)

        active = self.db.get_active_devices()
        assert len(active) == 1
        assert active[0].id == "active"

    def test_persistence(self):
        """Test data persistence across database reloads"""
        # Create device in first database instance
        device = FactoryDevice(id="persistent", name="Persistent Device")
        self.db.create_device(device)

        # Create new database instance (simulating restart)
        db2 = DeviceDatabase(self.db_path)

        # Check that device was loaded
        loaded = db2.get_device("persistent")
        assert loaded is not None
        assert loaded.name == "Persistent Device"


class TestIntegration:
    """Integration tests"""

    def setup_method(self):
        """Set up integration test"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False)
        self.temp_file.close()
        self.db_path = self.temp_file.name

    def teardown_method(self):
        """Clean up integration test"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_full_device_lifecycle(self):
        """Test complete device lifecycle"""
        db = DeviceDatabase(self.db_path)

        # Create device
        device = FactoryDevice(
            id="lifecycle_test",
            name="Lifecycle Test Device",
            device_type="test"
        )

        # Add signals
        temp_signal = SignalConfig(
            name="temperature",
            unit="°C",
            generator="normal",
            mean=25.0,
            std_dev=2.0
        )
        pressure_signal = SignalConfig(
            name="pressure",
            unit="bar",
            generator="uniform",
            min_value=1.0,
            max_value=5.0
        )

        device.signals.extend([temp_signal, pressure_signal])
        db.create_device(device)

        # Verify creation
        retrieved = db.get_device("lifecycle_test")
        assert retrieved is not None
        assert len(retrieved.signals) == 2

        # Update signals
        db.update_all_signals()

        # Update device
        db.update_device("lifecycle_test", {"name": "Updated Lifecycle Device"})

        # Verify updates
        updated = db.get_device("lifecycle_test")
        assert updated.name == "Updated Lifecycle Device"

        # Delete device
        assert db.delete_device("lifecycle_test") == True
        assert db.get_device("lifecycle_test") is None


if __name__ == "__main__":
    pytest.main([__file__])