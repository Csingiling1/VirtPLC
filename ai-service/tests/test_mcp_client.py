"""
Comprehensive unit tests for MCP (Model Context Protocol) client
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import pandas as pd
from src.services.mcp_client import MCPClient
from src.services.timebase_client import timebase_service


class TestMCPClient:
    """Test suite for MCP Client"""

    @pytest.fixture
    def mcp_client(self):
        """Create MCP client instance for testing"""
        return MCPClient()

    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx AsyncClient"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            yield mock_instance

    def test_initialization(self, mcp_client):
        """Test MCP client initialization"""
        assert mcp_client.server_url == "http://mcp-server:8000"
        assert mcp_client.timeout == 30
        assert mcp_client.enabled is True

    @pytest.mark.asyncio
    async def test_initialize_success(self, mcp_client, mock_httpx_client):
        """Test successful MCP initialization"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"status": "initialized"}
        mock_httpx_client.post.return_value = mock_response

        result = await mcp_client.initialize()

        assert result == {"status": "initialized"}
        mock_httpx_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_failure(self, mcp_client, mock_httpx_client):
        """Test MCP initialization failure"""
        mock_httpx_client.post.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await mcp_client.initialize()

    @pytest.mark.asyncio
    async def test_list_tools_enabled(self, mcp_client, mock_httpx_client):
        """Test listing tools when MCP is enabled"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = [
            {"name": "get_sensor_data", "description": "Get sensor data"},
            {"name": "get_equipment_status", "description": "Get equipment status"}
        ]
        mock_httpx_client.get.return_value = mock_response

        tools = await mcp_client.list_tools()

        assert len(tools) == 2
        assert tools[0]["name"] == "get_sensor_data"

    @pytest.mark.asyncio
    async def test_list_tools_disabled(self, mcp_client):
        """Test listing tools when MCP is disabled"""
        mcp_client.enabled = False

        tools = await mcp_client.list_tools()

        assert tools == []

    @pytest.mark.asyncio
    async def test_call_tool_success(self, mcp_client, mock_httpx_client):
        """Test successful tool call"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_httpx_client.post.return_value = mock_response

        result = await mcp_client.call_tool("test_tool", {"param": "value"})

        assert result == {"result": "success"}

    @pytest.mark.asyncio
    async def test_call_tool_disabled(self, mcp_client):
        """Test tool call when MCP is disabled"""
        mcp_client.enabled = False

        result = await mcp_client.call_tool("test_tool", {"param": "value"})

        assert result == {}

    @pytest.mark.asyncio
    async def test_get_timebase_data_success(self, mcp_client):
        """Test getting TimebaseDB data via MCP"""
        mock_data = pd.DataFrame({
            'timestamp': [datetime.utcnow()],
            'symbol': ['Motor1'],
            'metric_type': ['temperature'],
            'value': [75.5],
            'unit': ['celsius'],
            'quality': [100]
        })

        with patch.object(timebase_service, 'get_time_range_data', return_value=mock_data) as mock_get_data:
            result = await mcp_client.get_timebase_data(
                symbols=["Motor1"],
                metrics=["temperature"],
                hours_back=24
            )

            assert "timebase_data" in result
            assert len(result["timebase_data"]) == 1
            assert result["timebase_data"][0]["symbol"] == "Motor1"
            assert result["query_info"]["symbols"] == ["Motor1"]

    @pytest.mark.asyncio
    async def test_get_timebase_data_failure(self, mcp_client):
        """Test TimebaseDB data retrieval failure"""
        with patch.object(timebase_service, 'get_time_range_data', side_effect=Exception("DB error")):
            result = await mcp_client.get_timebase_data(symbols=["Motor1"])

            assert "error" in result
            assert "DB error" in result["error"]

    @pytest.mark.asyncio
    async def test_get_predictive_insights_success(self, mcp_client):
        """Test getting predictive insights"""
        mock_data = pd.DataFrame({
            'timestamp': [datetime.utcnow()],
            'type': ['MaintenancePrediction'],
            'symbol': ['Motor1'],
            'insight_type': ['predictive'],
            'title': ['Motor maintenance needed'],
            'description': ['High vibration detected'],
            'failure_probability': [0.85],
            'confidence': [0.92],
            'anomaly_score': [None],
            'severity': ['high'],
            'recommended_action': ['Schedule maintenance'],
            'priority': [1],
            'llm_model': ['qwen2.5-coder:7b']
        })

        with patch.object(timebase_service, 'query_data', return_value=mock_data):
            result = await mcp_client.get_predictive_insights(symbols=["Motor1"])

            assert "insights" in result
            assert len(result["insights"]) == 1
            insight = result["insights"][0]
            assert insight["title"] == "Motor maintenance needed"
            assert insight["failure_probability"] == 0.85
            assert insight["llm_model"] == "qwen2.5-coder:7b"

    @pytest.mark.asyncio
    async def test_get_predictive_insights_empty(self, mcp_client):
        """Test getting predictive insights when no data"""
        empty_df = pd.DataFrame()

        with patch.object(timebase_service, 'query_data', return_value=empty_df):
            result = await mcp_client.get_predictive_insights(symbols=["Motor1"])

            assert result["insights"] == []
            assert result["total_count"] == 0

    @pytest.mark.asyncio
    async def test_get_ollama_context_comprehensive(self, mcp_client):
        """Test getting comprehensive context for Ollama"""
        # Mock sensor data
        sensor_data = {
            "timebase_data": [{
                "symbol": "Motor1",
                "data": [{
                    "timestamp": "2025-10-26T10:00:00",
                    "metric_type": "temperature",
                    "value": 75.5,
                    "unit": "celsius"
                }]
            }]
        }

        # Mock insights data
        insights_data = {
            "insights": [{
                "timestamp": "2025-10-26T10:00:00",
                "type": "MaintenancePrediction",
                "symbol": "Motor1",
                "title": "Motor maintenance needed",
                "description": "High vibration detected",
                "confidence": 0.92,
                "severity": "high",
                "failure_probability": 0.85,
                "llm_model": "qwen2.5-coder:7b"
            }]
        }

        # Mock latest readings
        latest_data = pd.DataFrame({
            'timestamp': [datetime.utcnow()],
            'symbol': ['Motor1'],
            'value': [75.5]
        })

        with patch.object(mcp_client, 'get_timebase_data', return_value=sensor_data), \
             patch.object(mcp_client, 'get_predictive_insights', return_value=insights_data), \
             patch.object(timebase_service, 'get_latest_readings', return_value=latest_data):

            context = await mcp_client.get_ollama_context(
                symbols=["Motor1"],
                context_type="comprehensive"
            )

            assert "# Factory Monitoring Context" in context
            assert "qwen2.5-coder:7b" in context
            assert "## Current Sensor Data" in context
            assert "## AI Predictive Insights" in context
            assert "## Equipment Status Summary" in context
            assert "Motor maintenance needed" in context

    @pytest.mark.asyncio
    async def test_get_ollama_context_minimal(self, mcp_client):
        """Test getting minimal context for Ollama"""
        sensor_data = {"timebase_data": []}
        insights_data = {"insights": []}
        latest_data = pd.DataFrame()

        with patch.object(mcp_client, 'get_timebase_data', return_value=sensor_data), \
             patch.object(mcp_client, 'get_predictive_insights', return_value=insights_data), \
             patch.object(timebase_service, 'get_latest_readings', return_value=latest_data):

            context = await mcp_client.get_ollama_context(
                symbols=["Motor1"],
                context_type="minimal",
                include_predictions=False
            )

            assert "# Factory Monitoring Context" in context
            assert "## Equipment Status Summary" in context
            assert "no recent data" in context

    @pytest.mark.asyncio
    async def test_close_client(self, mcp_client, mock_httpx_client):
        """Test closing MCP client"""
        await mcp_client.close()

        mock_httpx_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_sensor_data_legacy(self, mcp_client, mock_httpx_client):
        """Test legacy sensor data method"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"data": "sensor_data"}
        mock_httpx_client.post.return_value = mock_response

        result = await mcp_client.get_sensor_data(["Motor1"], ["temperature"])

        assert result == {"data": "sensor_data"}

    @pytest.mark.asyncio
    async def test_get_equipment_status_legacy(self, mcp_client, mock_httpx_client):
        """Test legacy equipment status method"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"status": "operational"}
        mock_httpx_client.post.return_value = mock_response

        result = await mcp_client.get_equipment_status("Motor1")

        assert result == {"status": "operational"}

    @pytest.mark.asyncio
    async def test_get_historical_data_legacy(self, mcp_client, mock_httpx_client):
        """Test legacy historical data method"""
        start_time = datetime.utcnow() - timedelta(hours=24)
        end_time = datetime.utcnow()

        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"historical_data": []}
        mock_httpx_client.post.return_value = mock_response

        result = await mcp_client.get_historical_data(
            "Motor1", "temperature", start_time, end_time
        )

        assert result == {"historical_data": []}

    @pytest.mark.asyncio
    async def test_trigger_maintenance_alert_legacy(self, mcp_client, mock_httpx_client):
        """Test legacy maintenance alert method"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"alert_id": "123"}
        mock_httpx_client.post.return_value = mock_response

        result = await mcp_client.trigger_maintenance_alert(
            "Motor1", "high", "Urgent maintenance required"
        )

        assert result == {"alert_id": "123"}

    @pytest.mark.asyncio
    async def test_get_context_for_llm_legacy(self, mcp_client, mock_httpx_client):
        """Test legacy LLM context method"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "current_readings": "75.5°C",
            "status_summary": "operational",
            "trends": "stable",
            "recent_alerts": "none"
        }
        mock_httpx_client.post.return_value = mock_response

        context = await mcp_client.get_context_for_llm(["Motor1"])

        assert "Factory Status as of" in context
        assert "75.5°C" in context
        assert "operational" in context


# Test global instance
def test_global_mcp_client_instance():
    """Test that global MCP client instance exists"""
    from src.services.mcp_client import mcp_client
    assert isinstance(mcp_client, MCPClient)


@pytest.mark.parametrize("method_name,expected_tools", [
    ("get_timebase_data", ["timebase_query"]),
    ("get_predictive_insights", ["insights_query"]),
    ("get_ollama_context", ["context_generation"]),
])
def test_method_covers_core_functionality(method_name, expected_tools):
    """Test that key methods exist and are callable"""
    client = MCPClient()
    method = getattr(client, method_name)
    assert callable(method)


def test_mcp_client_inheritance():
    """Test MCP client class structure"""
    client = MCPClient()
    assert hasattr(client, 'initialize')
    assert hasattr(client, 'list_tools')
    assert hasattr(client, 'call_tool')
    assert hasattr(client, 'close')


@pytest.mark.asyncio
async def test_error_handling_comprehensive():
    """Test comprehensive error handling"""
    client = MCPClient()

    # Test with disabled MCP
    client.enabled = False
    result = await client.list_tools()
    assert result == []

    # Test with network errors
    client.enabled = True
    with patch.object(client, 'client') as mock_client:
        mock_client.get.side_effect = Exception("Network error")
        result = await client.list_tools()
        assert result == []


def test_timebase_integration_imports():
    """Test that TimebaseDB integration is properly imported"""
    from src.services.mcp_client import timebase_service
    assert timebase_service is not None
    assert hasattr(timebase_service, 'query_data')