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
            # Test connection by listing tools
            tools = await self.list_tools()
            if tools:
                logger.info(f"MCP server connection established - {len(tools)} tools available")
            else:
                logger.warning("MCP server connection established but no tools available")
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
                
                # Try to parse as JSON first (for queries that return JSON)
                try:
                    json_data = json.loads(text_content)
                    if isinstance(json_data, list):
                        return json_data
                    elif isinstance(json_data, dict):
                        return [json_data]
                except json.JSONDecodeError:
                    pass
                
                # Parse TSV format (tab-separated values)
                if "Results:" in text_content:
                    logger.debug("Attempting TSV parsing")
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
                                values = line.split('\t')
                                # Clean up values
                                values = [v.strip() for v in values]
                                if len(values) == len(headers):
                                    row = dict(zip(headers, values))
                                    # Parse JSON columns
                                    for key, value in row.items():
                                        if key == 'data' and value:
                                            try:
                                                row[key] = json.loads(value)
                                            except json.JSONDecodeError:
                                                pass
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
        Get latest sensor readings from TimescaleDB plc_data table via MCP
        """
        query = f"""
        SELECT timestamp, data
        FROM plc_data
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        
        raw_data = await self.query_sensor_data(query)
        
        # Transform the data to match expected format
        transformed_data = []
        for row in raw_data:
            if 'data' in row and row['data']:
                # The data is JSON with tenant structure
                tenant_data = row['data']
                if isinstance(tenant_data, dict):
                    for tenant_id, tenant_info in tenant_data.items():
                        if isinstance(tenant_info, dict) and 'manufacturers' in tenant_info:
                            for manufacturer in tenant_info.get('manufacturers', []):
                                for factory in manufacturer.get('factories', []):
                                    devices = factory.get('devices', [])
                                    plcs = factory.get('plcs', [])
                                    for device in devices:
                                        signals = device.get('signals', [])
                                        for signal in signals:
                                            transformed_data.append({
                                                'timestamp': row.get('timestamp'),
                                                'device_id': device.get('id', 'unknown'),
                                                'signal_name': signal.get('name', 'unknown'),
                                                'value': signal.get('value'),
                                                'unit': signal.get('unit', ''),
                                                'status': 'active'
                                            })
                                    
                                    # Also check PLCs for sensors
                                    for plc in plcs:
                                        sensors = plc.get('sensors', [])
                                        for sensor in sensors:
                                            # The sensor data is in signal_config
                                            signal_config = sensor.get('signal_config', {})
                                            transformed_data.append({
                                                'timestamp': row.get('timestamp'),
                                                'device_id': plc.get('id', 'unknown'),
                                                'signal_name': signal_config.get('name', sensor.get('name', 'unknown')),
                                                'value': signal_config.get('value'),
                                                'unit': signal_config.get('unit', ''),
                                                'status': 'active' if sensor.get('is_active', True) else 'inactive'
                                            })
        
        return transformed_data[:limit]
    
    async def get_historical_data(self, device_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get historical data for a specific device from plc_data table
        """
        query = f"""
        SELECT timestamp, 
               jsonb_object_keys(data) as tenant_id,
               data->jsonb_object_keys(data) as tenant_data
        FROM plc_data
        WHERE timestamp >= NOW() - INTERVAL '{hours} hours'
        ORDER BY timestamp ASC
        """
        
        raw_data = await self.query_sensor_data(query)
        
        # Filter and transform data for the specific device
        transformed_data = []
        for row in raw_data:
            if 'tenant_data' in row and row['tenant_data']:
                tenant_data = row['tenant_data']
                if isinstance(tenant_data, dict) and 'manufacturers' in tenant_data:
                    for manufacturer in tenant_data.get('manufacturers', []):
                        for factory in manufacturer.get('factories', []):
                            for device in factory.get('devices', []):
                                if device.get('id') == device_id:
                                    for signal in device.get('signals', []):
                                        transformed_data.append({
                                            'timestamp': row.get('timestamp'),
                                            'device_id': device.get('id'),
                                            'signal_name': signal.get('name'),
                                            'value': signal.get('value'),
                                            'unit': signal.get('unit', ''),
                                            'status': 'active'
                                        })
        
        return transformed_data
    
    async def get_historical_data_for_range(
        self, 
        start_time: datetime, 
        end_time: datetime, 
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get historical sensor data for a time range from plc_data table
        """
        query = f"""
        SELECT timestamp, data
        FROM plc_data
        WHERE timestamp >= '{start_time.isoformat()}'
        AND timestamp <= '{end_time.isoformat()}'
        ORDER BY timestamp ASC
        LIMIT {limit}
        """
        
        raw_data = await self.query_sensor_data(query)
        
        # Transform the data to match expected format
        transformed_data = []
        for row in raw_data:
            if 'data' in row and row['data']:
                # The data is JSON with tenant structure
                tenant_data = row['data']
                if isinstance(tenant_data, dict):
                    for tenant_id, tenant_info in tenant_data.items():
                        if isinstance(tenant_info, dict) and 'manufacturers' in tenant_info:
                            for manufacturer in tenant_info.get('manufacturers', []):
                                for factory in manufacturer.get('factories', []):
                                    devices = factory.get('devices', [])
                                    plcs = factory.get('plcs', [])
                                    for device in devices:
                                        signals = device.get('signals', [])
                                        for signal in signals:
                                            transformed_data.append({
                                                'timestamp': row.get('timestamp'),
                                                'device_id': device.get('id', 'unknown'),
                                                'signal_name': signal.get('name', 'unknown'),
                                                'value': signal.get('value'),
                                                'unit': signal.get('unit', ''),
                                                'status': 'active'
                                            })
                                    
                                    # Also check PLCs for sensors
                                    for plc in plcs:
                                        sensors = plc.get('sensors', [])
                                        for sensor in sensors:
                                            # The sensor data is in signal_config
                                            signal_config = sensor.get('signal_config', {})
                                            transformed_data.append({
                                                'timestamp': row.get('timestamp'),
                                                'device_id': plc.get('id', 'unknown'),
                                                'signal_name': signal_config.get('name', sensor.get('name', 'unknown')),
                                                'value': signal_config.get('value'),
                                                'unit': signal_config.get('unit', ''),
                                                'status': 'active' if sensor.get('is_active', True) else 'inactive'
                                            })
        
        return transformed_data[:limit]

    async def get_filtered_sensor_data(
        self,
        start_time: datetime,
        end_time: datetime,
        metrics: List[str] = None,
        devices: List[str] = None,
        limit: int = 2000
    ) -> List[Dict[str, Any]]:
        """
        Get filtered sensor data based on metrics and device types
        """
        query = f"""
        SELECT timestamp, data
        FROM plc_data
        WHERE timestamp >= '{start_time.isoformat()}'
        AND timestamp <= '{end_time.isoformat()}'
        ORDER BY timestamp ASC
        LIMIT {limit}
        """

        raw_data = await self.query_sensor_data(query)

        # Transform and filter the data
        transformed_data = []
        metrics = metrics or []
        devices = devices or []

        for row in raw_data:
            if 'data' in row and row['data']:
                tenant_data = row['data']
                if isinstance(tenant_data, dict):
                    for tenant_id, tenant_info in tenant_data.items():
                        if isinstance(tenant_info, dict) and 'manufacturers' in tenant_info:
                            for manufacturer in tenant_info.get('manufacturers', []):
                                for factory in manufacturer.get('factories', []):
                                    # Process devices
                                    for device in factory.get('devices', []):
                                        device_id = device.get('id', '').lower()
                                        device_name = device.get('name', '').lower()

                                        for signal in device.get('signals', []):
                                            signal_name = signal.get('name', '').lower()

                                            # Check if device and signal match filters
                                            device_matches = True
                                            if devices:
                                                device_matches = any(
                                                    device_filter.lower() in device_id or
                                                    device_filter.lower() in device_name or
                                                    device_filter.lower() in signal_name
                                                    for device_filter in devices
                                                )

                                            # Check if signal matches metrics filter
                                            signal_matches = True
                                            if metrics:
                                                signal_matches = any(
                                                    metric.lower() in signal_name
                                                    for metric in metrics
                                                )

                                            if device_matches and signal_matches:
                                                transformed_data.append({
                                                    'timestamp': row.get('timestamp'),
                                                    'device_id': device.get('id', 'unknown'),
                                                    'device_name': device.get('name', 'unknown'),
                                                    'signal_name': signal.get('name', 'unknown'),
                                                    'value': signal.get('value'),
                                                    'unit': signal.get('unit', ''),
                                                    'status': 'active'
                                                })

                                    # Process PLCs
                                    for plc in factory.get('plcs', []):
                                        plc_id = plc.get('id', '').lower()
                                        plc_name = plc.get('name', '').lower()

                                        for sensor in plc.get('sensors', []):
                                            signal_config = sensor.get('signal_config', {})
                                            signal_name = signal_config.get('name', '').lower()

                                            # Check if PLC and sensor match filters
                                            plc_matches = True
                                            if devices:
                                                plc_matches = any(
                                                    device_filter.lower() in plc_id or
                                                    device_filter.lower() in plc_name or
                                                    device_filter.lower() in signal_name
                                                    for device_filter in devices
                                                )

                                            # Check if sensor matches metrics filter
                                            sensor_matches = True
                                            if metrics:
                                                sensor_matches = any(
                                                    metric.lower() in signal_name
                                                    for metric in metrics
                                                )

                                            if plc_matches and sensor_matches:
                                                transformed_data.append({
                                                    'timestamp': row.get('timestamp'),
                                                    'device_id': plc.get('id', 'unknown'),
                                                    'device_name': plc.get('name', 'unknown'),
                                                    'signal_name': signal_config.get('name', 'unknown'),
                                                    'value': signal_config.get('value'),
                                                    'unit': signal_config.get('unit', ''),
                                                    'status': 'active' if sensor.get('is_active', True) else 'inactive'
                                                })

        return transformed_data[:limit]

    async def get_equipment_status(self) -> List[Dict[str, Any]]:
        """
        Get current equipment status from plc_data table
        """
        query = """
        SELECT timestamp, 
               jsonb_object_keys(data) as tenant_id,
               data->jsonb_object_keys(data) as tenant_data
        FROM plc_data
        WHERE timestamp >= NOW() - INTERVAL '1 hour'
        ORDER BY timestamp DESC
        LIMIT 10
        """
        
        raw_data = await self.query_sensor_data(query)
        
        # Transform to equipment status format
        status_data = []
        for row in raw_data:
            if 'tenant_data' in row and row['tenant_data']:
                tenant_data = row['tenant_data']
                if isinstance(tenant_data, dict) and 'manufacturers' in tenant_data:
                    for manufacturer in tenant_data.get('manufacturers', []):
                        for factory in manufacturer.get('factories', []):
                            for device in factory.get('devices', []):
                                status_data.append({
                                    'timestamp': row.get('timestamp'),
                                    'device_id': device.get('id'),
                                    'device_name': device.get('name', 'Unknown'),
                                    'status': 'running' if device.get('active', True) else 'stopped',
                                    'factory': factory.get('name', 'Unknown'),
                                    'manufacturer': manufacturer.get('name', 'Unknown')
                                })
        
        return status_data
    
    async def close(self):
        """Close MCP client"""
        await self.client.aclose()
        logger.info("MCP client closed")


# Global MCP client instance
mcp_client = MCPClient()
