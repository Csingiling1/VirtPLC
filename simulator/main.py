#!/usr/bin/env python3
"""
Simplified VirtPLC Multi-Tenant Simulator for testing collector integration
"""

import asyncio
import logging
import os
from database import MultiTenantDatabase
from web_api import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimulatorApp:
    """Simplified simulator app for multi-tenant testing"""

    def __init__(self, db_path: str = "data/tenants.json"):
        self.db = MultiTenantDatabase(db_path)
        self.web_app = None
        self._initialize_demo_data()

    def _initialize_demo_data(self):
        """Initialize demo data if database is empty"""
        if self.db.get_all_tenants():
            logger.info("Database already has data, skipping demo initialization")
            return
        
        logger.info("Initializing demo data for testing...")
        
        # Import models
        from models import Tenant, Manufacturer, Factory, PLC, Sensor
        
        # Create demo tenant
        tenant = Tenant(id="demo-tenant", name="Demo Manufacturing Corp", description="Demo tenant for testing")
        tenant = self.db.create_tenant(tenant)
        
        # Create manufacturer
        manufacturer = Manufacturer(id="demo-mfg", name="Demo Manufacturing", description="Demo manufacturer")
        tenant.manufacturers.append(manufacturer)
        
        # Create factory
        factory = Factory(id="demo-factory", name="Main Production Facility", description="Demo factory in New York, NY")
        manufacturer.factories.append(factory)
        
        # Create PLCs with sensors
        plc1 = PLC(id="PLC-001", name="Siemens S7-1500", model="Siemens S7-1500", ip_address="192.168.1.10", description="Main PLC")
        plc2 = PLC(id="PLC-002", name="Allen-Bradley ControlLogix", model="Allen-Bradley ControlLogix", ip_address="192.168.1.11", description="Backup PLC")
        factory.plcs.extend([plc1, plc2])
        
        # Add sensors to PLCs
        sensors_data = [
            ("temperature", "Temperature Sensor", "°C", 25.0, "normal", 20.0, 30.0),
            ("pressure", "Pressure Sensor", "bar", 5.0, "normal", 3.0, 7.0),
            ("flow_rate", "Flow Rate Sensor", "L/min", 100.0, "normal", 80.0, 120.0),
            ("vibration", "Vibration Sensor", "mm/s", 2.5, "normal", 1.0, 4.0),
        ]
        
        for plc in [plc1, plc2]:
            for i, (sensor_name, description, unit, value, generator, min_val, max_val) in enumerate(sensors_data):
                sensor_id = f"{sensor_name}_{plc.id}_{i}"
                sensor = Sensor(
                    id=sensor_id,
                    name=f"{description} {plc.id}",
                    description=description,
                    unit=unit,
                    value=value,
                    signal_config=SignalConfig(
                        name=sensor_name,
                        unit=unit,
                        value=value,
                        generator=generator,
                        min_value=min_val,
                        max_value=max_val
                    )
                )
                plc.sensors.append(sensor)
        
        # Save the updated tenant
        self.db._save_tenants()
        
        logger.info("Demo data initialized successfully")
        logger.info(f"Created tenant: {tenant.name} with {len(manufacturer.factories)} factories and {sum(len(plc.sensors) for plc in factory.plcs)} sensors")

    def list_devices(self, device_type=None, active_only=False):
        """Stub method for compatibility"""
        return []

    async def start_web_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start web server in background thread"""
        import threading
        import uvicorn

        self.web_app = create_app(self.db)
        
        def run_server():
            uvicorn.run(
                self.web_app,
                host=host,
                port=port,
                log_level="info"
            )
        
        # Start server in background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        logger.info(f"Web server started in background thread at http://{host}:{port}")


async def main():
    """Main entry point - simplified for multi-tenant testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VirtPLC Multi-Tenant Simulator")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--db-path", default="data/tenants.json", help="Database file path")
    # Accept old arguments for compatibility but ignore them
    parser.add_argument("--mode", default="web-only", help="Ignored for compatibility")
    parser.add_argument("--opcua-endpoint", default="", help="Ignored for compatibility")
    parser.add_argument("--update-interval", type=float, default=1.0, help="Ignored for compatibility")
    
    args = parser.parse_args()
    
    # Create app with multi-tenant database
    app = SimulatorApp(args.db_path)
    
    # Start web server only
    await app.start_web_server(args.host, args.port)
    
    logger.info("VirtPLC Multi-Tenant Simulator started!")
    logger.info(f"  - Web API: http://{args.host}:{args.port}")
    logger.info(f"  - Real-time data: http://{args.host}:{args.port}/api/stream/latest")
    
import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from database import MultiTenantDatabase
from models import Tenant, Manufacturer, Factory, PLC, Sensor, SignalConfig, SignalGenerator
from web_api import create_app
from opcua_server import OPCUAServer
from interactive_cli import InteractiveCLI
from cli_manager import DeviceCLI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimulatorApp:
    """Main simulator application"""

    def __init__(self, db_path: str = "tenants.json"):
        self.db = MultiTenantDatabase(db_path)
        self.opcua_server: Optional[OPCUAServer] = None
        self.web_app = None
        self.running = False

    def list_devices(self, device_type=None, active_only=False):
        """Stub method for compatibility - returns empty list"""
        logger.warning("list_devices called but not implemented for multi-tenant architecture")
        return []

    async def start_opcua_server(self, endpoint: str = "opc.tcp://0.0.0.0:4840/virtplc/"):
        """Start OPC-UA server"""
        print("Starting OPC-UA server")
        try:
            self.opcua_server = OPCUAServer(self.db, endpoint)
            await self.opcua_server.start()
            logger.info(f"OPC-UA server started at {endpoint}")
        except Exception as e:
            logger.error(f"Failed to start OPC-UA server: {e}")
            raise

    async def start_web_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start web server in background thread"""
        import threading
        import uvicorn

        self.web_app = create_app(self.db)
        
        def run_server():
            uvicorn.run(
                self.web_app,
                host=host,
                port=port,
                log_level="info"
            )
        
        # Start server in background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        logger.info(f"Web server started in background thread at http://{host}:{port}")
        
        # Wait a bit for server to start
        await asyncio.sleep(1)

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

    # Multi-tenant operations
    def initialize_sample_data(self):
        """Initialize sample multi-tenant data"""
        try:
            # Create sample tenant
            tenant = Tenant(
                id="tenant-demo",
                name="Demo Tenant",
                description="Sample tenant for demonstration",
                manufacturers=[
                    Manufacturer(
                        id="manufacturer-1",
                        name="Demo Manufacturer",
                        description="Sample manufacturer",
                        factories=[
                            Factory(
                                id="factory-1",
                                name="Demo Factory",
                                description="Sample factory",
                                plcs=[
                                    PLC(
                                        id="plc-1",
                                        name="Demo PLC",
                                        description="Sample PLC",
                                        sensors=[
                                            Sensor(
                                                id="temp-1",
                                                name="Temperature Sensor 1",
                                                signal_config=SignalConfig(
                                                    name="temperature",
                                                    unit="°C",
                                                    value=25.0,
                                                    generator=SignalGenerator.NORMAL.value,
                                                    mean=25.0,
                                                    std_dev=2.0
                                                )
                                            ),
                                            Sensor(
                                                id="pressure-1",
                                                name="Pressure Sensor 1",
                                                signal_config=SignalConfig(
                                                    name="pressure",
                                                    unit="bar",
                                                    value=1.0,
                                                    generator=SignalGenerator.UNIFORM.value,
                                                    min_value=0.8,
                                                    max_value=1.2
                                                )
                                            ),
                                            Sensor(
                                                id="flow-1",
                                                name="Flow Sensor 1",
                                                signal_config=SignalConfig(
                                                    name="flow_rate",
                                                    unit="L/min",
                                                    value=50.0,
                                                    generator=SignalGenerator.NORMAL.value,
                                                    mean=50.0,
                                                    std_dev=5.0
                                                )
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
            self.db.create_tenant(tenant)
            logger.info("Sample tenant data initialized")
        except ValueError:
            logger.info("Sample data already exists")

    def update_simulation(self):
        """Update all tenant signals"""
        self.db.update_all_signals()

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


async def create_sample_devices(app: SimulatorApp):
    """Create sample devices for testing"""
    logger.info("Starting to create sample devices")
    
    # Motor 1
    motor1 = await app.create_device("Motor1", "Main Drive Motor", "motor", "Primary conveyor motor")
    logger.info(f"Created Motor1: {motor1}")
    app.add_signal("Motor1", "Speed", "RPM", "uniform", min_value=1000, max_value=1800)
    app.add_signal("Motor1", "Temperature", "°C", "normal", mean=45, std_dev=5)
    app.add_signal("Motor1", "Current", "A", "normal", mean=8.5, std_dev=1.2)
    app.add_signal("Motor1", "Vibration", "mm/s", "exponential", rate=0.1)

    # Motor 2
    motor2 = await app.create_device("Motor2", "Secondary Motor", "motor", "Backup motor system")
    logger.info(f"Created Motor2: {motor2}")
    app.add_signal("Motor2", "Speed", "RPM", "uniform", min_value=800, max_value=1500)
    app.add_signal("Motor2", "Temperature", "°C", "normal", mean=40, std_dev=3)
    app.add_signal("Motor2", "Power", "kW", "uniform", min_value=2.5, max_value=4.2)

    # Conveyor
    conveyor = await app.create_device("Conveyor1", "Main Conveyor", "conveyor", "Production line conveyor")
    logger.info(f"Created Conveyor1: {conveyor}")
    app.add_signal("Conveyor1", "Speed", "m/min", "uniform", min_value=20, max_value=50)
    app.add_signal("Conveyor1", "Load", "%", "normal", mean=75, std_dev=10)
    app.add_signal("Conveyor1", "Items_per_minute", "items/min", "poisson", rate=30)

    # Temperature Sensor
    temp_sensor = await app.create_device("Sensor1", "Oven Temperature", "sensor", "Oven temperature monitoring")
    logger.info(f"Created Sensor1: {temp_sensor}")
    app.add_signal("Sensor1", "Value", "°C", "sinusoidal", frequency=0.001, amplitude=50, offset=200)

    # Pressure Sensor
    pressure_sensor = await app.create_device("Sensor2", "Hydraulic Pressure", "sensor", "Hydraulic system pressure")
    logger.info(f"Created Sensor2: {pressure_sensor}")
    app.add_signal("Sensor2", "Value", "bar", "normal", mean=120, std_dev=5)

    devices = app.list_devices()
    logger.info(f"Total devices created: {len(devices)}")
    for device in devices:
        logger.info(f"Device: {device.name} with {len(device.signals)} signals")
    
    logger.info("Created sample devices")


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="VirtPLC Enhanced Simulator")
    parser.add_argument("--db", default="tenants.json", help="Database file path")
    parser.add_argument("--mode", choices=["cli", "web", "opcua", "simulate", "interactive", "server", "plc-server"],
                       default=os.getenv("SIMULATOR_MODE", "cli"), help="Operation mode")
    parser.add_argument("--host", default=os.getenv("SIMULATOR_HOST", "0.0.0.0"), help="Web server host")
    parser.add_argument("--port", type=int, default=int(os.getenv("SIMULATOR_PORT", "8080")), help="Web server port")
    parser.add_argument("--opcua-endpoint", default=os.getenv("OPCUA_ENDPOINT", "opc.tcp://0.0.0.0:4840"),
                       help="OPC-UA server endpoint")
    parser.add_argument("--update-interval", type=float, default=float(os.getenv("UPDATE_INTERVAL", "1.0")),
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
        elif args.mode == "interactive":
            cli = InteractiveCLI(args.db)
            cli.cmdloop()
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
                    elif args.mode == "server":
                        # Create sample devices if none exist
                        devices = app.list_devices()
                        if not devices:
                            logger.info("No devices found, creating sample devices...")
                            await create_sample_devices(app)
                        
                        # Start OPC-UA server
                        await app.start_opcua_server(args.opcua_endpoint)
                        
                        # Start web server in background thread
                        await app.start_web_server(args.host, args.port)
                        
                        # Run simulation loop
                        await app.run_simulation(args.update_interval)
                    elif args.mode == "plc-server":
                        # PLC replacement server mode - optimized for Spring backend integration
                        logger.info("Starting VirtPLC as PLC replacement server...")
                        
                        # Start OPC-UA server for industrial protocols
                        await app.start_opcua_server(args.opcua_endpoint)
                        
                        # Start web server with real-time streaming
                        await app.start_web_server(args.host, args.port)
                        
                        logger.info("VirtPLC PLC Server started successfully!")
                        logger.info(f"  - Web API: http://{args.host}:{args.port}")
                        logger.info(f"  - OPC-UA: {args.opcua_endpoint}")
                        logger.info(f"  - Real-time data: http://{args.host}:{args.port}/api/stream/latest")
                        logger.info(f"  - WebSocket: ws://{args.host}:{args.port}/ws/data")
                        logger.info("  - Use 'python cli_manager.py' for device management")
                        
                        # Run simulation loop
                        await app.run_simulation(args.update_interval)
                    elif args.mode == "simulate":
                        await app.run_simulation(args.update_interval)
                except KeyboardInterrupt:
                    pass
                finally:
                    await app.stop()
            
            # Actually run the async function
            await run_async()


if __name__ == "__main__":
    asyncio.run(main())