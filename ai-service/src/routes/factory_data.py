"""
Factory data query routes for natural language queries
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from ..services.timescale_client import timescale_client

router = APIRouter()
logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    count: int


@router.get("/stats")
async def get_database_stats():
    """Get overall database statistics"""
    try:
        timescale_client.connect()
        stats = timescale_client.get_data_stats()
        timescale_client.disconnect()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices")
async def list_devices(search: Optional[str] = None, limit: int = 50):
    """Search for devices"""
    try:
        timescale_client.connect()
        if search:
            results = timescale_client.search_devices(search)
        else:
            results = timescale_client.get_latest_readings(limit=limit)
        timescale_client.disconnect()
        return {"results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Failed to search devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_id}")
async def get_device_info(device_id: str, hours: int = 24):
    """Get device statistics"""
    try:
        timescale_client.connect()
        stats = timescale_client.get_device_stats(device_id, hours)
        readings = timescale_client.get_latest_readings(device_id, limit=100)
        timescale_client.disconnect()
        return {"stats": stats, "recent_readings": readings}
    except Exception as e:
        logger.error(f"Failed to get device info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/factories")
async def get_factory_summary(factory_id: Optional[str] = None):
    """Get factory summary"""
    try:
        timescale_client.connect()
        summary = timescale_client.get_factory_summary(factory_id)
        timescale_client.disconnect()
        return {"factories": summary, "count": len(summary)}
    except Exception as e:
        logger.error(f"Failed to get factory summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def execute_custom_query(request: QueryRequest):
    """Execute a custom SQL query"""
    try:
        # Security check
        query = request.query.strip()
        if not query.lower().startswith("select"):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
        
        timescale_client.connect()
        results = timescale_client.execute_query(query)
        timescale_client.disconnect()
        
        return QueryResponse(results=results, count=len(results))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
