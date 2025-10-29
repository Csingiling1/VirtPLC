"""
Enhanced Web API for Factory Simulator

Provides REST API for device management and monitoring with real-time streaming
"""

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import time
from datetime import datetime
import logging

from database import DeviceDatabase
from models import FactoryDevice, SignalConfig, SignalGenerator

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


def create_app(database: DeviceDatabase) -> FastAPI:
    """Create FastAPI application"""

    app = FastAPI(
        title="VirtPLC Enhanced Simulator API",
        description="REST API for factory device management and monitoring with real-time streaming",
        version="2.0.0"
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

    # Real-time data streaming endpoints
    @app.get("/api/stream/latest")
    async def get_latest_data():
        """Get latest data from all devices - compatible with Spring backend"""
        devices = database.get_all_devices()
        current_time = int(time.time() * 1000)
        
        # Format data similar to Spring backend's SensorData model
        data = {
            "timestamp": current_time,
            "motor1Speed": 0.0,
            "motor1Temp": 0.0,
            "motor1Run": False,
            "motor1Fault": False,
            "motor2Speed": 0.0,
            "motor2Temp": 0.0,
            "motor2Run": False,
            "motor2Fault": False,
            "conveyor1Speed": 0.0,
            "conveyor1Run": False,
            "sensor1Value": 0.0,
            "sensor2Value": False,
            "systemStatus": "Running"
        }
        
        # Map device signals to the expected format
        for device in devices:
            if not device.is_active:
                continue
                
            for signal in device.signals:
                if device.device_type == "motor":
                    if "Motor1" in device.id or "motor1" in device.id.lower():
                        if signal.name.lower() in ["speed", "rpm"]:
                            data["motor1Speed"] = signal.value
                        elif signal.name.lower() in ["temperature", "temp"]:
                            data["motor1Temp"] = signal.value
                        elif signal.name.lower() in ["running", "run"]:
                            data["motor1Run"] = bool(signal.value)
                        elif signal.name.lower() in ["fault", "error"]:
                            data["motor1Fault"] = bool(signal.value)
                    elif "Motor2" in device.id or "motor2" in device.id.lower():
                        if signal.name.lower() in ["speed", "rpm"]:
                            data["motor2Speed"] = signal.value
                        elif signal.name.lower() in ["temperature", "temp"]:
                            data["motor2Temp"] = signal.value
                        elif signal.name.lower() in ["running", "run"]:
                            data["motor2Run"] = bool(signal.value)
                        elif signal.name.lower() in ["fault", "error"]:
                            data["motor2Fault"] = bool(signal.value)
                elif device.device_type == "conveyor":
                    if signal.name.lower() in ["speed"]:
                        data["conveyor1Speed"] = signal.value
                    elif signal.name.lower() in ["running", "run"]:
                        data["conveyor1Run"] = bool(signal.value)
                elif device.device_type == "sensor":
                    if "Sensor1" in device.id or "sensor1" in device.id.lower():
                        data["sensor1Value"] = signal.value
                    elif "Sensor2" in device.id or "sensor2" in device.id.lower():
                        data["sensor2Value"] = bool(signal.value)
        
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
    db = DeviceDatabase()
    app = create_app(db)
    uvicorn.run(app, host="0.0.0.0", port=8000)
