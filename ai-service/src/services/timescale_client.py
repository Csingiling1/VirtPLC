"""
TimescaleDB client for querying factory PLC/sensor data
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import json

from ..config import settings

logger = logging.getLogger(__name__)


class TimescaleClient:
    """Client for TimescaleDB operations on plc_data"""
    
    def __init__(self):
        self.host = settings.timescale_host
        self.port = settings.timescale_port
        self.database = settings.timescale_db
        self.user = settings.timescale_user
        self.password = settings.timescale_password
        self.conn = None
        
    def connect(self):
        """Connect to TimescaleDB"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"Connected to TimescaleDB at {self.host}:{self.port}/{self.database}")
        except Exception as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from TimescaleDB"""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from TimescaleDB")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of dictionaries with query results
        """
        if not self.conn:
            self.connect()
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                # Convert RealDictRow to regular dict
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query failed: {e}\nQuery: {query}")
            raise
    
    def get_latest_readings(self, device_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get latest sensor/PLC readings"""
        query = """
            SELECT timestamp, device_id, type, 
                   data->>'name' as name,
                   metadata->>'tenant' as tenant,
                   metadata->>'factory' as factory,
                   metadata->>'category' as category,
                   metadata->>'priority' as priority
            FROM plc_data
        """
        
        if device_id:
            query += " WHERE device_id = %s"
            query += " ORDER BY timestamp DESC LIMIT %s"
            return self.execute_query(query, (device_id, limit))
        else:
            query += " ORDER BY timestamp DESC LIMIT %s"
            return self.execute_query(query, (limit,))
    
    def get_device_stats(self, device_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get statistics for a specific device over time period"""
        query = """
            SELECT 
                device_id,
                type,
                COUNT(*) as record_count,
                MIN(timestamp) as first_seen,
                MAX(timestamp) as last_seen,
                metadata->>'tenant' as tenant,
                metadata->>'factory' as factory
            FROM plc_data
            WHERE device_id = %s 
              AND timestamp > NOW() - INTERVAL '%s hours'
            GROUP BY device_id, type, metadata->>'tenant', metadata->>'factory'
        """
        results = self.execute_query(query, (device_id, hours))
        return results[0] if results else {}
    
    def get_factory_summary(self, factory_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get summary of all devices in a factory"""
        query = """
            SELECT 
                metadata->>'factory' as factory,
                metadata->>'tenant' as tenant,
                type,
                COUNT(DISTINCT device_id) as unique_devices,
                COUNT(*) as total_records,
                MAX(timestamp) as last_update
            FROM plc_data
            WHERE timestamp > NOW() - INTERVAL '1 hour'
        """
        
        if factory_id:
            query += " AND metadata->>'factory' = %s"
            query += " GROUP BY metadata->>'factory', metadata->>'tenant', type"
            return self.execute_query(query, (factory_id,))
        else:
            query += " GROUP BY metadata->>'factory', metadata->>'tenant', type"
            return self.execute_query(query)
    
    def get_sensor_value_by_name(self, sensor_name: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get sensor readings by sensor name (e.g., 'Motor Speed', 'temperature')"""
        query = """
            SELECT 
                timestamp,
                device_id,
                data->>'name' as sensor_name,
                data->'signal_config'->>'value' as value,
                data->'signal_config'->>'unit' as unit,
                metadata->>'factory' as factory
            FROM plc_data
            WHERE type = 'sensor'
              AND data->>'name' ILIKE %s
              AND timestamp > NOW() - INTERVAL '%s hours'
            ORDER BY timestamp DESC
            LIMIT 1000
        """
        return self.execute_query(query, (f'%{sensor_name}%', hours))
    
    def get_time_series_avg(self, device_id: str, interval: str = '5 minutes', hours: int = 24) -> List[Dict[str, Any]]:
        """Get time-bucketed averages for sensor data"""
        query = """
            SELECT 
                time_bucket(%s, timestamp) as bucket,
                device_id,
                type,
                AVG((data->'signal_config'->>'value')::float) as avg_value,
                COUNT(*) as sample_count
            FROM plc_data
            WHERE device_id = %s
              AND type = 'sensor'
              AND timestamp > NOW() - INTERVAL '%s hours'
              AND data->'signal_config'->>'value' IS NOT NULL
            GROUP BY bucket, device_id, type
            ORDER BY bucket DESC
        """
        return self.execute_query(query, (interval, device_id, hours))
    
    def search_devices(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for devices by name or ID"""
        query = """
            SELECT DISTINCT
                device_id,
                type,
                data->>'name' as name,
                metadata->>'factory' as factory,
                metadata->>'tenant' as tenant,
                MAX(timestamp) as last_seen
            FROM plc_data
            WHERE device_id ILIKE %s
               OR data->>'name' ILIKE %s
            GROUP BY device_id, type, data->>'name', metadata->>'factory', metadata->>'tenant'
            ORDER BY last_seen DESC
            LIMIT 50
        """
        search_pattern = f'%{search_term}%'
        return self.execute_query(query, (search_pattern, search_pattern))
    
    def get_data_stats(self) -> Dict[str, Any]:
        """Get overall database statistics"""
        query = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT device_id) as unique_devices,
                COUNT(DISTINCT metadata->>'tenant') as unique_tenants,
                COUNT(DISTINCT metadata->>'factory') as unique_factories,
                MIN(timestamp) as oldest_record,
                MAX(timestamp) as newest_record,
                pg_size_pretty(pg_total_relation_size('plc_data')) as table_size
            FROM plc_data
        """
        results = self.execute_query(query)
        return results[0] if results else {}


# Global instance
timescale_client = TimescaleClient()
