"""
Simulation data models — pure data classes with no SimPy dependency.
These are shared between the simulation core, scheduling engine, and API layer.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Lot:
    """Represents a manufacturing lot (batch of wafers / work item)."""
    lot_id: str
    product_id: int          # index into the product list
    arrival_time: float      # simulation time when lot arrived at toolset queue
    start_time: Optional[float] = None   # when processing began
    finish_time: Optional[float] = None  # when processing completed
    assigned_tool: Optional[int] = None  # tool index that processed this lot

    @property
    def queue_time(self) -> float:
        """Time spent waiting in queue before processing started."""
        if self.start_time is None:
            return 0.0
        return self.start_time - self.arrival_time

    @property
    def cycle_time(self) -> float:
        """Total time from arrival to completion."""
        if self.finish_time is None or self.start_time is None:
            return 0.0
        return self.finish_time - self.arrival_time


@dataclass
class MetricSnapshot:
    """A single time-stamped observation of key simulation metrics."""
    time: float
    wip: int                      # lots currently in queue + being processed
    cumulative_moves: int         # total lots completed so far
    cumulative_queue_time: float  # sum of queue times for all completed lots
    tool_utilisation: list[float] # fraction busy per tool [0..1]


@dataclass
class SimulationResult:
    """Full result returned by a simulation run."""
    snapshots: list[MetricSnapshot]
    completed_lots: list[Lot]
    total_lots_arrived: int
    total_lots_completed: int
    mean_queue_time: float
    mean_cycle_time: float
    tool_utilisation: list[float]  # final utilisation per tool
