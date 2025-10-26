"""
Enhanced Web API for Factory Simulator

Provides REST API for device management and monitoring
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime

from database import DeviceDatabase
from models import FactoryDevice, SignalConfig, SignalGenerator


# Pydantic models for API
class SignalConfigModel(BaseModel):
    name: str
    unit: str
    value: float = 0.0
    generator: str = SignalGenerator.CONSTANT.value
    is_running: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean: Optional[float] = None
    std_dev: Optional[float] = None
    rate: Optional[float] = None
    frequency: Optional[float] = None
    amplitude: Optional[float] = None
    offset: Optional[float] = None
    step_size: Optional[float] = None


class DeviceModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    device_type: str = "generic"
    signals: List[SignalConfigModel] = []
    is_active: bool = True


class DeviceCreateModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    device_type: str = "generic"


class DeviceUpdateModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    device_type: Optional[str] = None
    is_active: Optional[bool] = None
    signals: Optional[List[SignalConfigModel]] = None


class SignalCreateModel(BaseModel):
    name: str
    unit: str
    generator: str = SignalGenerator.CONSTANT.value
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean: Optional[float] = None
    std_dev: Optional[float] = None
    rate: Optional[float] = None
    frequency: Optional[float] = None
    amplitude: Optional[float] = None
    offset: Optional[float] = None
    step_size: Optional[float] = None


def create_app(database: DeviceDatabase) -> FastAPI:
    """Create FastAPI application"""

    app = FastAPI(
        title="VirtPLC Enhanced Simulator API",
        description="REST API for factory device management and monitoring",
        version="2.0.0"
    )

    @app.get("/")
    async def root():
        """API root endpoint"""
        return {
            "message": "VirtPLC Enhanced Simulator API",
            "version": "2.0.0",
            "endpoints": [
                "/devices",
                "/devices/{device_id}",
                "/devices/{device_id}/signals",
                "/devices/{device_id}/signals/{signal_name}",
                "/simulation/start",
                "/simulation/stop"
            ]
        }

    @app.get("/devices", response_model=List[DeviceModel])
    async def list_devices(
        device_type: Optional[str] = Query(None, description="Filter by device type"),
        active_only: bool = Query(False, description="Show only active devices")
    ):
        """List all devices"""
        if device_type:
            devices = database.get_devices_by_type(device_type)
        elif active_only:
            devices = database.get_active_devices()
        else:
            devices = database.get_all_devices()

        return [DeviceModel(**device.to_dict()) for device in devices]

    @app.post("/devices", response_model=DeviceModel)
    async def create_device(device: DeviceCreateModel):
        """Create a new device"""
        try:
            factory_device = FactoryDevice(
                id=device.id,
                name=device.name,
                description=device.description,
                device_type=device.device_type
            )
            created_device = database.create_device(factory_device)
            return DeviceModel(**created_device.to_dict())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/devices/{device_id}", response_model=DeviceModel)
    async def get_device(device_id: str):
        """Get device by ID"""
        device = database.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return DeviceModel(**device.to_dict())

    @app.put("/devices/{device_id}", response_model=DeviceModel)
    async def update_device(device_id: str, updates: DeviceUpdateModel):
        """Update device"""
        update_dict = updates.dict(exclude_unset=True)
        device = database.update_device(device_id, update_dict)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return DeviceModel(**device.to_dict())

    @app.delete("/devices/{device_id}")
    async def delete_device(device_id: str):
        """Delete device"""
        if not database.delete_device(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        return {"message": f"Device {device_id} deleted"}

    @app.get("/devices/{device_id}/signals")
    async def get_device_signals(device_id: str):
        """Get all signals for a device"""
        device = database.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        return {
            "device_id": device_id,
            "signals": [
                {
                    "name": s.name,
                    "unit": s.unit,
                    "value": s.value,
                    "generator": s.generator,
                    "is_running": s.is_running
                }
                for s in device.signals
            ]
        }

    @app.post("/devices/{device_id}/signals")
    async def add_signal(device_id: str, signal: SignalCreateModel):
        """Add signal to device"""
        device = database.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        signal_config = SignalConfig(
            name=signal.name,
            unit=signal.unit,
            generator=signal.generator,
            min_value=signal.min_value,
            max_value=signal.max_value,
            mean=signal.mean,
            std_dev=signal.std_dev,
            rate=signal.rate,
            frequency=signal.frequency,
            amplitude=signal.amplitude,
            offset=signal.offset,
            step_size=signal.step_size
        )

        device.signals.append(signal_config)
        database._save_devices()
        return {"message": f"Signal {signal.name} added to device {device_id}"}

    @app.delete("/devices/{device_id}/signals/{signal_name}")
    async def remove_signal(device_id: str, signal_name: str):
        """Remove signal from device"""
        device = database.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        device.signals = [s for s in device.signals if s.name != signal_name]
        database._save_devices()
        return {"message": f"Signal {signal_name} removed from device {device_id}"}

    @app.get("/devices/{device_id}/signals/{signal_name}")
    async def get_signal_value(device_id: str, signal_name: str):
        """Get signal value"""
        device = database.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        value = device.get_signal_value(signal_name)
        if value is None:
            raise HTTPException(status_code=404, detail="Signal not found")

        return {
            "device_id": device_id,
            "signal_name": signal_name,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }

    @app.put("/devices/{device_id}/signals/{signal_name}")
    async def set_signal_value(device_id: str, signal_name: str, value: float):
        """Set signal value"""
        device = database.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        device.set_signal_value(signal_name, value)
        database._save_devices()
        return {"message": f"Signal {signal_name} set to {value}"}

    @app.post("/simulation/update")
    async def update_simulation():
        """Manually trigger simulation update"""
        database.update_all_signals()
        return {"message": "Simulation updated", "timestamp": datetime.now().isoformat()}

    @app.get("/simulation/status")
    async def get_simulation_status():
        """Get simulation status"""
        devices = database.get_all_devices()
        active_devices = len(database.get_active_devices())
        total_signals = sum(len(d.signals) for d in devices)

        return {
            "total_devices": len(devices),
            "active_devices": active_devices,
            "total_signals": total_signals,
            "timestamp": datetime.now().isoformat()
        }

    return app


if __name__ == "__main__":
    # For testing the API standalone
    import uvicorn
    db = DeviceDatabase()
    app = create_app(db)
    uvicorn.run(app, host="0.0.0.0", port=8000)
