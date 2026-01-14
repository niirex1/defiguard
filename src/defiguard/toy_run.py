from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from defiguard.utils import set_seed
from defiguard.toy.protocol import load_synth_protocols, load_synth_bugs
from defiguard.toy.run import run_toy


ROOT = Path(__file__).resolve().parents[2]  # repo root (src/defiguard/..)


def main() -> None:
    ap = argparse.ArgumentParser(description="DeFiGuard toy end-to-end pipeline (safe, offline).")
    ap.add_argument("--config", type=str, default="configs/default.yaml", help="YAML config (for seed).")
    ap.add_argument("--out", type=str, default="results/toy", help="Output directory (relative to repo root).")
    ap.add_argument("--max-protocols", type=int, default=10)
    ap.add_argument("--max-traces", type=int, default=10)

    args = ap.parse_args()

    cfg_path = ROOT / args.config
    with cfg_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    set_seed(int(cfg.get("seed", 7)))

    protocols = load_synth_protocols(ROOT / "data/DeFiSynth-Proto/protocols.csv")
    bugs = load_synth_bugs(ROOT / "data/DeFiSynth-Proto/injected_bugs.csv")

    out_dir = (ROOT / args.out).resolve()
    df = run_toy(protocols, bugs, out_dir, max_protocols=args.max_protocols, max_traces_per_protocol=args.max_traces)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
