"""
Test package for VirtPLC AI Service

This package contains comprehensive unit tests, integration tests,
and performance tests for all components of the AI service.
"""
import pytest

# Test configuration
pytest_plugins = ["pytest_asyncio"]

# Common test fixtures and utilities
from typing import Dict, Any
import asyncio
from unittest.mock import AsyncMock, MagicMock


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient for testing"""
    with pytest.importorskip("httpx"):
        from unittest.mock import patch

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            yield mock_instance


@pytest.fixture
def mock_timebase_client():
    """Mock TimeBase client for testing"""
    mock_client = MagicMock()
    mock_client.connect = AsyncMock()
    mock_client.disconnect = AsyncMock()
    mock_client.query = AsyncMock()
    mock_client.get_writer = MagicMock()
    return mock_client


@pytest.fixture
def sample_sensor_data():
    """Sample sensor data for testing"""
    return {
        "timestamp": "2025-10-26T10:00:00Z",
        "symbol": "Motor1",
        "metric_type": "temperature",
        "value": 75.5,
        "unit": "celsius",
        "quality": 100
    }


@pytest.fixture
def sample_prediction_data():
    """Sample prediction data for testing"""
    return {
        "symbol": "Motor1",
        "failure_probability": 0.85,
        "confidence": 0.92,
        "horizon_hours": 24,
        "recommended_action": "Schedule maintenance",
        "model_version": "v1.0",
        "features": ["vibration", "temperature"]
    }


@pytest.fixture
def sample_anomaly_data():
    """Sample anomaly data for testing"""
    return {
        "symbol": "Motor1",
        "anomaly_score": 2.5,
        "metrics_involved": ["vibration", "temperature"],
        "baseline_values": [1.0, 70.0],
        "actual_values": [2.5, 85.0],
        "deviation_std": 2.1,
        "severity": "high"
    }


# Test utilities
class TestUtils:
    """Utility functions for tests"""

    @staticmethod
    def create_mock_dataframe(data: Dict[str, Any]):
        """Create a mock pandas DataFrame"""
        pd = pytest.importorskip("pandas")
        return pd.DataFrame(data)

    @staticmethod
    def assert_dataframe_equal(df1, df2, check_dtype=True):
        """Assert that two DataFrames are equal"""
        pd = pytest.importorskip("pandas")
        pd.testing.assert_frame_equal(df1, df2, check_dtype=check_dtype)

    @staticmethod
    async def async_return(value):
        """Helper for async return values in mocks"""
        return value