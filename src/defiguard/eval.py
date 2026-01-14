from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yaml

from defiguard.metrics import ProtocolOutcome, aggregate
from defiguard.utils import read_jsonl, ensure_dir, set_seed


ROOT = Path(__file__).resolve().parents[2]  # repo root (src/defiguard/..)


def load_config(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def eval_from_logs(dataset: str, logs_path: Path, out_dir: Path) -> pd.DataFrame:
    rows = read_jsonl(logs_path)
    df = pd.DataFrame(rows)
    df = df[df["dataset"] == dataset].copy()
    if df.empty:
        raise ValueError(f"No rows for dataset={dataset} in {logs_path}")
    out_rows = []
    for method, mdf in df.groupby("method"):
        outcomes = [
            ProtocolOutcome(
                protocol_id=str(r["protocol_id"]),
                rca_hit=float(r["rca_hit"]),
                etd_hit=float(r["etd_hit"]),
                apc=float(r["apc"]),
                fpr=float(r["fpr"]),
            )
            for _, r in mdf.iterrows()
        ]
        agg = aggregate(outcomes)
        out_rows.append({
            "Method": method,
            "RCA": round(agg["RCA"], 2),
            "ETD": round(agg["ETD"], 2),
            "APC": round(agg["APC"], 2),
            "FPR": round(agg["FPR"], 1),
            "N": int(mdf.shape[0]),
        })
    out = pd.DataFrame(out_rows).sort_values("Method").reset_index(drop=True)
    ensure_dir(out_dir)
    out.to_csv(out_dir / f"eval_{dataset}.csv", index=False)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="DeFiGuard evaluation entrypoint (minimal reproduction path).")
    ap.add_argument("--dataset", type=str, required=True,
                    choices=["DeFiIncidents-CC", "DeFiSynth-Proto", "DeFiZero"],
                    help="Dataset to evaluate.")
    ap.add_argument("--config", type=str, required=True, help="YAML config path (used for parameters + seeds).")

    ap.add_argument("--mode", type=str, default="minimal", choices=["minimal"],
                    help="This artifact exposes the minimal reproduction path used in the appendix.")
    ap.add_argument("--logs", type=str, default="results/raw_logs/metrics.jsonl", help="Protocol-level raw logs.")
    ap.add_argument("--out", type=str, default="results/eval", help="Output directory (relative to repo root).")

    args = ap.parse_args()

    cfg = load_config(ROOT / args.config)
    set_seed(int(cfg.get("seed", 7)))

    out = eval_from_logs(args.dataset, ROOT / args.logs, (ROOT / args.out))
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
