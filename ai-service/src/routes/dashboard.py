"""
Dashboard routes for data visualization
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from ..services.timescale_client import timescale_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metrics")
async def get_dashboard_metrics():
    """
    Get key metrics for dashboard
    """
    try:
        # Get latest readings from TimescaleDB
        data = await timescale_service.get_latest_data(limit=50)

        # Calculate basic metrics
        metrics = {
            "total_devices": len(set(d.get('device_id') for d in data if d.get('device_id'))),
            "data_points": len(data),
            "last_update": data[0].get('timestamp') if data else None
        }

        return metrics
    except Exception as e:
        logger.error(f"Dashboard metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chart-data")
async def get_chart_data(device_id: str = "conveyor1", hours: int = 24):
    """
    Get time series data for charts
    """
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get historical data from TimescaleDB
        data = await timescale_service.get_device_data(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time
        )

        if not data:
            return {"data": [], "device_id": device_id}

        # Format for frontend charts
        chart_data = {
            "device_id": device_id,
            "data": data
        }

        return chart_data
    except Exception as e:
        logger.error(f"Chart data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_system_summary():
    """
    Get overall system status summary
    """
    try:
        # Mock summary data
        summary = {
            "status": "operational",
            "uptime": "24h",
            "alerts": 0,
            "efficiency": 95.2,
            "components": {
                "motors": {"active": 2, "total": 2},
                "sensors": {"active": 4, "total": 4},
                "controllers": {"active": 1, "total": 1}
            }
        }

        return summary
    except Exception as e:
        logger.error(f"System summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))