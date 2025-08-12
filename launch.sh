#!/bin/bash

# AgriLink Platform Launch Script
# This script starts the complete AgriLink platform

set -e

echo "🌱 AgriLink Platform - Launching..."
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please ensure Docker Desktop is running."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/storage
mkdir -p nginx/ssl

# Check if containers are already running
if docker compose ps | grep -q "Up"; then
    echo "⚠️  Some containers are already running. Stopping them first..."
    docker compose down
fi

# Start the platform
echo "🚀 Starting AgriLink platform..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check database
if docker compose exec -T db pg_isready -U agrilink_user -d agrilink > /dev/null 2>&1; then
    echo "✅ Database is ready"
else
    echo "❌ Database is not ready. Please check logs: docker compose logs db"
fi

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is ready"
else
    echo "❌ Backend API is not ready. Please check logs: docker-compose logs backend"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is ready"
else
    echo "❌ Frontend is not ready. Please check logs: docker-compose logs frontend"
fi

echo ""
echo "🎉 AgriLink Platform is launching!"
echo ""
echo "📱 Access your platform at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker compose logs -f"
echo "   Stop platform: docker compose down"
echo "   Restart: docker compose restart"
echo ""
echo "🚀 Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Register as a user or log in"
echo "3. For admin access, run: python3 scripts/setup_admin.py"
echo ""
echo "📚 For more information, see README.md"
echo ""

# Check if setup_admin.py exists and offer to run it
if [ -f "scripts/setup_admin.py" ]; then
    echo "🤔 Would you like to set up the admin user now? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "🔧 Setting up admin user..."
        python3 scripts/setup_admin.py
    fi
fi

echo "✨ Launch complete! Happy farming! 🌾"
