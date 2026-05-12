#!/usr/bin/env python3
"""Generate static figures used by the final LaTeX report."""

from pathlib import Path
import textwrap

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "figures"

OUT.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="white", context="paper")
plt.rcParams.update(
    {
        "figure.dpi": 160,
        "savefig.dpi": 220,
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

OUTCOME_ORDER = ["Withdrawn", "Fail", "Pass", "Distinction"]
OUTCOME_COLORS = {
    "Withdrawn": "#c44e52",
    "Fail": "#f58518",
    "Pass": "#4c78a8",
    "Distinction": "#2f7f5f",
}
SEGMENT_COLORS = {
    "Inactive Drop-offs": "#c44e52",
    "Sporadic Explorers": "#f58518",
    "Steady Progressors": "#4c78a8",
    "Focused Achievers": "#2f7f5f",
}


def save(fig: plt.Figure, name: str) -> None:
    for ax in fig.axes:
        ax.grid(False)
    fig.tight_layout()
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)


def pct_axis(ax: plt.Axes) -> None:
    ax.yaxis.set_major_formatter(lambda x, _: f"{x:.0%}")


def short_label(value: str, width: int = 18) -> str:
    return "\n".join(textwrap.wrap(str(value), width=width, break_long_words=False))


def figure_outcome_distribution() -> None:
    df = pd.read_csv(DATA / "student_info_clean.csv")
    counts = df["final_result"].value_counts().reindex(OUTCOME_ORDER)
    shares = counts / counts.sum()

    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    bars = ax.bar(
        counts.index,
        counts.values,
        color=[OUTCOME_COLORS[x] for x in counts.index],
        edgecolor="white",
        linewidth=0.8,
    )
    ax.set_title("Final Outcome Distribution")
    ax.set_ylabel("Enrollments")
    ax.set_xlabel("")
    ax.set_ylim(0, counts.max() * 1.18)
    ax.tick_params(axis="x", rotation=18)
    for bar, count, share in zip(bars, counts.values, shares.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + counts.max() * 0.025,
            f"{count:,.0f}\n{share:.1%}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.text(
        0.01,
        0.96,
        "At-risk label = Fail or Withdrawn",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        color="#555555",
    )
    save(fig, "fig01_outcome_distribution.png")


def figure_early_behavior() -> None:
    df = pd.read_csv(DATA / "features_final.csv")
    summary = (
        df.groupby("final_result", as_index=False)
        .agg(
            median_early_engagement=("early_engagement", "median"),
            median_avg_score=("avg_score", "median"),
        )
        .set_index("final_result")
        .reindex(OUTCOME_ORDER)
        .reset_index()
    )

    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.5), sharex=False)
    for ax, col, title, ylabel in [
        (
            axes[0],
            "median_early_engagement",
            "Median Early Clicks",
            "Clicks in early window",
        ),
        (
            axes[1],
            "median_avg_score",
            "Median Assessment Score",
            "Score",
        ),
    ]:
        bars = ax.bar(
            summary["final_result"],
            summary[col],
            color=[OUTCOME_COLORS[x] for x in summary["final_result"]],
            edgecolor="white",
            linewidth=0.8,
        )
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=24)
        ax.set_ylim(0, summary[col].max() * 1.22 if summary[col].max() else 1)
        for bar, value in zip(bars, summary[col].values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + summary[col].max() * 0.035,
                f"{value:.0f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    save(fig, "fig02_early_behavior_by_outcome.png")


def figure_segment_profile() -> None:
    df = pd.read_csv(DATA / "cluster_profiles.csv")
    df = df.sort_values("at_risk_rate", ascending=True)
    colors = [SEGMENT_COLORS.get(x, "#4c78a8") for x in df["cluster_label"]]

    fig, ax = plt.subplots(figsize=(7.0, 3.7))
    y = np.arange(len(df))
    bars = ax.barh(y, df["enrollments"], color=colors, edgecolor="white", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([short_label(x, 22) for x in df["cluster_label"]])
    ax.set_xlabel("Enrollments")
    ax.set_title("Learner Segment Size and At-Risk Rate")
    ax.set_xlim(0, df["enrollments"].max() * 1.28)
    for bar, rate, share in zip(bars, df["at_risk_rate"], df["share_of_dataset"]):
        ax.text(
            bar.get_width() + df["enrollments"].max() * 0.025,
            bar.get_y() + bar.get_height() / 2,
            f"{rate:.1f}% risk | {share:.1f}% share",
            va="center",
            fontsize=8,
        )
    save(fig, "fig03_segment_risk_profile.png")


def figure_horizon_quality() -> None:
    df = pd.read_csv(DATA / "model_horizon_comparison.csv")
    models = ["Logistic Regression", "Random Forest", "XGBoost"]
    df["model"] = pd.Categorical(df["model"], categories=models, ordered=True)
    df = df.sort_values(["model", "horizon_day"])

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.55), sharex=True)
    palette = {
        "Logistic Regression": "#4c78a8",
        "Random Forest": "#54a24b",
        "XGBoost": "#f58518",
    }
    for model, part in df.groupby("model", observed=True):
        axes[0].plot(
            part["horizon_day"],
            part["validation_pr_auc"],
            marker="o",
            linewidth=1.8,
            label=model,
            color=palette[str(model)],
        )
        axes[1].plot(
            part["horizon_day"],
            part["validation_recall"],
            marker="o",
            linewidth=1.8,
            label=model,
            color=palette[str(model)],
        )
    axes[0].set_title("Validation PR-AUC")
    axes[0].set_ylabel("PR-AUC")
    axes[0].set_xlabel("Prediction horizon")
    axes[0].set_xticks([7, 14, 21, 30])
    axes[0].set_ylim(0.68, 0.90)

    axes[1].axhline(0.90, linestyle="--", color="#555555", linewidth=1, label="Recall target")
    axes[1].set_title("Validation Recall")
    axes[1].set_ylabel("Recall")
    axes[1].set_xlabel("Prediction horizon")
    axes[1].set_xticks([7, 14, 21, 30])
    axes[1].set_ylim(0.82, 0.97)
    axes[1].legend(loc="lower left", frameon=True)
    save(fig, "fig04_horizon_model_quality.png")


def figure_risk_bands() -> None:
    df = pd.read_csv(DATA / "risk_band_summary.csv")
    order = ["Low", "Medium", "High", "Critical"]
    df["risk_band"] = pd.Categorical(df["risk_band"], categories=order, ordered=True)
    df = df.sort_values("risk_band")

    fig, ax = plt.subplots(figsize=(6.8, 3.7))
    x = np.arange(len(df))
    width = 0.36
    actual = ax.bar(
        x - width / 2,
        df["actual_at_risk_rate"],
        width,
        label="Actual at-risk rate",
        color="#c44e52",
        edgecolor="white",
    )
    predicted = ax.bar(
        x + width / 2,
        df["average_predicted_probability"],
        width,
        label="Average predicted probability",
        color="#4c78a8",
        edgecolor="white",
    )
    ax.set_title("Risk Bands Are Monotonic and Well Ordered")
    ax.set_ylabel("Rate / probability")
    ax.set_xticks(x)
    ax.set_xticklabels(df["risk_band"])
    pct_axis(ax)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="upper left", frameon=True)
    for bars in [actual, predicted]:
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.025,
                f"{bar.get_height():.0%}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    save(fig, "fig05_risk_band_calibration.png")


def figure_feature_importance() -> None:
    df = pd.read_csv(DATA / "model_feature_importance.csv")
    df = df.sort_values("permutation_importance_mean", ascending=False).head(10)
    df = df.iloc[::-1]

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.barh(
        df["original_feature_name"],
        df["permutation_importance_mean"],
        xerr=df["permutation_importance_std"],
        color="#4c78a8",
        edgecolor="white",
        linewidth=0.8,
        error_kw={"elinewidth": 1, "capsize": 2, "ecolor": "#333333"},
    )
    ax.set_title("Top Champion-Model Signals")
    ax.set_xlabel("Permutation importance")
    ax.set_ylabel("")
    save(fig, "fig06_feature_importance.png")


def figure_threshold_tradeoff() -> None:
    df = pd.read_csv(DATA / "threshold_cost_benefit.csv").sort_values("threshold")

    fig, ax1 = plt.subplots(figsize=(7.0, 3.7))
    ax1.plot(df["threshold"], df["recall"], marker="o", color="#c44e52", label="Recall")
    ax1.plot(df["threshold"], df["precision"], marker="o", color="#4c78a8", label="Precision")
    ax1.axvline(0.25, color="#555555", linestyle="--", linewidth=1, label="Selected threshold")
    ax1.set_xlabel("Probability threshold")
    ax1.set_ylabel("Precision / recall")
    ax1.set_ylim(0.45, 1.02)
    pct_axis(ax1)

    ax2 = ax1.twinx()
    ax2.plot(
        df["threshold"],
        df["expected_review_load_per_1000"],
        marker="s",
        color="#54a24b",
        label="Review load per 1,000",
        linewidth=1.6,
    )
    ax2.set_ylabel("Expected review load per 1,000")
    ax2.spines["right"].set_visible(True)

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="center right", frameon=True)
    ax1.set_title("Threshold Trade-Off: Recall, Precision, and Advisor Load")
    save(fig, "fig07_threshold_capacity_tradeoff.png")


def main() -> None:
    figure_outcome_distribution()
    figure_early_behavior()
    figure_segment_profile()
    figure_horizon_quality()
    figure_risk_bands()
    figure_feature_importance()
    figure_threshold_tradeoff()
    print(f"Generated report figures in {OUT}")


if __name__ == "__main__":
    main()
