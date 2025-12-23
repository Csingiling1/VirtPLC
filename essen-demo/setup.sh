#!/bin/bash

# Essen Demo Setup Script
# This script helps set up the multi-computer VirtPLC deployment

set -e

echo "🏭 VirtPLC Essen Demo Setup"
echo "============================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create external networks if they don't exist
print_status "Creating external networks..."

if ! docker network ls | grep -q "virtplc_data_network"; then
    docker network create --driver bridge --subnet=172.21.0.0/16 virtplc_data_network
    print_status "Created virtplc_data_network"
else
    print_warning "virtplc_data_network already exists"
fi

if ! docker network ls | grep -q "virtplc_plc_network"; then
    docker network create --driver bridge --subnet=172.20.0.0/16 virtplc_plc_network
    print_status "Created virtplc_plc_network"
else
    print_warning "virtplc_plc_network already exists"
fi

print_status "Setup complete!"
echo ""
echo "Next steps:"
echo "1. On PLC Computer (Gaming PC): docker-compose -f docker-compose.plc.yml up -d"
echo "2. On Data Server (Windows): docker-compose -f docker-compose.data.yml up -d"
echo "3. On Main Server (Linux): docker-compose -f docker-compose.main.yml up -d"
echo ""
echo "Remember to update IP addresses in docker-compose.main.yml for cross-computer communication!"</content>
<parameter name="filePath">/home/deginandor/Documents/Programming/VirtPLC/essen-demo/setup.sh