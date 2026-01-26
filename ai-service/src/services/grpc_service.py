"""
gRPC service implementation for AI Service
"""
import asyncio
import logging
from concurrent import futures
from typing import List, Dict, Any, Optional
import grpc
from google.protobuf import timestamp_pb2
import numpy as np
from datetime import datetime

# Import generated protobuf code
from src.proto import ai_service_pb2, ai_service_pb2_grpc

from .services.ai_analyzer import AIAnalyzer
from .services.model_manager import ModelManager
from .database import get_session
from .config import settings

logger = logging.getLogger(__name__)


class AIService(ai_service_pb2_grpc.AIServiceServicer):
    """gRPC service implementation for AI operations"""

    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
        self.model_manager = ModelManager()
        logger.info("AI gRPC service initialized")

    async def AnalyzeData(self, request: ai_service_pb2.AnalyzeRequest,
                         context) -> ai_service_pb2.AnalysisResponse:
        """Analyze PLC data for anomalies and predictions"""
        try:
            logger.info(f"Analyzing {len(request.data_points)} data points")

            # Convert protobuf data points to internal format
            data_points = []
            for dp in request.data_points:
                point = {
                    'device_id': dp.device_id,
                    'type': dp.type,
                    'timestamp': dp.timestamp.ToDatetime(),
                    'data': self._convert_value_map(dp.data),
                    'metadata': self._convert_value_map(dp.metadata),
                    'rpm': dp.rpm if dp.HasField('rpm') else None,
                    'position_x': dp.position_x if dp.HasField('position_x') else None,
                    'position_y': dp.position_y if dp.HasField('position_y') else None,
                    'is_on': dp.is_on if dp.HasField('is_on') else None,
                    'in_operation': dp.in_operation if dp.HasField('in_operation') else None,
                }
                data_points.append(point)

            # Perform analysis
            analysis_type = request.analysis_type or "anomaly"
            parameters = dict(request.parameters) if request.parameters else {}

            results = await self.ai_analyzer.analyze_batch(
                data_points, analysis_type, parameters
            )

            # Convert results to protobuf format
            predictions = []
            anomalies = []

            for result in results.get('predictions', []):
                pred = ai_service_pb2.Prediction(
                    device_id=result['device_id'],
                    prediction_type=result['type'],
                    value=result['value'],
                    confidence=result['confidence'],
                    predicted_for=self._datetime_to_timestamp(result['timestamp'])
                )
                predictions.append(pred)

            for result in results.get('anomalies', []):
                anomaly = ai_service_pb2.Anomaly(
                    device_id=result['device_id'],
                    anomaly_type=result['type'],
                    severity=result['severity'],
                    description=result['description'],
                    detected_at=self._datetime_to_timestamp(result['timestamp'])
                )
                anomalies.append(anomaly)

            return ai_service_pb2.AnalysisResponse(
                predictions=predictions,
                anomalies=anomalies,
                confidence_score=results.get('overall_confidence', 0.0),
                analyzed_at=self._datetime_to_timestamp(datetime.utcnow())
            )

        except Exception as e:
            logger.error(f"Error in AnalyzeData: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ai_service_pb2.AnalysisResponse()

    async def StreamAnalysis(self, request_iterator, context):
        """Stream real-time analysis of incoming data points"""
        try:
            async for data_point in request_iterator:
                # Convert protobuf to internal format
                point = {
                    'device_id': data_point.device_id,
                    'type': data_point.type,
                    'timestamp': data_point.timestamp.ToDatetime(),
                    'data': self._convert_value_map(data_point.data),
                    'metadata': self._convert_value_map(data_point.metadata),
                    'rpm': data_point.rpm if data_point.HasField('rpm') else None,
                    'position_x': data_point.position_x if data_point.HasField('position_x') else None,
                    'position_y': data_point.position_y if data_point.HasField('position_y') else None,
                    'is_on': data_point.is_on if data_point.HasField('is_on') else None,
                    'in_operation': data_point.in_operation if data_point.HasField('in_operation') else None,
                }

                # Perform real-time analysis
                result = await self.ai_analyzer.analyze_realtime(point)

                # Convert to protobuf response
                analysis_result = ai_service_pb2.AnalysisResult(
                    device_id=point['device_id'],
                    timestamp=self._datetime_to_timestamp(point['timestamp'])
                )

                if 'prediction' in result:
                    pred = result['prediction']
                    analysis_result.prediction.CopyFrom(ai_service_pb2.Prediction(
                        device_id=pred['device_id'],
                        prediction_type=pred['type'],
                        value=pred['value'],
                        confidence=pred['confidence'],
                        predicted_for=self._datetime_to_timestamp(pred['timestamp'])
                    ))

                if 'anomaly' in result:
                    anomaly = result['anomaly']
                    analysis_result.anomaly.CopyFrom(ai_service_pb2.Anomaly(
                        device_id=anomaly['device_id'],
                        anomaly_type=anomaly['type'],
                        severity=anomaly['severity'],
                        description=anomaly['description'],
                        detected_at=self._datetime_to_timestamp(anomaly['timestamp'])
                    ))

                yield analysis_result

        except Exception as e:
            logger.error(f"Error in StreamAnalysis: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    async def GetModelStatus(self, request: ai_service_pb2.ModelStatusRequest,
                           context) -> ai_service_pb2.ModelStatusResponse:
        """Get status and metrics for AI models"""
        try:
            model_name = request.model_name or "default"
            status = await self.model_manager.get_model_status(model_name)

            metrics = {}
            if 'metrics' in status:
                for key, value in status['metrics'].items():
                    metrics[key] = float(value)

            return ai_service_pb2.ModelStatusResponse(
                model_name=status.get('name', model_name),
                status=status.get('status', 'unknown'),
                accuracy=status.get('accuracy', 0.0),
                last_trained=self._datetime_to_timestamp(status.get('last_trained', datetime.utcnow())),
                version=status.get('version', '1.0.0'),
                metrics=metrics
            )

        except Exception as e:
            logger.error(f"Error in GetModelStatus: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ai_service_pb2.ModelStatusResponse()

    async def TrainModel(self, request: ai_service_pb2.TrainRequest,
                        context) -> ai_service_pb2.TrainResponse:
        """Train or update AI models"""
        try:
            logger.info(f"Training model: {request.model_name}")

            # Convert training data
            training_data = []
            for dp in request.training_data:
                point = {
                    'device_id': dp.device_id,
                    'type': dp.type,
                    'timestamp': dp.timestamp.ToDatetime(),
                    'data': self._convert_value_map(dp.data),
                    'metadata': self._convert_value_map(dp.metadata),
                }
                training_data.append(point)

            # Train model
            result = await self.model_manager.train_model(
                model_name=request.model_name,
                algorithm=request.algorithm,
                training_data=training_data,
                hyperparameters=dict(request.hyperparameters)
            )

            metrics = {}
            if 'metrics' in result:
                for key, value in result['metrics'].items():
                    metrics[key] = float(value)

            return ai_service_pb2.TrainResponse(
                success=result.get('success', False),
                message=result.get('message', ''),
                model_version=result.get('version', '1.0.0'),
                metrics=metrics
            )

        except Exception as e:
            logger.error(f"Error in TrainModel: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ai_service_pb2.TrainResponse(success=False, message=str(e))

    def _convert_value_map(self, proto_map) -> Dict[str, Any]:
        """Convert protobuf Value map to Python dict"""
        result = {}
        for key, value in proto_map.items():
            if value.HasField('string_value'):
                result[key] = value.string_value
            elif value.HasField('int_value'):
                result[key] = value.int_value
            elif value.HasField('double_value'):
                result[key] = value.double_value
            elif value.HasField('bool_value'):
                result[key] = value.bool_value
        return result

    def _datetime_to_timestamp(self, dt: datetime) -> timestamp_pb2.Timestamp:
        """Convert datetime to protobuf timestamp"""
        ts = timestamp_pb2.Timestamp()
        ts.FromDatetime(dt)
        return ts


async def create_grpc_server(host: str = "0.0.0.0", port: int = 9091) -> grpc.aio.Server:
    """Create and configure gRPC server"""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
        ]
    )

    ai_service_pb2_grpc.add_AIServiceServicer_to_server(AIService(), server)
    server.add_insecure_port(f"{host}:{port}")

    logger.info(f"gRPC server configured on {host}:{port}")
    return server