from __future__ import annotations

from dataclasses import asdict
from typing import List, Tuple

from .protocol import ProtocolSpec, BugSpec, TraceCall, TraceSpec


class ScoutAgent:
    """Produces high-level hypotheses about cross-contract risk.

    In the paper this role corresponds to "localization" signals.
    Here it is deterministic, rule-based, and operates only on CSV metadata.
    """

    def propose_hypotheses(self, p: ProtocolSpec) -> List[str]:
        # Deterministic ordering to keep runs reproducible.
        hypotheses: List[str] = []
        fam = p.bug_family.lower()
        profile = p.interface_profile.lower()

        if "oracle" in fam or "oracle" in profile:
            hypotheses.append("oracle manipulation via pool price shift")
            hypotheses.append("stale oracle / missing TWAP guard")

        if "liquidation" in fam or "lending" in profile:
            hypotheses.append("liquidation parameter misuse")
            hypotheses.append("collateral factor misconfiguration")

        if "routing" in fam or "amm" in profile:
            hypotheses.append("router slippage omission")
            hypotheses.append("multi-hop routing without minOut")

        if "governance" in fam:
            hypotheses.append("governance action without timelock")
            hypotheses.append("privileged role misuse")

        # Fallback: generic cross-contract issue.
        if not hypotheses:
            hypotheses.append("cross-contract state inconsistency")

        return hypotheses


class PlannerAgent:
    """Turns a hypothesis into abstract call-sequence candidates."""

    def plan_traces(self, p: ProtocolSpec, hypothesis: str, budget: int = 8) -> List[TraceSpec]:
        # Two variants in the paper: atomic and multi-block.
        variants = ["atomic", "multi-block"]
        traces: List[TraceSpec] = []

        # Deterministic template bank.
        templates: List[List[TraceCall]] = []

        h = hypothesis.lower()
        if "oracle" in h or "twap" in h:
            templates.append([
                TraceCall("attacker", "pool", "swap", "shift spot price"),
                TraceCall("attacker", "lending", "borrow", "borrow against manipulated price"),
            ])
            templates.append([
                TraceCall("attacker", "pool", "swap", "shift spot price"),
                TraceCall("attacker", "oracle", "read", "use stale reading"),
                TraceCall("attacker", "lending", "borrow", "borrow against stale price"),
            ])

        if "liquidation" in h or "collateral" in h:
            templates.append([
                TraceCall("attacker", "lending", "deposit", "post minimal collateral"),
                TraceCall("attacker", "lending", "borrow", "borrow close to limit"),
                TraceCall("attacker", "lending", "liquidate", "force liquidation edge case"),
            ])

        if "slippage" in h or "routing" in h or "router" in h:
            templates.append([
                TraceCall("attacker", "router", "swap", "no minOut"),
                TraceCall("attacker", "pool", "swap", "front-run price move"),
                TraceCall("attacker", "router", "swap", "victim executes swap"),
            ])

        if "governance" in h or "timelock" in h:
            templates.append([
                TraceCall("attacker", "governance", "propose", "malicious parameter change"),
                TraceCall("attacker", "governance", "execute", "no delay"),
                TraceCall("attacker", "treasury", "transfer", "drain via privileged action"),
            ])

        if not templates:
            templates.append([
                TraceCall("attacker", "protocol", "call", "unmodeled external call"),
                TraceCall("attacker", "protocol", "call", "state update order mismatch"),
            ])

        # Expand templates into traces for each variant.
        tid = 1
        for v in variants:
            for t in templates:
                if len(traces) >= budget:
                    break
                calls = list(t)
                if v == "multi-block":
                    # Insert an abstract "wait" to represent cross-block behavior.
                    calls = calls[:1] + [TraceCall("system", "chain", "wait", "next block")] + calls[1:]
                traces.append(
                    TraceSpec(
                        trace_id=f"TOY-{p.protocol_id}-{tid:03d}-{v}",
                        protocol_id=p.protocol_id,
                        variant=v,
                        calls=calls,
                        hypothesis=hypothesis,
                    )
                )
                tid += 1
        return traces


class CheckerAgent:
    """Checks whether a trace matches a bug pattern (offline, abstract).

    This is a *safe* proxy for the paper's verification stage.
    It uses keyword patterns only, not bytecode or exploit payloads.
    """

    def score(self, trace: TraceSpec, bug: BugSpec) -> Tuple[float, float, float]:
        # Returns (rca_hit, etd_hit, apc)
        funcs = [c.function for c in trace.calls]
        notes = " ".join([c.notes for c in trace.calls]).lower()
        bt = bug.bug_type.lower()

        # Root-cause hit proxy: hypothesis aligns with bug type.
        h = trace.hypothesis.lower()
        rca = 1.0 if any(k in h for k in bt.replace("-", " ").split()) else 0.0

        # Exploit-trace hit proxy: deterministic pattern matching.
        etd = 0.0
        if "missing-twap" in bt or "oracle" in bt:
            etd = 1.0 if ("swap" in funcs and "borrow" in funcs) else 0.0
        elif "router-missing-slippage" in bt:
            etd = 1.0 if ("swap" in funcs and "no minout" in notes) else 0.0
        elif "no-delay-governance" in bt:
            etd = 1.0 if ("propose" in funcs and "execute" in funcs) else 0.0
        elif "bad-liquidation" in bt or "liquidation" in bt:
            etd = 1.0 if ("liquidate" in funcs and "borrow" in funcs) else 0.0
        else:
            etd = 1.0 if len(funcs) >= 2 else 0.0

        # Attack-path coverage proxy: normalized trace length.
        denom = max(1, len(trace.calls) + 2)
        apc = min(1.0, len(trace.calls) / float(denom))

        return rca, etd, apc


def trace_to_json(trace: TraceSpec) -> dict:
    return {
        "trace_id": trace.trace_id,
        "protocol_id": trace.protocol_id,
        "variant": trace.variant,
        "hypothesis": trace.hypothesis,
        "calls": [asdict(c) for c in trace.calls],
    }
