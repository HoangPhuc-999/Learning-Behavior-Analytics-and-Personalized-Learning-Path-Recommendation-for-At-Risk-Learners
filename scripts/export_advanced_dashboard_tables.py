from __future__ import annotations

import argparse
import sys
from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "data").exists() and (candidate / "src").exists():
            return candidate
    raise FileNotFoundError("Could not locate repository root.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export advanced Power BI dashboard tables from processed modeling outputs.")
    parser.add_argument("--no-write", action="store_true", help="Build tables without writing CSV files.")
    parser.add_argument("--n-boot", type=int, default=1000, help="Bootstrap iterations for champion metric confidence intervals.")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed for bootstrap resampling.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = find_repo_root()
    sys.path.append(str(root))

    from src.features import build_advanced_dashboard_tables

    processed_dir = root / "data" / "processed"
    tables = build_advanced_dashboard_tables(
        processed_dir=processed_dir,
        write_outputs=not args.no_write,
        n_boot=args.n_boot,
        random_state=args.random_state,
    )

    print("Advanced dashboard tables ready.")
    print(f"champion_metric_bootstrap_ci: {tables.champion_metric_bootstrap_ci.shape}")
    print(f"subgroup_model_performance: {tables.subgroup_model_performance.shape}")
    print(f"risk_signal_trajectory: {tables.risk_signal_trajectory.shape}")
    print(f"threshold_cost_benefit: {tables.threshold_cost_benefit.shape}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
