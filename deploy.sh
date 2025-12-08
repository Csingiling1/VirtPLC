#!/bin/bash

# VirtPLC Automated Deployment Script
# Deploys based on DEPLOYMENT_PROFILE in .env file

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    print_error ".env file not found!"
    print_info "Creating .env from .env.example..."
    cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
    print_warning "Please configure .env file and run again"
    exit 1
fi

# Load .env file
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Get deployment profile
PROFILE="${DEPLOYMENT_PROFILE:-dev}"

print_header "VirtPLC Deployment"
print_info "Deployment Profile: $PROFILE"
echo ""

# Function to deploy based on profile
deploy() {
    local profile=$1
    
    case $profile in
        dev)
            print_header "Starting Development Environment (Single Machine)"
            print_info "Running: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d"
            docker-compose -f "$PROJECT_ROOT/docker-compose.yml" \
                          -f "$PROJECT_ROOT/docker-compose.dev.yml" \
                          up -d
            print_success "Development environment started"
            ;;
            
        stage2)
            print_header "Starting Stage2 Environment (2 Computers)"
            print_warning "Make sure you've configured PLC_HOST and COMPUTER1_HOST in .env"
            print_info "Running: docker-compose -f docker-compose.yml -f docker-compose.stage2.yml up -d"
            docker-compose -f "$PROJECT_ROOT/docker-compose.yml" \
                          -f "$PROJECT_ROOT/docker-compose.stage2.yml" \
                          up -d
            print_success "Stage2 environment started"
            ;;
            
        prod)
            print_header "Starting Production Environment (3 Servers)"
            print_warning "Make sure you've configured SERVER1_HOST, SERVER2_HOST, SERVER3_HOST in .env"
            print_info "Running: docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
            docker-compose -f "$PROJECT_ROOT/docker-compose.yml" \
                          -f "$PROJECT_ROOT/docker-compose.prod.yml" \
                          up -d
            print_success "Production environment started"
            ;;
            
        plc)
            print_header "Starting PLC Profile"
            print_info "Running: docker-compose -f docker-compose.yml -f docker-compose.plc.yml up -d"
            docker-compose -f "$PROJECT_ROOT/docker-compose.yml" \
                          -f "$PROJECT_ROOT/docker-compose.plc.yml" \
                          up -d
            print_success "PLC profile started"
            ;;
            
        *)
            print_error "Unknown deployment profile: $profile"
            print_info "Valid profiles: dev, stage2, prod, plc"
            exit 1
            ;;
    esac
}

# Function to stop all services
stop() {
    print_header "Stopping All Services"
    
    # Try to stop each profile in case they're running
    for compose_file in docker-compose.dev.yml docker-compose.stage2.yml docker-compose.prod.yml docker-compose.plc.yml; do
        if [ -f "$PROJECT_ROOT/$compose_file" ]; then
            docker-compose -f "$PROJECT_ROOT/docker-compose.yml" \
                          -f "$PROJECT_ROOT/$compose_file" \
                          down 2>/dev/null || true
        fi
    done
    
    print_success "All services stopped"
}

# Function to show status
status() {
    print_header "Service Status"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" ps
}

# Function to show logs
logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" logs -f
    else
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" logs -f "$service"
    fi
}

# Main command handling
case "${1:-deploy}" in
    deploy|up|start)
        deploy "$PROFILE"
        echo ""
        print_header "Deployment Complete"
        print_success "Services are starting up..."
        print_info "Check status with: ./deploy.sh status"
        print_info "View logs with: ./deploy.sh logs [service]"
        ;;
        
    down|stop)
        stop
        ;;
        
    restart)
        stop
        sleep 2
        deploy "$PROFILE"
        ;;
        
    status|ps)
        status
        ;;
        
    logs)
        logs "$2"
        ;;
        
    help|--help|-h)
        print_header "VirtPLC Deployment Script"
        echo "Usage: ./deploy.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  deploy, up, start  - Deploy services based on .env DEPLOYMENT_PROFILE"
        echo "  down, stop         - Stop all services"
        echo "  restart            - Restart all services"
        echo "  status, ps         - Show service status"
        echo "  logs [service]     - Show logs (optionally for specific service)"
        echo "  help               - Show this help message"
        echo ""
        echo "Configuration:"
        echo "  Edit .env file to set DEPLOYMENT_PROFILE (dev, stage2, prod, plc)"
        echo ""
        ;;
        
    *)
        print_error "Unknown command: $1"
        print_info "Run './deploy.sh help' for usage information"
        exit 1
        ;;
esac
