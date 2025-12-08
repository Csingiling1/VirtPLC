#!/bin/bash

# VirtPLC Quick Start Script
# Automatically detects and starts the appropriate deployment profile

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker found: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose found: $(docker-compose --version)"
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    print_success "Docker daemon is running"
}

# Load environment
load_environment() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.example .env
        print_info "Please edit .env file with your configuration"
        print_info "After editing, run this script again"
        exit 0
    fi
    
    source .env
    print_success "Environment loaded from .env"
}

# Detect profile
detect_profile() {
    print_header "Detecting Deployment Profile"
    
    if [ -z "$DEPLOYMENT_PROFILE" ]; then
        print_error "DEPLOYMENT_PROFILE not set in .env"
        echo ""
        echo "Please set DEPLOYMENT_PROFILE in .env to one of:"
        echo "  - dev      : Single machine development"
        echo "  - stage2   : 2 computers (pre-production)"
        echo "  - prod     : 3 servers (production)"
        exit 1
    fi
    
    case "$DEPLOYMENT_PROFILE" in
        dev)
            COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
            print_success "Profile: Development (Single Machine)"
            ;;
        stage2)
            COMPOSE_FILES="-f docker-compose.yml -f docker-compose.stage2.yml"
            print_success "Profile: Stage2 (2 Computers)"
            ;;
        prod)
            COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
            print_success "Profile: Production (3 Servers)"
            ;;
        *)
            print_error "Invalid DEPLOYMENT_PROFILE: $DEPLOYMENT_PROFILE"
            exit 1
            ;;
    esac
}

# Validate configuration
validate_config() {
    print_header "Validating Configuration"
    
    case "$DEPLOYMENT_PROFILE" in
        stage2)
            if [ -z "$PLC_HOST" ]; then
                print_error "PLC_HOST not set in .env (required for stage2)"
                exit 1
            fi
            print_success "PLC_HOST: $PLC_HOST"
            ;;
        prod)
            if [ -z "$SERVER1_HOST" ] || [ -z "$SERVER2_HOST" ] || [ -z "$SERVER3_HOST" ]; then
                print_error "SERVER*_HOST variables not set in .env (required for prod)"
                exit 1
            fi
            print_success "Server 1: $SERVER1_HOST"
            print_success "Server 2: $SERVER2_HOST"
            print_success "Server 3: $SERVER3_HOST"
            ;;
    esac
    
    # Check JWT secret
    if [ "$JWT_SECRET" == "your-secret-key-change-in-production" ] && [ "$DEPLOYMENT_PROFILE" != "dev" ]; then
        print_error "Please change JWT_SECRET in .env for non-dev deployments"
        exit 1
    fi
}

# Pull images
pull_images() {
    print_header "Pulling Docker Images"
    docker-compose $COMPOSE_FILES pull
    print_success "Images pulled successfully"
}

# Build images
build_images() {
    print_header "Building Custom Images"
    docker-compose $COMPOSE_FILES build
    print_success "Images built successfully"
}

# Start services
start_services() {
    print_header "Starting Services"
    docker-compose $COMPOSE_FILES up -d
    print_success "Services started"
}

# Wait for services
wait_for_services() {
    print_header "Waiting for Services to be Healthy"
    
    local max_wait=120
    local elapsed=0
    
    while [ $elapsed -lt $max_wait ]; do
        local healthy=$(docker-compose $COMPOSE_FILES ps -q | xargs docker inspect --format '{{.State.Health.Status}}' 2>/dev/null | grep -c "healthy" || true)
        local total=$(docker-compose $COMPOSE_FILES ps -q | wc -l)
        
        if [ "$healthy" -eq "$total" ]; then
            print_success "All services are healthy"
            return 0
        fi
        
        echo -ne "\rWaiting... ($elapsed/$max_wait seconds) - $healthy/$total healthy"
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    echo ""
    print_warning "Some services may not be healthy yet"
    return 1
}

# Show status
show_status() {
    print_header "Service Status"
    docker-compose $COMPOSE_FILES ps
}

# Show endpoints
show_endpoints() {
    print_header "Service Endpoints"
    
    case "$DEPLOYMENT_PROFILE" in
        dev)
            echo -e "${GREEN}Frontend:${NC}      http://localhost:3000"
            echo -e "${GREEN}Backend API:${NC}   http://localhost:18080"
            echo -e "${GREEN}AI Service:${NC}    http://localhost:3001"
            echo -e "${GREEN}Simulator:${NC}     http://localhost:5000"
            echo -e "${GREEN}Monitor:${NC}       http://localhost:5002"
            echo -e "${GREEN}Ignition:${NC}      http://localhost:8088"
            ;;
        stage2)
            echo -e "${GREEN}Frontend:${NC}      http://${COMPUTER1_HOST:-localhost}:3000"
            echo -e "${GREEN}Backend API:${NC}   http://${COMPUTER1_HOST:-localhost}:18080"
            echo -e "${GREEN}AI Service:${NC}    http://${COMPUTER1_HOST:-localhost}:3001"
            echo ""
            echo -e "${YELLOW}On PLC (Computer 2):${NC}"
            echo -e "${GREEN}Node-RED:${NC}      http://${PLC_HOST}:1880"
            ;;
        prod)
            echo -e "${GREEN}Frontend:${NC}      http://${SERVER2_HOST}:3000"
            echo -e "${GREEN}Backend API:${NC}   http://${SERVER2_HOST}:18080"
            echo -e "${GREEN}AI Service:${NC}    http://${SERVER2_HOST}:3001"
            echo ""
            echo -e "${YELLOW}Server 1 (PLC):${NC}"
            echo -e "${GREEN}Node-RED:${NC}      http://${SERVER1_HOST}:1880"
            echo -e "${GREEN}Ignition:${NC}      http://${SERVER1_HOST}:8088"
            ;;
    esac
}

# Show logs
show_logs() {
    print_header "Recent Logs (Ctrl+C to exit)"
    docker-compose $COMPOSE_FILES logs -f --tail=50
}

# Main menu
show_menu() {
    echo ""
    print_header "VirtPLC Management Menu"
    echo "1) Start services"
    echo "2) Stop services"
    echo "3) Restart services"
    echo "4) Show status"
    echo "5) Show logs"
    echo "6) Show endpoints"
    echo "7) Update images"
    echo "8) Clean up"
    echo "9) Exit"
    echo ""
}

# Parse command line arguments
ACTION="${1:-menu}"

# Main execution
main() {
    check_prerequisites
    load_environment
    detect_profile
    validate_config
    
    case "$ACTION" in
        start|up)
            pull_images
            build_images
            start_services
            wait_for_services
            show_status
            show_endpoints
            ;;
        stop|down)
            print_header "Stopping Services"
            docker-compose $COMPOSE_FILES down
            print_success "Services stopped"
            ;;
        restart)
            print_header "Restarting Services"
            docker-compose $COMPOSE_FILES restart
            print_success "Services restarted"
            wait_for_services
            show_status
            ;;
        status|ps)
            show_status
            ;;
        logs)
            show_logs
            ;;
        endpoints|urls)
            show_endpoints
            ;;
        update|pull)
            pull_images
            build_images
            print_info "Images updated. Run './start.sh restart' to apply changes"
            ;;
        clean|cleanup)
            print_warning "This will remove all containers, networks, and volumes"
            read -p "Are you sure? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker-compose $COMPOSE_FILES down -v
                print_success "Cleanup complete"
            fi
            ;;
        menu)
            while true; do
                show_menu
                read -p "Select option: " choice
                case "$choice" in
                    1) ACTION="start"; main ;;
                    2) ACTION="stop"; main ;;
                    3) ACTION="restart"; main ;;
                    4) ACTION="status"; main ;;
                    5) ACTION="logs"; main ;;
                    6) ACTION="endpoints"; main ;;
                    7) ACTION="update"; main ;;
                    8) ACTION="clean"; main ;;
                    9) exit 0 ;;
                    *) print_error "Invalid option" ;;
                esac
            done
            ;;
        help|--help|-h)
            echo "VirtPLC Deployment Script"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start, up      - Pull, build, and start services"
            echo "  stop, down     - Stop services"
            echo "  restart        - Restart services"
            echo "  status, ps     - Show service status"
            echo "  logs           - Show service logs"
            echo "  endpoints, urls - Show service endpoints"
            echo "  update, pull   - Update Docker images"
            echo "  clean, cleanup - Remove all containers and volumes"
            echo "  menu           - Show interactive menu (default)"
            echo "  help           - Show this help"
            echo ""
            ;;
        *)
            print_error "Unknown command: $ACTION"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main
main
