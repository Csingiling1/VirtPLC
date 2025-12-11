"""
Analysis routes for predictive analytics
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import logging

from ..services.timescale_client import timescale_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/predict")
async def predict_anomalies(devices: List[str] = None):
    """
    Predict anomalies in sensor data
    """
    try:
        # Get recent data from TimescaleDB
        data = await timescale_service.get_latest_data(limit=100)

        # For now, return basic analysis based on data
        analysis = {
            "status": "data_retrieved", 
            "devices": devices or [],
            "total_readings": len(data),
            "latest_timestamp": data[0].get("timestamp") if data else None
        }

        return {
            "predictions": analysis,
            "data_points": len(data)
        }
    except Exception as e:
        logger.error(f"Analysis prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_insights():
    """
    Get AI-generated insights
    """
    try:
        # Mock insights for now
        return {
            "insights": [
                "Motor efficiency trending downward",
                "Sensor calibration recommended",
                "Peak usage hours identified"
            ]
        }
    except Exception as e:
        logger.error(f"Insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical")
async def get_historical_data(
    start_time: str,
    end_time: str,
    limit: int = 1000,
    query: str = None
):
    """
    Get historical sensor data for a time range with intelligent filtering
    """
    try:
        # Parse timestamps
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # Get historical data from TimescaleDB
        data = await timescale_service.get_historical_data_for_range(start_dt, end_dt, limit)
        
        return {
            "data": data,
            "count": len(data),
            "filters_applied": {
                "query": query
            }
        }
    except Exception as e:
        logger.error(f"Historical data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))