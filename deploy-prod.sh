#!/bin/bash

# AgriLink Production Deployment Script
# This script deploys the AgriLink platform to production

set -e  # Exit on any error

echo "🚀 Starting AgriLink Production Deployment..."

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

# Check if Docker is running
check_docker() {
    print_status "Checking Docker status..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! docker compose version > /dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Create production environment file
setup_environment() {
    print_status "Setting up production environment..."
    
    if [ ! -f .env.prod ]; then
        cat > .env.prod << EOF
# Production Environment Variables
DB_PASSWORD=your_secure_db_password_here
SECRET_KEY=your_super_secret_key_here
PSP_MOCK_SECRET=your_psp_secret_here
NEXT_PUBLIC_API_BASE=https://your-domain.com
ENVIRONMENT=production
EOF
        print_warning "Created .env.prod file. Please edit it with your production values."
        print_warning "Press Enter when you've updated the environment variables..."
        read -r
    else
        print_success "Production environment file already exists"
    fi
}

# Create SSL certificates directory
setup_ssl() {
    print_status "Setting up SSL certificates..."
    
    mkdir -p nginx/ssl
    mkdir -p nginx/logs
    
    if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
        print_warning "SSL certificates not found in nginx/ssl/"
        print_warning "Please add your SSL certificates:"
        print_warning "  - nginx/ssl/cert.pem (SSL certificate)"
        print_warning "  - nginx/ssl/key.pem (Private key)"
        print_warning "Press Enter when you've added the SSL certificates..."
        read -r
    else
        print_success "SSL certificates found"
    fi
}

# Create monitoring configuration
setup_monitoring() {
    print_status "Setting up monitoring configuration..."
    
    mkdir -p monitoring
    
    if [ ! -f monitoring/prometheus.yml ]; then
        cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'agrilink-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'agrilink-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'
EOF
        print_success "Created Prometheus configuration"
    fi
}

# Stop existing services
stop_services() {
    print_status "Stopping existing services..."
    docker compose -f docker-compose.prod.yml down --remove-orphans || true
    print_success "Existing services stopped"
}

# Build and start services
deploy_services() {
    print_status "Building and starting production services..."
    
    # Load environment variables
    if [ -f .env.prod ]; then
        export $(cat .env.prod | grep -v '^#' | xargs)
    fi
    
    # Build and start services
    docker compose -f docker-compose.prod.yml up -d --build
    
    print_success "Production services started"
}

# Wait for services to be healthy
wait_for_health() {
    print_status "Waiting for services to be healthy..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Health check attempt $attempt/$max_attempts..."
        
        # Check backend health
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend is healthy"
        else
            print_warning "Backend health check failed, attempt $attempt"
            sleep 10
            ((attempt++))
            continue
        fi
        
        # Check frontend health
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend is healthy"
        else
            print_warning "Frontend health check failed, attempt $attempt"
            sleep 10
            ((attempt++))
            continue
        fi
        
        # Check nginx health
        if curl -f http://localhost/health > /dev/null 2>&1; then
            print_success "Nginx is healthy"
        else
            print_warning "Nginx health check failed, attempt $attempt"
            sleep 10
            ((attempt++))
            continue
        fi
        
        print_success "All services are healthy!"
        break
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "Services failed to become healthy after $max_attempts attempts"
        print_error "Check logs with: docker compose -f docker-compose.prod.yml logs"
        exit 1
    fi
}

# Show deployment status
show_status() {
    print_status "Deployment completed successfully!"
    echo
    echo "🌐 Service URLs:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - Nginx: http://localhost"
    echo "  - Monitoring: http://localhost:9090"
    echo
    echo "📊 Service Status:"
    docker compose -f docker-compose.prod.yml ps
    echo
    echo "📝 Useful Commands:"
    echo "  - View logs: docker compose -f docker-compose.prod.yml logs -f"
    echo "  - Stop services: docker compose -f docker-compose.prod.yml down"
    echo "  - Restart services: docker compose -f docker-compose.prod.yml restart"
    echo "  - Update services: docker compose -f docker-compose.prod.yml up -d --build"
}

# Main deployment flow
main() {
    echo "🌾 AgriLink Production Deployment"
    echo "================================="
    echo
    
    check_docker
    check_docker_compose
    setup_environment
    setup_ssl
    setup_monitoring
    stop_services
    deploy_services
    wait_for_health
    show_status
}

# Run main function
main "$@"
