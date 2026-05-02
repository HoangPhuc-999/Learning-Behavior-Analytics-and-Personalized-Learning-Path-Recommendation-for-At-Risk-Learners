# Final Submission Checklist

Use this before submitting or presenting the final project.

## Repository Readiness

- [ ] Pull latest branch and confirm `git status` is clean.
- [ ] Run `make validate` and confirm `Research output validation passed`.
- [ ] Run `make test` and confirm all non-integration tests pass.
- [ ] If time allows, run `make test-notebooks` for full notebook execution.
- [ ] Confirm `data/processed/` includes the four advanced dashboard tables:
  - `champion_metric_bootstrap_ci.csv`
  - `subgroup_model_performance.csv`
  - `risk_signal_trajectory.csv`
  - `threshold_cost_benefit.csv`

## Power BI Readiness

- [ ] Import all CSV files listed in `powerbi/dashboard_storyboard.md`.
- [ ] Build relationships using the enrollment key where applicable.
- [ ] Create measures from `powerbi/dax_measure_catalog.md`.
- [ ] Build the core six pages first, then add the optional reliability and campaign-capacity page.
- [ ] Check slicers for module, presentation, segment, final result, risk band, and recommendation path.
- [ ] Verify that risk-band charts show monotonic actual at-risk rate from Low to Critical.

## Presentation Readiness

- [ ] Lead with the business problem: reducing fail/withdrawal through targeted retention intervention.
- [ ] State the at-risk definition clearly: `Fail` or `Withdrawn`.
- [ ] Emphasize the horizon trade-off: day 7 is earliest useful; day 30 is strongest ranking.
- [ ] Explain why threshold `0.25` was selected using validation recall and precision, not test hindsight.
- [ ] Use ablation to defend why engagement and assessment behavior matter more than demographics alone.
- [ ] Use calibration and risk bands to defend intervention prioritization.
- [ ] Use confidence intervals and subgroup checks to show model reliability and responsible deployment thinking.

## Defense Answers to Prepare

- Why not use a default threshold of `0.50`?
- Why compare multiple prediction horizons?
- Why call day 7 the earliest useful horizon?
- Why choose XGBoost at day 30 as the final champion?
- What does ablation prove?
- How do calibration and risk bands help decision makers?
- How does the dashboard support a Data-Driven Marketing workflow?
- What would you test next before real deployment?
