# Installation Instructions

Complete installation guide for the Factory Dynamics Simulation Engine.

---

## System Requirements

### Minimum Requirements
- **OS**: macOS 10.15+, Ubuntu 20.04+, Windows 10+
- **RAM**: 4 GB
- **Disk Space**: 500 MB
- **Internet**: Required for initial setup (downloading dependencies)

### Software Requirements
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **npm**: 9.0 or higher
- **Git**: 2.0 or higher (optional, for version control)

---

## Installation Steps

### Step 1: Install Python 3.11+

#### macOS
```bash
# Using Homebrew
brew install python@3.11

# Verify installation
python3 --version
```

#### Ubuntu/Debian Linux
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Verify installation
python3 --version
```

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify in Command Prompt:
   ```cmd
   python --version
   ```

---

### Step 2: Install Node.js 18+

#### macOS
```bash
# Using Homebrew
brew install node@18

# Verify installation
node --version
npm --version
```

#### Ubuntu/Debian Linux
```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

#### Windows
1. Download Node.js from [nodejs.org](https://nodejs.org/)
2. Run the installer (includes npm)
3. Verify in Command Prompt:
   ```cmd
   node --version
   npm --version
   ```

---

### Step 3: Set Up the Backend

#### 3.1 Navigate to Backend Directory
```bash
cd factory-simulation/backend
```

#### 3.2 Create Python Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv

# Windows
python -m venv venv
```

#### 3.3 Activate Virtual Environment
```bash
# macOS/Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

#### 3.4 Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI 0.111.0
- Uvicorn 0.29.0
- SimPy 4.1.1
- Pydantic 2.7.1

#### 3.5 Verify Backend Installation
```bash
python3 -c "import fastapi, simpy, pydantic, uvicorn; print('✓ All dependencies installed')"
```

---

### Step 4: Set Up the Frontend

#### 4.1 Navigate to Frontend Directory
```bash
cd ../frontend
# Or from project root: cd factory-simulation/frontend
```

#### 4.2 Install Node.js Dependencies
```bash
npm install
```

This installs:
- React 18.2
- TypeScript 5.2
- Vite 5.2
- Recharts 2.12
- Axios 1.6
- And all dev dependencies

**Note**: This may take 2–3 minutes.

#### 4.3 Verify Frontend Installation
```bash
npm list react recharts axios
```

You should see the installed versions.

---

## Running the Application

### Terminal 1: Start Backend

```bash
cd factory-simulation/backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

**Verify backend is running:**
Open browser to `http://localhost:8000/health`  
Should return: `{"status":"ok"}`

**API Documentation:**
Open browser to `http://localhost:8000/docs`

---

### Terminal 2: Start Frontend

```bash
cd factory-simulation/frontend
npm run dev
```

**Expected output:**
```
  VITE v5.2.0  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**Open application:**
Navigate to `http://localhost:3000` in your browser

---

## Troubleshooting

### Python Issues

#### "python3: command not found"
- **Solution**: Python is not installed or not in PATH
- **macOS/Linux**: Install via package manager (see Step 1)
- **Windows**: Reinstall Python and check "Add to PATH"

#### "No module named 'fastapi'"
- **Solution**: Virtual environment not activated or dependencies not installed
- **Fix**:
  ```bash
  source venv/bin/activate  # Activate venv
  pip install -r requirements.txt  # Install dependencies
  ```

#### "Address already in use" (port 8000)
- **Solution**: Another process is using port 8000
- **Fix**: Use a different port:
  ```bash
  uvicorn main:app --reload --port 8001
  ```
  Then update `frontend/vite.config.ts` proxy target to `http://localhost:8001`

---

### Node.js Issues

#### "npm: command not found"
- **Solution**: Node.js is not installed or not in PATH
- **Fix**: Install Node.js (see Step 2)

#### "Cannot find module 'react'"
- **Solution**: Dependencies not installed
- **Fix**:
  ```bash
  cd frontend
  npm install
  ```

#### "EACCES: permission denied"
- **Solution**: npm permissions issue
- **Fix (macOS/Linux)**:
  ```bash
  sudo chown -R $(whoami) ~/.npm
  npm install
  ```

#### Port 3000 already in use
- **Solution**: Another process is using port 3000
- **Fix**: Vite will automatically try port 3001, 3002, etc.
- **Or specify a port**:
  ```bash
  npm run dev -- --port 3001
  ```

---

### Browser Issues

#### "Failed to load scenario"
- **Cause**: Backend is not running
- **Fix**: Start backend (see Terminal 1 instructions)

#### CORS errors in console
- **Cause**: Backend and frontend on different origins
- **Fix**: Ensure backend is on port 8000 and frontend on port 3000
- **Vite proxy** should handle CORS automatically

#### Charts not rendering
- **Cause**: Recharts not installed or JavaScript error
- **Fix**:
  1. Check browser console for errors
  2. Reinstall frontend dependencies:
     ```bash
     cd frontend
     rm -rf node_modules package-lock.json
     npm install
     ```

#### Blank page
- **Cause**: JavaScript error or build issue
- **Fix**:
  1. Open browser console (F12)
  2. Check for errors
  3. Try clearing browser cache (Ctrl+Shift+R / Cmd+Shift+R)

---

## Verification Checklist

After installation, verify:

- [ ] Backend starts without errors
- [ ] `http://localhost:8000/health` returns `{"status":"ok"}`
- [ ] `http://localhost:8000/docs` shows API documentation
- [ ] Frontend starts without errors
- [ ] `http://localhost:3000` loads the application
- [ ] Configuration panel is visible on the left
- [ ] "Run Simulation" button is clickable
- [ ] Clicking "Run Simulation" shows results with 4 charts
- [ ] All charts render correctly
- [ ] Summary statistics are displayed

---

## Uninstallation

### Remove Backend
```bash
cd factory-simulation/backend
rm -rf venv  # Remove virtual environment
```

### Remove Frontend
```bash
cd factory-simulation/frontend
rm -rf node_modules  # Remove dependencies
```

### Remove Entire Project
```bash
cd ..
rm -rf factory-simulation
```

---

## Environment Variables (Optional)

### Backend

Create `backend/.env` (optional):
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend

Create `frontend/.env` (optional):
```env
# Backend API URL
VITE_API_BASE=http://localhost:8000
```

---

## Building for Production

### Backend
No build step needed. Deploy Python code directly with:
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Frontend
```bash
cd frontend
npm run build
```

Output: `frontend/dist/` (static files ready for deployment)

Serve with any static file server:
```bash
npm run preview  # Preview production build locally
```

---

## Docker Installation (Alternative)

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t factory-sim-backend .
docker run -p 8000:8000 factory-sim-backend
```

### Frontend Dockerfile
```dockerfile
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json .
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t factory-sim-frontend .
docker run -p 3000:80 factory-sim-frontend
```

---

## Getting Help

- **Quick Start**: See `QUICKSTART.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Full Documentation**: See `README.md`
- **Issues**: Check browser console and terminal output for error messages

---

**Installation complete! Proceed to QUICKSTART.md to run your first simulation.**
