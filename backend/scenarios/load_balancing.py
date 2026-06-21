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
    "arrival_rate": 0.8,           # lots per time unit
    "arrival_distribution": "exponential",
    "processing_times": [3.0, 5.0, 4.0],   # one per product (time units)
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

**The core tension**

When lots arrive faster than tools can process them, a queue builds up. How you
*dispatch* lots to tools has a large impact on:

- **WIP (Work-In-Process)**: how many lots are waiting or being processed at any moment.
- **Queue time**: how long a lot waits before a tool picks it up.
- **Tool utilisation**: what fraction of time each tool is actually busy.

**What to explore**

1. **FIFO** (First-In-First-Out) is simple and fair, but ignores tool availability
   and processing time differences.
2. **Least-Loaded-Tool** tries to spread work across tools, reducing idle time.
3. **Random-Qualified-Tool** introduces stochastic behaviour — useful to see how
   much variance dispatching rules can introduce.
4. **Optimised (SPT)** prioritises short jobs, minimising average queue time but
   potentially starving long jobs.

**Cross-qualification effects**

Restrict the qualification matrix (uncheck some tool-product pairs) and watch
WIP spike for the affected products. This mirrors real fab constraints where
tool qualification is expensive and time-consuming.

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
    "sim_duration":   (10.0, 2000.0),
    "snapshot_interval": (0.5, 10.0),
    "processing_time_min": 0.1,
    "processing_time_max": 100.0,
}
