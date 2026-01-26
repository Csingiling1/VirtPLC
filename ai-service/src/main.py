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

    # Start gRPC server
    # from .services.grpc_service import create_grpc_server
    # grpc_server = await create_grpc_server(
    #     host=settings.host,
    #     port=settings.grpc_port
    # )
    # await grpc_server.start()
    # logger.info(f"gRPC server started on port {settings.grpc_port}")

    # Store grpc_server for shutdown
    # app.state.grpc_server = grpc_server

    yield

    # Shutdown
    logger.info("Shutting down AI Service")
    # await grpc_server.stop(grace=5.0)
    await mcp_client.close()
# Create FastAPI app
app = FastAPI(
    title="VirtPLC AI Service API",
    description="""
    AI-powered analytics service for industrial IoT and factory automation.

    ## Features

    * **Predictive Analytics**: Machine learning models for equipment failure prediction
    * **Real-time Analysis**: WebSocket-based live data processing and insights
    * **MCP Integration**: Model Context Protocol for AI agent communication
    * **Ollama Models**: Local LLM deployment for privacy-preserving AI
    * **Factory Data Analysis**: Specialized algorithms for manufacturing data

    ## Authentication

    All endpoints require JWT authentication via Bearer token in the Authorization header.

    ## WebSocket Endpoints

    Real-time communication channels for:
    * Live chat with AI assistants
    * Real-time analytics streaming
    * Factory data monitoring alerts
    """,
    version="1.0.0",
    contact={
        "name": "VirtPLC AI Team",
        "email": "ai@virtplc.com",
        "url": "https://github.com/Csingiling1/VirtPLC"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
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
    grpc_status = "unknown"
    try:
        # Check if gRPC server is running
        if hasattr(app.state, 'grpc_server') and app.state.grpc_server:
            grpc_status = "running"
        else:
            grpc_status = "not_started"
    except Exception:
        grpc_status = "error"

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "mcp": "connected" if mcp_client.enabled else "disabled",
            "database": "connected" if mcp_client.enabled else "disconnected",
            "ollama": settings.ollama_host,
            "grpc": grpc_status,
            "ports": {
                "http": settings.port,
                "grpc": settings.grpc_port,
                "websocket": settings.ws_port
            }
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
