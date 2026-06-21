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


# ---------------------------------------------------------------------------
# Strategy implementations
# ---------------------------------------------------------------------------

def _fifo(
    queue: list["Lot"],
    tool_busy: list[bool],
    qualification_matrix: list[list[bool]],
    processing_times: list[float],
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
) -> tuple[int, int] | None:
    """
    Least-Loaded-Tool: among all (lot, tool) pairs that are ready, prefer the
    tool that is currently free (all free tools are equally 'least loaded' in
    a binary busy/free model; tie-break by tool index).
    Picks the first lot in queue that can run on any free tool.
    """
    # Count free tools per product to find the lot with the most options
    best: tuple[int, int] | None = None
    best_free_count = -1
    for lot_idx, lot in enumerate(queue):
        free_qualified = [
            t for t, busy in enumerate(tool_busy)
            if not busy and qualification_matrix[t][lot.product_id]
        ]
        if free_qualified and len(free_qualified) > best_free_count:
            best_free_count = len(free_qualified)
            best = (lot_idx, free_qualified[0])
    return best


def _random_qualified_tool(
    queue: list["Lot"],
    tool_busy: list[bool],
    qualification_matrix: list[list[bool]],
    processing_times: list[float],
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


# ---------------------------------------------------------------------------
# Public registry
# ---------------------------------------------------------------------------

STRATEGIES: dict[str, callable] = {
    "fifo": _fifo,
    "least_loaded_tool": _least_loaded_tool,
    "random_qualified_tool": _random_qualified_tool,
    "optimised_spt": _shortest_processing_time,
}


def dispatch(
    strategy: str,
    queue: list["Lot"],
    tool_busy: list[bool],
    qualification_matrix: list[list[bool]],
    processing_times: list[float],
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
    return fn(queue, tool_busy, qualification_matrix, processing_times)
