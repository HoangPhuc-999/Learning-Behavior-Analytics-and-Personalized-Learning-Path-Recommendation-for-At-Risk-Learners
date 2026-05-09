# Final Submission Checklist

Use this before submitting or presenting the final project.

## Final Verification Snapshot

Verified on `2026-05-09`:

- `make validate`: passed
- `make test`: passed, `23` tests run with `2` notebook integration tests skipped by default
- `make test-notebooks`: passed, `2` notebook smoke tests executed
- `git lfs status`: clean

## Repository Readiness

- [x] Pull latest branch and confirm `git status` is clean.
- [x] Run `make validate` and confirm `Research output validation passed`.
- [x] Run `make test` and confirm all non-integration tests pass.
- [x] Run `make test-notebooks` for notebook smoke execution.
- [x] Confirm `data/processed/` includes the four advanced dashboard tables:
  - `champion_metric_bootstrap_ci.csv`
  - `subgroup_model_performance.csv`
  - `risk_signal_trajectory.csv`
  - `threshold_cost_benefit.csv`
- [x] Confirm `data/processed/` includes the A/B testing tables:
  - `ab_test_experiment_design.csv`
  - `ab_test_assignment.csv`
  - `ab_test_srm_check.csv`
  - `ab_test_balance.csv`
  - `ab_test_power_analysis.csv`
  - `ab_test_simulated_results.csv`

## Power BI Readiness

- [ ] Import all CSV files listed in `powerbi/dashboard_storyboard.md`.
- [ ] Build relationships using the enrollment key where applicable.
- [ ] Create measures from `powerbi/dax_measure_catalog.md`.
- [ ] Build the core six pages first, then add reliability/campaign-capacity and A/B experiment readiness pages.
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
- [ ] Use A/B testing outputs to explain control/treatment assignment, SRM, MDE, CI, p-value, and the business decision rule.

## Defense Answers to Prepare

- Why not use a default threshold of `0.50`?
- Why compare multiple prediction horizons?
- Why call day 7 the earliest useful horizon?
- Why choose XGBoost at day 30 as the final champion?
- What does ablation prove?
- How do calibration and risk bands help decision makers?
- How does A/B testing move the project from prediction toward causal validation?
- How does the dashboard support a Data-Driven Marketing workflow?
- What would you test next before real deployment?
