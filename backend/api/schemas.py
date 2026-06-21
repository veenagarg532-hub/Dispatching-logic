"""
Pydantic request/response schemas for the FastAPI layer.
Validation logic lives here, keeping the simulation core free of HTTP concerns.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, model_validator
from typing import Optional

from scenarios.load_balancing import BOUNDS


class SimulationRequest(BaseModel):
    """Input payload for a simulation run."""

    num_tools: int = Field(
        default=4,
        ge=BOUNDS["num_tools"][0],
        le=BOUNDS["num_tools"][1],
        description="Number of parallel tools in the toolset",
    )
    num_products: int = Field(
        default=3,
        ge=BOUNDS["num_products"][0],
        le=BOUNDS["num_products"][1],
        description="Number of distinct product types",
    )
    arrival_rate: float = Field(
        default=0.8,
        ge=BOUNDS["arrival_rate"][0],
        le=BOUNDS["arrival_rate"][1],
        description="Mean lot arrival rate (lots per time unit)",
    )
    arrival_distribution: str = Field(
        default="exponential",
        description="Arrival distribution: 'exponential' or 'fixed'",
    )
    processing_times: list[float] = Field(
        default=[3.0, 5.0, 4.0],
        description="Processing time per product type (time units)",
    )
    qualification_matrix: list[list[bool]] = Field(
        default=[
            [True,  True,  False],
            [True,  False, True],
            [False, True,  True],
            [True,  True,  True],
        ],
        description="qualification_matrix[tool][product] — True if tool can process product",
    )
    dispatching_rule: str = Field(
        default="fifo",
        description="Dispatching strategy: fifo | least_loaded_tool | random_qualified_tool | optimised_spt",
    )
    dispatching_rules_to_compare: Optional[list[str]] = Field(
        default=None,
        description="Optional: List of dispatching rules to compare (for comparison mode)",
    )
    sim_duration: float = Field(
        default=200.0,
        ge=BOUNDS["sim_duration"][0],
        le=BOUNDS["sim_duration"][1],
        description="Total simulation duration (time units)",
    )
    snapshot_interval: float = Field(
        default=1.0,
        ge=BOUNDS["snapshot_interval"][0],
        le=BOUNDS["snapshot_interval"][1],
        description="Interval between metric snapshots (time units)",
    )
    random_seed: Optional[int] = Field(
        default=42,
        description="Random seed for reproducibility (null for random)",
    )

    @model_validator(mode="after")
    def validate_dimensions(self) -> "SimulationRequest":
        # processing_times must have one entry per product
        if len(self.processing_times) != self.num_products:
            raise ValueError(
                f"processing_times must have {self.num_products} entries "
                f"(one per product), got {len(self.processing_times)}"
            )
        # qualification_matrix must be [num_tools][num_products]
        if len(self.qualification_matrix) != self.num_tools:
            raise ValueError(
                f"qualification_matrix must have {self.num_tools} rows "
                f"(one per tool), got {len(self.qualification_matrix)}"
            )
        for i, row in enumerate(self.qualification_matrix):
            if len(row) != self.num_products:
                raise ValueError(
                    f"qualification_matrix row {i} must have {self.num_products} "
                    f"entries, got {len(row)}"
                )
        # Each tool must be qualified for at least one product
        for i, row in enumerate(self.qualification_matrix):
            if not any(row):
                raise ValueError(
                    f"Tool {i} has no qualified products — at least one must be True"
                )
        # Each product must be reachable by at least one tool
        for p in range(self.num_products):
            if not any(self.qualification_matrix[t][p] for t in range(self.num_tools)):
                raise ValueError(
                    f"Product {p} has no qualified tools — at least one tool must be True"
                )
        # Validate processing times bounds
        for i, pt in enumerate(self.processing_times):
            if pt < BOUNDS["processing_time_min"] or pt > BOUNDS["processing_time_max"]:
                raise ValueError(
                    f"processing_times[{i}]={pt} out of range "
                    f"[{BOUNDS['processing_time_min']}, {BOUNDS['processing_time_max']}]"
                )
        # Validate dispatching rule
        from simulation.scheduling import STRATEGIES
        if self.dispatching_rule not in STRATEGIES:
            raise ValueError(
                f"Unknown dispatching_rule '{self.dispatching_rule}'. "
                f"Valid options: {list(STRATEGIES.keys())}"
            )
        # Validate arrival distribution
        if self.arrival_distribution not in ("exponential", "fixed"):
            raise ValueError(
                "arrival_distribution must be 'exponential' or 'fixed'"
            )
        return self


class MetricSnapshotOut(BaseModel):
    time: float
    wip: int
    cumulative_moves: int
    cumulative_queue_time: float
    tool_utilisation: list[float]


class SimulationResponse(BaseModel):
    """Output payload from a simulation run."""
    dispatching_rule: str
    snapshots: list[MetricSnapshotOut]
    total_lots_arrived: int
    total_lots_completed: int
    mean_queue_time: float
    mean_cycle_time: float
    tool_utilisation: list[float]


class ScenarioInfoResponse(BaseModel):
    """Metadata about the available scenario."""
    concept_title: str
    concept_explainer: str
    default_config: dict
    dispatching_rules: list[str]
    arrival_distributions: list[str]
