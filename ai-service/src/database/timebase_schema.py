"""
TimeBase stream schemas for time-series data
TimeBase uses QQL (similar to SQL) for querying time series data
"""

# TimeBase Schema Definition (as Python dict for documentation)
# In production, these would be defined in TimeBase using QQL or API

TIMEBASE_SCHEMAS = {
    "factory_metrics": {
        "description": "Main stream for factory sensor metrics",
        "type": "DURABLE",  # DURABLE or TRANSIENT
        "polymorphic": True,  # Allow multiple message types
        "messages": {
            "SensorReading": {
                "fields": [
                    {"name": "timestamp", "type": "TIMESTAMP", "description": "Reading timestamp"},
                    {"name": "symbol", "type": "VARCHAR(20)", "description": "Sensor/Equipment ID"},
                    {"name": "metric_type", "type": "VARCHAR(50)", "description": "Type of metric"},
                    {"name": "value", "type": "FLOAT", "description": "Metric value"},
                    {"name": "unit", "type": "VARCHAR(10)", "description": "Unit of measurement"},
                    {"name": "quality", "type": "INTEGER", "description": "Data quality (0-100)"},
                    {"name": "source", "type": "VARCHAR(50)", "description": "Data source (OPC-UA, PLC, etc)"},
                ]
            },
            "EquipmentState": {
                "fields": [
                    {"name": "timestamp", "type": "TIMESTAMP"},
                    {"name": "symbol", "type": "VARCHAR(20)", "description": "Equipment ID"},
                    {"name": "state", "type": "VARCHAR(20)", "description": "running, stopped, error, maintenance"},
                    {"name": "speed_rpm", "type": "FLOAT"},
                    {"name": "temperature_c", "type": "FLOAT"},
                    {"name": "vibration_mms", "type": "FLOAT"},
                    {"name": "power_kw", "type": "FLOAT"},
                    {"name": "efficiency", "type": "FLOAT", "description": "0-1 scale"},
                ]
            },
            "SystemEvent": {
                "fields": [
                    {"name": "timestamp", "type": "TIMESTAMP"},
                    {"name": "symbol", "type": "VARCHAR(20)"},
                    {"name": "event_type", "type": "VARCHAR(50)", "description": "alarm, warning, info, error"},
                    {"name": "severity", "type": "INTEGER", "description": "1-10 scale"},
                    {"name": "message", "type": "TEXT"},
                    {"name": "source", "type": "VARCHAR(50)"},
                ]
            }
        }
    },
    
    "ai_predictions": {
        "description": "AI-generated predictions and anomalies",
        "type": "DURABLE",
        "polymorphic": True,
        "messages": {
            "MaintenancePrediction": {
                "fields": [
                    {"name": "timestamp", "type": "TIMESTAMP"},
                    {"name": "symbol", "type": "VARCHAR(20)", "description": "Equipment ID"},
                    {"name": "prediction_horizon_hours", "type": "INTEGER"},
                    {"name": "failure_probability", "type": "FLOAT", "description": "0-1 scale"},
                    {"name": "confidence", "type": "FLOAT", "description": "0-1 scale"},
                    {"name": "recommended_action", "type": "TEXT"},
                    {"name": "model_version", "type": "VARCHAR(50)"},
                    {"name": "features_used", "type": "ARRAY(VARCHAR)"},
                ]
            },
            "AnomalyDetection": {
                "fields": [
                    {"name": "timestamp", "type": "TIMESTAMP"},
                    {"name": "symbol", "type": "VARCHAR(20)"},
                    {"name": "anomaly_score", "type": "FLOAT", "description": "Higher = more anomalous"},
                    {"name": "metrics_involved", "type": "ARRAY(VARCHAR)"},
                    {"name": "baseline_values", "type": "ARRAY(FLOAT)"},
                    {"name": "actual_values", "type": "ARRAY(FLOAT)"},
                    {"name": "deviation_std", "type": "FLOAT", "description": "Std deviations from normal"},
                    {"name": "severity", "type": "VARCHAR(20)", "description": "low, medium, high, critical"},
                ]
            },
            "AIInsight": {
                "fields": [
                    {"name": "timestamp", "type": "TIMESTAMP"},
                    {"name": "insight_type", "type": "VARCHAR(50)"},
                    {"name": "title", "type": "VARCHAR(200)"},
                    {"name": "description", "type": "TEXT"},
                    {"name": "affected_equipment", "type": "ARRAY(VARCHAR)"},
                    {"name": "confidence", "type": "FLOAT"},
                    {"name": "priority", "type": "INTEGER", "description": "1-10 scale"},
                    {"name": "llm_model", "type": "VARCHAR(50)"},
                ]
            }
        }
    },
    
    "aggregated_metrics": {
        "description": "Pre-aggregated metrics for faster queries (1min, 5min, 1hour)",
        "type": "DURABLE",
        "polymorphic": False,
        "messages": {
            "AggregatedMetric": {
                "fields": [
                    {"name": "timestamp", "type": "TIMESTAMP", "description": "Aggregation window start"},
                    {"name": "symbol", "type": "VARCHAR(20)"},
                    {"name": "metric_type", "type": "VARCHAR(50)"},
                    {"name": "window_size", "type": "VARCHAR(10)", "description": "1m, 5m, 1h, 1d"},
                    {"name": "avg_value", "type": "FLOAT"},
                    {"name": "min_value", "type": "FLOAT"},
                    {"name": "max_value", "type": "FLOAT"},
                    {"name": "sum_value", "type": "FLOAT"},
                    {"name": "count", "type": "INTEGER"},
                    {"name": "std_dev", "type": "FLOAT"},
                ]
            }
        }
    },
    
    "user_interactions": {
        "description": "User interactions with dashboards for AI learning",
        "type": "TRANSIENT",  # Short-term retention
        "polymorphic": False,
        "messages": {
            "DashboardView": {
                "fields": [
                    {"name": "timestamp", "type": "TIMESTAMP"},
                    {"name": "user_id", "type": "INTEGER"},
                    {"name": "dashboard_id", "type": "INTEGER"},
                    {"name": "component_id", "type": "INTEGER"},
                    {"name": "view_duration_seconds", "type": "INTEGER"},
                    {"name": "interactions", "type": "INTEGER", "description": "Click count"},
                ]
            }
        }
    }
}


# QQL Query Examples (as Python docstrings)
TIMEBASE_QUERIES = {
    "get_latest_readings": """
        SELECT * 
        FROM factory_metrics 
        WHERE symbol IN ('Motor1', 'Motor2', 'Conveyor1')
        ORDER BY timestamp DESC 
        LIMIT 100
    """,
    
    "get_temperature_trend": """
        SELECT timestamp, symbol, value 
        FROM factory_metrics 
        WHERE metric_type = 'temperature'
          AND timestamp >= NOW() - INTERVAL '1 HOUR'
        ORDER BY timestamp ASC
    """,
    
    "get_anomalies_last_24h": """
        SELECT * 
        FROM ai_predictions 
        WHERE timestamp >= NOW() - INTERVAL '24 HOURS'
          AND severity IN ('high', 'critical')
        ORDER BY anomaly_score DESC
    """,
    
    "get_aggregated_hourly": """
        SELECT * 
        FROM aggregated_metrics 
        WHERE symbol = 'Motor1'
          AND window_size = '1h'
          AND timestamp >= NOW() - INTERVAL '7 DAYS'
        ORDER BY timestamp ASC
    """,
}


# Python helper functions for TimeBase operations
def get_stream_config(stream_name: str) -> dict:
    """Get TimeBase stream configuration"""
    return TIMEBASE_SCHEMAS.get(stream_name, {})


def get_all_streams() -> list:
    """Get list of all TimeBase streams"""
    return list(TIMEBASE_SCHEMAS.keys())


def validate_message_type(stream_name: str, message_type: str) -> bool:
    """Validate if message type exists in stream"""
    schema = TIMEBASE_SCHEMAS.get(stream_name, {})
    messages = schema.get("messages", {})
    return message_type in messages
