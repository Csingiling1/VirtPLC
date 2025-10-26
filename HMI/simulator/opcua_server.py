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
        self.server = Server()
        await self.server.init()
        self.server.set_endpoint(self.endpoint)

        # Set up namespace
        uri = "http://virtplc.simulator"
        idx = await self.server.register_namespace(uri)

        # Create device nodes
        await self._create_device_nodes(idx)

        # Start server
        await self.server.start()
        logger.info(f"OPC-UA server started at {self.endpoint}")

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
            device_folder = await virplc_folder.add_folder(namespace_idx, device.name)
            self.device_nodes[device.id] = {}

            # Create signal nodes
            for signal in device.signals:
                try:
                    node = await device_folder.add_variable(
                        namespace_idx,
                        signal.name,
                        signal.value,
                        ua.VariantType.Float
                    )
                    # Make node writable
                    await node.set_writable()
                    self.device_nodes[device.id][signal.name] = node
                    logger.debug(f"Created OPC-UA node for {device.id}.{signal.name}")
                except Exception as e:
                    logger.error(f"Error creating node for {device.id}.{signal.name}: {e}")

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
                        await node.write_value(signal_value)
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
                await self.device_nodes[device_id][signal_name].write_value(value)
                # Update database
                device = self.db.get_device(device_id)
                if device:
                    device.set_signal_value(signal_name, value)
                return True
            except Exception as e:
                logger.error(f"Error writing {device_id}.{signal_name}: {e}")
        return False