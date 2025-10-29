#!/usr/bin/env python3
"""
Enhanced CLI Manager for VirtPLC Simulator

A comprehensive command-line tool for managing devices, signals, and simulation.
Provides both interactive and command-line modes.
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimulatorManager:
    """Manager for interacting with VirtPLC Simulator"""
    
    def __init__(self, api_url: str = "http://localhost:8080"):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10
        
    def _get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request"""
        try:
            response = self.session.get(f"{self.api_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
    
    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request"""
        try:
            response = self.session.post(
                f"{self.api_url}{endpoint}",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
    
    def _put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request"""
        try:
            response = self.session.put(
                f"{self.api_url}{endpoint}",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
    
    def _delete(self, endpoint: str) -> bool:
        """Make DELETE request"""
        try:
            response = self.session.delete(f"{self.api_url}{endpoint}")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to simulator"""
        try:
            self._get("/simulation/status")
            return True
        except Exception:
            return False
    
    def list_devices(self, device_type: Optional[str] = None, active_only: bool = False) -> List[Dict[str, Any]]:
        """List devices"""
        params = {}
        if device_type:
            params['device_type'] = device_type
        if active_only:
            params['active_only'] = True
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        endpoint = f"/devices?{query_string}" if query_string else "/devices"
        return self._get(endpoint)
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device by ID"""
        try:
            return self._get(f"/devices/{device_id}")
        except Exception:
            return None
    
    def create_device(self, device_id: str, name: str, device_type: str = "generic", 
                     description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new device"""
        data = {
            "id": device_id,
            "name": name,
            "device_type": device_type
        }
        if description:
            data["description"] = description
        return self._post("/devices", data)
    
    def update_device(self, device_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update device"""
        return self._put(f"/devices/{device_id}", updates)
    
    def delete_device(self, device_id: str) -> bool:
        """Delete device"""
        return self._delete(f"/devices/{device_id}")
    
    def add_signal(self, device_id: str, name: str, unit: str, generator: str = "constant", 
                   **params) -> Dict[str, Any]:
        """Add signal to device"""
        data = {
            "name": name,
            "unit": unit,
            "generator": generator
        }
        data.update(params)
        return self._post(f"/devices/{device_id}/signals", data)
    
    def remove_signal(self, device_id: str, signal_name: str) -> bool:
        """Remove signal from device"""
        return self._delete(f"/devices/{device_id}/signals/{signal_name}")
    
    def get_latest_data(self) -> Dict[str, Any]:
        """Get latest simulation data"""
        return self._get("/api/stream/latest")
    
    def get_simulation_status(self) -> Dict[str, Any]:
        """Get simulation status"""
        return self._get("/simulation/status")
    
    def update_simulation(self) -> Dict[str, Any]:
        """Trigger simulation update"""
        return self._post("/simulation/update", {})


class DeviceCLI:
    """Command-line interface for device management"""
    
    def __init__(self, api_url: str = "http://localhost:8080"):
        self.manager = SimulatorManager(api_url)
        self.api_url = api_url
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_device(self, device: Dict[str, Any], detailed: bool = False):
        """Print device information"""
        status_icon = "🟢" if device.get('is_active', True) else "🔴"
        print(f"{status_icon} {device['id']}")
        print(f"   Name: {device['name']}")
        print(f"   Type: {device['device_type']}")
        if device.get('description'):
            print(f"   Description: {device['description']}")
        
        signals = device.get('signals', [])
        print(f"   Signals: {len(signals)}")
        
        if detailed and signals:
            print("   Signal Details:")
            for signal in signals:
                print(f"     • {signal['name']}: {signal['value']:.2f} {signal['unit']} [{signal['generator']}]")
    
    def list_devices(self, device_type: Optional[str] = None, active_only: bool = False, detailed: bool = False):
        """List devices command"""
        try:
            devices = self.manager.list_devices(device_type, active_only)
            
            if not devices:
                print("📭 No devices found.")
                return
            
            self.print_header(f"Devices ({len(devices)} found)")
            for device in devices:
                self.print_device(device, detailed)
                print()
                
        except Exception as e:
            print(f"❌ Error listing devices: {e}")
    
    def create_device(self, device_id: str, name: str, device_type: str = "generic", 
                     description: Optional[str] = None):
        """Create device command"""
        try:
            device = self.manager.create_device(device_id, name, device_type, description)
            print(f"✅ Device '{device['name']}' created with ID: {device['id']}")
        except Exception as e:
            print(f"❌ Error creating device: {e}")
    
    def get_device(self, device_id: str):
        """Get device command"""
        try:
            device = self.manager.get_device(device_id)
            if not device:
                print(f"❌ Device '{device_id}' not found.")
                return
            
            self.print_header(f"Device Details: {device_id}")
            self.print_device(device, detailed=True)
            
        except Exception as e:
            print(f"❌ Error getting device: {e}")
    
    def update_device(self, device_id: str, field: str, value: str):
        """Update device command"""
        try:
            # Convert field names and values
            update_data = {}
            if field == "name":
                update_data["name"] = value
            elif field == "type":
                update_data["device_type"] = value
            elif field == "description":
                update_data["description"] = value
            elif field == "active":
                update_data["is_active"] = value.lower() in ("true", "1", "yes", "on")
            else:
                print(f"❌ Unknown field: {field}")
                return
            
            device = self.manager.update_device(device_id, update_data)
            print(f"✅ Updated {field} for device '{device_id}'")
            
        except Exception as e:
            print(f"❌ Error updating device: {e}")
    
    def delete_device(self, device_id: str, force: bool = False):
        """Delete device command"""
        try:
            if not force:
                device = self.manager.get_device(device_id)
                if not device:
                    print(f"❌ Device '{device_id}' not found.")
                    return
                
                confirm = input(f"⚠️  Are you sure you want to delete '{device['name']}'? (y/N): ")
                if confirm.lower() not in ("y", "yes"):
                    print("❌ Deletion cancelled.")
                    return
            
            if self.manager.delete_device(device_id):
                print(f"✅ Device '{device_id}' deleted.")
            else:
                print(f"❌ Failed to delete device '{device_id}'.")
                
        except Exception as e:
            print(f"❌ Error deleting device: {e}")
    
    def add_signal(self, device_id: str, name: str, unit: str, generator: str = "constant", **params):
        """Add signal command"""
        try:
            result = self.manager.add_signal(device_id, name, unit, generator, **params)
            print(f"✅ Signal '{name}' added to device '{device_id}'")
        except Exception as e:
            print(f"❌ Error adding signal: {e}")
    
    def remove_signal(self, device_id: str, signal_name: str):
        """Remove signal command"""
        try:
            if self.manager.remove_signal(device_id, signal_name):
                print(f"✅ Signal '{signal_name}' removed from device '{device_id}'")
            else:
                print(f"❌ Failed to remove signal '{signal_name}' from device '{device_id}'")
        except Exception as e:
            print(f"❌ Error removing signal: {e}")
    
    def show_status(self):
        """Show simulation status"""
        try:
            status = self.manager.get_simulation_status()
            self.print_header("Simulation Status")
            print(f"Total Devices: {status['total_devices']}")
            print(f"Active Devices: {status['active_devices']}")
            print(f"Total Signals: {status['total_signals']}")
            print(f"Timestamp: {status['timestamp']}")
            
            # Show latest data
            try:
                latest_data = self.manager.get_latest_data()
                print(f"\nLatest Data:")
                print(f"  Motor1 Speed: {latest_data.get('motor1Speed', 0):.2f} RPM")
                print(f"  Motor1 Temp: {latest_data.get('motor1Temp', 0):.2f} °C")
                print(f"  Motor1 Running: {latest_data.get('motor1Run', False)}")
                print(f"  Conveyor1 Speed: {latest_data.get('conveyor1Speed', 0):.2f} m/min")
                print(f"  System Status: {latest_data.get('systemStatus', 'Unknown')}")
            except Exception as e:
                print(f"  Could not fetch latest data: {e}")
                
        except Exception as e:
            print(f"❌ Error getting status: {e}")
    
    def monitor_data(self, interval: float = 1.0, duration: Optional[float] = None):
        """Monitor real-time data"""
        try:
            start_time = time.time()
            print(f"📊 Monitoring data (interval: {interval}s)")
            print("Press Ctrl+C to stop")
            print("-" * 60)
            
            while True:
                try:
                    data = self.manager.get_latest_data()
                    timestamp = datetime.fromtimestamp(data['timestamp'] / 1000).strftime('%H:%M:%S')
                    
                    print(f"[{timestamp}] Motor1: {data.get('motor1Speed', 0):.1f}RPM "
                          f"({data.get('motor1Temp', 0):.1f}°C) | "
                          f"Conveyor1: {data.get('conveyor1Speed', 0):.1f}m/min | "
                          f"Status: {data.get('systemStatus', 'Unknown')}")
                    
                    if duration and (time.time() - start_time) >= duration:
                        break
                        
                    time.sleep(interval)
                    
                except KeyboardInterrupt:
                    print("\n👋 Monitoring stopped.")
                    break
                except Exception as e:
                    print(f"❌ Error during monitoring: {e}")
                    time.sleep(5)
                    
        except Exception as e:
            print(f"❌ Error starting monitoring: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="VirtPLC Simulator CLI Manager")
    parser.add_argument("--api-url", default="http://localhost:8080",
                       help="Simulator API URL (default: http://localhost:8080)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List devices
    list_parser = subparsers.add_parser("list", help="List devices")
    list_parser.add_argument("--type", help="Filter by device type")
    list_parser.add_argument("--active-only", action="store_true", help="Show only active devices")
    list_parser.add_argument("--detailed", action="store_true", help="Show detailed information")
    
    # Create device
    create_parser = subparsers.add_parser("create", help="Create a new device")
    create_parser.add_argument("device_id", help="Device ID")
    create_parser.add_argument("name", help="Device name")
    create_parser.add_argument("--type", default="generic", help="Device type")
    create_parser.add_argument("--description", help="Device description")
    
    # Get device
    get_parser = subparsers.add_parser("get", help="Get device details")
    get_parser.add_argument("device_id", help="Device ID")
    
    # Update device
    update_parser = subparsers.add_parser("update", help="Update device")
    update_parser.add_argument("device_id", help="Device ID")
    update_parser.add_argument("field", help="Field to update (name, type, description, active)")
    update_parser.add_argument("value", help="New value")
    
    # Delete device
    delete_parser = subparsers.add_parser("delete", help="Delete device")
    delete_parser.add_argument("device_id", help="Device ID")
    delete_parser.add_argument("--force", action="store_true", help="Skip confirmation")
    
    # Add signal
    add_signal_parser = subparsers.add_parser("add-signal", help="Add signal to device")
    add_signal_parser.add_argument("device_id", help="Device ID")
    add_signal_parser.add_argument("name", help="Signal name")
    add_signal_parser.add_argument("unit", help="Signal unit")
    add_signal_parser.add_argument("--generator", default="constant", help="Signal generator type")
    add_signal_parser.add_argument("--min-value", type=float, help="Minimum value")
    add_signal_parser.add_argument("--max-value", type=float, help="Maximum value")
    add_signal_parser.add_argument("--mean", type=float, help="Mean value (for normal distribution)")
    add_signal_parser.add_argument("--std-dev", type=float, help="Standard deviation (for normal distribution)")
    
    # Remove signal
    remove_signal_parser = subparsers.add_parser("remove-signal", help="Remove signal from device")
    remove_signal_parser.add_argument("device_id", help="Device ID")
    remove_signal_parser.add_argument("signal_name", help="Signal name")
    
    # Status
    status_parser = subparsers.add_parser("status", help="Show simulation status")
    
    # Monitor
    monitor_parser = subparsers.add_parser("monitor", help="Monitor real-time data")
    monitor_parser.add_argument("--interval", type=float, default=1.0, help="Update interval in seconds")
    monitor_parser.add_argument("--duration", type=float, help="Monitor duration in seconds")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = DeviceCLI(args.api_url)
    
    # Test connection
    if not cli.manager.test_connection():
        print(f"❌ Cannot connect to simulator at {args.api_url}")
        print("   Make sure the simulator is running with web API enabled.")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == "list":
            cli.list_devices(args.type, args.active_only, args.detailed)
        elif args.command == "create":
            cli.create_device(args.device_id, args.name, args.type, args.description)
        elif args.command == "get":
            cli.get_device(args.device_id)
        elif args.command == "update":
            cli.update_device(args.device_id, args.field, args.value)
        elif args.command == "delete":
            cli.delete_device(args.device_id, args.force)
        elif args.command == "add-signal":
            params = {}
            if args.min_value is not None:
                params['min_value'] = args.min_value
            if args.max_value is not None:
                params['max_value'] = args.max_value
            if args.mean is not None:
                params['mean'] = args.mean
            if args.std_dev is not None:
                params['std_dev'] = args.std_dev
            cli.add_signal(args.device_id, args.name, args.unit, args.generator, **params)
        elif args.command == "remove-signal":
            cli.remove_signal(args.device_id, args.signal_name)
        elif args.command == "status":
            cli.show_status()
        elif args.command == "monitor":
            cli.monitor_data(args.interval, args.duration)
            
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
