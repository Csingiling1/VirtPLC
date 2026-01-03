#!/bin/bash

# VirtPLC Production Deployment Script
# This script helps deploy VirtPLC across 3 servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found! Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

print_status "Starting VirtPLC production deployment..."

# Function to deploy to a specific server
deploy_to_server() {
    local server_name=$1
    local server_ip=$2
    local compose_file=$3
    local description=$4

    print_status "Deploying $server_name to $server_ip..."
    print_status "Description: $description"

    # Check if we can reach the server
    if ping -c 1 -W 2 $server_ip &> /dev/null; then
        print_success "Server $server_ip is reachable"
    else
        print_warning "Server $server_ip is not reachable. Make sure it's configured correctly."
    fi

    echo "Run the following commands on $server_name ($server_ip):"
    echo "----------------------------------------"
    echo "# Copy deployment files to server"
    echo "scp -r /path/to/VirtPLC/prod user@$server_ip:~/"
    echo ""
    echo "# On the server, navigate to the directory and start services"
    echo "cd ~/prod"
    echo "docker-compose -f $compose_file up -d"
    echo ""
    echo "# Check that services are running"
    echo "docker-compose -f $compose_file ps"
    echo "----------------------------------------"
    echo ""
}

# Display deployment information
echo "=================================================="
echo "VirtPLC 3-Server Production Deployment"
echo "=================================================="
echo ""
echo "Network: 192.168.1.0/24"
echo "Make sure all servers can communicate on this network"
echo ""

# Historian Server
deploy_to_server "Historian Server" "$HISTORIAN_IP" "historian-compose.yml" "TimescaleDB + MCP Server for time-series data and AI access"

# PLC-AI Server
deploy_to_server "PLC-AI Server" "$PLC_AI_IP" "plc-ai-compose.yml" "Backend services, AI, frontend, and data collection"

# PLC Server
deploy_to_server "PLC Server" "$PLC_IP" "plc-compose.yml" "PLC simulator, Ignition HMI, and Node-RED"

echo "=================================================="
echo "Post-Deployment Checklist"
echo "=================================================="
echo ""
echo "1. Verify all services are running:"
echo "   docker-compose -f <compose-file> ps"
echo ""
echo "2. Check service health:"
echo "   docker-compose -f <compose-file> logs <service-name>"
echo ""
echo "3. Test connectivity between servers:"
echo "   - Historian: curl http://$MCP_IP:9092/health"
echo "   - PLC-AI: curl http://$PLC_AI_IP:18080/actuator/health"
echo "   - PLC: curl http://$PLC_IP:5000/simulation/status"
echo ""
echo "4. Access the application:"
echo "   - Frontend: http://$FRONTEND_IP:3000"
echo "   - Ignition HMI: http://$IGNITION_IP:8088"
echo "   - Node-RED: http://$NODERED_IP:1880"
echo ""
echo "5. Test AI functionality:"
echo "   - AI Service: http://$AI_IP:3001/docs"
echo "   - Make sure Claude API key is set for Claude model support"
echo ""

print_success "Deployment configuration complete!"
print_warning "Remember to:"
print_warning "  - Configure static IPs on each server"
print_warning "  - Set up firewall rules for inter-server communication"
print_warning "  - Change default passwords in production"
print_warning "  - Monitor logs for any connectivity issues"