"""
Section A — Simulation engine tests.

Covers: time advancement, snapshot ordering, determinism, conservation
invariants, processing-time honoring, no double-booking, and capacity
stability (WIP grows when overloaded, stays bounded when under-loaded).

All tests pass a fixed random_seed so outcomes are deterministic.
"""
from __future__ import annotations

import math
import pytest

from simulation.engine import run_simulation
from simulation.models import SimulationResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(config: dict) -> SimulationResult:
    """Thin wrapper so tests read cleanly."""
    return run_simulation(config)


def _busy_intervals(result: SimulationResult, tool_idx: int) -> list[tuple[float, float]]:
    """
    Return a sorted list of [start, finish) intervals for every completed
    lot that was processed on `tool_idx`.
    """
    intervals = [
        (lot.start_time, lot.finish_time)
        for lot in result.completed_lots
        if lot.assigned_tool == tool_idx
        and lot.start_time is not None
        and lot.finish_time is not None
    ]
    return sorted(intervals, key=lambda x: x[0])


# ---------------------------------------------------------------------------
# A1 — Time is bounded
# ---------------------------------------------------------------------------

class TestTimeBounded:
    def test_snapshot_times_within_duration(self, base_config):
        result = _run(base_config)
        duration = base_config["sim_duration"]
        for snap in result.snapshots:
            assert snap.time <= duration, (
                f"Snapshot at t={snap.time} exceeds sim_duration={duration}"
            )

    def test_lot_finish_times_within_duration(self, base_config):
        result = _run(base_config)
        duration = base_config["sim_duration"]
        for lot in result.completed_lots:
            assert lot.finish_time <= duration + 1e-9, (
                f"Lot {lot.lot_id} finished at {lot.finish_time} > {duration}"
            )


# ---------------------------------------------------------------------------
# A2 — Snapshots are ordered and evenly spaced
# ---------------------------------------------------------------------------

class TestSnapshotOrdering:
    def test_snapshots_strictly_increasing(self, base_config):
        result = _run(base_config)
        times = [s.time for s in result.snapshots]
        for i in range(1, len(times)):
            assert times[i] > times[i - 1], (
                f"Snapshot times not strictly increasing: {times[i-1]} → {times[i]}"
            )

    def test_snapshot_spacing_matches_interval(self, base_config):
        interval = base_config["snapshot_interval"]
        result = _run(base_config)
        times = [s.time for s in result.snapshots]
        # First snapshot is at t=0 (before any event), subsequent ones
        # should be spaced by snapshot_interval.
        for i in range(1, len(times)):
            gap = times[i] - times[i - 1]
            assert abs(gap - interval) < 1e-9, (
                f"Snapshot gap {gap} ≠ interval {interval} between "
                f"t={times[i-1]} and t={times[i]}"
            )

    def test_snapshot_count_matches_duration(self, base_config):
        result = _run(base_config)
        duration = base_config["sim_duration"]
        interval = base_config["snapshot_interval"]
        # We expect floor(duration/interval) + 1 snapshots (including t=0)
        expected = int(duration / interval) + 1
        # Allow ±1 for floating-point edge at the boundary
        assert abs(len(result.snapshots) - expected) <= 1, (
            f"Expected ~{expected} snapshots, got {len(result.snapshots)}"
        )


# ---------------------------------------------------------------------------
# A3 — Determinism: same seed → identical result
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_identical_results_same_seed(self, base_config):
        r1 = _run(base_config)
        r2 = _run(base_config)
        assert r1.total_lots_arrived  == r2.total_lots_arrived
        assert r1.total_lots_completed == r2.total_lots_completed
        assert r1.mean_queue_time == r2.mean_queue_time
        assert r1.mean_cycle_time == r2.mean_cycle_time
        assert len(r1.snapshots) == len(r2.snapshots)
        for s1, s2 in zip(r1.snapshots, r2.snapshots):
            assert s1.time == s2.time
            assert s1.wip  == s2.wip
            assert s1.cumulative_moves == s2.cumulative_moves

    def test_all_strategies_are_deterministic(self, base_config):
        from simulation.scheduling import STRATEGIES
        for strategy in STRATEGIES:
            if strategy == "random_qualified_tool":
                # NOTE (product owner Q4): random_qualified_tool uses the
                # *global* random module, not the seeded per-run RNG, so it is
                # NOT reproducible via random_seed alone.  Excluded here.
                # To fix: refactor _random_qualified_tool to accept the seeded
                # rng instance, or seed the global RNG in the test.
                continue
            cfg = {**base_config, "dispatching_rule": strategy}
            r1 = _run(cfg)
            r2 = _run(cfg)
            assert r1.total_lots_completed == r2.total_lots_completed, (
                f"Strategy '{strategy}' is not deterministic under same seed"
            )


# ---------------------------------------------------------------------------
# A4 — Seed sensitivity: different seeds → different patterns
# ---------------------------------------------------------------------------

class TestSeedSensitivity:
    def test_different_seeds_produce_different_arrivals(self, base_config):
        r1 = _run({**base_config, "random_seed": 1})
        r2 = _run({**base_config, "random_seed": 999})
        # Different Poisson processes should almost certainly produce
        # different total arrivals or different snapshot WIP patterns.
        wip1 = [s.wip for s in r1.snapshots]
        wip2 = [s.wip for s in r2.snapshots]
        assert wip1 != wip2 or r1.total_lots_arrived != r2.total_lots_arrived, (
            "Different seeds produced identical results — very unlikely unless broken"
        )


# ---------------------------------------------------------------------------
# A5 — Fixed vs exponential arrivals
# ---------------------------------------------------------------------------

class TestArrivalDistribution:
    def test_fixed_arrival_count_matches_rate(self, base_config):
        """With fixed inter-arrival time, lots arrive at precise multiples of 1/rate."""
        cfg = {
            **base_config,
            "arrival_distribution": "fixed",
            "arrival_rate": 0.2,   # IAT = 5 tu
            "sim_duration": 100.0,
        }
        result = _run(cfg)
        # Expected arrivals: floor(100 / 5) = 20 (first at t=5, last at t=100)
        expected = int(cfg["sim_duration"] * cfg["arrival_rate"])
        assert abs(result.total_lots_arrived - expected) <= 1, (
            f"Fixed arrivals: expected ~{expected}, got {result.total_lots_arrived}"
        )

    def test_fixed_arrivals_are_regularly_spaced(self, base_config):
        """Each lot's arrival_time should be a multiple of 1/rate."""
        rate = 0.5   # IAT = 2 tu
        cfg = {
            **base_config,
            # Keep num_tools=4 so qualification_matrix stays valid; just add
            # enough tools to avoid queuing (not needed for this test's assertion)
            "arrival_distribution": "fixed",
            "arrival_rate": rate,
            "sim_duration": 20.0,
            "random_seed": 0,
        }
        result = _run(cfg)
        iat = 1.0 / rate
        all_lots = result.completed_lots
        for lot in all_lots:
            # arrival_time should be a near-integer multiple of iat
            remainder = lot.arrival_time % iat
            assert remainder < 1e-9 or abs(remainder - iat) < 1e-9, (
                f"Lot {lot.lot_id} arrived at {lot.arrival_time}, not a multiple of {iat}"
            )


# ---------------------------------------------------------------------------
# A6 — Conservation: nothing is created or lost
# ---------------------------------------------------------------------------

class TestConservation:
    def test_completed_never_exceeds_arrived(self, base_config):
        result = _run(base_config)
        assert result.total_lots_completed <= result.total_lots_arrived

    def test_completed_count_matches_list_length(self, base_config):
        result = _run(base_config)
        assert result.total_lots_completed == len(result.completed_lots)

    def test_final_snapshot_moves_equals_completed(self, base_config):
        result = _run(base_config)
        final_moves = result.snapshots[-1].cumulative_moves
        assert final_moves == result.total_lots_completed, (
            f"Final cumulative_moves={final_moves} ≠ completed={result.total_lots_completed}"
        )

    def test_cumulative_queue_time_consistency(self, base_config):
        result = _run(base_config)
        sum_from_lots = sum(lot.queue_time for lot in result.completed_lots)
        final_from_snapshot = result.snapshots[-1].cumulative_queue_time
        assert abs(sum_from_lots - final_from_snapshot) < 1e-6, (
            f"Snapshot cumulative_queue_time={final_from_snapshot} ≠ "
            f"sum(lot.queue_time)={sum_from_lots}"
        )


# ---------------------------------------------------------------------------
# A7 — Processing time is honored
# ---------------------------------------------------------------------------

class TestProcessingTimes:
    def test_lot_duration_equals_processing_time(self, base_config):
        result = _run(base_config)
        pts = base_config["processing_times"]
        for lot in result.completed_lots:
            expected_pt = pts[lot.product_id]
            actual_pt = lot.finish_time - lot.start_time
            assert abs(actual_pt - expected_pt) < 1e-9, (
                f"Lot {lot.lot_id} (product {lot.product_id}): "
                f"expected pt={expected_pt}, got {actual_pt:.9f}"
            )


# ---------------------------------------------------------------------------
# A8 — No double-booking: a tool never runs two lots simultaneously
# ---------------------------------------------------------------------------

class TestNoDoubleBooking:
    def test_no_overlapping_intervals_per_tool(self, overloaded_config):
        """
        Under high load, the dispatcher runs frequently. Verify that no two
        completed lots on the same tool have overlapping [start, finish) intervals.
        This guards the tool_busy flag logic in dispatcher_process.
        """
        result = _run(overloaded_config)
        num_tools = overloaded_config["num_tools"]
        for t in range(num_tools):
            intervals = _busy_intervals(result, t)
            for i in range(1, len(intervals)):
                prev_end   = intervals[i - 1][1]
                curr_start = intervals[i][0]
                assert curr_start >= prev_end - 1e-9, (
                    f"Tool {t}: overlap detected — lot ending at {prev_end} "
                    f"and next lot starting at {curr_start}"
                )


# ---------------------------------------------------------------------------
# A9 — Queue time is non-negative
# ---------------------------------------------------------------------------

class TestQueueTime:
    def test_queue_time_non_negative(self, base_config):
        result = _run(base_config)
        for lot in result.completed_lots:
            assert lot.queue_time >= 0.0, (
                f"Lot {lot.lot_id} has negative queue_time={lot.queue_time}"
            )

    def test_queue_time_formula(self, base_config):
        """queue_time must equal start_time - arrival_time."""
        result = _run(base_config)
        for lot in result.completed_lots:
            expected = lot.start_time - lot.arrival_time
            assert abs(lot.queue_time - expected) < 1e-9


# ---------------------------------------------------------------------------
# A10 — Edge cases don't crash
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_very_low_arrival_rate(self, base_config):
        """Near-zero arrival rate: very few lots, possibly 0 completed."""
        cfg = {**base_config, "arrival_rate": 0.001, "sim_duration": 10.0}
        result = _run(cfg)
        assert result.total_lots_completed >= 0
        assert result.mean_queue_time == 0.0 or result.mean_queue_time >= 0.0

    def test_duration_shorter_than_one_processing_time(self, base_config):
        """sim_duration shorter than fastest processing time: 0 completions."""
        cfg = {
            **base_config,
            "arrival_rate": 10.0,
            "processing_times": [100.0, 100.0, 100.0],  # all lots take 100 tu
            "sim_duration": 10.0,                         # shorter than pt
        }
        result = _run(cfg)
        assert result.total_lots_completed == 0
        assert result.mean_queue_time == 0.0
        assert result.mean_cycle_time == 0.0

    def test_zero_completed_mean_stats_are_zero(self, base_config):
        """No divide-by-zero when nothing completes."""
        cfg = {
            **base_config,
            "arrival_rate": 0.001,
            "processing_times": [1000.0, 1000.0, 1000.0],
            "sim_duration": 10.0,
        }
        result = _run(cfg)
        assert result.mean_queue_time == 0.0
        assert result.mean_cycle_time == 0.0


# ---------------------------------------------------------------------------
# A11 — Capacity / stability: WIP trends
# ---------------------------------------------------------------------------

class TestCapacityStability:
    def test_wip_grows_when_overloaded(self, overloaded_config):
        """
        At 188% load, WIP must trend upward over the simulation.
        Compare the average WIP in the first 25% of time vs last 25%.
        """
        result = _run(overloaded_config)
        snaps = result.snapshots
        n = len(snaps)
        quarter = n // 4
        early_avg = sum(s.wip for s in snaps[:quarter]) / quarter
        late_avg  = sum(s.wip for s in snaps[-quarter:]) / quarter
        assert late_avg > early_avg, (
            f"Overloaded system: WIP should grow but early_avg={early_avg:.1f}, "
            f"late_avg={late_avg:.1f}"
        )

    def test_wip_stays_bounded_when_underloaded(self, base_config):
        """
        At 62% load, WIP should stay bounded (no runaway growth).
        Max WIP should be well below total_lots_arrived.
        """
        result = _run(base_config)
        max_wip = max(s.wip for s in result.snapshots)
        # In a stable under-loaded system, WIP should not exceed ~3x the
        # number of tools (a very loose upper bound to avoid false failures).
        upper_bound = base_config["num_tools"] * 3
        assert max_wip <= upper_bound, (
            f"Under-loaded system has unexpectedly high WIP={max_wip} "
            f"(bound={upper_bound})"
        )
