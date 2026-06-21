"""
Simulation core — discrete-event simulation engine built on SimPy.

Responsibilities:
  - Model lot arrivals (Poisson process or fixed inter-arrival time)
  - Maintain the toolset queue
  - Delegate dispatching decisions to the scheduling engine
  - Collect metric snapshots at configurable intervals
  - Return a SimulationResult

This module knows nothing about HTTP, FastAPI, or the frontend. It receives a
plain ScenarioConfig dict and returns a SimulationResult.
"""
from __future__ import annotations

import random
import simpy

from simulation.models import Lot, MetricSnapshot, SimulationResult
from simulation.scheduling import dispatch


# ---------------------------------------------------------------------------
# Internal simulation state (one instance per run)
# ---------------------------------------------------------------------------

class _ToolsetSimulation:
    def __init__(
        self,
        env: simpy.Environment,
        num_tools: int,
        num_products: int,
        processing_times: list[float],
        qualification_matrix: list[list[bool]],
        dispatching_rule: str,
        snapshot_interval: float,
        sim_duration: float,
    ):
        self.env = env
        self.num_tools = num_tools
        self.num_products = num_products
        self.processing_times = processing_times
        self.qualification_matrix = qualification_matrix  # [tool][product] -> bool
        self.dispatching_rule = dispatching_rule
        self.snapshot_interval = snapshot_interval
        self.sim_duration = sim_duration

        # State
        self.queue: list[Lot] = []
        self.tool_busy: list[bool] = [False] * num_tools
        self.tool_busy_time: list[float] = [0.0] * num_tools  # accumulated busy seconds

        # Metrics
        self.completed_lots: list[Lot] = []
        self.snapshots: list[MetricSnapshot] = []
        self.total_arrived = 0
        self.cumulative_moves = 0
        self.cumulative_queue_time = 0.0

        # Event used to wake the dispatcher when something changes
        self._dispatch_trigger = env.event()

    # ------------------------------------------------------------------
    # Processes
    # ------------------------------------------------------------------

    def arrival_process(
        self,
        arrival_rate: float,
        arrival_distribution: str,
        seed: int | None,
    ):
        """Generate lots and add them to the queue."""
        rng = random.Random(seed)
        lot_counter = 0
        while True:
            # Inter-arrival time
            if arrival_distribution == "exponential":
                iat = rng.expovariate(arrival_rate)
            else:  # fixed / deterministic
                iat = 1.0 / arrival_rate

            yield self.env.timeout(iat)

            product_id = rng.randint(0, self.num_products - 1)
            lot = Lot(
                lot_id=f"LOT-{lot_counter:05d}",
                product_id=product_id,
                arrival_time=self.env.now,
            )
            self.queue.append(lot)
            self.total_arrived += 1
            lot_counter += 1

            # Wake the dispatcher
            self._trigger_dispatch()

    def tool_process(self, tool_idx: int, lot: Lot):
        """Process a single lot on a specific tool."""
        lot.start_time = self.env.now
        lot.assigned_tool = tool_idx
        self.tool_busy[tool_idx] = True

        pt = self.processing_times[lot.product_id]
        yield self.env.timeout(pt)

        lot.finish_time = self.env.now
        self.tool_busy[tool_idx] = False
        self.tool_busy_time[tool_idx] += pt

        self.completed_lots.append(lot)
        self.cumulative_moves += 1
        self.cumulative_queue_time += lot.queue_time

        # Wake the dispatcher — a tool just freed up
        self._trigger_dispatch()

    def dispatcher_process(self):
        """
        Central dispatcher loop. Waits for a trigger event, then tries to
        assign lots to free tools until no more assignments are possible.
        """
        while True:
            yield self._dispatch_trigger
            # Reset trigger for next cycle
            self._dispatch_trigger = self.env.event()

            # Keep dispatching as long as assignments are possible
            while True:
                decision = dispatch(
                    self.dispatching_rule,
                    self.queue,
                    self.tool_busy,
                    self.qualification_matrix,
                    self.processing_times,
                )
                if decision is None:
                    break
                lot_idx, tool_idx = decision
                lot = self.queue.pop(lot_idx)
                self.env.process(self.tool_process(tool_idx, lot))

    def snapshot_process(self):
        """Periodically record metric snapshots."""
        while True:
            in_progress = sum(self.tool_busy)
            wip = len(self.queue) + in_progress
            utilisation = [
                self.tool_busy_time[t] / max(self.env.now, 1e-9)
                for t in range(self.num_tools)
            ]
            self.snapshots.append(MetricSnapshot(
                time=self.env.now,
                wip=wip,
                cumulative_moves=self.cumulative_moves,
                cumulative_queue_time=self.cumulative_queue_time,
                tool_utilisation=utilisation,
            ))
            yield self.env.timeout(self.snapshot_interval)

    def _trigger_dispatch(self):
        """Fire the dispatch trigger if it hasn't been fired yet."""
        if not self._dispatch_trigger.triggered:
            self._dispatch_trigger.succeed()


# ---------------------------------------------------------------------------
# Public run function
# ---------------------------------------------------------------------------

def run_simulation(config: dict) -> SimulationResult:
    """
    Execute a simulation run from a plain configuration dictionary.

    Expected config keys (all validated by the API layer before reaching here):
      num_tools            int   >= 1
      num_products         int   >= 1
      arrival_rate         float lots per time unit
      arrival_distribution str   "exponential" | "fixed"
      processing_times     list[float]  one per product
      qualification_matrix list[list[bool]]  [tool][product]
      dispatching_rule     str   see scheduling.STRATEGIES
      sim_duration         float total simulation time units
      snapshot_interval    float how often to record metrics (default 1.0)
      random_seed          int | None
    """
    env = simpy.Environment()

    num_tools: int = config["num_tools"]
    num_products: int = config["num_products"]
    processing_times: list[float] = config["processing_times"]
    qualification_matrix: list[list[bool]] = config["qualification_matrix"]
    dispatching_rule: str = config["dispatching_rule"]
    sim_duration: float = float(config["sim_duration"])
    arrival_rate: float = float(config["arrival_rate"])
    arrival_distribution: str = config.get("arrival_distribution", "exponential")
    snapshot_interval: float = float(config.get("snapshot_interval", 1.0))
    seed: int | None = config.get("random_seed", None)

    sim = _ToolsetSimulation(
        env=env,
        num_tools=num_tools,
        num_products=num_products,
        processing_times=processing_times,
        qualification_matrix=qualification_matrix,
        dispatching_rule=dispatching_rule,
        snapshot_interval=snapshot_interval,
        sim_duration=sim_duration,
    )

    # Register processes
    env.process(sim.arrival_process(arrival_rate, arrival_distribution, seed))
    env.process(sim.dispatcher_process())
    env.process(sim.snapshot_process())

    # Run
    env.run(until=sim_duration)

    # Final utilisation
    final_utilisation = [
        sim.tool_busy_time[t] / sim_duration
        for t in range(num_tools)
    ]

    # Aggregate stats
    completed = sim.completed_lots
    mean_queue = (
        sum(l.queue_time for l in completed) / len(completed)
        if completed else 0.0
    )
    mean_cycle = (
        sum(l.cycle_time for l in completed) / len(completed)
        if completed else 0.0
    )

    return SimulationResult(
        snapshots=sim.snapshots,
        completed_lots=completed,
        total_lots_arrived=sim.total_arrived,
        total_lots_completed=len(completed),
        mean_queue_time=mean_queue,
        mean_cycle_time=mean_cycle,
        tool_utilisation=final_utilisation,
    )
