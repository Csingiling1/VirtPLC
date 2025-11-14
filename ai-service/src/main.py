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
from .services.timebase_client import timebase_service
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
    
    # Connect to TimeBase
    try:
        await timebase_service.connect()
    except Exception as e:
        logger.warning(f"TimeBase connection failed: {e}")
    
    # Initialize MCP
    try:
        await mcp_client.initialize()
    except Exception as e:
        logger.warning(f"MCP initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Service")
    await timebase_service.disconnect()
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
        
        # Test TimeBase query
        sample_data = await timebase_service.get_latest_readings(
            symbols=["Motor1", "Motor2"],
            limit=5
        )
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "mcp": {
                "enabled": mcp_client.enabled,
                "tools_available": len(mcp_tools),
                "tools": [t.get("name") for t in mcp_tools]
            },
            "timebase": {
                "connected": timebase_service.client is not None,
                "sample_data_points": len(sample_data) if not sample_data.empty else 0
            },
            "ollama": {
                "host": settings.ollama_host,
                "model": settings.ollama_model
            },
            "sample_data": sample_data.to_dict(orient="records") if not sample_data.empty else []
        }
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Import routers
from .routes import analysis, chat, dashboard

app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )
