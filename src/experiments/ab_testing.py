from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chisquare, norm

KEY = ["id_student", "code_module", "code_presentation"]
EXPERIMENT_ID = "risk_targeted_personalized_intervention_ab_test"
PRIMARY_METRIC = "retention_success"
ELIGIBILITY_RULE = "champion_model_predicted_at_risk"
TREATMENT_LABEL = "Treatment: risk-targeted personalized intervention"
CONTROL_LABEL = "Control: standard learner support"
AB_TEST_FILENAMES = {
    "ab_test_experiment_design": "ab_test_experiment_design.csv",
    "ab_test_assignment": "ab_test_assignment.csv",
    "ab_test_srm_check": "ab_test_srm_check.csv",
    "ab_test_balance": "ab_test_balance.csv",
    "ab_test_power_analysis": "ab_test_power_analysis.csv",
    "ab_test_simulated_results": "ab_test_simulated_results.csv",
}
DEFAULT_EFFECT_SCENARIOS = (0.03, 0.05, 0.08, 0.10)
BALANCE_NUMERIC_FEATURES = ("risk_probability", "recommendation_score")
BALANCE_CATEGORICAL_FEATURES = ("risk_band", "recommended_path", "cluster_label", "code_module")


@dataclass
class ABTestingTables:
    ab_test_experiment_design: pd.DataFrame
    ab_test_assignment: pd.DataFrame
    ab_test_srm_check: pd.DataFrame
    ab_test_balance: pd.DataFrame
    ab_test_power_analysis: pd.DataFrame
    ab_test_simulated_results: pd.DataFrame


def _read_csv(processed_dir: Path, name: str) -> pd.DataFrame:
    path = processed_dir / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required input table: {path}")
    return pd.read_csv(path, low_memory=False)


def _validate_prediction_table(preds: pd.DataFrame) -> None:
    required_columns = {
        *KEY,
        "y_true",
        "y_pred",
        "risk_probability",
        "risk_band",
        "recommended_path",
        "cluster_label",
        "recommendation_score",
    }
    missing_columns = required_columns.difference(preds.columns)
    if missing_columns:
        raise KeyError(f"risk_band_test_predictions.csv is missing columns required for A/B testing: {sorted(missing_columns)}")


def _stratified_assignment(
    eligible: pd.DataFrame,
    *,
    random_state: int,
    treatment_share: float,
) -> pd.Series:
    if not 0 < treatment_share < 1:
        raise ValueError("treatment_share must be between 0 and 1.")

    rng = np.random.default_rng(seed=random_state)
    variants = pd.Series("control", index=eligible.index, dtype="object")
    strata = eligible[["risk_band", "recommended_path"]].fillna("Unknown").astype(str)

    for _, group_index in strata.groupby(["risk_band", "recommended_path"], sort=True).groups.items():
        shuffled = np.asarray(list(group_index))
        rng.shuffle(shuffled)
        n_treatment = int(np.floor(len(shuffled) * treatment_share))
        if len(shuffled) > 1 and n_treatment == 0:
            n_treatment = 1
        fractional_part = (len(shuffled) * treatment_share) - n_treatment
        if fractional_part > 0 and rng.random() < fractional_part:
            n_treatment += 1
        variants.loc[shuffled[:n_treatment]] = "treatment"

    return variants


def build_ab_test_assignment(
    processed_dir: Path,
    *,
    random_state: int = 42,
    treatment_share: float = 0.5,
) -> pd.DataFrame:
    preds = _read_csv(processed_dir, "risk_band_test_predictions.csv")
    _validate_prediction_table(preds)

    eligible = preds.loc[preds["y_pred"].astype(int).eq(1)].copy()
    if eligible.empty:
        raise ValueError("No eligible learners found for A/B testing. Expected at least one champion-model at-risk prediction.")

    sort_columns = [*KEY, "risk_band", "recommended_path"]
    eligible = eligible.sort_values(sort_columns).reset_index(drop=True)
    eligible["variant"] = _stratified_assignment(
        eligible,
        random_state=random_state,
        treatment_share=treatment_share,
    ).to_numpy()
    eligible["variant_label"] = np.where(
        eligible["variant"].eq("treatment"),
        TREATMENT_LABEL,
        CONTROL_LABEL,
    )
    eligible["experiment_id"] = EXPERIMENT_ID
    eligible["assignment_unit"] = "student-course enrollment"
    eligible["eligibility_rule"] = ELIGIBILITY_RULE
    eligible["primary_metric"] = PRIMARY_METRIC
    eligible["primary_metric_observed"] = 1 - eligible["y_true"].astype(int)
    eligible["historical_outcome_note"] = "Observed historical outcome; use only for offline randomization checks before a real intervention trial."
    eligible["stratification_key"] = (
        eligible["risk_band"].fillna("Unknown").astype(str)
        + " | "
        + eligible["recommended_path"].fillna("Unknown").astype(str)
    )
    eligible["random_state"] = random_state

    ordered_columns = [
        "experiment_id",
        "assignment_unit",
        "eligibility_rule",
        "variant",
        "variant_label",
        "primary_metric",
        "primary_metric_observed",
        "historical_outcome_note",
        "stratification_key",
        "random_state",
        *KEY,
        "horizon_day",
        "model",
        "selected_threshold",
        "y_true",
        "risk_probability",
        "y_pred",
        "risk_band",
        "final_result",
        "cluster_label",
        "rule_segment",
        "recommended_path",
        "action_1",
        "action_2",
        "action_3",
        "recommendation_score",
        "prediction_outcome",
    ]
    existing_ordered_columns = [column for column in ordered_columns if column in eligible.columns]
    remaining_columns = [column for column in eligible.columns if column not in existing_ordered_columns]
    return eligible[existing_ordered_columns + remaining_columns]


def build_ab_test_experiment_design(
    assignment: pd.DataFrame,
    *,
    minimum_practical_lift: float = 0.03,
) -> pd.DataFrame:
    total_eligible = len(assignment)
    treatment_n = int(assignment["variant"].eq("treatment").sum())
    control_n = int(assignment["variant"].eq("control").sum())
    baseline_success_rate = float(assignment["primary_metric_observed"].mean())
    return pd.DataFrame(
        [
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "business_question",
                "value": "Does risk-targeted personalized intervention improve retention among learners flagged by the champion model?",
                "lecture_alignment": "A/B testing is used to move from prediction to causal validation.",
            },
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "randomization_unit",
                "value": "student-course enrollment",
                "lecture_alignment": "User-level assignment keeps the learner experience consistent.",
            },
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "control_group",
                "value": CONTROL_LABEL,
                "lecture_alignment": "Control receives the current baseline experience.",
            },
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "treatment_group",
                "value": TREATMENT_LABEL,
                "lecture_alignment": "Treatment receives the new ML-driven intervention.",
            },
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "primary_metric",
                "value": f"{PRIMARY_METRIC}: pass/not-at-risk outcome after intervention",
                "lecture_alignment": "One primary metric decides win/loss.",
            },
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "secondary_metrics",
                "value": "recommendation_score, risk_probability, risk_band mix, intervention path uptake",
                "lecture_alignment": "Secondary metrics explain why the primary metric changes.",
            },
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "guardrail_metrics",
                "value": "advisor review load, false alert ratio, subgroup recall monitoring",
                "lecture_alignment": "Guardrails prevent a statistically positive test from creating operational harm.",
            },
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "sample_size_base",
                "value": f"{total_eligible} eligible flagged learners: {control_n} control and {treatment_n} treatment",
                "lecture_alignment": "Sample size is calculated before launch, not after peeking at results.",
            },
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "baseline_rate",
                "value": f"Historical retention_success among eligible flagged learners = {baseline_success_rate:.4f}",
                "lecture_alignment": "p1 comes from historical control data for binary metrics.",
            },
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "minimum_duration_rule",
                "value": "Run in multiples of 7 days, ideally at least 28 days if live traffic allows the required sample.",
                "lecture_alignment": "Duration should cover day-of-week effects.",
            },
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "decision_rule",
                "value": f"Deploy only if p_value < 0.05, 95% CI excludes 0, and absolute lift >= {minimum_practical_lift:.0%}.",
                "lecture_alignment": "Decision requires both statistical significance and business significance.",
            },
            {
                "experiment_id": EXPERIMENT_ID,
                "design_component": "pitfall_checks",
                "value": "SRM check, no peeking, no uncontrolled multiple testing, monitor spillover/network effects.",
                "lecture_alignment": "SRM, peeking bias, multiple testing, and network effects are practical A/B traps.",
            },
        ]
    )


def build_ab_test_srm_check(
    assignment: pd.DataFrame,
    *,
    expected_treatment_share: float = 0.5,
    alpha: float = 0.05,
) -> pd.DataFrame:
    if not 0 < expected_treatment_share < 1:
        raise ValueError("expected_treatment_share must be between 0 and 1.")

    observed = assignment["variant"].value_counts().reindex(["control", "treatment"], fill_value=0)
    total = int(observed.sum())
    expected = np.asarray(
        [
            total * (1 - expected_treatment_share),
            total * expected_treatment_share,
        ],
        dtype=float,
    )
    statistic, p_value = chisquare(f_obs=observed.to_numpy(dtype=float), f_exp=expected)
    return pd.DataFrame(
        [
            {
                "experiment_id": EXPERIMENT_ID,
                "check_name": "sample_ratio_mismatch",
                "statistical_test": "chi-square goodness-of-fit",
                "expected_control_share": 1 - expected_treatment_share,
                "expected_treatment_share": expected_treatment_share,
                "observed_control_n": int(observed["control"]),
                "observed_treatment_n": int(observed["treatment"]),
                "observed_control_share": float(observed["control"] / total),
                "observed_treatment_share": float(observed["treatment"] / total),
                "chi_square_statistic": float(statistic),
                "p_value": float(p_value),
                "alpha": alpha,
                "passed_srm_check": bool(p_value >= alpha),
                "interpretation": "Pass: observed traffic split is consistent with the planned ratio."
                if p_value >= alpha
                else "Fail: observed traffic split suggests sample-ratio mismatch.",
            }
        ]
    )


def _standardized_mean_difference(control: pd.Series, treatment: pd.Series) -> float:
    control_values = pd.to_numeric(control, errors="coerce").dropna()
    treatment_values = pd.to_numeric(treatment, errors="coerce").dropna()
    if control_values.empty or treatment_values.empty:
        return np.nan
    pooled_variance = (control_values.var(ddof=1) + treatment_values.var(ddof=1)) / 2
    if not np.isfinite(pooled_variance) or pooled_variance <= 0:
        return 0.0
    return float((treatment_values.mean() - control_values.mean()) / np.sqrt(pooled_variance))


def _proportion_standardized_difference(control_rate: float, treatment_rate: float) -> float:
    pooled_rate = (control_rate + treatment_rate) / 2
    variance = pooled_rate * (1 - pooled_rate)
    if variance <= 0:
        return 0.0
    return float((treatment_rate - control_rate) / np.sqrt(variance))


def build_ab_test_balance(assignment: pd.DataFrame) -> pd.DataFrame:
    control_mask = assignment["variant"].eq("control")
    treatment_mask = assignment["variant"].eq("treatment")
    if not control_mask.any() or not treatment_mask.any():
        raise ValueError("A/B assignment must contain both control and treatment learners.")

    rows: list[dict[str, object]] = []
    for feature in BALANCE_NUMERIC_FEATURES:
        if feature not in assignment.columns:
            continue
        control = pd.to_numeric(assignment.loc[control_mask, feature], errors="coerce")
        treatment = pd.to_numeric(assignment.loc[treatment_mask, feature], errors="coerce")
        control_mean = float(control.mean())
        treatment_mean = float(treatment.mean())
        smd = _standardized_mean_difference(control, treatment)
        rows.append(
            {
                "feature_type": "numeric",
                "feature": feature,
                "level": "overall",
                "control_n": int(control.notna().sum()),
                "treatment_n": int(treatment.notna().sum()),
                "control_rate_or_mean": control_mean,
                "treatment_rate_or_mean": treatment_mean,
                "absolute_difference": treatment_mean - control_mean,
                "standardized_difference": smd,
                "passed_balance_check": bool(abs(smd) <= 0.10) if np.isfinite(smd) else False,
            }
        )

    for feature in BALANCE_CATEGORICAL_FEATURES:
        if feature not in assignment.columns:
            continue
        levels = sorted(assignment[feature].fillna("Unknown").astype(str).unique())
        for level in levels:
            control_rate = float(assignment.loc[control_mask, feature].fillna("Unknown").astype(str).eq(level).mean())
            treatment_rate = float(assignment.loc[treatment_mask, feature].fillna("Unknown").astype(str).eq(level).mean())
            std_diff = _proportion_standardized_difference(control_rate, treatment_rate)
            rows.append(
                {
                    "feature_type": "categorical",
                    "feature": feature,
                    "level": level,
                    "control_n": int(control_mask.sum()),
                    "treatment_n": int(treatment_mask.sum()),
                    "control_rate_or_mean": control_rate,
                    "treatment_rate_or_mean": treatment_rate,
                    "absolute_difference": treatment_rate - control_rate,
                    "standardized_difference": std_diff,
                    "passed_balance_check": bool(abs(std_diff) <= 0.10),
                }
            )

    return pd.DataFrame(rows)


def _required_n_per_group_for_two_proportions(
    baseline_rate: float,
    absolute_lift: float,
    *,
    alpha: float,
    target_power: float,
) -> int:
    if not 0 < baseline_rate < 1:
        raise ValueError("baseline_rate must be between 0 and 1.")
    if absolute_lift <= 0:
        raise ValueError("absolute_lift must be positive.")

    treatment_rate = min(baseline_rate + absolute_lift, 0.999)
    effect_size = treatment_rate - baseline_rate
    pooled_rate = (baseline_rate + treatment_rate) / 2
    z_alpha = norm.ppf(1 - alpha / 2)
    z_power = norm.ppf(target_power)
    numerator = (
        z_alpha * np.sqrt(2 * pooled_rate * (1 - pooled_rate))
        + z_power * np.sqrt(baseline_rate * (1 - baseline_rate) + treatment_rate * (1 - treatment_rate))
    )
    return int(np.ceil((numerator / effect_size) ** 2))


def _available_power_for_two_proportions(
    baseline_rate: float,
    absolute_lift: float,
    *,
    n_per_group: int,
    alpha: float,
) -> float:
    treatment_rate = min(baseline_rate + absolute_lift, 0.999)
    effect_size = treatment_rate - baseline_rate
    pooled_rate = (baseline_rate + treatment_rate) / 2
    se_null = np.sqrt(2 * pooled_rate * (1 - pooled_rate) / n_per_group)
    se_alt = np.sqrt((baseline_rate * (1 - baseline_rate) + treatment_rate * (1 - treatment_rate)) / n_per_group)
    if se_null <= 0 or se_alt <= 0:
        return np.nan
    critical = norm.ppf(1 - alpha / 2) * se_null
    return float(norm.cdf((-critical - effect_size) / se_alt) + 1 - norm.cdf((critical - effect_size) / se_alt))


def _minimum_detectable_effect(
    baseline_rate: float,
    *,
    n_per_group: int,
    alpha: float,
    target_power: float,
) -> float:
    low = 1e-4
    high = min(0.999 - baseline_rate, 0.50)
    for _ in range(60):
        mid = (low + high) / 2
        required_n = _required_n_per_group_for_two_proportions(
            baseline_rate,
            mid,
            alpha=alpha,
            target_power=target_power,
        )
        if required_n <= n_per_group:
            high = mid
        else:
            low = mid
    return float(high)


def build_ab_test_power_analysis(
    assignment: pd.DataFrame,
    *,
    effect_scenarios: tuple[float, ...] = DEFAULT_EFFECT_SCENARIOS,
    alpha: float = 0.05,
    target_power: float = 0.80,
) -> pd.DataFrame:
    baseline_rate = float(assignment["primary_metric_observed"].mean())
    variant_counts = assignment["variant"].value_counts()
    available_n_per_group = int(variant_counts.min())
    mde = _minimum_detectable_effect(
        baseline_rate,
        n_per_group=available_n_per_group,
        alpha=alpha,
        target_power=target_power,
    )

    rows: list[dict[str, object]] = []
    for absolute_lift in effect_scenarios:
        required_n_per_group = _required_n_per_group_for_two_proportions(
            baseline_rate,
            absolute_lift,
            alpha=alpha,
            target_power=target_power,
        )
        rows.append(
            {
                "experiment_id": EXPERIMENT_ID,
                "primary_metric": PRIMARY_METRIC,
                "baseline_success_rate": baseline_rate,
                "baseline_source": "historical success rate among champion-model flagged learners",
                "absolute_lift": absolute_lift,
                "relative_mde": absolute_lift / baseline_rate,
                "treatment_success_rate": min(baseline_rate + absolute_lift, 0.999),
                "alpha": alpha,
                "target_power": target_power,
                "required_n_per_group": required_n_per_group,
                "required_total_n": required_n_per_group * 2,
                "available_n_per_group": available_n_per_group,
                "available_total_n": int(len(assignment)),
                "available_power": _available_power_for_two_proportions(
                    baseline_rate,
                    absolute_lift,
                    n_per_group=available_n_per_group,
                    alpha=alpha,
                ),
                "minimum_detectable_effect": mde,
                "feasible_with_current_sample": bool(available_n_per_group >= required_n_per_group),
            }
        )

    return pd.DataFrame(rows)


def _two_proportion_test(
    control_successes: int,
    control_n: int,
    treatment_successes: int,
    treatment_n: int,
) -> dict[str, float]:
    control_rate = control_successes / control_n
    treatment_rate = treatment_successes / treatment_n
    absolute_lift = treatment_rate - control_rate
    pooled_rate = (control_successes + treatment_successes) / (control_n + treatment_n)
    pooled_se = np.sqrt(pooled_rate * (1 - pooled_rate) * (1 / control_n + 1 / treatment_n))
    z_score = absolute_lift / pooled_se if pooled_se > 0 else np.nan
    p_value = 2 * (1 - norm.cdf(abs(z_score))) if np.isfinite(z_score) else np.nan
    ci_se = np.sqrt(
        control_rate * (1 - control_rate) / control_n
        + treatment_rate * (1 - treatment_rate) / treatment_n
    )
    ci_margin = norm.ppf(0.975) * ci_se
    return {
        "control_success_rate": float(control_rate),
        "treatment_success_rate": float(treatment_rate),
        "absolute_lift": float(absolute_lift),
        "relative_lift": float(absolute_lift / control_rate) if control_rate > 0 else np.nan,
        "ci_95_lower": float(absolute_lift - ci_margin),
        "ci_95_upper": float(absolute_lift + ci_margin),
        "z_score": float(z_score),
        "p_value": float(p_value),
        "significant_at_05": bool(p_value < 0.05) if np.isfinite(p_value) else False,
    }


def build_ab_test_simulated_results(
    assignment: pd.DataFrame,
    *,
    effect_scenarios: tuple[float, ...] = DEFAULT_EFFECT_SCENARIOS,
    random_state: int = 42,
    minimum_practical_lift: float = 0.03,
) -> pd.DataFrame:
    control = assignment.loc[assignment["variant"].eq("control")]
    treatment = assignment.loc[assignment["variant"].eq("treatment")]
    if control.empty or treatment.empty:
        raise ValueError("A/B assignment must contain both control and treatment learners.")

    control_n = len(control)
    treatment_n = len(treatment)
    control_successes = int(control["primary_metric_observed"].sum())
    treatment_successes = int(treatment["primary_metric_observed"].sum())

    historical_test = _two_proportion_test(
        control_successes=control_successes,
        control_n=control_n,
        treatment_successes=treatment_successes,
        treatment_n=treatment_n,
    )
    rows: list[dict[str, object]] = [
        {
            "experiment_id": EXPERIMENT_ID,
            "scenario": "A/A historical randomization check",
            "scenario_type": "historical_check",
            "n_control": control_n,
            "n_treatment": treatment_n,
            "statistical_test": "two-sided two-proportion z-test",
            "control_successes": control_successes,
            "treatment_successes": treatment_successes,
            "expected_additional_successes": treatment_successes - (historical_test["control_success_rate"] * treatment_n),
            "minimum_practical_lift": minimum_practical_lift,
            "decision_rule": f"Deploy if p_value < 0.05 and absolute_lift >= {minimum_practical_lift:.0%}.",
            "business_decision": "Hold: historical A/A check is for randomization quality, not treatment launch.",
            "random_state": random_state,
            **historical_test,
        }
    ]

    baseline_rate = historical_test["control_success_rate"]
    for absolute_lift in effect_scenarios:
        simulated_treatment_rate = min(baseline_rate + absolute_lift, 0.999)
        simulated_treatment_successes = int(round(simulated_treatment_rate * treatment_n))
        scenario_test = _two_proportion_test(
            control_successes=control_successes,
            control_n=control_n,
            treatment_successes=simulated_treatment_successes,
            treatment_n=treatment_n,
        )
        rows.append(
            {
                "experiment_id": EXPERIMENT_ID,
                "scenario": f"Simulated intervention lift +{absolute_lift:.0%}",
                "scenario_type": "simulated_lift",
                "n_control": control_n,
                "n_treatment": treatment_n,
                "statistical_test": "two-sided two-proportion z-test",
                "control_successes": control_successes,
                "treatment_successes": simulated_treatment_successes,
                "expected_additional_successes": scenario_test["absolute_lift"] * treatment_n,
                "minimum_practical_lift": minimum_practical_lift,
                "decision_rule": f"Deploy if p_value < 0.05 and absolute_lift >= {minimum_practical_lift:.0%}.",
                "business_decision": "Deploy"
                if scenario_test["p_value"] < 0.05 and scenario_test["absolute_lift"] >= minimum_practical_lift
                else "Do not deploy",
                "random_state": random_state,
                **scenario_test,
            }
        )

    return pd.DataFrame(rows)


def build_ab_testing_tables(
    processed_dir: Path,
    *,
    write_outputs: bool = True,
    random_state: int = 42,
    treatment_share: float = 0.5,
    effect_scenarios: tuple[float, ...] = DEFAULT_EFFECT_SCENARIOS,
    minimum_practical_lift: float = 0.03,
) -> ABTestingTables:
    processed_dir = Path(processed_dir)
    assignment = build_ab_test_assignment(
        processed_dir,
        random_state=random_state,
        treatment_share=treatment_share,
    )
    tables = ABTestingTables(
        ab_test_experiment_design=build_ab_test_experiment_design(
            assignment,
            minimum_practical_lift=minimum_practical_lift,
        ),
        ab_test_assignment=assignment,
        ab_test_srm_check=build_ab_test_srm_check(
            assignment,
            expected_treatment_share=treatment_share,
        ),
        ab_test_balance=build_ab_test_balance(assignment),
        ab_test_power_analysis=build_ab_test_power_analysis(
            assignment,
            effect_scenarios=effect_scenarios,
        ),
        ab_test_simulated_results=build_ab_test_simulated_results(
            assignment,
            effect_scenarios=effect_scenarios,
            random_state=random_state,
            minimum_practical_lift=minimum_practical_lift,
        ),
    )

    if write_outputs:
        for attr_name, filename in AB_TEST_FILENAMES.items():
            getattr(tables, attr_name).to_csv(processed_dir / filename, index=False)

    return tables
