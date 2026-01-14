from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd


@dataclass(frozen=True)
class ProtocolSpec:
    """Lightweight protocol specification used by the toy pipeline."""

    protocol_id: str
    num_contracts: int
    num_pools: int
    bug_family: str
    interface_profile: str


@dataclass(frozen=True)
class BugSpec:
    """Injected-bug metadata used to evaluate the toy pipeline."""

    protocol_id: str
    bug_id: str
    bug_type: str
    poc_trace_id: str


@dataclass(frozen=True)
class TraceCall:
    """Abstract call (no bytecode, no calldata)."""

    actor: str
    target: str
    function: str
    notes: str = ""


@dataclass(frozen=True)
class TraceSpec:
    """Abstract call-sequence trace spec."""

    trace_id: str
    protocol_id: str
    variant: str  # atomic | multi-block
    calls: List[TraceCall]
    hypothesis: str


def load_synth_protocols(csv_path: Path) -> List[ProtocolSpec]:
    df = pd.read_csv(csv_path)
    out: List[ProtocolSpec] = []
    for _, r in df.iterrows():
        out.append(
            ProtocolSpec(
                protocol_id=str(r["protocol_id"]),
                num_contracts=int(r["num_contracts"]),
                num_pools=int(r["num_pools"]),
                bug_family=str(r["bug_family"]),
                interface_profile=str(r["interface_profile"]),
            )
        )
    return out


def load_synth_bugs(csv_path: Path) -> List[BugSpec]:
    df = pd.read_csv(csv_path)
    out: List[BugSpec] = []
    for _, r in df.iterrows():
        out.append(
            BugSpec(
                protocol_id=str(r["protocol_id"]),
                bug_id=str(r["bug_id"]),
                bug_type=str(r["bug_type"]),
                poc_trace_id=str(r["poc_trace_id"]),
            )
        )
    return out


def find_bug(bugs: List[BugSpec], protocol_id: str) -> Optional[BugSpec]:
    for b in bugs:
        if b.protocol_id == protocol_id:
            return b
    return None
