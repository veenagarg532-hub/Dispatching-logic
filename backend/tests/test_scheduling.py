"""
Section B & C — Dispatch strategy tests.

All strategy functions are pure Python (no SimPy). They receive plain data
structures and return (lot_idx, tool_idx) | None.  Testing them in isolation
gives the highest signal-to-noise ratio of anything in this codebase.

Structure:
  TestSharedContract       — B0: invariants every strategy must satisfy
  TestFIFO                 — B: fifo-specific behavioral assertions
  TestSPT                  — B: optimised_spt-specific assertions
  TestLeastLoaded          — B: least_loaded_tool-specific assertions
  TestRandom               — B: random_qualified_tool-specific assertions
  TestDispatchRegistry     — B: dispatch() public entry-point
  TestMIPOptimized         — C: full MIP/hybrid branch coverage
  TestHybridHeuristic      — C-M7: scoring correctness
"""
from __future__ import annotations

import random
import pytest

from simulation.models import Lot
from simulation.scheduling import (
    _fifo,
    _least_loaded_tool,
    _random_qualified_tool,
    _shortest_processing_time,
    _mip_optimized,
    _hybrid_heuristic,
    dispatch,
    STRATEGIES,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_lot(lid: str, product_id: int, arrival: float = 0.0) -> Lot:
    return Lot(lot_id=lid, product_id=product_id, arrival_time=arrival)


def all_free(n: int) -> list[bool]:
    return [False] * n


def all_busy(n: int) -> list[bool]:
    return [True] * n


def all_qualified(num_tools: int, num_products: int) -> list[list[bool]]:
    return [[True] * num_products for _ in range(num_tools)]


# ---------------------------------------------------------------------------
# B0 — Shared contract (parameterised over all strategies)
# ---------------------------------------------------------------------------

ALL_STRATEGIES = list(STRATEGIES.keys())


def _valid_result(
    result,
    queue: list[Lot],
    tool_busy: list[bool],
    qualification_matrix: list[list[bool]],
) -> None:
    """Assert result satisfies B0a, B0b, B0d."""
    if result is None:
        return  # None is valid when nothing can be dispatched
    lot_idx, tool_idx = result
    assert 0 <= lot_idx < len(queue),            f"lot_idx={lot_idx} out of range"
    assert 0 <= tool_idx < len(tool_busy),       f"tool_idx={tool_idx} out of range"
    assert not tool_busy[tool_idx],              "B0a: assigned a BUSY tool"
    lot = queue[lot_idx]
    assert qualification_matrix[tool_idx][lot.product_id], \
        f"B0b: tool {tool_idx} not qualified for product {lot.product_id}"


class TestSharedContract:
    """B0a/b/c/d — every strategy must satisfy these."""

    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_result_is_valid_or_none(self, strategy):
        queue = [make_lot("L0", 0), make_lot("L1", 1), make_lot("L2", 2)]
        tool_busy = all_free(4)
        qmat = all_qualified(4, 3)
        pts = [2.0, 8.0, 5.0]
        tload = [0.0, 0.0, 0.0, 0.0]
        result = STRATEGIES[strategy](queue, tool_busy, qmat, pts, tload)
        _valid_result(result, queue, tool_busy, qmat)

    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_returns_none_when_queue_empty(self, strategy):
        result = STRATEGIES[strategy](
            [], all_free(4), all_qualified(4, 3), [2.0, 8.0, 5.0], [0.0]*4
        )
        assert result is None, f"{strategy}: expected None for empty queue"

    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_returns_none_when_all_tools_busy(self, strategy):
        queue = [make_lot("L0", 0)]
        result = STRATEGIES[strategy](
            queue, all_busy(4), all_qualified(4, 1), [3.0], [10.0]*4
        )
        assert result is None, f"{strategy}: expected None when all tools busy"

    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_returns_none_when_no_qualified_free_tool(self, strategy):
        """
        Single lot of product 0, but the only free tool doesn't qualify for it.
        Tool 0 qualifies only product 1. Tool 1 is busy.
        """
        queue = [make_lot("L0", product_id=0)]
        tool_busy = [False, True]
        qmat = [
            [False, True],   # tool 0: qualifies product 1 only
            [True,  True],   # tool 1: qualifies both — but it's busy
        ]
        pts = [3.0, 5.0]
        result = STRATEGIES[strategy](queue, tool_busy, qmat, pts, [0.0, 0.0])
        assert result is None

    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_never_assigns_busy_tool(self, strategy):
        """Stress: mix of busy/free tools, assert no busy tool is ever chosen."""
        queue = [make_lot(f"L{i}", i % 3) for i in range(5)]
        tool_busy = [False, True, False, True, False]
        qmat = all_qualified(5, 3)
        pts = [2.0, 8.0, 5.0]
        tload = [float(i * 5) for i in range(5)]
        for _ in range(20):   # run multiple times for random strategy
            result = STRATEGIES[strategy](queue, tool_busy, qmat, pts, tload)
            if result is not None:
                _, tool_idx = result
                assert not tool_busy[tool_idx], \
                    f"{strategy}: assigned busy tool {tool_idx}"


# ---------------------------------------------------------------------------
# B — FIFO
# ---------------------------------------------------------------------------

class TestFIFO:
    def test_picks_oldest_lot(self):
        """
        Lot 0 is product 1, qualified only by busy tool 1.
        Lot 1 is product 0, qualified by free tool 0.
        FIFO should skip lot 0 (no free qualified tool) and dispatch lot 1.
        """
        queue = [
            make_lot("L0", product_id=1),   # only tool 1 qualifies — but busy
            make_lot("L1", product_id=0),   # tool 0 qualifies and is free
        ]
        tool_busy = [False, True]
        qmat = [
            [True,  False],   # tool 0: only product 0
            [False, True],    # tool 1: only product 1
        ]
        result = _fifo(queue, tool_busy, qmat, [2.0, 8.0])
        assert result is not None
        lot_idx, tool_idx = result
        assert lot_idx == 1,   f"Expected lot_idx=1 (skipped lot 0), got {lot_idx}"
        assert tool_idx == 0,  f"Expected tool_idx=0, got {tool_idx}"

    def test_picks_first_available_tool(self):
        """Among multiple free qualified tools, FIFO picks the lowest-index one."""
        queue = [make_lot("L0", product_id=0)]
        tool_busy = [False, False, False]
        qmat = all_qualified(3, 1)
        result = _fifo(queue, tool_busy, qmat, [3.0])
        assert result == (0, 0), f"Expected (0,0), got {result}"

    def test_fifo_order_respected(self):
        """With all tools free and all qualified, first lot (idx 0) is always chosen."""
        queue = [make_lot(f"L{i}", 0) for i in range(5)]
        result = _fifo(queue, all_free(3), all_qualified(3, 1), [2.0])
        assert result[0] == 0, "FIFO should always pick lot index 0 when available"


# ---------------------------------------------------------------------------
# B — SPT (Shortest Processing Time)
# ---------------------------------------------------------------------------

class TestSPT:
    def test_picks_shortest_job(self):
        """
        Three products with times [5, 1, 9]. All tools free and fully qualified.
        SPT must pick the product-1 lot (pt=1).
        """
        queue = [
            make_lot("L0", product_id=0),   # pt=5
            make_lot("L1", product_id=1),   # pt=1  ← shortest
            make_lot("L2", product_id=2),   # pt=9
        ]
        pts = [5.0, 1.0, 9.0]
        result = _shortest_processing_time(queue, all_free(3), all_qualified(3, 3), pts)
        assert result is not None
        lot_idx, _ = result
        assert queue[lot_idx].product_id == 1, (
            f"SPT should pick product 1 (pt=1), got product {queue[lot_idx].product_id}"
        )

    def test_tiebreak_is_fifo(self):
        """When two lots have the same processing time, pick the earlier one (idx 0)."""
        queue = [
            make_lot("L0", product_id=0),
            make_lot("L1", product_id=0),
        ]
        pts = [3.0]
        result = _shortest_processing_time(queue, all_free(2), all_qualified(2, 1), pts)
        assert result[0] == 0, "SPT tiebreak should favor earlier queue position"

    def test_ignores_busy_tools(self):
        """SPT must not assign to a busy tool even if it's the only option."""
        queue = [make_lot("L0", 0)]
        tool_busy = [True, False]
        qmat = [[True], [True]]
        result = _shortest_processing_time(queue, tool_busy, qmat, [2.0])
        assert result is not None
        _, tool_idx = result
        assert tool_idx == 1


# ---------------------------------------------------------------------------
# B — Least-Loaded-Tool
# ---------------------------------------------------------------------------

class TestLeastLoaded:
    def test_picks_least_loaded_tool(self):
        """
        Three free tools with load [10, 2, 7]. All qualify product 0.
        Must assign to tool 1 (load=2, the minimum).
        """
        queue = [make_lot("L0", product_id=0)]
        tool_busy = [False, False, False]
        qmat = all_qualified(3, 1)
        pts = [3.0]
        tool_load = [10.0, 2.0, 7.0]
        result = _least_loaded_tool(queue, tool_busy, qmat, pts, tool_load)
        assert result is not None
        lot_idx, tool_idx = result
        assert tool_idx == 1, f"Expected tool 1 (least loaded), got tool {tool_idx}"

    def test_only_considers_head_of_queue(self):
        """
        DOCUMENTED BEHAVIOR (see QA plan B ⚠️ head-of-line blocking):
        least_loaded_tool only evaluates queue[0]. If queue[0]'s product has
        no free qualified tool, it returns None — even if a later lot could
        be dispatched.

        This test documents and encodes that behavior. If the product owner
        decides to change it (scan entire queue like FIFO), update this test.
        """
        # queue[0] is product 1 — only tool 1 qualifies, but tool 1 is busy.
        # queue[1] is product 0 — tool 0 is free and qualifies.
        queue = [
            make_lot("L0", product_id=1),
            make_lot("L1", product_id=0),
        ]
        tool_busy = [False, True]
        qmat = [
            [True,  False],   # tool 0: product 0 only
            [False, True],    # tool 1: product 1 only
        ]
        result = _least_loaded_tool(queue, tool_busy, qmat, [2.0, 8.0], [0.0, 5.0])
        # Documented behavior: returns None (head-of-line blocking)
        assert result is None, (
            "least_loaded_tool is expected to return None when queue[0] "
            "cannot be dispatched (head-of-line blocking). "
            "If this now scans the whole queue, update this test accordingly."
        )

    def test_falls_back_to_fifo_when_no_load_info(self):
        """When tool_load is None, should still return a valid dispatch."""
        queue = [make_lot("L0", 0)]
        result = _least_loaded_tool(queue, all_free(2), all_qualified(2, 1), [3.0], None)
        assert result is not None


# ---------------------------------------------------------------------------
# B — Random-Qualified-Tool
# ---------------------------------------------------------------------------

class TestRandom:
    def test_result_is_always_valid(self):
        """Every draw from random strategy must be a valid (B0a/B0b) pair."""
        queue = [make_lot(f"L{i}", i % 3) for i in range(4)]
        tool_busy = [False, True, False, False]
        qmat = all_qualified(4, 3)
        pts = [2.0, 8.0, 5.0]
        for _ in range(50):
            result = _random_qualified_tool(queue, tool_busy, qmat, pts)
            _valid_result(result, queue, tool_busy, qmat)

    def test_covers_multiple_pairs_over_many_draws(self):
        """
        With a seeded global RNG and a fixed candidate set, repeated draws
        should eventually cover more than one (lot, tool) pair.
        """
        random.seed(0)
        queue = [make_lot(f"L{i}", 0) for i in range(3)]
        tool_busy = [False, False, False]
        qmat = all_qualified(3, 1)
        pts = [2.0]
        seen = set()
        for _ in range(100):
            result = _random_qualified_tool(queue, tool_busy, qmat, pts)
            if result:
                seen.add(result)
        # 3 lots × 3 tools = 9 candidates; we expect to see at least 3 distinct ones
        assert len(seen) >= 3, (
            f"Random strategy covered only {len(seen)} distinct pairs in 100 draws"
        )


# ---------------------------------------------------------------------------
# B — dispatch() registry
# ---------------------------------------------------------------------------

class TestDispatchRegistry:
    def test_known_strategies_do_not_raise(self):
        queue = [make_lot("L0", 0)]
        for name in STRATEGIES:
            dispatch(name, queue, all_free(2), all_qualified(2, 1), [3.0], [0.0, 0.0])

    def test_unknown_strategy_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown dispatching strategy"):
            dispatch("does_not_exist", [], all_free(2), all_qualified(2, 1), [3.0])

    def test_error_message_lists_available_strategies(self):
        with pytest.raises(ValueError) as exc_info:
            dispatch("bad_name", [], all_free(2), all_qualified(2, 1), [3.0])
        msg = str(exc_info.value)
        for name in STRATEGIES:
            assert name in msg

    def test_all_five_strategies_registered(self):
        expected = {"fifo", "least_loaded_tool", "random_qualified_tool",
                    "optimised_spt", "mip_optimized"}
        assert expected == set(STRATEGIES.keys())


# ---------------------------------------------------------------------------
# C-MIP — _mip_optimized branch coverage
# ---------------------------------------------------------------------------

class TestMIPOptimized:
    """
    M1–M8 from the QA plan. Each test targets a specific branch in _mip_optimized.
    """

    def test_M1_valid_assignment_with_solver(self):
        """M1: With ≥2 free tools and ≥2 queued lots, returns a valid pair."""
        queue = [make_lot(f"L{i}", i % 3) for i in range(3)]
        result = _mip_optimized(
            queue, all_free(4), all_qualified(4, 3), [2.0, 8.0, 5.0], [0.0]*4
        )
        _valid_result(result, queue, all_free(4), all_qualified(4, 3))

    def test_M2_fallback_when_mip_unavailable(self, monkeypatch):
        """M2: When MIP_AVAILABLE is False, falls back to hybrid heuristic."""
        import simulation.scheduling as sched
        monkeypatch.setattr(sched, "MIP_AVAILABLE", False)
        queue = [make_lot("L0", 0), make_lot("L1", 1)]
        result = _mip_optimized(
            queue, all_free(4), all_qualified(4, 2), [2.0, 8.0], [0.0]*4
        )
        _valid_result(result, queue, all_free(4), all_qualified(4, 2))

    def test_M3_single_lot_delegates_to_spt(self):
        """M3: Single lot in queue → delegates to SPT behavior."""
        queue = [make_lot("L0", 0)]
        result = _mip_optimized(
            queue, all_free(3), all_qualified(3, 1), [5.0], [0.0]*3
        )
        spt_result = _shortest_processing_time(
            queue, all_free(3), all_qualified(3, 1), [5.0]
        )
        assert result == spt_result

    def test_M4_single_free_tool_delegates_to_spt(self):
        """M4: Exactly one free tool → delegates to SPT."""
        queue = [make_lot("L0", 0), make_lot("L1", 1)]
        tool_busy = [True, False, True]
        qmat = all_qualified(3, 2)
        pts = [2.0, 8.0]
        result = _mip_optimized(queue, tool_busy, qmat, pts, [5.0, 0.0, 5.0])
        _valid_result(result, queue, tool_busy, qmat)

    def test_M5_infeasible_returns_none(self):
        """M5: No qualified free tool for any lot → returns None."""
        queue = [make_lot("L0", product_id=1)]  # product 1
        tool_busy = [False, True]
        qmat = [
            [True,  False],   # tool 0 free but only qualifies product 0
            [False, True],    # tool 1 qualifies product 1 but is busy
        ]
        result = _mip_optimized(queue, tool_busy, qmat, [2.0, 8.0], [0.0, 10.0])
        assert result is None

    def test_M6_optimization_window_cap(self):
        """M6: With >10 lots, returned lot_idx must be < MAX_LOTS_TO_OPTIMIZE (10)."""
        queue = [make_lot(f"L{i}", 0) for i in range(15)]
        result = _mip_optimized(
            queue, all_free(4), all_qualified(4, 1), [3.0], [0.0]*4
        )
        if result is not None:
            lot_idx, _ = result
            assert lot_idx < 10, (
                f"MIP should only consider first 10 lots, but returned lot_idx={lot_idx}"
            )

    def test_M8_exception_in_solver_returns_valid_fallback(self, monkeypatch):
        """
        M8: Force an internal exception and assert the result is still a valid
        dispatch (not a crash). Simulates a broken solver environment.
        """
        import simulation.scheduling as sched

        original_hybrid = sched._hybrid_heuristic

        call_count = {"n": 0}

        def _raise_first_then_hybrid(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("Simulated solver crash")
            return original_hybrid(*args, **kwargs)

        # Force MIP_AVAILABLE so the try block runs
        monkeypatch.setattr(sched, "MIP_AVAILABLE", True)
        monkeypatch.setattr(sched, "_hybrid_heuristic", _raise_first_then_hybrid)

        queue = [make_lot("L0", 0), make_lot("L1", 1)]
        # Should not raise; exception is caught inside _mip_optimized
        try:
            result = _mip_optimized(
                queue, all_free(3), all_qualified(3, 2), [2.0, 8.0], [0.0]*3
            )
            # If it reaches here, it either returned a valid result or None
            if result is not None:
                _valid_result(result, queue, all_free(3), all_qualified(3, 2))
        except Exception as exc:
            pytest.fail(f"_mip_optimized raised an exception instead of handling it: {exc}")


# ---------------------------------------------------------------------------
# C-M7 — Hybrid heuristic scoring
# ---------------------------------------------------------------------------

class TestHybridHeuristic:
    def test_M7_weighted_minimum_is_chosen(self):
        """
        M7: Hand-craft a scenario where the weighted-minimum pair is known exactly.

        Setup:
          - 1 lot of product 0 (pt=2), 1 lot of product 1 (pt=8)
          - 2 free tools, loads [0, 10]
          - queue_size=2, so queue_cost for lot 0 = 0/2=0.0, lot 1 = 1/2=0.5
          - max_pt=8, max_load=10

        Costs:
          lot0 → tool0: 0.4*(2/8) + 0.4*(0/10) + 0.2*(0/2) = 0.1  + 0.0  + 0.0  = 0.10
          lot0 → tool1: 0.4*(2/8) + 0.4*(10/10)+ 0.2*(0/2) = 0.1  + 0.4  + 0.0  = 0.50
          lot1 → tool0: 0.4*(8/8) + 0.4*(0/10) + 0.2*(1/2) = 0.4  + 0.0  + 0.1  = 0.50
          lot1 → tool1: 0.4*(8/8) + 0.4*(10/10)+ 0.2*(1/2) = 0.4  + 0.4  + 0.1  = 0.90

        Minimum is lot0→tool0 with cost 0.10.
        """
        queue = [
            make_lot("L0", product_id=0),
            make_lot("L1", product_id=1),
        ]
        tool_busy = [False, False]
        qmat = all_qualified(2, 2)
        pts = [2.0, 8.0]
        tool_load = [0.0, 10.0]

        result = _hybrid_heuristic(queue, tool_busy, qmat, pts, tool_load)
        assert result == (0, 0), (
            f"Expected (lot0, tool0) with minimum cost 0.10, got {result}"
        )

    def test_all_equal_loads_prefers_shorter_job(self):
        """When all tool loads are equal, shorter pt wins."""
        queue = [
            make_lot("L0", product_id=0),   # pt=5
            make_lot("L1", product_id=1),   # pt=2  ← shorter
        ]
        tool_busy = [False, False]
        qmat = all_qualified(2, 2)
        pts = [5.0, 2.0]
        tool_load = [5.0, 5.0]

        result = _hybrid_heuristic(queue, tool_busy, qmat, pts, tool_load)
        assert result is not None
        lot_idx, _ = result
        assert queue[lot_idx].product_id == 1, (
            "With equal loads, hybrid should prefer the shorter-pt lot"
        )

    def test_returns_none_on_empty_queue(self):
        result = _hybrid_heuristic([], [False]*2, all_qualified(2, 1), [3.0], [0.0]*2)
        assert result is None
