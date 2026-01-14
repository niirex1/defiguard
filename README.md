# DeFiGuard (CCS Artifact)

This repository contains the **CCS artifact bundle** for the DeFiGuard paper, *“DeFiGuard: An Advanced Multi-Agent System for Cross-Contract Vulnerability Detection in DeFi Protocols.”*  
It is designed for **deterministic, reviewer-centric reproduction** of the paper’s reported tables and figures from the included CSV datasets and raw evaluation logs.

The artifact provides:
- a lightweight Python package (`defiguard`) with fixed-seed evaluation entry points,
- CSV-only datasets for **DeFiIncidents-CC**, **DeFiSynth-Proto**, and **DeFiZero**, and
- scripts that regenerate the paper outputs under `results/paper/` (tables, figures, and a summary).

The repository mirrors the organization and usability conventions of the included reference artifacts (CLUE, TIPSO) while avoiding heavyweight dependencies and excluding any weaponized exploit payloads or live-target tooling.


The artifact supports two use cases:

1. **Minimal, deterministic reproduction (default).**
   Regenerates *all paper tables and plots* from the included protocol-level raw logs.

2. **Toy end-to-end run (optional).**
   Runs a small, self-contained protocol simulator and a simplified multi-agent search loop on synthetic protocol specs.
   This mirrors the algorithmic structure without shipping weaponized exploit bundles.

> Safety note: we do **not** ship exploit payloads for live targets. All traces are abstract call-sequence specs and
> are only intended for offline evaluation in a sandbox.

---

## Quickstart (recommended)

### 1) Create an environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### 2) Regenerate all paper tables and figures
```bash
python -m defiguard.scripts.make_paper_tables_figs --out results/paper
```

Outputs:
- `results/paper/*.csv` (Tables 2, 4, 5, 6, 7, 8)
- `results/paper/figures/*.png` (Figures 1, 5, 6)
- `results/paper/SUMMARY.md` (quick view)

---

## Optional toy end-to-end run

This run mirrors the paper's structure (protocol model + bounded search + role-separated agents) using **abstract** call-sequence specs only.

```bash
python -m defiguard.toy_run --config configs/default.yaml --out results/toy
```

Outputs:
- `results/toy/toy_summary.csv`
- `results/toy/toy_traces.jsonl` (abstract calls only)

---

## Dataset-specific evaluation entrypoint (as in the appendix)

```bash
python -m defiguard.eval --dataset DeFiIncidents-CC --config configs/default.yaml
python -m defiguard.eval --dataset DeFiSynth-Proto  --config configs/default.yaml
python -m defiguard.eval --dataset DeFiZero         --config configs/default.yaml
```

Each command writes a CSV into `results/eval/`.

---

## Repository layout

- `src/defiguard/`
  - `eval.py` minimal evaluator (reads `results/raw_logs/`)
  - `scripts/make_paper_tables_figs.py` regenerates tables/figures
- `data/`
  - `DeFiIncidents-CC/` incident metadata + labels (CSV)
  - `DeFiSynth-Proto/` synthetic protocol specs + injected bug metadata (CSV)
  - `DeFiZero/` held-out incident metadata (CSV)
- `results/raw_logs/`
  - `metrics.jsonl` protocol-level metric logs used to regenerate Table 4 and Figure 1/5
  - `synth_variants.jsonl` ETD logs for Table 5
  - `runtime_tokens.jsonl` overhead logs for Table 7
- `results/tables/` and `results/figures/` contain the numeric inputs for ablation/runtime plots.

---

## Notes for reviewers

- The included datasets are **metadata + labels + abstract traces**. They are sufficient to regenerate the reported
  tables and figures deterministically.
- If you need full on-chain traces, snapshots, or contract bytecode for replay, see `artifacts/artifact.md`
  for the expected download hooks and file formats.

---

## Citation

See `CITATION.cff`.
