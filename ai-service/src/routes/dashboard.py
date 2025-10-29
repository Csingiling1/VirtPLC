"""
Dashboard routes for data visualization
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

from ..services.timebase_client import timebase_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metrics")
async def get_dashboard_metrics():
    """
    Get key metrics for dashboard
    """
    try:
        # Get latest readings
        symbols = ["Motor1", "Motor2", "Sensor1", "Sensor2"]
        data = await timebase_service.get_latest_readings(symbols=symbols, limit=50)

        # Calculate basic metrics
        metrics = {
            "total_sensors": len(symbols),
            "active_sensors": len(data.columns) if not data.empty else 0,
            "data_points": len(data) if not data.empty else 0,
            "last_update": data.index.max().isoformat() if not data.empty and len(data) > 0 else None
        }

        return metrics
    except Exception as e:
        logger.error(f"Dashboard metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chart-data")
async def get_chart_data(symbol: str = "Motor1", hours: int = 24):
    """
    Get time series data for charts
    """
    try:
        # Get historical data
        data = await timebase_service.get_historical_data(
            symbol=symbol,
            hours=hours
        )

        if data.empty:
            return {"data": [], "symbol": symbol}

        # Format for frontend charts
        chart_data = {
            "symbol": symbol,
            "data": [
                {
                    "timestamp": timestamp.isoformat(),
                    "value": float(value)
                } for timestamp, value in zip(data.index, data[symbol])
            ]
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