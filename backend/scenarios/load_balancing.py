"""
Scenario configuration: Load Balancing at a Toolset with Cross-Qualification.

This module defines the default scenario parameters and the pedagogical
description for the concept demonstration. It is the ONLY place that needs
to change when the scenario is reconfigured — the simulation core and
scheduling engine are untouched.

To add a new concept demonstration in a future phase, create a new file in
this package (e.g. critical_ratio.py) following the same interface.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Default scenario — sensible starting point for the UI
# ---------------------------------------------------------------------------

DEFAULT_CONFIG: dict = {
    "num_tools": 4,
    "num_products": 3,
    # System capacity = num_tools / avg_processing_time = 4 / 5.0 = 0.8 lots/tu.
    # Default arrival_rate of 0.7 keeps utilisation at ~88% — near-critical, so
    # queues are visible but the system is not yet overwhelmed.
    # Increase to 1.0+ to see WIP grow unboundedly (overloaded system).
    "arrival_rate": 0.7,
    "arrival_distribution": "exponential",
    "processing_times": [2.0, 8.0, 5.0],   # wide spread highlights SPT vs FIFO
    # qualification_matrix[tool][product] — which tools can run which products
    "qualification_matrix": [
        [True,  True,  False],   # Tool 0: qualified for products 0 and 1
        [True,  False, True],    # Tool 1: qualified for products 0 and 2
        [False, True,  True],    # Tool 2: qualified for products 1 and 2
        [True,  True,  True],    # Tool 3: fully qualified (all products)
    ],
    "dispatching_rule": "fifo",
    "sim_duration": 200.0,
    "snapshot_interval": 1.0,
    "random_seed": 42,
}

# ---------------------------------------------------------------------------
# Pedagogical description shown in the UI
# ---------------------------------------------------------------------------

CONCEPT_TITLE = "Load Balancing at a Toolset with Cross-Qualification"

CONCEPT_EXPLAINER = """
**What is this demonstrating?**

In semiconductor fabrication (and discrete manufacturing generally), a *toolset*
is a group of parallel machines that can each process certain product types.
Not every tool can run every product — this is called *cross-qualification*.

**System capacity**

With 4 tools and average processing time of 5 time units, this toolset can
process at most **0.8 lots per time unit** (4 ÷ 5).

- Arrival rate **< 0.8**: System is under capacity — queues stay small and WIP stays low.
- Arrival rate **≈ 0.8**: Near-critical — queues build slowly, WIP grows gradually.
- Arrival rate **> 0.8**: Overloaded — WIP grows without bound. Try 1.0–1.5 to see this clearly.

**What dispatching rules change**

Even when overloaded, the dispatching rule determines *which* lots wait longest
and *how efficiently* tools are used:

1. **FIFO** — Simple and fair, but ignores processing time differences.
2. **Least-Loaded-Tool** — Spreads work across tools to prevent hot spots.
3. **Random-Qualified-Tool** — Stochastic; shows how much variance dispatching introduces.
4. **Optimised (SPT)** — Shortest Processing Time: clears fast jobs first, minimising
   average queue time — but can starve slow (Product 1, pt=8) jobs.
5. **MIP-Optimized** — Multi-objective: balances processing time, load, and queue age.

**Cross-qualification effects**

Uncheck some tool-product pairs in the qualification matrix and watch WIP spike
for the restricted products. This mirrors real fab constraints where tool
qualification is expensive and slow to change.

**Key insight**

Even a small change in dispatching rule or qualification coverage can shift
average queue time by 20–50%. This is why factory physics and scheduling
strategy matter enormously in high-mix semiconductor fabs.
"""

# ---------------------------------------------------------------------------
# Validation bounds (used by the API layer)
# ---------------------------------------------------------------------------

BOUNDS = {
    "num_tools":      (1, 10),
    "num_products":   (1, 8),
    "arrival_rate":   (0.01, 10.0),
    "sim_duration":   (10.0, 5000.0),   # allow longer runs to observe WIP buildup
    "snapshot_interval": (0.5, 20.0),   # allow coarser snapshots for long runs
    "processing_time_min": 0.1,
    "processing_time_max": 100.0,
}
