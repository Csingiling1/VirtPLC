# VirtPLC Monitoring and Observability Stack

This directory contains the complete monitoring and observability setup for the VirtPLC platform, providing comprehensive insights into system performance, application metrics, and centralized logging.

## 🏗️ Architecture

The monitoring stack consists of:

- **Prometheus**: Metrics collection and time-series database
- **Grafana**: Visualization and dashboarding platform
- **Loki**: Log aggregation system
- **Promtail**: Log shipping agent
- **AlertManager**: Alert routing and notification system
- **Jaeger**: Distributed tracing (for future implementation)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Main VirtPLC services running

### Starting the Monitoring Stack

```bash
# Make sure you're in the project root directory
cd /path/to/VirtPLC

# Start monitoring services
./start-monitoring.sh
```

Or manually:
```bash
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### Accessing the Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3003 | admin/admin123 |
| Prometheus | http://localhost:9090 | - |
| AlertManager | http://localhost:9093 | - |
| Jaeger | http://localhost:16686 | - |
| Loki | http://localhost:3100 | - |

## 📊 Available Dashboards

### System Overview Dashboard
- CPU usage by service
- Memory usage by service
- Network I/O metrics
- Container health status

### Application Logs Dashboard
- Centralized log aggregation from all services
- Real-time log streaming
- Search and filter capabilities
- Structured log parsing

## 🔧 Configuration Files

### Prometheus (`monitoring/prometheus.yml`)
- Service discovery configuration
- Scraping intervals and targets
- Alert rules and recording rules

### Loki (`monitoring/loki-config.yml`)
- Log retention policies
- Schema configuration
- Storage settings

### Promtail (`monitoring/promtail-config.yml`)
- Log file discovery patterns
- Parsing pipelines
- Label extraction rules

### AlertManager (`monitoring/alertmanager.yml`)
- Alert routing rules
- Notification channels (Email, Slack)
- Inhibition and grouping settings

### Grafana Provisioning
- `monitoring/grafana/provisioning/datasources.yml`: Data source configurations
- `monitoring/grafana/provisioning/dashboards.yml`: Dashboard provisioning settings
- `monitoring/grafana/dashboards/`: JSON dashboard definitions

## 📈 Adding Custom Metrics

### Application Metrics
Add Prometheus client libraries to your services:

**Java/Spring Boot (pom.xml):**
```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

**Python/FastAPI (requirements.txt):**
```
prometheus-client
```

**Go (go.mod):**
```go
require github.com/prometheus/client_golang v1.16.0
```

### Custom Dashboards
1. Create dashboard JSON in `monitoring/grafana/dashboards/`
2. Restart Grafana or use the provisioning API
3. Dashboards will be automatically loaded

## 🚨 Alerting

### Default Alerts
- Service down detection
- High CPU/memory usage
- Disk space warnings
- Network connectivity issues

### Adding Custom Alerts
Edit `monitoring/prometheus.yml` and add rules to the `rule_files` section.

Example alert rule:
```yaml
groups:
  - name: custom_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}% for {{ $labels.service }}"
```

## 🔍 Log Aggregation

### Log Labels
All logs are automatically labeled with:
- `namespace`: virtplc
- `service`: container service name
- `container_name`: full container name
- `filename`: log file path

### Log Queries
Use Loki query language in Grafana Explore:

```
{service="backend"} |= "ERROR"
{namespace="virtplc"} | json | level="error"
rate({service="frontend"}[5m])
```

## 🛠️ Troubleshooting

### Services Not Starting
```bash
# Check service logs
docker-compose -f docker-compose.monitoring.yml logs <service_name>

# Check service status
docker-compose -f docker-compose.monitoring.yml ps
```

### Metrics Not Appearing
1. Verify Prometheus targets are healthy: http://localhost:9090/targets
2. Check service metrics endpoints are accessible
3. Ensure services are on the same Docker network

### Logs Not Appearing
1. Check Promtail status: `docker-compose logs promtail`
2. Verify log file paths in `promtail-config.yml`
3. Ensure containers are writing to stdout/stderr

## 🔒 Security Considerations

### Production Deployment
- Change default Grafana credentials
- Configure TLS/SSL for all services
- Use secrets management for sensitive configurations
- Implement network segmentation
- Set up authentication and authorization

### Network Security
- Use internal Docker networks only
- Configure firewall rules
- Implement rate limiting
- Regular security updates

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [AlertManager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)

## 🤝 Contributing

When adding new services or metrics:
1. Update Prometheus configuration for new targets
2. Add appropriate dashboards
3. Configure alerting rules if needed
4. Update this documentation