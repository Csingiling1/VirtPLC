"""
Model Context Protocol (MCP) client for AI interactions
MCP provides structured communication between AI models and data sources
"""
import logging
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime, timedelta

from ..config import settings
from .timebase_client import timebase_service

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
    
    async def get_timebase_data(
        self,
        symbols: List[str],
        metrics: Optional[List[str]] = None,
        hours_back: int = 24,
        aggregation: str = "raw"
    ) -> Dict[str, Any]:
        """
        Get time-series data directly from TimebaseDB via MCP
        
        Enhanced integration that bypasses backend for direct TimebaseDB access
        """
        try:
            # Get data directly from TimebaseDB
            all_data = []
            for symbol in symbols:
                if metrics:
                    for metric in metrics:
                        data = await timebase_service.get_time_range_data(
                            symbol=symbol,
                            metric_type=metric,
                            start_time=datetime.utcnow() - timedelta(hours=hours_back),
                            end_time=datetime.utcnow()
                        )
                        if not data.empty:
                            all_data.append({
                                "symbol": symbol,
                                "metric": metric,
                                "data": data.to_dict(orient="records")
                            })
                else:
                    # Get all metrics for symbol
                    data = await timebase_service.get_latest_readings([symbol], limit=1000)
                    if not data.empty:
                        all_data.append({
                            "symbol": symbol,
                            "data": data.to_dict(orient="records")
                        })
            
            return {
                "timebase_data": all_data,
                "query_info": {
                    "symbols": symbols,
                    "metrics": metrics,
                    "hours_back": hours_back,
                    "aggregation": aggregation,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"TimebaseDB query failed: {e}")
            return {"error": str(e)}
    
    async def get_predictive_insights(
        self,
        symbols: List[str],
        insight_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get AI-generated predictive insights from TimebaseDB
        
        Returns maintenance predictions, anomaly detections, and insights
        """
        try:
            # Query AI predictions and insights from TimebaseDB
            query = """
                SELECT timestamp, type, symbol, insight_type, title, description,
                       failure_probability, confidence, anomaly_score, severity,
                       recommended_action, priority, llm_model
                FROM ai_predictions
                WHERE symbol IN ({})
                  AND timestamp >= '{}'
                ORDER BY timestamp DESC
                LIMIT 50
            """.format(
                ','.join(f"'{s}'" for s in symbols),
                (datetime.utcnow() - timedelta(days=7)).isoformat()
            )
            
            insights_data = await timebase_service.query_data(query)
            
            insights = []
            if not insights_data.empty:
                for _, row in insights_data.iterrows():
                    insight = {
                        "timestamp": row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                        "type": row['type'],
                        "symbol": row['symbol'],
                        "title": row.get('title', ''),
                        "description": row.get('description', ''),
                        "confidence": float(row.get('confidence', 0)),
                        "severity": row.get('severity', 'unknown'),
                        "llm_model": row.get('llm_model', 'unknown')
                    }
                    
                    if row['type'] == 'MaintenancePrediction':
                        insight.update({
                            "failure_probability": float(row.get('failure_probability', 0)),
                            "recommended_action": row.get('recommended_action', '')
                        })
                    elif row['type'] == 'AnomalyDetection':
                        insight.update({
                            "anomaly_score": float(row.get('anomaly_score', 0))
                        })
                    
                    insights.append(insight)
            
            return {
                "insights": insights,
                "total_count": len(insights),
                "symbols_queried": symbols,
                "time_range_days": 7
            }
        except Exception as e:
            logger.error(f"Failed to get predictive insights: {e}")
            return {"error": str(e), "insights": []}
    
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
    
    async def get_ollama_context(
        self,
        symbols: List[str],
        context_type: str = "comprehensive",
        include_predictions: bool = True,
        include_anomalies: bool = True,
        hours_back: int = 24
    ) -> str:
        """
        Get structured context optimized for Ollama/qwen2.5-coder model
        
        Provides comprehensive factory data in a format suitable for code generation
        and analysis tasks.
        """
        try:
            context_parts = []
            
            # Current sensor data
            sensor_data = await self.get_timebase_data(symbols, hours_back=hours_back)
            if "timebase_data" in sensor_data and sensor_data["timebase_data"]:
                context_parts.append("## Current Sensor Data")
                for item in sensor_data["timebase_data"]:
                    context_parts.append(f"### Equipment: {item['symbol']}")
                    if 'data' in item and item['data']:
                        # Show last 5 readings for each metric
                        recent_data = item['data'][-5:] if len(item['data']) > 5 else item['data']
                        for reading in recent_data:
                            timestamp = reading.get('timestamp', 'unknown')
                            value = reading.get('value', 'N/A')
                            unit = reading.get('unit', '')
                            metric = reading.get('metric_type', 'unknown')
                            context_parts.append(f"- {metric}: {value} {unit} (at {timestamp})")
            
            # Predictive insights
            if include_predictions:
                insights = await self.get_predictive_insights(symbols)
                if insights.get("insights"):
                    context_parts.append("\n## AI Predictive Insights")
                    for insight in insights["insights"][:10]:  # Limit to 10 most recent
                        context_parts.append(f"### {insight['title']} ({insight['symbol']})")
                        context_parts.append(f"- Type: {insight['type']}")
                        context_parts.append(f"- Description: {insight['description']}")
                        context_parts.append(f"- Confidence: {insight['confidence']:.2f}")
                        if 'failure_probability' in insight:
                            context_parts.append(f"- Failure Probability: {insight['failure_probability']:.2f}")
                        if 'anomaly_score' in insight:
                            context_parts.append(f"- Anomaly Score: {insight['anomaly_score']:.2f}")
                        context_parts.append(f"- Severity: {insight['severity']}")
                        context_parts.append(f"- Generated by: {insight['llm_model']}")
                        context_parts.append("")
            
            # Equipment status summary
            context_parts.append("## Equipment Status Summary")
            for symbol in symbols:
                latest_data = await timebase_service.get_latest_readings([symbol], limit=1)
                if not latest_data.empty:
                    latest = latest_data.iloc[0]
                    status = "operational"  # Could be enhanced with actual status logic
                    context_parts.append(f"- {symbol}: {status} (last reading: {latest.get('timestamp', 'unknown')})")
                else:
                    context_parts.append(f"- {symbol}: no recent data")
            
            # Add metadata for Ollama
            context_parts.insert(0, f"""# Factory Monitoring Context
Generated: {datetime.utcnow().isoformat()}
Equipment: {', '.join(symbols)}
Time Range: {hours_back} hours
Context Type: {context_type}
AI Model: qwen2.5-coder:7b

This context provides real-time factory data for analysis and code generation tasks.
""")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate Ollama context: {e}")
            return f"Error generating context: {str(e)}"
    
    async def close(self):
        """Close MCP client"""
        await self.client.aclose()
        logger.info("MCP client closed")


# Global MCP client instance
mcp_client = MCPClient()
