#!/usr/bin/env python3
"""
Test script for VirtPLC Simulator

Tests the simulator functionality including device management, data streaming, and API endpoints.
"""

import asyncio
import json
import time
import requests
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from database import DeviceDatabase
from models import FactoryDevice, SignalConfig, SignalGenerator
from cli_manager import SimulatorManager

def test_database():
    """Test database functionality"""
    print("🧪 Testing Database...")
    
    # Create test database
    db = DeviceDatabase("test_devices.json")
    
    # Create test device
    device = FactoryDevice(
        id="TestMotor1",
        name="Test Motor",
        device_type="motor",
        description="Test motor for validation"
    )
    
    # Add signals
    device.add_signal("Speed", "RPM", SignalGenerator.UNIFORM.value, min_value=1000, max_value=1800)
    device.add_signal("Temperature", "°C", SignalGenerator.NORMAL.value, mean=45, std_dev=5)
    device.add_signal("Running", "bool", SignalGenerator.CONSTANT.value)
    
    # Save device
    created_device = db.create_device(device)
    print(f"✅ Created device: {created_device.name}")
    
    # Test retrieval
    retrieved_device = db.get_device("TestMotor1")
    assert retrieved_device is not None, "Device retrieval failed"
    print(f"✅ Retrieved device: {retrieved_device.name}")
    
    # Test signal generation
    retrieved_device.update_signals()
    print(f"✅ Generated signals: Speed={retrieved_device.get_signal_value('Speed'):.2f}")
    
    # Cleanup
    db.delete_device("TestMotor1")
    print("✅ Database test completed")

def test_api_endpoints():
    """Test API endpoints (requires running server)"""
    print("🌐 Testing API Endpoints...")
    
    manager = SimulatorManager("http://localhost:8080")
    
    try:
        # Test connection
        if not manager.test_connection():
            print("❌ Cannot connect to simulator API")
            return False
        
        print("✅ Connected to simulator API")
        
        # Test device creation
        device = manager.create_device("TestAPI1", "API Test Motor", "motor", "Test motor via API")
        print(f"✅ Created device via API: {device['name']}")
        
        # Test signal addition
        manager.add_signal("TestAPI1", "Speed", "RPM", "uniform", min_value=1000, max_value=1800)
        print("✅ Added signal via API")
        
        # Test data retrieval
        latest_data = manager.get_latest_data()
        print(f"✅ Retrieved latest data: {len(latest_data)} fields")
        
        # Test device listing
        devices = manager.list_devices()
        print(f"✅ Listed devices: {len(devices)} devices found")
        
        # Cleanup
        manager.delete_device("TestAPI1")
        print("✅ API test completed")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_signal_generators():
    """Test different signal generators"""
    print("📊 Testing Signal Generators...")
    
    db = DeviceDatabase("test_signals.json")
    
    # Create test device with different signal types
    device = FactoryDevice(
        id="SignalTest",
        name="Signal Test Device",
        device_type="test"
    )
    
    # Test different generators
    generators = [
        ("Constant", SignalGenerator.CONSTANT.value, {"value": 42.0}),
        ("Uniform", SignalGenerator.UNIFORM.value, {"min_value": 10, "max_value": 20}),
        ("Normal", SignalGenerator.NORMAL.value, {"mean": 50, "std_dev": 5}),
        ("Exponential", SignalGenerator.EXPONENTIAL.value, {"rate": 0.1}),
        ("Sinusoidal", SignalGenerator.SINUSOIDAL.value, {"frequency": 0.01, "amplitude": 10, "offset": 50}),
    ]
    
    for name, generator, params in generators:
        device.add_signal(name, "units", generator, **params)
    
    db.create_device(device)
    
    # Generate values
    for _ in range(5):
        device.update_signals()
        values = {signal.name: signal.value for signal in device.signals}
        print(f"   {values}")
    
    # Cleanup
    db.delete_device("SignalTest")
    print("✅ Signal generator test completed")

def test_web_api_models():
    """Test web API data models"""
    print("🔧 Testing Web API Models...")
    
    # Test TimeSeriesDataPoint
    from web_api import TimeSeriesDataPoint, TimeSeriesData
    
    point = TimeSeriesDataPoint(
        timestamp=int(time.time() * 1000),
        device_id="TestDevice",
        signal_name="TestSignal",
        value=42.5,
        unit="RPM"
    )
    
    assert point.device_id == "TestDevice"
    assert point.value == 42.5
    print("✅ TimeSeriesDataPoint model works")
    
    # Test TimeSeriesData
    data = TimeSeriesData(
        data_points=[point],
        total_count=1,
        start_time=int(time.time() * 1000) - 1000,
        end_time=int(time.time() * 1000)
    )
    
    assert len(data.data_points) == 1
    assert data.total_count == 1
    print("✅ TimeSeriesData model works")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting VirtPLC Simulator Tests")
    print("=" * 50)
    
    try:
        test_database()
        print()
        
        test_signal_generators()
        print()
        
        test_web_api_models()
        print()
        
        # Test API endpoints if server is running
        print("Testing API endpoints (requires running server)...")
        api_success = test_api_endpoints()
        
        print("\n" + "=" * 50)
        if api_success:
            print("🎉 All tests completed successfully!")
        else:
            print("⚠️  Some tests failed (API server may not be running)")
            print("   Start the simulator with: python start_simulator.py")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)