"""
Device Models for VirtPLC Simulator

Defines factory devices with configurable signals and generators.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import random
import math
from datetime import datetime


class SignalGenerator(Enum):
    """Available signal generators"""
    CONSTANT = "constant"
    UNIFORM = "uniform"
    NORMAL = "normal"
    EXPONENTIAL = "exponential"
    POISSON = "poisson"
    SINUSOIDAL = "sinusoidal"
    TRIANGULAR = "triangular"
    STEP = "step"


@dataclass
class SignalConfig:
    """Configuration for a single signal"""
    name: str
    unit: str
    value: float = 0.0
    generator: str = SignalGenerator.CONSTANT.value
    is_running: bool = True

    # Generator parameters
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean: Optional[float] = None
    std_dev: Optional[float] = None
    rate: Optional[float] = None  # For exponential/poisson
    frequency: Optional[float] = None  # For sinusoidal
    amplitude: Optional[float] = None  # For sinusoidal/triangular
    offset: Optional[float] = None  # For sinusoidal
    step_size: Optional[float] = None  # For step changes

    # Runtime state
    last_update: float = field(default_factory=lambda: datetime.now().timestamp())

    def generate_value(self) -> float:
        """Generate next value based on generator type"""
        if not self.is_running:
            return self.value

        current_time = datetime.now().timestamp()

        if self.generator == SignalGenerator.CONSTANT.value:
            return self.value

        elif self.generator == SignalGenerator.UNIFORM.value:
            if self.min_value is not None and self.max_value is not None:
                return random.uniform(self.min_value, self.max_value)
            return self.value

        elif self.generator == SignalGenerator.NORMAL.value:
            if self.mean is not None and self.std_dev is not None:
                return random.gauss(self.mean, self.std_dev)
            return self.value

        elif self.generator == SignalGenerator.EXPONENTIAL.value:
            if self.rate is not None:
                return random.expovariate(self.rate)
            return self.value

        elif self.generator == SignalGenerator.POISSON.value:
            if self.rate is not None:
                return random.expovariate(self.rate)  # Poisson process
            return self.value

        elif self.generator == SignalGenerator.SINUSOIDAL.value:
            if self.frequency is not None and self.amplitude is not None:
                offset = self.offset or 0.0
                time_diff = current_time - self.last_update
                phase = 2 * math.pi * self.frequency * time_diff
                return offset + self.amplitude * math.sin(phase)
            return self.value

        elif self.generator == SignalGenerator.TRIANGULAR.value:
            if self.min_value is not None and self.max_value is not None:
                return random.triangular(self.min_value, self.max_value)
            return self.value

        elif self.generator == SignalGenerator.STEP.value:
            if self.step_size is not None:
                # Random step changes
                if random.random() < 0.1:  # 10% chance of step change
                    step = random.choice([-1, 1]) * self.step_size
                    self.value += step
                return self.value
            return self.value

        return self.value


@dataclass
class Sensor:
    """Individual sensor within a PLC"""
    id: str
    name: str
    signal_config: SignalConfig
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "signal_config": {
                "name": self.signal_config.name,
                "unit": self.signal_config.unit,
                "value": self.signal_config.value,
                "generator": self.signal_config.generator,
                "is_running": self.signal_config.is_running,
                "min_value": self.signal_config.min_value,
                "max_value": self.signal_config.max_value,
                "mean": self.signal_config.mean,
                "std_dev": self.signal_config.std_dev,
                "rate": self.signal_config.rate,
                "frequency": self.signal_config.frequency,
                "amplitude": self.signal_config.amplitude,
                "offset": self.signal_config.offset,
                "step_size": self.signal_config.step_size,
            },
            "is_active": self.is_active,
        }


@dataclass
class PLC:
    """Programmable Logic Controller within a factory"""
    id: str
    name: str
    description: Optional[str] = None
    sensors: List[Sensor] = field(default_factory=list)
    is_active: bool = True
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())
    # Position within factory (in meters from top-left corner)
    x_position: float = 0.0
    y_position: float = 0.0
    # Physical dimensions (in meters)
    width: float = 2.0
    height: float = 1.5

    def update_sensors(self):
        """Update all sensors with new generated values"""
        for sensor in self.sensors:
            if sensor.is_active and sensor.signal_config.is_running:
                sensor.signal_config.value = sensor.signal_config.generate_value()
                sensor.signal_config.last_update = datetime.now().timestamp()
        self.updated_at = datetime.now().timestamp()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "sensors": [sensor.to_dict() for sensor in self.sensors],
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "x_position": self.x_position,
            "y_position": self.y_position,
            "width": self.width,
            "height": self.height,
        }


@dataclass
class Factory:
    """Factory within a manufacturer"""
    id: str
    name: str
    description: Optional[str] = None
    plcs: List[PLC] = field(default_factory=list)
    is_active: bool = True
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())
    # Factory layout properties
    shape: str = "rectangle"  # rectangle, L, I, Z, U, T shapes
    width: int = 100  # Width in meters
    height: int = 80  # Height in meters
    width_meters: float = 50.0  # Actual width in meters for visualization
    height_meters: float = 40.0  # Actual height in meters for visualization
    wireframe_color: str = "#3b82f6"  # Blue color for wireframe

    def update_plcs(self):
        """Update all PLCs and their sensors"""
        for plc in self.plcs:
            plc.update_sensors()
        self.updated_at = datetime.now().timestamp()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "plcs": [plc.to_dict() for plc in self.plcs],
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "shape": self.shape,
            "width": self.width,
            "height": self.height,
            "width_meters": self.width_meters,
            "height_meters": self.height_meters,
            "wireframe_color": self.wireframe_color,
        }


@dataclass
class Manufacturer:
    """Manufacturer within a tenant"""
    id: str
    name: str
    description: Optional[str] = None
    factories: List[Factory] = field(default_factory=list)
    is_active: bool = True
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())

    def update_factories(self):
        """Update all factories and their PLCs"""
        for factory in self.factories:
            factory.update_plcs()
        self.updated_at = datetime.now().timestamp()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "factories": [factory.to_dict() for factory in self.factories],
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class Tenant:
    """Top-level tenant containing manufacturers"""
    id: str
    name: str
    description: Optional[str] = None
    manufacturers: List[Manufacturer] = field(default_factory=list)
    is_active: bool = True
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())

    def update_manufacturers(self):
        """Update all manufacturers and their factories"""
        for manufacturer in self.manufacturers:
            manufacturer.update_factories()
        self.updated_at = datetime.now().timestamp()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "manufacturers": [manufacturer.to_dict() for manufacturer in self.manufacturers],
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }