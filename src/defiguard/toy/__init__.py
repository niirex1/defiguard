"""Toy end-to-end pipeline (safe).

This module mirrors the manuscript's algorithmic structure:
- protocol model (lightweight spec from CSV)
- bounded search loop
- role-separated agents (scout/planner/checker)

It does **not** ship bytecode, live exploit payloads, or on-chain traces.
It only operates on abstract call-sequence specs for offline sandbox evaluation.
"""

from .protocol import ProtocolSpec, BugSpec, load_synth_protocols, load_synth_bugs
from .run import run_toy

__all__ = [
    "ProtocolSpec",
    "BugSpec",
    "load_synth_protocols",
    "load_synth_bugs",
    "run_toy",
]
