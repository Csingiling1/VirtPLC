"""
Main FastAPI application for AI Service
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import asyncio
from datetime import datetime

from .config import settings
from .services.mcp_client import mcp_client
from .database.models import Base
from .database import get_engine

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting VirtPLC AI Service (Python)")
    
    # Initialize database
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
    
    # Initialize MCP
    try:
        await mcp_client.initialize()
    except Exception as e:
        logger.warning(f"MCP initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Service")
    await mcp_client.close()


# Create FastAPI app
app = FastAPI(
    title="VirtPLC AI Service",
    description="AI-powered predictive analysis for factory monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "mcp": "connected" if mcp_client.enabled else "disabled",
            "database": "connected" if mcp_client.enabled else "disconnected",
            "ollama": settings.ollama_host
        }
    }


@app.get("/test")
async def test_endpoint():
    """
    Test endpoint for curl testing
    Returns sample data and service status
    """
    try:
        # Test MCP connection
        mcp_tools = await mcp_client.list_tools() if mcp_client.enabled else []
        
        # Test database query via MCP
        sample_data = []
        if mcp_client.enabled:
            try:
                result = await mcp_client.call_tool("query_timescale", {
                    "query": "SELECT timestamp, device_id, type FROM plc_data ORDER BY timestamp DESC LIMIT 5"
                })
                sample_data = result
            except Exception as e:
                logger.warning(f"Failed to get sample data: {e}")
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "mcp": {
                "enabled": mcp_client.enabled,
                "tools_available": len(mcp_tools),
                "tools": [t.get("name") for t in mcp_tools]
            },
            "database": {
                "connected": mcp_client.enabled,
                "sample_data_available": bool(sample_data)
            },
            "ollama": {
                "host": settings.ollama_host,
                "model": settings.ollama_model
            },
            "sample_data": sample_data
        }
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Import routers
from .routes import analysis, chat, dashboard, factory_data

app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(factory_data.router, prefix="/api/factory", tags=["factory"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )
