#!/bin/bash
# Setup verification script for Factory Dynamics Simulation Engine
# Run this after following QUICKSTART.md to verify everything is working

set -e

echo "=========================================="
echo "Factory Dynamics Simulation - Setup Verification"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -n "Checking Python version... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found"
    exit 1
fi

# Check Node.js
echo -n "Checking Node.js version... "
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js not found"
    echo -e "${YELLOW}Install Node.js from https://nodejs.org/${NC}"
    exit 1
fi

# Check npm
echo -n "Checking npm version... "
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm $NPM_VERSION"
else
    echo -e "${RED}✗${NC} npm not found"
    exit 1
fi

echo ""
echo "=========================================="
echo "Backend Verification"
echo "=========================================="

# Check backend directory
if [ ! -d "backend" ]; then
    echo -e "${RED}✗${NC} backend/ directory not found"
    exit 1
fi

cd backend

# Check virtual environment
echo -n "Checking Python virtual environment... "
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} venv/ exists"
else
    echo -e "${YELLOW}!${NC} venv/ not found - creating..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} venv/ created"
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Check requirements.txt
echo -n "Checking requirements.txt... "
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} requirements.txt exists"
else
    echo -e "${RED}✗${NC} requirements.txt not found"
    exit 1
fi

# Check if dependencies are installed
echo -n "Checking Python dependencies... "
if python3 -c "import fastapi, simpy, pydantic, uvicorn" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} All dependencies installed"
else
    echo -e "${YELLOW}!${NC} Dependencies not installed - installing..."
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
fi

# Check backend files
echo -n "Checking backend structure... "
BACKEND_FILES=(
    "main.py"
    "simulation/engine.py"
    "simulation/scheduling.py"
    "simulation/models.py"
    "scenarios/load_balancing.py"
    "api/routes.py"
    "api/schemas.py"
)

MISSING_FILES=()
for file in "${BACKEND_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All backend files present"
else
    echo -e "${RED}✗${NC} Missing files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

cd ..

echo ""
echo "=========================================="
echo "Frontend Verification"
echo "=========================================="

# Check frontend directory
if [ ! -d "frontend" ]; then
    echo -e "${RED}✗${NC} frontend/ directory not found"
    exit 1
fi

cd frontend

# Check package.json
echo -n "Checking package.json... "
if [ -f "package.json" ]; then
    echo -e "${GREEN}✓${NC} package.json exists"
else
    echo -e "${RED}✗${NC} package.json not found"
    exit 1
fi

# Check if node_modules exists
echo -n "Checking Node.js dependencies... "
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓${NC} node_modules/ exists"
else
    echo -e "${YELLOW}!${NC} node_modules/ not found - installing..."
    npm install --silent
    echo -e "${GREEN}✓${NC} Dependencies installed"
fi

# Check frontend files
echo -n "Checking frontend structure... "
FRONTEND_FILES=(
    "src/App.tsx"
    "src/main.tsx"
    "src/api.ts"
    "src/types.ts"
    "src/components/InputPanel.tsx"
    "src/components/ResultsPanel.tsx"
    "src/components/ConceptExplainer.tsx"
    "vite.config.ts"
    "index.html"
)

MISSING_FILES=()
for file in "${FRONTEND_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All frontend files present"
else
    echo -e "${RED}✗${NC} Missing files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

cd ..

echo ""
echo "=========================================="
echo "Documentation Verification"
echo "=========================================="

DOCS=(
    "README.md"
    "QUICKSTART.md"
    "ARCHITECTURE.md"
    "LICENSE"
    ".gitignore"
)

for doc in "${DOCS[@]}"; do
    echo -n "Checking $doc... "
    if [ -f "$doc" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
done

echo ""
echo "=========================================="
echo "Setup Verification Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload --port 8000"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser to:"
echo "   http://localhost:3000"
echo ""
echo -e "${GREEN}All checks passed!${NC}"
