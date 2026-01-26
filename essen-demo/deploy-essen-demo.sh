#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_machine_type() {
    echo -e "${PURPLE}[MACHINE]${NC} $1"
}

# Function to get local IP address
get_local_ip() {
    # Try multiple methods to get the local IP
    local ip=""

    # Method 1: Use hostname -I (Linux)
    if command -v hostname &> /dev/null; then
        ip=$(hostname -I | awk '{print $1}')
    fi

    # Method 2: Use ip route (Linux)
    if [ -z "$ip" ] && command -v ip &> /dev/null; then
        ip=$(ip route get 8.8.8.8 | awk 'NR==1 {print $7}')
    fi

    # Method 3: Use ifconfig (fallback)
    if [ -z "$ip" ] && command -v ifconfig &> /dev/null; then
        ip=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -1 | awk '{print $2}' | sed 's/addr://')
    fi

    # Method 4: Use hostname command
    if [ -z "$ip" ]; then
        ip=$(hostname -i 2>/dev/null | awk '{print $1}' | grep -v '127.0.0.1' || echo "")
    fi

    echo "$ip"
}

# Function to detect machine type automatically
detect_machine_type() {
    print_status "Attempting to auto-detect machine type..."

    # Check for Windows-specific indicators
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
        return
    fi

    # Check for GPU/CPU intensive tasks (AI PC)
    if command -v nvidia-smi &> /dev/null; then
        print_status "NVIDIA GPU detected - likely AI PC"
        echo "ai"
        return
    fi

    # Check available memory (AI PC typically has more RAM)
    local total_mem=$(free -g | awk 'NR==2{printf "%.0f", $2}' 2>/dev/null || echo "0")
    if [ "$total_mem" -gt 16 ]; then
        print_status "High memory detected (${total_mem}GB) - likely AI PC"
        echo "ai"
        return
    fi

    # Check for gaming/PLC indicators
    if command -v wine &> /dev/null || [ -d "/mnt/c" ]; then
        print_status "Windows compatibility detected - likely PLC machine"
        echo "plc"
        return
    fi

    # Default to AI PC if can't determine
    print_warning "Could not auto-detect machine type, defaulting to AI PC"
    echo "ai"
}

# Function to validate IP address
validate_ip() {
    local ip=$1
    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to get user input with default
get_input() {
    local prompt=$1
    local default=$2
    local input=""

    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        input=${input:-$default}
    else
        read -p "$prompt: " input
    fi

    echo "$input"
}

# Function to create environment file
create_env_file() {
    local machine_type=$1
    local local_ip=$2
    local env_file=".env.${machine_type}"

    print_status "Creating environment file: $env_file"

    cat > "$env_file" << EOF
# VirtPLC Essen Demo Environment Configuration
# Generated on $(date)
# Machine Type: $machine_type
# Local IP: $local_ip

# JWT Secret (change in production)
JWT_SECRET=your-essen-demo-secret-key-change-in-production

# MQTT Configuration
MQTT_USERNAME=virtplc
MQTT_PASSWORD=virtplc123

# Node-RED Secret
NODE_RED_CREDENTIAL_SECRET=your-nodered-secret-key

EOF

    case $machine_type in
        "windows")
            cat >> "$env_file" << EOF
# Windows Machine (PLC Simulator only)
# PLC_IP should be set to the PLC machine's IP
PLC_IP=\${PLC_IP:-192.168.1.100}
HISTORIAN_IP=\${HISTORIAN_IP:-192.168.1.103}
MAIN_IP=\${MAIN_IP:-192.168.1.101}
EOF
            ;;
        "historian")
            cat >> "$env_file" << EOF
# Historian Server (Data Services)
WINDOWS_IP=\${WINDOWS_IP:-192.168.1.102}
MAIN_IP=\${MAIN_IP:-192.168.1.101}
PLC_IP=\${PLC_IP:-192.168.1.100}
HISTORIAN_IP=\$local_ip
EOF
            ;;
        "ai")
            cat >> "$env_file" << EOF
# AI PC (Main Application Server + Go Collector)
WINDOWS_IP=\${WINDOWS_IP:-192.168.1.102}
HISTORIAN_IP=\${HISTORIAN_IP:-192.168.1.103}
PLC_IP=\${PLC_IP:-192.168.1.100}
MAIN_IP=\$local_ip
EOF
            ;;
        "plc")
            cat >> "$env_file" << EOF
# PLC Machine (Ignition + RabbitMQ)
PLC_IP=\$local_ip
HISTORIAN_IP=\${HISTORIAN_IP:-192.168.1.103}
MAIN_IP=\${MAIN_IP:-192.168.1.101}
WINDOWS_IP=\${WINDOWS_IP:-192.168.1.102}
EOF
            ;;
    esac

    print_status "Environment file created: $env_file"
}

# Function to deploy services
deploy_services() {
    local machine_type=$1
    local compose_files=""
    local services=""

    case $machine_type in
        "windows")
            compose_files="docker-compose.simulator.yml"
            services="Python PLC Simulator"
            ;;
        "historian")
            compose_files="docker-compose.data.yml"
            services="TimescaleDB + PostgreSQL"
            ;;
        "ai")
            compose_files="docker-compose.main.yml"
            services="Backend + Frontend + AI Service + Redis + Ollama + Nginx + Go Collector"
            ;;
        "plc")
            compose_files="docker-compose.plc.yml"
            services="Ignition + RabbitMQ + Node-RED"
            ;;
    esac

    print_header "Deploying $services"

    # Load environment variables
    local env_file=".env.${machine_type}"
    if [ -f "$env_file" ]; then
        print_status "Loading environment from $env_file"
        # Copy to .env so docker-compose can pick it up
        cp "$env_file" .env
        set -a
        source "$env_file"
        set +a
    fi

    # Create external networks if needed
    print_status "Ensuring external networks exist..."
    if ! docker network ls | grep -q "virtplc_data_network"; then
        docker network create --driver bridge --subnet=172.21.0.0/16 virtplc_data_network
        print_status "Created virtplc_data_network"
    fi

    if ! docker network ls | grep -q "virtplc_plc_network"; then
        docker network create --driver bridge --subnet=172.20.0.0/16 virtplc_plc_network
        print_status "Created virtplc_plc_network"
    fi

    # Deploy services
    print_status "Starting services with docker-compose..."
    for compose_file in $compose_files; do
        if [ -f "$compose_file" ]; then
            print_status "Starting services from $compose_file..."
            docker-compose -f "$compose_file" up -d
        else
            print_warning "Compose file $compose_file not found, skipping..."
        fi
    done

    # Start Go collector on AI PC
    if [ "$machine_type" = "ai" ]; then
        print_status "Starting Go Collector..."
        if [ -f "../collector/collector" ]; then
            nohup ../collector/collector > collector.log 2>&1 &
            print_status "Go Collector started (PID: $!)"
        else
            print_warning "Go collector binary not found at ../collector/collector"
        fi
    fi

    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    sleep 10

    # Show status
    print_status "Deployment completed!"
    echo ""
    print_status "Service Status:"
    for compose_file in $compose_files; do
        if [ -f "$compose_file" ]; then
            echo "Services from $compose_file:"
            docker-compose -f "$compose_file" ps
            echo ""
        fi
    done

    # Show collector status for AI PC
    if [ "$machine_type" = "ai" ]; then
        echo "Go Collector:"
        if pgrep -f collector > /dev/null; then
            echo "  Status: Running"
        else
            echo "  Status: Not running"
        fi
        echo ""
    fi

    echo ""
    print_status "Useful commands:"
    for compose_file in $compose_files; do
        if [ -f "$compose_file" ]; then
            echo "  For $compose_file:"
            echo "    View logs: docker-compose -f $compose_file logs -f"
            echo "    Stop services: docker-compose -f $compose_file down"
            echo "    Restart services: docker-compose -f $compose_file restart"
            echo ""
        fi
    done

    # Add collector commands for AI PC
    if [ "$machine_type" = "ai" ]; then
        echo "  For Go Collector:"
        echo "    View logs: tail -f collector.log"
        echo "    Stop collector: pkill -f collector"
        echo "    Restart collector: nohup ../collector/collector > collector.log 2>&1 &"
        echo ""
    fi
}

# Function to show network configuration
show_network_config() {
    local machine_type=$1
    local local_ip=$2

    print_header "Network Configuration for $machine_type"

    case $machine_type in
        "windows")
            echo "Local IP (PLC Simulator): $local_ip"
            echo "PLC Machine IP: \${PLC_IP:-192.168.1.100}"
            echo "Historian Server IP: \${HISTORIAN_IP:-192.168.1.103}"
            echo "Main AI PC IP: \${MAIN_IP:-192.168.1.101}"
            echo ""
            echo "Services:"
            echo "  PLC Simulator API: $local_ip:5000"
            echo "  Simulator Monitor: $local_ip:5002"
            ;;
        "historian")
            echo "Local IP (Data Server): $local_ip"
            echo "Windows Machine IP: \${WINDOWS_IP:-192.168.1.102}"
            echo "Main AI PC IP: \${MAIN_IP:-192.168.1.101}"
            echo "PLC Machine IP: \${PLC_IP:-192.168.1.100}"
            echo ""
            echo "Services:"
            echo "  PostgreSQL: $local_ip:15432"
            echo "  TimescaleDB: $local_ip:15433"
            ;;
        "ai")
            echo "Local IP (Main Server): $local_ip"
            echo "Windows Machine IP: \${WINDOWS_IP:-192.168.1.102}"
            echo "Historian Server IP: \${HISTORIAN_IP:-192.168.1.103}"
            echo "PLC Machine IP: \${PLC_IP:-192.168.1.100}"
            echo ""
            echo "Services:"
            echo "  Frontend: $local_ip:3000"
            echo "  Backend API: $local_ip:18080"
            echo "  AI Service: $local_ip:3001"
            echo "  Ollama: $local_ip:11434"
            echo "  Redis: $local_ip:6379"
            echo "  Go Collector: $local_ip (various ports)"
            ;;
        "plc")
            echo "Local IP (PLC Server): $local_ip"
            echo "Historian Server IP: \${HISTORIAN_IP:-192.168.1.103}"
            echo "Main AI PC IP: \${MAIN_IP:-192.168.1.101}"
            echo "Windows Machine IP: \${WINDOWS_IP:-192.168.1.102}"
            echo ""
            echo "Services:"
            echo "  Ignition: $local_ip:8088"
            echo "  RabbitMQ MQTT: $local_ip:1883"
            echo "  RabbitMQ Management: $local_ip:15672"
            echo "  Node-RED: $local_ip:1880"
            ;;
    esac
}

# Main script
main() {
    print_header "VirtPLC Essen Demo Deployment Script"

    # Check prerequisites
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Get local IP
    LOCAL_IP=$(get_local_ip)
    if [ -z "$LOCAL_IP" ]; then
        print_warning "Could not detect local IP address"
        LOCAL_IP=$(get_input "Please enter your local IP address" "192.168.1.100")
    else
        print_status "Detected local IP: $LOCAL_IP"
    fi

    # Machine type selection
    echo ""
    print_header "Machine Type Selection"
    echo "1) Windows Machine (Python PLC Simulator only)"
    echo "2) Historian Server (TimescaleDB + PostgreSQL)"
    echo "3) Main AI PC (Backend, Frontend, AI Service, Redis, Ollama + Go Collector)"
    echo "4) PLC Machine (Ignition, RabbitMQ, Node-RED)"
    echo "5) Auto-detect machine type"
    echo ""

    MACHINE_TYPE=""
    while [ -z "$MACHINE_TYPE" ]; do
        choice=$(get_input "Select machine type (1-5)" "5")

        case $choice in
            1)
                MACHINE_TYPE="windows"
                print_machine_type "Selected: Windows Machine (PLC Simulator only)"
                ;;
            2)
                MACHINE_TYPE="historian"
                print_machine_type "Selected: Historian Server (Data Services)"
                ;;
            3)
                MACHINE_TYPE="ai"
                print_machine_type "Selected: Main AI PC (Full Stack + Go Collector)"
                ;;
            4)
                MACHINE_TYPE="plc"
                print_machine_type "Selected: PLC Machine (Ignition + MQTT)"
                ;;
            5)
                MACHINE_TYPE=$(detect_machine_type)
                print_machine_type "Auto-detected: $MACHINE_TYPE"
                ;;
            *)
                print_error "Invalid choice. Please select 1-5."
                ;;
        esac
    done

    # IP Configuration
    echo ""
    print_header "IP Address Configuration"

    case $MACHINE_TYPE in
        "windows")
            PLC_IP=$(get_input "Enter PLC Machine IP" "192.168.1.100")
            HISTORIAN_IP=$(get_input "Enter Historian Server IP" "192.168.1.103")
            MAIN_IP=$(get_input "Enter Main AI PC IP" "192.168.1.101")
            ;;
        "historian")
            HISTORIAN_IP=$LOCAL_IP
            WINDOWS_IP=$(get_input "Enter Windows Machine IP" "192.168.1.102")
            MAIN_IP=$(get_input "Enter Main AI PC IP" "192.168.1.101")
            PLC_IP=$(get_input "Enter PLC Machine IP" "192.168.1.100")
            ;;
        "ai")
            WINDOWS_IP=$(get_input "Enter Windows Machine IP" "192.168.1.102")
            HISTORIAN_IP=$(get_input "Enter Historian Server IP" "192.168.1.103")
            PLC_IP=$(get_input "Enter PLC Machine IP" "192.168.1.100")
            MAIN_IP=$LOCAL_IP
            ;;
        "plc")
            PLC_IP=$LOCAL_IP
            HISTORIAN_IP=$(get_input "Enter Historian Server IP" "192.168.1.103")
            MAIN_IP=$(get_input "Enter Main AI PC IP" "192.168.1.101")
            WINDOWS_IP=$(get_input "Enter Windows Machine IP" "192.168.1.102")
            ;;
    esac

    # Create environment file
    create_env_file "$MACHINE_TYPE" "$LOCAL_IP"

    # Show network configuration
    show_network_config "$MACHINE_TYPE" "$LOCAL_IP"

    # Confirm deployment
    echo ""
    echo "Ready to deploy services? (y/N): "
    read -n 1 -r REPLY
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled."
        exit 0
    fi

    # Deploy services
    deploy_services "$MACHINE_TYPE"

    # Final instructions
    echo ""
    print_header "Deployment Complete!"
    echo ""
    echo "Deployment Complete! VirtPLC Essen Demo is now running!"
    echo ""
    echo "Access URLs:"
    case $MACHINE_TYPE in
        "windows")
            echo "  PLC Simulator API: http://$LOCAL_IP:5000"
            echo "  Simulator Monitor Dashboard: http://$LOCAL_IP:5002"
            ;;
        "historian")
            echo "  PostgreSQL: $LOCAL_IP:15432 (external access)"
            echo "  TimescaleDB: $LOCAL_IP:15433 (external access)"
            ;;
        "ai")
            echo "  Frontend: http://$LOCAL_IP:3000"
            echo "  Backend API: http://$LOCAL_IP:18080"
            echo "  AI Service: http://$LOCAL_IP:3001"
            echo "  Ollama API: http://$LOCAL_IP:11434"
            echo "  Go Collector: Running locally (check collector.log)"
            ;;
        "plc")
            echo "  Ignition Gateway: http://$LOCAL_IP:8088"
            echo "  RabbitMQ Management: http://$LOCAL_IP:15672"
            echo "  Node-RED: http://$LOCAL_IP:1880"
            ;;
    esac

    echo ""
    echo "Remember to update the IP addresses on other machines!"
    echo "   Environment files are saved as .env.${MACHINE_TYPE}"
    echo ""
    echo "Useful commands:"
    case $MACHINE_TYPE in
        "windows")
            echo "   View simulator logs: docker-compose -f docker-compose.simulator.yml logs -f"
            echo "   Stop simulator: docker-compose -f docker-compose.simulator.yml down"
            echo "   Restart simulator: docker-compose -f docker-compose.simulator.yml restart"
            ;;
        "historian")
            echo "   View data logs: docker-compose -f docker-compose.data.yml logs -f"
            echo "   Stop data services: docker-compose -f docker-compose.data.yml down"
            echo "   Restart data services: docker-compose -f docker-compose.data.yml restart"
            ;;
        "ai")
            echo "   View logs: docker-compose -f docker-compose.main.yml logs -f"
            echo "   Stop all: docker-compose -f docker-compose.main.yml down"
            echo "   Restart all: docker-compose -f docker-compose.main.yml restart"
            echo "   View collector logs: tail -f collector.log"
            echo "   Stop collector: pkill -f collector"
            echo "   Restart collector: nohup ../collector/collector > collector.log 2>&1 &"
            ;;
        "plc")
            echo "   View logs: docker-compose -f docker-compose.plc.yml logs -f"
            echo "   Stop all: docker-compose -f docker-compose.plc.yml down"
            echo "   Restart all: docker-compose -f docker-compose.plc.yml restart"
            ;;
    esac
}

# Run main function
main "$@"