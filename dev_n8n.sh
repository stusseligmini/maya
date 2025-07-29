#!/bin/bash
# Start Maya AI with n8n integration for development

# Set environment variables
export MAYA_ENV="development"
export N8N_WEBHOOK_SECRET="dev-webhook-secret"

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Starting Maya AI with n8n Integration ===${NC}"

# Check if n8n is installed
if ! command -v n8n &> /dev/null; then
    echo -e "${YELLOW}n8n is not installed. Installing now...${NC}"
    npm install -g n8n
fi

# Check if docker is running and start required services
if command -v docker &> /dev/null; then
    if ! docker ps &> /dev/null; then
        echo -e "${YELLOW}Docker is not running. Please start Docker first.${NC}"
    else
        echo -e "${GREEN}Starting required services with Docker...${NC}"
        docker-compose -f docker-compose.dev.yml up -d postgres redis
    fi
fi

# Create a temporary directory for n8n
mkdir -p .tmp/n8n

# Start n8n in the background
echo -e "${GREEN}Starting n8n...${NC}"
N8N_PORT=5678 \
N8N_EDITOR_BASE_URL=http://localhost:5678 \
N8N_USER_FOLDER=.tmp/n8n \
n8n start > .tmp/n8n-output.log 2>&1 &
N8N_PID=$!

# Wait for n8n to start
echo -e "${YELLOW}Waiting for n8n to start...${NC}"
sleep 10

# Start Maya API in development mode
echo -e "${GREEN}Starting Maya API...${NC}"
uvicorn main:app --reload --port 8000 &
MAYA_PID=$!

echo -e "${BLUE}=== Services Started ===${NC}"
echo -e "Maya API: ${GREEN}http://localhost:8000${NC}"
echo -e "n8n:      ${GREEN}http://localhost:5678${NC}"

# Register Maya nodes in n8n
echo -e "${YELLOW}Registering Maya nodes in n8n...${NC}"
python -m maya.cli n8n register

echo -e "${GREEN}Maya AI with n8n integration is ready!${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Trap Ctrl+C and stop services
trap "echo -e '${RED}Stopping services...${NC}'; kill $MAYA_PID; kill $N8N_PID; echo -e '${GREEN}All services stopped${NC}'" INT

# Wait for Ctrl+C
wait
