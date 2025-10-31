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

    @app.get("/simulation/status")
    async def simulation_status():
        """Health check endpoint for Docker"""
        return {"status": "healthy", "timestamp": int(time.time() * 1000)}

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

    # Simulator API endpoints (flat device representation for frontend compatibility)
    @app.get("/api/simulator/devices")
    async def get_simulator_devices():
        """Get all devices in flat format for frontend compatibility"""
        tenants = database.get_all_tenants()
        devices = []

        for tenant in tenants:
            if not tenant.is_active:
                continue

            for manufacturer in tenant.manufacturers:
                if not manufacturer.is_active:
                    continue

                for factory in manufacturer.factories:
                    if not factory.is_active:
                        continue

                    for plc in factory.plcs:
                        if not plc.is_active:
                            continue

                        # Convert PLC to device format
                        device = {
                            "id": plc.id,
                            "name": plc.name,
                            "description": plc.description or f"PLC in {factory.name}",
                            "deviceType": "plc",
                            "signals": [
                                {
                                    "name": sensor.signal_config.name,
                                    "unit": sensor.signal_config.unit,
                                    "value": sensor.signal_config.value,
                                    "generator": sensor.signal_config.generator,
                                    "isRunning": sensor.signal_config.is_running,
                                    "minValue": sensor.signal_config.min_value,
                                    "maxValue": sensor.signal_config.max_value,
                                    "mean": sensor.signal_config.mean,
                                    "stdDev": sensor.signal_config.std_dev,
                                    "rate": sensor.signal_config.rate,
                                    "frequency": sensor.signal_config.frequency,
                                    "amplitude": sensor.signal_config.amplitude,
                                    "offset": sensor.signal_config.offset,
                                    "stepSize": sensor.signal_config.step_size,
                                    "lastUpdate": int(sensor.signal_config.last_update * 1000)
                                }
                                for sensor in plc.sensors if sensor.is_active
                            ],
                            "is_active": plc.is_active,
                            "created_at": int(plc.created_at * 1000),
                            "updated_at": int(plc.updated_at * 1000)
                        }
                        devices.append(device)

        return devices

    @app.post("/api/simulator/devices")
    async def create_simulator_device(device: dict):
        """Create a new device (PLC)"""
        try:
            # For now, create a simple PLC with basic sensors
            tenant_id = device.get("tenantId", "demo-tenant")
            manufacturer_id = device.get("manufacturerId", "demo-mfg")
            factory_id = device.get("factoryId", "demo-factory")

            # Get or create tenant
            tenant = database.get_tenant(tenant_id)
            if not tenant:
                tenant = Tenant(id=tenant_id, name=device.get("tenantName", "New Tenant"))
                tenant = database.create_tenant(tenant)

            # Get or create manufacturer
            manufacturer = None
            for m in tenant.manufacturers:
                if m.id == manufacturer_id:
                    manufacturer = m
                    break
            if not manufacturer:
                manufacturer = Manufacturer(id=manufacturer_id, name=device.get("manufacturerName", "New Manufacturer"))
                tenant.manufacturers.append(manufacturer)

            # Get or create factory
            factory = None
            for f in manufacturer.factories:
                if f.id == factory_id:
                    factory = f
                    break
            if not factory:
                factory = Factory(id=factory_id, name=device.get("factoryName", "New Factory"))
                manufacturer.factories.append(factory)

            # Create PLC
            plc_id = device.get("id", f"plc-{int(time.time())}")
            plc = PLC(
                id=plc_id,
                name=device.get("name", "New PLC"),
                description=device.get("description", "Auto-created PLC")
            )

            # Add default sensors if none provided
            if not device.get("signals"):
                sensors_data = [
                    ("temperature", "Temperature Sensor", "°C", 25.0, "normal", 20.0, 30.0),
                    ("pressure", "Pressure Sensor", "bar", 1.0, "uniform", 0.8, 1.2),
                    ("flow_rate", "Flow Rate Sensor", "L/min", 50.0, "normal", 40.0, 60.0),
                ]
                for sensor_name, description, unit, value, generator, min_val, max_val in sensors_data:
                    sensor = Sensor(
                        id=f"{sensor_name}_{plc_id}",
                        name=description,
                        signal_config=SignalConfig(
                            name=sensor_name,
                            unit=unit,
                            value=value,
                            generator=generator,
                            min_value=min_val,
                            max_value=max_val
                        )
                    )
                    plc.sensors.append(sensor)
            else:
                # Add provided signals as sensors
                for signal in device.get("signals", []):
                    sensor = Sensor(
                        id=f"{signal['name']}_{plc_id}",
                        name=signal.get("name", "Sensor"),
                        signal_config=SignalConfig(
                            name=signal["name"],
                            unit=signal["unit"],
                            value=signal.get("value", 0.0),
                            generator=signal.get("generator", "constant"),
                            min_value=signal.get("minValue"),
                            max_value=signal.get("maxValue"),
                            mean=signal.get("mean"),
                            std_dev=signal.get("stdDev"),
                            rate=signal.get("rate"),
                            frequency=signal.get("frequency"),
                            amplitude=signal.get("amplitude"),
                            offset=signal.get("offset"),
                            step_size=signal.get("stepSize")
                        )
                    )
                    plc.sensors.append(sensor)

            factory.plcs.append(plc)
            database._save_tenants()

            return {
                "id": plc.id,
                "name": plc.name,
                "description": plc.description,
                "deviceType": "plc",
                "signals": [
                    {
                        "name": sensor.signal_config.name,
                        "unit": sensor.signal_config.unit,
                        "value": sensor.signal_config.value,
                        "generator": sensor.signal_config.generator,
                        "isRunning": sensor.signal_config.is_running,
                        "lastUpdate": int(sensor.signal_config.last_update * 1000)
                    }
                    for sensor in plc.sensors
                ],
                "is_active": plc.is_active,
                "created_at": int(plc.created_at * 1000),
                "updated_at": int(plc.updated_at * 1000)
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.delete("/api/simulator/devices/{device_id}")
    async def delete_simulator_device(device_id: str):
        """Delete a device (PLC)"""
        # Find and remove the PLC from the hierarchy
        tenants = database.get_all_tenants()
        for tenant in tenants:
            for manufacturer in tenant.manufacturers:
                for factory in manufacturer.factories:
                    for i, plc in enumerate(factory.plcs):
                        if plc.id == device_id:
                            factory.plcs.pop(i)
                            database._save_tenants()
                            return {"message": f"Device {device_id} deleted"}

        raise HTTPException(status_code=404, detail="Device not found")

    @app.get("/api/simulator/status")
    async def get_simulator_status():
        """Get simulator status"""
        tenants = database.get_all_tenants()
        total_devices = 0
        total_signals = 0

        for tenant in tenants:
            if tenant.is_active:
                for manufacturer in tenant.manufacturers:
                    if manufacturer.is_active:
                        for factory in manufacturer.factories:
                            if factory.is_active:
                                for plc in factory.plcs:
                                    if plc.is_active:
                                        total_devices += 1
                                        total_signals += len([s for s in plc.sensors if s.is_active])

        return {
            "isRunning": True,
            "activeDevices": total_devices,
            "totalSignals": total_signals,
            "lastUpdate": int(time.time() * 1000)
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
