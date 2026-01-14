from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np


@dataclass(frozen=True)
class ProtocolOutcome:
    protocol_id: str
    rca_hit: float
    etd_hit: float
    apc: float
    fpr: float


def aggregate(outcomes: Iterable[ProtocolOutcome]) -> Dict[str, float]:
    outs = list(outcomes)
    if not outs:
        raise ValueError("No outcomes to aggregate.")
    rca = float(np.mean([float(o.rca_hit) for o in outs]))
    etd = float(np.mean([float(o.etd_hit) for o in outs]))
    apc = float(np.mean([o.apc for o in outs]))
    fpr = float(np.mean([o.fpr for o in outs]))
    return {"RCA": rca, "ETD": etd, "APC": apc, "FPR": fpr}
