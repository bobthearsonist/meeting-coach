#!/bin/bash

# Teams Meeting Coach - Development Startup Script
# This script starts both backend and frontend in the correct order

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Teams Meeting Coach - Development Startup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if backend dependencies are installed
if [ ! -d "backend/venv" ]; then
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

echo -e "${GREEN}✅ Starting backend WebSocket server...${NC}"
echo -e "${YELLOW}💡 Backend will run on ws://localhost:3001${NC}"
echo ""

# Start backend in background
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to start (5 seconds)...${NC}"
sleep 5

# Check if backend is running
if ! ps -p $BACKEND_PID > /dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend is running (PID: $BACKEND_PID)${NC}"
echo ""
echo -e "${GREEN}🚀 Starting frontend...${NC}"
echo -e "${YELLOW}💡 Metro bundler will start in a new terminal${NC}"
echo -e "${YELLOW}💡 React Native app will launch automatically${NC}"
echo ""

# Start frontend
cd frontend
npm start &
METRO_PID=$!
cd ..

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✅ Development environment started!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Backend PID: ${BACKEND_PID}${NC}"
echo -e "${YELLOW}Metro PID: ${METRO_PID}${NC}"
echo ""
echo -e "${YELLOW}To stop all services:${NC}"
echo -e "${YELLOW}  kill $BACKEND_PID $METRO_PID${NC}"
echo ""
echo -e "${YELLOW}Or press Ctrl+C in each terminal${NC}"
echo ""

# Keep script running to catch Ctrl+C
trap "echo ''; echo -e '${YELLOW}💡 Stopping services...${NC}'; kill $BACKEND_PID $METRO_PID 2>/dev/null; exit" INT

wait
