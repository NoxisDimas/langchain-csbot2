#!/bin/bash

# RAG System Starter Script
# Quick start script for the RAG system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    print_warning ".env file not found!"
    print_status "Please run setup first: ./run_rag_system.sh"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    cd backend
    
    # Check if backend is already running
    if check_port 8000; then
        print_warning "Backend is already running on port 8000"
        return
    fi
    
    # Start backend in background
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    cd ..
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    for i in {1..30}; do
        if check_port 8000; then
            print_success "Backend started successfully (PID: $BACKEND_PID)"
            return
        fi
        sleep 1
    done
    
    print_error "Backend failed to start"
    exit 1
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    cd frontend
    
    # Check if frontend is already running
    if check_port 5173; then
        print_warning "Frontend is already running on port 5173"
        return
    fi
    
    # Start frontend in background
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    cd ..
    
    # Wait for frontend to start
    print_status "Waiting for frontend to start..."
    for i in {1..30}; do
        if check_port 5173; then
            print_success "Frontend started successfully (PID: $FRONTEND_PID)"
            return
        fi
        sleep 1
    done
    
    print_error "Frontend failed to start"
    exit 1
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    # Stop backend
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_status "Backend stopped (PID: $BACKEND_PID)"
        fi
        rm -f backend.pid
    fi
    
    # Stop frontend
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_status "Frontend stopped (PID: $FRONTEND_PID)"
        fi
        rm -f frontend.pid
    fi
    
    print_success "All services stopped"
}

# Function to show status
show_status() {
    print_status "Service Status:"
    
    if check_port 8000; then
        print_success "Backend: Running on port 8000"
    else
        print_error "Backend: Not running"
    fi
    
    if check_port 5173; then
        print_success "Frontend: Running on port 5173"
    else
        print_error "Frontend: Not running"
    fi
    
    echo ""
    print_status "Access URLs:"
    print_status "  Frontend: http://localhost:5173"
    print_status "  Backend API: http://localhost:8000"
    print_status "  API Docs: http://localhost:8000/docs"
    print_status "  Health Check: http://localhost:8000/api/rag/health"
}

# Function to show logs
show_logs() {
    local service=$1
    
    case $service in
        "backend")
            if [ -f "backend.log" ]; then
                tail -f backend.log
            else
                print_error "Backend log file not found"
            fi
            ;;
        "frontend")
            if [ -f "frontend.log" ]; then
                tail -f frontend.log
            else
                print_error "Frontend log file not found"
            fi
            ;;
        *)
            print_error "Invalid service. Use 'backend' or 'frontend'"
            ;;
    esac
}

# Function to run tests
run_tests() {
    print_status "Running RAG system tests..."
    cd backend
    python test_rag_system.py
    cd ..
}

# Main script logic
case "${1:-start}" in
    "start")
        print_status "Starting RAG System..."
        start_backend
        start_frontend
        
        echo ""
        print_success "RAG System started successfully!"
        show_status
        
        echo ""
        print_status "Press Ctrl+C to stop all services"
        
        # Wait for user to stop
        trap stop_services INT
        wait
        ;;
    
    "stop")
        stop_services
        ;;
    
    "restart")
        stop_services
        sleep 2
        $0 start
        ;;
    
    "status")
        show_status
        ;;
    
    "logs")
        show_logs "${2:-backend}"
        ;;
    
    "test")
        run_tests
        ;;
    
    "health")
        print_status "Checking system health..."
        if check_port 8000; then
            response=$(curl -s http://localhost:8000/api/rag/health || echo "{}")
            echo "$response" | python -m json.tool 2>/dev/null || echo "$response"
        else
            print_error "Backend is not running"
        fi
        ;;
    
    *)
        echo "RAG System Starter Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start     - Start all services (default)"
        echo "  stop      - Stop all services"
        echo "  restart   - Restart all services"
        echo "  status    - Show service status"
        echo "  logs      - Show logs (backend|frontend)"
        echo "  test      - Run system tests"
        echo "  health    - Check system health"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 logs backend"
        echo "  $0 test"
        ;;
esac