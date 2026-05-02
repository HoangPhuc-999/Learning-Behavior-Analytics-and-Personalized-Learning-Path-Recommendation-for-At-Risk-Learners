from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score

KEY = ["id_student", "code_module", "code_presentation"]
HORIZONS = (7, 14, 21, 30)
TARGET_RECALL = 0.90
BOOTSTRAP_METRICS = ("precision", "recall", "f1", "roc_auc", "pr_auc")
ADVANCED_TABLE_FILENAMES = {
    "champion_metric_bootstrap_ci": "champion_metric_bootstrap_ci.csv",
    "subgroup_model_performance": "subgroup_model_performance.csv",
    "risk_signal_trajectory": "risk_signal_trajectory.csv",
    "threshold_cost_benefit": "threshold_cost_benefit.csv",
}
TRAJECTORY_FEATURES = {
    "learning_risk_index": "Learning risk index",
    "early_engagement_ratio": "Early engagement ratio",
    "avg_score": "Avg assessment score",
    "persistence_score": "Persistence score",
}


@dataclass
class AdvancedDashboardTables:
    champion_metric_bootstrap_ci: pd.DataFrame
    subgroup_model_performance: pd.DataFrame
    risk_signal_trajectory: pd.DataFrame
    threshold_cost_benefit: pd.DataFrame


def _read_csv(processed_dir: Path, name: str) -> pd.DataFrame:
    path = processed_dir / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required input table: {path}")
    return pd.read_csv(path, low_memory=False)


def _validate_binary_prediction_inputs(y_true: np.ndarray, *, context: str) -> None:
    if len(y_true) == 0:
        raise ValueError(f"{context} has no usable prediction rows.")
    if len(np.unique(y_true)) < 2:
        raise ValueError(f"{context} must contain both positive and negative classes.")


def _metric_point_estimates(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> dict[str, float]:
    return {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "pr_auc": float(average_precision_score(y_true, y_prob)),
    }


def build_champion_metric_bootstrap_ci(
    processed_dir: Path,
    *,
    n_boot: int = 1000,
    random_state: int = 42,
) -> pd.DataFrame:
    if n_boot <= 0:
        raise ValueError("n_boot must be a positive integer.")

    preds = _read_csv(processed_dir, "risk_band_test_predictions.csv")
    preds = preds.dropna(subset=["y_true", "y_pred", "risk_probability"]).reset_index(drop=True)

    y_true = preds["y_true"].astype(int).to_numpy()
    y_pred = preds["y_pred"].astype(int).to_numpy()
    y_prob = preds["risk_probability"].astype(float).to_numpy()
    _validate_binary_prediction_inputs(y_true, context="risk_band_test_predictions.csv")
    point = _metric_point_estimates(y_true, y_pred, y_prob)

    rng = np.random.default_rng(seed=random_state)
    boot_scores: dict[str, list[float]] = {metric: [] for metric in BOOTSTRAP_METRICS}
    n = len(y_true)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        yt = y_true[idx]
        yp = y_pred[idx]
        yp_prob = y_prob[idx]
        if yt.sum() == 0 or yt.sum() == len(yt):
            continue
        scores = _metric_point_estimates(yt, yp, yp_prob)
        for metric, value in scores.items():
            boot_scores[metric].append(value)

    rows = []
    for metric, scores in boot_scores.items():
        if not scores:
            raise ValueError(f"No valid bootstrap samples were produced for metric `{metric}`.")
        arr = np.asarray(scores, dtype=float)
        rows.append(
            {
                "metric": metric,
                "point_estimate": point[metric],
                "ci_95_lower": float(np.percentile(arr, 2.5)),
                "ci_95_upper": float(np.percentile(arr, 97.5)),
                "bootstrap_mean": float(arr.mean()),
                "bootstrap_std": float(arr.std()),
                "n_boot": len(arr),
                "random_state": random_state,
            }
        )
    return pd.DataFrame(rows)


def _subgroup_metrics(df: pd.DataFrame, subgroup: str, label: str) -> dict[str, object] | None:
    if len(df) < 20 or df["y_true"].sum() == 0:
        return None
    y_true = df["y_true"].astype(int).to_numpy()
    y_pred = df["y_pred"].astype(int).to_numpy()
    y_prob = df["risk_probability"].astype(float).to_numpy()
    roc_auc = float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else np.nan
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    return {
        "subgroup": subgroup,
        "group": label,
        "n": len(df),
        "at_risk_rate": float(y_true.mean()),
        "recall": recall,
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": roc_auc,
        "recall_gap_to_target": recall - TARGET_RECALL,
        "review_flag": bool(recall < TARGET_RECALL),
    }


def build_subgroup_model_performance(processed_dir: Path) -> pd.DataFrame:
    preds = _read_csv(processed_dir, "risk_band_test_predictions.csv")
    student_info = _read_csv(processed_dir, "student_info_clean.csv")
    demo_cols = ["gender", "disability", "imd_band", "num_of_prev_attempts"]
    missing_pred_keys = [column for column in KEY if column not in preds.columns]
    missing_info_columns = [column for column in [*KEY, *demo_cols] if column not in student_info.columns]
    if missing_pred_keys or missing_info_columns:
        raise KeyError(
            "Missing columns required for subgroup merge: "
            f"prediction keys={missing_pred_keys}, student_info={missing_info_columns}"
        )

    merged = preds.merge(student_info[KEY + demo_cols], on=KEY, how="left")
    merged["y_true"] = merged["y_true"].astype(int)
    merged["y_pred"] = merged["y_pred"].astype(int)

    rows: list[dict[str, object]] = []
    if "gender" in merged.columns:
        for value, label in [("M", "Male"), ("F", "Female")]:
            row = _subgroup_metrics(merged.loc[merged["gender"] == value], "Gender", label)
            if row:
                rows.append(row)

    if "disability" in merged.columns:
        for value, label in [("Y", "Disability = Yes"), ("N", "Disability = No")]:
            row = _subgroup_metrics(merged.loc[merged["disability"] == value], "Disability", label)
            if row:
                rows.append(row)

    if "imd_band" in merged.columns:
        low_imd = {"0-10%", "10-20", "10-20%", "20-30%", "30-40%"}
        high_imd = {"70-80%", "80-90%", "90-100%"}
        row = _subgroup_metrics(
            merged.loc[merged["imd_band"].isin(low_imd)],
            "IMD deprivation",
            "Low IMD band (0-40%)",
        )
        if row:
            rows.append(row)
        row = _subgroup_metrics(
            merged.loc[merged["imd_band"].isin(high_imd)],
            "IMD deprivation",
            "High IMD band (70-100%)",
        )
        if row:
            rows.append(row)

    if "num_of_prev_attempts" in merged.columns:
        for mask, label in [
            (merged["num_of_prev_attempts"] == 0, "First attempt"),
            (merged["num_of_prev_attempts"] >= 1, "Re-attempt"),
        ]:
            row = _subgroup_metrics(merged.loc[mask], "Prior attempts", label)
            if row:
                rows.append(row)

    return pd.DataFrame(rows)


def build_risk_signal_trajectory(processed_dir: Path) -> pd.DataFrame:
    rows = []
    for horizon in HORIZONS:
        df = _read_csv(processed_dir, f"features_prediction_day{horizon:02d}.csv")
        if "at_risk" not in df.columns:
            raise KeyError(f"`at_risk` missing in features_prediction_day{horizon:02d}.csv")
        for feature, label in TRAJECTORY_FEATURES.items():
            if feature not in df.columns:
                continue
            grouped_stats = {}
            for at_risk, group in [(0, "Non at-risk"), (1, "At-risk")]:
                values = df.loc[df["at_risk"] == at_risk, feature].dropna()
                mean = float(values.mean())
                sem = float(values.std(ddof=1) / np.sqrt(len(values))) if len(values) > 1 else 0.0
                grouped_stats[group] = mean
                rows.append(
                    {
                        "horizon_day": horizon,
                        "feature": feature,
                        "feature_label": label,
                        "group": group,
                        "at_risk": at_risk,
                        "mean": mean,
                        "sem": sem,
                        "n": len(values),
                    }
                )
            if {"At-risk", "Non at-risk"}.issubset(grouped_stats):
                rows.append(
                    {
                        "horizon_day": horizon,
                        "feature": feature,
                        "feature_label": label,
                        "group": "Gap: at-risk minus non at-risk",
                        "at_risk": np.nan,
                        "mean": grouped_stats["At-risk"] - grouped_stats["Non at-risk"],
                        "sem": np.nan,
                        "n": int(df[feature].notna().sum()),
                    }
                )
    return pd.DataFrame(rows)


def build_threshold_cost_benefit(processed_dir: Path) -> pd.DataFrame:
    champion_metrics = _read_csv(processed_dir, "champion_test_metrics.csv")
    validation_row = champion_metrics.loc[champion_metrics["split"].eq("validation")].iloc[0]
    champion_horizon = int(validation_row["horizon_day"])
    champion_model = str(validation_row["model"])
    selected_threshold = float(validation_row["threshold"])

    threshold_search = _read_csv(processed_dir, "threshold_search_by_horizon.csv")
    curve = threshold_search.loc[
        threshold_search["horizon_day"].eq(champion_horizon)
        & threshold_search["model"].eq(champion_model)
    ].copy()
    curve = curve.sort_values("threshold").reset_index(drop=True)
    if curve.empty:
        raise ValueError(f"No threshold curve found for {champion_model} at day {champion_horizon}.")

    n_validation = int(curve[["tp", "fp", "fn", "tn"]].iloc[0].sum())
    curve["total_flagged"] = curve["tp"] + curve["fp"]
    curve["flagged_pct"] = curve["total_flagged"] / n_validation
    curve["false_alert_ratio"] = np.where(curve["tp"] > 0, curve["fp"] / curve["tp"], np.nan)
    curve["missed_at_risk"] = curve["fn"]
    curve["expected_review_load_per_1000"] = curve["flagged_pct"] * 1000
    curve["caught_at_risk_per_1000"] = curve["tp"] / n_validation * 1000
    curve["selected_operating_point"] = np.isclose(curve["threshold"], selected_threshold)
    curve["target_recall_met"] = curve["recall"] >= TARGET_RECALL
    return curve


def build_advanced_dashboard_tables(
    processed_dir: Path,
    *,
    write_outputs: bool = True,
    n_boot: int = 1000,
    random_state: int = 42,
) -> AdvancedDashboardTables:
    processed_dir = Path(processed_dir)
    tables = AdvancedDashboardTables(
        champion_metric_bootstrap_ci=build_champion_metric_bootstrap_ci(
            processed_dir,
            n_boot=n_boot,
            random_state=random_state,
        ),
        subgroup_model_performance=build_subgroup_model_performance(processed_dir),
        risk_signal_trajectory=build_risk_signal_trajectory(processed_dir),
        threshold_cost_benefit=build_threshold_cost_benefit(processed_dir),
    )

    if write_outputs:
        for attr_name, filename in ADVANCED_TABLE_FILENAMES.items():
            getattr(tables, attr_name).to_csv(processed_dir / filename, index=False)

    return tables
