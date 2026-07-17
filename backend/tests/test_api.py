"""
Section E — API layer tests.

Uses FastAPI's TestClient (backed by httpx) to exercise routes.py and
schemas.py end-to-end without a running server.

Covers:
  E1  GET /api/scenario — shape and content
  E2  GET /health
  E3  POST /api/simulate — happy path, response shape
  E4  POST /api/simulate — schema validation rejects bad payloads
  E5  POST /api/simulate/compare — multi-strategy results
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# E1 — GET /api/scenario
# ---------------------------------------------------------------------------

class TestGetScenario:
    def test_returns_200(self, client):
        resp = client.get("/api/scenario")
        assert resp.status_code == 200

    def test_response_has_required_fields(self, client):
        data = client.get("/api/scenario").json()
        assert "concept_title"    in data
        assert "concept_explainer" in data
        assert "default_config"   in data
        assert "dispatching_rules" in data
        assert "arrival_distributions" in data

    def test_all_five_strategies_present(self, client):
        data = client.get("/api/scenario").json()
        rules = data["dispatching_rules"]
        expected = {"fifo", "least_loaded_tool", "random_qualified_tool",
                    "optimised_spt", "mip_optimized"}
        assert expected == set(rules), (
            f"Expected strategies {expected}, got {set(rules)}"
        )

    def test_mip_optimized_in_dispatching_rules(self, client):
        data = client.get("/api/scenario").json()
        assert "mip_optimized" in data["dispatching_rules"]

    def test_arrival_distributions_present(self, client):
        data = client.get("/api/scenario").json()
        assert "exponential" in data["arrival_distributions"]
        assert "fixed"        in data["arrival_distributions"]

    def test_default_config_has_required_keys(self, client):
        cfg = client.get("/api/scenario").json()["default_config"]
        for key in ("num_tools", "num_products", "arrival_rate",
                    "processing_times", "qualification_matrix",
                    "dispatching_rule", "sim_duration"):
            assert key in cfg, f"default_config missing key: {key}"


# ---------------------------------------------------------------------------
# E2 — GET /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_returns_status_ok(self, client):
        data = client.get("/health").json()
        assert data == {"status": "ok"}


# ---------------------------------------------------------------------------
# E3 — POST /api/simulate happy path
# ---------------------------------------------------------------------------

class TestSimulateHappyPath:
    def test_returns_200(self, client, default_api_payload):
        resp = client.post("/api/simulate", json=default_api_payload)
        assert resp.status_code == 200, resp.text

    def test_response_has_all_summary_fields(self, client, default_api_payload):
        data = client.post("/api/simulate", json=default_api_payload).json()
        for field in ("dispatching_rule", "snapshots", "total_lots_arrived",
                      "total_lots_completed", "mean_queue_time",
                      "mean_cycle_time", "tool_utilisation"):
            assert field in data, f"Response missing field: {field}"

    def test_dispatching_rule_echoed_in_response(self, client, default_api_payload):
        data = client.post("/api/simulate", json=default_api_payload).json()
        assert data["dispatching_rule"] == default_api_payload["dispatching_rule"]

    def test_snapshots_is_non_empty_list(self, client, default_api_payload):
        data = client.post("/api/simulate", json=default_api_payload).json()
        assert isinstance(data["snapshots"], list)
        assert len(data["snapshots"]) > 0

    def test_each_snapshot_has_required_fields(self, client, default_api_payload):
        data = client.post("/api/simulate", json=default_api_payload).json()
        for snap in data["snapshots"]:
            for field in ("time", "wip", "cumulative_moves",
                          "cumulative_queue_time", "tool_utilisation"):
                assert field in snap, f"Snapshot missing field: {field}"

    def test_summary_stats_are_rounded_to_4dp(self, client, default_api_payload):
        data = client.post("/api/simulate", json=default_api_payload).json()
        for field in ("mean_queue_time", "mean_cycle_time"):
            val = data[field]
            assert round(val, 4) == val, (
                f"{field}={val} is not rounded to 4 decimal places"
            )

    def test_tool_utilisation_length_matches_num_tools(self, client, default_api_payload):
        data = client.post("/api/simulate", json=default_api_payload).json()
        assert len(data["tool_utilisation"]) == default_api_payload["num_tools"]

    def test_completed_leq_arrived(self, client, default_api_payload):
        data = client.post("/api/simulate", json=default_api_payload).json()
        assert data["total_lots_completed"] <= data["total_lots_arrived"]

    @pytest.mark.parametrize("strategy", [
        "fifo", "least_loaded_tool", "random_qualified_tool",
        "optimised_spt", "mip_optimized",
    ])
    def test_all_strategies_return_200(self, client, default_api_payload, strategy):
        payload = {**default_api_payload, "dispatching_rule": strategy}
        resp = client.post("/api/simulate", json=payload)
        assert resp.status_code == 200, (
            f"Strategy '{strategy}' returned {resp.status_code}: {resp.text}"
        )


# ---------------------------------------------------------------------------
# E4 — POST /api/simulate validation (bad payloads)
# ---------------------------------------------------------------------------

class TestSimulateValidation:
    def test_wrong_processing_times_length(self, client, default_api_payload):
        """processing_times length ≠ num_products must be rejected."""
        payload = {
            **default_api_payload,
            "num_products": 3,
            "processing_times": [1.0, 2.0],  # only 2 entries, not 3
        }
        resp = client.post("/api/simulate", json=payload)
        assert resp.status_code in (422, 500), (
            f"Expected 422/500 for mismatched processing_times, got {resp.status_code}"
        )

    def test_wrong_qualification_matrix_rows(self, client, default_api_payload):
        """qualification_matrix row count ≠ num_tools must be rejected."""
        payload = {
            **default_api_payload,
            "num_tools": 4,
            "qualification_matrix": [[True, True, False]],  # only 1 row
        }
        resp = client.post("/api/simulate", json=payload)
        assert resp.status_code in (422, 500)

    def test_unknown_dispatching_rule(self, client, default_api_payload):
        """Unknown dispatching rule must be rejected."""
        payload = {**default_api_payload, "dispatching_rule": "teleportation"}
        resp = client.post("/api/simulate", json=payload)
        assert resp.status_code in (422, 500)

    def test_negative_num_tools(self, client, default_api_payload):
        payload = {**default_api_payload, "num_tools": -1}
        resp = client.post("/api/simulate", json=payload)
        assert resp.status_code == 422

    def test_zero_num_tools(self, client, default_api_payload):
        payload = {**default_api_payload, "num_tools": 0}
        resp = client.post("/api/simulate", json=payload)
        assert resp.status_code == 422

    def test_invalid_arrival_distribution(self, client, default_api_payload):
        payload = {**default_api_payload, "arrival_distribution": "gaussian"}
        resp = client.post("/api/simulate", json=payload)
        assert resp.status_code in (422, 500)

    def test_tool_with_no_qualifications_rejected(self, client, default_api_payload):
        """A tool qualified for zero products must be rejected."""
        payload = {
            **default_api_payload,
            "qualification_matrix": [
                [False, False, False],   # tool 0: no qualifications ← invalid
                [True,  False, True],
                [False, True,  True],
                [True,  True,  True],
            ],
        }
        resp = client.post("/api/simulate", json=payload)
        assert resp.status_code in (422, 500)

    def test_product_with_no_qualified_tools_rejected(self, client, default_api_payload):
        """A product reachable by zero tools must be rejected."""
        payload = {
            **default_api_payload,
            "qualification_matrix": [
                [True,  False, False],  # no tool qualifies product 1
                [True,  False, True],
                [True,  False, True],
                [True,  False, True],
            ],
        }
        resp = client.post("/api/simulate", json=payload)
        assert resp.status_code in (422, 500)


# ---------------------------------------------------------------------------
# E5 — POST /api/simulate/compare
# ---------------------------------------------------------------------------

class TestSimulateCompare:
    def test_returns_200(self, client, default_api_payload):
        payload = {
            **default_api_payload,
            "dispatching_rules_to_compare": ["fifo", "optimised_spt"],
        }
        resp = client.post("/api/simulate/compare", json=payload)
        assert resp.status_code == 200, resp.text

    def test_returns_one_result_per_strategy(self, client, default_api_payload):
        strategies = ["fifo", "optimised_spt", "mip_optimized"]
        payload = {
            **default_api_payload,
            "dispatching_rules_to_compare": strategies,
        }
        data = client.post("/api/simulate/compare", json=payload).json()
        assert "results" in data
        assert len(data["results"]) == len(strategies)

    def test_each_result_has_dispatching_rule_field(self, client, default_api_payload):
        strategies = ["fifo", "least_loaded_tool"]
        payload = {
            **default_api_payload,
            "dispatching_rules_to_compare": strategies,
        }
        data = client.post("/api/simulate/compare", json=payload).json()
        returned_rules = [r["dispatching_rule"] for r in data["results"]]
        assert set(returned_rules) == set(strategies)

    def test_all_five_strategies_compare(self, client, default_api_payload):
        strategies = ["fifo", "least_loaded_tool", "random_qualified_tool",
                      "optimised_spt", "mip_optimized"]
        payload = {
            **default_api_payload,
            "dispatching_rules_to_compare": strategies,
        }
        data = client.post("/api/simulate/compare", json=payload).json()
        assert len(data["results"]) == 5

    def test_fallback_to_single_strategy_when_no_list(self, client, default_api_payload):
        """
        If dispatching_rules_to_compare is omitted, compare endpoint should
        fall back to the single dispatching_rule.
        """
        resp = client.post("/api/simulate/compare", json=default_api_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["results"]) >= 1

    def test_each_result_has_summary_fields(self, client, default_api_payload):
        payload = {
            **default_api_payload,
            "dispatching_rules_to_compare": ["fifo", "optimised_spt"],
        }
        data = client.post("/api/simulate/compare", json=payload).json()
        for result in data["results"]:
            for field in ("dispatching_rule", "snapshots", "total_lots_arrived",
                          "total_lots_completed", "mean_queue_time",
                          "mean_cycle_time", "tool_utilisation"):
                assert field in result, f"Compare result missing field: {field}"
