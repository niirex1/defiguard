# CCS Artifact Notes (DeFiGuard)

## Claims supported by this artifact

This bundle supports the manuscript's **reproducibility claims** by providing:
- Protocol-level raw logs for all evaluated methods (Table 4, Figure 1, Figure 5).
- Synthetic-variant ETD logs (Table 5).
- Held-out zero-day-style logs (Table 6).
- Runtime/token logs and a runtime breakdown input file (Table 7, Figure 6).
- Ablation summary (Table 8).

The scripts in `src/defiguard/scripts/` regenerate these tables/figures end-to-end.

## Running the full pipeline

The manuscript describes optional EVM replay using forked nodes and bounded search. That mode requires:
- an archival Ethereum RPC endpoint (or a local archive node),
- access to contract bytecode and historical state,
- a trace provider.

This submission bundle intentionally avoids shipping exploit bundles and does not auto-download chain data.
If you would like to reproduce the full replay mode, the expected interfaces are documented in:

- `artifacts/replay_interface.md` (inputs/outputs for traces and snapshots)
- `configs/default.yaml` (budget parameters)

## Determinism

All provided scripts are deterministic given `configs/default.yaml` and the included CSV/JSONL files.

## Safety

No payloads intended for real-world exploitation are included. Traces are abstract call-sequence specs only.
