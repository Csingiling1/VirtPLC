"""
Analysis routes for predictive analytics
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

from ..services.timebase_client import timebase_service
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

        # Get recent data
        data = await timebase_service.get_latest_readings(symbols=symbols, limit=100)

        # Use MCP for analysis if available
        if mcp_client.enabled:
            analysis = await mcp_client.analyze_data(data)
        else:
            analysis = {"status": "mock_analysis", "symbols": symbols}

        return {
            "predictions": analysis,
            "data_points": len(data) if not data.empty else 0
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