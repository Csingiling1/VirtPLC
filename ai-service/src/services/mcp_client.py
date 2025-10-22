"""
Model Context Protocol (MCP) client for AI interactions
MCP provides structured communication between AI models and data sources
"""
import logging
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client for communicating with Spring Backend via Model Context Protocol
    
    MCP enables:
    - Structured context sharing between AI and backend
    - Tool calling for data retrieval
    - Real-time data streaming
    - Semantic caching
    """
    
    def __init__(self):
        self.server_url = settings.mcp_server_url
        self.timeout = settings.mcp_timeout
        self.enabled = settings.mcp_enabled
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def initialize(self):
        """Initialize MCP connection with Spring backend"""
        if not self.enabled:
            logger.info("MCP is disabled")
            return
        
        try:
            response = await self.client.post(
                f"{self.server_url}/mcp/initialize",
                json={
                    "client_info": {
                        "name": "virtplc-ai-service",
                        "version": "1.0.0"
                    },
                    "protocol_version": "1.0",
                    "capabilities": [
                        "tools",
                        "resources",
                        "prompts",
                        "sampling"
                    ]
                }
            )
            response.raise_for_status()
            logger.info("MCP initialized successfully")
            return response.json()
        except Exception as e:
            logger.error(f"MCP initialization failed: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from backend
        
        Tools might include:
        - get_sensor_data: Retrieve current sensor readings
        - get_equipment_status: Get equipment operational status
        - get_historical_data: Query historical time series
        - trigger_alert: Create maintenance alert
        """
        if not self.enabled:
            return []
        
        try:
            response = await self.client.get(f"{self.server_url}/mcp/tools")
            response.raise_for_status()
            tools = response.json()
            logger.info(f"Retrieved {len(tools)} tools from MCP server")
            return tools
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool via MCP
        
        Example:
            result = await mcp.call_tool(
                "get_sensor_data",
                {"symbol": "Motor1", "metrics": ["temperature", "vibration"]}
            )
        """
        if not self.enabled:
            logger.warning("MCP disabled, tool call skipped")
            return {}
        
        try:
            response = await self.client.post(
                f"{self.server_url}/mcp/tools/{tool_name}",
                json={"arguments": arguments}
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            raise
    
    async def get_sensor_data(
        self,
        symbols: List[str],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get current sensor data via MCP"""
        return await self.call_tool(
            "get_sensor_data",
            {
                "symbols": symbols,
                "metrics": metrics or []
            }
        )
    
    async def get_equipment_status(self, symbol: str) -> Dict[str, Any]:
        """Get equipment operational status via MCP"""
        return await self.call_tool(
            "get_equipment_status",
            {"symbol": symbol}
        )
    
    async def get_historical_data(
        self,
        symbol: str,
        metric: str,
        start_time: datetime,
        end_time: datetime,
        aggregation: str = "raw"
    ) -> Dict[str, Any]:
        """Get historical time series data via MCP"""
        return await self.call_tool(
            "get_historical_data",
            {
                "symbol": symbol,
                "metric": metric,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "aggregation": aggregation
            }
        )
    
    async def trigger_maintenance_alert(
        self,
        symbol: str,
        severity: str,
        message: str,
        predicted_failure_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Trigger maintenance alert via MCP"""
        return await self.call_tool(
            "trigger_alert",
            {
                "symbol": symbol,
                "alert_type": "maintenance",
                "severity": severity,
                "message": message,
                "predicted_failure_time": predicted_failure_time.isoformat() if predicted_failure_time else None
            }
        )
    
    async def get_context_for_llm(
        self,
        symbols: List[str],
        include_historical: bool = True,
        time_range_hours: int = 24
    ) -> str:
        """
        Get formatted context for LLM prompts
        
        Returns structured text with:
        - Current equipment status
        - Recent sensor readings
        - Historical trends
        - Recent anomalies/alerts
        """
        if not self.enabled:
            return "MCP disabled, using fallback context"
        
        try:
            response = await self.client.post(
                f"{self.server_url}/mcp/context",
                json={
                    "symbols": symbols,
                    "include_historical": include_historical,
                    "time_range_hours": time_range_hours
                }
            )
            response.raise_for_status()
            context = response.json()
            
            # Format context for LLM
            formatted = f"""
Factory Status as of {datetime.utcnow().isoformat()}

Equipment: {', '.join(symbols)}

Current Readings:
{context.get('current_readings', 'No data')}

Status Summary:
{context.get('status_summary', 'Unknown')}

Recent Trends ({time_range_hours}h):
{context.get('trends', 'No trend data')}

Recent Alerts:
{context.get('recent_alerts', 'No alerts')}
"""
            return formatted.strip()
        
        except Exception as e:
            logger.error(f"Failed to get LLM context: {e}")
            return f"Error retrieving context: {str(e)}"
    
    async def close(self):
        """Close MCP client"""
        await self.client.aclose()
        logger.info("MCP client closed")


# Global MCP client instance
mcp_client = MCPClient()
