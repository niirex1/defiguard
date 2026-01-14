# Optional replay interface (not required for minimal reproduction)

If you want to plug in a full EVM replay backend, the artifact expects the following file formats.

## 1) Snapshot index
`data/replay/snapshots.csv`

Columns:
- `protocol_id`
- `block_number`
- `rpc_url` (optional)
- `state_root` (optional)
- `notes`

## 2) Contract index
`data/replay/contracts.csv`

Columns:
- `protocol_id`
- `chain_id`
- `address`
- `name` (optional)
- `abi_path` (optional)
- `bytecode_hash` (optional)

## 3) Trace specification
`data/replay/traces.jsonl`

Each line is a JSON object:
- `protocol_id`
- `trace_id`
- `variant` (atomic | multi-block)
- `calls`: list of `{from,to,selector,args,value}`
- `expected_profit_asset`
- `expected_profit_min`

A replay backend should:
- execute `calls` against the snapshot,
- return state deltas and profit signals,
- surface invariant violations.

The minimal artifact does **not** ship these files and does not fetch them automatically.
