#!/bin/bash

# VirtPLC Microservices Orchestration Script
# Manages all 4 compose stacks: Edge (HMI), Frontend, AI Service, Backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EDGE_DIR="$PROJECT_ROOT/HMI"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
AI_DIR="$PROJECT_ROOT/ai-service"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Network name
SHARED_NETWORK="virtplc-shared"

# Functions
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

# Create shared network if it doesn't exist
create_network() {
    print_header "Creating Shared Network"
    if docker network inspect "$SHARED_NETWORK" >/dev/null 2>&1; then
        print_warning "Network $SHARED_NETWORK already exists"
    else
        docker network create "$SHARED_NETWORK"
        print_success "Network $SHARED_NETWORK created"
    fi
}

# Remove shared network
remove_network() {
    print_header "Removing Shared Network"
    if docker network inspect "$SHARED_NETWORK" >/dev/null 2>&1; then
        docker network rm "$SHARED_NETWORK"
        print_success "Network $SHARED_NETWORK removed"
    else
        print_warning "Network $SHARED_NETWORK does not exist"
    fi
}

# Start all stacks
start_all() {
    print_header "Starting All Stacks"
    create_network
    
    # Start backend first (has databases)
    print_info "Starting Backend Stack (PostgreSQL, Redis, TimescaleDB, Java Backend)..."
    cd "$BACKEND_DIR"
    docker compose up -d
    print_success "Backend stack started"
    
    # Wait for databases to be ready
    print_info "Waiting for databases to initialize (30s)..."
    sleep 30
    
    # Start AI service
    print_info "Starting AI Service Stack (FastAPI, Redis, MCP)..."
    cd "$AI_DIR"
    docker compose up -d
    print_success "AI service stack started"
    
    # Start Edge/HMI
    print_info "Starting Edge Stack (Ignition, Redis, PLC Simulator)..."
    cd "$EDGE_DIR"
    docker compose up -d
    print_success "Edge stack started"
    
    # Start Frontend
    print_info "Starting Frontend Stack (React, Nginx, Redis)..."
    cd "$FRONTEND_DIR"
    docker compose up -d
    print_success "Frontend stack started"
    
    cd "$PROJECT_ROOT"
    print_success "All stacks started successfully!"
    echo ""
    show_status
}

# Stop all stacks
stop_all() {
    print_header "Stopping All Stacks"
    
    print_info "Stopping Frontend..."
    cd "$FRONTEND_DIR"
    docker compose stop
    
    print_info "Stopping Edge/HMI..."
    cd "$EDGE_DIR"
    docker compose stop
    
    print_info "Stopping AI Service..."
    cd "$AI_DIR"
    docker compose stop
    
    print_info "Stopping Backend..."
    cd "$BACKEND_DIR"
    docker compose stop
    
    cd "$PROJECT_ROOT"
    print_success "All stacks stopped"
}

# Down all stacks (stop and remove containers)
down_all() {
    print_header "Bringing Down All Stacks"
    
    print_info "Removing Frontend..."
    cd "$FRONTEND_DIR"
    docker compose down
    
    print_info "Removing Edge/HMI..."
    cd "$EDGE_DIR"
    docker compose down
    
    print_info "Removing AI Service..."
    cd "$AI_DIR"
    docker compose down
    
    print_info "Removing Backend..."
    cd "$BACKEND_DIR"
    docker compose down
    
    cd "$PROJECT_ROOT"
    
    # Ask before removing network
    read -p "Remove shared network? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        remove_network
    fi
    
    print_success "All stacks removed"
}

# Restart all stacks
restart_all() {
    stop_all
    sleep 5
    start_all
}

# Show status of all services
show_status() {
    print_header "Service Status"
    
    echo -e "${YELLOW}Backend Stack:${NC}"
    cd "$BACKEND_DIR"
    docker compose ps
    
    echo ""
    echo -e "${YELLOW}AI Service Stack:${NC}"
    cd "$AI_DIR"
    docker compose ps
    
    echo ""
    echo -e "${YELLOW}Edge Stack:${NC}"
    cd "$EDGE_DIR"
    docker compose ps
    
    echo ""
    echo -e "${YELLOW}Frontend Stack:${NC}"
    cd "$FRONTEND_DIR"
    docker compose ps
    
    cd "$PROJECT_ROOT"
}

# Show logs
show_logs() {
    local stack=$1
    local follow=$2
    
    case $stack in
        backend)
            cd "$BACKEND_DIR"
            ;;
        ai|ai-service)
            cd "$AI_DIR"
            ;;
        edge|hmi)
            cd "$EDGE_DIR"
            ;;
        frontend)
            cd "$FRONTEND_DIR"
            ;;
        *)
            print_error "Unknown stack: $stack"
            print_info "Available stacks: backend, ai, edge, frontend"
            return 1
            ;;
    esac
    
    if [ "$follow" = "-f" ] || [ "$follow" = "--follow" ]; then
        docker compose logs -f
    else
        docker compose logs --tail=100
    fi
    
    cd "$PROJECT_ROOT"
}

# Build all images
build_all() {
    print_header "Building All Images"
    
    print_info "Building Backend..."
    cd "$BACKEND_DIR"
    docker compose build
    
    print_info "Building AI Service..."
    cd "$AI_DIR"
    docker compose build
    
    print_info "Building Edge/HMI..."
    cd "$EDGE_DIR"
    docker compose build
    
    print_info "Building Frontend..."
    cd "$FRONTEND_DIR"
    docker compose build
    
    cd "$PROJECT_ROOT"
    print_success "All images built"
}

# Health check
health_check() {
    print_header "Health Check"
    
    # Check backend
    print_info "Checking Backend (port 8080)..."
    if curl -sf http://localhost:8080/actuator/health > /dev/null 2>&1; then
        print_success "Backend is healthy"
    else
        print_error "Backend is not responding"
    fi
    
    # Check AI service
    print_info "Checking AI Service (port 8000)..."
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        print_success "AI Service is healthy"
    else
        print_error "AI Service is not responding"
    fi
    
    # Check Ignition
    print_info "Checking Ignition Edge (port 8088)..."
    if curl -sf http://localhost:8088/StatusPing > /dev/null 2>&1; then
        print_success "Ignition Edge is healthy"
    else
        print_error "Ignition Edge is not responding"
    fi
    
    # Check Frontend
    print_info "Checking Frontend (port 3000)..."
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend is healthy"
    else
        print_error "Frontend is not responding"
    fi
    
    # Check databases
    print_info "Checking PostgreSQL (port 5432)..."
    if nc -z localhost 5432 2>/dev/null; then
        print_success "PostgreSQL is running"
    else
        print_error "PostgreSQL is not running"
    fi
    
    print_info "Checking TimescaleDB (port 5433)..."
    if nc -z localhost 5433 2>/dev/null; then
        print_success "TimescaleDB is running"
    else
        print_error "TimescaleDB is not running"
    fi
}

# Show help
show_help() {
    cat << EOF
${BLUE}VirtPLC Microservices Orchestration${NC}

Usage: $0 [COMMAND] [OPTIONS]

${YELLOW}Commands:${NC}
  start         Start all stacks (backend → ai → edge → frontend)
  stop          Stop all stacks (without removing containers)
  down          Stop and remove all containers (asks about network)
  restart       Restart all stacks
  status        Show status of all services
  build         Build all images
  logs STACK    Show logs for specific stack (backend, ai, edge, frontend)
                Add -f or --follow to follow logs
  health        Run health checks on all services
  network       Create shared network manually
  help          Show this help message

${YELLOW}Examples:${NC}
  $0 start                  # Start all services
  $0 logs backend           # Show backend logs (last 100 lines)
  $0 logs ai -f             # Follow AI service logs
  $0 health                 # Check health of all services
  $0 down                   # Stop and remove all containers

${YELLOW}Service URLs:${NC}
  Frontend:       http://localhost:3000
  Backend API:    http://localhost:8080
  AI Service:     http://localhost:8000
  Ignition HMI:   http://localhost:8088
  PostgreSQL:     localhost:5432
  TimescaleDB:    localhost:5433
  Grafana:        http://localhost:3001

${YELLOW}Redis Instances:${NC}
  Edge Redis:     localhost:6379
  Frontend Redis: localhost:6380
  AI Redis:       localhost:6381
  Backend Redis:  localhost:6382

EOF
}

# Main script logic
case "${1:-}" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    down)
        down_all
        ;;
    restart)
        restart_all
        ;;
    status)
        show_status
        ;;
    build)
        build_all
        ;;
    logs)
        if [ -z "$2" ]; then
            print_error "Please specify a stack: backend, ai, edge, or frontend"
            exit 1
        fi
        show_logs "$2" "$3"
        ;;
    health)
        health_check
        ;;
    network)
        create_network
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac
