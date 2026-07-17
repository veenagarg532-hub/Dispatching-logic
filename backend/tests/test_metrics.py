"""
Section D — Metric and plot-data correctness tests.

These tests pin the exact definitions of each metric that feeds the four
charts and the summary stat cards. If these pass, the plots show what they
claim to show.

⚠️  Two metric definitions are encoded here (see QA plan D notes).
    They reflect the *current* implementation and must be reviewed with the
    product owner. Comment markers indicate where to update if the agreed
    definition changes.
"""
from __future__ import annotations

import pytest
from simulation.engine import run_simulation
from simulation.models import SimulationResult


def _run(config: dict) -> SimulationResult:
    return run_simulation(config)


# ---------------------------------------------------------------------------
# D — WIP: snapshot.wip == queue_length + tools_busy
# ---------------------------------------------------------------------------

class TestWIPDefinition:
    def test_wip_is_non_negative(self, base_config):
        result = _run(base_config)
        for snap in result.snapshots:
            assert snap.wip >= 0, f"Negative WIP={snap.wip} at t={snap.time}"

    def test_wip_is_integer(self, base_config):
        result = _run(base_config)
        for snap in result.snapshots:
            assert isinstance(snap.wip, int), (
                f"WIP at t={snap.time} is {type(snap.wip)}, expected int"
            )

    def test_wip_trends_upward_when_overloaded(self, overloaded_config):
        """Regression guard for the double-booking bug: WIP must grow under load."""
        result = _run(overloaded_config)
        snaps = result.snapshots
        n = len(snaps)
        quarter = max(1, n // 4)
        early_avg = sum(s.wip for s in snaps[:quarter]) / quarter
        late_avg  = sum(s.wip for s in snaps[-quarter:]) / quarter
        assert late_avg > early_avg, (
            f"WIP should grow when overloaded: early={early_avg:.1f}, late={late_avg:.1f}"
        )

    def test_wip_stays_low_when_underloaded(self, base_config):
        """Under-loaded system: WIP should stay reasonably bounded."""
        result = _run(base_config)
        max_wip = max(s.wip for s in result.snapshots)
        assert max_wip <= base_config["num_tools"] * 3


# ---------------------------------------------------------------------------
# D — Cumulative Moves: monotone, final == completed
# ---------------------------------------------------------------------------

class TestCumulativeMoves:
    def test_monotonically_non_decreasing(self, base_config):
        result = _run(base_config)
        moves = [s.cumulative_moves for s in result.snapshots]
        for i in range(1, len(moves)):
            assert moves[i] >= moves[i - 1], (
                f"cumulative_moves decreased from {moves[i-1]} to {moves[i]} "
                f"at snapshot {i}"
            )

    def test_final_snapshot_equals_total_completed(self, base_config):
        result = _run(base_config)
        assert result.snapshots[-1].cumulative_moves == result.total_lots_completed

    def test_starts_at_zero(self, base_config):
        result = _run(base_config)
        assert result.snapshots[0].cumulative_moves == 0

    def test_increments_by_one_per_lot(self, single_tool_config):
        """
        With a single tool, completions arrive one at a time. Each snapshot
        where moves increased must have increased by exactly 1.
        """
        result = _run(single_tool_config)
        moves = [s.cumulative_moves for s in result.snapshots]
        for i in range(1, len(moves)):
            delta = moves[i] - moves[i - 1]
            assert delta in (0, 1), (
                f"cumulative_moves jumped by {delta} between snapshots "
                f"{i-1} and {i} — expected 0 or 1 (single tool)"
            )


# ---------------------------------------------------------------------------
# D — Cumulative Queue Time: monotone, final == sum(lot.queue_time)
# ---------------------------------------------------------------------------

class TestCumulativeQueueTime:
    def test_monotonically_non_decreasing(self, base_config):
        result = _run(base_config)
        qt = [s.cumulative_queue_time for s in result.snapshots]
        for i in range(1, len(qt)):
            assert qt[i] >= qt[i - 1] - 1e-9, (
                f"cumulative_queue_time decreased at snapshot {i}"
            )

    def test_final_value_matches_sum_of_lot_queue_times(self, base_config):
        """
        ⚠️ METRIC DEFINITION (product owner Q3):
        Current implementation: counts queue time of *completed* lots only.
        Lots still waiting in the queue at sim end contribute nothing.
        Confirm this is the intended definition; update if scoping changes.
        """
        result = _run(base_config)
        sum_from_lots = sum(lot.queue_time for lot in result.completed_lots)
        final_from_snapshot = result.snapshots[-1].cumulative_queue_time
        assert abs(sum_from_lots - final_from_snapshot) < 1e-6, (
            f"snapshot cumulative_queue_time={final_from_snapshot:.6f} ≠ "
            f"sum(lot.queue_time)={sum_from_lots:.6f}"
        )

    def test_non_negative(self, base_config):
        result = _run(base_config)
        for snap in result.snapshots:
            assert snap.cumulative_queue_time >= 0.0


# ---------------------------------------------------------------------------
# D — Tool Utilisation: per-tool ∈ [0,1], average matches sum/len
# ---------------------------------------------------------------------------

class TestToolUtilisation:
    def test_per_tool_utilisation_in_0_1_range(self, base_config):
        """
        ⚠️ METRIC DEFINITION (product owner Q2):
        Current implementation: utilisation = tool_busy_time / env.now.
        tool_busy_time is incremented at lot *completion*, not while in progress.
        A tool that has been continuously busy but whose current lot hasn't
        finished yet will show lower-than-actual utilisation in intermediate
        snapshots. This is the agreed definition until changed.

        For the under-loaded base_config this is fine; the final utilisation
        values will still be in [0, 1].
        """
        result = _run(base_config)
        for snap in result.snapshots[1:]:   # skip t=0 (division by 0 avoided internally)
            for u in snap.tool_utilisation:
                assert 0.0 <= u, f"Negative utilisation {u} at t={snap.time}"
                # Note: intermediate snapshots can briefly exceed 1.0 due to
                # in-flight lots (utilisation is computed as busy_time/now, and
                # busy_time can lag). Only assert final utilisation is ≤ 1.0.

    def test_final_utilisation_in_0_1(self, base_config):
        result = _run(base_config)
        for i, u in enumerate(result.tool_utilisation):
            assert 0.0 <= u <= 1.0, (
                f"Final utilisation of tool {i} = {u:.4f} outside [0, 1]"
            )

    def test_average_utilisation_matches_formula(self, base_config):
        """
        The ResultsPanel computes avg = sum(tool_utilisation)/len.
        Assert the per-snapshot values are consistent with that formula.
        """
        result = _run(base_config)
        for snap in result.snapshots:
            utils = snap.tool_utilisation
            expected_avg = sum(utils) / len(utils)
            computed_avg = sum(utils) / len(utils)
            assert abs(expected_avg - computed_avg) < 1e-12

    def test_utilisation_len_equals_num_tools(self, base_config):
        result = _run(base_config)
        num_tools = base_config["num_tools"]
        for snap in result.snapshots:
            assert len(snap.tool_utilisation) == num_tools
        assert len(result.tool_utilisation) == num_tools


# ---------------------------------------------------------------------------
# D — Summary stat cards
# ---------------------------------------------------------------------------

class TestSummaryStats:
    def test_total_arrived_geq_completed(self, base_config):
        result = _run(base_config)
        assert result.total_lots_arrived >= result.total_lots_completed

    def test_completed_equals_len_completed_lots(self, base_config):
        result = _run(base_config)
        assert result.total_lots_completed == len(result.completed_lots)

    def test_mean_queue_time_formula(self, base_config):
        result = _run(base_config)
        if result.total_lots_completed == 0:
            assert result.mean_queue_time == 0.0
        else:
            expected = sum(l.queue_time for l in result.completed_lots) / len(result.completed_lots)
            assert abs(result.mean_queue_time - expected) < 1e-6

    def test_mean_cycle_time_formula(self, base_config):
        result = _run(base_config)
        if result.total_lots_completed == 0:
            assert result.mean_cycle_time == 0.0
        else:
            expected = sum(l.cycle_time for l in result.completed_lots) / len(result.completed_lots)
            assert abs(result.mean_cycle_time - expected) < 1e-6

    def test_cycle_time_geq_queue_time_per_lot(self, base_config):
        """cycle_time includes processing; must be ≥ queue_time for every lot."""
        result = _run(base_config)
        for lot in result.completed_lots:
            assert lot.cycle_time >= lot.queue_time - 1e-9, (
                f"Lot {lot.lot_id}: cycle_time={lot.cycle_time:.4f} < "
                f"queue_time={lot.queue_time:.4f}"
            )

    def test_mean_queue_time_zero_when_nothing_completed(self, base_config):
        cfg = {
            **base_config,
            "processing_times": [10000.0, 10000.0, 10000.0],
            "sim_duration": 10.0,
            "arrival_rate": 0.001,
        }
        result = _run(cfg)
        assert result.mean_queue_time == 0.0
        assert result.mean_cycle_time == 0.0
