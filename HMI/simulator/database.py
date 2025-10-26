"""
File-based database for device persistence
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from models import FactoryDevice

logger = logging.getLogger(__name__)


class DeviceDatabase:
    """File-based database for factory devices"""

    def __init__(self, db_path: str = "devices.json"):
        self.db_path = Path(db_path)
        self.devices: Dict[str, FactoryDevice] = {}
        self._load_devices()

    def _load_devices(self):
        """Load devices from file"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    for device_data in data.get("devices", []):
                        device = FactoryDevice.from_dict(device_data)
                        self.devices[device.id] = device
                logger.info(f"Loaded {len(self.devices)} devices from {self.db_path}")
            except Exception as e:
                logger.error(f"Error loading devices: {e}")
        else:
            logger.info(f"Database file {self.db_path} not found, starting with empty database")

    def _save_devices(self):
        """Save devices to file"""
        try:
            data = {
                "devices": [device.to_dict() for device in self.devices.values()]
            }
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.devices)} devices to {self.db_path}")
        except Exception as e:
            logger.error(f"Error saving devices: {e}")

    def create_device(self, device: FactoryDevice) -> FactoryDevice:
        """Create a new device"""
        if device.id in self.devices:
            raise ValueError(f"Device with id {device.id} already exists")
        self.devices[device.id] = device
        self._save_devices()
        logger.info(f"Created device: {device.name} ({device.id})")
        return device

    def get_device(self, device_id: str) -> Optional[FactoryDevice]:
        """Get device by ID"""
        return self.devices.get(device_id)

    def get_all_devices(self) -> List[FactoryDevice]:
        """Get all devices"""
        return list(self.devices.values())

    def update_device(self, device_id: str, updates: Dict[str, Any]) -> Optional[FactoryDevice]:
        """Update device properties"""
        device = self.devices.get(device_id)
        if not device:
            return None

        # Update device properties
        for key, value in updates.items():
            if key == "name":
                device.name = value
            elif key == "description":
                device.description = value
            elif key == "device_type":
                device.device_type = value
            elif key == "is_active":
                device.is_active = value
            elif key == "signals":
                # Handle signal updates
                device.signals = [FactoryDevice.from_dict({"signals": [s]})["signals"][0] for s in value]

        device.updated_at = FactoryDevice.__annotations__.get('updated_at', lambda: 0)()
        self._save_devices()
        logger.info(f"Updated device: {device.name} ({device.id})")
        return device

    def delete_device(self, device_id: str) -> bool:
        """Delete device"""
        if device_id in self.devices:
            device = self.devices.pop(device_id)
            self._save_devices()
            logger.info(f"Deleted device: {device.name} ({device.id})")
            return True
        return False

    def get_devices_by_type(self, device_type: str) -> List[FactoryDevice]:
        """Get devices by type"""
        return [d for d in self.devices.values() if d.device_type == device_type]

    def get_active_devices(self) -> List[FactoryDevice]:
        """Get active devices"""
        return [d for d in self.devices.values() if d.is_active]

    def update_all_signals(self):
        """Update signals for all active devices"""
        for device in self.get_active_devices():
            device.update_signals()
        self._save_devices()