#!/usr/bin/env python3
"""
VirtPLC Enhanced Simulator

A comprehensive factory simulation tool that can run as:
- CLI tool for device management and simulation
- Web server for REST API and monitoring
- OPC-UA server for industrial protocols

Features:
- CRUD operations for factory devices
- Configurable signal generators (uniform, normal, exponential, etc.)
- File-based persistence
- REST API for integration with HMI and Spring backend
- OPC-UA server for industrial communication
"""

import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from database import DeviceDatabase
from models import FactoryDevice, SignalConfig, SignalGenerator
from web_api import create_app
from opcua_server import OPCUAServer
from interactive_cli import InteractiveCLI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimulatorApp:
    """Main simulator application"""

    def __init__(self, db_path: str = "devices.json"):
        self.db = DeviceDatabase(db_path)
        self.opcua_server: Optional[OPCUAServer] = None
        self.web_app = None
        self.running = False

    async def start_opcua_server(self, endpoint: str = "opc.tcp://0.0.0.0:4840/virtplc/"):
        """Start OPC-UA server"""
        self.opcua_server = OPCUAServer(self.db, endpoint)
        await self.opcua_server.start()
        logger.info(f"OPC-UA server started at {endpoint}")

    async def start_web_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start web server"""
        import uvicorn
        from uvicorn import Server, Config

        self.web_app = create_app(self.db)

        # Create uvicorn server config
        config = Config(
            app=self.web_app,
            host=host,
            port=port,
            log_level="info"
        )

        # Create and start server
        server = Server(config)
        logger.info(f"Starting web server at http://{host}:{port}")

        # Start server in background
        await server.serve()

    async def run_simulation(self, update_interval: float = 1.0):
        """Run the simulation loop"""
        self.running = True
        logger.info("Starting simulation loop...")

        try:
            while self.running:
                # Update all device signals
                self.db.update_all_signals()

                # Update OPC-UA server if running
                if self.opcua_server:
                    await self.opcua_server.update_values()

                await asyncio.sleep(update_interval)

        except KeyboardInterrupt:
            logger.info("Simulation stopped by user")
        except Exception as e:
            logger.error(f"Simulation error: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop all services"""
        self.running = False
        if self.opcua_server:
            await self.opcua_server.stop()
        logger.info("Simulator stopped")

    # Device CRUD operations
    def create_device(self, device_id: str, name: str, device_type: str = "generic",
                     description: Optional[str] = None) -> FactoryDevice:
        """Create a new device"""
        device = FactoryDevice(
            id=device_id,
            name=name,
            device_type=device_type,
            description=description
        )
        return self.db.create_device(device)

    def list_devices(self, device_type: Optional[str] = None, active_only: bool = False):
        """List devices"""
        if device_type:
            devices = self.db.get_devices_by_type(device_type)
        elif active_only:
            devices = self.db.get_active_devices()
        else:
            devices = self.db.get_all_devices()

        return devices

    def get_device(self, device_id: str) -> Optional[FactoryDevice]:
        """Get device by ID"""
        return self.db.get_device(device_id)

    def update_device(self, device_id: str, **updates) -> Optional[FactoryDevice]:
        """Update device"""
        return self.db.update_device(device_id, updates)

    def delete_device(self, device_id: str) -> bool:
        """Delete device"""
        return self.db.delete_device(device_id)

    def add_signal(self, device_id: str, name: str, unit: str, generator: str = "constant",
                   **params) -> bool:
        """Add signal to device"""
        device = self.db.get_device(device_id)
        if not device:
            return False

        signal = SignalConfig(
            name=name,
            unit=unit,
            generator=generator,
            **params
        )
        device.signals.append(signal)
        self.db._save_devices()
        return True

    def remove_signal(self, device_id: str, signal_name: str) -> bool:
        """Remove signal from device"""
        device = self.db.get_device(device_id)
        if not device:
            return False

        device.signals = [s for s in device.signals if s.name != signal_name]
        self.db._save_devices()
        return True


def create_sample_devices(app: SimulatorApp):
    """Create sample devices for testing"""
    # Motor 1
    motor1 = app.create_device("motor1", "Main Drive Motor", "motor", "Primary conveyor motor")
    app.add_signal("motor1", "speed", "RPM", "uniform", min_value=1000, max_value=1800)
    app.add_signal("motor1", "temperature", "°C", "normal", mean=45, std_dev=5)
    app.add_signal("motor1", "current", "A", "normal", mean=8.5, std_dev=1.2)
    app.add_signal("motor1", "vibration", "mm/s", "exponential", rate=0.1)

    # Motor 2
    motor2 = app.create_device("motor2", "Secondary Motor", "motor", "Backup motor system")
    app.add_signal("motor2", "speed", "RPM", "uniform", min_value=800, max_value=1500)
    app.add_signal("motor2", "temperature", "°C", "normal", mean=40, std_dev=3)
    app.add_signal("motor2", "power", "kW", "uniform", min_value=2.5, max_value=4.2)

    # Conveyor
    conveyor = app.create_device("conveyor1", "Main Conveyor", "conveyor", "Production line conveyor")
    app.add_signal("conveyor1", "speed", "m/min", "uniform", min_value=20, max_value=50)
    app.add_signal("conveyor1", "load", "%", "normal", mean=75, std_dev=10)
    app.add_signal("conveyor1", "items_per_minute", "items/min", "poisson", rate=30)

    # Temperature Sensor
    temp_sensor = app.create_device("temp_sensor1", "Oven Temperature", "sensor", "Oven temperature monitoring")
    app.add_signal("temp_sensor1", "temperature", "°C", "sinusoidal", frequency=0.001, amplitude=50, offset=200)

    # Pressure Sensor
    pressure_sensor = app.create_device("pressure_sensor1", "Hydraulic Pressure", "sensor", "Hydraulic system pressure")
    app.add_signal("pressure_sensor1", "pressure", "bar", "normal", mean=120, std_dev=5)

    logger.info("Created sample devices")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="VirtPLC Enhanced Simulator")
    parser.add_argument("--db", default="devices.json", help="Database file path")
    parser.add_argument("--mode", choices=["cli", "web", "opcua", "simulate", "interactive", "server"],
                       default="cli", help="Operation mode")
    parser.add_argument("--host", default="0.0.0.0", help="Web server host")
    parser.add_argument("--port", type=int, default=8000, help="Web server port")
    parser.add_argument("--opcua-endpoint", default="opc.tcp://0.0.0.0:4840/virtplc/",
                       help="OPC-UA server endpoint")
    parser.add_argument("--update-interval", type=float, default=1.0,
                       help="Simulation update interval in seconds")
    parser.add_argument("--create-samples", action="store_true",
                       help="Create sample devices")

    # Device management commands
    subparsers = parser.add_subparsers(dest="command", help="Device management commands")

    # Create device
    create_parser = subparsers.add_parser("create", help="Create a new device")
    create_parser.add_argument("device_id", help="Device ID")
    create_parser.add_argument("name", help="Device name")
    create_parser.add_argument("--type", default="generic", help="Device type")
    create_parser.add_argument("--description", help="Device description")

    # List devices
    list_parser = subparsers.add_parser("list", help="List devices")
    list_parser.add_argument("--type", help="Filter by device type")
    list_parser.add_argument("--active-only", action="store_true", help="Show only active devices")

    # Get device
    get_parser = subparsers.add_parser("get", help="Get device details")
    get_parser.add_argument("device_id", help="Device ID")

    # Delete device
    delete_parser = subparsers.add_parser("delete", help="Delete a device")
    delete_parser.add_argument("device_id", help="Device ID")

    # Add signal
    add_signal_parser = subparsers.add_parser("add-signal", help="Add signal to device")
    add_signal_parser.add_argument("device_id", help="Device ID")
    add_signal_parser.add_argument("signal_name", help="Signal name")
    add_signal_parser.add_argument("unit", help="Signal unit")
    add_signal_parser.add_argument("--generator", default="constant",
                                  choices=[g.value for g in SignalGenerator],
                                  help="Signal generator type")

    args = parser.parse_args()

    # Initialize app
    app = SimulatorApp(args.db)

    if args.create_samples:
        create_sample_devices(app)
        logger.info("Sample devices created")
        return

    # Handle commands
    if args.command == "create":
        try:
            device = app.create_device(args.device_id, args.name, args.type, args.description)
            print(f"Created device: {device.name} ({device.id})")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "list":
        devices = app.list_devices(args.type, args.active_only)
        if not devices:
            print("No devices found")
        else:
            for device in devices:
                status = "ACTIVE" if device.is_active else "INACTIVE"
                print(f"{device.id}: {device.name} ({device.device_type}) - {status}")

    elif args.command == "get":
        device = app.get_device(args.device_id)
        if not device:
            print(f"Device {args.device_id} not found")
            sys.exit(1)

        print(f"Device: {device.name} ({device.id})")
        print(f"Type: {device.device_type}")
        print(f"Active: {device.is_active}")
        if device.description:
            print(f"Description: {device.description}")
        print("Signals:")
        for signal in device.signals:
            print(f"  - {signal.name} ({signal.unit}): {signal.value} [{signal.generator}]")

    elif args.command == "delete":
        if app.delete_device(args.device_id):
            print(f"Deleted device: {args.device_id}")
        else:
            print(f"Device {args.device_id} not found")
            sys.exit(1)

    elif args.command == "add-signal":
        if app.add_signal(args.device_id, args.signal_name, args.unit, args.generator):
            print(f"Added signal {args.signal_name} to device {args.device_id}")
        else:
            print(f"Device {args.device_id} not found")
            sys.exit(1)

    else:
        # Run in specified mode
        if args.mode == "cli":
            print("Use --help to see available commands")
        else:
            # Run async modes
            async def run_async():
                try:
                    if args.mode == "opcua":
                        await app.start_opcua_server(args.opcua_endpoint)
                        await app.run_simulation(args.update_interval)
                    elif args.mode == "web":
                        await app.start_web_server(args.host, args.port)
                        await app.run_simulation(args.update_interval)
                    elif args.mode == "simulate":
                        await app.run_simulation(args.update_interval)
                    elif args.mode == "server":
                        # Run both web API and OPC UA servers
                        await app.start_web_server(args.host, args.port)
                        await app.start_opcua_server(args.opcua_endpoint)
                        await app.run_simulation(args.update_interval)
                    elif args.mode == "interactive":
                        # Run interactive CLI that connects to running simulator
                        cli = InteractiveCLI()
                        cli.cmdloop()
                except KeyboardInterrupt:
                    pass
                finally:
                    await app.stop()

            asyncio.run(run_async())


if __name__ == "__main__":
    main()