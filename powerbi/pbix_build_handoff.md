# PBIX Build Handoff

The repository now contains all source artifacts needed to assemble the research dashboard in Power BI Desktop:

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

## What still requires Power BI Desktop

- importing the CSVs into a `.pbix`
- building measures and visuals
- page layout polish
- slicer interactions
- final theme and formatting
- optional page 7 build for confidence intervals, subgroup diagnostics, risk trajectory, and threshold cost-benefit
- optional page 8 build for A/B experiment readiness

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

When the Power BI Desktop build is created, save it as:

`powerbi/final_decision_dashboard.pbix`
