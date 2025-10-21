"""
TimeBase client for time-series data operations
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

# TimeBase Python client (pseudo-implementation - adjust based on actual SDK)
try:
    from timebase import TimeBaseClient, QQLQuery, MessageWriter
except ImportError:
    # Fallback for development without TimeBase
    logging.warning("TimeBase client not available, using mock implementation")
    TimeBaseClient = None
    QQLQuery = None
    MessageWriter = None

from ..config import settings
from ..database.timebase_schema import TIMEBASE_QUERIES

logger = logging.getLogger(__name__)


class TimeBaseService:
    """Service for TimeBase operations"""
    
    def __init__(self):
        self.url = settings.timebase_url
        self.user = settings.timebase_user
        self.password = settings.timebase_password
        self.stream = settings.timebase_stream
        self.client = None
        
    async def connect(self):
        """Connect to TimeBase"""
        if TimeBaseClient is None:
            logger.warning("TimeBase client not available, using mock mode")
            return
        
        try:
            self.client = TimeBaseClient(
                url=self.url,
                username=self.user,
                password=self.password
            )
            await self.client.connect()
            logger.info(f"Connected to TimeBase at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to TimeBase: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from TimeBase"""
        if self.client:
            await self.client.disconnect()
            logger.info("Disconnected from TimeBase")
    
    async def query_data(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Execute QQL query and return results as DataFrame
        
        Args:
            query: QQL query string
            params: Query parameters
            
        Returns:
            DataFrame with query results
        """
        if self.client is None:
            logger.warning("Using mock data - TimeBase not connected")
            return self._mock_query_data()
        
        try:
            cursor = await self.client.query(query, params)
            data = await cursor.fetchall()
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    async def get_latest_readings(
        self,
        symbols: List[str],
        limit: int = 100
    ) -> pd.DataFrame:
        """Get latest sensor readings for specified equipment"""
        query = """
            SELECT timestamp, symbol, metric_type, value, unit, quality
            FROM factory_metrics
            WHERE symbol IN ({})
            ORDER BY timestamp DESC
            LIMIT {}
        """.format(
            ','.join(f"'{s}'" for s in symbols),
            limit
        )
        return await self.query_data(query)
    
    async def get_time_range_data(
        self,
        symbol: str,
        metric_type: str,
        start_time: datetime,
        end_time: datetime
    ) -> pd.DataFrame:
        """Get data for specific metric in time range"""
        query = """
            SELECT timestamp, value, unit, quality
            FROM factory_metrics
            WHERE symbol = '{}'
              AND metric_type = '{}'
              AND timestamp BETWEEN '{}' AND '{}'
            ORDER BY timestamp ASC
        """.format(
            symbol,
            metric_type,
            start_time.isoformat(),
            end_time.isoformat()
        )
        return await self.query_data(query)
    
    async def get_aggregated_metrics(
        self,
        symbol: str,
        window_size: str,
        hours_back: int = 24
    ) -> pd.DataFrame:
        """Get pre-aggregated metrics"""
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        query = """
            SELECT timestamp, metric_type, avg_value, min_value, max_value, std_dev
            FROM aggregated_metrics
            WHERE symbol = '{}'
              AND window_size = '{}'
              AND timestamp >= '{}'
            ORDER BY timestamp ASC
        """.format(symbol, window_size, start_time.isoformat())
        return await self.query_data(query)
    
    async def write_prediction(
        self,
        symbol: str,
        failure_probability: float,
        confidence: float,
        horizon_hours: int,
        recommended_action: str,
        model_version: str,
        features: List[str]
    ):
        """Write maintenance prediction to TimeBase"""
        if self.client is None:
            logger.warning("Cannot write to TimeBase - not connected")
            return
        
        message = {
            "type": "MaintenancePrediction",
            "timestamp": datetime.utcnow(),
            "symbol": symbol,
            "prediction_horizon_hours": horizon_hours,
            "failure_probability": failure_probability,
            "confidence": confidence,
            "recommended_action": recommended_action,
            "model_version": model_version,
            "features_used": features
        }
        
        try:
            writer = await self.client.get_writer("ai_predictions")
            await writer.write(message)
            logger.info(f"Written prediction for {symbol}")
        except Exception as e:
            logger.error(f"Failed to write prediction: {e}")
    
    async def write_anomaly(
        self,
        symbol: str,
        anomaly_score: float,
        metrics_involved: List[str],
        baseline_values: List[float],
        actual_values: List[float],
        deviation_std: float,
        severity: str
    ):
        """Write anomaly detection to TimeBase"""
        if self.client is None:
            logger.warning("Cannot write to TimeBase - not connected")
            return
        
        message = {
            "type": "AnomalyDetection",
            "timestamp": datetime.utcnow(),
            "symbol": symbol,
            "anomaly_score": anomaly_score,
            "metrics_involved": metrics_involved,
            "baseline_values": baseline_values,
            "actual_values": actual_values,
            "deviation_std": deviation_std,
            "severity": severity
        }
        
        try:
            writer = await self.client.get_writer("ai_predictions")
            await writer.write(message)
            logger.info(f"Written anomaly for {symbol}")
        except Exception as e:
            logger.error(f"Failed to write anomaly: {e}")
    
    async def write_ai_insight(
        self,
        insight_type: str,
        title: str,
        description: str,
        affected_equipment: List[str],
        confidence: float,
        priority: int,
        llm_model: str
    ):
        """Write AI-generated insight to TimeBase"""
        if self.client is None:
            logger.warning("Cannot write to TimeBase - not connected")
            return
        
        message = {
            "type": "AIInsight",
            "timestamp": datetime.utcnow(),
            "insight_type": insight_type,
            "title": title,
            "description": description,
            "affected_equipment": affected_equipment,
            "confidence": confidence,
            "priority": priority,
            "llm_model": llm_model
        }
        
        try:
            writer = await self.client.get_writer("ai_predictions")
            await writer.write(message)
            logger.info(f"Written AI insight: {title}")
        except Exception as e:
            logger.error(f"Failed to write insight: {e}")
    
    def _mock_query_data(self) -> pd.DataFrame:
        """Mock data for development without TimeBase"""
        import numpy as np
        
        timestamps = pd.date_range(
            start=datetime.utcnow() - timedelta(hours=1),
            end=datetime.utcnow(),
            freq='1min'
        )
        
        data = {
            'timestamp': timestamps,
            'symbol': ['Motor1'] * len(timestamps),
            'metric_type': ['temperature'] * len(timestamps),
            'value': 70 + 5 * np.sin(np.arange(len(timestamps)) / 10) + np.random.randn(len(timestamps)),
            'unit': ['celsius'] * len(timestamps),
            'quality': [100] * len(timestamps)
        }
        
        return pd.DataFrame(data)


# Global TimeBase service instance
timebase_service = TimeBaseService()
