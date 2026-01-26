"""
AI Analyzer service for anomaly detection and predictions
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI service for analyzing PLC data"""

    def __init__(self):
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        self.scaler = StandardScaler()
        self.anomaly_model = None
        self._load_models()

    def _load_models(self):
        """Load pre-trained models"""
        try:
            model_path = self.models_dir / "anomaly_detector.pkl"
            if model_path.exists():
                self.anomaly_model = joblib.load(model_path)
                logger.info("Loaded anomaly detection model")
            else:
                logger.info("No pre-trained model found, will use default")
        except Exception as e:
            logger.warning(f"Failed to load model: {e}")

    async def analyze_batch(self, data_points: List[Dict[str, Any]],
                           analysis_type: str = "anomaly",
                           parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze a batch of data points"""
        if parameters is None:
            parameters = {}

        results = {
            "predictions": [],
            "anomalies": [],
            "overall_confidence": 0.0
        }

        try:
            if analysis_type == "anomaly":
                results["anomalies"] = await self._detect_anomalies(data_points, parameters)
            elif analysis_type == "prediction":
                results["predictions"] = await self._generate_predictions(data_points, parameters)
            else:
                # Combined analysis
                results["anomalies"] = await self._detect_anomalies(data_points, parameters)
                results["predictions"] = await self._generate_predictions(data_points, parameters)

            # Calculate overall confidence
            all_confidences = []
            for anomaly in results["anomalies"]:
                all_confidences.append(anomaly.get("confidence", 0.5))
            for prediction in results["predictions"]:
                all_confidences.append(prediction.get("confidence", 0.5))

            if all_confidences:
                results["overall_confidence"] = np.mean(all_confidences)

        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")

        return results

    async def analyze_realtime(self, data_point: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single data point in real-time"""
        result = {}

        try:
            # Quick anomaly check
            anomaly = await self._check_single_anomaly(data_point)
            if anomaly:
                result["anomaly"] = anomaly

            # Generate prediction if applicable
            prediction = await self._predict_single(data_point)
            if prediction:
                result["prediction"] = prediction

        except Exception as e:
            logger.error(f"Error in real-time analysis: {e}")

        return result

    async def _detect_anomalies(self, data_points: List[Dict[str, Any]],
                               parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in data points"""
        anomalies = []
        threshold = parameters.get("threshold", 2.0)

        try:
            # Prepare data for anomaly detection
            features = []
            for point in data_points:
                feature_vector = self._extract_features(point)
                if feature_vector:
                    features.append(feature_vector)

            if not features:
                return anomalies

            # Scale features
            features_scaled = self.scaler.fit_transform(features)

            # Use pre-trained model or create new one
            if self.anomaly_model is None:
                self.anomaly_model = IsolationForest(
                    contamination=0.1,
                    random_state=42
                )
                self.anomaly_model.fit(features_scaled)

            # Predict anomalies
            predictions = self.anomaly_model.predict(features_scaled)
            scores = self.anomaly_model.decision_function(features_scaled)

            for i, (point, prediction, score) in enumerate(zip(data_points, predictions, scores)):
                if prediction == -1:  # Anomaly detected
                    severity = min(abs(score) * threshold, 1.0)
                    anomaly = {
                        "device_id": point["device_id"],
                        "type": "anomaly",
                        "severity": severity,
                        "description": f"Anomaly detected with score {score:.3f}",
                        "timestamp": point["timestamp"],
                        "confidence": min(severity + 0.3, 1.0)
                    }
                    anomalies.append(anomaly)

        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")

        return anomalies

    async def _generate_predictions(self, data_points: List[Dict[str, Any]],
                                  parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate predictions for data points"""
        predictions = []

        try:
            # Simple trend-based prediction for now
            # In a real implementation, this would use trained ML models
            for point in data_points:
                if point.get("rpm") is not None:
                    # Predict next RPM value based on current trend
                    current_rpm = point["rpm"]
                    predicted_rpm = current_rpm * (0.95 + np.random.random() * 0.1)  # ±5% variation

                    prediction = {
                        "device_id": point["device_id"],
                        "type": "rpm_prediction",
                        "value": predicted_rpm,
                        "confidence": 0.7,
                        "timestamp": point["timestamp"] + timedelta(minutes=5)
                    }
                    predictions.append(prediction)

        except Exception as e:
            logger.error(f"Error in prediction generation: {e}")

        return predictions

    async def _check_single_anomaly(self, data_point: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for anomaly in a single data point"""
        try:
            features = self._extract_features(data_point)
            if not features:
                return None

            features_scaled = self.scaler.transform([features])

            if self.anomaly_model:
                prediction = self.anomaly_model.predict(features_scaled)[0]
                score = self.anomaly_model.decision_function(features_scaled)[0]

                if prediction == -1:
                    return {
                        "device_id": data_point["device_id"],
                        "type": "anomaly",
                        "severity": min(abs(score) * 2.0, 1.0),
                        "description": f"Real-time anomaly detected with score {score:.3f}",
                        "timestamp": data_point["timestamp"],
                        "confidence": 0.8
                    }

        except Exception as e:
            logger.error(f"Error in single anomaly check: {e}")

        return None

    async def _predict_single(self, data_point: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate prediction for a single data point"""
        try:
            if data_point.get("rpm") is not None:
                current_rpm = data_point["rpm"]
                predicted_rpm = current_rpm * (0.98 + np.random.random() * 0.04)  # ±2% variation

                return {
                    "device_id": data_point["device_id"],
                    "type": "rpm_prediction",
                    "value": predicted_rpm,
                    "confidence": 0.75,
                    "timestamp": data_point["timestamp"] + timedelta(minutes=1)
                }

        except Exception as e:
            logger.error(f"Error in single prediction: {e}")

        return None

    def _extract_features(self, data_point: Dict[str, Any]) -> Optional[List[float]]:
        """Extract numerical features from data point"""
        try:
            features = []

            # Basic numerical values
            if data_point.get("rpm") is not None:
                features.append(float(data_point["rpm"]))
            else:
                features.append(0.0)

            if data_point.get("position_x") is not None:
                features.append(float(data_point["position_x"]))
            else:
                features.append(0.0)

            if data_point.get("position_y") is not None:
                features.append(float(data_point["position_y"]))
            else:
                features.append(0.0)

            # Boolean states as numerical
            features.append(1.0 if data_point.get("is_on") else 0.0)
            features.append(1.0 if data_point.get("in_operation") else 0.0)

            # Extract numerical values from data map
            if "data" in data_point:
                for key, value in data_point["data"].items():
                    if isinstance(value, (int, float)):
                        features.append(float(value))
                    elif isinstance(value, dict) and "value" in value:
                        if isinstance(value["value"], (int, float)):
                            features.append(float(value["value"]))

            return features[:10]  # Limit to 10 features

        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None</content>
<parameter name="filePath">/home/deginandor/Documents/Programming/VirtPLC/ai-service/src/services/ai_analyzer.py