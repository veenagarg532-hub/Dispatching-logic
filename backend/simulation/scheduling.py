"""
Scheduling engine — decides which tool processes the next lot from the queue.

This module is intentionally decoupled from SimPy. It receives plain Python
data structures and returns a (lot_index, tool_index) decision. Adding a new
dispatching strategy requires only adding a new function and registering it in
STRATEGIES — no changes to the simulation core are needed.
"""
from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Lot

try:
    import pulp
    MIP_AVAILABLE = True
except ImportError:
    MIP_AVAILABLE = False


# ---------------------------------------------------------------------------
# Strategy implementations
# ---------------------------------------------------------------------------

def _fifo(
    queue: list["Lot"],
    tool_busy: list[bool],
    qualification_matrix: list[list[bool]],
    processing_times: list[float],
    tool_load: list[float] | None = None,
) -> tuple[int, int] | None:
    """
    First-In-First-Out: pick the oldest lot that has at least one free,
    qualified tool, then assign it to the first available qualified tool.
    """
    for lot_idx, lot in enumerate(queue):
        for tool_idx, busy in enumerate(tool_busy):
            if not busy and qualification_matrix[tool_idx][lot.product_id]:
                return lot_idx, tool_idx
    return None


def _least_loaded_tool(
    queue: list["Lot"],
    tool_busy: list[bool],
    qualification_matrix: list[list[bool]],
    processing_times: list[float],
    tool_load: list[float] | None = None,
) -> tuple[int, int] | None:
    """
    Least-Loaded-Tool: Pick the first lot in queue and assign it to the
    tool with the LEAST accumulated busy time among free qualified tools.
    This genuinely balances load across tools.
    """
    if not queue or tool_load is None:
        # Fallback to FIFO if no load info
        for lot_idx, lot in enumerate(queue):
            for tool_idx, busy in enumerate(tool_busy):
                if not busy and qualification_matrix[tool_idx][lot.product_id]:
                    return lot_idx, tool_idx
        return None
    
    # Take the first lot (FIFO order for lot selection)
    lot = queue[0]
    lot_idx = 0
    
    # Find all free qualified tools for this lot
    free_qualified_tools = [
        t for t, busy in enumerate(tool_busy)
        if not busy and qualification_matrix[t][lot.product_id]
    ]
    
    if not free_qualified_tools:
        return None
    
    # Assign to the tool with LEAST accumulated busy time
    tool_idx = min(free_qualified_tools, key=lambda t: tool_load[t])
    return (lot_idx, tool_idx)


def _random_qualified_tool(
    queue: list["Lot"],
    tool_busy: list[bool],
    qualification_matrix: list[list[bool]],
    processing_times: list[float],
    tool_load: list[float] | None = None,
) -> tuple[int, int] | None:
    """
    Random-Qualified-Tool: pick a random dispatchable (lot, tool) pair.
    """
    candidates: list[tuple[int, int]] = []
    for lot_idx, lot in enumerate(queue):
        for tool_idx, busy in enumerate(tool_busy):
            if not busy and qualification_matrix[tool_idx][lot.product_id]:
                candidates.append((lot_idx, tool_idx))
    if not candidates:
        return None
    return random.choice(candidates)


def _shortest_processing_time(
    queue: list["Lot"],
    tool_busy: list[bool],
    qualification_matrix: list[list[bool]],
    processing_times: list[float],
    tool_load: list[float] | None = None,
) -> tuple[int, int] | None:
    """
    Optimised (SPT — Shortest Processing Time): among all dispatchable pairs,
    choose the lot with the shortest processing time on its assigned tool.
    Tie-break by earliest arrival (FIFO).
    """
    best: tuple[int, int] | None = None
    best_pt = float("inf")
    for lot_idx, lot in enumerate(queue):
        for tool_idx, busy in enumerate(tool_busy):
            if not busy and qualification_matrix[tool_idx][lot.product_id]:
                pt = processing_times[lot.product_id]
                if pt < best_pt:
                    best_pt = pt
                    best = (lot_idx, tool_idx)
    return best


def _mip_optimized(
    queue: list["Lot"],
    tool_busy: list[bool],
    qualification_matrix: list[list[bool]],
    processing_times: list[float],
    tool_load: list[float] | None = None,
) -> tuple[int, int] | None:
    """
    MIP-Optimized: Uses Mixed Integer Programming to find the optimal assignment
    that minimizes total weighted cost considering:
    1. Processing time (minimize)
    2. Load balancing (balance tool utilization)
    3. Queue position (prioritize older lots)
    
    If MIP solver is unavailable or fails, falls back to a hybrid heuristic
    that combines SPT with load balancing.
    """
    # If MIP not available, use hybrid heuristic
    if not MIP_AVAILABLE:
        return _hybrid_heuristic(queue, tool_busy, qualification_matrix, processing_times, tool_load)
    
    if not queue or tool_load is None:
        return _hybrid_heuristic(queue, tool_busy, qualification_matrix, processing_times, tool_load)
    
    # Only optimize if we have multiple lots in queue
    if len(queue) <= 1:
        return _shortest_processing_time(queue, tool_busy, qualification_matrix, processing_times, tool_load)
    
    # Limit optimization window for performance
    MAX_LOTS_TO_OPTIMIZE = min(10, len(queue))
    lots_to_consider = queue[:MAX_LOTS_TO_OPTIMIZE]
    
    # Get free tools
    free_tools = [t for t, busy in enumerate(tool_busy) if not busy]
    if not free_tools:
        return None
    
    if len(free_tools) == 1:
        return _shortest_processing_time(queue, tool_busy, qualification_matrix, processing_times, tool_load)
    
    try:
        # Create MIP problem
        prob = pulp.LpProblem("ToolAssignment", pulp.LpMinimize)
        
        # Decision variables
        x = {}
        for lot_idx, lot in enumerate(lots_to_consider):
            for tool_idx in free_tools:
                if qualification_matrix[tool_idx][lot.product_id]:
                    x[(lot_idx, tool_idx)] = pulp.LpVariable(
                        f"x_{lot_idx}_{tool_idx}", 
                        cat='Binary'
                    )
        
        if not x:
            return None
        
        # Normalize tool loads
        max_load = max(tool_load) if max(tool_load) > 0 else 1.0
        normalized_load = [load / max_load for load in tool_load]
        
        # Objective function
        objective = []
        for (lot_idx, tool_idx), var in x.items():
            lot = lots_to_consider[lot_idx]
            pt = processing_times[lot.product_id]
            
            max_pt = max(processing_times)
            pt_cost = pt / max_pt
            load_cost = normalized_load[tool_idx]
            queue_position_cost = lot_idx / len(lots_to_consider)
            
            total_cost = (
                0.4 * pt_cost +
                0.4 * load_cost +
                0.2 * queue_position_cost
            )
            objective.append(total_cost * var)
        
        prob += pulp.lpSum(objective), "TotalCost"
        
        # Constraints
        for lot_idx in range(len(lots_to_consider)):
            lot_vars = [var for (l, t), var in x.items() if l == lot_idx]
            if lot_vars:
                prob += pulp.lpSum(lot_vars) <= 1, f"Lot_{lot_idx}_assignment"
        
        for tool_idx in free_tools:
            tool_vars = [var for (l, t), var in x.items() if t == tool_idx]
            if tool_vars:
                prob += pulp.lpSum(tool_vars) <= 1, f"Tool_{tool_idx}_assignment"
        
        # Solve with fallback
        solved = False
        try:
            status = prob.solve(pulp.getSolver('PULP_CBC_CMD', msg=0))
            if prob.status == pulp.LpStatusOptimal:
                solved = True
        except Exception:
            try:
                status = prob.solve()
                if prob.status == pulp.LpStatusOptimal:
                    solved = True
            except Exception:
                pass
        
        if not solved or prob.status != pulp.LpStatusOptimal:
            return _hybrid_heuristic(queue, tool_busy, qualification_matrix, processing_times, tool_load)
        
        # Extract solution
        best_assignment = None
        best_lot_priority = float('inf')
        
        for (lot_idx, tool_idx), var in x.items():
            if var.varValue and var.varValue > 0.5:
                if lot_idx < best_lot_priority:
                    best_lot_priority = lot_idx
                    best_assignment = (lot_idx, tool_idx)
        
        return best_assignment if best_assignment else _hybrid_heuristic(queue, tool_busy, qualification_matrix, processing_times, tool_load)
    
    except Exception:
        # Fallback to hybrid heuristic on any error
        return _hybrid_heuristic(queue, tool_busy, qualification_matrix, processing_times, tool_load)


def _hybrid_heuristic(
    queue: list["Lot"],
    tool_busy: list[bool],
    qualification_matrix: list[list[bool]],
    processing_times: list[float],
    tool_load: list[float] | None = None,
) -> tuple[int, int] | None:
    """
    Hybrid heuristic that mimics MIP optimization without requiring a solver.
    Evaluates all dispatchable (lot, tool) pairs using a weighted scoring function:
    - 40% processing time (shorter is better)
    - 40% load balancing (less loaded tool is better)
    - 20% queue position (older lot is better)
    
    This provides near-optimal results without solver dependency.
    """
    if not queue:
        return None
    
    # Default load if not provided
    if tool_load is None:
        tool_load = [0.0] * len(tool_busy)
    
    # Normalize factors
    max_pt = max(processing_times) if processing_times else 1.0
    max_load = max(tool_load) if max(tool_load) > 0 else 1.0
    queue_size = len(queue)
    
    # Evaluate all dispatchable pairs
    best_score = float('inf')
    best_pair = None
    
    for lot_idx, lot in enumerate(queue):
        for tool_idx, busy in enumerate(tool_busy):
            if not busy and qualification_matrix[tool_idx][lot.product_id]:
                # Calculate weighted cost
                pt_cost = processing_times[lot.product_id] / max_pt
                load_cost = tool_load[tool_idx] / max_load
                queue_cost = lot_idx / queue_size if queue_size > 1 else 0.0
                
                total_cost = (
                    0.4 * pt_cost +      # Favor short processing times
                    0.4 * load_cost +    # Favor less loaded tools
                    0.2 * queue_cost     # Favor older lots
                )
                
                # Update best if this is better
                if total_cost < best_score:
                    best_score = total_cost
                    best_pair = (lot_idx, tool_idx)
    
    return best_pair


# ---------------------------------------------------------------------------
# Public registry
# ---------------------------------------------------------------------------

STRATEGIES: dict[str, callable] = {
    "fifo": _fifo,
    "least_loaded_tool": _least_loaded_tool,
    "random_qualified_tool": _random_qualified_tool,
    "optimised_spt": _shortest_processing_time,
    "mip_optimized": _mip_optimized,
}


def dispatch(
    strategy: str,
    queue: list["Lot"],
    tool_busy: list[bool],
    qualification_matrix: list[list[bool]],
    processing_times: list[float],
    tool_load: list[float] | None = None,
) -> tuple[int, int] | None:
    """
    Public entry point for the scheduling engine.

    Returns (lot_index_in_queue, tool_index) or None if nothing can be
    dispatched right now.
    """
    fn = STRATEGIES.get(strategy)
    if fn is None:
        raise ValueError(
            f"Unknown dispatching strategy '{strategy}'. "
            f"Available: {list(STRATEGIES.keys())}"
        )
    return fn(queue, tool_busy, qualification_matrix, processing_times, tool_load)
