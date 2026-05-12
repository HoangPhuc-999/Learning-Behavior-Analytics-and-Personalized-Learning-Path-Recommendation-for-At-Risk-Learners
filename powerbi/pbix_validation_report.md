# Power BI PBIX Validation Report

Validated file: `powerbi/final_share.pbix`

Source file checked: `powerbi/final_share.pbix`

Validation date: `2026-05-09`

## Summary

No blocking metric issue was found. The PBIX data model contains the expected final dashboard tables and the headline metrics align with the repository CSV outputs and final report.

## Structure Checks

- PBIX opens as a valid archive with `Report/Layout` and `DataModel`.
- Report contains `16` pages.
- Data model contains `32` imported/model tables plus DAX dimension tables.
- Main CSV-backed tables match the repository outputs after accounting for expected Power Query transforms:
  - `EnrollmentKey` added to enrollment-grain tables.
  - `Risk Status` added to `features_final`.
  - `threshold_search_by_horizon` unpivoted from wide metric columns into `metric` and `value`.

## Key Metric Checks

- Final analytic sample: `32,593` enrollments.
- Unique learners: `28,785`.
- Final result counts:
  - `Pass`: `12,361`
  - `Withdrawn`: `10,156`
  - `Fail`: `7,052`
  - `Distinction`: `3,024`
- At-risk rate: `52.8%`.
- Champion model: `XGBoost @ day 30`, threshold `0.25`.
- Held-out test metrics:
  - accuracy: `0.6777`
  - precision: `0.6313`
  - recall: `0.9367`
  - F2: `0.8540`
  - ROC-AUC: `0.8467`
  - PR-AUC: `0.8766`
- Risk band actual at-risk rates:
  - `Low`: `15.4%`
  - `Medium`: `35.3%`
  - `High`: `62.2%`
  - `Critical`: `92.5%`
- A/B eligible learner-enrollments: `5,107`.
- A/B split: `2,554` control and `2,553` treatment.
- SRM p-value: `0.9888`.
- Minimum detectable effect: `3.82%`.

## Non-Blocking Notes

1. Power Query source paths inside the PBIX point to an absolute Windows path under `C:\Users\0916h\OneDrive\...`. The embedded model data is present, so the report can be viewed, but refresh on another machine will require repointing the CSV folder in Power BI Desktop.
2. A few feature columns in `features_final` and `personalized_learning_paths` are typed as whole numbers in Power Query:
   - `avg_submission_delay`
   - `avg_score`
   - `score_std`

   The maximum row-level rounding difference is about `0.5`, and the aggregate mean differences are negligible for dashboard-level interpretation. The final model metrics and exported research tables are not affected.
3. Blank text fields in several action/gap columns appear as empty strings in Power BI and as missing values in CSV. This is a display/typing difference, not a metric mismatch.

## Recommendation

The PBIX is acceptable for final submission. If there is time before a live demo, open the report in Power BI Desktop and repoint the data source folder to this repository's `data/processed/` directory so refresh works on the presentation machine.
