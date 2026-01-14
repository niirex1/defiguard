from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .agents import ScoutAgent, PlannerAgent, CheckerAgent
from .protocol import ProtocolSpec, BugSpec, TraceSpec


@dataclass
class SearchResult:
    protocol_id: str
    bug_type: str
    best_trace_id: str
    best_variant: str
    rca: float
    etd: float
    apc: float
    evaluated_traces: int


class BoundedSearch:
    """Deterministic bounded search over abstract trace candidates."""

    def __init__(self, scout: ScoutAgent, planner: PlannerAgent, checker: CheckerAgent):
        self.scout = scout
        self.planner = planner
        self.checker = checker

    def run(self, p: ProtocolSpec, bug: BugSpec, max_traces: int = 10) -> Tuple[SearchResult, List[TraceSpec]]:
        hypotheses = self.scout.propose_hypotheses(p)

        best: Optional[Tuple[float, float, float, TraceSpec]] = None
        evaluated: List[TraceSpec] = []

        for h in hypotheses:
            # Allocate a small budget per hypothesis.
            budget = max(1, max_traces // max(1, len(hypotheses)))
            traces = self.planner.plan_traces(p, h, budget=budget)
            for tr in traces:
                evaluated.append(tr)
                rca, etd, apc = self.checker.score(tr, bug)
                key = (etd, rca, apc)
                if best is None or key > (best[1], best[0], best[2]):
                    best = (rca, etd, apc, tr)

        if best is None:
            raise RuntimeError("No traces generated")

        rca, etd, apc, tr = best
        res = SearchResult(
            protocol_id=p.protocol_id,
            bug_type=bug.bug_type,
            best_trace_id=tr.trace_id,
            best_variant=tr.variant,
            rca=float(rca),
            etd=float(etd),
            apc=float(apc),
            evaluated_traces=len(evaluated),
        )
        return res, evaluated
