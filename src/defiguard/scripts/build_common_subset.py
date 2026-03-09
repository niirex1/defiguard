from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List

DEFAULT_BASELINES = [
    "zhou2021jit",
    "babel2023clockwork",
    "babel2023lanturn",
    "shou2023ityfuzz",
    "kong2025verite",
    "gervais2025aiagent",
]

DEFAULT_EXCLUSION_ORDER = [
    "unavailable_equivalent_inputs",
    "unsupported_multiblock_or_governance",
    "unsupported_replay_assumptions",
    "method_scope_restriction",
]


def load_config(path: Path) -> Dict:
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def read_jsonl(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def build_rows(log_rows: List[Dict], compared_baselines: List[str]) -> List[Dict]:
    out: List[Dict] = []
    for row in log_rows:
        baseline_support = row.get("baseline_support", {})
        supported = all(bool(baseline_support.get(b, False)) for b in compared_baselines)
        reason = row.get("exclusion_reason", "")
        if not supported and not reason:
            # best-effort fallback for older logs
            missing = [b for b in compared_baselines if not baseline_support.get(b, False)]
            reason = "method_scope_restriction" if missing else "unknown"
        out.append(
            {
                "target_id": row.get("target_id", ""),
                "dataset": row.get("dataset", ""),
                "included": int(supported),
                "exclusion_reason": "" if supported else reason,
                "supported_by": ";".join([b for b in compared_baselines if baseline_support.get(b, False)]),
            }
        )
    return out


def write_csv(path: Path, rows: List[Dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: List[Dict]) -> List[Dict]:
    datasets = sorted({r["dataset"] for r in rows if r["dataset"]})
    summary: List[Dict] = []
    for ds in datasets:
        ds_rows = [r for r in rows if r["dataset"] == ds]
        included = sum(r["included"] for r in ds_rows)
        excluded = len(ds_rows) - included
        summary.append({"Dataset": ds, "Included": included, "Excluded": excluded})
    return summary


def summarize_reasons(rows: List[Dict]) -> List[Dict]:
    counter = Counter(r["exclusion_reason"] for r in rows if not r["included"] and r["exclusion_reason"])
    return [{"exclusion_reason": k, "count": v} for k, v in sorted(counter.items())]


def write_support_matrix(path: Path, rows: List[Dict], baselines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # row-wise support matrix derived from supported_by strings
    with path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["target_id", "dataset"] + baselines
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            supported = set(filter(None, r["supported_by"].split(";")))
            record = {"target_id": r["target_id"], "dataset": r["dataset"]}
            for b in baselines:
                record[b] = 1 if b in supported else 0
            writer.writerow(record)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build strict common-comparison subset manifest.")
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument(
        "--logs",
        default="results/raw_logs/metrics.jsonl",
        help="JSONL log file with per-target baseline support metadata",
    )
    args = ap.parse_args()

    config = load_config(Path(args.config))
    baselines = config.get("closest_protocol_baselines", DEFAULT_BASELINES)

    log_rows = read_jsonl(Path(args.logs))
    rows = build_rows(log_rows, baselines)

    out_dir = Path(args.out)
    write_csv(
        out_dir / "common_subset_targets.csv",
        rows,
        ["target_id", "dataset", "included", "exclusion_reason", "supported_by"],
    )
    write_csv(
        out_dir / "common_subset_summary.csv",
        summarize(rows),
        ["Dataset", "Included", "Excluded"],
    )
    write_csv(
        out_dir / "common_subset_reasons.csv",
        summarize_reasons(rows),
        ["exclusion_reason", "count"],
    )
    write_support_matrix(out_dir / "baseline_support_matrix.csv", rows, baselines)

    print(f"Wrote manifests to {out_dir}")


if __name__ == "__main__":
    main()
