"""
Web API for Factory Simulator Monitoring

Provides REST API and web dashboard for monitoring simulator state
"""

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import json

app = FastAPI(
    title="VirtPLC Simulator API",
    description="Monitoring and control API for factory simulator",
    version="1.0.0"
)


class MotorStatus(BaseModel):
    name: str
    state: str
    speed: float
    target_speed: float
    temperature: float
    current: float
    voltage: float
    power: float
    vibration: float
    running: bool
    fault: bool
    fault_code: int


class ConveyorStatus(BaseModel):
    name: str
    state: str
    speed: float
    target_speed: float
    running: bool
    item_count: int


class SystemStatus(BaseModel):
    emergency_stop: bool
    motors: List[MotorStatus]
    conveyors: List[ConveyorStatus]
    uptime: float


# Global reference to simulator (set by main app)
simulator = None


def set_simulator(sim):
    """Set global simulator reference"""
    global simulator
    simulator = sim


@app.get("/")
async def root():
    """Root endpoint with links"""
    return {
        "name": "VirtPLC Simulator API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "status": "/api/status",
            "motors": "/api/motors",
            "conveyors": "/api/conveyors",
            "dashboard": "/dashboard"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/status", response_model=SystemStatus)
async def get_status():
    """Get complete system status"""
    if not simulator:
        return {"error": "Simulator not initialized"}
    
    motors_status = []
    for motor in simulator.motors:
        motors_status.append(MotorStatus(
            name=motor.name,
            state=motor.state.name,
            speed=motor.speed,
            target_speed=motor.target_speed,
            temperature=motor.temperature,
            current=motor.current,
            voltage=motor.voltage,
            power=motor.power,
            vibration=motor.vibration,
            running=motor.state.name == "RUNNING",
            fault=motor.fault_active,
            fault_code=motor.fault_code
        ))
    
    conveyors_status = []
    for conveyor in simulator.conveyors:
        conveyors_status.append(ConveyorStatus(
            name=conveyor.name,
            state=conveyor.state.name,
            speed=conveyor.speed,
            target_speed=conveyor.target_speed,
            running=conveyor.running,
            item_count=conveyor.item_count
        ))
    
    return SystemStatus(
        emergency_stop=simulator.emergency_stop_active,
        motors=motors_status,
        conveyors=conveyors_status,
        uptime=0.0  # TODO: track uptime
    )


@app.get("/api/motors")
async def get_motors():
    """Get all motor statuses"""
    if not simulator:
        return {"error": "Simulator not initialized"}
    
    motors = []
    for motor in simulator.motors:
        motors.append({
            "name": motor.name,
            "state": motor.state.name,
            "speed": round(motor.speed, 2),
            "target_speed": motor.target_speed,
            "temperature": round(motor.temperature, 2),
            "current": round(motor.current, 2),
            "voltage": round(motor.voltage, 2),
            "power": round(motor.power, 2),
            "vibration": round(motor.vibration, 2),
            "running": motor.state.name == "RUNNING",
            "fault": motor.fault_active,
            "fault_code": motor.fault_code
        })
    return {"motors": motors}


@app.get("/api/conveyors")
async def get_conveyors():
    """Get all conveyor statuses"""
    if not simulator:
        return {"error": "Simulator not initialized"}
    
    conveyors = []
    for conveyor in simulator.conveyors:
        conveyors.append({
            "name": conveyor.name,
            "state": conveyor.state.name,
            "speed": round(conveyor.speed, 2),
            "target_speed": conveyor.target_speed,
            "running": conveyor.running,
            "item_count": conveyor.item_count
        })
    return {"conveyors": conveyors}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Simple web dashboard"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VirtPLC Simulator Dashboard</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }
            .card h2 {
                margin-top: 0;
                font-size: 1.5em;
                border-bottom: 2px solid rgba(255,255,255,0.3);
                padding-bottom: 10px;
            }
            .metric {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            .metric:last-child {
                border-bottom: none;
            }
            .metric-label {
                font-weight: 600;
            }
            .metric-value {
                font-family: 'Courier New', monospace;
                background: rgba(0,0,0,0.2);
                padding: 2px 8px;
                border-radius: 4px;
            }
            .status-running {
                color: #4ade80;
                font-weight: bold;
            }
            .status-stopped {
                color: #cbd5e1;
            }
            .status-fault {
                color: #f87171;
                font-weight: bold;
            }
            .refresh-info {
                text-align: center;
                margin-top: 20px;
                opacity: 0.8;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏭 VirtPLC Factory Simulator</h1>
            
            <div id="status"></div>
            
            <div class="refresh-info">
                Auto-refreshing every 2 seconds | Last update: <span id="timestamp"></span>
            </div>
        </div>
        
        <script>
            async function updateStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    let html = '<div class="grid">';
                    
                    // Emergency stop indicator
                    html += `
                        <div class="card" style="background: ${data.emergency_stop ? 'rgba(248, 113, 113, 0.3)' : 'rgba(74, 222, 128, 0.2)'}">
                            <h2>🚨 Emergency Stop</h2>
                            <div class="metric">
                                <span class="metric-label">Status:</span>
                                <span class="metric-value ${data.emergency_stop ? 'status-fault' : 'status-running'}">
                                    ${data.emergency_stop ? 'ACTIVE' : 'NORMAL'}
                                </span>
                            </div>
                        </div>
                    `;
                    
                    // Motors
                    data.motors.forEach(motor => {
                        const statusClass = motor.fault ? 'status-fault' : 
                                          motor.running ? 'status-running' : 'status-stopped';
                        html += `
                            <div class="card">
                                <h2>⚙️ ${motor.name}</h2>
                                <div class="metric">
                                    <span class="metric-label">State:</span>
                                    <span class="metric-value ${statusClass}">${motor.state}</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Speed:</span>
                                    <span class="metric-value">${motor.speed.toFixed(1)} RPM</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Target:</span>
                                    <span class="metric-value">${motor.target_speed.toFixed(1)} RPM</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Temperature:</span>
                                    <span class="metric-value">${motor.temperature.toFixed(1)} °C</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Current:</span>
                                    <span class="metric-value">${motor.current.toFixed(2)} A</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Power:</span>
                                    <span class="metric-value">${(motor.power/1000).toFixed(2)} kW</span>
                                </div>
                                ${motor.fault ? `
                                <div class="metric">
                                    <span class="metric-label">Fault Code:</span>
                                    <span class="metric-value status-fault">${motor.fault_code}</span>
                                </div>
                                ` : ''}
                            </div>
                        `;
                    });
                    
                    // Conveyors
                    data.conveyors.forEach(conveyor => {
                        const statusClass = conveyor.running ? 'status-running' : 'status-stopped';
                        html += `
                            <div class="card">
                                <h2>📦 ${conveyor.name}</h2>
                                <div class="metric">
                                    <span class="metric-label">State:</span>
                                    <span class="metric-value ${statusClass}">${conveyor.state}</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Speed:</span>
                                    <span class="metric-value">${conveyor.speed.toFixed(1)} m/min</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Target:</span>
                                    <span class="metric-value">${conveyor.target_speed.toFixed(1)} m/min</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Item Count:</span>
                                    <span class="metric-value">${conveyor.item_count}</span>
                                </div>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    
                    document.getElementById('status').innerHTML = html;
                    document.getElementById('timestamp').textContent = new Date().toLocaleTimeString();
                } catch (error) {
                    console.error('Error fetching status:', error);
                }
            }
            
            // Initial update
            updateStatus();
            
            // Auto-refresh every 2 seconds
            setInterval(updateStatus, 2000);
        </script>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
