# Power BI DAX Measure Catalog

Use these measures after importing the CSV tables listed in `dashboard_storyboard.md`.

## Core Scale

```DAX
Total Enrollments =
COUNTROWS(features_final)

Unique Learners =
DISTINCTCOUNT(features_final[id_student])

At-Risk Learners =
CALCULATE(
    COUNTROWS(features_final),
    features_final[at_risk] = 1
)

At-Risk Rate =
DIVIDE([At-Risk Learners], [Total Enrollments])
```

## Champion Model

```DAX
Champion Precision =
CALCULATE(
    MAX(champion_test_metrics[precision]),
    champion_test_metrics[split] = "test"
)

Champion Recall =
CALCULATE(
    MAX(champion_test_metrics[recall]),
    champion_test_metrics[split] = "test"
)

Champion F2 =
CALCULATE(
    MAX(champion_test_metrics[f2]),
    champion_test_metrics[split] = "test"
)

Champion ROC AUC =
CALCULATE(
    MAX(champion_test_metrics[roc_auc]),
    champion_test_metrics[split] = "test"
)

Champion PR AUC =
CALCULATE(
    MAX(champion_test_metrics[pr_auc]),
    champion_test_metrics[split] = "test"
)

Champion Brier Score =
CALCULATE(
    MAX(champion_test_metrics[brier_score]),
    champion_test_metrics[split] = "test"
)
```

## Risk Bands and Watchlist

```DAX
Avg Risk Probability =
AVERAGE(champion_test_predictions[risk_probability])

Predicted Positive Learners =
CALCULATE(
    COUNTROWS(champion_test_predictions),
    champion_test_predictions[y_pred] = 1
)

Critical Risk Learners =
CALCULATE(
    COUNTROWS(risk_band_test_predictions),
    risk_band_test_predictions[risk_band] = "Critical"
)

Critical Band Actual At-Risk Rate =
CALCULATE(
    MAX(risk_band_summary[actual_at_risk_rate]),
    risk_band_summary[risk_band] = "Critical"
)

False Positives =
CALCULATE(
    COUNTROWS(champion_test_predictions),
    champion_test_predictions[prediction_outcome] = "False Positive"
)

False Negatives =
CALCULATE(
    COUNTROWS(champion_test_predictions),
    champion_test_predictions[prediction_outcome] = "False Negative"
)
```

## Multi-Horizon

```DAX
Earliest Useful Horizon =
MINX(
    FILTER(
        selected_operating_points,
        selected_operating_points[is_earliest_useful_horizon] = TRUE()
    ),
    selected_operating_points[horizon_day]
)

Best Validation PR AUC =
MAXX(
    FILTER(
        selected_operating_points,
        selected_operating_points[is_best_for_horizon] = TRUE()
    ),
    selected_operating_points[pr_auc]
)
```

## Reliability and Campaign Capacity

```DAX
Recall CI Lower =
CALCULATE(
    MAX(champion_metric_bootstrap_ci[ci_95_lower]),
    champion_metric_bootstrap_ci[metric] = "recall"
)

Recall CI Upper =
CALCULATE(
    MAX(champion_metric_bootstrap_ci[ci_95_upper]),
    champion_metric_bootstrap_ci[metric] = "recall"
)

PR AUC CI Lower =
CALCULATE(
    MAX(champion_metric_bootstrap_ci[ci_95_lower]),
    champion_metric_bootstrap_ci[metric] = "pr_auc"
)

PR AUC CI Upper =
CALCULATE(
    MAX(champion_metric_bootstrap_ci[ci_95_upper]),
    champion_metric_bootstrap_ci[metric] = "pr_auc"
)

Selected Review Load per 1000 =
CALCULATE(
    MAX(threshold_cost_benefit[expected_review_load_per_1000]),
    threshold_cost_benefit[selected_operating_point] = TRUE()
)

Selected False Alert Ratio =
CALCULATE(
    MAX(threshold_cost_benefit[false_alert_ratio]),
    threshold_cost_benefit[selected_operating_point] = TRUE()
)

Subgroups Needing Review =
CALCULATE(
    COUNTROWS(subgroup_model_performance),
    subgroup_model_performance[review_flag] = TRUE()
)
```

## A/B Testing

```DAX
A/B Eligible Learners =
COUNTROWS(ab_test_assignment)

A/B Control Learners =
CALCULATE(
    COUNTROWS(ab_test_assignment),
    ab_test_assignment[variant] = "control"
)

A/B Treatment Learners =
CALCULATE(
    COUNTROWS(ab_test_assignment),
    ab_test_assignment[variant] = "treatment"
)

A/B SRM P-value =
MAX(ab_test_srm_check[p_value])

A/B Minimum Detectable Effect =
MAX(ab_test_power_analysis[minimum_detectable_effect])

A/B Best Simulated Lift =
MAXX(
    FILTER(
        ab_test_simulated_results,
        ab_test_simulated_results[business_decision] = "Deploy"
    ),
    ab_test_simulated_results[absolute_lift]
)
```

## Formatting Notes

- Format rates, precision, recall, AUC, and confidence interval measures as percentages or 3-decimal decimals consistently.
- Use `risk_band_summary[band_edges]` only as tooltip text.
- Keep `threshold_cost_benefit[threshold]` numeric so line charts sort correctly.
- Format A/B lift, MDE, SRM p-value, and confidence interval fields as percentages or 3-decimal decimals consistently.
