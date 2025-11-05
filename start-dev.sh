#!/bin/bash

# Teams Meeting Coach - Development Startup Script
# This script starts both backend and frontend in the correct order

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults if not in .env
export WEBSOCKET_HOST=${WEBSOCKET_HOST:-localhost}
export WEBSOCKET_PORT=${WEBSOCKET_PORT:-3002}
export METRO_PORT=${METRO_PORT:-8082}

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Teams Meeting Coach - Development Startup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if ports are already in use
if lsof -Pi :${WEBSOCKET_PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port ${WEBSOCKET_PORT} is already in use!${NC}"
    echo -e "${YELLOW}   Run 'lsof -i :${WEBSOCKET_PORT}' to see what's using it${NC}"
    echo -e "${YELLOW}   Or change WEBSOCKET_PORT in .env${NC}"
    exit 1
fi

if lsof -Pi :${METRO_PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port ${METRO_PORT} is already in use!${NC}"
    echo -e "${YELLOW}   Run 'lsof -i :${METRO_PORT}' to see what's using it${NC}"
    echo -e "${YELLOW}   Or change METRO_PORT in .env${NC}"
    exit 1
fi

# Check if backend dependencies are installed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Backend virtual environment not found${NC}"
    echo -e "${YELLOW}   Run: make backend-install${NC}"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not found${NC}"
    echo -e "${YELLOW}   Run: make frontend-install${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Starting Metro bundler first...${NC}"
echo -e "${YELLOW}💡 Metro will run in background on port ${METRO_PORT}${NC}"
echo -e "${YELLOW}💡 Logs: frontend/metro.log${NC}"
echo ""

# Start Metro in background (it's fast and we need it ready)
cd frontend
npm start > metro.log 2>&1 &
METRO_PID=$!
cd ..

# Wait for Metro to be ready by polling its health endpoint
echo -e "${YELLOW}⏳ Waiting for Metro to start...${NC}"
METRO_READY=false
for i in {1..30}; do
    if curl -s "http://localhost:${METRO_PORT}/status" >/dev/null 2>&1; then
        METRO_READY=true
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

if [ "$METRO_READY" = false ]; then
    echo -e "${RED}❌ Metro failed to start after 30 seconds. Check frontend/metro.log${NC}"
    kill $METRO_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ Metro is running (PID: $METRO_PID)${NC}"
echo ""

# Setup cleanup trap BEFORE starting backend
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping services...${NC}"

    # Kill Metro and all its child processes
    if [ ! -z "$METRO_PID" ] && kill -0 $METRO_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping Metro (PID: ${METRO_PID}) and child processes...${NC}"
        # Kill the entire process group
        pkill -P $METRO_PID 2>/dev/null || true
        kill $METRO_PID 2>/dev/null || true
        sleep 1
        # Force kill if still running
        kill -9 $METRO_PID 2>/dev/null || true
    fi

    # Also kill any process still using the Metro port
    if lsof -Pi :${METRO_PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}Cleaning up port ${METRO_PORT}...${NC}"
        lsof -ti:${METRO_PORT} | xargs kill -9 2>/dev/null || true
    fi

    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}
trap cleanup INT TERM EXIT

echo -e "${GREEN}✅ Starting backend WebSocket server...${NC}"
echo -e "${YELLOW}💡 Backend will run on ws://${WEBSOCKET_HOST}:${WEBSOCKET_PORT}${NC}"
echo -e "${YELLOW}💡 Backend runs in FOREGROUND - you'll see its logs below${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop all services${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Start backend in FOREGROUND (blocking) - this keeps the script alive
cd backend
source ../venv/bin/activate
exec python main.py
