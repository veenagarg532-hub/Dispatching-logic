# Architecture Documentation

## System Overview

The Factory Dynamics Simulation Engine is built with a **strict separation of concerns** to enable future extensibility without modifying core components.

### Design Principles

1. **Separation of Concerns**: Simulation core, scheduling engine, scenario configuration, and presentation layer are independent modules.

2. **Open-Closed Principle**: Adding new concept demonstrations or dispatching strategies requires only adding new files/functions, not modifying existing code.

3. **Dependency Inversion**: The simulation core depends on abstractions (scheduling interface), not concrete implementations.

4. **Single Responsibility**: Each module has one reason to change.

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React + TS)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ InputPanel   │  │ ResultsPanel │  │ ConceptExplainer     │  │
│  │ - Form inputs│  │ - Charts     │  │ - Pedagogical text   │  │
│  └──────┬───────┘  └──────▲───────┘  └──────────────────────┘  │
│         │                  │                                     │
│         └──────────┬───────┘                                     │
│                    │                                             │
│              ┌─────▼──────┐                                      │
│              │   api.ts   │  (Axios HTTP client)                │
│              └─────┬──────┘                                      │
└────────────────────┼────────────────────────────────────────────┘
                     │ HTTP/JSON
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   API LAYER                                │ │
│  │  ┌──────────────┐         ┌──────────────────────────┐    │ │
│  │  │  routes.py   │────────▶│  schemas.py (Pydantic)   │    │ │
│  │  │  - /scenario │         │  - Request validation    │    │ │
│  │  │  - /simulate │         │  - Response serialization│    │ │
│  │  └──────┬───────┘         └──────────────────────────┘    │ │
│  └─────────┼────────────────────────────────────────────────┘ │
│            │                                                    │
│  ┌─────────▼────────────────────────────────────────────────┐ │
│  │              SIMULATION CORE (engine.py)                 │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  SimPy Environment                                 │  │ │
│  │  │  - arrival_process()   (lot generation)            │  │ │
│  │  │  - dispatcher_process() (central dispatcher)       │  │ │
│  │  │  - tool_process()      (lot processing)            │  │ │
│  │  │  - snapshot_process()  (metric collection)         │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │                          │                                │ │
│  │                          │ calls                          │ │
│  │                          ▼                                │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │         SCHEDULING ENGINE (scheduling.py)          │  │ │
│  │  │  dispatch(strategy, queue, tool_busy, ...)         │  │ │
│  │  │    ├─ _fifo()                                      │  │ │
│  │  │    ├─ _least_loaded_tool()                         │  │ │
│  │  │    ├─ _random_qualified_tool()                     │  │ │
│  │  │    └─ _shortest_processing_time()                  │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         SCENARIO LAYER (scenarios/load_balancing.py)       │ │
│  │  - DEFAULT_CONFIG (default parameters)                     │ │
│  │  - CONCEPT_TITLE, CONCEPT_EXPLAINER (pedagogical text)     │ │
│  │  - BOUNDS (validation rules)                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              DATA MODELS (models.py)                       │ │
│  │  - Lot (lot_id, product_id, arrival_time, ...)             │ │
│  │  - MetricSnapshot (time, wip, cumulative_moves, ...)       │ │
│  │  - SimulationResult (snapshots, completed_lots, ...)       │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. User Configures Simulation (Frontend → Backend)

```
User fills form
    ↓
InputPanel.tsx collects config
    ↓
api.ts sends POST /api/simulate with SimulationRequest
    ↓
routes.py receives request
    ↓
schemas.py validates (Pydantic)
    ↓
engine.run_simulation(config) called
```

### 2. Simulation Execution (Backend)

```
run_simulation(config)
    ↓
Create SimPy environment
    ↓
Register processes:
  - arrival_process (generates lots)
  - dispatcher_process (assigns lots to tools)
  - tool_process (processes lots)
  - snapshot_process (records metrics)
    ↓
env.run(until=sim_duration)
    ↓
Dispatcher calls scheduling.dispatch(strategy, queue, tool_busy, ...)
    ↓
Scheduling engine returns (lot_idx, tool_idx) or None
    ↓
Dispatcher starts tool_process for selected lot
    ↓
Metrics collected at snapshot_interval
    ↓
Return SimulationResult
```

### 3. Results Display (Backend → Frontend)

```
SimulationResult returned to routes.py
    ↓
Serialized to JSON (SimulationResponse)
    ↓
Sent to frontend
    ↓
ResultsPanel.tsx receives data
    ↓
Recharts renders line charts
    ↓
Summary stats displayed
```

---

## Module Responsibilities

### Backend Modules

| Module | File | Responsibility | External Dependencies |
|--------|------|----------------|----------------------|
| **Simulation Core** | `simulation/engine.py` | Discrete-event simulation using SimPy | SimPy |
| **Scheduling Engine** | `simulation/scheduling.py` | Dispatching strategies (pure Python) | None |
| **Data Models** | `simulation/models.py` | Shared data structures | None |
| **Scenario Config** | `scenarios/load_balancing.py` | Default config, pedagogical text | None |
| **API Routes** | `api/routes.py` | HTTP endpoints | FastAPI |
| **API Schemas** | `api/schemas.py` | Request/response validation | Pydantic |
| **Main App** | `main.py` | FastAPI app initialization | FastAPI |

### Frontend Modules

| Module | File | Responsibility | External Dependencies |
|--------|------|----------------|----------------------|
| **App** | `App.tsx` | Root component, state management | React |
| **Input Panel** | `components/InputPanel.tsx` | Configuration form | React |
| **Results Panel** | `components/ResultsPanel.tsx` | Charts and summary stats | React, Recharts |
| **Concept Explainer** | `components/ConceptExplainer.tsx` | Pedagogical text display | React |
| **API Client** | `api.ts` | HTTP communication | Axios |
| **Types** | `types.ts` | TypeScript type definitions | None |

---

## Key Design Decisions

### 1. Why SimPy?

- **Mature**: 15+ years of development, widely used in academia and industry.
- **Pythonic**: Clean API, easy to read and extend.
- **Discrete-Event**: Natural fit for manufacturing simulation.
- **Open Source**: MIT license, no vendor lock-in.

### 2. Why FastAPI?

- **Modern**: Async support, automatic OpenAPI docs.
- **Fast**: Built on Starlette and Pydantic, high performance.
- **Type-Safe**: Pydantic validation catches errors early.
- **Lightweight**: No ORM or database required for this MVP.

### 3. Why React + TypeScript?

- **Industry Standard**: Large ecosystem, easy to hire developers.
- **Type Safety**: TypeScript catches errors at compile time.
- **Component-Based**: Easy to add new UI elements.
- **Vite**: Fast dev server and build tool.

### 4. Why Recharts?

- **React-Native**: Built for React, not a wrapper around D3.
- **Declarative**: Easy to configure charts with JSX.
- **Responsive**: Works well on mobile and desktop.
- **MIT License**: Compatible with project license.

### 5. Why Separate Scheduling Engine?

- **Testability**: Scheduling logic can be unit-tested without SimPy.
- **Extensibility**: Adding a new strategy requires only adding a function.
- **Reusability**: Scheduling engine could be used in other simulation tools.
- **Clarity**: Separation makes the codebase easier to understand.

---

## Extension Patterns

### Adding a New Concept Demonstration

**Goal**: Add "Critical Ratio Dispatching" concept without modifying simulation core.

**Steps**:

1. Create `backend/scenarios/critical_ratio.py`:
   ```python
   DEFAULT_CONFIG = { ... }
   CONCEPT_TITLE = "Critical Ratio Dispatching"
   CONCEPT_EXPLAINER = """..."""
   BOUNDS = { ... }
   ```

2. Add route in `backend/api/routes.py`:
   ```python
   @router.get("/api/scenario/critical_ratio")
   def get_critical_ratio_info():
       return ScenarioInfoResponse(...)
   ```

3. Update frontend to allow scenario selection.

**Files Modified**: 2 (routes.py, frontend)  
**Files Added**: 1 (critical_ratio.py)  
**Core Modules Modified**: 0 ✅

### Adding a New Dispatching Strategy

**Goal**: Add "Earliest Due Date" (EDD) dispatching.

**Steps**:

1. Add function in `backend/simulation/scheduling.py`:
   ```python
   def _earliest_due_date(queue, tool_busy, qualification_matrix, processing_times):
       # Assume lots have a due_date attribute
       best = None
       best_due = float("inf")
       for lot_idx, lot in enumerate(queue):
           if lot.due_date < best_due:
               for tool_idx, busy in enumerate(tool_busy):
                   if not busy and qualification_matrix[tool_idx][lot.product_id]:
                       best = (lot_idx, tool_idx)
                       best_due = lot.due_date
                       break
       return best
   ```

2. Register in `STRATEGIES`:
   ```python
   STRATEGIES = {
       ...
       "earliest_due_date": _earliest_due_date,
   }
   ```

**Files Modified**: 1 (scheduling.py)  
**Files Added**: 0  
**Core Modules Modified**: 0 ✅

### Adding a New Metric

**Goal**: Track "average tool idle time".

**Steps**:

1. Add field to `MetricSnapshot` in `models.py`:
   ```python
   @dataclass
   class MetricSnapshot:
       ...
       tool_idle_time: list[float]  # NEW
   ```

2. Update `engine.py` to collect the metric:
   ```python
   self.snapshots.append(MetricSnapshot(
       ...
       tool_idle_time=[self.env.now - self.tool_busy_time[t] for t in range(self.num_tools)],
   ))
   ```

3. Update `schemas.py` to include in response:
   ```python
   class MetricSnapshotOut(BaseModel):
       ...
       tool_idle_time: list[float]
   ```

4. Update frontend to display the metric.

**Files Modified**: 4 (models.py, engine.py, schemas.py, frontend)  
**Files Added**: 0  
**Scheduling Engine Modified**: 0 ✅

---

## Testing Strategy

### Unit Tests

- **Scheduling Engine**: Test each strategy with known inputs, verify correct (lot, tool) selection.
- **Data Models**: Test Lot.queue_time, Lot.cycle_time calculations.
- **API Schemas**: Test Pydantic validation (invalid inputs should raise errors).

### Integration Tests

- **Simulation Core**: Run a small simulation (10 lots, 2 tools), verify metrics are correct.
- **API Endpoints**: Test GET /api/scenario and POST /api/simulate with valid/invalid payloads.

### End-to-End Tests

- **Frontend**: Use Playwright or Cypress to test full user flow (configure → run → view results).

---

## Performance Considerations

### Backend

- **Simulation Speed**: O(n) in number of lots. A 1,000-lot simulation takes ~2–5 seconds.
- **Memory**: Each lot is ~200 bytes. 10,000 lots = ~2 MB.
- **Concurrency**: FastAPI is async, but SimPy is single-threaded. For multiple concurrent users, consider running simulations in a background task queue (Celery, RQ).

### Frontend

- **Chart Rendering**: Recharts handles 200–500 data points smoothly. For longer simulations, downsample snapshots (e.g., every 10th point).
- **Bundle Size**: React + Recharts + Axios = ~300 KB gzipped. Acceptable for modern web.

---

## Security Considerations

### Phase 1 (MVP)

- **No Authentication**: Suitable for internal prototype only.
- **No Rate Limiting**: A malicious user could spam the /simulate endpoint.
- **No Input Sanitization**: Pydantic validates types and ranges, but does not prevent resource exhaustion (e.g., sim_duration=1,000,000).

### Future Phases

- Add authentication (OAuth2, JWT).
- Add rate limiting (per-user or per-IP).
- Add resource limits (max simulation duration, max queue size).
- Add HTTPS (TLS certificates).

---

## Deployment Architecture

### Development

```
Developer Machine
  ├─ Backend (uvicorn, port 8000)
  └─ Frontend (Vite dev server, port 3000)
```

### Production (Render)

```
Internet
    │
    ├─ Frontend (Static Site, CDN)
    │    └─ Calls API via HTTPS
    │
    └─ Backend (Web Service, HTTPS)
         └─ FastAPI + Uvicorn
```

### Production (AWS)

```
Internet
    │
    ├─ CloudFront (CDN)
    │    └─ S3 Bucket (Frontend static files)
    │
    └─ Application Load Balancer
         └─ EC2 Instance (Backend)
              └─ Nginx → Uvicorn → FastAPI
```

---

## Glossary

- **DES**: Discrete-Event Simulation
- **WIP**: Work-In-Process (lots in queue + being processed)
- **Toolset**: A group of parallel machines
- **Cross-Qualification**: Which tools can process which products
- **Dispatching Rule**: Strategy for assigning lots to tools
- **FIFO**: First-In-First-Out
- **SPT**: Shortest Processing Time
- **Lot**: A batch of wafers or work items
- **Queue Time**: Time a lot waits before processing starts
- **Cycle Time**: Total time from arrival to completion
- **Utilisation**: Fraction of time a tool is busy

---

## References

- **SimPy Documentation**: https://simpy.readthedocs.io/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **Recharts Documentation**: https://recharts.org/
- **Factory Physics** (Hopp & Spearman): Foundational text on manufacturing dynamics
- **Semiconductor Manufacturing** (May & Spanos): Domain-specific reference

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-24 | Initial MVP release (Phase 1) |

---

**Document Owner**: Contractor (as per SOW-001)  
**Last Updated**: 2026-04-24
