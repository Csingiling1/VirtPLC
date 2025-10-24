# VirtPLC Production Deployment Guide

This guide covers deploying VirtPLC to production environments.

## Deployment Options

### Option 1: Single Server (Recommended for Start)
- **Best for**: Small to medium deployments, < 100 concurrent users
- **Infrastructure**: 1 server with 32GB+ RAM, 8+ CPU cores, 200GB+ SSD
- **Cost**: ~$50-100/month (cloud) or on-premise server
- **Complexity**: Low - use Docker Compose

### Option 2: Docker Swarm (Medium Scale)
- **Best for**: Multi-server, 100-500 concurrent users
- **Infrastructure**: 3-5 servers in swarm cluster
- **Cost**: ~$200-500/month
- **Complexity**: Medium - uses same compose files

### Option 3: Kubernetes (Enterprise Scale)
- **Best for**: > 500 concurrent users, multi-region
- **Infrastructure**: Managed K8s cluster (AKS/EKS/GKE)
- **Cost**: ~$500-2000+/month
- **Complexity**: High - see `/docs/ORCHESTRATION.md`

## Pre-Deployment Checklist

### Infrastructure Requirements

**Minimum Server Specs:**
- **CPU**: 8 cores (16 recommended)
- **RAM**: 32GB (64GB recommended with Ollama 17B)
- **Disk**: 200GB SSD (500GB recommended)
- **Network**: 1Gbps connection
- **OS**: Ubuntu 22.04 LTS or RHEL 8+

**Port Requirements:**
- 80/443 (HTTP/HTTPS) - Frontend
- 8080 (Backend API)
- 8000 (AI Service)
- 8088 (Ignition HMI)
- 5432 (PostgreSQL)
- 8086 (InfluxDB)
- 11434 (Ollama)

### Security Checklist

- [ ] Change all default passwords
- [ ] Generate strong JWT secret
- [ ] Configure firewall rules
- [ ] Set up SSL/TLS certificates
- [ ] Enable database encryption
- [ ] Configure backup strategy
- [ ] Set up monitoring/alerting
- [ ] Review security groups/network policies
- [ ] Enable audit logging
- [ ] Configure rate limiting

## Production Configuration

### 1. Environment Variables

Create production `.env` files for each service:

**backend/.env** (Production)
```bash
# Spring Boot
SPRING_PROFILES_ACTIVE=production

# PostgreSQL
POSTGRES_DB=virtplc_prod
POSTGRES_USER=virtplc_prod
POSTGRES_PASSWORD=<STRONG_PASSWORD_HERE>

# InfluxDB
INFLUXDB_USER=admin
INFLUXDB_PASSWORD=<STRONG_PASSWORD_HERE>
INFLUXDB_TOKEN=<GENERATE_SECURE_TOKEN>
INFLUXDB_ORG=virtplc
INFLUXDB_BUCKET=factory_data

# Security
JWT_SECRET=<GENERATE_STRONG_SECRET_256_BIT>
JWT_EXPIRATION=86400000

# Grafana
GRAFANA_PASSWORD=<STRONG_PASSWORD_HERE>
```

**Generate secrets:**
```bash
# JWT Secret (256-bit)
openssl rand -base64 32

# InfluxDB Token
openssl rand -hex 32

# Passwords
openssl rand -base64 24
```

**ai-service/.env** (Production)
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=virtplc_prod
POSTGRES_USER=virtplc_prod
POSTGRES_PASSWORD=<SAME_AS_BACKEND>

# InfluxDB
INFLUXDB_HOST=influxdb
INFLUXDB_PORT=8086
INFLUXDB_TOKEN=<SAME_AS_BACKEND>
INFLUXDB_ORG=virtplc
INFLUXDB_BUCKET=factory_data

# Ollama
OLLAMA_HOST=ollama
OLLAMA_MODEL=llama3.2:8b-instruct-q8_0
# For production with better accuracy:
# OLLAMA_MODEL=llama3.2:17b-instruct-q8_0

# MCP
MCP_ENABLED=true
MCP_SERVER_URL=

# Optional AI APIs
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

**frontend/.env** (Production)
```bash
NODE_ENV=production
VITE_API_URL=https://api.yourcompany.com
VITE_AI_URL=https://ai.yourcompany.com
VITE_IGNITION_URL=https://hmi.yourcompany.com
```

**HMI/.env** (Production)
```bash
GATEWAY_ADMIN_USERNAME=admin
GATEWAY_ADMIN_PASSWORD=<STRONG_PASSWORD_HERE>
LOG_LEVEL=INFO
SIMULATION_SPEED=1.0
```

### 2. SSL/TLS Configuration

#### Option A: Nginx Reverse Proxy (Recommended)

Create `nginx/nginx.conf`:
```nginx
upstream backend {
    server java-backend:8080;
}

upstream ai-service {
    server ai-backend:8000;
}

upstream frontend {
    server frontend:80;
}

upstream ignition {
    server ignition-edge:8088;
}

server {
    listen 80;
    server_name yourcompany.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourcompany.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 443 ssl http2;
    server_name api.yourcompany.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 443 ssl http2;
    server_name ai.yourcompany.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location / {
        proxy_pass http://ai-service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 443 ssl http2;
    server_name hmi.yourcompany.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location / {
        proxy_pass http://ignition;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Add nginx to docker-compose:
```yaml
# Create nginx/docker-compose.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - virtplc-shared
    restart: unless-stopped
```

#### Option B: Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificates
sudo certbot --nginx -d yourcompany.com -d api.yourcompany.com -d ai.yourcompany.com -d hmi.yourcompany.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

### 3. Database Backups

#### PostgreSQL Backup Script

Create `scripts/backup-postgres.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/var/backups/virtplc/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

# Backup
docker exec postgres pg_dump -U virtplc_prod -d virtplc_prod | gzip > "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# Remove old backups
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
```

#### InfluxDB Backup Script

Create `scripts/backup-influxdb.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/var/backups/virtplc/influxdb"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

docker exec influxdb influx backup -t <YOUR_TOKEN> "$BACKUP_DIR/backup_$TIMESTAMP"

echo "InfluxDB backup completed: backup_$TIMESTAMP"
```

#### Automated Backups with Cron

```bash
# Edit crontab
crontab -e

# Add backup jobs
0 2 * * * /opt/virtplc/scripts/backup-postgres.sh >> /var/log/virtplc-backup.log 2>&1
0 3 * * * /opt/virtplc/scripts/backup-influxdb.sh >> /var/log/virtplc-backup.log 2>&1
```

### 4. Monitoring & Alerting

#### Prometheus Configuration

Create `monitoring/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['java-backend:8081']  # Actuator metrics
    
  - job_name: 'ai-service'
    static_configs:
      - targets: ['ai-backend:8000']
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    
  - job_name: 'influxdb'
    static_configs:
      - targets: ['influxdb:8086']
```

#### Grafana Dashboards

Access Grafana at `https://yourcompany.com:3001`:
1. Import dashboard 11074 (Spring Boot)
2. Import dashboard 12708 (PostgreSQL)
3. Import dashboard 11074 (InfluxDB)
4. Create custom VirtPLC dashboard

### 5. Logging

#### Centralized Logging with Loki

Add to `backend/docker-compose.yml`:
```yaml
  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml
      - loki-data:/loki
    networks:
      - backend-network
    restart: unless-stopped

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - /var/log:/var/log:ro
      - ./promtail-config.yaml:/etc/promtail/config.yml
    networks:
      - backend-network
    restart: unless-stopped
```

## Deployment Steps

### Single Server Deployment

1. **Prepare Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Create deployment directory
sudo mkdir -p /opt/virtplc
cd /opt/virtplc
```

2. **Clone Repository**
```bash
git clone https://github.com/Dedzsinator/VirtPLC.git .
git checkout release  # Use stable branch
```

3. **Configure Environment**
```bash
# Copy example env files
cp backend/.env.example backend/.env
cp ai-service/.env.example ai-service/.env
cp frontend/.env.example frontend/.env
cp HMI/.env.example HMI/.env

# Edit with production values
nano backend/.env
nano ai-service/.env
nano frontend/.env
nano HMI/.env
```

4. **Create Shared Network**
```bash
docker network create virtplc-shared
```

5. **Build Images**
```bash
./orchestrate.sh build
```

6. **Pull Ollama Model**
```bash
# Start AI service first to download model
cd ai-service/
docker compose up -d ollama ollama-setup

# Wait for model download (check logs)
docker logs -f ollama-setup

# Once complete, proceed
cd ..
```

7. **Start All Services**
```bash
./orchestrate.sh start
```

8. **Verify Deployment**
```bash
./orchestrate.sh health
./orchestrate.sh status
```

9. **Configure Firewall**
```bash
# Allow required ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 8088/tcp
sudo ufw enable
```

10. **Set Up System Service**

Create `/etc/systemd/system/virtplc.service`:
```ini
[Unit]
Description=VirtPLC Services
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/virtplc
ExecStart=/opt/virtplc/orchestrate.sh start
ExecStop=/opt/virtplc/orchestrate.sh stop
StandardOutput=journal

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable virtplc
sudo systemctl start virtplc
```

### Docker Swarm Deployment (Multi-Server)

1. **Initialize Swarm on Manager**
```bash
docker swarm init --advertise-addr <MANAGER_IP>
```

2. **Join Workers**
```bash
# On worker nodes, run the join command from manager output
docker swarm join --token <TOKEN> <MANAGER_IP>:2377
```

3. **Deploy Stacks**
```bash
# Create overlay network
docker network create --driver overlay virtplc-shared

# Deploy each stack
docker stack deploy -c backend/docker-compose.yml backend
docker stack deploy -c ai-service/docker-compose.yml ai-service
docker stack deploy -c HMI/docker-compose.yml edge
docker stack deploy -c frontend/docker-compose.yml frontend
```

4. **Scale Services**
```bash
docker service scale backend_java-backend=3
docker service scale frontend_frontend=2
docker service scale ai-service_ai-backend=2
```

## Post-Deployment

### 1. Initial Configuration

- Access Ignition at `https://hmi.yourcompany.com:8088`
- Login with configured admin credentials
- Configure OPC-UA connections
- Import HMI projects
- Set up user accounts

### 2. Monitoring Setup

- Access Grafana at `https://yourcompany.com:3001`
- Configure alerting (email/Slack)
- Set up dashboards
- Configure alert thresholds

### 3. Testing

Run full integration tests as per `TEST.md`

### 4. Documentation

- Document deployment configuration
- Update DNS records
- Share access credentials (securely)
- Document backup/restore procedures

## Maintenance

### Regular Tasks

**Daily:**
- Check service health: `./orchestrate.sh health`
- Review logs for errors
- Monitor disk space

**Weekly:**
- Review backup logs
- Check for security updates
- Review performance metrics

**Monthly:**
- Update Docker images
- Review and rotate logs
- Database maintenance (VACUUM, ANALYZE)
- Review and update SSL certificates

### Updates & Rollbacks

**Update Procedure:**
```bash
# Backup first!
./scripts/backup-postgres.sh
./scripts/backup-influxdb.sh

# Pull latest code
git pull origin release

# Rebuild images
./orchestrate.sh build

# Rolling restart
cd backend/
docker compose up -d --no-deps java-backend

cd ../ai-service/
docker compose up -d --no-deps ai-backend

cd ../frontend/
docker compose up -d --no-deps frontend

cd ../HMI/
docker compose up -d --no-deps ignition-edge
```

**Rollback:**
```bash
git checkout <PREVIOUS_TAG>
./orchestrate.sh build
./orchestrate.sh restart
```

## Scaling Ollama for Production

### Use 17B Model for Better Accuracy

```bash
# Pull 17B model
docker exec ollama ollama pull llama3.2:17b-instruct-q8_0

# Update ai-service/.env
OLLAMA_MODEL=llama3.2:17b-instruct-q8_0

# Restart AI service
cd ai-service/
docker compose restart ai-backend
```

**Resource Requirements for 17B:**
- **RAM**: 24GB+ for Ollama container
- **CPU**: 16+ cores recommended
- **GPU**: NVIDIA GPU with 24GB+ VRAM (optional but recommended)

### Enable GPU Support

Edit `ai-service/docker-compose.yml`:
```yaml
  ollama:
    image: ollama/ollama:latest
    runtime: nvidia  # Enable this line
    environment:
      - NVIDIA_VISIBLE_DEVICES=all  # Enable this line
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

Install NVIDIA Container Toolkit:
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## Troubleshooting Production Issues

### Service Down
```bash
./orchestrate.sh status
docker logs <container-name>
./orchestrate.sh restart
```

### High CPU/Memory
```bash
docker stats
# Scale down Ollama or switch to 8B model
```

### Database Full
```bash
# Check disk space
df -h

# Clean old data
docker exec postgres psql -U virtplc_prod -d virtplc_prod -c "DELETE FROM logs WHERE created_at < NOW() - INTERVAL '90 days';"
```

### Ollama Not Responding
```bash
docker restart ollama
docker logs ollama
# If needed, repull model
docker exec ollama ollama pull llama3.2:8b-instruct-q8_0
```

## Support & Contact

- **GitHub Issues**: https://github.com/Dedzsinator/VirtPLC/issues
- **Documentation**: `/docs/`
- **Monitoring**: Grafana dashboard
- **Logs**: `./orchestrate.sh logs <service>`

---

**Deployment Checklist:** ✅ Server prepared | ✅ Environment configured | ✅ SSL/TLS set up | ✅ Backups configured | ✅ Monitoring enabled | ✅ Services running | ✅ Tests passed
