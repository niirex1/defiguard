#!/usr/bin/env bash
set -euo pipefail

python -m defiguard.eval --dataset DeFiIncidents-CC --config configs/default.yaml
python -m defiguard.eval --dataset DeFiSynth-Proto  --config configs/default.yaml
python -m defiguard.eval --dataset DeFiZero         --config configs/default.yaml

python -m defiguard.scripts.make_paper_tables_figs --out results/paper
echo "Done. See results/paper/."
