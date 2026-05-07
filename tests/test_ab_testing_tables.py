from __future__ import annotations

import unittest
from pathlib import Path

from src.experiments import build_ab_testing_tables


class ABTestingTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.processed_dir = cls.repo_root / "data" / "processed"
        cls.tables = build_ab_testing_tables(
            cls.processed_dir,
            write_outputs=False,
            random_state=42,
        )

    def test_assignment_contains_balanced_control_and_treatment(self) -> None:
        assignment = self.tables.ab_test_assignment
        self.assertEqual(set(assignment["variant"]), {"control", "treatment"})
        self.assertTrue(assignment["y_pred"].astype(int).eq(1).all())
        self.assertTrue(assignment["primary_metric_observed"].isin({0, 1}).all())
        counts = assignment["variant"].value_counts()
        self.assertLessEqual(abs(int(counts["control"]) - int(counts["treatment"])), 5)

    def test_experiment_design_matches_lecture_checklist(self) -> None:
        design = self.tables.ab_test_experiment_design
        expected_components = {
            "business_question",
            "randomization_unit",
            "control_group",
            "treatment_group",
            "primary_metric",
            "secondary_metrics",
            "guardrail_metrics",
            "sample_size_base",
            "baseline_rate",
            "minimum_duration_rule",
            "decision_rule",
            "pitfall_checks",
        }
        self.assertTrue(expected_components.issubset(set(design["design_component"])))
        self.assertTrue(design["lecture_alignment"].notna().all())

    def test_srm_check_is_present(self) -> None:
        srm = self.tables.ab_test_srm_check
        self.assertEqual(set(srm["check_name"]), {"sample_ratio_mismatch"})
        self.assertTrue(srm["p_value"].between(0, 1).all())
        self.assertTrue(srm["passed_srm_check"].isin({True, False}).all())

    def test_balance_table_has_required_features(self) -> None:
        balance = self.tables.ab_test_balance
        self.assertIn("risk_probability", set(balance["feature"]))
        self.assertIn("recommendation_score", set(balance["feature"]))
        self.assertIn("risk_band", set(balance["feature"]))
        self.assertTrue(balance["feature_type"].isin({"numeric", "categorical"}).all())
        self.assertTrue(balance["standardized_difference"].notna().all())

    def test_power_analysis_is_bounded(self) -> None:
        power = self.tables.ab_test_power_analysis
        self.assertTrue(power["baseline_success_rate"].between(0, 1).all())
        self.assertTrue((power["relative_mde"] > 0).all())
        self.assertTrue(power["treatment_success_rate"].between(0, 1).all())
        self.assertTrue((power["required_n_per_group"] > 0).all())
        self.assertTrue(power["minimum_detectable_effect"].between(0, 1).all())

    def test_simulated_results_include_historical_check_and_lift_scenarios(self) -> None:
        results = self.tables.ab_test_simulated_results
        self.assertIn("historical_check", set(results["scenario_type"]))
        self.assertIn("simulated_lift", set(results["scenario_type"]))
        self.assertTrue(results["p_value"].between(0, 1).all())
        self.assertTrue(results["significant_at_05"].isin({True, False}).all())
        self.assertTrue(results["business_decision"].notna().all())


if __name__ == "__main__":
    unittest.main()
