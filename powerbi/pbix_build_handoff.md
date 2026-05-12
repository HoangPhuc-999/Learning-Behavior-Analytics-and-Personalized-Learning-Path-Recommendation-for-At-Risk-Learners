# PBIX Build Handoff

The repository now contains the final Power BI dashboard and the handoff artifacts needed to review or rebuild it in Power BI Desktop:

- `final_share.pbix`
- `dashboard_storyboard.md`
- `dashboard_data_dictionary.md`
- `dashboard_screenshot_pack/`
- all exported CSV tables from notebooks `05` and `06`

## What is ready

- page structure
- source tables
- recommended relationships
- KPI definitions
- page-level visual logic
- wireframe screenshots
- advanced reliability and campaign-capacity CSVs
- A/B testing readiness CSVs
- validated PBIX dashboard file

## What still requires Power BI Desktop

- optional data source repointing before refresh on another machine
- optional page layout polish
- optional slicer interaction review
- optional final theme and formatting
- optional page 7 build for confidence intervals, subgroup diagnostics, risk trajectory, and threshold cost-benefit
- optional page 8 build for A/B experiment readiness

See `pbix_validation_report.md` for the latest PBIX data checks and non-blocking notes.

## Recommended build order

1. Import all tables listed in `dashboard_storyboard.md`
2. Build the relationships from `dashboard_data_dictionary.md`
3. Create KPI measures first
4. Build page 4 and page 5 first because they hold the core research value
5. Build page 7 next because it proves reliability, subgroup awareness, and campaign-capacity thinking
6. Build page 8 to show A/B experiment design, SRM, balance, power, and simulated decision logic
7. Finish with page 6 watchlist and page 1 overview

## Advanced Table Refresh

Run this after modeling outputs are regenerated:

```bash
make advanced-dashboard
```

This refreshes:

- `champion_metric_bootstrap_ci.csv`
- `subgroup_model_performance.csv`
- `risk_signal_trajectory.csv`
- `threshold_cost_benefit.csv`

Use `powerbi/dax_measure_catalog.md` for the recommended Power BI measures.

## A/B Testing Table Refresh

Run this after champion prediction outputs are regenerated:

```bash
make ab-testing
```

This refreshes:

- `ab_test_experiment_design.csv`
- `ab_test_assignment.csv`
- `ab_test_srm_check.csv`
- `ab_test_balance.csv`
- `ab_test_power_analysis.csv`
- `ab_test_simulated_results.csv`

## Naming

The submitted Power BI Desktop build is saved as:

`powerbi/final_share.pbix`
