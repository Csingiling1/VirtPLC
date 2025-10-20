#!/bin/bash

# VirtPLC - Complete Git Workflow Script
# Pushes all feature branches, merges to develop, and pushes develop

set -e  # Exit on error

echo "🚀 VirtPLC Complete Git Workflow"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Get current directory
REPO_DIR=$(pwd)
echo "Repository: $REPO_DIR"
echo ""

# ========================================
# STEP 1: Commit and Push feature/Web
# ========================================
print_step "STEP 1: Committing and pushing feature/Web branch"

if git rev-parse --verify feature/Web > /dev/null 2>&1; then
    git checkout feature/Web
    
    # Check if there are changes to commit
    if [[ -n $(git status -s) ]]; then
        git add .
        git commit -m "feat(web): Complete Spring Boot backend and React frontend

- Spring Boot 3.2 backend with Eclipse Milo OPC-UA server
- JWT authentication and security
- REST API for sensor data access
- React 18 + TypeScript + Vite frontend
- Live metrics dashboard with Recharts
- HMI iframe embed page
- Dockerfiles for both services"
        print_success "Committed feature/Web"
    else
        print_warning "No changes to commit on feature/Web"
    fi
    
    git push origin feature/Web
    print_success "Pushed feature/Web to remote"
else
    print_warning "feature/Web branch not found, skipping"
fi

echo ""

# ========================================
# STEP 2: Commit and Push feature/AI
# ========================================
print_step "STEP 2: Committing and pushing feature/AI branch"

if git rev-parse --verify feature/AI > /dev/null 2>&1; then
    git checkout feature/AI
    
    # Check if there are changes to commit
    if [[ -n $(git status -s) ]]; then
        git add .
        git commit -m "feat(ai): Complete AI analysis service with Ollama Llama3

- Node.js Express REST API server
- Ollama integration with Llama3 8B model
- WebSocket server for real-time streaming
- Predictive maintenance algorithms
- Anomaly detection with threshold checks
- Rule-based fallback when AI unavailable
- Docker containerization with Ollama service"
        print_success "Committed feature/AI"
    else
        print_warning "No changes to commit on feature/AI"
    fi
    
    git push origin feature/AI
    print_success "Pushed feature/AI to remote"
else
    print_warning "feature/AI branch not found, skipping"
fi

echo ""

# ========================================
# STEP 3: Switch to develop and add Docker Compose
# ========================================
print_step "STEP 3: Switching to develop and committing infrastructure"

git checkout develop

# Check if there are changes to commit
if [[ -n $(git status -s) ]]; then
    git add docker-compose.yml docker-compose.prod.yml docker-compose.dev.yml .env.example .github/ MAIN_README.md DEPLOYMENT_GUIDE.md OLLAMA_SETUP.md
    git commit -m "feat(infra): Add Docker Compose with Ollama and CI/CD

- Complete docker-compose with backend/frontend/AI/Ollama services
- Ollama service running Llama3 8B for AI analysis
- Development configuration with hot reload
- Production configuration with resource limits
- GitHub Actions CI/CD pipeline (build/test/integration/deploy)
- Security scanning workflow with Trivy
- Comprehensive project documentation
- Ollama setup guide"
    print_success "Committed infrastructure to develop"
else
    print_warning "No changes to commit on develop"
fi

echo ""

# ========================================
# STEP 4: Merge all feature branches into develop
# ========================================
print_step "STEP 4: Merging all feature branches into develop"

# Merge feature/UEBlender
if git rev-parse --verify feature/UEBlender > /dev/null 2>&1; then
    print_step "Merging feature/UEBlender..."
    git merge feature/UEBlender --no-ff -m "Merge feature/UEBlender into develop

- Unreal Engine 5 project structure
- Blender asset directories
- OPC-UA C++ plugin
- CMake build system"
    print_success "Merged feature/UEBlender"
else
    print_warning "feature/UEBlender not found, skipping"
fi

# Merge feature/HMI
if git rev-parse --verify feature/HMI > /dev/null 2>&1; then
    print_step "Merging feature/HMI..."
    git merge feature/HMI --no-ff -m "Merge feature/HMI into develop

- Ignition Edge configuration
- OPC-UA tag definitions
- TimeBase DB integration
- PLC logic examples"
    print_success "Merged feature/HMI"
else
    print_warning "feature/HMI not found, skipping"
fi

# Merge feature/Web
if git rev-parse --verify feature/Web > /dev/null 2>&1; then
    print_step "Merging feature/Web..."
    git merge feature/Web --no-ff -m "Merge feature/Web into develop

- Spring Boot backend with OPC-UA
- React TypeScript frontend
- JWT authentication
- Live metrics dashboard"
    print_success "Merged feature/Web"
else
    print_warning "feature/Web not found, skipping"
fi

# Merge feature/AI
if git rev-parse --verify feature/AI > /dev/null 2>&1; then
    print_step "Merging feature/AI..."
    git merge feature/AI --no-ff -m "Merge feature/AI into develop

- Node.js AI analysis service
- Ollama Llama3 integration
- WebSocket real-time streaming
- Predictive maintenance"
    print_success "Merged feature/AI"
else
    print_warning "feature/AI not found, skipping"
fi

echo ""

# ========================================
# STEP 5: Push develop to remote
# ========================================
print_step "STEP 5: Pushing develop branch to remote"

git push origin develop
print_success "Pushed develop to remote"

echo ""
echo "=================================="
echo -e "${GREEN}✅ ALL DONE! Complete workflow executed successfully!${NC}"
echo "=================================="
echo ""
echo "📊 Summary:"
echo "  ✅ feature/Web - committed and pushed"
echo "  ✅ feature/AI - committed and pushed"
echo "  ✅ develop - infrastructure committed"
echo "  ✅ All feature branches merged to develop"
echo "  ✅ develop pushed to remote"
echo ""
echo "🎉 VirtPLC project is ready for deployment!"
echo ""
echo "Next steps:"
echo "  1. Pull the latest develop on production server"
echo "  2. Run: docker-compose up -d"
echo "  3. Run: docker exec -it virtplc-ollama ollama pull llama3:8b"
echo "  4. Access at http://localhost:3000"
echo ""
print_warning "NOTE: Release branch was NOT touched (as requested)"
