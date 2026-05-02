from __future__ import annotations

import unittest
from pathlib import Path

from src.features.advanced_dashboard_tables import (
    BOOTSTRAP_METRICS,
    HORIZONS,
    TARGET_RECALL,
    build_advanced_dashboard_tables,
)


class AdvancedDashboardTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.processed_dir = cls.repo_root / "data" / "processed"
        cls.tables = build_advanced_dashboard_tables(
            cls.processed_dir,
            write_outputs=False,
            n_boot=100,
            random_state=42,
        )

    def test_bootstrap_ci_contains_expected_metrics(self) -> None:
        ci = self.tables.champion_metric_bootstrap_ci
        self.assertEqual(set(ci["metric"]), set(BOOTSTRAP_METRICS))
        self.assertTrue((ci["n_boot"] == 100).all())
        self.assertTrue((ci["ci_95_lower"] <= ci["point_estimate"]).all())
        self.assertTrue((ci["point_estimate"] <= ci["ci_95_upper"]).all())

    def test_subgroup_performance_has_monitoring_fields(self) -> None:
        subgroup = self.tables.subgroup_model_performance
        expected_subgroups = {"Gender", "Disability", "IMD deprivation", "Prior attempts"}
        self.assertTrue(expected_subgroups.issubset(set(subgroup["subgroup"])))
        self.assertIn("Low IMD band (0-40%)", set(subgroup["group"]))
        self.assertTrue(subgroup["recall"].between(0, 1).all())
        self.assertTrue(subgroup["precision"].between(0, 1).all())
        self.assertTrue((subgroup["review_flag"] == (subgroup["recall"] < TARGET_RECALL)).all())

    def test_risk_signal_trajectory_covers_all_horizons_and_gap_rows(self) -> None:
        trajectory = self.tables.risk_signal_trajectory
        self.assertEqual(set(trajectory["horizon_day"].dropna().astype(int)), set(HORIZONS))
        self.assertIn("Gap: at-risk minus non at-risk", set(trajectory["group"]))
        self.assertTrue((trajectory.loc[trajectory["group"] != "Gap: at-risk minus non at-risk", "n"] > 0).all())

    def test_threshold_cost_benefit_flags_selected_operating_point(self) -> None:
        cost_benefit = self.tables.threshold_cost_benefit
        selected = cost_benefit.loc[cost_benefit["selected_operating_point"]]
        self.assertEqual(len(selected), 1)
        self.assertTrue(bool(selected["target_recall_met"].iloc[0]))
        self.assertTrue(cost_benefit["threshold"].is_monotonic_increasing)
        self.assertTrue(cost_benefit["flagged_pct"].between(0, 1).all())


if __name__ == "__main__":
    unittest.main()
