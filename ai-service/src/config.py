"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=3001, env="PORT")
    ws_port: int = Field(default=3002, env="WS_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Backend API
    backend_api_url: str = Field(default="http://backend:8080", env="BACKEND_API_URL")
    backend_api_key: Optional[str] = Field(default=None, env="BACKEND_API_KEY")
    
    # Ollama
    ollama_host: str = Field(default="http://ollama:11434", env="OLLAMA_HOST")
    ollama_model: str = Field(default="qwen2:0.5b", env="OLLAMA_MODEL")
    ollama_temperature: float = Field(default=0.7, env="OLLAMA_TEMPERATURE")
    ollama_max_tokens: int = Field(default=2048, env="OLLAMA_MAX_TOKENS")
    
    # MCP
    mcp_enabled: bool = Field(default=True, env="MCP_ENABLED")
    mcp_server_url: str = Field(default="http://mcp-server:8000", env="MCP_SERVER_URL")
    mcp_timeout: int = Field(default=30, env="MCP_TIMEOUT")
    
    # TimeBase
    timebase_url: str = Field(default="dts://timebase:8011", env="TIMEBASE_URL")
    timebase_user: str = Field(default="admin", env="TIMEBASE_USER")
    timebase_password: str = Field(default="changeme", env="TIMEBASE_PASSWORD")
    timebase_stream: str = Field(default="factory_metrics", env="TIMEBASE_STREAM")
    
    # PostgreSQL
    postgres_host: str = Field(default="postgres", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_db: str = Field(default="virtplc", env="POSTGRES_DB")
    postgres_user: str = Field(default="virtplc", env="POSTGRES_USER")
    postgres_password: str = Field(default="changeme", env="POSTGRES_PASSWORD")
    
    # Redis
    redis_host: str = Field(default="redis", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Chat History
    chat_history_retention_days: int = Field(default=30, env="CHAT_HISTORY_RETENTION_DAYS")
    chat_history_max_messages: int = Field(default=1000, env="CHAT_HISTORY_MAX_MESSAGES")
    
    # Analysis
    analysis_interval: int = Field(default=5000, env="ANALYSIS_INTERVAL")
    prediction_threshold: float = Field(default=0.7, env="PREDICTION_THRESHOLD")
    anomaly_threshold: float = Field(default=2.0, env="ANOMALY_THRESHOLD")
    min_data_points: int = Field(default=10, env="MIN_DATA_POINTS")
    
    # TimescaleDB (for plc_data queries)
    timescale_host: str = Field(default="timescale", env="TIMESCALE_HOST")
    timescale_port: int = Field(default=5432, env="TIMESCALE_PORT")
    timescale_db: str = Field(default="virtplc_ts", env="TIMESCALE_DB")
    timescale_user: str = Field(default="virtplc", env="TIMESCALE_USER")
    timescale_password: str = Field(default="changeme", env="TIMESCALE_PASSWORD")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Metrics
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
