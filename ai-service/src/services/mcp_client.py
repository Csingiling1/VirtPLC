"""
Model Context Protocol (MCP) client for AI interactions with database
Uses FreePeak db-mcp-server for direct TimescaleDB access
"""
import logging
from typing import List, Dict, Any, Optional
import httpx
import json
from datetime import datetime, timedelta

from ..config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client for communicating with FreePeak db-mcp-server
    
    Provides structured database access for AI models via MCP protocol
    """
    
    def __init__(self):
        self.base_url = settings.mcp_server_url.replace('/sse', '')
        self.timeout = settings.mcp_timeout
        self.enabled = settings.mcp_enabled
        self.client = httpx.AsyncClient(timeout=self.timeout, base_url=self.base_url)
    
    async def initialize(self):
        """Initialize MCP connection"""
        if not self.enabled:
            logger.info("MCP is disabled")
            return
        
        try:
            # Test connection to MCP server
            response = await self.client.get("/health")
            if response.status_code == 200:
                logger.info("MCP server connection established")
            else:
                logger.warning(f"MCP server health check failed: {response.status_code}")
        except Exception as e:
            logger.error(f"MCP initialization failed: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available database tools from MCP server
        """
        if not self.enabled:
            return []
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            response = await self.client.post("/jsonrpc", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                tools = result.get("result", {}).get("tools", [])
                logger.info(f"Retrieved {len(tools)} tools from MCP server")
                return tools
            
            logger.warning(f"Failed to get tools from MCP server: {response.status_code}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a database tool via MCP
        
        Example:
            result = await mcp.call_tool(
                "query_timescale",
                {"query": "SELECT * FROM sensor_data LIMIT 10"}
            )
        """
        if not self.enabled:
            return {"error": "MCP disabled"}
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = await self.client.post("/jsonrpc", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("result", {})
            else:
                logger.error(f"MCP tool call failed: {response.status_code} - {response.text}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            return {"error": str(e)}
import logging
from typing import List, Dict, Any, Optional
import httpx
import json
from datetime import datetime, timedelta

from ..config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client for communicating with FreePeak db-mcp-server
    
    Provides structured database access for AI models via MCP protocol
    """
    
    def __init__(self):
        self.server_url = settings.mcp_server_url
        self.timeout = settings.mcp_timeout
        self.enabled = settings.mcp_enabled
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def initialize(self):
        """Initialize MCP connection"""
        if not self.enabled:
            logger.info("MCP is disabled")
            return
        
        try:
            # Test connection to MCP server
            response = await self.client.get(f"{self.server_url.replace('/sse', '')}/health")
            if response.status_code == 200:
                logger.info("MCP server connection established")
            else:
                logger.warning(f"MCP server health check failed: {response.status_code}")
        except Exception as e:
            logger.error(f"MCP initialization failed: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available database tools from MCP server
        """
        if not self.enabled:
            return []
        
        try:
            # For FreePeak db-mcp-server, use JSON-RPC over HTTP
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            response = await self.client.post(
                f"{self.server_url.replace('/sse', '')}/jsonrpc",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                tools = result.get("result", {}).get("tools", [])
                logger.info(f"Retrieved {len(tools)} tools from MCP server")
                return tools
            
            logger.warning(f"Failed to get tools from MCP server: {response.status_code}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a database tool via MCP
        
        Example:
            result = await mcp.call_tool(
                "query_timescale",
                {"query": "SELECT * FROM sensor_data LIMIT 10"}
            )
        """
        if not self.enabled:
            return {"error": "MCP disabled"}
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = await self.client.post(
                f"{self.server_url.replace('/sse', '')}/jsonrpc",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("result", {})
            else:
                logger.error(f"MCP tool call failed: {response.status_code} - {response.text}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def query_sensor_data(self, query: str) -> List[Dict[str, Any]]:
        """
        Query sensor data using MCP database tools
        """
        if not self.enabled:
            return []
        
        try:
            result = await self.call_tool("query_timescale", {"query": query})
            
            if "error" in result:
                logger.error(f"Database query failed: {result['error']}")
                return []
            
            # Extract data from MCP response
            content = result.get("content", [])
            if content and len(content) > 0:
                # Parse the text content
                text_content = content[0].get("text", "")
                
                # The response format is complex, extract the actual data
                # Look for "Results:" followed by tab-separated data
                if "Results:" in text_content:
                    # Find the data section
                    lines = text_content.split('\n')
                    data_start = -1
                    headers = []
                    
                    for i, line in enumerate(lines):
                        line = line.strip()
                        if line == "Results:":
                            continue
                        elif not line:  # Empty line
                            continue
                        elif line.startswith('-') and len(line) > 10:  # Separator line
                            data_start = i + 1
                            break
                        elif data_start == -1 and '\t' in line:  # Header line
                            headers = [h.strip() for h in line.split('\t')]
                    
                    # Parse data rows
                    results = []
                    if data_start > 0 and headers:
                        for line in lines[data_start:]:
                            line = line.strip()
                            if not line or line.startswith('Total rows:'):
                                break
                            if '\t' in line:
                                values = [v.strip() for v in line.split('\t')]
                                if len(values) == len(headers):
                                    row = dict(zip(headers, values))
                                    results.append(row)
                    
                    return results
                
                # Fallback: return raw result
                return [{"raw_result": text_content}]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to query sensor data: {e}")
            return []
    
    async def get_latest_sensor_readings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get latest sensor readings from TimescaleDB via MCP
        """
        query = f"""
        SELECT device_id, timestamp, motor1_speed, motor1_temp, motor1_run, motor1_fault,
               motor2_speed, motor2_temp, motor2_run, motor2_fault, conveyor1_speed,
               conveyor1_run, sensor1_value, sensor2_value, system_status, quality
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        
        return await self.query_sensor_data(query)
    
    async def get_historical_data(self, device_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get historical data for a specific device
        """
        query = f"""
        SELECT device_id, timestamp, motor1_speed, motor1_temp, motor1_run, motor1_fault,
               motor2_speed, motor2_temp, motor2_run, motor2_fault, conveyor1_speed,
               conveyor1_run, sensor1_value, sensor2_value, system_status, quality
        FROM sensor_data
        WHERE device_id = '{device_id}'
        AND timestamp >= NOW() - INTERVAL '{hours} hours'
        ORDER BY timestamp ASC
        """
        
        return await self.query_sensor_data(query)
    
    async def get_equipment_status(self) -> List[Dict[str, Any]]:
        """
        Get current equipment status
        """
        query = """
        SELECT device_id, timestamp, motor1_run, motor1_fault, motor2_run, motor2_fault,
               conveyor1_run, system_status
        FROM sensor_data
        WHERE timestamp >= NOW() - INTERVAL '1 hour'
        ORDER BY timestamp DESC
        LIMIT 10
        """
        
        return await self.query_sensor_data(query)
    
    async def close(self):
        """Close MCP client"""
        await self.client.aclose()
        logger.info("MCP client closed")


# Global MCP client instance
mcp_client = MCPClient()
