#!/usr/bin/env python3
"""
Interactive CLI for VirtPLC Simulator

A beautiful interactive command-line interface for managing
VirtPLC simulator devices with ASCII art and real-time updates.
Connects to a running simulator instance via REST API.
"""

import cmd
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from database import MultiTenantDatabase

try:
    import requests
except ImportError:
    print("❌ requests library not found. Please install with: pip install requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Less verbose for interactive mode
logger = logging.getLogger(__name__)


class SimulatorAPIClient:
    """Client for connecting to VirtPLC Simulator REST API"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10

    def _get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request"""
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request"""
        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}",
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
                f"{self.base_url}{endpoint}",
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
            response = self.session.delete(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")

    def list_devices(self) -> List[Dict[str, Any]]:
        """Get all devices"""
        return self._get("/devices")

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device by ID"""
        try:
            return self._get(f"/devices/{device_id}")
        except Exception:
            return None

    def create_device(self, device_id: str, name: str, device_type: str = "generic", description: Optional[str] = None) -> Dict[str, Any]:
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

    def add_signal(self, device_id: str, name: str, unit: str, generator: str = "constant", **params) -> Dict[str, Any]:
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

    def get_simulation_status(self) -> Dict[str, Any]:
        """Get simulation status"""
        return self._get("/simulation/status")

    def update_simulation(self) -> Dict[str, Any]:
        """Trigger simulation update"""
        return self._post("/simulation/update", {})


class InteractiveCLI(cmd.Cmd):
    """Interactive command-line interface for VirtPLC Simulator"""

    intro = """
╔══════════════════════════════════════════════════════════════╗
║                      VIRTPLC SIMULATOR                       ║
║                 Interactive Device Manager                   ║
╠══════════════════════════════════════════════════════════════╣
║  Commands: list, create, get, update, delete, add-signal     ║
║            remove-signal, status, help, quit                 ║
╚══════════════════════════════════════════════════════════════╝

Welcome to VirtPLC Interactive CLI!
Type 'help' or '?' for command list.
"""

    prompt = "virtPLC> "

    def __init__(self, db_path: str = "devices.json"):
        super().__init__()
        self.db = MultiTenantDatabase(db_path)

        # ASCII Art for different operations
        self.art = {
            "welcome": """
██╗   ██╗██╗██████╗ ████████╗██████╗ ██╗      ██████╗
██║   ██║██║██╔══██╗╚══██╔══╝██╔══██╗██║     ██╔════╝
██║   ██║██║██████╔╝   ██║   ██████╔╝██║     ██║
╚██╗ ██╔╝██║██╔══██╗   ██║   ██╔═══╝ ██║     ██║
 ╚████╔╝ ██║██║  ██║   ██║   ██║     ███████╗╚██████╗
  ╚═══╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚══════╝ ╚═════╝
            """,
            "device_created": """
╔══════════════════════════════════════╗
║           ✓ Device Created!          ║
╚══════════════════════════════════════╝
""",
            "device_deleted": """
╔══════════════════════════════════════╗
║           ✗ Device Deleted!          ║
╚══════════════════════════════════════╝
""",
            "signal_added": """
╔══════════════════════════════════════╗
║           + Signal Added!            ║
╚══════════════════════════════════════╝
""",
            "connected": """
╔══════════════════════════════════════╗
║        🔗 Connected to Simulator      ║
╚══════════════════════════════════════╝
"""
        }

    def print_art(self, art_name: str):
        """Print ASCII art for the given operation"""
        if art_name in self.art:
            print(self.art[art_name])

    def do_list(self, arg):
        """List all devices: list [type_filter]"""
        try:
            devices = self.db.get_all_devices()
            type_filter = arg.strip() if arg.strip() else None

            if type_filter:
                devices = [d for d in devices if d.device_type == type_filter]

            if not devices:
                print("📭 No devices found.")
                return

            print(f"\n📋 Found {len(devices)} device(s):")
            print("═" * 80)

            for device in devices:
                status_icon = "🟢" if device.is_active else "🔴"
                print(f"{status_icon} {device.id}")
                print(f"   Name: {device.name}")
                print(f"   Type: {device.device_type}")
                if device.description:
                    print(f"   Desc: {device.description}")
                signals = device.signals
                print(f"   Signals: {len(signals)}")
                if signals:
                    for signal in signals[:3]:  # Show first 3 signals
                        print(f"     • {signal.name}: {signal.value:.2f} {signal.unit}")
                    if len(signals) > 3:
                        print(f"     ... and {len(signals) - 3} more")
                print()

        except Exception as e:
            print(f"❌ Error listing devices: {e}")

    def do_create(self, arg):
        """Create a new device: create <id> <name> [type] [description]"""
        args = arg.split()
        if len(args) < 2:
            print("❌ Usage: create <id> <name> [type] [description]")
            return

        device_id = args[0]
        name = args[1]
        device_type = args[2] if len(args) > 2 else "generic"
        description = " ".join(args[3:]) if len(args) > 3 else None

        try:
            from models import FactoryDevice
            device = FactoryDevice(id=device_id, name=name, device_type=device_type, description=description)
            device = self.db.create_device(device)
            self.print_art("device_created")
            print(f"📝 Device '{device.name}' created with ID: {device.id}")
        except Exception as e:
            print(f"❌ Error creating device: {e}")

    def do_get(self, arg):
        """Get device details: get <device_id>"""
        if not arg.strip():
            print("❌ Usage: get <device_id>")
            return

        try:
            device = self.db.get_device(arg.strip())
            if not device:
                print(f"❌ Device '{arg}' not found.")
                return

            print(f"\n📋 Device Details:")
            print("═" * 50)
            print(f"ID: {device.id}")
            print(f"Name: {device.name}")
            print(f"Type: {device.device_type}")
            print(f"Active: {'Yes' if device.is_active else 'No'}")
            if device.description:
                print(f"Description: {device.description}")

            signals = device.signals
            if signals:
                print(f"\n📊 Signals ({len(signals)}):")
                for signal in signals:
                    generator_info = f" [{signal.generator}]"
                    print(f"  • {signal.name}: {signal.value:.2f} {signal.unit}{generator_info}")
            else:
                print("\n📊 No signals configured.")

        except Exception as e:
            print(f"❌ Error getting device: {e}")

    def do_update(self, arg):
        """Update device: update <id> <field> <value>"""
        args = arg.split()
        if len(args) < 3:
            print("❌ Usage: update <id> <field> <value>")
            print("   Fields: name, type, description, active")
            return

        device_id = args[0]
        field = args[1].lower()
        value = " ".join(args[2:])

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

        try:
            device = self.api.update_device(device_id, update_data)
            print(f"✅ Updated {field} for device '{device_id}'")
        except Exception as e:
            print(f"❌ Error updating device: {e}")

    def do_delete(self, arg):
        """Delete a device: delete <device_id>"""
        if not arg.strip():
            print("❌ Usage: delete <device_id>")
            return

        device_id = arg.strip()

        # Confirm deletion
        confirm = input(f"⚠️  Are you sure you want to delete '{device_id}'? (y/N): ")
        if confirm.lower() not in ("y", "yes"):
            print("❌ Deletion cancelled.")
            return

        try:
            if self.api.delete_device(device_id):
                self.print_art("device_deleted")
                print(f"🗑️  Device '{device_id}' deleted.")
            else:
                print(f"❌ Failed to delete device '{device_id}'.")
        except Exception as e:
            print(f"❌ Error deleting device: {e}")

    def do_add_signal(self, arg):
        """Add signal to device: add-signal <device_id> <name> <unit> [generator]"""
        args = arg.split()
        if len(args) < 3:
            print("❌ Usage: add-signal <device_id> <name> <unit> [generator]")
            print("   Generators: constant, uniform, normal, exponential, random")
            return

        device_id = args[0]
        signal_name = args[1]
        unit = args[2]
        generator = args[3] if len(args) > 3 else "constant"

        try:
            if self.db.add_signal(device_id, signal_name, unit, generator):
                self.print_art("signal_added")
                print(f"📊 Signal '{signal_name}' added to device '{device_id}'")
            else:
                print(f"❌ Failed to add signal. Device '{device_id}' not found.")
        except Exception as e:
            print(f"❌ Error adding signal: {e}")

    def do_remove_signal(self, arg):
        """Remove signal from device: remove-signal <device_id> <signal_name>"""
        args = arg.split()
        if len(args) < 2:
            print("❌ Usage: remove-signal <device_id> <signal_name>")
            return

        device_id = args[0]
        signal_name = args[1]

        try:
            if self.api.remove_signal(device_id, signal_name):
                print(f"🗑️  Signal '{signal_name}' removed from device '{device_id}'.")
            else:
                print(f"❌ Failed to remove signal '{signal_name}' from device '{device_id}'.")
        except Exception as e:
            print(f"❌ Error removing signal: {e}")

    def do_status(self, arg):
        """Show system status: status"""
        try:
            status = self.api.get_simulation_status()
            print(f"\n📊 System Status:")
            print("═" * 30)
            print(f"Simulator: {'Running' if status.get('running', False) else 'Stopped'}")
            print(f"Connected: {'Yes' if status.get('connected', True) else 'No'}")
            print(f"API URL: {self.api.base_url}")

            # Try to get device count
            try:
                devices = self.api.list_devices()
                print(f"Total Devices: {len(devices)}")
                active_devices = len([d for d in devices if d.get('is_active', True)])
                print(f"Active Devices: {active_devices}")
            except:
                print("Total Devices: Unable to fetch")

        except Exception as e:
            print(f"❌ Error getting status: {e}")
            print(f"API URL: {self.api.base_url} (connection failed)")

    def do_clear(self, arg):
        """Clear the screen: clear"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def do_quit(self, arg):
        """Exit the interactive CLI: quit"""
        print("👋 Goodbye!")
        return True

    def do_EOF(self, arg):
        """Handle Ctrl+D"""
        return self.do_quit(arg)

    def default(self, line):
        """Handle unknown commands"""
        print(f"❌ Unknown command: {line}")
        print("Type 'help' or '?' for available commands.")

    def emptyline(self):
        """Do nothing on empty line"""
        pass


def main():
    """Main entry point for interactive CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="VirtPLC Interactive CLI")
    parser.add_argument("--api-url", default="http://localhost:8080",
                       help="Simulator API URL (default: http://localhost:8080)")

    args = parser.parse_args()

    # Test connection
    try:
        api = SimulatorAPIClient(args.api_url)
        api.get_simulation_status()  # Test connection
        print(f"🔗 Connected to simulator at {args.api_url}")
    except Exception as e:
        print(f"❌ Cannot connect to simulator at {args.api_url}")
        print(f"   Error: {e}")
        print("   Make sure the simulator is running with web API enabled.")
        sys.exit(1)

    # Print welcome art
    cli = InteractiveCLI(args.api_url)
    cli.print_art("welcome")

    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Goodbye!")


if __name__ == "__main__":
    main()

import asyncio
import cmd
import logging
import os
import sys
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any

from database import MultiTenantDatabase
from models import SignalConfig, SignalGenerator

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Less verbose for interactive mode
logger = logging.getLogger(__name__)


class InteractiveCLI(cmd.Cmd):
    """Interactive command-line interface for VirtPLC Simulator"""

    intro = """
╔══════════════════════════════════════════════════════════════╗
║                      VIRTPLC SIMULATOR                       ║
║                 Interactive Device Manager                   ║
╠══════════════════════════════════════════════════════════════╣
║  Commands: list, create, get, update, delete, add-signal     ║
║            remove-signal, start-sim, stop-sim, help, quit    ║
╚══════════════════════════════════════════════════════════════╝

Welcome to VirtPLC Interactive CLI!
Type 'help' or '?' for command list.
"""

    prompt = "virtPLC> "

    def __init__(self, db_path: str = "devices.json"):
        super().__init__()
        self.db = MultiTenantDatabase(db_path)
        self.simulator_thread: Optional[threading.Thread] = None
        self.simulator_running = False
        self.update_interval = 1.0

        # ASCII Art for different operations
        self.art = {
            "welcome": """
██╗   ██╗██╗██████╗ ████████╗██████╗ ██╗      ██████╗
██║   ██║██║██╔══██╗╚══██╔══╝██╔══██╗██║     ██╔════╝
██║   ██║██║██████╔╝   ██║   ██████╔╝██║     ██║
╚██╗ ██╔╝██║██╔══██╗   ██║   ██╔═══╝ ██║     ██║
 ╚████╔╝ ██║██║  ██║   ██║   ██║     ███████╗╚██████╗
  ╚═══╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚══════╝ ╚═════╝
            """,
            "device_created": """
╔══════════════════════════════════════╗
║           ✓ Device Created!          ║
╚══════════════════════════════════════╝
""",
            "device_deleted": """
╔══════════════════════════════════════╗
║           ✗ Device Deleted!          ║
╚══════════════════════════════════════╝
""",
            "signal_added": """
╔══════════════════════════════════════╗
║           + Signal Added!            ║
╚══════════════════════════════════════╝
""",
            "simulator_started": """
╔══════════════════════════════════════╗
║        ▶ Simulator Started!          ║
╚══════════════════════════════════════╝
""",
            "simulator_stopped": """
╔══════════════════════════════════════╗
║        ⏹ Simulator Stopped!         ║
╚══════════════════════════════════════╝
"""
        }

    def print_art(self, art_name: str):
        """Print ASCII art for the given operation"""
        if art_name in self.art:
            print(self.art[art_name])

    def do_list(self, arg):
        """List all devices: list [type_filter]"""
        args = arg.split()
        type_filter = args[0] if args else None

        devices = self.db.list_devices()
        if type_filter:
            devices = [d for d in devices if d.device_type == type_filter]

        if not devices:
            print("📭 No devices found.")
            return

        print(f"\n📋 Found {len(devices)} device(s):")
        print("═" * 80)

        for device in devices:
            status_icon = "🟢" if device.is_active else "🔴"
            print(f"{status_icon} {device.id}")
            print(f"   Name: {device.name}")
            print(f"   Type: {device.device_type}")
            if device.description:
                print(f"   Desc: {device.description}")
            print(f"   Signals: {len(device.signals)}")
            if device.signals:
                for signal in device.signals[:3]:  # Show first 3 signals
                    print(f"     • {signal.name}: {signal.value:.2f} {signal.unit}")
                if len(device.signals) > 3:
                    print(f"     ... and {len(device.signals) - 3} more")
            print()

    def do_create(self, arg):
        """Create a new device: create <id> <name> [type] [description]"""
        args = arg.split()
        if len(args) < 2:
            print("❌ Usage: create <id> <name> [type] [description]")
            return

        device_id = args[0]
        name = args[1]
        device_type = args[2] if len(args) > 2 else "generic"
        description = " ".join(args[3:]) if len(args) > 3 else None

        try:
            device = self.db.create_device(device_id, name, device_type, description)
            self.print_art("device_created")
            print(f"📝 Device '{device.name}' created with ID: {device.id}")
        except ValueError as e:
            print(f"❌ Error: {e}")

    def do_get(self, arg):
        """Get device details: get <device_id>"""
        if not arg.strip():
            print("❌ Usage: get <device_id>")
            return

        device = self.db.get_device(arg.strip())
        if not device:
            print(f"❌ Device '{arg}' not found.")
            return

        print(f"\n📋 Device Details:")
        print("═" * 50)
        print(f"ID: {device.id}")
        print(f"Name: {device.name}")
        print(f"Type: {device.device_type}")
        print(f"Active: {'Yes' if device.is_active else 'No'}")
        if device.description:
            print(f"Description: {device.description}")
        print(f"Created: {device.created_at}")
        print(f"Updated: {device.updated_at}")

        if device.signals:
            print(f"\n📊 Signals ({len(device.signals)}):")
            for signal in device.signals:
                generator_info = f" [{signal.generator.value}]"
                print(f"  • {signal.name}: {signal.value:.2f} {signal.unit}{generator_info}")
        else:
            print("\n📊 No signals configured.")

    def do_update(self, arg):
        """Update device: update <id> <field> <value>"""
        args = arg.split()
        if len(args) < 3:
            print("❌ Usage: update <id> <field> <value>")
            print("   Fields: name, type, description, active")
            return

        device_id = args[0]
        field = args[1].lower()
        value = " ".join(args[2:])

        device = self.db.get_device(device_id)
        if not device:
            print(f"❌ Device '{device_id}' not found.")
            return

        try:
            if field == "name":
                device.name = value
            elif field == "type":
                device.device_type = value
            elif field == "description":
                device.description = value
            elif field == "active":
                device.is_active = value.lower() in ("true", "1", "yes", "on")
            else:
                print(f"❌ Unknown field: {field}")
                return

            self.db.save_devices()
            print(f"✅ Updated {field} for device '{device_id}'")
        except Exception as e:
            print(f"❌ Error updating device: {e}")

    def do_delete(self, arg):
        """Delete a device: delete <device_id>"""
        if not arg.strip():
            print("❌ Usage: delete <device_id>")
            return

        device_id = arg.strip()
        device = self.db.get_device(device_id)
        if not device:
            print(f"❌ Device '{device_id}' not found.")
            return

        # Confirm deletion
        confirm = input(f"⚠️  Are you sure you want to delete '{device.name}'? (y/N): ")
        if confirm.lower() not in ("y", "yes"):
            print("❌ Deletion cancelled.")
            return

        if self.db.delete_device(device_id):
            self.print_art("device_deleted")
            print(f"🗑️  Device '{device_id}' deleted.")
        else:
            print(f"❌ Failed to delete device '{device_id}'.")

    def do_add_signal(self, arg):
        """Add signal to device: add-signal <device_id> <name> <unit> [generator]"""
        args = arg.split()
        if len(args) < 3:
            print("❌ Usage: add-signal <device_id> <name> <unit> [generator]")
            print("   Generators: constant, uniform, normal, exponential, random")
            return

        device_id = args[0]
        signal_name = args[1]
        unit = args[2]
        generator = args[3] if len(args) > 3 else "constant"

        try:
            if self.db.add_signal(device_id, signal_name, unit, generator):
                self.print_art("signal_added")
                print(f"📊 Signal '{signal_name}' added to device '{device_id}'")
            else:
                print(f"❌ Device '{device_id}' not found.")
        except ValueError as e:
            print(f"❌ Error: {e}")

    def do_remove_signal(self, arg):
        """Remove signal from device: remove-signal <device_id> <signal_name>"""
        args = arg.split()
        if len(args) < 2:
            print("❌ Usage: remove-signal <device_id> <signal_name>")
            return

        device_id = args[0]
        signal_name = args[1]

        device = self.db.get_device(device_id)
        if not device:
            print(f"❌ Device '{device_id}' not found.")
            return

        # Find and remove the signal
        signal_to_remove = None
        for signal in device.signals:
            if signal.name == signal_name:
                signal_to_remove = signal
                break

        if not signal_to_remove:
            print(f"❌ Signal '{signal_name}' not found in device '{device_id}'.")
            return

        device.signals.remove(signal_to_remove)
        self.db.save_devices()
        print(f"🗑️  Signal '{signal_name}' removed from device '{device_id}'.")

    def do_start_sim(self, arg):
        """Start the simulator: start-sim [interval]"""
        if self.simulator_running:
            print("⚠️  Simulator is already running.")
            return

        args = arg.split()
        if args:
            try:
                self.update_interval = float(args[0])
            except ValueError:
                print("❌ Invalid interval. Using default 1.0 seconds.")
                self.update_interval = 1.0

        self.simulator_running = True
        self.simulator_thread = threading.Thread(target=self._run_simulation, daemon=True)
        self.simulator_thread.start()

        self.print_art("simulator_started")
        print(f"🔄 Simulator started with {self.update_interval}s update interval.")

    def do_stop_sim(self, arg):
        """Stop the simulator: stop-sim"""
        if not self.simulator_running:
            print("⚠️  Simulator is not running.")
            return

        self.simulator_running = False
        if self.simulator_thread:
            self.simulator_thread.join(timeout=2.0)

        self.print_art("simulator_stopped")
        print("⏹️  Simulator stopped.")

    def _run_simulation(self):
        """Run the simulation loop in a separate thread"""
        while self.simulator_running:
            try:
                # Update all device signals
                devices = self.db.list_devices()
                for device in devices:
                    if device.is_active:
                        for signal in device.signals:
                            signal.update_value()

                self.db.save_devices()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Simulation error: {e}")
                break

    def do_status(self, arg):
        """Show system status: status"""
        print(f"\n📊 System Status:")
        print("═" * 30)
        print(f"Simulator: {'Running' if self.simulator_running else 'Stopped'}")
        print(f"Update Interval: {self.update_interval}s")
        print(f"Database: {self.db.db_path}")
        print(f"Total Devices: {len(self.db.list_devices())}")

        active_devices = len([d for d in self.db.list_devices() if d.is_active])
        print(f"Active Devices: {active_devices}")

    def do_clear(self, arg):
        """Clear the screen: clear"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def do_quit(self, arg):
        """Exit the interactive CLI: quit"""
        if self.simulator_running:
            print("⚠️  Stopping simulator...")
            self.do_stop_sim("")
        print("👋 Goodbye!")
        return True

    def do_EOF(self, arg):
        """Handle Ctrl+D"""
        return self.do_quit(arg)

    def default(self, line):
        """Handle unknown commands"""
        print(f"❌ Unknown command: {line}")
        print("Type 'help' or '?' for available commands.")

    def emptyline(self):
        """Do nothing on empty line"""
        pass


def main():
    """Main entry point for interactive CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="VirtPLC Interactive CLI")
    parser.add_argument("--db", default="devices.json", help="Database file path")

    args = parser.parse_args()

    # Print welcome art
    cli = InteractiveCLI(args.db)
    cli.print_art("welcome")

    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Goodbye!")
        if cli.simulator_running:
            cli.do_stop_sim("")


if __name__ == "__main__":
    main()