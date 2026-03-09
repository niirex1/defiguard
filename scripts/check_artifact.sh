#!/usr/bin/env bash
set -euo pipefail

required=(
  "configs/default.yaml"
  "data/DeFiIncidents-CC/incidents.csv"
  "data/DeFiSynth-Proto/protocols.csv"
  "data/DeFiSynth-Proto/injected_bugs.csv"
  "data/DeFiZero/incidents.csv"
  "results/raw_logs/metrics.jsonl"
  "results/raw_logs/synth_variants.jsonl"
  "results/raw_logs/runtime_tokens.jsonl"
  "results/tables/table1_agent_roles.csv"
  "results/tables/table2_overall_performance.csv"
  "results/tables/table3_common_subset.csv"
  "results/tables/table4_closest_baselines.csv"
  "results/tables/table5_atomic_vs_multiblock.csv"
  "results/tables/table6_heldout_defizero.csv"
  "results/tables/table7_overhead.csv"
  "results/tables/table8_ablation.csv"
)

missing=0
for f in "${required[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "Missing: $f"
    missing=1
  fi
done

if [[ $missing -ne 0 ]]; then
  echo "Artifact check failed."
  exit 1
fi

echo "Artifact check passed."
