"""
Analysis routes for predictive analytics and data insights
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from ..services.timescale_client import timescale_service
from ..services.claude_client import claude_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/predict")
async def predict_anomalies(devices: Optional[List[str]] = None, hours: int = 24):
    """
    Predict anomalies in sensor data using machine learning
    """
    try:
        # Get historical data
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        if devices:
            all_data = []
            for device in devices:
                data = await timescale_service.get_device_data(device, start_time, end_time)
                all_data.extend(data)
        else:
            all_data = await timescale_service.get_latest_data(limit=1000)

        if not all_data:
            return {"predictions": [], "message": "No data available for analysis"}

        # Convert to DataFrame for analysis
        df = pd.DataFrame(all_data)

        # Prepare features for anomaly detection
        features = []
        if 'rpm' in df.columns:
            features.append('rpm')
        if 'position_x' in df.columns and 'position_y' in df.columns:
            # Calculate movement speed as a feature
            df['movement_speed'] = np.sqrt(df['position_x'].diff()**2 + df['position_y'].diff()**2)
            features.append('movement_speed')

        if not features:
            return {"predictions": [], "message": "No suitable features found for anomaly detection"}

        # Prepare data for ML
        feature_data = df[features].fillna(method='ffill').fillna(0)
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_data)

        # Anomaly detection using Isolation Forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomalies = iso_forest.fit_predict(scaled_features)

        # Prepare results
        predictions = []
        for i, row in df.iterrows():
            prediction = {
                "timestamp": row.get('timestamp'),
                "device_id": row.get('device_id'),
                "is_anomaly": anomalies[i] == -1,
                "anomaly_score": -iso_forest.score_samples([scaled_features[i]])[0],
                "features": {feature: row.get(feature) for feature in features}
            }
            predictions.append(prediction)

        return {
            "predictions": predictions,
            "total_analyzed": len(predictions),
            "anomalies_detected": sum(1 for p in predictions if p["is_anomaly"]),
            "analysis_period_hours": hours
        }

    except Exception as e:
        logger.error(f"Anomaly prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/insights")
async def get_insights(hours: int = 24):
    """
    Get AI-generated insights about system performance
    """
    try:
        # Get recent data for analysis
        data = await timescale_service.get_latest_data(limit=500)

        if not data:
            return {"insights": [], "message": "No data available for insights"}

        # Analyze data patterns
        insights = []

        # Device activity insight
        device_counts = {}
        for item in data:
            device = item.get('device_id', 'unknown')
            device_counts[device] = device_counts.get(device, 0) + 1

        most_active = max(device_counts.items(), key=lambda x: x[1])
        insights.append({
            "type": "activity",
            "title": "Most Active Device",
            "description": f"Device '{most_active[0]}' has the highest activity with {most_active[1]} readings",
            "priority": "low"
        })

        # Performance insights
        if data and 'rpm' in data[0]:
            rpms = [d.get('rpm', 0) for d in data if d.get('rpm') is not None]
            if rpms:
                avg_rpm = sum(rpms) / len(rpms)
                max_rpm = max(rpms)
                min_rpm = min(rpms)

                insights.append({
                    "type": "performance",
                    "title": "RPM Analysis",
                    "description": f"Average RPM: {avg_rpm:.1f}, Range: {min_rpm:.1f} - {max_rpm:.1f}",
                    "priority": "medium"
                })

        # Generate AI-powered insights using Claude
        try:
            data_summary = f"Analyzed {len(data)} data points from {len(device_counts)} devices. "
            data_summary += f"Most active device: {most_active[0]} with {most_active[1]} readings."

            ai_insight_prompt = f"Based on this industrial IoT data summary, provide one key insight about system performance or optimization opportunities: {data_summary}"

            ai_response = await claude_client.generate_text(
                prompt=ai_insight_prompt,
                system_prompt="You are an industrial IoT expert. Provide concise, actionable insights."
            )

            insights.append({
                "type": "ai_generated",
                "title": "AI Performance Insight",
                "description": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                "priority": "high"
            })

        except Exception as e:
            logger.warning(f"Failed to generate AI insight: {e}")

        return {
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat(),
            "data_points_analyzed": len(data)
        }

    except Exception as e:
        logger.error(f"Insights generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")


@router.post("/analyze-patterns")
async def analyze_patterns(devices: List[str], start_time: Optional[str] = None, end_time: Optional[str] = None):
    """
    Analyze patterns in device data for predictive maintenance
    """
    try:
        # Parse time range
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        else:
            end_dt = datetime.utcnow()

        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start_dt = end_dt - timedelta(hours=24)

        # Get data for analysis
        all_data = []
        for device in devices:
            data = await timescale_service.get_device_data(device, start_dt, end_dt)
            all_data.extend(data)

        if not all_data:
            return {"patterns": [], "message": "No data available for pattern analysis"}

        # Simple pattern analysis
        patterns = []

        # Trend analysis
        df = pd.DataFrame(all_data)
        if 'rpm' in df.columns and len(df) > 10:
            rpm_trend = df['rpm'].rolling(window=10).mean()
            if rpm_trend.iloc[-1] > rpm_trend.iloc[0] * 1.1:  # 10% increase
                patterns.append({
                    "type": "trend",
                    "description": f"Increasing RPM trend detected for devices: {', '.join(devices)}",
                    "severity": "medium",
                    "recommendation": "Monitor for potential wear or increased load"
                })

        # Consistency analysis
        if 'rpm' in df.columns:
            rpm_std = df['rpm'].std()
            rpm_mean = df['rpm'].mean()
            cv = rpm_std / rpm_mean if rpm_mean != 0 else 0  # Coefficient of variation

            if cv > 0.2:  # High variation
                patterns.append({
                    "type": "variability",
                    "description": f"High RPM variability detected (CV: {cv:.2f})",
                    "severity": "low",
                    "recommendation": "Normal operational variation"
                })

        return {
            "patterns": patterns,
            "devices_analyzed": devices,
            "time_range": {"start": start_dt.isoformat(), "end": end_dt.isoformat()},
            "data_points": len(all_data)
        }

    except Exception as e:
        logger.error(f"Pattern analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")


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
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # Get historical data from TimescaleDB
        data = await timescale_service.get_historical_data_for_range(start_dt, end_dt, limit)
        
        return {
            "data": data,
            "count": len(data),
            "filters_applied": {
                "query": query
            }
        }
    except Exception as e:
        logger.error(f"Historical data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))