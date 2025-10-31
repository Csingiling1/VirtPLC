"""
Enhanced Web API for Multi-Tenant Factory Simulator

Provides REST API for tenant/manufacturer/factory/PLC/sensor management and monitoring with real-time streaming
"""

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import time
from datetime import datetime
import logging

from database import MultiTenantDatabase
from models import Tenant, Manufacturer, Factory, PLC, Sensor, SignalConfig, SignalGenerator

# Configure logging
logger = logging.getLogger(__name__)


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


class SensorModel(BaseModel):
    id: str
    name: str
    signal_config: SignalConfigModel
    is_active: bool = True


class PLCCreateModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    sensors: List[SensorModel] = []


class PLCModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    sensors: List[SensorModel] = []
    is_active: bool = True


class FactoryCreateModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    plcs: List[PLCCreateModel] = []


class FactoryModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    plcs: List[PLCModel] = []
    is_active: bool = True


class ManufacturerCreateModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    factories: List[FactoryCreateModel] = []


class ManufacturerModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    factories: List[FactoryModel] = []
    is_active: bool = True


class TenantCreateModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    manufacturers: List[ManufacturerCreateModel] = []


class TenantModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    manufacturers: List[ManufacturerModel] = []
    is_active: bool = True
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


class TimeSeriesDataPoint(BaseModel):
    timestamp: int
    device_id: str
    signal_name: str
    value: float
    unit: str


class TimeSeriesData(BaseModel):
    data_points: List[TimeSeriesDataPoint]
    total_count: int
    start_time: int
    end_time: int


class WebSocketMessage(BaseModel):
    type: str  # "data", "status", "error"
    data: Dict[str, Any]
    timestamp: int


class ConnectionManager:
    """Manages WebSocket connections for real-time data streaming"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.data_subscribers: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, subscribe_to_data: bool = False):
        await websocket.accept()
        self.active_connections.append(websocket)
        if subscribe_to_data:
            self.data_subscribers.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.data_subscribers:
            self.data_subscribers.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast_data(self, data: Dict[str, Any]):
        """Broadcast data to all subscribers"""
        if not self.data_subscribers:
            return
        
        message = WebSocketMessage(
            type="data",
            data=data,
            timestamp=int(time.time() * 1000)
        )
        
        message_json = message.json()
        disconnected = []
        
        for connection in self.data_subscribers:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting to subscriber: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


def create_app(database: MultiTenantDatabase) -> FastAPI:
    """Create FastAPI application"""

    app = FastAPI(
        title="VirtPLC Multi-Tenant Simulator API",
        description="REST API for multi-tenant factory management and monitoring with real-time streaming",
        version="3.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global connection manager
    manager = ConnectionManager()

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

    @app.get("/tenants", response_model=List[TenantModel])
    async def list_tenants(active_only: bool = Query(False, description="Show only active tenants")):
        """List all tenants"""
        if active_only:
            tenants = database.get_active_tenants()
        else:
            tenants = database.get_all_tenants()

        return [TenantModel(**tenant.to_dict()) for tenant in tenants]

    @app.post("/tenants", response_model=TenantModel)
    async def create_tenant(tenant: TenantCreateModel):
        """Create a new tenant"""
        try:
            # Convert Pydantic models to domain models
            manufacturers = []
            for m_data in tenant.manufacturers:
                factories = []
                for f_data in m_data.factories:
                    plcs = []
                    for p_data in f_data.plcs:
                        sensors = []
                        for s_data in p_data.sensors:
                            sensor = Sensor(
                                id=s_data.id,
                                name=s_data.name,
                                signal_config=SignalConfig(
                                    name=s_data.signal_config.name,
                                    unit=s_data.signal_config.unit,
                                    value=s_data.signal_config.value,
                                    generator=s_data.signal_config.generator,
                                    is_running=s_data.signal_config.is_running,
                                    min_value=s_data.signal_config.min_value,
                                    max_value=s_data.signal_config.max_value,
                                    mean=s_data.signal_config.mean,
                                    std_dev=s_data.signal_config.std_dev,
                                    rate=s_data.signal_config.rate,
                                    frequency=s_data.signal_config.frequency,
                                    amplitude=s_data.signal_config.amplitude,
                                    offset=s_data.signal_config.offset,
                                    step_size=s_data.signal_config.step_size,
                                ),
                                is_active=s_data.is_active,
                            )
                            sensors.append(sensor)
                        plc = PLC(
                            id=p_data.id,
                            name=p_data.name,
                            description=p_data.description,
                            sensors=sensors,
                            is_active=True,
                        )
                        plcs.append(plc)
                    factory = Factory(
                        id=f_data.id,
                        name=f_data.name,
                        description=f_data.description,
                        plcs=plcs,
                        is_active=True,
                    )
                    factories.append(factory)
                manufacturer = Manufacturer(
                    id=m_data.id,
                    name=m_data.name,
                    description=m_data.description,
                    factories=factories,
                    is_active=True,
                )
                manufacturers.append(manufacturer)

            tenant_obj = Tenant(
                id=tenant.id,
                name=tenant.name,
                description=tenant.description,
                manufacturers=manufacturers,
                is_active=True,
            )
            created_tenant = database.create_tenant(tenant_obj)
            return TenantModel(**created_tenant.to_dict())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/tenants/{tenant_id}", response_model=TenantModel)
    async def get_tenant(tenant_id: str):
        """Get tenant by ID"""
        tenant = database.get_tenant(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return TenantModel(**tenant.to_dict())

    @app.put("/devices/{device_id}", response_model=PLCModel)
    async def update_device(device_id: str, updates: DeviceUpdateModel):
        """Update device"""
        update_dict = updates.dict(exclude_unset=True)
        device = database.update_device(device_id, update_dict)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return PLCModel(**device.to_dict())

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
        tenants = database.get_all_tenants()
        active_tenants = len(database.get_active_tenants())
        
        # Count total PLCs across all tenants
        total_plcs = 0
        total_sensors = 0
        for tenant in tenants:
            for manufacturer in tenant.manufacturers:
                for factory in manufacturer.factories:
                    total_plcs += len(factory.plcs)
                    for plc in factory.plcs:
                        total_sensors += len(plc.sensors)

        return {
            "total_tenants": len(tenants),
            "active_tenants": active_tenants,
            "total_plcs": total_plcs,
            "total_sensors": total_sensors,
            "timestamp": datetime.now().isoformat()
        }

    # Real-time data streaming endpoints
    @app.get("/api/stream/latest")
    async def get_latest_data():
        """Get latest data from all tenants - hierarchical format"""
        tenants = database.get_all_tenants()
        current_time = int(time.time() * 1000)

        # Return hierarchical data structure
        data = {
            "timestamp": current_time,
            "tenants": []
        }

        for tenant in tenants:
            if tenant.is_active:
                tenant_data = {
                    "id": tenant.id,
                    "name": tenant.name,
                    "manufacturers": []
                }

                for manufacturer in tenant.manufacturers:
                    if manufacturer.is_active:
                        manufacturer_data = {
                            "id": manufacturer.id,
                            "name": manufacturer.name,
                            "factories": []
                        }

                        for factory in manufacturer.factories:
                            if factory.is_active:
                                factory_data = {
                                    "id": factory.id,
                                    "name": factory.name,
                                    "plcs": []
                                }

                                for plc in factory.plcs:
                                    if plc.is_active:
                                        plc_data = {
                                            "id": plc.id,
                                            "name": plc.name,
                                            "sensors": []
                                        }

                                        for sensor in plc.sensors:
                                            if sensor.is_active:
                                                sensor_data = {
                                                    "id": sensor.id,
                                                    "name": sensor.name,
                                                    "value": sensor.signal_config.value,
                                                    "unit": sensor.signal_config.unit,
                                                    "timestamp": current_time
                                                }
                                                plc_data["sensors"].append(sensor_data)

                                        factory_data["plcs"].append(plc_data)

                                manufacturer_data["factories"].append(factory_data)

                        tenant_data["manufacturers"].append(manufacturer_data)

                data["tenants"].append(tenant_data)

        return data
        
        return data

    @app.get("/api/stream/timeseries", response_model=TimeSeriesData)
    async def get_timeseries_data(
        start_time: Optional[int] = Query(None, description="Start timestamp in milliseconds"),
        end_time: Optional[int] = Query(None, description="End timestamp in milliseconds"),
        device_id: Optional[str] = Query(None, description="Filter by device ID"),
        signal_name: Optional[str] = Query(None, description="Filter by signal name")
    ):
        """Get time-series data for analysis and storage in TimescaleDB"""
        current_time = int(time.time() * 1000)
        start = start_time or (current_time - 3600000)  # Default to last hour
        end = end_time or current_time
        
        devices = database.get_all_devices()
        data_points = []
        
        for device in devices:
            if device_id and device.id != device_id:
                continue
                
            if not device.is_active:
                continue
                
            for signal in device.signals:
                if signal_name and signal.name != signal_name:
                    continue
                    
                # Generate historical data points (simplified - in real implementation, 
                # this would come from a time-series database)
                points_count = min(1000, (end - start) // 1000)  # Max 1000 points, 1 per second
                for i in range(points_count):
                    point_time = start + (i * ((end - start) // points_count))
                    data_points.append(TimeSeriesDataPoint(
                        timestamp=point_time,
                        device_id=device.id,
                        signal_name=signal.name,
                        value=signal.value + (i * 0.1),  # Simulate some variation
                        unit=signal.unit
                    ))
        
        return TimeSeriesData(
            data_points=data_points,
            total_count=len(data_points),
            start_time=start,
            end_time=end
        )

    @app.websocket("/ws/data")
    async def websocket_data_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time data streaming"""
        await manager.connect(websocket, subscribe_to_data=True)
        try:
            while True:
                # Keep connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    @app.websocket("/ws/control")
    async def websocket_control_endpoint(websocket: WebSocket):
        """WebSocket endpoint for device control commands"""
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                # Process control commands here
                # For now, just echo back
                await manager.send_personal_message(f"Echo: {data}", websocket)
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    # Background task for broadcasting data
    async def broadcast_simulation_data():
        """Background task to broadcast simulation data to WebSocket subscribers"""
        while True:
            try:
                if manager.data_subscribers:
                    latest_data = await get_latest_data()
                    await manager.broadcast_data(latest_data)
                await asyncio.sleep(1.0)  # Broadcast every second
            except Exception as e:
                logger.error(f"Error in broadcast task: {e}")
                await asyncio.sleep(5.0)

    # Start background task
    asyncio.create_task(broadcast_simulation_data())

    return app


if __name__ == "__main__":
    # For testing the API standalone
    import uvicorn
    db = MultiTenantDatabase()
    app = create_app(db)
    uvicorn.run(app, host="0.0.0.0", port=8000)
