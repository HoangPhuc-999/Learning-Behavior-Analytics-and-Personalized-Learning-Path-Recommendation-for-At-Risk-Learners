# Final Presentation Outline

## Slide 1. Title

- Project title
- Team / course / university
- One-line value proposition:
  - `Behavior analytics + segmentation + multi-horizon early warning for at-risk learners`

## Slide 2. Problem Context

- Why online learner risk matters
- At-risk definition: `Fail` or `Withdrawn`
- Dataset scale:
  - `32,593` enrollments
  - `28,785` learners
  - `52.8%` at-risk rate

## Slide 3. Research Questions

- How do learning behaviors differ by outcome?
- Can learners be segmented into meaningful profiles?
- How early can at-risk learners be identified?
- Which feature groups matter most?
- Are the predicted probabilities useful for intervention prioritization?
- How should the intervention be A/B tested before claiming causal impact?

## Slide 4. Pipeline Overview

- Data cleaning and integration
- EDA
- Multi-horizon feature engineering
- Segmentation and recommendation
- Multi-horizon modeling
- Ablation and calibration
- Reliability, fairness, and threshold diagnostics
- A/B testing readiness
- Power BI research dashboard

## Slide 5. EDA Insights

- Early engagement gap by outcome
- Assessment completion and score separation
- Module-level risk variation

Key sentence:

> Risk is visible early, and both engagement and assessment behavior matter.

## Slide 6. Segmentation Results

- Four clusters:
  - Inactive Drop-offs
  - Sporadic Explorers
  - Steady Progressors
  - Focused Achievers
- Show cluster size and at-risk rate

## Slide 7. Recommendation Layer

- Recommendation logic:
  - compare with successful peers in the same cluster
  - identify main behavioral gap
  - assign learning path
- Show top recommended paths

## Slide 8. Multi-Horizon Feature Engineering

- Horizons:
  - day 7
  - day 14
  - day 21
  - day 30
- Stress leakage control
- Show coverage growth across horizons

## Slide 9. Model Design

- Candidate models:
  - Logistic Regression
  - Random Forest
  - XGBoost
- Train / validation / test split
- Threshold tuning rule:
  - recall first
  - then precision
  - then F2
  - then PR-AUC

## Slide 10. Horizon Comparison

- Table with best pair per horizon
- Key message:
  - day 7 is the earliest useful horizon
  - day 30 is the strongest overall horizon

## Slide 11. Final Champion Model

- Champion: `XGBoost @ day 30`
- Threshold: `0.25`
- Test metrics:
  - Precision `0.6313`
  - Recall `0.9367`
  - F2 `0.8540`
  - ROC-AUC `0.8467`
  - PR-AUC `0.8766`

## Slide 12. Ablation Results

- Compare:
  - demographics only
  - engagement only
  - assessment only
  - engagement + assessment
  - full feature set
- Main message:
  - full feature set is strongest
  - demographics alone are weak

## Slide 13. Calibration and Risk Bands

- Show calibration curve
- Show risk bands:
  - Low
  - Medium
  - High
  - Critical
- Main message:
  - model probabilities are usable for tiered intervention

## Slide 14. Diagnostic Interpretation

- Top feature importance:
  - avg_score
  - studied_credits
  - days_since_last
  - avg_submission_delay
  - assessment_discipline
- Cluster-level recall differences

## Slide 15. Reliability and Fairness Diagnostics

- Bootstrap 95% confidence intervals:
  - Recall CI: `0.9281` to `0.9447`
  - PR-AUC CI: `0.8673` to `0.8865`
- Subgroup checks:
  - recall remains above `0.90` in checked groups
  - high-IMD group is closest to the recall floor

Key sentence:

> The model is not only accurate on average; it is checked for metric stability and subgroup-level recall before any intervention recommendation.

## Slide 16. Threshold Cost-Benefit

- Selected threshold: `0.25`
- Review-load implication:
  - flags about `77.8%` of validation enrollments
  - catches about `488.6` at-risk learners per `1,000` enrollments
  - false-alert ratio about `0.59` false positives per true positive

Key sentence:

> In a marketing or learner-retention setting, the threshold is a campaign capacity decision, not only a model metric.

## Slide 17. A/B Testing Readiness

- Control group: `2,554` flagged learners with standard support
- Treatment group: `2,553` flagged learners with risk-targeted personalized intervention
- Primary metric: `retention_success`
- SRM check p-value: `0.9888`, so the 50/50 split is valid
- Minimum detectable effect: `3.82%`
- Decision rule:
  - deploy only if `p_value < 0.05`
  - 95% CI excludes zero
  - lift is practically meaningful

Key sentence:

> The project does not claim live causal proof; it adds the randomized experiment design needed to prove whether the intervention works after deployment.

## Slide 18. Power BI Research Dashboard

- 8 pages:
  - Executive Overview
  - Behavior & Outcome Analytics
  - Segmentation & Recommendation Context
  - Multi-Horizon Early Warning
  - Calibration & Model Diagnostics
  - At-Risk Learner Watchlist
  - Reliability & Campaign Capacity
  - A/B Experiment Readiness
- Advanced page/table set:
  - confidence intervals
  - subgroup performance
  - risk trajectory
  - threshold cost-benefit
  - A/B testing design

## Slide 19. Managerial Implications

- Day 7 can be used for early triage
- Day 30 gives the strongest ranking
- Critical risk band should be prioritized first
- Segments help assign differentiated follow-up
- Threshold choice should reflect advisor capacity
- A/B testing should validate causal intervention lift before full rollout

## Slide 20. Limitations and Future Work

- Single dataset
- At-risk target is broad
- Recommendation is not causal
- A/B testing is a design/simulation, not a completed live RCT
- Subgroup checks are diagnostic, not causal fairness proof
- Future work:
  - temporal sequence modeling
  - external validation
  - intervention impact evaluation

## Slide 21. Conclusion

- The project moved from a static classifier to a research-grade early-warning study
- It links:
  - behavior
  - segmentation
  - recommendation
  - multi-horizon prediction
  - calibration
  - intervention prioritization
  - A/B testing readiness
  - capacity-aware targeting
