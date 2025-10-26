"""
Comprehensive unit tests for AI Service configuration
"""
import pytest
from unittest.mock import patch, MagicMock
import os
from src.config import Settings


class TestSettings:
    """Test suite for Settings configuration class"""

    def test_default_values(self):
        """Test default configuration values"""
        settings = Settings()

        # Server settings
        assert settings.host == "0.0.0.0"
        assert settings.port == 3001
        assert settings.ws_port == 3002
        assert settings.environment == "development"

        # Backend API
        assert settings.backend_api_url == "http://backend:8080"
        assert settings.backend_api_key is None

        # Ollama settings
        assert settings.ollama_host == "http://ollama:11434"
        assert settings.ollama_model == "qwen2.5-coder:7b"  # Updated model
        assert settings.ollama_temperature == 0.7
        assert settings.ollama_max_tokens == 2048

        # MCP settings
        assert settings.mcp_enabled is True
        assert settings.mcp_server_url == "http://mcp-server:8000"
        assert settings.mcp_timeout == 30

        # TimeBase settings
        assert settings.timebase_url == "dts://timebase:8011"
        assert settings.timebase_user == "admin"
        assert settings.timebase_password == "changeme"
        assert settings.timebase_stream == "factory_metrics"

        # Database settings
        assert settings.postgres_host == "postgres"
        assert settings.postgres_port == 5432
        assert settings.postgres_db == "virtplc"
        assert settings.postgres_user == "virtplc"
        assert settings.postgres_password == "changeme"

        # Redis settings
        assert settings.redis_host == "redis"
        assert settings.redis_port == 6379
        assert settings.redis_db == 0
        assert settings.redis_password is None

        # Analysis settings
        assert settings.analysis_interval == 5000
        assert settings.prediction_threshold == 0.7
        assert settings.anomaly_threshold == 2.0
        assert settings.min_data_points == 10

        # Logging and metrics
        assert settings.log_level == "INFO"
        assert settings.log_format == "json"
        assert settings.metrics_enabled is True
        assert settings.metrics_port == 9090

    @patch.dict(os.environ, {
        "HOST": "127.0.0.1",
        "PORT": "8080",
        "OLLAMA_MODEL": "custom-model:1.0",
        "MCP_ENABLED": "false",
        "TIMEBASE_PASSWORD": "secret123"
    })
    def test_environment_variables(self):
        """Test configuration from environment variables"""
        settings = Settings()

        assert settings.host == "127.0.0.1"
        assert settings.port == 8080
        assert settings.ollama_model == "custom-model:1.0"
        assert settings.mcp_enabled is False
        assert settings.timebase_password == "secret123"

    def test_postgres_url_property(self):
        """Test PostgreSQL URL generation"""
        settings = Settings()
        expected_url = "postgresql://virtplc:changeme@postgres:5432/virtplc"
        assert settings.postgres_url == expected_url

    def test_redis_url_property_no_password(self):
        """Test Redis URL generation without password"""
        settings = Settings()
        expected_url = "redis://redis:6379/0"
        assert settings.redis_url == expected_url

    @patch.dict(os.environ, {"REDIS_PASSWORD": "redispass"})
    def test_redis_url_property_with_password(self):
        """Test Redis URL generation with password"""
        settings = Settings()
        expected_url = "redis://:redispass@redis:6379/0"
        assert settings.redis_url == expected_url

    def test_qwen_model_default(self):
        """Test that qwen2.5-coder:7b is the default model"""
        settings = Settings()
        assert settings.ollama_model == "qwen2.5-coder:7b"

    @patch.dict(os.environ, {"OLLAMA_MODEL": "llama3:8b"})
    def test_fallback_to_old_model(self):
        """Test that old model can still be configured"""
        settings = Settings()
        assert settings.ollama_model == "llama3:8b"

    def test_numeric_validation(self):
        """Test numeric field validation"""
        settings = Settings()

        # Test float fields
        assert isinstance(settings.ollama_temperature, float)
        assert isinstance(settings.prediction_threshold, float)
        assert isinstance(settings.anomaly_threshold, float)

        # Test int fields
        assert isinstance(settings.port, int)
        assert isinstance(settings.ws_port, int)
        assert isinstance(settings.postgres_port, int)
        assert isinstance(settings.redis_port, int)
        assert isinstance(settings.analysis_interval, int)

    def test_url_validation(self):
        """Test URL field patterns"""
        settings = Settings()

        # Test URL formats
        assert settings.ollama_host.startswith("http://")
        assert settings.backend_api_url.startswith("http://")
        assert settings.mcp_server_url.startswith("http://")
        assert settings.timebase_url.startswith("dts://")

    def test_boolean_fields(self):
        """Test boolean field defaults"""
        settings = Settings()

        assert isinstance(settings.mcp_enabled, bool)
        assert isinstance(settings.metrics_enabled, bool)

    @patch.dict(os.environ, {
        "MCP_ENABLED": "true",
        "METRICS_ENABLED": "false"
    })
    def test_boolean_env_vars(self):
        """Test boolean environment variable parsing"""
        settings = Settings()

        assert settings.mcp_enabled is True
        assert settings.metrics_enabled is False

    def test_chat_history_settings(self):
        """Test chat history configuration"""
        settings = Settings()

        assert settings.chat_history_retention_days == 30
        assert settings.chat_history_max_messages == 1000

    def test_analysis_settings(self):
        """Test analysis configuration"""
        settings = Settings()

        assert settings.analysis_interval == 5000
        assert settings.prediction_threshold == 0.7
        assert settings.anomaly_threshold == 2.0
        assert settings.min_data_points == 10

    def test_log_settings(self):
        """Test logging configuration"""
        settings = Settings()

        assert settings.log_level == "INFO"
        assert settings.log_format == "json"

    def test_metrics_settings(self):
        """Test metrics configuration"""
        settings = Settings()

        assert settings.metrics_enabled is True
        assert settings.metrics_port == 9090

    def test_pydantic_config(self):
        """Test Pydantic configuration"""
        settings = Settings()

        # Test that env file is configured
        assert hasattr(settings, 'Config')
        assert settings.Config.env_file == ".env"
        assert settings.Config.case_sensitive is False


# Global settings instance tests
def test_global_settings_instance():
    """Test that global settings instance is created"""
    from src.config import settings
    assert isinstance(settings, Settings)
    assert settings.ollama_model == "qwen2.5-coder:7b"


@pytest.mark.parametrize("field,value", [
    ("port", 8080),
    ("ollama_temperature", 0.5),
    ("mcp_timeout", 60),
    ("analysis_interval", 10000),
    ("prediction_threshold", 0.8),
])
def test_field_types(field, value):
    """Test that fields accept correct types"""
    settings = Settings()
    assert hasattr(settings, field)
    current_value = getattr(settings, field)
    assert type(current_value) == type(value)


def test_config_immutability():
    """Test that config values don't change unexpectedly"""
    settings1 = Settings()
    settings2 = Settings()

    assert settings1.ollama_model == settings2.ollama_model
    assert settings1.port == settings2.port
    assert settings1.timebase_url == settings2.timebase_url