from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from defiguard.utils import ensure_dir, write_jsonl

from .agents import ScoutAgent, PlannerAgent, CheckerAgent, trace_to_json
from .protocol import ProtocolSpec, BugSpec, TraceSpec
from .search import BoundedSearch, SearchResult


def run_toy(
    protocols: List[ProtocolSpec],
    bugs: List[BugSpec],
    out_dir: Path,
    max_protocols: int = 10,
    max_traces_per_protocol: int = 10,
) -> pd.DataFrame:
    """Run the toy pipeline on a subset of synthetic protocol specs.

    Writes:
    - `toy_summary.csv`: per-protocol best outcome
    - `toy_traces.jsonl`: evaluated abstract traces

    This is optional and not required for the minimal reproduction path.
    """

    ensure_dir(out_dir)

    scout = ScoutAgent()
    planner = PlannerAgent()
    checker = CheckerAgent()
    search = BoundedSearch(scout, planner, checker)

    results: List[Dict] = []
    all_traces: List[Dict] = []

    by_id: Dict[str, BugSpec] = {b.protocol_id: b for b in bugs}

    for p in protocols[:max_protocols]:
        bug = by_id.get(p.protocol_id)
        if bug is None:
            continue

        res, evaluated = search.run(p, bug, max_traces=max_traces_per_protocol)
        results.append(asdict(res))
        for tr in evaluated:
            all_traces.append({
                **trace_to_json(tr),
                "bug_type": bug.bug_type,
            })

    write_jsonl(out_dir / "toy_traces.jsonl", all_traces)
    df = pd.DataFrame(results)
    df.to_csv(out_dir / "toy_summary.csv", index=False)
    return df
