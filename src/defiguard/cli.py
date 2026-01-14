from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(prog="defiguard", description="DeFiGuard artifact CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_eval = sub.add_parser("eval", help="Run evaluation (same as `python -m defiguard.eval`).")
    p_eval.add_argument("--dataset", required=True, choices=["DeFiIncidents-CC", "DeFiSynth-Proto", "DeFiZero"])
    p_eval.add_argument("--config", default="configs/default.yaml")
    p_eval.add_argument("--out", default="results/eval")

    p_rep = sub.add_parser("make-paper", help="Regenerate all paper tables/figures from included raw logs.")
    p_rep.add_argument("--out", default="results/paper")

    args = ap.parse_args()

    if args.cmd == "eval":
        cmd = [sys.executable, "-m", "defiguard.eval", "--dataset", args.dataset, "--config", args.config, "--out", args.out]
        raise SystemExit(subprocess.call(cmd))

    if args.cmd == "make-paper":
        cmd = [sys.executable, "-m", "defiguard.scripts.make_paper_tables_figs", "--out", args.out]
        raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
