# Quick Start Guide

Get the Factory Dynamics Simulation running in 5 minutes.

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed ([Download](https://www.python.org/downloads/))
- **Node.js 18+** and **npm** installed ([Download](https://nodejs.org/))
- **Git** installed ([Download](https://git-scm.com/downloads))

Check your versions:
```bash
python3 --version  # Should be 3.11 or higher
node --version     # Should be v18 or higher
npm --version      # Should be 9 or higher
```

---

## Step 1: Install Node.js (if not installed)

### macOS
```bash
# Using Homebrew
brew install node

# Or download from https://nodejs.org/
```

### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm

# Or use nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

### Windows
Download and install from [nodejs.org](https://nodejs.org/)

---

## Step 2: Set Up the Backend

Open a terminal and navigate to the backend directory:

```bash
cd factory-simulation/backend
```

Create a Python virtual environment:
```bash
python3 -m venv venv
```

Activate the virtual environment:
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Start the backend server:
```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Keep this terminal open** and proceed to Step 3 in a new terminal.

---

## Step 3: Set Up the Frontend

Open a **new terminal** and navigate to the frontend directory:

```bash
cd factory-simulation/frontend
```

Install Node.js dependencies:
```bash
npm install
```

This will take 1–2 minutes to download all packages.

Start the frontend development server:
```bash
npm run dev
```

You should see:
```
  VITE v5.2.0  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

---

## Step 4: Open the Application

Open your web browser and navigate to:

```
http://localhost:3000
```

You should see the **Factory Dynamics Simulation** interface with:
- A configuration panel on the left
- A concept explainer in the center
- "Run Simulation" and "Reset" buttons

---

## Step 5: Run Your First Simulation

1. **Review the default configuration** (already filled in):
   - 4 tools
   - 3 products
   - Arrival rate: 0.8 lots/time unit
   - Dispatching rule: FIFO

2. **Click "Run Simulation"**

3. **Wait 2–5 seconds** for the simulation to complete

4. **View the results**:
   - Toolset WIP Over Time (line chart)
   - Cumulative Total Moves (line chart)
   - Total Accumulated Queue Time (line chart)
   - Average Tool Utilisation Over Time (line chart)
   - Summary statistics (mean queue time, mean cycle time, etc.)

---

## Step 6: Experiment with Different Configurations

Try changing:

### Dispatching Rules
- **FIFO**: First-In-First-Out (baseline)
- **LEAST LOADED TOOL**: Spreads work across tools
- **RANDOM QUALIFIED TOOL**: Introduces stochasticity
- **OPTIMISED SPT**: Shortest Processing Time first

**Observation**: SPT typically reduces mean queue time by 20–40% compared to FIFO.

### Cross-Qualification Matrix
- **Uncheck some boxes** to restrict which tools can run which products
- **Observation**: Restricted qualification increases WIP and queue time

### Arrival Rate
- **Increase to 1.5** (high load)
- **Observation**: WIP grows unbounded if arrival rate > processing capacity

### Processing Times
- **Make Product 0 very fast (1.0)** and Product 2 very slow (10.0)
- **Observation**: SPT heavily favors Product 0, potentially starving Product 2

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`  
**Solution**: Make sure you activated the virtual environment and ran `pip install -r requirements.txt`

**Problem**: `Address already in use` (port 8000)  
**Solution**: Another process is using port 8000. Kill it or use a different port:
```bash
uvicorn main:app --reload --port 8001
```
Then update `frontend/vite.config.ts` to proxy to port 8001.

**Problem**: `ImportError: cannot import name 'app' from 'main'`  
**Solution**: Make sure you're in the `backend/` directory when running uvicorn.

### Frontend Issues

**Problem**: `command not found: npm`  
**Solution**: Node.js is not installed. See Step 1.

**Problem**: `ENOENT: no such file or directory, open 'package.json'`  
**Solution**: Make sure you're in the `frontend/` directory.

**Problem**: Frontend loads but shows "Failed to load scenario"  
**Solution**: Backend is not running. Start the backend (Step 2) before the frontend.

**Problem**: Charts not rendering  
**Solution**: Check browser console for errors. Make sure Recharts installed correctly (`npm install`).

### Browser Issues

**Problem**: Page shows "Cannot GET /api/scenario"  
**Solution**: Backend is not running or not accessible. Check that `http://localhost:8000/health` returns `{"status":"ok"}`.

**Problem**: CORS errors in browser console  
**Solution**: Make sure backend is running on port 8000 and frontend on port 3000. The Vite proxy should handle CORS automatically.

---

## Next Steps

- **Read the full README**: `README.md` for architecture details
- **Explore the code**: Start with `backend/simulation/engine.py` and `frontend/src/App.tsx`
- **Add a new dispatching strategy**: See `ARCHITECTURE.md` → Extension Patterns
- **Deploy to production**: See `README.md` → Deployment

---

## API Documentation

Once the backend is running, visit:

```
http://localhost:8000/docs
```

This opens the **interactive API documentation** (Swagger UI) where you can:
- View all endpoints
- Test API calls directly from the browser
- See request/response schemas

---

## Stopping the Application

### Stop the Frontend
In the frontend terminal, press `Ctrl+C`

### Stop the Backend
In the backend terminal, press `Ctrl+C`

### Deactivate Python Virtual Environment
```bash
deactivate
```

---

## Restarting the Application

### Backend
```bash
cd factory-simulation/backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd factory-simulation/frontend
npm run dev
```

---

## Building for Production

### Backend
No build step needed. Deploy the Python code directly.

### Frontend
```bash
cd factory-simulation/frontend
npm run build
```

This creates a `dist/` folder with optimized static files ready for deployment.

---

## Getting Help

- **Check the README**: `README.md`
- **Check the Architecture docs**: `ARCHITECTURE.md`
- **Check the SOW**: `SOW-Factory-Simulation-MVP.pdf`
- **Contact**: Project point of contact (as per SOW-001)

---

**Happy Simulating! 🏭**
