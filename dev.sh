#!/bin/bash

# NetDash Development Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}NetDash Development Helper${NC}"
echo "================================"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists docker; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${YELLOW}Warning: Node.js is not installed (required for local frontend development)${NC}"
fi

if ! command_exists python3; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Menu
echo "What would you like to do?"
echo "1) Start full stack with Docker"
echo "2) Stop Docker containers"
echo "3) View logs"
echo "4) Setup local backend development"
echo "5) Setup local frontend development"
echo "6) Clean Docker volumes"
echo "7) Rebuild Docker images"
echo "8) Run tests"
echo "9) Exit"
echo ""
read -p "Enter your choice [1-9]: " choice

case $choice in
    1)
        echo -e "${GREEN}Starting NetDash with Docker Compose...${NC}"
        docker compose up -d
        echo ""
        echo -e "${GREEN}NetDash is running!${NC}"
        echo "Frontend: http://localhost:3000"
        echo "Backend API: http://localhost:5000"
        echo ""
        echo "Use 'docker compose logs -f' to view logs"
        ;;
    2)
        echo -e "${YELLOW}Stopping Docker containers...${NC}"
        docker compose down
        echo -e "${GREEN}✓ Containers stopped${NC}"
        ;;
    3)
        docker compose logs -f
        ;;
    4)
        echo -e "${GREEN}Setting up local backend development...${NC}"
        cd backend
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt
        if [ ! -f ".env" ]; then
            cp .env.example .env
            echo -e "${YELLOW}Created .env file. Please update with your settings.${NC}"
        fi
        echo -e "${GREEN}✓ Backend setup complete${NC}"
        echo "To start the backend:"
        echo "  cd backend"
        echo "  source venv/bin/activate"
        echo "  python app.py"
        ;;
    5)
        echo -e "${GREEN}Setting up local frontend development...${NC}"
        cd frontend
        npm install
        echo -e "${GREEN}✓ Frontend setup complete${NC}"
        echo "To start the frontend:"
        echo "  cd frontend"
        echo "  npm run dev"
        ;;
    6)
        echo -e "${YELLOW}Cleaning Docker volumes...${NC}"
        docker compose down -v
        echo -e "${GREEN}✓ Volumes cleaned${NC}"
        ;;
    7)
        echo -e "${YELLOW}Rebuilding Docker images...${NC}"
        docker compose build --no-cache
        echo -e "${GREEN}✓ Images rebuilt${NC}"
        ;;
    8)
        echo -e "${GREEN}Running tests...${NC}"
        echo -e "${YELLOW}Note: Test implementation is pending${NC}"
        ;;
    9)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
