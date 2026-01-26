#!/bin/bash

# VirtPLC Monitoring Stack Startup Script
# This script starts the complete monitoring and observability stack

set -e

echo "🚀 Starting VirtPLC Monitoring Stack..."

# Check if docker-compose files exist
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found in current directory"
    exit 1
fi

if [ ! -f "docker-compose.monitoring.yml" ]; then
    echo "❌ Error: docker-compose.monitoring.yml not found in current directory"
    exit 1
fi

# Create monitoring directory if it doesn't exist
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/grafana/dashboards

# Start the monitoring stack
echo "📊 Starting monitoring services..."
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d prometheus grafana loki promtail alertmanager jaeger

echo "✅ Monitoring stack started successfully!"
echo ""
echo "📈 Access your monitoring tools:"
echo "  • Grafana:     http://localhost:3003 (admin/admin123)"
echo "  • Prometheus:  http://localhost:9090"
echo "  • AlertManager: http://localhost:9093"
echo "  • Jaeger:      http://localhost:16686"
echo "  • Loki:        http://localhost:3100"
echo ""
echo "📋 Available dashboards:"
echo "  • System Overview: Pre-configured metrics dashboard"
echo "  • Application Logs: Centralized logging view"
echo ""
echo "To stop the monitoring stack, run: docker-compose -f docker-compose.monitoring.yml down"