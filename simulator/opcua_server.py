"""
OPC-UA Server for Simulator Integration

Provides OPC-UA server for industrial protocol communication
"""

import asyncio
import logging
from typing import Dict, Optional
from asyncua import Server, ua
from asyncua.common.methods import uamethod

from database import DeviceDatabase
from models import FactoryDevice

logger = logging.getLogger(__name__)


class OPCUAServer:
    """OPC-UA server for simulator"""

    def __init__(self, database: DeviceDatabase, endpoint: str = "opc.tcp://0.0.0.0:4840/virtplc/"):
        self.db = database
        self.endpoint = endpoint
        self.server: Optional[Server] = None
        self.device_nodes: Dict[str, Dict] = {}  # device_id -> {signal_name -> node}

    async def start(self):
        """Start the OPC-UA server"""
        try:
            logger.info("Starting OPC-UA server...")
            self.server = Server()
            await self.server.init()
            self.server.set_endpoint(self.endpoint)

            # Set up namespace
            uri = "http://virtplc.simulator"
            idx = await self.server.register_namespace(uri)
            logger.info(f"Registered namespace {uri} with index {idx}")

            # Create device nodes
            await self._create_device_nodes(idx)

            # Start server
            await self.server.start()
            logger.info(f"OPC-UA server started at {self.endpoint}")
        except Exception as e:
            logger.error(f"Failed to start OPC-UA server: {e}")
            raise

    async def stop(self):
        """Stop the OPC-UA server"""
        if self.server:
            await self.server.stop()
            logger.info("OPC-UA server stopped")

    async def _create_device_nodes(self, namespace_idx: int):
        """Create OPC-UA nodes for all devices and signals"""
        # Create root objects node
        objects = self.server.nodes.objects

        # Create VirtPLC folder
        virplc_folder = await objects.add_folder(namespace_idx, "VirtPLC")

        # Create devices
        for device in self.db.get_all_devices():
            await self._add_device_nodes(device, namespace_idx, virplc_folder)

    async def _add_device_nodes(self, device: FactoryDevice, namespace_idx: int, virplc_folder):
        """Create OPC-UA nodes for a single device"""
        # Create signal nodes directly under VirtPLC with device.signal format
        for signal in device.signals:
            try:
                node_name = f"{device.id.capitalize()}.{signal.name.capitalize()}"
                node = await virplc_folder.add_variable(
                        namespace_idx,
                        node_name,
                        signal.value,
                        ua.VariantType.Double
                    )
                # Make node writable
                await node.set_writable()
                # Store node reference for updates
                if device.id not in self.device_nodes:
                    self.device_nodes[device.id] = {}
                self.device_nodes[device.id][signal.name] = node
                logger.debug(f"Created OPC-UA node for {node_name}")
            except Exception as e:
                logger.error(f"Error creating node for {device.name}.{signal.name}: {e}")

    async def add_device(self, device: FactoryDevice):
        """Add OPC-UA nodes for a new device"""
        if not self.server:
            return
        uri = "http://virtplc.simulator"
        idx = await self.server.register_namespace(uri)
        objects = self.server.nodes.objects
        virplc_folder = await objects.get_child([f"{idx}:VirtPLC"])
        await self._add_device_nodes(device, idx, virplc_folder)

    async def update_values(self):
        """Update OPC-UA node values from database"""
        if not self.server:
            return

        for device_id, signals in self.device_nodes.items():
            device = self.db.get_device(device_id)
            if not device:
                continue

            for signal_name, node in signals.items():
                signal_value = device.get_signal_value(signal_name)
                if signal_value is not None:
                    try:
                        # Create a Double variant explicitly
                        double_value = float(signal_value)
                        variant = ua.Variant(double_value, ua.VariantType.Double)
                        await node.write_value(variant)
                    except Exception as e:
                        logger.error(f"Error updating {device_id}.{signal_name}: {e}")

    async def read_value(self, device_id: str, signal_name: str) -> Optional[float]:
        """Read value from OPC-UA node"""
        if device_id in self.device_nodes and signal_name in self.device_nodes[device_id]:
            try:
                return await self.device_nodes[device_id][signal_name].read_value()
            except Exception as e:
                logger.error(f"Error reading {device_id}.{signal_name}: {e}")
        return None

    async def write_value(self, device_id: str, signal_name: str, value: float) -> bool:
        """Write value to OPC-UA node and database"""
        if device_id in self.device_nodes and signal_name in self.device_nodes[device_id]:
            try:
                # Wrap the value in a Float variant explicitly
                float_value = float(value)
                variant = ua.Variant(float_value, ua.VariantType.Float)
                await self.device_nodes[device_id][signal_name].write_value(variant)
                # Update database
                device = self.db.get_device(device_id)
                if device:
                    device.set_signal_value(signal_name, value)
                return True
            except Exception as e:
                logger.error(f"Error writing {device_id}.{signal_name}: {e}")
        return False