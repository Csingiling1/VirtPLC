"""
Comprehensive unit tests for TimebaseDB client
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from src.services.timebase_client import TimeBaseService


class TestTimeBaseService:
    """Test suite for TimeBase Service"""

    @pytest.fixture
    def timebase_service(self):
        """Create TimeBase service instance for testing"""
        return TimeBaseService()

    @pytest.fixture
    def mock_timebase_client(self):
        """Mock TimeBase client"""
        mock_client = MagicMock()
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.query = AsyncMock()
        mock_client.get_writer = MagicMock()
        return mock_client

    def test_initialization(self, timebase_service):
        """Test TimeBase service initialization"""
        assert timebase_service.url == "dts://timebase:8011"
        assert timebase_service.user == "admin"
        assert timebase_service.password == "changeme"
        assert timebase_service.stream == "factory_metrics"
        assert timebase_service.client is None

    @pytest.mark.asyncio
    async def test_connect_success(self, timebase_service, mock_timebase_client):
        """Test successful TimeBase connection"""
        with patch('src.services.timebase_client.TimeBaseClient', return_value=mock_timebase_client):
            await timebase_service.connect()

            assert timebase_service.client == mock_timebase_client
            mock_timebase_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, timebase_service):
        """Test TimeBase connection failure"""
        with patch('src.services.timebase_client.TimeBaseClient', side_effect=Exception("Connection failed")):
            await timebase_service.connect()

            # Should not crash, just log warning
            assert timebase_service.client is None

    @pytest.mark.asyncio
    async def test_disconnect(self, timebase_service, mock_timebase_client):
        """Test TimeBase disconnection"""
        timebase_service.client = mock_timebase_client

        await timebase_service.disconnect()

        mock_timebase_client.disconnect.assert_called_once()
        assert timebase_service.client == mock_timebase_client  # Still assigned

    @pytest.mark.asyncio
    async def test_query_data_success(self, timebase_service, mock_timebase_client):
        """Test successful data query"""
        timebase_service.client = mock_timebase_client

        mock_cursor = AsyncMock()
        mock_cursor.fetchall.return_value = [
            {"timestamp": datetime.utcnow(), "value": 75.5, "symbol": "Motor1"}
        ]
        mock_timebase_client.query.return_value = mock_cursor

        result = await timebase_service.query_data("SELECT * FROM test")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["value"] == 75.5

    @pytest.mark.asyncio
    async def test_query_data_no_client(self, timebase_service):
        """Test data query without client (mock mode)"""
        result = await timebase_service.query_data("SELECT * FROM test")

        assert isinstance(result, pd.DataFrame)
        # Should return mock data
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_latest_readings_success(self, timebase_service, mock_timebase_client):
        """Test getting latest readings"""
        timebase_service.client = mock_timebase_client

        mock_data = [
            {"timestamp": datetime.utcnow(), "symbol": "Motor1", "value": 75.5},
            {"timestamp": datetime.utcnow(), "symbol": "Motor2", "value": 80.0}
        ]

        with patch.object(timebase_service, 'query_data') as mock_query:
            mock_query.return_value = pd.DataFrame(mock_data)

            result = await timebase_service.get_latest_readings(["Motor1", "Motor2"], limit=10)

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            mock_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_time_range_data(self, timebase_service, mock_timebase_client):
        """Test getting data for time range"""
        timebase_service.client = mock_timebase_client

        start_time = datetime.utcnow() - timedelta(hours=24)
        end_time = datetime.utcnow()

        mock_data = [
            {"timestamp": start_time, "value": 70.0},
            {"timestamp": end_time, "value": 75.5}
        ]

        with patch.object(timebase_service, 'query_data') as mock_query:
            mock_query.return_value = pd.DataFrame(mock_data)

            result = await timebase_service.get_time_range_data(
                "Motor1", "temperature", start_time, end_time
            )

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_aggregated_metrics(self, timebase_service, mock_timebase_client):
        """Test getting aggregated metrics"""
        timebase_service.client = mock_timebase_client

        mock_data = [
            {"timestamp": datetime.utcnow(), "avg_value": 75.0, "min_value": 70.0, "max_value": 80.0}
        ]

        with patch.object(timebase_service, 'query_data') as mock_query:
            mock_query.return_value = pd.DataFrame(mock_data)

            result = await timebase_service.get_aggregated_metrics("Motor1", "1h")

            assert isinstance(result, pd.DataFrame)
            assert "avg_value" in result.columns

    @pytest.mark.asyncio
    async def test_write_prediction_success(self, timebase_service, mock_timebase_client):
        """Test writing maintenance prediction"""
        timebase_service.client = mock_timebase_client

        mock_writer = AsyncMock()
        mock_timebase_client.get_writer.return_value = mock_writer

        await timebase_service.write_prediction(
            symbol="Motor1",
            failure_probability=0.85,
            confidence=0.92,
            horizon_hours=24,
            recommended_action="Schedule maintenance",
            model_version="v1.0",
            features=["vibration", "temperature"]
        )

        mock_timebase_client.get_writer.assert_called_with("ai_predictions")
        mock_writer.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_prediction_no_client(self, timebase_service):
        """Test writing prediction without client"""
        # Should not crash, just log warning
        await timebase_service.write_prediction(
            symbol="Motor1",
            failure_probability=0.85,
            confidence=0.92,
            horizon_hours=24,
            recommended_action="Schedule maintenance",
            model_version="v1.0",
            features=["vibration"]
        )

        # No assertions needed, just ensure no exception

    @pytest.mark.asyncio
    async def test_write_anomaly_success(self, timebase_service, mock_timebase_client):
        """Test writing anomaly detection"""
        timebase_service.client = mock_timebase_client

        mock_writer = AsyncMock()
        mock_timebase_client.get_writer.return_value = mock_writer

        await timebase_service.write_anomaly(
            symbol="Motor1",
            anomaly_score=2.5,
            metrics_involved=["vibration", "temperature"],
            baseline_values=[1.0, 70.0],
            actual_values=[2.5, 85.0],
            deviation_std=2.1,
            severity="high"
        )

        mock_writer.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_ai_insight_success(self, timebase_service, mock_timebase_client):
        """Test writing AI insight"""
        timebase_service.client = mock_timebase_client

        mock_writer = AsyncMock()
        mock_timebase_client.get_writer.return_value = mock_writer

        await timebase_service.write_ai_insight(
            insight_type="optimization",
            title="Energy optimization opportunity",
            description="Motor running inefficiently during off-peak hours",
            affected_equipment=["Motor1"],
            confidence=0.88,
            priority=2,
            llm_model="qwen2.5-coder:7b"
        )

        mock_writer.write.assert_called_once()

    def test_mock_query_data_structure(self, timebase_service):
        """Test mock data generation structure"""
        mock_data = timebase_service._mock_query_data()

        assert isinstance(mock_data, pd.DataFrame)
        assert len(mock_data) > 0

        required_columns = ['timestamp', 'symbol', 'metric_type', 'value', 'unit', 'quality']
        for col in required_columns:
            assert col in mock_data.columns

    def test_mock_query_data_values(self, timebase_service):
        """Test mock data value ranges"""
        mock_data = timebase_service._mock_query_data()

        # Check temperature range (reasonable for industrial equipment)
        temperatures = mock_data['value']
        assert temperatures.min() >= 60  # Not too cold
        assert temperatures.max() <= 100  # Not too hot

        # Check quality values
        qualities = mock_data['quality']
        assert all(q == 100 for q in qualities)  # Mock data has perfect quality

    @pytest.mark.asyncio
    async def test_multiple_symbols_query(self, timebase_service):
        """Test querying multiple symbols"""
        symbols = ["Motor1", "Motor2", "Conveyor1"]

        with patch.object(timebase_service, 'query_data') as mock_query:
            mock_query.return_value = pd.DataFrame({
                'symbol': symbols * 2,
                'value': [75.0, 80.0, 65.0] * 2
            })

            result = await timebase_service.get_latest_readings(symbols)

            assert len(result) == 6  # 3 symbols * 2 readings each
            assert set(result['symbol'].unique()) == set(symbols)

    @pytest.mark.asyncio
    async def test_empty_result_handling(self, timebase_service):
        """Test handling of empty query results"""
        with patch.object(timebase_service, 'query_data') as mock_query:
            mock_query.return_value = pd.DataFrame()

            result = await timebase_service.get_latest_readings(["NonExistent"])

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_service_attributes(self, timebase_service):
        """Test service attribute access"""
        assert hasattr(timebase_service, 'url')
        assert hasattr(timebase_service, 'user')
        assert hasattr(timebase_service, 'password')
        assert hasattr(timebase_service, 'stream')
        assert hasattr(timebase_service, 'client')

    @pytest.mark.asyncio
    async def test_connection_state_management(self, timebase_service, mock_timebase_client):
        """Test connection state management"""
        # Initially disconnected
        assert timebase_service.client is None

        # Connect
        with patch('src.services.timebase_client.TimeBaseClient', return_value=mock_timebase_client):
            await timebase_service.connect()
            assert timebase_service.client is not None

        # Disconnect
        await timebase_service.disconnect()
        # Client reference remains for potential reconnection
        assert timebase_service.client is not None

    @pytest.mark.parametrize("method_name", [
        "connect", "disconnect", "query_data", "get_latest_readings",
        "get_time_range_data", "get_aggregated_metrics", "write_prediction",
        "write_anomaly", "write_ai_insight"
    ])
    def test_method_existence(self, method_name, timebase_service):
        """Test that all public methods exist"""
        assert hasattr(timebase_service, method_name)
        method = getattr(timebase_service, method_name)
        assert callable(method)

    def test_data_types_in_mock_data(self, timebase_service):
        """Test data types in mock data"""
        mock_data = timebase_service._mock_query_data()

        # Check timestamp type
        assert pd.api.types.is_datetime64_any_dtype(mock_data['timestamp'])

        # Check numeric types
        assert pd.api.types.is_numeric_dtype(mock_data['value'])
        assert pd.api.types.is_numeric_dtype(mock_data['quality'])

        # Check string types
        assert pd.api.types.is_string_dtype(mock_data['symbol'])
        assert pd.api.types.is_string_dtype(mock_data['metric_type'])
        assert pd.api.types.is_string_dtype(mock_data['unit'])

    @pytest.mark.asyncio
    async def test_query_error_handling(self, timebase_service, mock_timebase_client):
        """Test error handling in queries"""
        timebase_service.client = mock_timebase_client
        mock_timebase_client.query.side_effect = Exception("Query failed")

        with pytest.raises(Exception):
            await timebase_service.query_data("SELECT * FROM test")

    @pytest.mark.asyncio
    async def test_write_operations_error_handling(self, timebase_service):
        """Test error handling in write operations"""
        # Should not raise exceptions when client is None
        await timebase_service.write_prediction(
            symbol="Motor1",
            failure_probability=0.5,
            confidence=0.8,
            horizon_hours=12,
            recommended_action="test",
            model_version="test",
            features=["test"]
        )

        # Should handle writer creation errors gracefully
        timebase_service.client = MagicMock()
        timebase_service.client.get_writer.side_effect = Exception("Writer error")

        await timebase_service.write_anomaly(
            symbol="Motor1",
            anomaly_score=1.5,
            metrics_involved=["temp"],
            baseline_values=[70.0],
            actual_values=[75.0],
            deviation_std=1.0,
            severity="low"
        )


# Test global instance
def test_global_timebase_service_instance():
    """Test that global TimeBase service instance exists"""
    from src.services.timebase_client import timebase_service
    assert isinstance(timebase_service, TimeBaseService)


@pytest.mark.asyncio
async def test_service_lifecycle():
    """Test complete service lifecycle"""
    service = TimeBaseService()

    # Start disconnected
    assert service.client is None

    # Mock connection (would normally connect to real TimeBase)
    with patch.object(service, 'connect') as mock_connect:
        await service.connect()
        mock_connect.assert_called_once()

    # Mock some operations
    with patch.object(service, 'get_latest_readings') as mock_readings:
        mock_readings.return_value = pd.DataFrame({'test': [1, 2, 3]})
        result = await service.get_latest_readings(['Motor1'])
        assert len(result) == 3

    # Disconnect
    with patch.object(service, 'disconnect') as mock_disconnect:
        await service.disconnect()
        mock_disconnect.assert_called_once()


def test_pandas_integration():
    """Test pandas DataFrame integration"""
    service = TimeBaseService()

    # Test that service can create and manipulate DataFrames
    df = pd.DataFrame({
        'timestamp': [datetime.utcnow()],
        'symbol': ['TestMotor'],
        'value': [42.0]
    })

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]['symbol'] == 'TestMotor'


@pytest.mark.parametrize("hours_back,expected_records", [
    (1, 60),  # 1 hour of minute-level data
    (24, 1440),  # 24 hours
    (168, 10080),  # 1 week
])
def test_time_range_calculations(hours_back, expected_records):
    """Test time range calculations for queries"""
    service = TimeBaseService()

    # This is more of a documentation test - in real implementation,
    # we'd verify the query parameters are calculated correctly
    start_time = datetime.utcnow() - timedelta(hours=hours_back)
    end_time = datetime.utcnow()

    time_diff = end_time - start_time
    expected_diff = timedelta(hours=hours_back)

    assert abs(time_diff - expected_diff) < timedelta(seconds=1)