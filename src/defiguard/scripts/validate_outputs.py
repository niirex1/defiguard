from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


EXPECTED_TABLES = [
    "table1_agent_roles.csv",
    "table2_overall_performance.csv",
    "table3_common_subset.csv",
    "table4_closest_baselines.csv",
    "table5_atomic_vs_multiblock.csv",
    "table6_heldout_defizero.csv",
    "table7_overhead.csv",
    "table8_ablation.csv",
]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ensure_files_exist(paper_dir: Path) -> None:
    missing = [name for name in EXPECTED_TABLES if not (paper_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing paper tables: {missing}")


def validate_table3_against_manifest(paper_dir: Path, manifest_dir: Path) -> None:
    t3 = read_csv(paper_dir / "table3_common_subset.csv")
    manifest = read_csv(manifest_dir / "common_subset_summary.csv")
    if t3 != manifest:
        raise ValueError("table3_common_subset.csv does not match common_subset_summary.csv")


def validate_table4_schema(paper_dir: Path) -> None:
    t4 = read_csv(paper_dir / "table4_closest_baselines.csv")
    headers = set(t4[0].keys()) if t4 else set()
    allowed = [
        {"Method", "RCA", "ETD"},
        {"Method", "RCA@10%", "ETD@20%"},
    ]
    if headers not in allowed:
        raise ValueError(f"Unexpected Table 4 schema: {headers}")


def validate_known_values(paper_dir: Path) -> None:
    t2 = read_csv(paper_dir / "table2_overall_performance.csv")
    full_rows = [r for r in t2 if r.get("Method") == "DeFiGuard (full)"]
    if not full_rows:
        raise ValueError("DeFiGuard (full) missing from Table 2")
    row = full_rows[0]
    expected = {
        "DeFiIncidents-CC_RCA": "0.95",
        "DeFiIncidents-CC_ETD": "0.54",
        "DeFiSynth-Proto_RCA": "0.98",
        "DeFiSynth-Proto_ETD": "0.76",
    }
    for k, v in expected.items():
        if row.get(k) != v:
            raise ValueError(f"Unexpected value for {k}: got {row.get(k)}, expected {v}")

    t8 = read_csv(paper_dir / "table8_ablation.csv")
    ab_full = [r for r in t8 if r.get("Variant") == "DeFiGuard (full)"]
    if not ab_full:
        raise ValueError("DeFiGuard (full) missing from Table 8")
    if ab_full[0].get("RCA") != "0.95" or ab_full[0].get("ETD") != "0.54":
        raise ValueError("Table 8 full-system values are inconsistent with manuscript expectations")


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate generated manuscript outputs.")
    ap.add_argument("--paper_dir", required=True)
    ap.add_argument("--manifest_dir", required=True)
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    paper_dir = Path(args.paper_dir)
    manifest_dir = Path(args.manifest_dir)

    ensure_files_exist(paper_dir)
    validate_table3_against_manifest(paper_dir, manifest_dir)
    validate_table4_schema(paper_dir)
    validate_known_values(paper_dir)

    print("Validation passed.")


if __name__ == "__main__":
    main()
