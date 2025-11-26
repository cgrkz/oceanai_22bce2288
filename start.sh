#!/bin/bash
# Startup script for QA Agent (Linux/Mac)

echo "🚀 Starting QA Agent - Test Case & Script Generator"
echo "=================================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env file and add your AWS credentials:"
    echo "   - AWS_ACCESS_KEY_ID"
    echo "   - AWS_SECRET_ACCESS_KEY"
    echo "   - AWS_REGION"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    echo "📁 Creating logs directory..."
    mkdir logs
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "=================================================="
echo "Starting services..."
echo "=================================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "🔷 Starting FastAPI Backend on http://localhost:8000"
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 3
echo "   ✓ Backend started (PID: $BACKEND_PID)"
echo "   📚 API Docs: http://localhost:8000/docs"
echo ""

# Start frontend
echo "🔶 Starting Streamlit Frontend on http://localhost:8501"
streamlit run frontend/streamlit_app.py > logs/frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 2
echo "   ✓ Frontend started (PID: $FRONTEND_PID)"
echo ""

echo "=================================================="
echo "✅ QA Agent is now running!"
echo "=================================================="
echo ""
echo "🌐 Access the application:"
echo "   Streamlit UI:  http://localhost:8501"
echo "   FastAPI Docs:  http://localhost:8000/docs"
echo "   Health Check:  http://localhost:8000/health"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo "   App:      tail -f logs/app.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=================================================="

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
