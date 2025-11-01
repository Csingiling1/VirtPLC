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
        self._add_factory_shapes()

    def _initialize_demo_data(self):
        """Initialize comprehensive demo data with multiple tenants, manufacturers, factories, and devices"""
        existing_tenants = self.db.get_all_tenants()
        
        # Only skip if we have comprehensive demo data (more than just a basic demo tenant)
        if existing_tenants and len(existing_tenants) > 1:
            logger.info("Database already has comprehensive demo data, skipping initialization")
            return
        
        # Clear existing minimal data and reinitialize with comprehensive demo data
        if existing_tenants:
            logger.info("Clearing existing minimal demo data and initializing comprehensive demo data...")
            # Clear all existing data
            self.db.tenants.clear()
            self.db.save_tenants()
        else:
            logger.info("Initializing comprehensive demo data for testing...")
        
        # Import models
        from models import Tenant, Manufacturer, Factory, PLC, Sensor
        
        # Create multiple tenants
        tenants_data = [
            {
                "id": "acme-corp",
                "name": "Acme Manufacturing Corp",
                "description": "Leading manufacturer of industrial equipment",
                "manufacturers": [
                    {
                        "id": "acme-motors",
                        "name": "Acme Motor Division",
                        "description": "High-performance motor manufacturing",
                        "factories": [
                            {
                                "id": "acme-factory-ny",
                                "name": "New York Production Facility",
                                "description": "Main production facility in NYC",
                                "location": {"x": 40.7128, "y": -74.0060, "address": "123 Industrial Blvd, NYC, NY"},
                                "plcs": [
                                    {
                                        "id": "PLC-NY-001",
                                        "name": "Siemens S7-1500 #1",
                                        "description": "Assembly line controller",
                                        "model": "Siemens S7-1500",
                                        "ip_address": "192.168.1.10",
                                        "position": {"x": 100, "y": 150},
                                        "sensors": [
                                            ("motor_speed", "Motor Speed", "RPM", 1750.0, "normal", 1700.0, 1800.0, {"mean": 1750.0, "std_dev": 25.0}),
                                            ("motor_temp", "Motor Temperature", "°C", 65.0, "normal", 50.0, 80.0, {"mean": 65.0, "std_dev": 5.0}),
                                            ("vibration", "Vibration Sensor", "mm/s", 1.2, "normal", 0.5, 2.0, {"mean": 1.2, "std_dev": 0.3}),
                                            ("power_consumption", "Power Consumption", "kW", 15.5, "uniform", 12.0, 18.0, {}),
                                        ]
                                    },
                                    {
                                        "id": "PLC-NY-002", 
                                        "name": "Allen-Bradley ControlLogix #1",
                                        "description": "Quality control station",
                                        "model": "Allen-Bradley ControlLogix",
                                        "ip_address": "192.168.1.11",
                                        "position": {"x": 300, "y": 200},
                                        "sensors": [
                                            ("pressure_main", "Main Pressure", "bar", 8.5, "normal", 7.0, 10.0, {"mean": 8.5, "std_dev": 0.8}),
                                            ("flow_rate", "Flow Rate", "L/min", 120.0, "normal", 100.0, 140.0, {"mean": 120.0, "std_dev": 10.0}),
                                            ("level_tank", "Tank Level", "%", 75.0, "uniform", 20.0, 90.0, {}),
                                            ("ph_level", "pH Level", "pH", 7.2, "normal", 6.8, 7.6, {"mean": 7.2, "std_dev": 0.2}),
                                        ]
                                    }
                                ]
                            },
                            {
                                "id": "acme-factory-la",
                                "name": "Los Angeles Assembly Plant",
                                "description": "West coast assembly facility",
                                "location": {"x": 34.0522, "y": -118.2437, "address": "456 Production Ave, LA, CA"},
                                "plcs": [
                                    {
                                        "id": "PLC-LA-001",
                                        "name": "Schneider M580 #1",
                                        "description": "Conveyor system controller",
                                        "model": "Schneider M580",
                                        "ip_address": "192.168.2.10",
                                        "position": {"x": 150, "y": 100},
                                        "sensors": [
                                            ("conveyor_speed", "Conveyor Speed", "m/min", 25.0, "uniform", 20.0, 30.0, {}),
                                            ("load_weight", "Load Weight", "kg", 45.0, "normal", 30.0, 60.0, {"mean": 45.0, "std_dev": 8.0}),
                                            ("belt_tension", "Belt Tension", "N", 850.0, "normal", 800.0, 900.0, {"mean": 850.0, "std_dev": 25.0}),
                                            ("motor_current", "Motor Current", "A", 12.5, "normal", 10.0, 15.0, {"mean": 12.5, "std_dev": 1.5}),
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "id": "tech-solutions",
                "name": "Tech Solutions Inc",
                "description": "Advanced technology manufacturing",
                "manufacturers": [
                    {
                        "id": "tech-electronics",
                        "name": "Electronics Division",
                        "description": "PCB and electronics manufacturing",
                        "factories": [
                            {
                                "id": "tech-factory-austin",
                                "name": "Austin Tech Hub",
                                "description": "R&D and production facility",
                                "location": {"x": 30.2672, "y": -97.7431, "address": "789 Innovation Dr, Austin, TX"},
                                "plcs": [
                                    {
                                        "id": "PLC-AUS-001",
                                        "name": "Beckhoff CX9020 #1",
                                        "description": "SMT line controller",
                                        "model": "Beckhoff CX9020",
                                        "ip_address": "192.168.3.10",
                                        "position": {"x": 200, "y": 180},
                                        "sensors": [
                                            ("humidity", "Humidity", "%", 45.0, "normal", 30.0, 60.0, {"mean": 45.0, "std_dev": 5.0}),
                                            ("temperature_oven", "Oven Temperature", "°C", 180.0, "normal", 170.0, 190.0, {"mean": 180.0, "std_dev": 5.0}),
                                            ("air_quality", "Air Quality", "ppm", 15.0, "exponential", None, None, {"rate": 0.1}),
                                            ("static_charge", "Static Charge", "V", 0.5, "normal", 0.0, 1.0, {"mean": 0.5, "std_dev": 0.2}),
                                        ]
                                    },
                                    {
                                        "id": "PLC-AUS-002",
                                        "name": "Omron NJ501 #1",
                                        "description": "Testing station controller",
                                        "model": "Omron NJ501",
                                        "ip_address": "192.168.3.11",
                                        "position": {"x": 400, "y": 250},
                                        "sensors": [
                                            ("resistance", "Resistance", "Ω", 1000.0, "normal", 950.0, 1050.0, {"mean": 1000.0, "std_dev": 25.0}),
                                            ("voltage", "Test Voltage", "V", 5.0, "uniform", 4.8, 5.2, {}),
                                            ("current_test", "Test Current", "mA", 50.0, "normal", 40.0, 60.0, {"mean": 50.0, "std_dev": 5.0}),
                                            ("frequency", "Signal Frequency", "MHz", 100.0, "sinusoidal", None, None, {"frequency": 0.01, "amplitude": 10.0, "offset": 100.0}),
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "id": "global-industries",
                "name": "Global Industries Ltd",
                "description": "Heavy machinery and equipment",
                "manufacturers": [
                    {
                        "id": "global-machinery",
                        "name": "Heavy Machinery Division",
                        "description": "Large-scale industrial equipment",
                        "factories": [
                            {
                                "id": "global-factory-chicago",
                                "name": "Chicago Manufacturing Complex",
                                "description": "Heavy equipment production",
                                "location": {"x": 41.8781, "y": -87.6298, "address": "321 Heavy Ind Blvd, Chicago, IL"},
                                "plcs": [
                                    {
                                        "id": "PLC-CHI-001",
                                        "name": "Mitsubishi Q Series #1",
                                        "description": "Press machine controller",
                                        "model": "Mitsubishi Q Series",
                                        "ip_address": "192.168.4.10",
                                        "position": {"x": 250, "y": 120},
                                        "sensors": [
                                            ("force_pressure", "Press Force", "tons", 500.0, "normal", 450.0, 550.0, {"mean": 500.0, "std_dev": 25.0}),
                                            ("hydraulic_pressure", "Hydraulic Pressure", "bar", 180.0, "uniform", 160.0, 200.0, {}),
                                            ("oil_temp", "Oil Temperature", "°C", 70.0, "normal", 60.0, 80.0, {"mean": 70.0, "std_dev": 5.0}),
                                            ("vibration_heavy", "Heavy Vibration", "mm/s", 8.5, "normal", 5.0, 12.0, {"mean": 8.5, "std_dev": 1.5}),
                                        ]
                                    },
                                    {
                                        "id": "PLC-CHI-002",
                                        "name": "Rockwell Automation #1",
                                        "description": "Assembly robot controller",
                                        "model": "Rockwell Automation",
                                        "ip_address": "192.168.4.11",
                                        "position": {"x": 450, "y": 300},
                                        "sensors": [
                                            ("robot_position_x", "Robot X Position", "mm", 1250.0, "uniform", 1000.0, 1500.0, {}),
                                            ("robot_position_y", "Robot Y Position", "mm", 800.0, "uniform", 500.0, 1000.0, {}),
                                            ("gripper_force", "Gripper Force", "N", 250.0, "normal", 200.0, 300.0, {"mean": 250.0, "std_dev": 20.0}),
                                            ("cycle_time", "Cycle Time", "seconds", 45.0, "normal", 40.0, 50.0, {"mean": 45.0, "std_dev": 3.0}),
                                        ]
                                    },
                                    {
                                        "id": "PLC-CHI-003",
                                        "name": "Siemens S7-300 #1",
                                        "description": "Welding station controller",
                                        "model": "Siemens S7-300",
                                        "ip_address": "192.168.4.12",
                                        "position": {"x": 600, "y": 180},
                                        "sensors": [
                                            ("weld_current", "Weld Current", "A", 150.0, "uniform", 120.0, 180.0, {}),
                                            ("weld_voltage", "Weld Voltage", "V", 25.0, "normal", 20.0, 30.0, {"mean": 25.0, "std_dev": 2.0}),
                                            ("wire_feed", "Wire Feed Rate", "m/min", 8.0, "uniform", 6.0, 10.0, {}),
                                            ("gas_flow", "Shield Gas Flow", "L/min", 18.0, "normal", 15.0, 20.0, {"mean": 18.0, "std_dev": 1.0}),
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        
        for tenant_data in tenants_data:
            tenant = Tenant(
                id=tenant_data["id"],
                name=tenant_data["name"],
                description=tenant_data["description"]
            )
            
            for m_data in tenant_data["manufacturers"]:
                manufacturer = Manufacturer(
                    id=m_data["id"],
                    name=m_data["name"],
                    description=m_data["description"]
                )
                
                for f_data in m_data["factories"]:
                    factory = Factory(
                        id=f_data["id"],
                        name=f_data["name"],
                        description=f_data["description"]
                    )
                    
                    for p_data in f_data["plcs"]:
                        plc = PLC(
                            id=p_data["id"],
                            name=p_data["name"],
                            description=p_data["description"]
                        )
                        
                        for sensor_data in p_data["sensors"]:
                            sensor_name, description, unit, value, generator, min_val, max_val, params = sensor_data
                            
                            sensor_config = SignalConfig(
                                name=sensor_name,
                                unit=unit,
                                value=value,
                                generator=generator,
                                **params
                            )
                            
                            sensor = Sensor(
                                id=f"{sensor_name}_{p_data['id']}",
                                name=description,
                                signal_config=sensor_config
                            )
                            plc.sensors.append(sensor)
                        
                        factory.plcs.append(plc)
                    
                    manufacturer.factories.append(factory)
                
                tenant.manufacturers.append(manufacturer)
            
            self.db.create_tenant(tenant)
        
        logger.info("Comprehensive demo data initialized successfully")
        total_tenants = len(tenants_data)
        total_manufacturers = sum(len(t["manufacturers"]) for t in tenants_data)
        total_factories = sum(len(m["factories"]) for t in tenants_data for m in t["manufacturers"])
        total_plcs = sum(len(f["plcs"]) for t in tenants_data for m in t["manufacturers"] for f in m["factories"])
        total_sensors = sum(len(p["sensors"]) for t in tenants_data for m in t["manufacturers"] for f in m["factories"] for p in f["plcs"])
        
        logger.info(f"Created {total_tenants} tenants, {total_manufacturers} manufacturers, {total_factories} factories, {total_plcs} PLCs, and {total_sensors} sensors")

    def _add_factory_shapes(self):
        """Add shapes and dimensions to factories"""
        logger.info("Starting to add factory shapes...")
        tenants = self.db.get_all_tenants()
        logger.info(f"Found {len(tenants)} tenants")
        
        # Define factory shapes and colors
        factory_configs = {
            "acme-factory-ny": {"shape": "L", "width": 120, "height": 90, "width_meters": 120.0, "height_meters": 90.0, "wireframe_color": "#ef4444"},
            "acme-factory-la": {"shape": "rectangle", "width": 100, "height": 80, "width_meters": 100.0, "height_meters": 80.0, "wireframe_color": "#f59e0b"},
            "tech-factory-austin": {"shape": "I", "width": 80, "height": 120, "width_meters": 80.0, "height_meters": 120.0, "wireframe_color": "#10b981"},
            "global-factory-chicago": {"shape": "Z", "width": 150, "height": 100, "width_meters": 150.0, "height_meters": 100.0, "wireframe_color": "#8b5cf6"},
        }
        
        shapes_assigned = 0
        for tenant in tenants:
            logger.info(f"Processing tenant: {tenant.id}")
            for manufacturer in tenant.manufacturers:
                logger.info(f"Processing manufacturer: {manufacturer.id}")
                for factory in manufacturer.factories:
                    logger.info(f"Processing factory: {factory.id}")
                    if factory.id in factory_configs:
                        config = factory_configs[factory.id]
                        factory.shape = config["shape"]
                        factory.width = config["width"]
                        factory.height = config["height"]
                        factory.width_meters = config["width_meters"]
                        factory.height_meters = config["height_meters"]
                        factory.wireframe_color = config["wireframe_color"]
                        shapes_assigned += 1
                        logger.info(f"Assigned shape {config['shape']} to factory {factory.id}")
        
        # Save the updated data
        self.db.save_tenants()
        logger.info(f"Factory shapes and dimensions added for {shapes_assigned} factories")
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
        print("DEBUG: SimulatorApp __init__ called")
        self.db = MultiTenantDatabase(db_path)
        self.opcua_server: Optional[OPCUAServer] = None
        self.web_app = None
        self.running = False
        self._initialize_demo_data()
        self._add_factory_shapes()

    def list_devices(self, device_type=None, active_only=False):
        """Stub method for compatibility - returns empty list"""
        logger.warning("list_devices called but not implemented for multi-tenant architecture")
        return []

    def _initialize_demo_data(self):
        """Initialize comprehensive demo data with multiple tenants, manufacturers, factories, and devices"""
        existing_tenants = self.db.get_all_tenants()
        
        # Only skip if we have comprehensive demo data (more than just a basic demo tenant)
        if existing_tenants and len(existing_tenants) >= 3:  # We expect 3 tenants
            logger.info("Database already has comprehensive demo data, skipping initialization")
            return
        
        # Clear existing minimal data and reinitialize with comprehensive demo data
        if existing_tenants:
            logger.info("Clearing existing minimal demo data and initializing comprehensive demo data...")
            # Clear all existing data
            self.db.tenants.clear()
            self.db.save_tenants()
        else:
            logger.info("Initializing comprehensive demo data for testing...")
        
        # Import models
        from models import Tenant, Manufacturer, Factory, PLC, Sensor
        
        # Create multiple tenants
        tenants_data = [
            {
                "id": "acme-corp",
                "name": "Acme Manufacturing Corp",
                "description": "Leading manufacturer of industrial equipment",
                "manufacturers": [
                    {
                        "id": "acme-motors",
                        "name": "Acme Motor Division",
                        "description": "High-performance motor manufacturing",
                        "factories": [
                            {
                                "id": "acme-factory-ny",
                                "name": "New York Production Facility",
                                "description": "Main production facility in NYC",
                                "location": {"x": 40.7128, "y": -74.0060, "address": "123 Industrial Blvd, NYC, NY"},
                                "plcs": [
                                    {
                                        "id": "PLC-NY-001",
                                        "name": "Siemens S7-1500 #1",
                                        "description": "Assembly line controller",
                                        "model": "Siemens S7-1500",
                                        "ip_address": "192.168.1.10",
                                        "position": {"x": 100, "y": 150},
                                        "sensors": [
                                            ("motor_speed", "Motor Speed", "RPM", 1750.0, "normal", 1700.0, 1800.0, {"mean": 1750.0, "std_dev": 25.0}),
                                            ("motor_temp", "Motor Temperature", "°C", 65.0, "normal", 50.0, 80.0, {"mean": 65.0, "std_dev": 5.0}),
                                            ("vibration", "Vibration Sensor", "mm/s", 1.2, "normal", 0.5, 2.0, {"mean": 1.2, "std_dev": 0.3}),
                                            ("power_consumption", "Power Consumption", "kW", 15.5, "uniform", 12.0, 18.0, {}),
                                        ]
                                    },
                                    {
                                        "id": "PLC-NY-002", 
                                        "name": "Allen-Bradley ControlLogix #1",
                                        "description": "Quality control station",
                                        "model": "Allen-Bradley ControlLogix",
                                        "ip_address": "192.168.1.11",
                                        "position": {"x": 300, "y": 200},
                                        "sensors": [
                                            ("pressure_main", "Main Pressure", "bar", 8.5, "normal", 7.0, 10.0, {"mean": 8.5, "std_dev": 0.8}),
                                            ("flow_rate", "Flow Rate", "L/min", 120.0, "normal", 100.0, 140.0, {"mean": 120.0, "std_dev": 10.0}),
                                            ("level_tank", "Tank Level", "%", 75.0, "uniform", 20.0, 90.0, {}),
                                            ("ph_level", "pH Level", "pH", 7.2, "normal", 6.8, 7.6, {"mean": 7.2, "std_dev": 0.2}),
                                        ]
                                    }
                                ]
                            },
                            {
                                "id": "acme-factory-la",
                                "name": "Los Angeles Assembly Plant",
                                "description": "West coast assembly facility",
                                "location": {"x": 34.0522, "y": -118.2437, "address": "456 Production Ave, LA, CA"},
                                "plcs": [
                                    {
                                        "id": "PLC-LA-001",
                                        "name": "Schneider M580 #1",
                                        "description": "Conveyor system controller",
                                        "model": "Schneider M580",
                                        "ip_address": "192.168.2.10",
                                        "position": {"x": 150, "y": 100},
                                        "sensors": [
                                            ("conveyor_speed", "Conveyor Speed", "m/min", 25.0, "uniform", 20.0, 30.0, {}),
                                            ("load_weight", "Load Weight", "kg", 45.0, "normal", 30.0, 60.0, {"mean": 45.0, "std_dev": 8.0}),
                                            ("belt_tension", "Belt Tension", "N", 850.0, "normal", 800.0, 900.0, {"mean": 850.0, "std_dev": 25.0}),
                                            ("motor_current", "Motor Current", "A", 12.5, "normal", 10.0, 15.0, {"mean": 12.5, "std_dev": 1.5}),
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "id": "tech-solutions",
                "name": "Tech Solutions Inc",
                "description": "Advanced technology manufacturing",
                "manufacturers": [
                    {
                        "id": "tech-electronics",
                        "name": "Electronics Division",
                        "description": "PCB and electronics manufacturing",
                        "factories": [
                            {
                                "id": "tech-factory-austin",
                                "name": "Austin Tech Hub",
                                "description": "R&D and production facility",
                                "location": {"x": 30.2672, "y": -97.7431, "address": "789 Innovation Dr, Austin, TX"},
                                "plcs": [
                                    {
                                        "id": "PLC-AUS-001",
                                        "name": "Beckhoff CX9020 #1",
                                        "description": "SMT line controller",
                                        "model": "Beckhoff CX9020",
                                        "ip_address": "192.168.3.10",
                                        "position": {"x": 200, "y": 180},
                                        "sensors": [
                                            ("humidity", "Humidity", "%", 45.0, "normal", 30.0, 60.0, {"mean": 45.0, "std_dev": 5.0}),
                                            ("temperature_oven", "Oven Temperature", "°C", 180.0, "normal", 170.0, 190.0, {"mean": 180.0, "std_dev": 5.0}),
                                            ("air_quality", "Air Quality", "ppm", 15.0, "exponential", None, None, {"rate": 0.1}),
                                            ("static_charge", "Static Charge", "V", 0.5, "normal", 0.0, 1.0, {"mean": 0.5, "std_dev": 0.2}),
                                        ]
                                    },
                                    {
                                        "id": "PLC-AUS-002",
                                        "name": "Omron NJ501 #1",
                                        "description": "Testing station controller",
                                        "model": "Omron NJ501",
                                        "ip_address": "192.168.3.11",
                                        "position": {"x": 400, "y": 250},
                                        "sensors": [
                                            ("resistance", "Resistance", "Ω", 1000.0, "normal", 950.0, 1050.0, {"mean": 1000.0, "std_dev": 25.0}),
                                            ("voltage", "Test Voltage", "V", 5.0, "uniform", 4.8, 5.2, {}),
                                            ("current_test", "Test Current", "mA", 50.0, "normal", 40.0, 60.0, {"mean": 50.0, "std_dev": 5.0}),
                                            ("frequency", "Signal Frequency", "MHz", 100.0, "sinusoidal", None, None, {"frequency": 0.01, "amplitude": 10.0, "offset": 100.0}),
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "id": "global-industries",
                "name": "Global Industries Ltd",
                "description": "Heavy machinery and equipment",
                "manufacturers": [
                    {
                        "id": "global-machinery",
                        "name": "Heavy Machinery Division",
                        "description": "Large-scale industrial equipment",
                        "factories": [
                            {
                                "id": "global-factory-chicago",
                                "name": "Chicago Manufacturing Complex",
                                "description": "Heavy equipment production",
                                "location": {"x": 41.8781, "y": -87.6298, "address": "321 Heavy Ind Blvd, Chicago, IL"},
                                "plcs": [
                                    {
                                        "id": "PLC-CHI-001",
                                        "name": "Mitsubishi Q Series #1",
                                        "description": "Press machine controller",
                                        "model": "Mitsubishi Q Series",
                                        "ip_address": "192.168.4.10",
                                        "position": {"x": 250, "y": 120},
                                        "sensors": [
                                            ("force_pressure", "Press Force", "tons", 500.0, "normal", 450.0, 550.0, {"mean": 500.0, "std_dev": 25.0}),
                                            ("hydraulic_pressure", "Hydraulic Pressure", "bar", 180.0, "uniform", 160.0, 200.0, {}),
                                            ("oil_temp", "Oil Temperature", "°C", 70.0, "normal", 60.0, 80.0, {"mean": 70.0, "std_dev": 5.0}),
                                            ("vibration_heavy", "Heavy Vibration", "mm/s", 8.5, "normal", 5.0, 12.0, {"mean": 8.5, "std_dev": 1.5}),
                                        ]
                                    },
                                    {
                                        "id": "PLC-CHI-002",
                                        "name": "Rockwell Automation #1",
                                        "description": "Assembly robot controller",
                                        "model": "Rockwell Automation",
                                        "ip_address": "192.168.4.11",
                                        "position": {"x": 450, "y": 300},
                                        "sensors": [
                                            ("robot_position_x", "Robot X Position", "mm", 1250.0, "uniform", 1000.0, 1500.0, {}),
                                            ("robot_position_y", "Robot Y Position", "mm", 800.0, "uniform", 500.0, 1000.0, {}),
                                            ("gripper_force", "Gripper Force", "N", 250.0, "normal", 200.0, 300.0, {"mean": 250.0, "std_dev": 20.0}),
                                            ("cycle_time", "Cycle Time", "seconds", 45.0, "normal", 40.0, 50.0, {"mean": 45.0, "std_dev": 3.0}),
                                        ]
                                    },
                                    {
                                        "id": "PLC-CHI-003",
                                        "name": "Siemens S7-300 #1",
                                        "description": "Welding station controller",
                                        "model": "Siemens S7-300",
                                        "ip_address": "192.168.4.12",
                                        "position": {"x": 600, "y": 180},
                                        "sensors": [
                                            ("weld_current", "Weld Current", "A", 150.0, "uniform", 120.0, 180.0, {}),
                                            ("weld_voltage", "Weld Voltage", "V", 25.0, "normal", 20.0, 30.0, {"mean": 25.0, "std_dev": 2.0}),
                                            ("wire_feed", "Wire Feed Rate", "m/min", 8.0, "uniform", 6.0, 10.0, {}),
                                            ("gas_flow", "Shield Gas Flow", "L/min", 18.0, "normal", 15.0, 20.0, {"mean": 18.0, "std_dev": 1.0}),
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        
        for tenant_data in tenants_data:
            tenant = Tenant(
                id=tenant_data["id"],
                name=tenant_data["name"],
                description=tenant_data["description"]
            )
            
            for m_data in tenant_data["manufacturers"]:
                manufacturer = Manufacturer(
                    id=m_data["id"],
                    name=m_data["name"],
                    description=m_data["description"]
                )
                
                for f_data in m_data["factories"]:
                    factory = Factory(
                        id=f_data["id"],
                        name=f_data["name"],
                        description=f_data["description"]
                    )
                    
                    for p_data in f_data["plcs"]:
                        plc = PLC(
                            id=p_data["id"],
                            name=p_data["name"],
                            description=p_data["description"]
                        )
                        
                        for sensor_data in p_data["sensors"]:
                            sensor_name, description, unit, value, generator, min_val, max_val, params = sensor_data
                            
                            sensor_config = SignalConfig(
                                name=sensor_name,
                                unit=unit,
                                value=value,
                                generator=generator,
                                **params
                            )
                            
                            sensor = Sensor(
                                id=f"{sensor_name}_{p_data['id']}",
                                name=description,
                                signal_config=sensor_config
                            )
                            plc.sensors.append(sensor)
                        
                        factory.plcs.append(plc)
                    
                    manufacturer.factories.append(factory)
                
                tenant.manufacturers.append(manufacturer)
            
            self.db.create_tenant(tenant)
        
        logger.info("Comprehensive demo data initialized successfully")
        total_tenants = len(tenants_data)
        total_manufacturers = sum(len(t["manufacturers"]) for t in tenants_data)
        total_factories = sum(len(m["factories"]) for t in tenants_data for m in t["manufacturers"])
        total_plcs = sum(len(f["plcs"]) for t in tenants_data for m in t["manufacturers"] for f in m["factories"])
        total_sensors = sum(len(p["sensors"]) for t in tenants_data for m in t["manufacturers"] for f in m["factories"] for p in f["plcs"])
        
        logger.info(f"Created {total_tenants} tenants, {total_manufacturers} manufacturers, {total_factories} factories, {total_plcs} PLCs, and {total_sensors} sensors")

    def _add_factory_shapes(self):
        """Add shapes and dimensions to factories"""
        logger.info("Starting to add factory shapes...")
        tenants = self.db.get_all_tenants()
        logger.info(f"Found {len(tenants)} tenants")
        
        # Define factory shapes and colors
        factory_configs = {
            "acme-factory-ny": {"shape": "L", "width": 120, "height": 90, "width_meters": 120.0, "height_meters": 90.0, "wireframe_color": "#ef4444"},
            "acme-factory-la": {"shape": "rectangle", "width": 100, "height": 80, "width_meters": 100.0, "height_meters": 80.0, "wireframe_color": "#f59e0b"},
            "tech-factory-austin": {"shape": "I", "width": 80, "height": 120, "width_meters": 80.0, "height_meters": 120.0, "wireframe_color": "#10b981"},
            "global-factory-chicago": {"shape": "Z", "width": 150, "height": 100, "width_meters": 150.0, "height_meters": 100.0, "wireframe_color": "#8b5cf6"},
        }
        
        shapes_assigned = 0
        for tenant in tenants:
            logger.info(f"Processing tenant: {tenant.id}")
            for manufacturer in tenant.manufacturers:
                logger.info(f"Processing manufacturer: {manufacturer.id}")
                for factory in manufacturer.factories:
                    logger.info(f"Processing factory: {factory.id}")
                    if factory.id in factory_configs:
                        config = factory_configs[factory.id]
                        factory.shape = config["shape"]
                        factory.width = config["width"]
                        factory.height = config["height"]
                        factory.width_meters = config["width_meters"]
                        factory.height_meters = config["height_meters"]
                        factory.wireframe_color = config["wireframe_color"]
                        shapes_assigned += 1
                        logger.info(f"Assigned shape {config['shape']} to factory {factory.id}")
        
        # Save the updated data
        self.db._save_tenants()
        logger.info(f"Factory shapes and dimensions added for {shapes_assigned} factories")

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