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
    parser = argparse.ArgumentParser(description="Export A/B testing design and simulation tables from champion model outputs.")
    parser.add_argument("--no-write", action="store_true", help="Build tables without writing CSV files.")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed for control/treatment assignment.")
    parser.add_argument("--treatment-share", type=float, default=0.5, help="Share of eligible learners assigned to treatment.")
    parser.add_argument("--minimum-practical-lift", type=float, default=0.03, help="Minimum absolute lift required for a deploy decision.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = find_repo_root()
    sys.path.append(str(root))

    from src.experiments import build_ab_testing_tables

    processed_dir = root / "data" / "processed"
    tables = build_ab_testing_tables(
        processed_dir=processed_dir,
        write_outputs=not args.no_write,
        random_state=args.random_state,
        treatment_share=args.treatment_share,
        minimum_practical_lift=args.minimum_practical_lift,
    )

    print("A/B testing tables ready.")
    print(f"ab_test_experiment_design: {tables.ab_test_experiment_design.shape}")
    print(f"ab_test_assignment: {tables.ab_test_assignment.shape}")
    print(f"ab_test_srm_check: {tables.ab_test_srm_check.shape}")
    print(f"ab_test_balance: {tables.ab_test_balance.shape}")
    print(f"ab_test_power_analysis: {tables.ab_test_power_analysis.shape}")
    print(f"ab_test_simulated_results: {tables.ab_test_simulated_results.shape}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
