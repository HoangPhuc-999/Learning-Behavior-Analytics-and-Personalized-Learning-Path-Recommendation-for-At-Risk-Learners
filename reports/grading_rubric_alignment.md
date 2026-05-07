# Grading Rubric Alignment

This file maps the project to common Data-Driven Marketing grading criteria so the final submission can be defended clearly.

## 1. Business and Marketing Relevance

- Frames learner failure and withdrawal as a retention and engagement problem.
- Uses risk bands to prioritize outreach instead of treating all learners equally.
- Converts model thresholds into campaign-capacity metrics such as review load per 1,000 enrollments.
- Connects segments to differentiated recommendation paths, similar to audience strategy in marketing analytics.
- Adds A/B testing readiness so the intervention can be validated causally before full rollout.

## 2. Data Understanding and Preparation

- Integrates OULAD learner profile, registration, assessment, course, and VLE interaction tables.
- Works at the enrollment grain: `id_student + code_module + code_presentation`.
- Exports clean processed tables with no missing cells or duplicate enrollment keys in the four horizon feature stores.
- Uses a reproducible pipeline through notebooks, `src/`, scripts, Makefile targets, tests, and validation checks.

## 3. Analytical Depth

- Combines descriptive EDA, segmentation, recommendation, classification, ablation, calibration, confidence intervals, subgroup diagnostics, threshold cost-benefit, and A/B experiment design.
- Compares four intervention horizons: day 7, day 14, day 21, and day 30.
- Compares three model families: Logistic Regression, Random Forest, and XGBoost.
- Uses a validation-based threshold rule aligned with early-warning costs: recall first, then precision, then F2 and PR-AUC.

## 4. Model Quality and Defensibility

- Final champion: `XGBoost @ day 30`, threshold `0.25`.
- Held-out test performance: recall `0.9367`, F2 `0.8540`, ROC-AUC `0.8467`, PR-AUC `0.8766`.
- Bootstrap confidence intervals confirm stable test-set performance.
- Calibration and risk-band results show monotonic realized risk from Low to Critical.
- Ablation shows that full behavioral and assessment feature sets outperform demographics-only baselines.
- A/B testing outputs include control/treatment assignment, SRM check, balance diagnostics, power/MDE planning, confidence intervals, p-values, and a decision rule.

## 5. Managerial Actionability

- Day 7 gives the earliest credible triage checkpoint.
- Day 30 gives the strongest final ranking checkpoint.
- Risk bands support prioritization when advisor capacity is limited.
- Segments and learning paths translate risk scores into differentiated next actions.
- Subgroup diagnostics identify where rollout monitoring should focus.
- A/B simulation shows that a `+5%` retention lift would be detectable with the current flagged sample and would pass the business decision rule.

## 6. Communication and Dashboard Readiness

- Power BI storyboard defines the dashboard flow, page purpose, source tables, and key messages.
- Data dictionary documents grain, purpose, and important fields for each dashboard table.
- DAX measure catalog provides ready-to-build KPI definitions.
- Final report handoff, presentation outline, demo talk track, and submission checklist support defense preparation.

## 7. Limitations Stated Honestly

- The target combines `Fail` and `Withdrawn`, which is operationally useful but broad.
- Recommendation paths are prototype-based and not causal.
- A/B testing is currently a design and offline simulation, not a completed live RCT.
- Subgroup diagnostics are fairness checks, not proof of causal fairness.
- External validation and real intervention experiments are still required before production deployment.
