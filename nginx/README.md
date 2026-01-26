# NGINX Reverse Proxy

NGINX configuration for VirtPLC API gateway and reverse proxy.

## Overview

NGINX serves as the main entry point for VirtPLC, providing:
- Reverse proxy for backend services
- Static file serving for frontend
- SSL/TLS termination
- Load balancing
- Rate limiting

## Architecture

```
Client Requests
    ↓
NGINX (Port 80/443)
    ↓
├─→ Frontend (Port 3000)
├─→ Backend API (Port 8080)
├─→ AI Service (Port 3001)
├─→ Node-RED (Port 1880)
└─→ Grafana (Port 3002)
```

## Configuration

### Main Configuration

File: `nginx.conf`

```nginx
http {
    # Upstream services
    upstream backend {
        server backend:8080;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    upstream ai_service {
        server ai-service:3001;
    }
    
    # Server blocks for routing
    server {
        listen 80;
        
        location /api/ {
            proxy_pass http://backend/;
        }
        
        location /ai/ {
            proxy_pass http://ai_service/;
        }
        
        location / {
            proxy_pass http://frontend/;
        }
    }
}
```

## Routing Rules

| Path | Upstream Service | Description |
|------|-----------------|-------------|
| `/` | Frontend | Main web application |
| `/api/*` | Backend | REST API endpoints |
| `/ai/*` | AI Service | AI/ML analytics API |
| `/nodered/*` | Node-RED | Flow editor (admin) |
| `/grafana/*` | Grafana | Monitoring dashboards |

## Features

### Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20;
}
```

### SSL/TLS Configuration

```nginx
server {
    listen 443 ssl http2;
    
    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
}
```

### CORS Headers

```nginx
add_header Access-Control-Allow-Origin *;
add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
add_header Access-Control-Allow-Headers "Authorization, Content-Type";
```

### Compression

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

## Logging

Logs are written to `logs/` directory:

- **Access Log**: `logs/access.log`
- **Error Log**: `logs/error.log`

### Log Format

```nginx
log_format main '$remote_addr - $remote_user [$time_local] '
                '"$request" $status $body_bytes_sent '
                '"$http_referer" "$http_user_agent"';
```

## Running

### Docker Compose

```yaml
nginx:
  image: nginx:alpine
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/logs:/var/log/nginx
  ports:
    - "80:80"
    - "443:443"
```

### Standalone

```bash
# Test configuration
nginx -t -c nginx.conf

# Start NGINX
nginx -c nginx.conf

# Reload configuration
nginx -s reload

# Stop NGINX
nginx -s stop
```

## Health Checks

NGINX exposes a health check endpoint:

```nginx
location /health {
    access_log off;
    return 200 "healthy\n";
    add_header Content-Type text/plain;
}
```

## Performance Tuning

### Worker Processes

```nginx
worker_processes auto;
worker_connections 1024;
```

### Caching

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;

location /api/static/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 1h;
}
```

### Buffer Sizes

```nginx
client_body_buffer_size 10K;
client_header_buffer_size 1k;
client_max_body_size 8m;
large_client_header_buffers 2 1k;
```

## Security

### Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000";
```

### IP Whitelisting

```nginx
location /admin/ {
    allow 192.168.1.0/24;
    deny all;
}
```

## Troubleshooting

### 502 Bad Gateway
- Check upstream services are running: `docker-compose ps`
- Verify service names in nginx.conf match docker-compose.yml
- Check logs: `tail -f logs/error.log`

### 404 Not Found
- Verify routing rules in nginx.conf
- Check upstream path stripping is correct
- Test upstream directly: `curl http://backend:8080/health`

### SSL Certificate Errors
- Verify certificate files exist and are readable
- Check certificate validity: `openssl x509 -in cert.pem -text -noout`
- Ensure private key matches certificate

## Monitoring

Key metrics to monitor:
- Request rate and latency
- Upstream response times
- Error rates (4xx, 5xx)
- Connection counts
- SSL handshake times

## Related Services

- [Frontend](../frontend/README.md) - Web application
- [Backend](../backend/README.md) - API service
- [Monitoring](../monitoring/README.md) - Observability stack

## Additional Resources

- [NGINX Documentation](https://nginx.org/en/docs/)
- [NGINX Optimization Guide](https://nginx.org/en/docs/http/ngx_http_core_module.html)
