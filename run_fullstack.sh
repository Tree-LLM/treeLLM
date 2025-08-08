#!/bin/bash

# TreeLLM Full Stack Runner
# This script starts both backend and frontend servers

echo "Starting TreeLLM Full Stack Application..."
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js.${NC}"
    exit 1
fi

# Function to kill processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up trap to call cleanup on script exit
trap cleanup EXIT INT TERM

# Start Backend Server
echo -e "${GREEN}Starting TreeLLM Backend Server...${NC}"
cd /Users/kimminjun/Desktop/TreeLLM

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating template...${NC}"
    echo "OPENAI_API_KEY=your-api-key-here" > .env
    echo "PORT=5001" >> .env
    echo -e "${RED}Please add your OpenAI API key to the .env file${NC}"
fi

# Start backend in background
python3 app.py &
BACKEND_PID=$!
echo -e "${GREEN}Backend started with PID: $BACKEND_PID${NC}"

# Wait for backend to start
echo "Waiting for backend to be ready..."
sleep 5

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Backend failed to start. Check the logs above.${NC}"
    exit 1
fi

# Start Frontend Server
echo -e "${GREEN}Starting TreeLLM Frontend Server...${NC}"
cd /Users/kimminjun/Desktop/TreeLLM/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend started with PID: $FRONTEND_PID${NC}"

# Display access information
echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}TreeLLM is running!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "Frontend: ${YELLOW}http://localhost:5173${NC}"
echo -e "Backend API: ${YELLOW}http://localhost:5001${NC}"
echo -e "\nPress ${YELLOW}Ctrl+C${NC} to stop both servers"
echo -e "${GREEN}=========================================${NC}\n"

# Keep script running
while true; do
    sleep 1
done