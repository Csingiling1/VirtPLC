"""
Enhanced OPC-UA Server for Simulator Integration

Provides OPC-UA server for industrial protocol communication with dynamic device management
"""

import logging
from typing import Dict, Optional
from asyncua import Server, ua

from database import DeviceDatabase
from models import FactoryDevice, SignalConfig

logger = logging.getLogger(__name__)


class OPCUAServer:
    """Enhanced OPC-UA server for simulator with dynamic device management"""

    def __init__(self, database: DeviceDatabase, endpoint: str = "opc.tcp://0.0.0.0:4840/virtplc/"):
        self.db = database
        self.endpoint = endpoint
        self.server: Optional[Server] = None
        self.device_nodes: Dict[str, Dict] = {}  # device_id -> {signal_name -> node}
        self.namespace_idx: Optional[int] = None
        self.virtplc_folder = None
        self.system_nodes: Dict[str, ua.Node] = {}  # System-level nodes

    async def start(self):
        """Start the OPC-UA server"""
        try:
            logger.info("Starting OPC-UA server...")
            self.server = Server()
            await self.server.init()
            self.server.set_endpoint(self.endpoint)
            self.server.set_server_name("VirtPLC Enhanced Simulator")

            # Set up namespace
            uri = "http://virtplc.simulator"
            self.namespace_idx = await self.server.register_namespace(uri)
            logger.info(f"Registered namespace {uri} with index {self.namespace_idx}")

            # Create system and device nodes
            await self._create_system_nodes()
            await self._create_device_nodes()

            # Start server
            await self.server.start()
            logger.info(f"OPC-UA server started at {self.endpoint}")
            logger.info("Available nodes:")
            await self._log_available_nodes()
        except Exception as e:
            logger.error(f"Failed to start OPC-UA server: {e}")
            raise

    async def stop(self):
        """Stop the OPC-UA server"""
        if self.server:
            await self.server.stop()
            logger.info("OPC-UA server stopped")

    async def _create_system_nodes(self):
        """Create system-level OPC-UA nodes"""
        objects = self.server.nodes.objects
        
        # Create VirtPLC folder
        self.virtplc_folder = await objects.add_folder(self.namespace_idx, "VirtPLC")
        
        # Create System folder
        system_folder = await self.virtplc_folder.add_folder(self.namespace_idx, "System")
        
        # System status nodes
        self.system_nodes['EmergencyStop'] = await system_folder.add_variable(
            self.namespace_idx, "EmergencyStop", False, ua.VariantType.Boolean
        )
        await self.system_nodes['EmergencyStop'].set_writable()
        
        self.system_nodes['SystemReset'] = await system_folder.add_variable(
            self.namespace_idx, "SystemReset", False, ua.VariantType.Boolean
        )
        await self.system_nodes['SystemReset'].set_writable()
        
        self.system_nodes['SystemStatus'] = await system_folder.add_variable(
            self.namespace_idx, "SystemStatus", "Running", ua.VariantType.String
        )
        
        self.system_nodes['TotalDevices'] = await system_folder.add_variable(
            self.namespace_idx, "TotalDevices", 0
        )
        
        self.system_nodes['ActiveDevices'] = await system_folder.add_variable(
            self.namespace_idx, "ActiveDevices", 0
        )
        
        logger.info("Created system nodes")

    async def _create_device_nodes(self):
        """Create OPC-UA nodes for all devices and signals"""
        # Create devices
        for device in self.db.get_all_devices():
            await self._add_device_nodes(device)

    async def _add_device_nodes(self, device: FactoryDevice):
        """Create OPC-UA nodes for a single device"""
        if not self.server or not self.virtplc_folder:
            return
            
        try:
            # Create device folder
            device_folder = await self.virtplc_folder.add_folder(self.namespace_idx, device.id)
            
            # Device info nodes
            device_info_folder = await device_folder.add_folder(self.namespace_idx, "Info")
            await device_info_folder.add_variable(
                self.namespace_idx, "Name", device.name, ua.VariantType.String
            )
            await device_info_folder.add_variable(
                self.namespace_idx, "Type", device.device_type, ua.VariantType.String
            )
            await device_info_folder.add_variable(
                self.namespace_idx, "Active", device.is_active, ua.VariantType.Boolean
            )
            if device.description:
                await device_info_folder.add_variable(
                    self.namespace_idx, "Description", device.description, ua.VariantType.String
                )
            
            # Create signals folder
            signals_folder = await device_folder.add_folder(self.namespace_idx, "Signals")
            
            # Create signal nodes
            if device.id not in self.device_nodes:
                self.device_nodes[device.id] = {}
                
            for signal in device.signals:
                try:
                    # Determine variant type based on signal characteristics
                    variant_type = self._get_variant_type(signal)
                    
                    signal_node = await signals_folder.add_variable(
                        self.namespace_idx,
                        signal.name,
                        signal.value,
                        variant_type
                    )
                    
                    # Make node writable for control signals
                    if signal.name.lower() in ['start', 'stop', 'reset', 'target', 'command']:
                        await signal_node.set_writable()
                    
                    # Store node reference for updates
                    self.device_nodes[device.id][signal.name] = signal_node
                    logger.debug(f"Created OPC-UA node for {device.id}.{signal.name}")
                    
                except Exception as e:
                    logger.error(f"Error creating signal node for {device.id}.{signal.name}: {e}")
                    
            logger.info(f"Created OPC-UA nodes for device: {device.id}")
            
        except Exception as e:
            logger.error(f"Error creating device nodes for {device.id}: {e}")

    def _get_variant_type(self, signal: SignalConfig) -> ua.VariantType:
        """Determine appropriate OPC-UA variant type for signal"""
        # Check if signal represents a boolean value
        if signal.name.lower() in ['running', 'fault', 'active', 'enabled', 'start', 'stop', 'reset']:
            return ua.VariantType.Boolean
        # Check if signal represents an integer value
        elif signal.name.lower() in ['count', 'items', 'fault_code', 'state']:
            return ua.VariantType.Int32
        # Default to double for numeric values
        else:
            return ua.VariantType.Double

    async def add_device(self, device: FactoryDevice):
        """Add OPC-UA nodes for a new device"""
        if not self.server or not self.virtplc_folder:
            return
        await self._add_device_nodes(device)
        await self._update_system_stats()

    async def remove_device(self, device_id: str):
        """Remove OPC-UA nodes for a device"""
        if device_id in self.device_nodes:
            # Note: OPC-UA doesn't support dynamic node removal easily
            # We'll mark the device as inactive instead
            logger.warning(f"Cannot remove OPC-UA nodes for {device_id} dynamically. Marking as inactive.")
            del self.device_nodes[device_id]
            await self._update_system_stats()

    async def add_signal(self, device_id: str, signal: SignalConfig):
        """Add OPC-UA node for a new signal"""
        if not self.server or not self.virtplc_folder or device_id not in self.device_nodes:
            return
            
        try:
            # Find the device folder and signals folder
            device_folder = await self.virtplc_folder.get_child([f"{self.namespace_idx}:{device_id}"])
            signals_folder = await device_folder.get_child([f"{self.namespace_idx}:Signals"])
            
            # Create signal node
            variant_type = self._get_variant_type(signal)
            signal_node = await signals_folder.add_variable(
                self.namespace_idx,
                signal.name,
                signal.value,
                variant_type
            )
            
            # Make node writable for control signals
            if signal.name.lower() in ['start', 'stop', 'reset', 'target', 'command']:
                await signal_node.set_writable()
            
            # Store node reference
            self.device_nodes[device_id][signal.name] = signal_node
            logger.info(f"Added OPC-UA node for {device_id}.{signal.name}")
            
        except Exception as e:
            logger.error(f"Error adding signal node for {device_id}.{signal.name}: {e}")

    async def remove_signal(self, device_id: str, signal_name: str):
        """Remove OPC-UA node for a signal"""
        if device_id in self.device_nodes and signal_name in self.device_nodes[device_id]:
            # Note: OPC-UA doesn't support dynamic node removal easily
            logger.warning(f"Cannot remove OPC-UA node for {device_id}.{signal_name} dynamically.")
            del self.device_nodes[device_id][signal_name]

    async def _update_system_stats(self):
        """Update system statistics nodes"""
        if not self.server or not self.system_nodes:
            return
            
        try:
            devices = self.db.get_all_devices()
            active_devices = [d for d in devices if d.is_active]
            
            await self.system_nodes['TotalDevices'].write_value(int(len(devices)))
            await self.system_nodes['ActiveDevices'].write_value(int(len(active_devices)))
            
        except Exception as e:
            logger.error(f"Error updating system stats: {e}")

    async def _log_available_nodes(self):
        """Log available OPC-UA nodes for debugging"""
        try:
            if self.virtplc_folder:
                children = await self.virtplc_folder.get_children()
                for child in children:
                    child_name = await child.read_browse_name()
                    logger.info(f"  - {child_name.Name}")
        except Exception as e:
            logger.error(f"Error logging available nodes: {e}")

    async def update_values(self):
        """Update OPC-UA node values from database"""
        if not self.server:
            return

        # Update device signal values
        for device_id, signals in self.device_nodes.items():
            device = self.db.get_device(device_id)
            if not device:
                continue

            for signal_name, node in signals.items():
                signal_value = device.get_signal_value(signal_name)
                if signal_value is not None:
                    try:
                        # Determine appropriate variant type
                        variant_type = ua.VariantType.Double
                        if signal_name.lower() in ['running', 'fault', 'active', 'enabled', 'start', 'stop', 'reset']:
                            variant_type = ua.VariantType.Boolean
                        elif signal_name.lower() in ['count', 'items', 'fault_code', 'state']:
                            variant_type = ua.VariantType.Int32
                        
                        # Create appropriate variant
                        if variant_type == ua.VariantType.Boolean:
                            variant = ua.Variant(bool(signal_value), variant_type)
                        elif variant_type == ua.VariantType.Int32:
                            variant = ua.Variant(int(signal_value), variant_type)
                        else:
                            variant = ua.Variant(float(signal_value), variant_type)
                            
                        await node.write_value(variant)
                    except Exception as e:
                        logger.error(f"Error updating {device_id}.{signal_name}: {e}")

        # Update system statistics
        await self._update_system_stats()

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