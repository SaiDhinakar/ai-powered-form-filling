#!/bin/bash

# Startup script for AI-Powered Form Filling backend with Celery worker

set -e

echo "🚀 Starting AI-Powered Form Filling Backend..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start services (MinIO and Redis)
echo "📦 Starting MinIO and Redis services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 3

# Check if Redis is ready
if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "⚠️  Redis is not responding, but continuing..."
fi

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "📦 Installing dependencies..."
    uv sync
fi

# Create necessary directories
mkdir -p chroma_db
mkdir -p minio
mkdir -p redis-data

echo ""
echo "✅ All services started!"
echo ""
echo "🌐 Services running:"
echo "   - MinIO API: http://localhost:9000"
echo "   - MinIO Console: http://localhost:9001"
echo "   - Redis: localhost:6379"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Start FastAPI server (in this terminal):"
echo "   uv run python -m fastapi dev main.py"
echo ""
echo "2. Start Celery worker (in a new terminal):"
echo "   cd $(pwd)"
echo "   celery -A src.tasks worker --loglevel=info"
echo ""
echo "3. Access API documentation:"
echo "   http://127.0.0.1:8000/docs"
echo ""
