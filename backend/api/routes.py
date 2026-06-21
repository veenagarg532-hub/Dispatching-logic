"""
FastAPI route definitions.

Two endpoints:
  GET  /api/scenario   — returns default config and pedagogical metadata
  POST /api/simulate   — runs a simulation and returns results
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import SimulationRequest, SimulationResponse, ScenarioInfoResponse, MetricSnapshotOut
from simulation.engine import run_simulation
from simulation.scheduling import STRATEGIES
from scenarios.load_balancing import (
    DEFAULT_CONFIG,
    CONCEPT_TITLE,
    CONCEPT_EXPLAINER,
)

router = APIRouter(prefix="/api")


@router.get("/scenario", response_model=ScenarioInfoResponse)
def get_scenario_info():
    """Return the default configuration and pedagogical description."""
    return ScenarioInfoResponse(
        concept_title=CONCEPT_TITLE,
        concept_explainer=CONCEPT_EXPLAINER,
        default_config=DEFAULT_CONFIG,
        dispatching_rules=list(STRATEGIES.keys()),
        arrival_distributions=["exponential", "fixed"],
    )


@router.post("/simulate", response_model=SimulationResponse)
def run_simulation_endpoint(request: SimulationRequest):
    """
    Execute a discrete-event simulation run and return metric time-series
    plus summary statistics.
    """
    try:
        config = request.model_dump()
        result = run_simulation(config)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    snapshots_out = [
        MetricSnapshotOut(
            time=s.time,
            wip=s.wip,
            cumulative_moves=s.cumulative_moves,
            cumulative_queue_time=s.cumulative_queue_time,
            tool_utilisation=s.tool_utilisation,
        )
        for s in result.snapshots
    ]

    return SimulationResponse(
        dispatching_rule=config["dispatching_rule"],
        snapshots=snapshots_out,
        total_lots_arrived=result.total_lots_arrived,
        total_lots_completed=result.total_lots_completed,
        mean_queue_time=round(result.mean_queue_time, 4),
        mean_cycle_time=round(result.mean_cycle_time, 4),
        tool_utilisation=[round(u, 4) for u in result.tool_utilisation],
    )


@router.post("/simulate/compare")
def run_comparison_endpoint(request: SimulationRequest):
    """
    Execute multiple simulations with different dispatching rules and return
    results for side-by-side comparison.
    """
    try:
        # Get the base config
        base_config = request.model_dump()
        
        # Get selected strategies (comma-separated string or list)
        strategies = base_config.get("dispatching_rules_to_compare", [])
        if isinstance(strategies, str):
            strategies = [s.strip() for s in strategies.split(",")]
        
        if not strategies:
            # Fallback to single strategy if none specified
            strategies = [base_config["dispatching_rule"]]
        
        # Run simulation for each strategy
        results = []
        for strategy in strategies:
            config = base_config.copy()
            config["dispatching_rule"] = strategy
            result = run_simulation(config)
            
            snapshots_out = [
                MetricSnapshotOut(
                    time=s.time,
                    wip=s.wip,
                    cumulative_moves=s.cumulative_moves,
                    cumulative_queue_time=s.cumulative_queue_time,
                    tool_utilisation=s.tool_utilisation,
                )
                for s in result.snapshots
            ]
            
            results.append({
                "dispatching_rule": strategy,
                "snapshots": snapshots_out,
                "total_lots_arrived": result.total_lots_arrived,
                "total_lots_completed": result.total_lots_completed,
                "mean_queue_time": round(result.mean_queue_time, 4),
                "mean_cycle_time": round(result.mean_cycle_time, 4),
                "tool_utilisation": [round(u, 4) for u in result.tool_utilisation],
            })
        
        return {"results": results}
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
