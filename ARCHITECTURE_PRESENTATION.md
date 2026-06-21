# Factory Dynamics Simulation Engine
## Architecture & Technical Stack Documentation

**Project:** Factory Dynamics Simulation Engine — MVP (Phase 1)  
**Client:** Opersci BV  
**Concept:** Load Balancing at a Toolset with Cross-Qualification  
**Date:** April 2026

---

## Executive Summary

The Factory Dynamics Simulation Engine is a web-based discrete-event simulation (DES) platform designed to demonstrate manufacturing dynamics in semiconductor fabrication environments. The system enables interactive exploration of load balancing strategies through real-time visualization of key performance metrics.

### Key Capabilities
- **Interactive Simulation**: Configure and run discrete-event simulations in real-time
- **Multiple Dispatching Strategies**: Compare FIFO, Least-Loaded-Tool, Random, and Optimised (SPT) approaches
- **Real-Time Visualization**: Four synchronized metric charts showing WIP, throughput, queue time, and utilisation
- **Extensible Architecture**: Add new concepts and strategies without modifying core simulation engine

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (React + TypeScript SPA)                     │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Input Panel  │  │ Results Panel│  │ Concept Explainer    │  │
│  │ - Config     │  │ - 4 Charts   │  │ - Pedagogical Text   │  │
│  │ - Controls   │  │ - Statistics │  │                      │  │
│  └──────┬───────┘  └──────▲───────┘  └──────────────────────┘  │
│         │                  │                                     │
└─────────┼──────────────────┼─────────────────────────────────────┘
          │                  │
          │   HTTP/JSON      │
          │   REST API       │
          ▼                  │
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API LAYER                          │
│                      (FastAPI + Python)                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  API Routes                    Pydantic Schemas            │ │
│  │  • GET  /api/scenario          • Request Validation        │ │
│  │  • POST /api/simulate          • Response Serialization    │ │
│  │  • GET  /health                • Type Safety               │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                              │
└───────────────────┼──────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SIMULATION CORE LAYER                         │
│                   (SimPy + Python)                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Discrete-Event Simulation Engine                          │ │
│  │  • Lot Arrival Process (Poisson/Deterministic)             │ │
│  │  • Toolset Queue Management                                │ │
│  │  • Tool Processing (Product-Dependent Times)               │ │
│  │  • Metric Collection (Time-Series Snapshots)               │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                              │
│                   │ Dispatching Decisions                        │
│                   ▼                                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Scheduling Engine (Strategy Pattern)                      │ │
│  │  • FIFO (First-In-First-Out)                               │ │
│  │  • Least-Loaded-Tool                                       │ │
│  │  • Random-Qualified-Tool                                   │ │
│  │  • Optimised (Shortest Processing Time)                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                    ▲
                    │
                    │ Configuration
                    │
┌─────────────────────────────────────────────────────────────────┐
│                   SCENARIO CONFIGURATION                        │
│                                                                  │
│  • Default Parameters (Tools, Products, Rates)                  │
│  • Pedagogical Content (Educational Text)                       │
│  • Validation Rules (Input Bounds)                              │
│  • Cross-Qualification Matrix                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architectural Principles

### 1. Separation of Concerns
Each layer has a single, well-defined responsibility:
- **Presentation Layer**: User interface and interaction
- **API Layer**: HTTP communication and validation
- **Simulation Core**: Discrete-event simulation logic
- **Scheduling Engine**: Dispatching strategy implementation
- **Configuration Layer**: Scenario parameters and metadata

### 2. Open-Closed Principle
The system is **open for extension** but **closed for modification**:
- Adding a new concept demonstration requires only creating a new scenario file
- Adding a new dispatching strategy requires only adding a new function
- No changes to the simulation core are needed for either extension

### 3. Dependency Inversion
High-level modules do not depend on low-level modules:
- Simulation core depends on scheduling interface (abstraction)
- API layer depends on simulation interface (abstraction)
- Frontend depends on API contract (abstraction)

### 4. Single Responsibility
Each module has one reason to change:
- `engine.py` changes only if simulation logic changes
- `scheduling.py` changes only if dispatching strategies change
- `load_balancing.py` changes only if scenario parameters change

---

## Technology Stack

### Backend Stack

#### Core Technologies

| Technology | Version | Purpose | License |
|------------|---------|---------|---------|
| **Python** | 3.11+ | Programming language | PSF |
| **SimPy** | 4.1.1 | Discrete-event simulation framework | MIT |
| **FastAPI** | 0.111.0 | Modern web framework for APIs | MIT |
| **Uvicorn** | 0.29.0 | ASGI server for FastAPI | BSD-3 |
| **Pydantic** | 2.7.1 | Data validation and serialization | MIT |

#### Why These Technologies?

**Python 3.11+**
- Industry standard for scientific computing and simulation
- Rich ecosystem of libraries
- Excellent readability and maintainability
- Strong typing support (type hints)

**SimPy**
- Mature discrete-event simulation library (15+ years)
- Pythonic API with generators and coroutines
- Widely used in academia and industry
- MIT licensed (no vendor lock-in)
- Active community and documentation

**FastAPI**
- Modern async framework (high performance)
- Automatic OpenAPI documentation generation
- Built-in request/response validation via Pydantic
- Type-safe with Python type hints
- Easy to test and deploy

**Uvicorn**
- Lightning-fast ASGI server
- Production-ready with auto-reload for development
- Low memory footprint
- Excellent performance characteristics

**Pydantic**
- Runtime type checking and validation
- Automatic JSON serialization/deserialization
- Clear error messages for invalid inputs
- Integrates seamlessly with FastAPI

---

### Frontend Stack

#### Core Technologies

| Technology | Version | Purpose | License |
|------------|---------|---------|---------|
| **React** | 18.2 | UI framework | MIT |
| **TypeScript** | 5.2 | Type-safe JavaScript | Apache 2.0 |
| **Vite** | 5.2 | Build tool and dev server | MIT |
| **Recharts** | 2.12.2 | Charting library | MIT |
| **Axios** | 1.6.8 | HTTP client | MIT |

#### Why These Technologies?

**React**
- Industry-standard UI framework
- Component-based architecture (reusable, testable)
- Large ecosystem and community
- Excellent developer tools
- Virtual DOM for efficient rendering

**TypeScript**
- Type safety catches errors at compile time
- Better IDE support (autocomplete, refactoring)
- Self-documenting code (types as documentation)
- Easier to maintain and refactor
- Gradual adoption path from JavaScript

**Vite**
- Extremely fast dev server (instant hot module reload)
- Optimized production builds
- Modern ES modules support
- Simple configuration
- Better developer experience than Webpack

**Recharts**
- React-native charting library (not a D3 wrapper)
- Declarative API (easy to configure)
- Responsive and interactive charts
- Good performance with time-series data
- MIT licensed

**Axios**
- Promise-based HTTP client
- Automatic JSON transformation
- Request/response interceptors
- Better error handling than fetch
- Wide browser support

---

## Component Architecture

### Backend Components

#### 1. Simulation Core (`simulation/engine.py`)

**Responsibility**: Execute discrete-event simulations using SimPy

**Key Classes**:
- `_ToolsetSimulation`: Internal simulation state and processes

**Key Processes**:
- `arrival_process()`: Generate lot arrivals (Poisson or deterministic)
- `dispatcher_process()`: Central dispatcher loop
- `tool_process()`: Process individual lots on tools
- `snapshot_process()`: Collect metrics at intervals

**Inputs**:
- Configuration dictionary (tools, products, rates, etc.)

**Outputs**:
- `SimulationResult` object with time-series data and statistics

**Dependencies**:
- SimPy (discrete-event simulation)
- `models.py` (data structures)
- `scheduling.py` (dispatching decisions)

---

#### 2. Scheduling Engine (`simulation/scheduling.py`)

**Responsibility**: Implement dispatching strategies

**Key Functions**:
- `dispatch()`: Public entry point
- `_fifo()`: First-In-First-Out strategy
- `_least_loaded_tool()`: Balance load across tools
- `_random_qualified_tool()`: Random selection
- `_shortest_processing_time()`: Optimised SPT strategy

**Inputs**:
- Strategy name (string)
- Queue state (list of lots)
- Tool availability (list of booleans)
- Qualification matrix (2D boolean array)
- Processing times (list of floats)

**Outputs**:
- `(lot_index, tool_index)` tuple or `None`

**Dependencies**:
- None (pure Python, no external dependencies)

**Design Pattern**: Strategy Pattern

---

#### 3. Data Models (`simulation/models.py`)

**Responsibility**: Define shared data structures

**Key Classes**:
- `Lot`: Represents a manufacturing lot
  - `lot_id`: Unique identifier
  - `product_id`: Product type index
  - `arrival_time`: When lot entered queue
  - `start_time`: When processing began
  - `finish_time`: When processing completed
  - `assigned_tool`: Tool that processed the lot

- `MetricSnapshot`: Time-stamped metrics
  - `time`: Simulation time
  - `wip`: Work-in-process (queue + processing)
  - `cumulative_moves`: Total lots completed
  - `cumulative_queue_time`: Sum of all queue times
  - `tool_utilisation`: Per-tool utilisation [0..1]

- `SimulationResult`: Complete simulation output
  - `snapshots`: List of metric snapshots
  - `completed_lots`: List of finished lots
  - `total_lots_arrived`: Count
  - `total_lots_completed`: Count
  - `mean_queue_time`: Average
  - `mean_cycle_time`: Average
  - `tool_utilisation`: Final per-tool utilisation

**Dependencies**: None (pure Python dataclasses)

---

#### 4. Scenario Configuration (`scenarios/load_balancing.py`)

**Responsibility**: Define scenario parameters and pedagogical content

**Key Exports**:
- `DEFAULT_CONFIG`: Default simulation parameters
- `CONCEPT_TITLE`: Display title
- `CONCEPT_EXPLAINER`: Educational text (markdown)
- `BOUNDS`: Validation rules for inputs

**Purpose**:
- Separate configuration from simulation logic
- Enable easy reconfiguration without code changes
- Provide pedagogical context for users

**Dependencies**: None

---

#### 5. API Layer (`api/routes.py`, `api/schemas.py`)

**Responsibility**: HTTP endpoints and request/response validation

**Endpoints**:
- `GET /api/scenario`: Returns default config and metadata
- `POST /api/simulate`: Runs simulation and returns results
- `GET /health`: Health check

**Validation** (Pydantic schemas):
- `SimulationRequest`: Validates all input parameters
  - Range checks (e.g., num_tools: 1-10)
  - Dimension checks (matrix sizes match)
  - Qualification checks (each tool/product reachable)
  - Strategy validation (known dispatching rule)

- `SimulationResponse`: Serializes simulation results
  - Converts internal data structures to JSON
  - Rounds floats to 4 decimal places

**Dependencies**:
- FastAPI (web framework)
- Pydantic (validation)
- Simulation core (execution)

---

### Frontend Components

#### 1. App Component (`App.tsx`)

**Responsibility**: Root component, state management, orchestration

**State**:
- `scenarioInfo`: Metadata from backend
- `config`: Current simulation configuration
- `results`: Simulation results
- `loading`: Loading state
- `error`: Error messages

**Key Functions**:
- `handleRun()`: Trigger simulation
- `handleReset()`: Reset to defaults

**Lifecycle**:
1. Mount: Fetch scenario info from backend
2. User configures: Update local state
3. User clicks "Run": POST to backend, display results

---

#### 2. Input Panel (`components/InputPanel.tsx`)

**Responsibility**: Configuration form with all user inputs

**Inputs Managed**:
- Number of tools (1-10)
- Number of products (1-8)
- Arrival rate (0.01-10.0)
- Arrival distribution (exponential/fixed)
- Processing times per product
- Cross-qualification matrix (interactive checkboxes)
- Dispatching rule (dropdown)
- Simulation duration (10-2000)
- Snapshot interval (0.5-10)
- Random seed (optional)

**Features**:
- Real-time validation
- Dynamic matrix resizing (when tools/products change)
- Responsive layout

---

#### 3. Results Panel (`components/ResultsPanel.tsx`)

**Responsibility**: Display simulation results with charts and statistics

**Charts** (Recharts):
1. **Toolset WIP Over Time**: Line chart showing queue + processing
2. **Cumulative Total Moves**: Line chart showing throughput
3. **Total Accumulated Queue Time**: Line chart showing cumulative wait
4. **Average Tool Utilisation**: Line chart showing efficiency

**Summary Statistics**:
- Total lots arrived
- Total lots completed
- Mean queue time
- Mean cycle time
- Final tool utilisation (per tool)

**Features**:
- Synchronized tooltips across charts
- Responsive sizing
- Color-coded metrics

---

#### 4. Concept Explainer (`components/ConceptExplainer.tsx`)

**Responsibility**: Display pedagogical content

**Content**:
- What is being demonstrated
- Why it matters
- Key insights
- How to explore

**Features**:
- Markdown-style formatting (bold text)
- Collapsible sections (future enhancement)

---

## Data Flow

### 1. Initial Load

```
User opens browser
    ↓
Frontend loads (React app)
    ↓
useEffect() hook triggers
    ↓
GET /api/scenario
    ↓
Backend returns:
  - Default config
  - Pedagogical text
  - Available strategies
    ↓
Frontend displays:
  - Input panel (pre-filled)
  - Concept explainer
```

### 2. Simulation Execution

```
User configures parameters
    ↓
User clicks "Run Simulation"
    ↓
Frontend validates inputs (client-side)
    ↓
POST /api/simulate with config
    ↓
Backend validates (Pydantic)
    ↓
Simulation core executes:
  1. Create SimPy environment
  2. Register processes (arrival, dispatcher, tools, snapshots)
  3. Run simulation (env.run(until=duration))
  4. Collect metrics
    ↓
Backend returns SimulationResult
    ↓
Frontend receives JSON response
    ↓
ResultsPanel renders:
  - 4 charts (Recharts)
  - Summary statistics
```

### 3. Dispatching Decision Flow

```
Lot arrives at toolset
    ↓
Added to queue
    ↓
Dispatcher wakes up (event-driven)
    ↓
Calls scheduling.dispatch(strategy, queue, tool_busy, ...)
    ↓
Scheduling engine evaluates:
  - Which lots are in queue?
  - Which tools are free?
  - Which tools can process which lots? (qualification matrix)
  - Apply strategy logic (FIFO, SPT, etc.)
    ↓
Returns (lot_index, tool_index) or None
    ↓
If match found:
  - Remove lot from queue
  - Start tool_process()
  - Tool becomes busy
    ↓
Tool finishes processing:
  - Lot marked complete
  - Tool becomes free
  - Dispatcher wakes up again
```

---

## Key Design Patterns

### 1. Strategy Pattern (Scheduling Engine)

**Problem**: Need to support multiple dispatching algorithms without modifying simulation core

**Solution**: Encapsulate each algorithm in a separate function, register in a dictionary

```python
STRATEGIES = {
    "fifo": _fifo,
    "least_loaded_tool": _least_loaded_tool,
    "random_qualified_tool": _random_qualified_tool,
    "optimised_spt": _shortest_processing_time,
}

def dispatch(strategy: str, ...):
    fn = STRATEGIES[strategy]
    return fn(...)
```

**Benefits**:
- Easy to add new strategies (just add a function)
- No if/else chains
- Strategies are independently testable

---

### 2. Repository Pattern (Scenario Configuration)

**Problem**: Need to separate configuration data from simulation logic

**Solution**: Centralize scenario parameters in dedicated modules

```python
# scenarios/load_balancing.py
DEFAULT_CONFIG = { ... }
CONCEPT_TITLE = "..."
CONCEPT_EXPLAINER = """..."""
```

**Benefits**:
- Configuration changes don't touch simulation code
- Easy to add new scenarios (new file)
- Clear separation of concerns

---

### 3. Facade Pattern (API Layer)

**Problem**: Frontend needs simple interface to complex simulation system

**Solution**: API layer provides simplified endpoints that hide complexity

```python
@router.post("/simulate")
def run_simulation_endpoint(request: SimulationRequest):
    config = request.model_dump()
    result = run_simulation(config)  # Complex internal logic
    return SimulationResponse(...)   # Simple response
```

**Benefits**:
- Frontend doesn't need to know about SimPy
- Backend can change implementation without breaking API
- Clear contract between layers

---

### 4. Observer Pattern (Metric Collection)

**Problem**: Need to collect metrics at regular intervals without blocking simulation

**Solution**: Separate snapshot process that observes simulation state

```python
def snapshot_process(self):
    while True:
        # Observe current state
        wip = len(self.queue) + sum(self.tool_busy)
        self.snapshots.append(MetricSnapshot(...))
        yield self.env.timeout(self.snapshot_interval)
```

**Benefits**:
- Metrics collection is decoupled from simulation logic
- Easy to change snapshot frequency
- No performance impact on simulation

---

## Performance Characteristics

### Backend Performance

| Metric | Value | Notes |
|--------|-------|-------|
| **Simulation Speed** | 2-5 seconds | 1,000 lots, 4 tools, 3 products |
| **Memory Usage** | 50-100 MB | Per simulation run |
| **Lot Processing** | O(n) | Linear in number of lots |
| **Dispatching** | O(n×m) | n=queue size, m=tools |
| **Snapshot Collection** | O(1) | Constant time per snapshot |

### Frontend Performance

| Metric | Value | Notes |
|--------|-------|-------|
| **Initial Load** | <2 seconds | First paint |
| **Bundle Size** | ~300 KB | Gzipped (React + Recharts) |
| **Chart Rendering** | <100ms | 200 data points |
| **Re-render Time** | <50ms | Configuration changes |

### Scalability Limits (Phase 1)

| Parameter | Limit | Reason |
|-----------|-------|--------|
| **Tools** | 10 | UI space, validation bounds |
| **Products** | 8 | UI space, validation bounds |
| **Simulation Duration** | 2,000 time units | Frontend chart rendering |
| **Lots** | ~10,000 | Memory constraints |
| **Concurrent Users** | 10-20 | Single-threaded SimPy |

**Note**: These are MVP limits. Production system would use background task queues (Celery, RQ) for scalability.

---

## Security Considerations

### Phase 1 (MVP) — Internal Prototype

**Current State**:
- ❌ No authentication
- ❌ No rate limiting
- ❌ No input sanitization beyond validation
- ✅ CORS enabled (for development)
- ✅ Pydantic validation (type safety)

**Acceptable for**:
- Internal demonstrations
- Proof-of-concept
- Controlled environments

**NOT acceptable for**:
- Public internet deployment
- Production use
- Multi-tenant environments

### Future Phases — Production Hardening

**Required Additions**:
1. **Authentication**: OAuth2 / JWT tokens
2. **Authorization**: Role-based access control
3. **Rate Limiting**: Per-user or per-IP limits
4. **Input Sanitization**: Prevent resource exhaustion
5. **HTTPS**: TLS certificates
6. **Logging**: Audit trails
7. **Monitoring**: Performance and error tracking

---

## Testing Strategy

### Unit Tests (M2)

**Backend**:
- `test_scheduling.py`: Test each dispatching strategy
  - Known inputs → expected (lot, tool) selection
  - Edge cases (empty queue, all tools busy)
  
- `test_models.py`: Test data model calculations
  - Lot.queue_time, Lot.cycle_time
  - MetricSnapshot aggregations

- `test_api_schemas.py`: Test Pydantic validation
  - Valid inputs → accepted
  - Invalid inputs → clear error messages

**Frontend**:
- `InputPanel.test.tsx`: Test form interactions
- `ResultsPanel.test.tsx`: Test chart rendering
- `api.test.ts`: Test HTTP client

### Integration Tests (M2)

**Backend**:
- `test_simulation_integration.py`: End-to-end simulation
  - Small scenario (10 lots, 2 tools)
  - Verify metrics are correct
  - Compare strategies (FIFO vs SPT)

- `test_api_integration.py`: Test API endpoints
  - GET /api/scenario → returns valid data
  - POST /api/simulate → returns results
  - Invalid payloads → 422 errors

### End-to-End Tests (M3)

**Full Stack**:
- Use Playwright or Cypress
- Test complete user flow:
  1. Load application
  2. Configure simulation
  3. Run simulation
  4. Verify charts render
  5. Verify statistics displayed

---

## Deployment Architecture

### Development Environment

```
Developer Machine
├── Backend (uvicorn, port 8000)
│   └── Hot reload enabled
└── Frontend (Vite dev server, port 3000)
    └── Hot module replacement
```

### Production Environment (Render)

```
Internet
    │
    ├─── Frontend (Static Site)
    │    ├── CDN (Render CDN)
    │    └── Static files (HTML, JS, CSS)
    │
    └─── Backend (Web Service)
         ├── Uvicorn (ASGI server)
         ├── FastAPI (application)
         └── Environment variables
```

### Alternative: AWS Deployment

```
Internet
    │
    ├─── CloudFront (CDN)
    │    └── S3 Bucket (Frontend)
    │
    └─── Application Load Balancer
         └── EC2 Instance (Backend)
              ├── Nginx (reverse proxy)
              └── Uvicorn (ASGI server)
```

---

## Extension Patterns

### Adding a New Concept Demonstration

**Example**: Critical Ratio Dispatching

**Steps**:
1. Create `scenarios/critical_ratio.py`:
   ```python
   DEFAULT_CONFIG = { ... }
   CONCEPT_TITLE = "Critical Ratio Dispatching"
   CONCEPT_EXPLAINER = """..."""
   ```

2. Add route in `api/routes.py`:
   ```python
   @router.get("/api/scenario/critical_ratio")
   def get_critical_ratio_info():
       return ScenarioInfoResponse(...)
   ```

3. Update frontend to allow scenario selection

**Files Modified**: 2  
**Core Modules Modified**: 0 ✅

---

### Adding a New Dispatching Strategy

**Example**: Earliest Due Date (EDD)

**Steps**:
1. Add function in `simulation/scheduling.py`:
   ```python
   def _earliest_due_date(queue, tool_busy, ...):
       # Implementation
       return (lot_idx, tool_idx)
   ```

2. Register in `STRATEGIES`:
   ```python
   STRATEGIES["earliest_due_date"] = _earliest_due_date
   ```

**Files Modified**: 1  
**Core Modules Modified**: 0 ✅

---

### Adding a New Metric

**Example**: Tool Idle Time

**Steps**:
1. Add field to `MetricSnapshot` in `models.py`
2. Update `engine.py` to collect the metric
3. Update `schemas.py` to include in response
4. Update frontend to display

**Files Modified**: 4  
**Scheduling Engine Modified**: 0 ✅

---

## Glossary

| Term | Definition |
|------|------------|
| **DES** | Discrete-Event Simulation — simulation where state changes at discrete points in time |
| **WIP** | Work-In-Process — lots currently in queue or being processed |
| **Toolset** | A group of parallel machines that can process lots |
| **Cross-Qualification** | Which tools are certified to process which product types |
| **Dispatching Rule** | Strategy for assigning lots to tools |
| **FIFO** | First-In-First-Out — process lots in arrival order |
| **SPT** | Shortest Processing Time — prioritize short jobs |
| **Queue Time** | Time a lot waits before processing starts |
| **Cycle Time** | Total time from arrival to completion |
| **Utilisation** | Fraction of time a tool is busy (0 = idle, 1 = always busy) |
| **Lot** | A batch of wafers or work items |
| **SimPy** | Python library for discrete-event simulation |
| **FastAPI** | Modern Python web framework |
| **Pydantic** | Data validation library |
| **React** | JavaScript UI framework |
| **TypeScript** | Typed superset of JavaScript |
| **Recharts** | React charting library |

---

## References

### Technical Documentation
- **SimPy**: https://simpy.readthedocs.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **TypeScript**: https://www.typescriptlang.org/
- **Recharts**: https://recharts.org/
- **Pydantic**: https://docs.pydantic.dev/

### Domain Knowledge
- **Factory Physics** (Hopp & Spearman) — Foundational text on manufacturing dynamics
- **Semiconductor Manufacturing** (May & Spanos) — Domain-specific reference
- **Discrete-Event System Simulation** (Banks et al.) — Simulation methodology

### Standards & Best Practices
- **REST API Design**: https://restfulapi.net/
- **React Best Practices**: https://react.dev/learn
- **Python Type Hints**: PEP 484, PEP 585
- **OpenAPI Specification**: https://swagger.io/specification/

---

## Appendix: File Inventory

### Backend Files (12)
```
backend/
├── main.py                    # FastAPI app (40 lines)
├── requirements.txt           # Dependencies
├── simulation/
│   ├── engine.py             # DES core (220 lines)
│   ├── scheduling.py         # Strategies (140 lines)
│   └── models.py             # Data models (60 lines)
├── scenarios/
│   └── load_balancing.py     # Config (90 lines)
└── api/
    ├── routes.py             # Endpoints (60 lines)
    └── schemas.py            # Validation (140 lines)
```

### Frontend Files (11)
```
frontend/
├── package.json              # Dependencies
├── vite.config.ts            # Build config
├── src/
│   ├── App.tsx              # Root (100 lines)
│   ├── api.ts               # HTTP client (20 lines)
│   ├── types.ts             # TypeScript types (40 lines)
│   └── components/
│       ├── InputPanel.tsx   # Form (200 lines)
│       ├── ResultsPanel.tsx # Charts (150 lines)
│       └── ConceptExplainer.tsx # Text (30 lines)
```

### Documentation Files (8)
```
├── README.md                 # Main docs (500 lines)
├── ARCHITECTURE.md           # Detailed arch (600 lines)
├── QUICKSTART.md            # Setup guide (300 lines)
├── INSTALLATION.md          # Install guide (400 lines)
├── PROJECT_SUMMARY.md       # Summary (300 lines)
├── DELIVERY_CHECKLIST.md    # SOW compliance (400 lines)
├── ARCHITECTURE_PRESENTATION.md  # This document
└── LICENSE                  # MIT license
```

**Total**: 32 files, ~2,500 lines of code, ~2,500 lines of documentation

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-24 | Contractor | Initial architecture documentation |

**Document Owner**: Contractor (as per SOW-001)  
**Approval**: Pending Client Review  
**Next Review**: M2 (Week 5)

---

**End of Architecture & Technical Stack Documentation**
