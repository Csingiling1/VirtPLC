"""
OPC-UA Server for VirtPLC Simulator

Provides OPC-UA interface for multi-tenant PLC telemetry data
"""

import asyncio
import logging
from typing import Dict, Optional, List
from asyncua import Server, ua
from asyncua.common.node import Node
from database import MultiTenantDatabase
from models import Tenant, Manufacturer, Factory, PLC, Sensor

logger = logging.getLogger(__name__)


class OPCUAServer:
    """OPC-UA server exposing multi-tenant PLC sensor data"""

    def __init__(self, database: MultiTenantDatabase, endpoint: str = "opc.tcp://0.0.0.0:4840/virtplc/"):
        self.db = database
        self.endpoint = endpoint
        self.server: Optional[Server] = None
        self.nodes: Dict[str, Node] = {}
        self.running = False

    async def start(self):
        """Start the OPC-UA server"""
        try:
            self.server = Server()
            await self.server.init()
            self.server.set_endpoint(self.endpoint)
            self.server.set_server_name("VirtPLC Simulator OPC-UA Server")

            # Register namespace
            uri = "http://virtplc.simulator"
            idx = await self.server.register_namespace(uri)
            self.ns_idx = idx
            logger.info(f"Registered namespace '{uri}' with index {idx}")

            # Create object node
            objects = self.server.get_objects_node()
            virtplc_obj = await objects.add_object(idx, "VirtPLC")

            # Create tenant nodes
            await self._create_tenant_nodes(virtplc_obj, idx)

            logger.info(f"OPC-UA server started at {self.endpoint}")
            self.running = True
            
            # Start update loop
            asyncio.create_task(self._update_loop())
            
            await self.server.start()

        except Exception as e:
            logger.error(f"Failed to start OPC-UA server: {e}")
            raise

    async def _update_loop(self):
        """Update OPC-UA values periodically"""
        logger.info("OPC-UA update loop started")
        while self.running:
            try:
                logger.debug("Calling update_values()")
                await self.update_values()
                await asyncio.sleep(1.0)  # Update every second
            except Exception as e:
                logger.error(f"Failed to update OPC-UA values: {e}")
                await asyncio.sleep(1.0)

    async def stop(self):
        """Stop the OPC-UA server"""
        if self.server:
            await self.server.stop()
            self.running = False
            logger.info("OPC-UA server stopped")

    async def update_values(self):
        """Update all sensor values in OPC-UA server"""
        logger.debug("update_values() called")
        try:
            if not self.server or not self.running:
                return

            # Update tenant sensor values
            tenants = self.db.get_all_tenants()
            for tenant in tenants:
                for manufacturer in tenant.manufacturers:
                    for factory in manufacturer.factories:
                        for plc in factory.plcs:
                            for sensor in plc.sensors:
                                # Update sensor value in OPC-UA
                                node_id = f"{tenant.id}.{manufacturer.id}.{factory.id}.{plc.id}.{sensor.id}"
                                full_node_id = f"ns={self.ns_idx};s={node_id}"
                                if full_node_id in self.nodes:
                                    await self.nodes[full_node_id].write_value(sensor.signal_config.value)

            # Update demo nodes for backward compatibility
            await self._update_demo_values()

        except Exception as e:
            logger.error(f"Failed to update OPC-UA values: {e}")

    async def _update_demo_nodes(self):
        """Update demo nodes with current values"""
        # This is for backward compatibility with the backend
        pass

    async def _update_demo_values(self):
        """Update demo nodes with simulated values"""
        import random
        import time

        current_time = time.time()

        # Simulate motor speeds (RPM)
        motor1_speed = 1500 + 100 * (0.5 - random.random())
        motor2_speed = 1200 + 150 * (0.5 - random.random())

        # Simulate temperatures (°C)
        motor1_temp = 75 + 10 * (0.5 - random.random())
        motor2_temp = 68 + 8 * (0.5 - random.random())

        # Simulate conveyor speed (m/s)
        conveyor_speed = 2.5 + 0.5 * (0.5 - random.random())

        # Simulate sensor values
        sensor1_value = 25.5 + 5 * (0.5 - random.random())
        sensor2_value = (current_time % 10) > 5  # Boolean alternating

        # Simulate motor running status (most of the time running)
        motor1_running = random.random() > 0.05  # 95% uptime
        motor2_running = random.random() > 0.08  # 92% uptime
        conveyor_running = motor1_running  # Conveyor follows motor1

        # Simulate faults (rare)
        motor1_fault = random.random() < 0.02  # 2% fault rate
        motor2_fault = random.random() < 0.03  # 3% fault rate

        updates = [
            ("Motor1.Speed", motor1_speed),
            ("Motor1.Temperature", motor1_temp),
            ("Motor1.Running", motor1_running),
            ("Motor1.Fault", motor1_fault),
            ("Motor2.Speed", motor2_speed),
            ("Motor2.Temperature", motor2_temp),
            ("Motor2.Running", motor2_running),
            ("Motor2.Fault", motor2_fault),
            ("Conveyor1.Speed", conveyor_speed),
            ("Conveyor1.Running", conveyor_running),
            ("Sensor1.Value", sensor1_value),
            ("Sensor2.Value", sensor2_value),
        ]

        # Debug logging every 3 seconds
        import time
        current_time = time.time()
        if not hasattr(self, '_last_debug_time') or (current_time - self._last_debug_time) > 3:
            logger.info(f"DEBUG: Setting demo values - Motor1.Speed: {motor1_speed:.2f}, Motor1.Temp: {motor1_temp:.2f}, Motor1.Run: {motor1_running}, Motor1.Fault: {motor1_fault}, Motor2.Speed: {motor2_speed:.2f}, Motor2.Temp: {motor2_temp:.2f}, Motor2.Run: {motor2_running}, Motor2.Fault: {motor2_fault}, Conveyor1.Speed: {conveyor_speed:.2f}, Conveyor1.Run: {conveyor_running}, Sensor1.Value: {sensor1_value:.2f}, Sensor2.Value: {sensor2_value}")
            self._last_debug_time = current_time

        for node_name, value in updates:
            full_node_id = f"ns={self.ns_idx};s={node_name}"
            if full_node_id in self.nodes:
                await self.nodes[full_node_id].write_value(value)

    async def _create_tenant_nodes(self, parent_node: Node, ns_idx: int):
        """Create OPC-UA nodes for all tenants, manufacturers, factories, PLCs and sensors"""
        tenants = self.db.get_all_tenants()

        for tenant in tenants:
            # Create tenant node
            tenant_node = await parent_node.add_object(ns_idx, tenant.id)

            for manufacturer in tenant.manufacturers:
                # Create manufacturer node
                mfg_node = await tenant_node.add_object(ns_idx, manufacturer.id)

                for factory in manufacturer.factories:
                    # Create factory node
                    factory_node = await mfg_node.add_object(ns_idx, factory.id)

                    for plc in factory.plcs:
                        # Create PLC node
                        plc_node = await factory_node.add_object(ns_idx, plc.id)

                        for sensor in plc.sensors:
                            # Create sensor variable node
                            node_id = f"{tenant.id}.{manufacturer.id}.{factory.id}.{plc.id}.{sensor.id}"
                            # Use Double for numeric sensor values to match Python float writes
                            variant_type = ua.VariantType.Double if isinstance(sensor.signal_config.value, float) else ua.VariantType.Boolean
                            sensor_node = await plc_node.add_variable(
                                ns_idx,
                                sensor.id,
                                sensor.signal_config.value,
                                variant_type
                            )
                            # Make it writable
                            await sensor_node.set_writable()

                            # Store node reference for updates
                            full_node_id = f"ns={ns_idx};s={node_id}"
                            self.nodes[full_node_id] = sensor_node

                            logger.debug(f"Created OPC-UA node: {full_node_id}")

        # Create fixed demo nodes for backend compatibility
        await self._create_demo_nodes(parent_node, ns_idx)

    async def _create_demo_nodes(self, parent_node: Node, ns_idx: int):
        """Create fixed demo nodes that the backend expects"""
        demo_nodes = [
            ("Motor1.Speed", 1500.0, ua.VariantType.Double),
            ("Motor1.Temperature", 75.0, ua.VariantType.Double),
            ("Motor1.Running", True, ua.VariantType.Boolean),
            ("Motor1.Fault", False, ua.VariantType.Boolean),
            ("Motor2.Speed", 1200.0, ua.VariantType.Double),
            ("Motor2.Temperature", 68.0, ua.VariantType.Double),
            ("Motor2.Running", True, ua.VariantType.Boolean),
            ("Motor2.Fault", False, ua.VariantType.Boolean),
            ("Conveyor1.Speed", 2.5, ua.VariantType.Double),
            ("Conveyor1.Running", True, ua.VariantType.Boolean),
            ("Sensor1.Value", 25.5, ua.VariantType.Double),
            ("Sensor2.Value", True, ua.VariantType.Boolean),
        ]

        for node_name, initial_value, variant_type in demo_nodes:
            # Create node with explicit string-based node ID
            node_id = ua.NodeId(node_name, ns_idx)
            node = await parent_node.add_variable(node_id, node_name, initial_value, variant_type)
            await node.set_writable()
            full_node_id = f"ns={ns_idx};s={node_name}"
            self.nodes[full_node_id] = node
            logger.info(f"Created demo OPC-UA node: {full_node_id} -> actual node_id: {node.nodeid}")

    def get_sensor_node_ids(self) -> List[str]:
        """Get list of all sensor node IDs for backend to read"""
        return list(self.nodes.keys())
