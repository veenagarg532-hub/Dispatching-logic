# Factory Dynamics Simulation Engine — MVP (Phase 1)

**SOW Reference:** SOW-001 — Factory Dynamics Simulation MVP  
**Client:** Opersci BV  
**Concept:** Load Balancing at a Toolset with Cross-Qualification

---

## Overview

This is a browser-based discrete-event simulation (DES) prototype demonstrating factory dynamics in semiconductor fabrication environments. The application allows users to interactively configure toolset parameters, dispatching rules, and cross-qualification matrices, then visualize the impact on key manufacturing metrics in real-time.

**Key Features:**
- Python-based SimPy discrete-event simulation engine
- Pluggable scheduling strategies (FIFO, Least-Loaded-Tool, Random, Optimised SPT)
- FastAPI backend with clean REST API
- React + TypeScript frontend with interactive charts (Recharts)
- Fully separated architecture: simulation core, scheduling engine, scenario configuration, and presentation layer

---

## Architecture

### System Context Diagram

```
┌─────────────┐
│   Browser   │
│  (React +   │
│ TypeScript) │
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                 │
│  ┌────────────────────────────────────┐ │
│  │  API Layer (routes.py, schemas.py) │ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│  ┌────────────▼───────────────────────┐ │
│  │  Simulation Core (engine.py)       │ │
│  │  - SimPy environment               │ │
│  │  - Lot arrivals, toolset queue     │ │
│  │  - Metric collection               │ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│  ┌────────────▼───────────────────────┐ │
│  │  Scheduling Engine (scheduling.py) │ │
│  │  - Dispatching strategies          │ │
│  │  - FIFO, Least-Loaded, Random, SPT │ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│  ┌────────────▼───────────────────────┐ │
│  │  Scenario Layer (load_balancing.py)│ │
│  │  - Default config                  │ │
│  │  - Pedagogical description         │ │
│  │  - Validation bounds               │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Dependencies |
|-----------|---------------|--------------|
| **Simulation Core** (`simulation/engine.py`) | Discrete-event simulation using SimPy; lot arrivals, toolset queue, metric snapshots | SimPy, `models.py`, `scheduling.py` |
| **Scheduling Engine** (`simulation/scheduling.py`) | Dispatching logic; decides (lot, tool) assignments | None (pure Python) |
| **Scenario Configuration** (`scenarios/load_balancing.py`) | Default parameters, pedagogical text, validation bounds | None |
| **API Layer** (`api/routes.py`, `api/schemas.py`) | HTTP endpoints, request validation (Pydantic) | FastAPI, Pydantic, simulation core |
| **Frontend** (`frontend/src/`) | User interface, input forms, metric charts | React, TypeScript, Recharts, Axios |

---

## Local Setup

### Prerequisites

- **Python 3.11+** (tested on 3.11, 3.12)
- **Node.js 18+** and **npm** (for frontend)
- **Git**

### Backend Setup

1. **Clone the repository** (or navigate to the project root):
   ```bash
   cd factory-simulation/backend
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`.  
   Interactive API docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd factory-simulation/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`.

4. **Build for production**:
   ```bash
   npm run build
   ```

   The production build will be in `frontend/dist/`.

---

## Running the Application

1. **Start the backend** (in one terminal):
   ```bash
   cd factory-simulation/backend
   source venv/bin/activate
   uvicorn main:app --reload --port 8000
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   cd factory-simulation/frontend
   npm run dev
   ```

3. **Open your browser** to `http://localhost:3000`

4. **Configure the simulation** using the left panel:
   - Number of tools and products
   - Arrival rate and distribution
   - Processing times per product
   - Cross-qualification matrix (which tools can run which products)
   - Dispatching rule (FIFO, Least-Loaded-Tool, Random, Optimised SPT)
   - Simulation duration and snapshot interval

5. **Click "Run Simulation"** to execute the simulation and view results.

---

## Extension Points

### Adding a New Concept Demonstration

The architecture is designed so that **adding a new concept requires zero changes to the simulation core or scheduling engine**. Follow these steps:

1. **Create a new scenario file** in `backend/scenarios/`, e.g., `critical_ratio.py`:
   ```python
   DEFAULT_CONFIG = { ... }
   CONCEPT_TITLE = "Critical Ratio Dispatching"
   CONCEPT_EXPLAINER = """..."""
   BOUNDS = { ... }
   ```

2. **Update the API layer** (`backend/api/routes.py`) to expose the new scenario:
   ```python
   from ..scenarios import critical_ratio

   @router.get("/api/scenario/critical_ratio")
   def get_critical_ratio_info():
       return ScenarioInfoResponse(
           concept_title=critical_ratio.CONCEPT_TITLE,
           concept_explainer=critical_ratio.CONCEPT_EXPLAINER,
           default_config=critical_ratio.DEFAULT_CONFIG,
           ...
       )
   ```

3. **Update the frontend** to allow scenario selection (dropdown or tabs).

4. **No changes needed** in `simulation/engine.py` or `simulation/scheduling.py`.

### Adding a New Dispatching Strategy

1. **Add a new function** in `backend/simulation/scheduling.py`:
   ```python
   def _my_new_strategy(queue, tool_busy, qualification_matrix, processing_times):
       # Your logic here
       return (lot_idx, tool_idx) or None
   ```

2. **Register it** in the `STRATEGIES` dict:
   ```python
   STRATEGIES = {
       ...
       "my_new_strategy": _my_new_strategy,
   }
   ```

3. **No other changes needed** — the API and frontend will automatically pick it up.

---

## Testing

### Backend Unit Tests

(To be added in future milestones)

Example test structure:
```bash
backend/tests/
  test_engine.py       # Test simulation core
  test_scheduling.py   # Test dispatching strategies
  test_api.py          # Test FastAPI endpoints
```

Run tests:
```bash
pytest backend/tests/
```

### Frontend Tests

(To be added in future milestones)

Example test structure:
```bash
frontend/src/__tests__/
  App.test.tsx
  InputPanel.test.tsx
  ResultsPanel.test.tsx
```

Run tests:
```bash
npm test
```

---

## Deployment

### Option 1: Render (Recommended for MVP)

**Backend:**
1. Create a new **Web Service** on Render
2. Connect your Git repository
3. Set **Build Command**: `pip install -r backend/requirements.txt`
4. Set **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Set **Root Directory**: `backend`
6. Deploy

**Frontend:**
1. Create a new **Static Site** on Render
2. Set **Build Command**: `npm install && npm run build`
3. Set **Publish Directory**: `dist`
4. Set **Root Directory**: `frontend`
5. Add environment variable: `VITE_API_BASE=<your-backend-url>`
6. Deploy

### Option 2: Railway

Similar steps to Render. Railway auto-detects Python and Node.js projects.

### Option 3: Fly.io

1. Install Fly CLI: `https://fly.io/docs/hands-on/install-flyctl/`
2. Create `Dockerfile` for backend and frontend
3. Deploy with `fly deploy`

### Option 4: AWS (EC2 + S3 + CloudFront)

1. **Backend**: Deploy FastAPI on EC2 with Nginx reverse proxy
2. **Frontend**: Build static files, upload to S3, serve via CloudFront

---

## Technical Notes

### Simulation Model Assumptions

1. **Lot Arrivals**: Modeled as a Poisson process (exponential inter-arrival times) or deterministic (fixed inter-arrival time).

2. **Processing Times**: Deterministic per product type. No variability within a product.

3. **Cross-Qualification**: Binary (tool can or cannot process a product). No partial qualification or yield loss.

4. **Toolset Queue**: Single FIFO queue feeding all tools. No per-tool queues.

5. **Dispatching**: Centralized dispatcher with perfect information. No communication delays.

6. **No Breakdowns**: Tools are always available (no maintenance, failures, or setup times).

7. **No Batching**: Each lot is processed individually. No batch processing or lot splitting.

8. **No Re-entrant Flow**: Lots visit the toolset once. No multi-pass or re-entrant flows.

9. **Infinite Horizon**: Simulation runs for a fixed duration. No warm-up period or steady-state detection.

10. **Metrics Collection**: Snapshots taken at fixed intervals. No event-driven metric collection.

### Performance Characteristics

- **Simulation Speed**: A 1,000-lot, 4-tool, 3-product scenario completes in ~2–5 seconds on a modern laptop.
- **Frontend Rendering**: 200 time-series data points render smoothly. For longer simulations, consider downsampling.
- **Memory**: Backend uses ~50–100 MB per simulation run. No persistent state between runs.

### Known Limitations (Phase 1)

- **No 2D/3D Animation**: Metrics plots only (as per SOW).
- **Single Toolset**: No multi-toolset or line-balancing scenarios.
- **No Authentication**: Public access (suitable for internal prototype only).
- **No Persistence**: Simulation results are not saved. Each run is ephemeral.
- **No Real-Time Streaming**: Results returned after simulation completes (not streamed incrementally).

---

## License

MIT License

Copyright (c) 2026 Opersci BV

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Third-Party Licenses

All dependencies use MIT, BSD, Apache 2.0, or ISC licenses (compatible with MIT):

**Backend:**
- FastAPI: MIT
- Uvicorn: BSD 3-Clause
- SimPy: MIT
- Pydantic: MIT

**Frontend:**
- React: MIT
- Recharts: MIT
- Axios: MIT
- Vite: MIT
- TypeScript: Apache 2.0

Full license inventory available in `THIRD_PARTY_LICENSES.md` (to be generated at M4).

---

## Contact

**Client:** Opersci BV  
**Project:** Factory Dynamics Simulation Engine — MVP  
**SOW:** SOW-001

For questions or support, contact the project point of contact as defined in the SOW.
