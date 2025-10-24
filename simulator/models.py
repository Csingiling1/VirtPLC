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
class FactoryDevice:
    """Factory device with multiple signals"""
    id: str
    name: str
    description: Optional[str] = None
    device_type: str = "generic"  # motor, conveyor, sensor, valve, etc.
    signals: List[SignalConfig] = field(default_factory=list)
    is_active: bool = True
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())

    def update_signals(self):
        """Update all signals with new generated values"""
        for signal in self.signals:
            if signal.is_running:
                signal.value = signal.generate_value()
                signal.last_update = datetime.now().timestamp()
        self.updated_at = datetime.now().timestamp()

    def get_signal_value(self, signal_name: str) -> Optional[float]:
        """Get value of a specific signal"""
        for signal in self.signals:
            if signal.name == signal_name:
                return signal.value
        return None

    def set_signal_value(self, signal_name: str, value: float):
        """Set value of a specific signal"""
        for signal in self.signals:
            if signal.name == signal_name:
                signal.value = value
                signal.last_update = datetime.now().timestamp()
                break

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "device_type": self.device_type,
            "signals": [
                {
                    "name": s.name,
                    "unit": s.unit,
                    "value": s.value,
                    "generator": s.generator,
                    "is_running": s.is_running,
                    "min_value": s.min_value,
                    "max_value": s.max_value,
                    "mean": s.mean,
                    "std_dev": s.std_dev,
                    "rate": s.rate,
                    "frequency": s.frequency,
                    "amplitude": s.amplitude,
                    "offset": s.offset,
                    "step_size": s.step_size,
                }
                for s in self.signals
            ],
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FactoryDevice':
        """Create from dictionary"""
        signals = []
        for s_data in data.get("signals", []):
            signal = SignalConfig(
                name=s_data["name"],
                unit=s_data["unit"],
                value=s_data.get("value", 0.0),
                generator=s_data.get("generator", SignalGenerator.CONSTANT.value),
                is_running=s_data.get("is_running", True),
                min_value=s_data.get("min_value"),
                max_value=s_data.get("max_value"),
                mean=s_data.get("mean"),
                std_dev=s_data.get("std_dev"),
                rate=s_data.get("rate"),
                frequency=s_data.get("frequency"),
                amplitude=s_data.get("amplitude"),
                offset=s_data.get("offset"),
                step_size=s_data.get("step_size"),
            )
            signals.append(signal)

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            device_type=data.get("device_type", "generic"),
            signals=signals,
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", datetime.now().timestamp()),
            updated_at=data.get("updated_at", datetime.now().timestamp()),
        )