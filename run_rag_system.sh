#!/bin/bash

# RAG System Runner Script
# This script sets up and runs the complete RAG system

set -e

echo "🚀 Starting RAG System Setup..."

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

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    print_warning ".env file not found in backend directory"
    print_status "Creating .env file from example..."
    cp backend/.env.example backend/.env
    print_warning "Please edit backend/.env with your configuration before continuing"
    print_warning "Required variables:"
    print_warning "  - DATABASE_URL"
    print_warning "  - OPENAI_API_KEY (or OLLAMA_BASE_URL)"
    read -p "Press Enter after editing .env file..."
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi

print_status "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
print_success "Backend dependencies installed"

print_status "Setting up database..."
python setup_database.py setup
print_success "Database setup completed"

print_status "Installing frontend dependencies..."
cd ../frontend
npm install
print_success "Frontend dependencies installed"

cd ..

print_success "Setup completed successfully!"
echo ""
print_status "To run the system:"
echo ""
print_status "Terminal 1 - Backend:"
echo "  cd backend"
echo "  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
print_status "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
print_status "Then open http://localhost:5173 in your browser"
echo ""
print_status "API Documentation will be available at:"
echo "  http://localhost:8000/docs"
echo ""
print_status "Health check:"
echo "  http://localhost:8000/api/rag/health"
echo ""

# Ask if user wants to start the services now
read -p "Do you want to start the services now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting services..."
    
    # Start backend in background
    print_status "Starting backend server..."
    cd backend
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Start frontend in background
    print_status "Starting frontend server..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    print_success "Services started!"
    print_status "Backend PID: $BACKEND_PID"
    print_status "Frontend PID: $FRONTEND_PID"
    echo ""
    print_status "Access the application at:"
    print_status "  Frontend: http://localhost:5173"
    print_status "  Backend API: http://localhost:8000"
    print_status "  API Docs: http://localhost:8000/docs"
    echo ""
    print_status "Press Ctrl+C to stop all services"
    
    # Wait for user to stop
    trap "echo ''; print_status 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; print_success 'Services stopped'; exit 0" INT
    wait
else
    print_status "Setup completed. You can start the services manually when ready."
fi