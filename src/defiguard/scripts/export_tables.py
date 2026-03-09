from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path
from typing import Iterable, List

EXPECTED = [
    "table1_agent_roles.csv",
    "table2_overall_performance.csv",
    "table3_common_subset.csv",
    "table4_closest_baselines.csv",
    "table5_atomic_vs_multiblock.csv",
    "table6_heldout_defizero.csv",
    "table7_overhead.csv",
    "table8_ablation.csv",
]


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def ensure_table3_from_manifest(manifest_dir: Path, out_dir: Path) -> None:
    summary = manifest_dir / "common_subset_summary.csv"
    if not summary.exists():
        return
    copy_file(summary, out_dir / "table3_common_subset.csv")


def main() -> None:
    ap = argparse.ArgumentParser(description="Export manuscript tables as CSV files.")
    ap.add_argument("--source", default="results/tables", help="Source tables directory")
    ap.add_argument("--manifest_dir", default="results/manifests", help="Manifest directory")
    ap.add_argument("--out", required=True, help="Output directory")
    args = ap.parse_args()

    src_dir = Path(args.source)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for name in EXPECTED:
        src = src_dir / name
        if src.exists():
            copy_file(src, out_dir / name)

    ensure_table3_from_manifest(Path(args.manifest_dir), out_dir)

    missing = [name for name in EXPECTED if not (out_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing exported tables: {missing}")

    print(f"Exported {len(EXPECTED)} tables to {out_dir}")


if __name__ == "__main__":
    main()
