"""
Shared fixtures for the test suite.

All fixtures that produce simulation configs, Lot objects, or queue states
that are needed by more than one test module live here.
"""
from __future__ import annotations

import pytest
from simulation.models import Lot


# ---------------------------------------------------------------------------
# Simulation config factories
# ---------------------------------------------------------------------------

@pytest.fixture
def base_config() -> dict:
    """
    A fully-specified, deterministic simulation config used as a baseline.

    System capacity: 4 tools / avg_pt(5.0) = 0.8 lots/tu.
    At arrival_rate=0.5 the system is under-loaded (~62% utilisation).
    Use this for tests that need a stable, non-exploding run.
    """
    return {
        "num_tools": 4,
        "num_products": 3,
        "arrival_rate": 0.5,
        "arrival_distribution": "exponential",
        "processing_times": [2.0, 8.0, 5.0],
        "qualification_matrix": [
            [True,  True,  False],
            [True,  False, True],
            [False, True,  True],
            [True,  True,  True],
        ],
        "dispatching_rule": "fifo",
        "sim_duration": 100.0,
        "snapshot_interval": 1.0,
        "random_seed": 42,
    }


@pytest.fixture
def overloaded_config(base_config) -> dict:
    """
    Same as base_config but with arrival_rate=1.5 (188% of capacity).
    WIP should grow unboundedly over time.
    """
    return {**base_config, "arrival_rate": 1.5, "sim_duration": 200.0}


@pytest.fixture
def single_tool_config() -> dict:
    """
    Simplest possible config: 1 tool, 1 product, deterministic arrivals.
    Makes hand-calculation of expected outcomes trivial.
    """
    return {
        "num_tools": 1,
        "num_products": 1,
        "arrival_rate": 0.1,           # fixed IAT = 10 tu
        "arrival_distribution": "fixed",
        "processing_times": [3.0],     # tool finishes in 3 tu, idle 7 tu per cycle
        "qualification_matrix": [[True]],
        "dispatching_rule": "fifo",
        "sim_duration": 50.0,
        "snapshot_interval": 1.0,
        "random_seed": 0,
    }


# ---------------------------------------------------------------------------
# Lot / queue helpers
# ---------------------------------------------------------------------------

def make_lot(lot_id: str, product_id: int, arrival_time: float = 0.0) -> Lot:
    """Convenience constructor for Lot objects in scheduling tests."""
    return Lot(lot_id=lot_id, product_id=product_id, arrival_time=arrival_time)


@pytest.fixture
def three_lot_queue() -> list[Lot]:
    """
    A queue with one lot of each product type (products 0, 1, 2) arriving in order.
    Useful for checking FIFO ordering and SPT product selection.
    """
    return [
        make_lot("LOT-000", product_id=0, arrival_time=1.0),
        make_lot("LOT-001", product_id=1, arrival_time=2.0),
        make_lot("LOT-002", product_id=2, arrival_time=3.0),
    ]


@pytest.fixture
def four_tool_state():
    """
    Four-tool state where tools 0 and 2 are free, tools 1 and 3 are busy.
    Paired with the default 3-product qualification matrix:
        Tool 0: qualifies P0, P1
        Tool 1: qualifies P0, P2
        Tool 2: qualifies P1, P2
        Tool 3: qualifies P0, P1, P2
    """
    tool_busy          = [False, True, False, True]
    qualification_matrix = [
        [True,  True,  False],
        [True,  False, True],
        [False, True,  True],
        [True,  True,  True],
    ]
    processing_times   = [2.0, 8.0, 5.0]
    tool_load          = [10.0, 20.0, 5.0, 30.0]
    return tool_busy, qualification_matrix, processing_times, tool_load


# ---------------------------------------------------------------------------
# FastAPI TestClient fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def client():
    """
    A FastAPI TestClient for the full application.
    Session-scoped so the app is only instantiated once per pytest run.
    """
    from fastapi.testclient import TestClient
    from main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture
def default_api_payload() -> dict:
    """
    A minimal valid POST body for /api/simulate that matches the schema defaults.
    """
    return {
        "num_tools": 4,
        "num_products": 3,
        "arrival_rate": 0.5,
        "arrival_distribution": "exponential",
        "processing_times": [2.0, 8.0, 5.0],
        "qualification_matrix": [
            [True,  True,  False],
            [True,  False, True],
            [False, True,  True],
            [True,  True,  True],
        ],
        "dispatching_rule": "fifo",
        "sim_duration": 50.0,
        "snapshot_interval": 1.0,
        "random_seed": 42,
    }
