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
        """Load demo data from static file"""
        import json
        import os
        from models import Tenant, Manufacturer, Factory, PLC, Sensor, SignalConfig
        
        static_data_path = "static_data.json"
        if os.path.exists(static_data_path):
            logger.info(f"Loading data from {static_data_path}")
            try:
                with open(static_data_path, 'r') as f:
                    data = json.load(f)
                
                # Convert the loaded data to our model objects
                self._load_from_static_data(data)
                logger.info("Successfully loaded data from static file")
                return
            except Exception as e:
                logger.error(f"Failed to load static data: {e}")
        
        # Fallback to generating demo data if static file doesn't exist
        logger.info("Static data file not found, generating demo data...")
        self._generate_demo_data()

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
        
        # Position devices in factories that don't have positions set
        self._position_devices_in_existing_factories()
        """Stub method for compatibility"""
        return []

    def _position_devices_in_existing_factories(self):
        """Position PLCs in existing factories that have shapes but no positions"""
        logger.info("Checking and positioning devices in existing factories...")
        tenants = self.db.get_all_tenants()
        
        repositioned_count = 0
        for tenant in tenants:
            for manufacturer in tenant.manufacturers:
                for factory in manufacturer.factories:
                    if factory.shape and factory.plcs:
                        # Check if any PLC has no position (x_position == 0 and y_position == 0)
                        needs_positioning = any(
                            plc.x_position == 0 and plc.y_position == 0 
                            for plc in factory.plcs
                        )
                        
                        if needs_positioning:
                            logger.info(f"Positioning devices in factory {factory.id} with shape {factory.shape}")
                            
                            # Convert PLCs to plcs_data format for positioning
                            plcs_data = []
                            for plc in factory.plcs:
                                plc_data = {
                                    "id": plc.id,
                                    "name": plc.name,
                                    "description": plc.description,
                                    "position": {"x": plc.x_position, "y": plc.y_position},
                                    "dimensions": {"width": plc.width, "height": plc.height}
                                }
                                plcs_data.append(plc_data)
                            
                            # Position the devices
                            self._position_devices_in_factory(factory, plcs_data)
                            
                            # Update PLC positions
                            for i, plc in enumerate(factory.plcs):
                                if i < len(plcs_data):
                                    position = plcs_data[i].get("position", {"x": 0, "y": 0})
                                    plc.x_position = position["x"]
                                    plc.y_position = position["y"]
                                    dimensions = plcs_data[i].get("dimensions", {"width": 2.5, "height": 1.8})
                                    plc.width = dimensions["width"]
                                    plc.height = dimensions["height"]
                            
                            repositioned_count += 1
        
        if repositioned_count > 0:
            # Save the updated positions
            self.db._save_tenants()
            logger.info(f"Repositioned devices in {repositioned_count} factories")
        else:
            logger.info("All factories already have positioned devices")
        
    def _position_devices_in_factory(self, factory, plcs_data):
        """Position PLCs realistically within the factory based on its shape"""
        shape = factory.shape
        width_m = factory.width_meters
        height_m = factory.height_meters
        
        # Return positions in meters, not pixels - let frontend handle scaling
        positions = []
        
        if shape == "rectangle":
            # Position devices along the perimeter and interior
            num_devices = len(plcs_data)
            if num_devices == 1:
                # Center
                positions.append({"x": width_m * 0.5, "y": height_m * 0.5})
            elif num_devices == 2:
                # Two corners
                positions.append({"x": width_m * 0.2, "y": height_m * 0.2})
                positions.append({"x": width_m * 0.8, "y": height_m * 0.8})
            else:
                # Distribute around perimeter
                for i, plc_data in enumerate(plcs_data):
                    angle = (i / num_devices) * 2 * 3.14159
                    margin = 5.0  # margin in meters
                    x = margin + (width_m - 2*margin) * (0.5 + 0.4 * (i % 2 * 2 - 1) * (0.5 if i < num_devices//2 else 0.8))
                    y = margin + (height_m - 2*margin) * (i / (num_devices - 1)) if num_devices > 1 else height_m * 0.5
                    positions.append({"x": x, "y": y})
                    
        elif shape == "L":
            # L-shaped factory: long horizontal section with vertical extension
            num_devices = len(plcs_data)
            # Horizontal section (bottom)
            horiz_devices = max(1, num_devices // 2)
            # Vertical section (left side)
            vert_devices = num_devices - horiz_devices
            
            # Horizontal positions (bottom row)
            for i in range(horiz_devices):
                x = width_m * 0.1 + (width_m * 0.8) * (i / max(1, horiz_devices - 1))
                y = height_m * 0.8
                positions.append({"x": x, "y": y})
            
            # Vertical positions (left column, top part)
            for i in range(vert_devices):
                x = width_m * 0.1
                y = height_m * 0.1 + (height_m * 0.6) * (i / max(1, vert_devices - 1))
                positions.append({"x": x, "y": y})
                
        elif shape == "I":
            # I-shaped factory: narrow vertical layout
            num_devices = len(plcs_data)
            for i in range(num_devices):
                x = width_m * 0.5
                y = height_m * 0.1 + (height_m * 0.8) * (i / max(1, num_devices - 1))
                positions.append({"x": x, "y": y})
                
        elif shape == "Z":
            # Z-shaped factory: zigzag pattern
            num_devices = len(plcs_data)
            if num_devices <= 3:
                # Simple Z with 3 points
                positions.extend([
                    {"x": width_m * 0.1, "y": height_m * 0.1},
                    {"x": width_m * 0.5, "y": height_m * 0.5},
                    {"x": width_m * 0.9, "y": height_m * 0.9}
                ])
            else:
                # Distribute along Z path
                for i in range(num_devices):
                    if i < num_devices // 3:
                        # First segment (bottom left to top center)
                        progress = i / (num_devices // 3)
                        x = width_m * 0.1 + (width_m * 0.4) * progress
                        y = height_m * 0.9 - (height_m * 0.4) * progress
                    elif i < 2 * num_devices // 3:
                        # Second segment (top center to bottom center)
                        progress = (i - num_devices // 3) / (num_devices // 3)
                        x = width_m * 0.5
                        y = height_m * 0.5 - (height_m * 0.4) * progress
                    else:
                        # Third segment (bottom center to top right)
                        progress = (i - 2 * num_devices // 3) / (num_devices // 3)
                        x = width_m * 0.5 + (width_m * 0.4) * progress
                        y = height_m * 0.1 + (height_m * 0.4) * progress
                    positions.append({"x": x, "y": y})
        else:
            # Default rectangular positioning
            num_devices = len(plcs_data)
            cols = min(3, num_devices)
            rows = (num_devices + cols - 1) // cols
            
            for i in range(num_devices):
                row = i // cols
                col = i % cols
                x = width_m * 0.2 + (width_m * 0.6) * (col / max(1, cols - 1))
                y = height_m * 0.2 + (height_m * 0.6) * (row / max(1, rows - 1))
                positions.append({"x": x, "y": y})
        
        # Apply positions to PLCs (in meters)
        for i, plc_data in enumerate(plcs_data):
            if i < len(positions):
                plc_data["position"] = positions[i]
                # Set dimensions if not present (in meters)
                if "dimensions" not in plc_data:
                    plc_data["dimensions"] = {"width": 2.5, "height": 1.8}
            else:
                # Fallback position
                plc_data["position"] = {"x": width_m * 0.5, "y": height_m * 0.5}
                plc_data["dimensions"] = {"width": 2.5, "height": 1.8}

    def _load_from_static_data(self, data):
        """Load tenant data from static JSON data"""
        from models import Tenant, Manufacturer, Factory, PLC, Sensor, SignalConfig
        
        tenants_data = data.get("tenants", [])
        
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
                        x_position = p_data.get("x_position", 0)
                        y_position = p_data.get("y_position", 0)
                        width = p_data.get("width", 2)
                        height = p_data.get("height", 1)
                        plc = PLC(
                            id=p_data["id"],
                            name=p_data["name"],
                            description=p_data["description"],
                            x_position=x_position,
                            y_position=y_position,
                            width=width,
                            height=height
                        )
                        
                        for sensor_data in p_data["sensors"]:
                            # Handle both old tuple format and new object format
                            if isinstance(sensor_data, list):
                                # Old tuple format
                                sensor_name, description, unit, value, generator, min_val, max_val, params = sensor_data
                            else:
                                # New object format
                                sensor_name = sensor_data["signal_config"]["name"]
                                description = sensor_data["name"]
                                unit = sensor_data["signal_config"]["unit"]
                                value = sensor_data["signal_config"]["value"]
                                generator = sensor_data["signal_config"]["generator"]
                                min_val = sensor_data["signal_config"]["min_value"]
                                max_val = sensor_data["signal_config"]["max_value"]
                                params = {
                                    k: v for k, v in sensor_data["signal_config"].items() 
                                    if k not in ["name", "unit", "value", "generator", "min_value", "max_value"]
                                    and v is not None
                                }
                            
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
        
        logger.info("Static data loaded successfully")
        total_tenants = len(tenants_data)
        total_manufacturers = sum(len(t["manufacturers"]) for t in tenants_data)
        total_factories = sum(len(m["factories"]) for t in tenants_data for m in t["manufacturers"])
        total_plcs = sum(len(f["plcs"]) for t in tenants_data for m in t["manufacturers"] for f in m["factories"])
        total_sensors = sum(len(p["sensors"]) for t in tenants_data for m in t["manufacturers"] for f in m["factories"] for p in f["plcs"])
        
        logger.info(f"Loaded {total_tenants} tenants, {total_manufacturers} manufacturers, {total_factories} factories, {total_plcs} PLCs, and {total_sensors} sensors")

    def _generate_demo_data(self):
        """Generate comprehensive demo data with multiple tenants, manufacturers, factories, and devices"""
        existing_tenants = self.db.get_all_tenants()
        
        # Force re-initialization if we need to update position data
        force_reinit = False  # Set to False since we're using static data by default
        
        # Only skip if we have comprehensive demo data (more than just a basic demo tenant)
        if existing_tenants and len(existing_tenants) >= 3 and not force_reinit:  # We expect 3 tenants
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
        from models import Tenant, Manufacturer, Factory, PLC, Sensor, SignalConfig
        
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
                                        "sensors": [
                                            ("press_force", "Press Force", "tons", 500.0, "normal", 450.0, 550.0, {"mean": 500.0, "std_dev": 25.0}),
                                            ("hydraulic_pressure", "Hydraulic Pressure", "bar", 120.0, "normal", 100.0, 140.0, {"mean": 120.0, "std_dev": 10.0}),
                                            ("material_thickness", "Material Thickness", "mm", 5.0, "uniform", 3.0, 8.0, {}),
                                            ("cycle_time", "Cycle Time", "s", 45.0, "normal", 40.0, 50.0, {"mean": 45.0, "std_dev": 3.0}),
                                        ]
                                    },
                                    {
                                        "id": "PLC-CHI-002",
                                        "name": "Siemens S7-400 #1",
                                        "description": "Welding station controller",
                                        "model": "Siemens S7-400",
                                        "ip_address": "192.168.4.11",
                                        "sensors": [
                                            ("weld_current", "Weld Current", "A", 150.0, "normal", 120.0, 180.0, {"mean": 150.0, "std_dev": 15.0}),
                                            ("weld_voltage", "Weld Voltage", "V", 25.0, "normal", 20.0, 30.0, {"mean": 25.0, "std_dev": 2.5}),
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
                    
                    # Assign factory shape and dimensions
                    factory_configs = {
                        "acme-factory-ny": {"shape": "L", "width": 120, "height": 90, "width_meters": 120.0, "height_meters": 90.0, "wireframe_color": "#ef4444"},
                        "acme-factory-la": {"shape": "rectangle", "width": 100, "height": 80, "width_meters": 100.0, "height_meters": 80.0, "wireframe_color": "#f59e0b"},
                        "tech-factory-austin": {"shape": "I", "width": 80, "height": 120, "width_meters": 80.0, "height_meters": 120.0, "wireframe_color": "#10b981"},
                        "global-factory-chicago": {"shape": "Z", "width": 150, "height": 100, "width_meters": 150.0, "height_meters": 100.0, "wireframe_color": "#8b5cf6"},
                    }
                    
                    if factory.id in factory_configs:
                        config = factory_configs[factory.id]
                        factory.shape = config["shape"]
                        factory.width = config["width"]
                        factory.height = config["height"]
                        factory.width_meters = config["width_meters"]
                        factory.height_meters = config["height_meters"]
                        factory.wireframe_color = config["wireframe_color"]
                    
                    # Collect PLC data for positioning
                    plcs_data = []
                    for p_data in f_data["plcs"]:
                        plcs_data.append(p_data)
                    
                    # Position devices within the factory
                    self._position_devices_in_factory(factory, plcs_data)
                    
                    # Create PLCs with calculated positions
                    for p_data in plcs_data:
                        position = p_data.get("position", {"x": 0, "y": 0})
                        dimensions = p_data.get("dimensions", {"width": 2, "height": 1})
                        plc = PLC(
                            id=p_data["id"],
                            name=p_data["name"],
                            description=p_data["description"],
                            x_position=position["x"],
                            y_position=position["y"],
                            width=dimensions["width"],
                            height=dimensions["height"]
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

    def start_web_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start web server"""
        import uvicorn

        self.web_app = create_app(self.db)
        
        logger.info(f"Starting web server at http://{host}:{port}")
        uvicorn.run(
            self.web_app,
            host=host,
            port=port,
            log_level="info"
        )

    async def start_mqtt_client(self):
        """Start MQTT client"""
        import paho.mqtt.client as mqtt
        import json
        import time
        
        MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
        MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
        MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
        MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
        
        def on_message(client, userdata, msg):
            data = json.loads(msg.payload.decode())
            logger.info(f"Received MQTT from Unreal: {data}")
            # Process Unreal commands (update simulator state)
            # Example: Update PLC data based on MQTT
        
        client = mqtt.Client()
        if MQTT_USERNAME:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.on_message = on_message
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.subscribe("unreal/commands")  # Topic from Unreal
        client.loop_start()
        
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        
        # Publish simulator data periodically
        while True:
            # Get current PLC data
            tenants = self.db.get_all_tenants()
            timestamp = time.time()
            
            # Publish individual device data
            for tenant in tenants:
                for manufacturer in tenant.manufacturers:
                    for factory in manufacturer.factories:
                        # Publish PLCs
                        for plc in factory.plcs:
                            topic = f"plc/{plc.id}"
                            payload = {
                                "device_id": plc.id,
                                "type": "plc",
                                "timestamp": timestamp,
                                "data": plc.to_dict(),
                                "metadata": {
                                    "tenant": tenant.id,
                                    "factory": factory.id
                                }
                            }
                            client.publish(topic, json.dumps(payload))
                            logger.debug(f"Published PLC data to {topic}")
                            
                            # Publish Sensors within this PLC
                            for sensor in plc.sensors:
                                topic = f"plc/{sensor.id}"
                                payload = {
                                    "device_id": sensor.id,
                                    "type": "sensor",
                                    "timestamp": timestamp,
                                    "data": sensor.to_dict(),
                                    "metadata": {
                                        "tenant": tenant.id,
                                        "factory": factory.id,
                                        "plc": plc.id
                                    }
                                }
                                client.publish(topic, json.dumps(payload))
                                logger.debug(f"Published sensor data to {topic}")

            await asyncio.sleep(1)  # Publish every second

def main():
    """Main entry point - simplified for multi-tenant testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VirtPLC Multi-Tenant Simulator")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--db-path", default="data/tenants.json", help="Database file path")
    parser.add_argument("--mode", default=os.getenv("SIMULATOR_MODE", "web-only"), help="Mode: web-only or plc-server")
    parser.add_argument("--mqtt-broker", default=os.getenv("MQTT_BROKER", "mqtt"), help="MQTT broker host")
    parser.add_argument("--mqtt-port", type=int, default=int(os.getenv("MQTT_PORT", 1883)), help="MQTT broker port")
    
    args = parser.parse_args()
    
    # Create app with multi-tenant database
    app = SimulatorApp(args.db_path)
    
    if args.mode == "plc-server":
        # Start MQTT client in a separate thread
        logger.info(f"Starting MQTT client in plc-server mode connecting to {args.mqtt_broker}:{args.mqtt_port}")
        import threading
        mqtt_thread = threading.Thread(target=lambda: asyncio.run(app.start_mqtt_client()))
        mqtt_thread.daemon = True
        mqtt_thread.start()
        
        # Start web server (blocking)
        app.start_web_server(args.host, args.port)
    else:
        # Start web server only (blocking)
        app.start_web_server(args.host, args.port)


if __name__ == "__main__":
    main()