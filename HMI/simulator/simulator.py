"""
VirtPLC Factory Simulator

Realistic PLC simulation with state machines for:
- Motors with temperature, vibration, and fault conditions
- Conveyors with item counting and speed control
- Emergency stop system
- OPC-UA server for Ignition Edge integration
"""

import asyncio
import random
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List
import logging
from datetime import datetime

from asyncua import Server, ua
from asyncua.common.methods import uamethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MotorState(Enum):
    """Motor state machine states"""
    STOPPED = 0
    STARTING = 1
    RUNNING = 2
    STOPPING = 3
    FAULTED = 4
    EMERGENCY_STOP = 5


class ConveyorState(Enum):
    """Conveyor state machine states"""
    STOPPED = 0
    STARTING = 1
    RUNNING = 2
    STOPPING = 3
    FAULTED = 4
    EMERGENCY_STOP = 5


@dataclass
class MotorSimulation:
    """Realistic motor simulation with physics"""
    name: str
    state: MotorState = MotorState.STOPPED
    speed: float = 0.0  # Current speed (RPM)
    target_speed: float = 0.0  # Target speed (RPM)
    temperature: float = 25.0  # °C
    current: float = 0.0  # Amperes
    voltage: float = 0.0  # Volts
    power: float = 0.0  # Watts
    vibration: float = 0.0  # mm/s
    running_hours: float = 0.0  # Total running hours
    start_command: bool = False
    stop_command: bool = False
    reset_command: bool = False
    fault_active: bool = False
    fault_code: int = 0
    emergency_stop: bool = False
    
    # Physical constants
    MAX_SPEED: float = 2200.0  # RPM
    MIN_SPEED: float = 100.0  # RPM
    ACCELERATION: float = 50.0  # RPM/s
    DECELERATION: float = 100.0  # RPM/s
    AMBIENT_TEMP: float = 25.0  # °C
    HEATING_RATE: float = 0.5  # °C per second at full load
    COOLING_RATE: float = 0.2  # °C per second when stopped
    MAX_TEMP: float = 85.0  # °C
    OVERTEMP_THRESHOLD: float = 80.0  # °C
    RATED_VOLTAGE: float = 400.0  # Volts
    RATED_CURRENT: float = 10.0  # Amperes at full load
    
    async def update(self, dt: float):
        """Update motor simulation (called every dt seconds)"""
        
        # Emergency stop overrides everything
        if self.emergency_stop:
            self.state = MotorState.EMERGENCY_STOP
            self.target_speed = 0.0
            self.start_command = False
            return
        
        # State machine
        if self.state == MotorState.STOPPED:
            if self.start_command and not self.fault_active:
                self.state = MotorState.STARTING
                logger.info(f"{self.name}: Starting")
            
        elif self.state == MotorState.STARTING:
            if self.stop_command or self.emergency_stop:
                self.state = MotorState.STOPPING
            elif self.fault_active:
                self.state = MotorState.FAULTED
            elif abs(self.speed - self.target_speed) < 10.0:
                self.state = MotorState.RUNNING
                logger.info(f"{self.name}: Running at {self.speed:.1f} RPM")
            
        elif self.state == MotorState.RUNNING:
            if self.stop_command or self.emergency_stop:
                self.state = MotorState.STOPPING
                self.target_speed = 0.0
            elif self.fault_active:
                self.state = MotorState.FAULTED
                self.target_speed = 0.0
            
        elif self.state == MotorState.STOPPING:
            if self.speed < 1.0:
                self.state = MotorState.STOPPED
                self.speed = 0.0
                self.stop_command = False
                logger.info(f"{self.name}: Stopped")
            
        elif self.state == MotorState.FAULTED:
            if self.reset_command and not self.fault_active:
                self.state = MotorState.STOPPED
                self.reset_command = False
                self.fault_code = 0
                logger.info(f"{self.name}: Fault cleared")
            
        elif self.state == MotorState.EMERGENCY_STOP:
            if not self.emergency_stop and self.reset_command:
                self.state = MotorState.STOPPED
                self.reset_command = False
                logger.info(f"{self.name}: E-stop cleared")
        
        # Physics simulation
        await self._update_speed(dt)
        await self._update_temperature(dt)
        await self._update_electrical(dt)
        await self._update_vibration(dt)
        await self._check_faults()
        
        # Update running hours
        if self.state == MotorState.RUNNING:
            self.running_hours += dt / 3600.0
    
    async def _update_speed(self, dt: float):
        """Update motor speed with acceleration/deceleration"""
        if self.state in [MotorState.RUNNING, MotorState.STARTING]:
            # Clamp target speed
            self.target_speed = max(self.MIN_SPEED, min(self.MAX_SPEED, self.target_speed))
            
            # Accelerate or decelerate
            if self.speed < self.target_speed:
                self.speed += self.ACCELERATION * dt
                self.speed = min(self.speed, self.target_speed)
            elif self.speed > self.target_speed:
                self.speed -= self.DECELERATION * dt
                self.speed = max(self.speed, self.target_speed)
        
        elif self.state in [MotorState.STOPPING, MotorState.FAULTED, MotorState.EMERGENCY_STOP]:
            # Decelerate to stop
            self.speed -= self.DECELERATION * dt
            self.speed = max(0.0, self.speed)
    
    async def _update_temperature(self, dt: float):
        """Update motor temperature based on load"""
        load_factor = self.speed / self.MAX_SPEED
        
        if self.state in [MotorState.RUNNING, MotorState.STARTING]:
            # Heating when running
            temp_increase = self.HEATING_RATE * load_factor * dt
            # Add random fluctuation
            temp_increase += random.gauss(0, 0.1) * dt
            self.temperature += temp_increase
        else:
            # Cooling when stopped
            temp_decrease = self.COOLING_RATE * (self.temperature - self.AMBIENT_TEMP) * dt
            self.temperature -= temp_decrease
        
        # Clamp temperature
        self.temperature = max(self.AMBIENT_TEMP, min(self.MAX_TEMP, self.temperature))
    
    async def _update_electrical(self, dt: float):
        """Update electrical parameters"""
        load_factor = self.speed / self.MAX_SPEED
        
        if self.state in [MotorState.RUNNING, MotorState.STARTING]:
            # Voltage relatively constant
            self.voltage = self.RATED_VOLTAGE + random.gauss(0, 5)
            
            # Current proportional to load
            self.current = self.RATED_CURRENT * load_factor + random.gauss(0, 0.5)
            self.current = max(0, self.current)
            
            # Power = Voltage * Current * power factor (0.85)
            self.power = self.voltage * self.current * 0.85
        else:
            self.voltage = 0.0
            self.current = 0.0
            self.power = 0.0
    
    async def _update_vibration(self, dt: float):
        """Update vibration levels"""
        if self.state in [MotorState.RUNNING, MotorState.STARTING]:
            # Base vibration increases with speed
            base_vib = (self.speed / self.MAX_SPEED) * 2.0  # mm/s
            
            # Add random fluctuation
            self.vibration = base_vib + random.gauss(0, 0.3)
            self.vibration = max(0, self.vibration)
            
            # High temperature increases vibration
            if self.temperature > self.OVERTEMP_THRESHOLD:
                self.vibration *= 1.5
        else:
            self.vibration = 0.0
    
    async def _check_faults(self):
        """Check for fault conditions"""
        # Overspeed fault
        if self.speed > self.MAX_SPEED * 1.1:
            self.fault_active = True
            self.fault_code = 101  # Overspeed
            logger.warning(f"{self.name}: FAULT - Overspeed ({self.speed:.1f} RPM)")
        
        # Overtemperature fault
        elif self.temperature > self.OVERTEMP_THRESHOLD:
            self.fault_active = True
            self.fault_code = 102  # Overtemperature
            logger.warning(f"{self.name}: FAULT - Overtemperature ({self.temperature:.1f} °C)")
        
        # Random fault simulation (1% chance per second)
        elif self.state == MotorState.RUNNING and random.random() < 0.01:
            self.fault_active = True
            self.fault_code = random.choice([103, 104, 105])  # Various faults
            logger.warning(f"{self.name}: FAULT - Code {self.fault_code}")


@dataclass
class ConveyorSimulation:
    """Realistic conveyor simulation"""
    name: str
    state: ConveyorState = ConveyorState.STOPPED
    speed: float = 0.0  # m/min
    target_speed: float = 0.0  # m/min
    item_count: int = 0
    running: bool = False
    start_command: bool = False
    stop_command: bool = False
    reset_command: bool = False
    fault_active: bool = False
    emergency_stop: bool = False
    motor_interlock: bool = False  # Requires motor to be running
    
    # Physical constants
    MAX_SPEED: float = 60.0  # m/min
    ACCELERATION: float = 5.0  # m/min/s
    ITEM_DETECTION_RATE: float = 0.5  # items per second average
    
    # Internal state
    _time_since_item: float = 0.0
    
    async def update(self, dt: float, motor_running: bool = False):
        """Update conveyor simulation"""
        
        # Update motor interlock
        self.motor_interlock = motor_running
        
        # Emergency stop overrides everything
        if self.emergency_stop:
            self.state = ConveyorState.EMERGENCY_STOP
            self.target_speed = 0.0
            self.start_command = False
            return
        
        # State machine
        if self.state == ConveyorState.STOPPED:
            if self.start_command and self.motor_interlock and not self.fault_active:
                self.state = ConveyorState.STARTING
                logger.info(f"{self.name}: Starting")
            elif self.start_command and not self.motor_interlock:
                logger.warning(f"{self.name}: Cannot start - motor interlock not satisfied")
        
        elif self.state == ConveyorState.STARTING:
            if self.stop_command or self.emergency_stop or not self.motor_interlock:
                self.state = ConveyorState.STOPPING
            elif abs(self.speed - self.target_speed) < 1.0:
                self.state = ConveyorState.RUNNING
                logger.info(f"{self.name}: Running at {self.speed:.1f} m/min")
        
        elif self.state == ConveyorState.RUNNING:
            if self.stop_command or self.emergency_stop or not self.motor_interlock:
                self.state = ConveyorState.STOPPING
                self.target_speed = 0.0
        
        elif self.state == ConveyorState.STOPPING:
            if self.speed < 0.1:
                self.state = ConveyorState.STOPPED
                self.speed = 0.0
                self.stop_command = False
                logger.info(f"{self.name}: Stopped")
        
        elif self.state == ConveyorState.EMERGENCY_STOP:
            if not self.emergency_stop and self.reset_command:
                self.state = ConveyorState.STOPPED
                self.reset_command = False
                logger.info(f"{self.name}: E-stop cleared")
        
        # Physics simulation
        await self._update_speed(dt)
        await self._update_item_detection(dt)
        
        # Update running flag
        self.running = self.state == ConveyorState.RUNNING
    
    async def _update_speed(self, dt: float):
        """Update conveyor speed"""
        if self.state in [ConveyorState.RUNNING, ConveyorState.STARTING]:
            # Accelerate to target
            if self.speed < self.target_speed:
                self.speed += self.ACCELERATION * dt
                self.speed = min(self.speed, self.target_speed)
        else:
            # Decelerate to stop
            self.speed -= self.ACCELERATION * dt
            self.speed = max(0.0, self.speed)
    
    async def _update_item_detection(self, dt: float):
        """Simulate item detection on conveyor"""
        if self.state == ConveyorState.RUNNING and self.speed > 10.0:
            self._time_since_item += dt
            
            # Poisson-like item arrival
            expected_time = 1.0 / self.ITEM_DETECTION_RATE
            if self._time_since_item >= expected_time:
                if random.random() < 0.8:  # 80% chance
                    self.item_count += 1
                    self._time_since_item = 0.0
                    logger.debug(f"{self.name}: Item detected (count: {self.item_count})")


class FactorySimulator:
    """Main factory simulator with OPC-UA server"""
    
    def __init__(self):
        self.running = False
        self.emergency_stop_active = False
        self.system_reset_command = False
        
        # Create equipment
        self.motors: List[MotorSimulation] = [
            MotorSimulation(name="Motor1", target_speed=1800.0),
            MotorSimulation(name="Motor2", target_speed=1500.0),
        ]
        
        self.conveyors: List[ConveyorSimulation] = [
            ConveyorSimulation(name="Conveyor1", target_speed=30.0),
        ]
        
        # OPC-UA server
        self.opcua_server = None
        self.opcua_nodes = {}
        
    async def init_opcua_server(self):
        """Initialize OPC-UA server"""
        self.opcua_server = Server()
        await self.opcua_server.init()
        
        self.opcua_server.set_endpoint("opc.tcp://0.0.0.0:4840/virtplc/")
        self.opcua_server.set_server_name("VirtPLC Factory Simulator")
        
        # Setup namespaces
        uri = "http://virtplc.simulator"
        idx = await self.opcua_server.register_namespace(uri)
        
        # Create object node for factory
        objects = self.opcua_server.get_objects_node()
        factory = await objects.add_object(idx, "Factory")
        
        # System nodes
        system = await factory.add_object(idx, "System")
        self.opcua_nodes['EmergencyStop'] = await system.add_variable(
            idx, "EmergencyStop", False
        )
        await self.opcua_nodes['EmergencyStop'].set_writable()
        
        self.opcua_nodes['SystemReset'] = await system.add_variable(
            idx, "SystemReset", False
        )
        await self.opcua_nodes['SystemReset'].set_writable()
        
        # Motor nodes
        for i, motor in enumerate(self.motors, 1):
            motor_node = await factory.add_object(idx, f"Motor{i}")
            
            self.opcua_nodes[f'Motor{i}.Speed'] = await motor_node.add_variable(
                idx, "Speed", 0.0
            )
            self.opcua_nodes[f'Motor{i}.TargetSpeed'] = await motor_node.add_variable(
                idx, "TargetSpeed", motor.target_speed
            )
            await self.opcua_nodes[f'Motor{i}.TargetSpeed'].set_writable()
            
            self.opcua_nodes[f'Motor{i}.Running'] = await motor_node.add_variable(
                idx, "Running", False
            )
            self.opcua_nodes[f'Motor{i}.Fault'] = await motor_node.add_variable(
                idx, "Fault", False
            )
            self.opcua_nodes[f'Motor{i}.FaultCode'] = await motor_node.add_variable(
                idx, "FaultCode", 0
            )
            self.opcua_nodes[f'Motor{i}.Temperature'] = await motor_node.add_variable(
                idx, "Temperature", 25.0
            )
            self.opcua_nodes[f'Motor{i}.Current'] = await motor_node.add_variable(
                idx, "Current", 0.0
            )
            self.opcua_nodes[f'Motor{i}.Voltage'] = await motor_node.add_variable(
                idx, "Voltage", 0.0
            )
            self.opcua_nodes[f'Motor{i}.Power'] = await motor_node.add_variable(
                idx, "Power", 0.0
            )
            self.opcua_nodes[f'Motor{i}.Vibration'] = await motor_node.add_variable(
                idx, "Vibration", 0.0
            )
            
            # Commands
            self.opcua_nodes[f'Motor{i}.StartCommand'] = await motor_node.add_variable(
                idx, "StartCommand", False
            )
            await self.opcua_nodes[f'Motor{i}.StartCommand'].set_writable()
            
            self.opcua_nodes[f'Motor{i}.StopCommand'] = await motor_node.add_variable(
                idx, "StopCommand", False
            )
            await self.opcua_nodes[f'Motor{i}.StopCommand'].set_writable()
            
            self.opcua_nodes[f'Motor{i}.ResetCommand'] = await motor_node.add_variable(
                idx, "ResetCommand", False
            )
            await self.opcua_nodes[f'Motor{i}.ResetCommand'].set_writable()
        
        # Conveyor nodes
        for i, conveyor in enumerate(self.conveyors, 1):
            conv_node = await factory.add_object(idx, f"Conveyor{i}")
            
            self.opcua_nodes[f'Conveyor{i}.Speed'] = await conv_node.add_variable(
                idx, "Speed", 0.0
            )
            self.opcua_nodes[f'Conveyor{i}.TargetSpeed'] = await conv_node.add_variable(
                idx, "TargetSpeed", conveyor.target_speed
            )
            await self.opcua_nodes[f'Conveyor{i}.TargetSpeed'].set_writable()
            
            self.opcua_nodes[f'Conveyor{i}.Running'] = await conv_node.add_variable(
                idx, "Running", False
            )
            self.opcua_nodes[f'Conveyor{i}.ItemCount'] = await conv_node.add_variable(
                idx, "ItemCount", 0
            )
            
            # Commands
            self.opcua_nodes[f'Conveyor{i}.StartCommand'] = await conv_node.add_variable(
                idx, "StartCommand", False
            )
            await self.opcua_nodes[f'Conveyor{i}.StartCommand'].set_writable()
            
            self.opcua_nodes[f'Conveyor{i}.StopCommand'] = await conv_node.add_variable(
                idx, "StopCommand", False
            )
            await self.opcua_nodes[f'Conveyor{i}.StopCommand'].set_writable()
        
        logger.info("OPC-UA server initialized")
    
    async def start(self):
        """Start the simulator"""
        await self.init_opcua_server()
        await self.opcua_server.start()
        logger.info("OPC-UA server started at opc.tcp://0.0.0.0:4840/virtplc/")
        
        self.running = True
        
        # Main simulation loop
        last_time = time.time()
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Read commands from OPC-UA
            await self._read_opcua_commands()
            
            # Update emergency stop
            for motor in self.motors:
                motor.emergency_stop = self.emergency_stop_active
            for conveyor in self.conveyors:
                conveyor.emergency_stop = self.emergency_stop_active
            
            # Update simulations
            for i, motor in enumerate(self.motors):
                await motor.update(dt)
            
            for i, conveyor in enumerate(self.conveyors):
                # Conveyor interlock with Motor1
                motor_running = self.motors[0].state == MotorState.RUNNING
                await conveyor.update(dt, motor_running)
            
            # Write values to OPC-UA
            await self._write_opcua_values()
            
            # Sleep to control update rate (100ms = 10 Hz)
            await asyncio.sleep(0.1)
    
    async def _read_opcua_commands(self):
        """Read command values from OPC-UA"""
        # System commands
        self.emergency_stop_active = await self.opcua_nodes['EmergencyStop'].read_value()
        self.system_reset_command = await self.opcua_nodes['SystemReset'].read_value()
        
        # Motor commands
        for i, motor in enumerate(self.motors, 1):
            motor.start_command = await self.opcua_nodes[f'Motor{i}.StartCommand'].read_value()
            motor.stop_command = await self.opcua_nodes[f'Motor{i}.StopCommand'].read_value()
            motor.reset_command = await self.opcua_nodes[f'Motor{i}.ResetCommand'].read_value()
            motor.target_speed = await self.opcua_nodes[f'Motor{i}.TargetSpeed'].read_value()
        
        # Conveyor commands
        for i, conveyor in enumerate(self.conveyors, 1):
            conveyor.start_command = await self.opcua_nodes[f'Conveyor{i}.StartCommand'].read_value()
            conveyor.stop_command = await self.opcua_nodes[f'Conveyor{i}.StopCommand'].read_value()
            conveyor.target_speed = await self.opcua_nodes[f'Conveyor{i}.TargetSpeed'].read_value()
    
    async def _write_opcua_values(self):
        """Write simulation values to OPC-UA"""
        # Motor values
        for i, motor in enumerate(self.motors, 1):
            await self.opcua_nodes[f'Motor{i}.Speed'].write_value(motor.speed)
            await self.opcua_nodes[f'Motor{i}.Running'].write_value(
                motor.state == MotorState.RUNNING
            )
            await self.opcua_nodes[f'Motor{i}.Fault'].write_value(motor.fault_active)
            await self.opcua_nodes[f'Motor{i}.FaultCode'].write_value(motor.fault_code)
            await self.opcua_nodes[f'Motor{i}.Temperature'].write_value(motor.temperature)
            await self.opcua_nodes[f'Motor{i}.Current'].write_value(motor.current)
            await self.opcua_nodes[f'Motor{i}.Voltage'].write_value(motor.voltage)
            await self.opcua_nodes[f'Motor{i}.Power'].write_value(motor.power)
            await self.opcua_nodes[f'Motor{i}.Vibration'].write_value(motor.vibration)
        
        # Conveyor values
        for i, conveyor in enumerate(self.conveyors, 1):
            await self.opcua_nodes[f'Conveyor{i}.Speed'].write_value(conveyor.speed)
            await self.opcua_nodes[f'Conveyor{i}.Running'].write_value(conveyor.running)
            await self.opcua_nodes[f'Conveyor{i}.ItemCount'].write_value(conveyor.item_count)
    
    async def stop(self):
        """Stop the simulator"""
        self.running = False
        if self.opcua_server:
            await self.opcua_server.stop()
        logger.info("Simulator stopped")


async def main():
    """Main entry point"""
    simulator = FactorySimulator()
    
    try:
        await simulator.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await simulator.stop()


if __name__ == "__main__":
    asyncio.run(main())
