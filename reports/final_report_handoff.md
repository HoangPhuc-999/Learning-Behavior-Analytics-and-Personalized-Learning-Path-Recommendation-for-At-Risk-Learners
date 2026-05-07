# Final Report Handoff

This file turns notebooks `01` to `06` into a report-ready narrative for the upgraded version of the project.

The new storyline is:

`behavior analytics -> segmentation -> recommendation -> multi-horizon early warning -> ablation -> calibration -> reliability diagnostics -> intervention watchlist -> A/B testing readiness`

## 1. Executive Summary

Use this as the opening paragraph:

> This project analyzes learner behavior in the OULAD dataset and develops a research-focused framework for segmentation, personalized recommendation, and early identification of at-risk learners. The final pipeline uses 32,593 enrollment records and compares early-warning models at day 7, 14, 21, and 30. Results show that useful recall is already achievable at day 7, but predictive ranking quality improves materially as more course history becomes available. The final champion pair is an XGBoost model at day 30 with a recall-oriented threshold of 0.25, while calibration, confidence intervals, subgroup diagnostics, threshold cost-benefit analysis, and A/B testing readiness show how the output can support a capacity-aware learner retention campaign and a future causal intervention test.

## 2. Project Scope

State these points clearly:

- Dataset: OULAD
- Observation unit: `id_student + code_module + code_presentation`
- Part I objective: explain learner behavior, segment learners, and generate personalized learning paths
- Part II objective: identify at-risk learners early enough for intervention and quantify how model quality changes over time

## 3. Dataset Facts

Use these numbers:

- Final enrollments used: `32,593`
- Unique learners: `28,785`
- Final result distribution:
  - `Pass`: `12,361`
  - `Withdrawn`: `10,156`
  - `Fail`: `7,052`
  - `Distinction`: `3,024`
- At-risk definition: `Fail` or `Withdrawn`
- Overall at-risk rate: `52.8%`

Suggested sentence:

> The problem is operationally large rather than marginal. More than half of all enrollments end in fail or withdrawal outcomes, which makes early warning and differentiated support a meaningful management problem.

## 4. EDA Storyline

### 4.1 Risk is uneven across modules

- Highest-risk module: `CCC` with about `62.2%` at-risk rate
- Lowest-risk module: `AAA` with about `29.0%` at-risk rate

Suggested wording:

> Risk is not evenly distributed across the curriculum. Some modules carry much heavier withdrawal and failure burdens, so a single institution-wide support policy is unlikely to be efficient.

### 4.2 Early engagement matters immediately

Median clicks in the first 14 days:

- `Distinction`: `156`
- `Pass`: `104`
- `Fail`: `40`
- `Withdrawn`: `12`

Suggested wording:

> Weak outcomes are visible very early. Learners who eventually withdraw are already far behind successful learners in the first two weeks, which justifies an early-warning framing rather than a late-course diagnostic framing.

### 4.3 Assessment behavior matters with engagement

Suggested wording:

> Browsing alone is not enough. Assessment completion, submission discipline, and score quality all contribute strongly to outcome separation, which is why the downstream feature store keeps both engagement and assessment signals.

## 5. Feature Engineering Story

This is the core message for notebook `04_feature_engineering.ipynb`.

### 5.1 The project now uses four predictive horizons

State this explicitly:

- `day 7`
- `day 14`
- `day 21`
- `day 30`

All four prediction tables:

- have `32,593` rows,
- have `40` columns,
- have `0` missing cells,
- have `0` duplicate enrollment keys.

### 5.2 Leakage control

Use this sentence:

> Every predictive table is built from information available only up to its own horizon. Day-7 features use only day-7-safe behavior and submissions, day-14 features use only day-14-safe information, and so on. This keeps the horizon comparison methodologically defensible.

### 5.3 Coverage trade-off

Use these coverage facts:

| Horizon | Activity Coverage | Submission Coverage | Score Coverage |
|---|---:|---:|---:|
| Day 7 | `74.0%` | `2.7%` | `2.7%` |
| Day 14 | `81.5%` | `10.3%` | `10.3%` |
| Day 21 | `84.7%` | `46.7%` | `46.7%` |
| Day 30 | `85.8%` | `63.8%` | `63.7%` |

Interpretation:

> Earlier horizons give more time for intervention, but they observe much less assessment evidence. This is the central trade-off that notebook 06 evaluates formally.

## 6. Segmentation and Recommendation Story

Notebook `05_segmentation_recommendation.ipynb` remains the project's interpretability layer.

### 6.1 Final learner segments

Use these four clusters:

1. `Inactive Drop-offs`
2. `Sporadic Explorers`
3. `Steady Progressors`
4. `Focused Achievers`

### 6.2 Cluster summary

| Cluster | Enrollments | Share | At-risk rate |
|---|---:|---:|---:|
| Steady Progressors | `17,047` | `52.3%` | `39.43%` |
| Sporadic Explorers | `8,476` | `26.0%` | `60.82%` |
| Inactive Drop-offs | `5,018` | `15.4%` | `93.08%` |
| Focused Achievers | `2,052` | `6.3%` | `32.16%` |

### 6.3 Recommendation layer

Most common paths:

- `Consistency Building Path`: `11,133`
- `Early Start Path`: `7,108`
- `Assessment Recovery Path`: `5,613`
- `Mastery Improvement Path`: `5,145`

Suggested wording:

> The recommendation engine translates observed behavioral gaps into actionable learning paths rather than only ranking abstract content items.

## 7. Multi-Horizon Modeling Story

Notebook `06_at_risk_modeling.ipynb` is now the center of the research contribution.

### 7.1 Candidate models

State that the study compares:

- `Logistic Regression`
- `Random Forest`
- `XGBoost`

across all four horizons.

### 7.2 Threshold selection rule

Use this exactly:

1. Use the validation split only
2. Keep thresholds with `recall >= 0.90`
3. Among those, choose the highest `precision`
4. Break ties with `F2`, then `PR-AUC`

This is an important defense point because it explains why the project does not use the default threshold of `0.50`.

### 7.3 Earliest useful horizon

Use this sentence:

> A useful early-warning signal already appears at day 7. The best day-7 operating point is Logistic Regression with validation recall `0.9393`, precision `0.5771`, and PR-AUC `0.7592`. This makes day 7 a credible earliest intervention checkpoint even though later horizons rank learners more accurately.

### 7.4 Horizon comparison summary

Use the best model for each horizon:

| Horizon | Best Pair | Validation Recall | Validation Precision | Validation PR-AUC |
|---|---|---:|---:|---:|
| Day 7 | Logistic Regression | `0.9393` | `0.5771` | `0.7592` |
| Day 14 | XGBoost | `0.9372` | `0.5794` | `0.8012` |
| Day 21 | XGBoost | `0.9311` | `0.6122` | `0.8432` |
| Day 30 | XGBoost | `0.9253` | `0.6278` | `0.8639` |

Interpretation:

> The ranking quality improves steadily from day 7 to day 30, while recall remains high throughout. That confirms the expected research trade-off: later horizons are stronger, but earlier horizons remain operationally useful.

### 7.5 Final champion pair

Champion: `XGBoost @ day 30`, threshold `0.25`

Held-out test metrics:

| Metric | Value |
|---|---:|
| Accuracy | `0.6777` |
| Precision | `0.6313` |
| Recall | `0.9367` |
| F1 | `0.7542` |
| F2 | `0.8540` |
| ROC-AUC | `0.8467` |
| PR-AUC | `0.8766` |
| Brier score | `0.1580` |

Suggested model-choice explanation:

> The final champion was selected from validation performance, not from test hindsight. XGBoost at day 30 offered the strongest PR-AUC and F2 among the high-recall operating points, while earlier horizons remained part of the evidence base to show how predictive quality evolves over time.

## 8. Ablation Story

This is one of the biggest upgrades in the project.

### 8.1 Why ablation was added

Use this sentence:

> Ablation was introduced to test whether the model's value comes mainly from demographics, engagement, assessment behavior, or their combination.

### 8.2 Main ablation findings

At `day 14`:

- Full feature set test PR-AUC: `0.8114`
- Engagement + assessment: `0.7689`
- Engagement only: `0.7583`
- Demographics only: `0.6666`
- Assessment only: `0.5561`

At `day 30`:

- Full feature set test PR-AUC: `0.8766`
- Engagement + assessment: `0.8472`
- Engagement only: `0.8033`
- Assessment only: `0.7431`
- Demographics only: `0.6666`

Interpretation:

> The full model clearly outperforms weaker feature subsets, and the biggest practical lift comes from combining engagement and assessment evidence. Demographics alone are not competitive, which is a strong result for both methodology and educational interpretation.

## 9. Calibration and Risk Bands

This section is new and should be highlighted in the report.

### 9.1 Why calibration matters

Use this wording:

> Early-warning systems are used to prioritize intervention, which depends on probability quality rather than only on a binary label. For that reason, the project evaluates calibration and converts final probabilities into operational risk bands.

### 9.2 Final risk bands

| Risk Band | Learners | Actual At-Risk Rate | Avg Predicted Probability |
|---|---:|---:|---:|
| Low | `1,412` | `15.4%` | `0.159` |
| Medium | `1,971` | `35.3%` | `0.366` |
| High | `1,232` | `62.2%` | `0.622` |
| Critical | `1,904` | `92.5%` | `0.922` |

Interpretation:

> The risk tiers are well ordered. As predicted risk increases, the realized at-risk rate increases sharply, which makes the output suitable for watchlists and intervention prioritization.

## 10. Main Predictive Signals

Top global importance signals in the champion model:

1. `avg_score`
2. `studied_credits`
3. `days_since_last`
4. `avg_submission_delay`
5. `assessment_discipline`

Use this interpretation:

> Academic quality, engagement recency, and submission timing matter together. The model is not driven by one simple proxy such as clicks alone.

## 11. Segment-Level Diagnostics

Use these lines:

- `Inactive Drop-offs`: actual at-risk rate `93.0%`, recall `1.0000`
- `Sporadic Explorers`: actual at-risk rate `61.6%`, recall `0.9778`
- `Steady Progressors`: actual at-risk rate `38.9%`, recall `0.8827`
- `Focused Achievers`: actual at-risk rate `33.5%`, recall `0.7163`

Suggested interpretation:

> The model is strongest in clearly vulnerable clusters and weaker in the more ambiguous high-functioning group. That is acceptable for an early-warning system designed to catch disengagement aggressively.

## 12. Reliability and Marketing Deployment Diagnostics

These sections strengthen the project beyond a normal classifier by showing whether the model can support an actual data-driven marketing or learner retention workflow.

### 12.1 Bootstrap confidence intervals

Use these held-out test-set intervals:

| Metric | Point estimate | 95% CI lower | 95% CI upper |
|---|---:|---:|---:|
| Precision | `0.6313` | `0.6173` | `0.6442` |
| Recall | `0.9367` | `0.9281` | `0.9447` |
| F1 | `0.7542` | `0.7435` | `0.7648` |
| ROC-AUC | `0.8467` | `0.8369` | `0.8559` |
| PR-AUC | `0.8766` | `0.8673` | `0.8865` |

Interpretation:

> The confidence intervals are narrow enough to support the claim that the champion model is stable on the held-out test set, especially for recall and PR-AUC.

### 12.2 Subgroup and fairness checks

Use these points:

- Recall stays above the `0.90` target across gender, disability, IMD, and prior-attempt slices.
- The high-IMD group is closest to the recall floor at about `0.9040`, so it should be monitored if the system is used operationally.
- Re-attempt learners show weaker ROC-AUC at about `0.7625`, which suggests that ranking quality is less stable for this subgroup even though recall is high.

Suggested wording:

> The model does not show an immediate recall failure in the checked subgroups, but the diagnostic table identifies where monitoring should focus before any real intervention rollout.

### 12.3 Risk trajectory and threshold cost-benefit

Use these points:

- The risk-signal trajectory shows that at-risk and non-at-risk learners already separate by day 7 on engagement and risk-index features.
- The selected threshold `0.25` preserves high recall but flags about `77.8%` of the validation cohort.
- This creates an advisor-capacity trade-off: a stricter threshold reduces review load but misses more at-risk learners.

Suggested wording:

> In marketing terms, the model creates a targeting list, but threshold choice is a campaign-capacity decision. The dashboard therefore reports both predictive quality and expected review load.

### 12.4 SHAP explainability

Notebook `06` retrains the champion XGBoost model and produces SHAP outputs when the optional `shap` package is installed. Use this as an advanced interpretability point:

> SHAP supports individual-level explanations for advisor dashboards, while the fallback native importance keeps the notebook reproducible even without optional dependencies.

## 13. A/B Testing and Experiment Readiness

This section was added to close the methodological gap between offline prediction and causal validation.

Use this sentence:

> The model and recommendation layer identify who should be prioritized, but A/B testing is required to prove whether the intervention itself causes better learner outcomes.

### 13.1 Experiment design

- Experiment ID: `risk_targeted_personalized_intervention_ab_test`
- Randomization unit: student-course enrollment
- Control: standard learner support
- Treatment: risk-targeted personalized intervention
- Primary metric: `retention_success`
- Secondary metrics: recommendation score, risk probability, risk-band mix, intervention path uptake
- Guardrail metrics: advisor review load, false-alert ratio, subgroup recall monitoring

### 13.2 Readiness checks

- Eligible learners: `5,107`
- Control group: `2,554`
- Treatment group: `2,553`
- SRM p-value: `0.9888`, so the planned 50/50 split passes the sample-ratio mismatch check
- Historical baseline retention success among flagged learners: `0.3687`
- Minimum detectable effect with current sample: `0.0382`

### 13.3 Power and decision rule

The current offline sample is not large enough to reliably detect a `+3%` absolute lift at 80% power, but it is large enough for `+5%`, `+8%`, and `+10%` scenarios.

Use this sentence:

> The recommended decision rule follows the lecture logic: deploy only if `p_value < 0.05`, the 95% confidence interval excludes zero, and the lift is large enough to matter operationally.

The simulated `+5%` lift scenario has p-value `0.00026`, 95% CI `[+2.32%, +7.66%]`, and passes the business decision rule.

Important limitation:

> This is an A/B test design and offline simulation, not a completed live experiment. A real rollout would still need live randomized traffic and post-intervention outcome tracking.

## 14. Managerial Implications

### 14.1 For instructors

- Treat `day 7` as the earliest viable warning checkpoint
- Treat `day 30` as the strongest ranking checkpoint
- Prioritize `Inactive Drop-offs` and `Sporadic Explorers` for intervention
- Use recommendation paths to assign differentiated next actions

### 14.2 For program managers

- Compare module-level risk burden before assigning support resources
- Use the risk bands instead of a single yes/no flag when triaging learners
- Monitor the `Critical` risk band first because its realized at-risk rate is already above `92%`
- Tune the operating threshold based on available advisor capacity
- Use the A/B testing table to decide whether intervention lift is statistically and practically meaningful before full rollout

### 14.3 For platform design

- Push engagement prompts very early
- Surface assessment actions more visibly
- Reduce delays between weak early behavior and instructor outreach
- Track subgroup performance after deployment to avoid hidden targeting gaps

## 15. Limitations

Use these points:

- The target combines `Fail` and `Withdrawn`, which is useful operationally but broad
- Recommendations are prototype-based rather than causal
- A/B testing is currently a ready-to-launch design and simulation, not a completed live RCT
- Calibration is evaluated on one dataset only
- Subgroup diagnostics are observational fairness checks, not proof of causal fairness
- External validation would still be needed before production deployment

## 16. Suggested Report Structure

1. Introduction
2. Research objectives and questions
3. Dataset and methodology
4. Data cleaning and integration
5. Exploratory data analysis
6. Multi-horizon feature engineering
7. Segmentation and personalized recommendation
8. Multi-horizon at-risk modeling
9. Ablation and calibration analysis
10. Reliability, subgroup, and explainability diagnostics
11. Power BI dashboard and intervention design
12. A/B testing and experiment readiness
13. Managerial implications
14. Limitations and future work
15. Conclusion

## 17. Defense Q&A

### Why not use threshold `0.50`?

Because the project is an early-warning problem. Missing an at-risk learner is more costly than reviewing an extra flagged learner, so thresholds were selected on validation data to maintain recall above `0.90`.

### Why compare multiple horizons instead of only day 30?

Because intervention value depends on time. A day-30 model may be stronger, but a day-7 model is more actionable. The project needed to show both.

### Why is day 7 called the earliest useful horizon?

Because day 7 already reaches validation recall `0.9393` with nontrivial precision and PR-AUC, which makes it usable for early triage even though later horizons are stronger.

### Why choose XGBoost at day 30 as champion?

Because after enforcing the recall target, it delivered the strongest validation PR-AUC and F2 among the candidate horizon-model pairs, and the choice was locked before looking at the final test summary.

### What does ablation prove?

It proves that demographics alone are weak, while the combination of engagement and assessment features creates most of the predictive value.

### Why add calibration and risk bands?

Because interventions are prioritized by risk level, not only by hard class labels. Calibration shows whether the probabilities are trustworthy enough to support that prioritization.

### Why add A/B testing if the dataset is historical?

Because the offline model only proves prediction quality, not causal intervention impact. The project therefore adds a ready-to-launch randomized experiment design with control/treatment assignment, SRM check, power/MDE planning, p-values, confidence intervals, and a business decision rule.

### Why add confidence intervals?

Because single test-set metrics can look stronger or weaker by sampling chance. Bootstrap confidence intervals show whether the champion performance is stable enough to defend.

### Why include subgroup analysis?

Because a retention model can perform well on average while under-serving a subgroup. The checked subgroup recalls remain above the target, but the high-IMD and re-attempt diagnostics deserve monitoring.

### Why is threshold choice a marketing decision?

Because threshold choice controls the size of the outreach list. A lower threshold catches more at-risk learners but creates more false alerts and advisor workload.
