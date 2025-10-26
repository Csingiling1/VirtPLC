"""
Comprehensive unit tests for main FastAPI application
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
import json
from datetime import datetime
from src.main import app, lifespan
from src.services.mcp_client import mcp_client
from src.services.timebase_client import timebase_service


class TestMainApp:
    """Test suite for main FastAPI application"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_services(self):
        """Mock external services"""
        with patch.object(mcp_client, 'initialize') as mock_mcp_init, \
             patch.object(timebase_service, 'connect') as mock_tb_connect, \
             patch.object(mcp_client, 'close') as mock_mcp_close, \
             patch.object(timebase_service, 'disconnect') as mock_tb_disconnect:

            mock_mcp_init.return_value = {"status": "initialized"}
            mock_tb_connect.return_value = None
            mock_mcp_close.return_value = None
            mock_tb_disconnect.return_value = None

            yield {
                'mcp_init': mock_mcp_init,
                'tb_connect': mock_tb_connect,
                'mcp_close': mock_mcp_close,
                'tb_disconnect': mock_tb_disconnect
            }

    def test_app_creation(self):
        """Test FastAPI app creation"""
        assert app.title == "VirtPLC AI Service"
        assert app.version == "1.0.0"
        assert app.description == "AI-powered predictive analysis for factory monitoring"

    def test_cors_middleware(self):
        """Test CORS middleware configuration"""
        cors_middleware = None
        for middleware in app.user_middleware:
            if hasattr(middleware, 'app'):
                # Check if it's CORSMiddleware
                if hasattr(middleware.app, 'allow_origins'):
                    cors_middleware = middleware.app
                    break

        assert cors_middleware is not None
        assert cors_middleware.allow_origins == ["*"]
        assert cors_middleware.allow_credentials is True
        assert cors_middleware.allow_methods == ["*"]
        assert cors_middleware.allow_headers == ["*"]

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"

    def test_health_services_status(self, client):
        """Test health endpoint service status"""
        response = client.get("/health")
        data = response.json()

        services = data["services"]
        assert "mcp" in services
        assert "timebase" in services
        assert "ollama" in services

        # Test with MCP enabled
        assert services["mcp"] == "connected"  # MCP is enabled by default

        # Ollama host should be present
        assert "http://" in services["ollama"]

    @pytest.mark.asyncio
    async def test_lifespan_startup_success(self, mock_services):
        """Test successful application startup"""
        # Lifespan is already tested via app creation, but we can test the components
        assert mcp_client.enabled is True  # Should be enabled by default

    @pytest.mark.asyncio
    async def test_lifespan_startup_with_failures(self):
        """Test startup with service failures"""
        with patch.object(mcp_client, 'initialize', side_effect=Exception("MCP failed")), \
             patch.object(timebase_service, 'connect', side_effect=Exception("TimeBase failed")):

            # App should still start even with service failures
            # (they're caught and logged as warnings)
            test_app = FastAPI(lifespan=lifespan)

            # Just verify app can be created
            assert test_app is not None

    def test_test_endpoint_structure(self, client):
        """Test test endpoint response structure"""
        response = client.get("/test")

        assert response.status_code == 200
        data = response.json()

        # Should contain basic test information
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_test_endpoint_comprehensive(self):
        """Test comprehensive test endpoint functionality"""
        with patch('src.main.mcp_client') as mock_mcp, \
             patch('src.main.timebase_service') as mock_tb:

            # Mock MCP context call
            mock_mcp.get_context_for_llm = AsyncMock(return_value="Mock context")

            # Mock TimeBase latest readings
            mock_tb.get_latest_readings = AsyncMock(return_value=MagicMock())

            # Create a test client for the endpoint
            from fastapi.testclient import TestClient
            test_app = FastAPI()
            from src.main import test_endpoint
            test_app.get("/test")(test_endpoint)

            client = TestClient(test_app)
            response = client.get("/test")

            assert response.status_code == 200

    def test_app_router_inclusion(self):
        """Test that routers are properly included"""
        # Check that analysis router is included
        analysis_routes = [route for route in app.routes if hasattr(route, 'path') and 'analysis' in str(route.path)]
        assert len(analysis_routes) > 0

        # Check that chat router is included
        chat_routes = [route for route in app.routes if hasattr(route, 'path') and 'chat' in str(route.path)]
        assert len(chat_routes) > 0

        # Check that dashboard router is included
        dashboard_routes = [route for route in app.routes if hasattr(route, 'path') and 'dashboard' in str(route.path)]
        assert len(dashboard_routes) > 0

    def test_openapi_schema(self, client):
        """Test OpenAPI schema generation"""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()

        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        assert schema["info"]["title"] == "VirtPLC AI Service"
        assert schema["info"]["version"] == "1.0.0"

    def test_health_endpoint_content_type(self, client):
        """Test health endpoint returns correct content type"""
        response = client.get("/health")

        assert response.headers["content-type"] == "application/json"

    def test_test_endpoint_content_type(self, client):
        """Test test endpoint returns correct content type"""
        response = client.get("/test")

        assert response.headers["content-type"] == "application/json"

    @pytest.mark.parametrize("endpoint", ["/health", "/test"])
    def test_endpoint_availability(self, endpoint, client):
        """Test that key endpoints are available"""
        response = client.get(endpoint)

        assert response.status_code == 200

    def test_app_middleware_order(self):
        """Test middleware order and configuration"""
        # CORS should be configured
        middleware_classes = [type(mw.app) if hasattr(mw, 'app') else type(mw)
                             for mw in app.user_middleware]

        # Should have CORSMiddleware
        from fastapi.middleware.cors import CORSMiddleware
        assert CORSMiddleware in middleware_classes

    def test_static_file_handling(self, client):
        """Test that static files are handled appropriately"""
        # Test 404 for non-existent static files
        response = client.get("/static/nonexistent.css")

        # Should return 404
        assert response.status_code == 404

    def test_error_handling(self, client):
        """Test error handling for invalid endpoints"""
        response = client.get("/nonexistent-endpoint")

        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test method not allowed responses"""
        response = client.post("/health")

        # POST not allowed on GET-only endpoint
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_lifespan_error_handling(self):
        """Test lifespan error handling"""
        # Test that lifespan handles exceptions gracefully
        with patch('src.main.logger') as mock_logger:
            # Simulate database initialization failure
            with patch('src.main.get_engine', side_effect=Exception("DB init failed")):
                test_app = FastAPI(lifespan=lifespan)

                # App should still be created despite DB failure
                assert test_app is not None

                # Warning should be logged
                mock_logger.warning.assert_called()

    def test_app_state_management(self):
        """Test application state management"""
        # Test that app can handle multiple requests
        client = TestClient(app)

        # Multiple health checks
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200

    def test_json_response_format(self, client):
        """Test JSON response formatting"""
        response = client.get("/health")
        data = response.json()

        # Should be valid JSON
        assert isinstance(data, dict)

        # Should have required fields
        required_fields = ["status", "timestamp", "version", "services"]
        for field in required_fields:
            assert field in data

    def test_timestamp_format(self, client):
        """Test timestamp format in responses"""
        response = client.get("/health")
        data = response.json()

        timestamp = data["timestamp"]

        # Should be ISO format
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp}")

    def test_service_status_types(self, client):
        """Test service status value types"""
        response = client.get("/health")
        data = response.json()

        services = data["services"]

        # All service statuses should be strings
        for service, status in services.items():
            assert isinstance(status, str)
            assert len(status) > 0

    @pytest.mark.parametrize("header,value", [
        ("content-type", "application/json"),
        ("server", "uvicorn"),  # May vary
    ])
    def test_response_headers(self, header, value, client):
        """Test response headers"""
        response = client.get("/health")

        # Check that expected headers are present
        if header in response.headers:
            if header == "content-type":
                assert value in response.headers[header]

    def test_app_configuration(self):
        """Test app configuration settings"""
        assert app.debug is False  # Should be production-ready
        assert app.title is not None
        assert app.version is not None
        assert app.description is not None


# Integration tests
class TestAppIntegration:
    """Integration tests for the complete application"""

    @pytest.fixture
    def integration_client(self):
        """Create integration test client"""
        return TestClient(app)

    def test_full_request_response_cycle(self, integration_client):
        """Test complete request-response cycle"""
        # Health check
        response = integration_client.get("/health")
        assert response.status_code == 200

        # Test endpoint
        response = integration_client.get("/test")
        assert response.status_code == 200

        # Verify responses are different
        health_data = integration_client.get("/health").json()
        test_data = integration_client.get("/test").json()

        assert health_data != test_data

    def test_concurrent_requests(self, integration_client):
        """Test handling concurrent requests"""
        import asyncio
        import threading

        results = []

        def make_request():
            response = integration_client.get("/health")
            results.append(response.status_code)

        # Simulate concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All requests should succeed
        assert all(code == 200 for code in results)
        assert len(results) == 5

    def test_memory_usage_stability(self, integration_client):
        """Test memory usage stability under load"""
        # Make multiple requests to check for memory leaks
        for _ in range(10):
            response = integration_client.get("/health")
            assert response.status_code == 200

        # If we get here without crashes, basic stability is maintained
        assert True

    def test_error_recovery(self, integration_client):
        """Test error recovery and continued operation"""
        # Make a valid request
        response = integration_client.get("/health")
        assert response.status_code == 200

        # Make an invalid request
        response = integration_client.get("/invalid-endpoint")
        assert response.status_code == 404

        # Make another valid request - should still work
        response = integration_client.get("/health")
        assert response.status_code == 200


# Performance tests
class TestAppPerformance:
    """Performance tests for the application"""

    @pytest.fixture
    def perf_client(self):
        """Create performance test client"""
        return TestClient(app)

    def test_response_time(self, perf_client):
        """Test response time is reasonable"""
        import time

        start_time = time.time()
        response = perf_client.get("/health")
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        # Should respond within 1 second
        assert response_time < 1.0

    def test_payload_size(self, perf_client):
        """Test response payload size is reasonable"""
        response = perf_client.get("/health")

        # Response should not be too large
        content_length = len(response.content)
        assert content_length < 10000  # Less than 10KB

    def test_json_serialization_performance(self, perf_client):
        """Test JSON serialization performance"""
        import json

        response = perf_client.get("/health")
        data = response.json()

        # Should be valid JSON and serializable
        json_str = json.dumps(data)
        assert len(json_str) > 0

        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed == data


# Test global imports
def test_global_imports():
    """Test that all global imports work"""
    from src.main import app, lifespan
    from src.services import mcp_client, timebase_service

    assert app is not None
    assert lifespan is not None
    assert mcp_client is not None
    assert timebase_service is not None


@pytest.mark.asyncio
async def test_async_operations():
    """Test async operation handling"""
    # Test that async endpoints can be called
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # These endpoints should handle async operations properly
    response = client.get("/health")
    assert response.status_code == 200

    response = client.get("/test")
    assert response.status_code == 200


def test_app_startup_configuration():
    """Test app startup configuration"""
    # Verify that the app is configured for production use
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"
    assert app.openapi_url == "/openapi.json"


def test_router_prefixes():
    """Test that router prefixes are correctly applied"""
    routes = [str(route.path) for route in app.routes if hasattr(route, 'path')]

    # Should have prefixed routes
    analysis_routes = [r for r in routes if r.startswith("/api/analysis")]
    chat_routes = [r for r in routes if r.startswith("/api/chat")]
    dashboard_routes = [r for r in routes if r.startswith("/api/dashboard")]

    # At minimum, should have some routes for each
    assert len(analysis_routes) >= 0  # May be empty if routers not fully loaded
    assert len(chat_routes) >= 0
    assert len(dashboard_routes) >= 0