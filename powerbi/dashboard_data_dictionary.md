# Dashboard Data Dictionary

This file maps each Power BI source table to its grain, purpose, and the most important fields.

## 1. Enrollment Key

Use this composite key across the dashboard:

- `id_student`
- `code_module`
- `code_presentation`

## 2. Core Tables

### `features_final.csv`

- Grain: enrollment
- Purpose: main behavior and outcome table for descriptive analytics
- Key fields:
  - `final_result`
  - `at_risk`
  - `total_clicks`
  - `active_days`
  - `early_engagement`
  - `avg_score`
  - `avg_submission_delay`
  - `completion_ratio`
  - `assessment_discipline`
  - `persistence_score`
  - `learning_risk_index`

### `segment_assignments.csv`

- Grain: enrollment
- Purpose: attach learner segment labels
- Key fields:
  - `cluster_label`
  - `rule_segment`
  - `cluster_id`
  - `final_result`
  - `at_risk`

### `personalized_learning_paths.csv`

- Grain: enrollment
- Purpose: recommendation layer for table visuals and learner watchlists
- Key fields:
  - `recommended_path`
  - `action_1`
  - `action_2`
  - `action_3`
  - `recommendation_score`
  - `cluster_label`
  - `final_result`

### `champion_test_predictions.csv`

- Grain: enrollment on the held-out test set
- Purpose: final watchlist fact table
- Key fields:
  - `risk_probability`
  - `risk_band`
  - `y_pred`
  - `y_true`
  - `prediction_outcome`
  - `cluster_label`
  - `recommended_path`
  - `action_1`
  - `action_2`
  - `action_3`

### `risk_band_test_predictions.csv`

- Grain: enrollment on the held-out test set
- Purpose: duplicate of champion predictions kept for risk-band pages
- Key fields:
  - `risk_band`
  - `risk_band_method`
  - `risk_probability`
  - `prediction_outcome`

## 3. Research Summary Tables

### `features_horizon_metadata.csv`

- Grain: horizon
- Purpose: explain feature coverage and leakage-safe horizon design
- Key fields:
  - `horizon_day`
  - `observed_activity_rate`
  - `submission_coverage`
  - `score_coverage`
  - `available_assessment_rate`
  - `prediction_columns`

### `model_horizon_comparison.csv`

- Grain: horizon-model pair
- Purpose: compare selected operating points across all candidate models
- Key fields:
  - `horizon_day`
  - `model`
  - `selected_threshold`
  - `validation_precision`
  - `validation_recall`
  - `validation_f2`
  - `validation_pr_auc`
  - `test_precision`
  - `test_recall`
  - `test_f2`
  - `test_pr_auc`

### `selected_operating_points.csv`

- Grain: horizon-model pair
- Purpose: selected validation operating point per pair
- Key fields:
  - `threshold`
  - `precision`
  - `recall`
  - `f2`
  - `pr_auc`
  - `is_best_for_horizon`
  - `is_earliest_useful_horizon`

### `champion_test_metrics.csv`

- Grain: split
- Purpose: final metric cards for validation vs test
- Key fields:
  - `split`
  - `model`
  - `horizon_day`
  - `threshold`
  - `precision`
  - `recall`
  - `f2`
  - `roc_auc`
  - `pr_auc`
  - `brier_score`

### `calibration_summary.csv`

- Grain: horizon-probability-bin
- Purpose: calibration page
- Key fields:
  - `horizon_day`
  - `probability_bin`
  - `avg_predicted_probability`
  - `observed_at_risk_rate`
  - `brier_score`

### `risk_band_summary.csv`

- Grain: risk band
- Purpose: summarize final operational risk tiers
- Key fields:
  - `risk_band`
  - `n`
  - `actual_at_risk_rate`
  - `average_predicted_probability`
  - `risk_band_method`

### `ablation_results.csv`

- Grain: horizon-feature-group
- Purpose: ablation comparison
- Key fields:
  - `horizon_day`
  - `feature_group`
  - `test_precision`
  - `test_recall`
  - `test_f2`
  - `test_roc_auc`
  - `test_pr_auc`

### `ablation_gain_summary.csv`

- Grain: horizon-feature-group
- Purpose: compare each ablation to the full model
- Key fields:
  - `delta_test_precision_vs_full`
  - `delta_test_recall_vs_full`
  - `delta_test_f2_vs_full`
  - `delta_test_roc_auc_vs_full`
  - `delta_test_pr_auc_vs_full`

### `ab_test_experiment_design.csv`

- Grain: experiment-design component
- Purpose: document the A/B testing setup in the lecture checklist format
- Key fields:
  - `experiment_id`
  - `design_component`
  - `value`
  - `lecture_alignment`

### `ab_test_assignment.csv`

- Grain: eligible enrollment assigned to an experiment variant
- Purpose: control/treatment assignment for flagged learners
- Key fields:
  - `experiment_id`
  - `variant`
  - `variant_label`
  - `primary_metric`
  - `primary_metric_observed`
  - `stratification_key`
  - `risk_probability`
  - `risk_band`
  - `recommended_path`

### `ab_test_srm_check.csv`

- Grain: experiment
- Purpose: sample-ratio mismatch check for the planned traffic split
- Key fields:
  - `expected_control_share`
  - `expected_treatment_share`
  - `observed_control_n`
  - `observed_treatment_n`
  - `statistical_test`
  - `chi_square_statistic`
  - `p_value`
  - `passed_srm_check`

### `ab_test_balance.csv`

- Grain: feature-level balance check
- Purpose: verify that randomization produced similar control/treatment groups
- Key fields:
  - `feature_type`
  - `feature`
  - `level`
  - `control_rate_or_mean`
  - `treatment_rate_or_mean`
  - `standardized_difference`
  - `passed_balance_check`

### `ab_test_power_analysis.csv`

- Grain: effect-size scenario
- Purpose: sample size, power, and MDE planning for a binary primary metric
- Key fields:
  - `baseline_success_rate`
  - `absolute_lift`
  - `relative_mde`
  - `required_n_per_group`
  - `available_n_per_group`
  - `available_power`
  - `minimum_detectable_effect`
  - `feasible_with_current_sample`

### `ab_test_simulated_results.csv`

- Grain: historical or simulated experiment scenario
- Purpose: show p-value, confidence interval, uplift, and business decision rule
- Key fields:
  - `scenario`
  - `scenario_type`
  - `statistical_test`
  - `control_success_rate`
  - `treatment_success_rate`
  - `absolute_lift`
  - `ci_95_lower`
  - `ci_95_upper`
  - `p_value`
  - `business_decision`

### `model_feature_importance.csv`

- Grain: feature
- Purpose: global interpretation of the champion model
- Key fields:
  - `original_feature_name`
  - `native_importance`
  - `permutation_importance_mean`
  - `importance_rank`

### `error_analysis_samples.csv`

- Grain: enrollment
- Purpose: sample false positives and false negatives for review
- Key fields:
  - `prediction_outcome`
  - `risk_probability`
  - `risk_band`
  - `avg_score`
  - `completion_ratio`
  - `days_since_last`
  - `learning_risk_index`

### `segment_model_performance.csv`

- Grain: cluster
- Purpose: segment-level model diagnostics
- Key fields:
  - `cluster_label`
  - `actual_at_risk_rate`
  - `predicted_positive_rate`
  - `average_risk_probability`
  - `precision`
  - `recall`
  - `accuracy`

### `outcome_risk_summary.csv`

- Grain: final outcome
- Purpose: compare predicted risk by observed outcome
- Key fields:
  - `final_result`
  - `predicted_positive_rate`
  - `average_risk_probability`

### `champion_metric_bootstrap_ci.csv`

- Grain: champion metric
- Purpose: show metric stability with bootstrap confidence intervals
- Key fields:
  - `metric`
  - `point_estimate`
  - `ci_95_lower`
  - `ci_95_upper`
  - `bootstrap_std`
  - `n_boot`

### `subgroup_model_performance.csv`

- Grain: subgroup group
- Purpose: check champion model recall and ranking quality across observable learner groups
- Key fields:
  - `subgroup`
  - `group`
  - `n`
  - `at_risk_rate`
  - `recall`
  - `precision`
  - `roc_auc`
  - `recall_gap_to_target`
  - `review_flag`

### `risk_signal_trajectory.csv`

- Grain: horizon-feature-group
- Purpose: compare how behavioral signals separate at-risk and non-at-risk learners from day 7 to day 30
- Key fields:
  - `horizon_day`
  - `feature`
  - `feature_label`
  - `group`
  - `mean`
  - `sem`
  - `n`

### `threshold_cost_benefit.csv`

- Grain: threshold for the final champion pair
- Purpose: support advisor-capacity and campaign-size trade-off decisions
- Key fields:
  - `threshold`
  - `recall`
  - `precision`
  - `f2`
  - `total_flagged`
  - `flagged_pct`
  - `false_alert_ratio`
  - `expected_review_load_per_1000`
  - `caught_at_risk_per_1000`
  - `selected_operating_point`
  - `target_recall_met`

## 4. Suggested Page-to-Table Mapping

### Executive Overview

- `features_final`
- `segment_assignments`
- `personalized_learning_paths`
- `risk_band_summary`

### Behavior & Outcome Analytics

- `features_final`

### Segmentation & Recommendation Context

- `segment_assignments`
- `cluster_profiles`
- `cluster_success_activity_profile`
- `personalized_learning_paths`

### Multi-Horizon Early Warning

- `features_horizon_metadata`
- `model_horizon_comparison`
- `selected_operating_points`
- `champion_test_metrics`

### Calibration & Model Diagnostics

- `calibration_summary`
- `risk_band_summary`
- `ablation_results`
- `ablation_gain_summary`
- `model_feature_importance`

### At-Risk Learner Watchlist

- `champion_test_predictions`
- `risk_band_test_predictions`
- `segment_model_performance`

### Reliability & Campaign Capacity

- `champion_metric_bootstrap_ci`
- `subgroup_model_performance`
- `risk_signal_trajectory`
- `threshold_cost_benefit`

## 5. Build Note

This repository provides the source tables and design artifacts for the Power BI build. The `.pbix` file should be created in Power BI Desktop by importing the CSVs above and following `dashboard_storyboard.md`.
