"""
SQLAlchemy models for relational data (PostgreSQL)
TimeBase is used for time series, PostgreSQL for relational/metadata
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # user, admin, analyst
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    dashboards = relationship("UserDashboard", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    """Chat sessions with AI"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Made nullable for demo
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, index=True)  # Auto-cleanup after 30 days
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Individual chat messages (up to 1 month retention)"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    tokens_used = Column(Integer)
    model_used = Column(String(50))
    message_metadata = Column(JSON)  # Additional context, tool calls, etc.
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class UserDashboard(Base):
    """User-customized React dashboard configurations"""
    __tablename__ = "user_dashboards"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    dashboard_name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="dashboards")
    components = relationship("DashboardComponent", back_populates="dashboard", cascade="all, delete-orphan")


class DashboardComponent(Base):
    """React components/metrics prompted by users for dashboards"""
    __tablename__ = "dashboard_components"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dashboard_id = Column(Integer, ForeignKey("user_dashboards.id"), nullable=False, index=True)
    component_type = Column(String(50), nullable=False)  # chart, gauge, table, alert, etc.
    component_name = Column(String(100), nullable=False)
    
    # Component Configuration
    config = Column(JSON, nullable=False)  # React component props, chart config, etc.
    # Example config structure:
    # {
    #   "chartType": "line",
    #   "metrics": ["motor1_temperature", "motor2_vibration"],
    #   "timeRange": "1h",
    #   "refreshInterval": 5000,
    #   "thresholds": {"warning": 70, "critical": 85}
    # }
    
    # Layout
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)  # Grid columns (out of 12)
    height = Column(Integer, default=3)  # Grid rows
    
    # AI Context
    prompt_text = Column(Text)  # Original user prompt that created this component
    ai_generated = Column(Boolean, default=False)
    generation_timestamp = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    dashboard = relationship("UserDashboard", back_populates="components")


class AIAnalysisLog(Base):
    """Log of AI analysis runs for auditing"""
    __tablename__ = "ai_analysis_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_type = Column(String(50), nullable=False)  # prediction, anomaly, recommendation
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    model_used = Column(String(50))
    input_data_summary = Column(JSON)
    output_summary = Column(JSON)
    confidence_score = Column(Float)
    execution_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    error_message = Column(Text)
    success = Column(Boolean, default=True)


class MetricDefinition(Base):
    """Catalog of available metrics for AI and dashboards"""
    __tablename__ = "metric_definitions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_key = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    unit = Column(String(20))
    category = Column(String(50))  # temperature, vibration, speed, pressure, etc.
    source_system = Column(String(50))  # opc-ua, plc, sensor, calculated
    timebase_field = Column(String(100))  # Field name in TimeBase stream
    aggregation_methods = Column(JSON)  # ["avg", "min", "max", "sum", "count"]
    normal_range_min = Column(Float)
    normal_range_max = Column(Float)
    critical_threshold = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
