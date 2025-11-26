"""
Analysis routes for predictive analytics
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

from ..services.mcp_client import mcp_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/predict")
async def predict_anomalies(symbols: List[str] = None):
    """
    Predict anomalies in sensor data
    """
    try:
        if not symbols:
            symbols = ["Motor1", "Motor2", "Sensor1"]

        # Get recent data from TimescaleDB via MCP
        data = await mcp_client.get_latest_sensor_readings(limit=100)

        # For now, return basic analysis based on data
        analysis = {
            "status": "data_retrieved", 
            "symbols": symbols,
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
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # If query is provided, analyze intent for filtering
        metrics = None
        devices = None
        if query:
            from .chat import analyze_sensor_intent
            intent = analyze_sensor_intent(query)
            metrics = intent.get('metrics', [])
            devices = intent.get('devices', [])
        
        # Get filtered historical data from MCP
        if metrics or devices:
            data = await mcp_client.get_filtered_sensor_data(
                start_dt, end_dt, metrics=metrics, devices=devices, limit=limit
            )
        else:
            # Fallback to unfiltered data if no query provided
            data = await mcp_client.get_historical_data_for_range(start_dt, end_dt, limit)
        
        return {
            "data": data,
            "count": len(data),
            "filters_applied": {
                "metrics": metrics,
                "devices": devices,
                "query": query
            }
        }
    except Exception as e:
        logger.error(f"Historical data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))