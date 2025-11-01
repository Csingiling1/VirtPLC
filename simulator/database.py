"""
File-based database for multi-tenant factory simulation
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from models import Tenant, Manufacturer, Factory, PLC, Sensor, SignalConfig, SignalGenerator

logger = logging.getLogger(__name__)


class MultiTenantDatabase:
    """File-based database for multi-tenant factory simulation"""

    def __init__(self, db_path: str = "tenants.json"):
        self.db_path = Path(db_path)
        self.tenants: Dict[str, Tenant] = {}
        self._load_tenants()

    def _load_tenants(self):
        """Load tenants from file"""
        if self.db_path.exists():
            try:
                # Check if it's a directory instead of a file
                if self.db_path.is_dir():
                    logger.warning(f"Database path {self.db_path} is a directory, removing it and creating a new file")
                    import shutil
                    shutil.rmtree(self.db_path)
                    self.db_path.touch()  # Create empty file
                    logger.info(f"Created new empty database file at {self.db_path}")
                    return

                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    for tenant_data in data.get("tenants", []):
                        tenant = self._tenant_from_dict(tenant_data)
                        self.tenants[tenant.id] = tenant
                logger.info(f"Loaded {len(self.tenants)} tenants from {self.db_path}")
            except Exception as e:
                logger.error(f"Error loading tenants: {e}")
        else:
            logger.info(f"Database file {self.db_path} not found, starting with empty database")

    def _tenant_from_dict(self, data: Dict[str, Any]) -> Tenant:
        """Create tenant from dictionary"""
        manufacturers = []
        for m_data in data.get("manufacturers", []):
            manufacturer = self._manufacturer_from_dict(m_data)
            manufacturers.append(manufacturer)

        return Tenant(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            manufacturers=manufacturers,
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", 0),
            updated_at=data.get("updated_at", 0),
        )

    def _manufacturer_from_dict(self, data: Dict[str, Any]) -> Manufacturer:
        """Create manufacturer from dictionary"""
        factories = []
        for f_data in data.get("factories", []):
            factory = self._factory_from_dict(f_data)
            factories.append(factory)

        return Manufacturer(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            factories=factories,
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", 0),
            updated_at=data.get("updated_at", 0),
        )

    def _factory_from_dict(self, data: Dict[str, Any]) -> Factory:
        """Create factory from dictionary"""
        plcs = []
        for p_data in data.get("plcs", []):
            plc = self._plc_from_dict(p_data)
            plcs.append(plc)

        return Factory(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            plcs=plcs,
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", 0),
            updated_at=data.get("updated_at", 0),
            shape=data.get("shape"),
            width=data.get("width"),
            height=data.get("height"),
            width_meters=data.get("width_meters", 50.0),
            height_meters=data.get("height_meters", 40.0),
            wireframe_color=data.get("wireframe_color"),
        )

    def _plc_from_dict(self, data: Dict[str, Any]) -> PLC:
        """Create PLC from dictionary"""
        sensors = []
        for s_data in data.get("sensors", []):
            sensor = self._sensor_from_dict(s_data)
            sensors.append(sensor)

        return PLC(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            sensors=sensors,
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", 0),
            updated_at=data.get("updated_at", 0),
            x_position=data.get("x_position", 0.0),
            y_position=data.get("y_position", 0.0),
        )

    def _sensor_from_dict(self, data: Dict[str, Any]) -> Sensor:
        """Create sensor from dictionary"""
        s_config = data.get("signal_config", {})
        signal_config = SignalConfig(
            name=s_config.get("name", ""),
            unit=s_config.get("unit", ""),
            value=s_config.get("value", 0.0),
            generator=s_config.get("generator", SignalGenerator.CONSTANT.value),
            is_running=s_config.get("is_running", True),
            min_value=s_config.get("min_value"),
            max_value=s_config.get("max_value"),
            mean=s_config.get("mean"),
            std_dev=s_config.get("std_dev"),
            rate=s_config.get("rate"),
            frequency=s_config.get("frequency"),
            amplitude=s_config.get("amplitude"),
            offset=s_config.get("offset"),
            step_size=s_config.get("step_size"),
        )

        return Sensor(
            id=data["id"],
            name=data["name"],
            signal_config=signal_config,
            is_active=data.get("is_active", True),
        )

    def _save_tenants(self):
        """Save tenants to file"""
        try:
            data = {
                "tenants": [tenant.to_dict() for tenant in self.tenants.values()]
            }
            logger.info(f"Saving {len(self.tenants)} tenants to {self.db_path}")
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.tenants)} tenants to {self.db_path}")
        except Exception as e:
            logger.error(f"Error saving tenants: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def create_tenant(self, tenant: Tenant) -> Tenant:
        """Create a new tenant"""
        if tenant.id in self.tenants:
            raise ValueError(f"Tenant with id {tenant.id} already exists")
        self.tenants[tenant.id] = tenant
        self._save_tenants()
        logger.info(f"Created tenant: {tenant.name} ({tenant.id})")
        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.tenants.get(tenant_id)

    def get_all_tenants(self) -> List[Tenant]:
        """Get all tenants"""
        return list(self.tenants.values())

    def update_all_signals(self):
        """Update signals for all active tenants"""
        for tenant in self.get_active_tenants():
            tenant.update_manufacturers()
        self._save_tenants()

    def get_active_tenants(self) -> List[Tenant]:
        """Get active tenants"""
        return [t for t in self.tenants.values() if t.is_active]

    def get_tenant_hierarchy(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get full tenant hierarchy as nested dict"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
        return tenant.to_dict()