from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from defiguard.metrics import ProtocolOutcome, aggregate
from defiguard.utils import read_jsonl, ensure_dir


ROOT = Path(__file__).resolve().parents[3]  # repo root (src/defiguard/scripts/..)


def _load_metrics_jsonl(path: Path) -> pd.DataFrame:
    rows = read_jsonl(path)
    if not rows:
        raise ValueError(f"No rows in {path}")
    return pd.DataFrame(rows)


def build_table2(incidents_csv: Path, out_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(incidents_csv)
    # Summary in the paper: counts and medians by protocol_type
    g = df.groupby("protocol_type").agg(
        protocols=("protocol_name", "nunique"),
        incidents=("incident_id", "count"),
        median_contracts_per_attack=("contracts_touched", "median"),
    ).reset_index()
    # Order to match the manuscript table
    order = ["AMMs / DEXes", "Lending / borrowing", "Stablecoins", "Yield aggregators",
             "Liquid staking", "Other DeFi (derivatives, options)"]
    g["protocol_type"] = pd.Categorical(g["protocol_type"], categories=order, ordered=True)
    g = g.sort_values("protocol_type").reset_index(drop=True)

    total = pd.DataFrame([{
        "protocol_type": "Total",
        "protocols": int(df["protocol_name"].nunique()),
        "incidents": int(df.shape[0]),
        "median_contracts_per_attack": float(df["contracts_touched"].median()),
    }])
    out = pd.concat([g, total], ignore_index=True)
    ensure_dir(out_csv.parent)
    out.to_csv(out_csv, index=False)
    return out


def build_table4(metrics_jsonl: Path, out_csv: Path) -> pd.DataFrame:
    df = _load_metrics_jsonl(metrics_jsonl)
    # Table 4 is reported as overall performance on DeFiIncidents-CC and DeFiSynth-Proto.
    # Here we aggregate over those two datasets.
    df = df[df["dataset"].isin(["DeFiIncidents-CC", "DeFiSynth-Proto"])].copy()

    out_rows = []
    for method, mdf in df.groupby("method"):
        outcomes = [
            ProtocolOutcome(
                protocol_id=str(r["protocol_id"]),
                rca_hit=float(r["rca_hit"]),
                etd_hit=float(r["etd_hit"]),
                apc=float(r["apc"]),
                fpr=float(r["fpr"]),
            )
            for _, r in mdf.iterrows()
        ]
        agg = aggregate(outcomes)
        out_rows.append({
            "Method": method,
            "RCA": round(agg["RCA"], 2),
            "ETD": round(agg["ETD"], 2),
            "APC": round(agg["APC"], 2),
            "FPR": round(agg["FPR"], 1),
        })
    out = pd.DataFrame(out_rows).sort_values("Method").reset_index(drop=True)
    ensure_dir(out_csv.parent)
    out.to_csv(out_csv, index=False)
    return out


def build_table5(atomic_jsonl: Path, out_csv: Path) -> pd.DataFrame:
    df = _load_metrics_jsonl(atomic_jsonl)
    # Expected columns: method, variant in {atomic,multi-block}, etd_hit
    rows = []
    for method, mdf in df.groupby("method"):
        for variant, vdf in mdf.groupby("variant"):
            rows.append({
                "Method": method,
                "Variant": variant,
                "ETD": round(float(vdf["etd_hit"].mean()), 2),
            })
    out = pd.DataFrame(rows)
    piv = out.pivot(index="Method", columns="Variant", values="ETD").reset_index()
    piv = piv.rename(columns={"atomic": "Atomic", "multi-block": "Multi-block"})
    ensure_dir(out_csv.parent)
    piv.to_csv(out_csv, index=False)
    return piv


def build_table6(metrics_jsonl: Path, out_csv: Path) -> pd.DataFrame:
    df = _load_metrics_jsonl(metrics_jsonl)
    df = df[df["dataset"] == "DeFiZero"].copy()
    rows = []
    for method, mdf in df.groupby("method"):
        rows.append({
            "Method": method,
            "RCA": round(float(mdf["rca_hit"].mean()), 2),
            "ETD": round(float(mdf["etd_hit"].mean()), 2),
        })
    out = pd.DataFrame(rows).sort_values("Method").reset_index(drop=True)
    ensure_dir(out_csv.parent)
    out.to_csv(out_csv, index=False)
    return out


def build_table7(runtime_jsonl: Path, out_csv: Path) -> pd.DataFrame:
    df = _load_metrics_jsonl(runtime_jsonl)
    # Columns: method, latency_min, tokens_k
    rows = []
    for method, mdf in df.groupby("method"):
        rows.append({
            "Method": method,
            "Latency_median_min": int(np.median(mdf["latency_min"])),
            "Latency_95th_min": int(np.quantile(mdf["latency_min"], 0.95, method="higher")),
            "Tokens_median_k": int(np.median(mdf["tokens_k"])),
            "Tokens_95th_k": int(np.quantile(mdf["tokens_k"], 0.95, method="higher")),
        })
    out = pd.DataFrame(rows).sort_values("Method").reset_index(drop=True)
    ensure_dir(out_csv.parent)
    out.to_csv(out_csv, index=False)
    return out


def build_table8(ablation_csv: Path, out_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(ablation_csv)
    out = df.copy()
    ensure_dir(out_csv.parent)
    out.to_csv(out_csv, index=False)
    return out


def fig1_detection_and_apc(metrics_jsonl: Path, incidents_csv: Path, out_dir: Path) -> None:
    dfm = _load_metrics_jsonl(metrics_jsonl)
    dfi = pd.read_csv(incidents_csv)

    # Focus Figure 1 on incident corpus and tool families.
    dfm = dfm[dfm["dataset"] == "DeFiIncidents-CC"].copy()
    dfm = dfm.merge(dfi[["incident_id", "attack_vector"]], left_on="protocol_id", right_on="incident_id", how="left")

    family_map = {
        "Securify [32]": "General",
        "VeriSmart [28]": "General",
        "Oyente [20]": "General",
        "Mythril [23]": "General",
        "GPTScan [29]": "LLM-based",
        "PropertyGPT [19]": "LLM-based",
        "David et al. [10]": "LLM-based",
        "LLM-SmartAudit (BA) [33]": "LLM-based",
        "LLM-SmartAudit (TA) [33]": "LLM-based",
        "DeFiGuard (protocol-only)": "DeFi-focused",
        "DeFiGuard (Full)": "DeFi-focused",
    }
    dfm["family"] = dfm["method"].map(family_map).fillna("Other")

    # Left: per-incident detection by attack vector (family averaged)
    left = dfm.groupby(["attack_vector", "family"]).rca_hit.mean().reset_index()

    ensure_dir(out_dir)
    plt.figure()
    for fam in ["General", "DeFi-focused", "LLM-based"]:
        sdf = left[left["family"] == fam].sort_values("attack_vector")
        plt.plot(sdf["attack_vector"], sdf["rca_hit"], marker="o", label=fam)
    plt.xticks(rotation=25, ha="right")
    plt.ylim(0.0, 1.0)
    plt.ylabel("Per-incident detection rate")
    plt.title("Detection by attack vector (family average)")
    plt.tight_layout()
    plt.savefig(out_dir / "fig1_left_detection_by_vector.png", dpi=200)
    plt.close()

    # Right: distribution of attack-path coverage (APC) by family
    plt.figure()
    for fam in ["General", "DeFi-focused", "LLM-based"]:
        sdf = dfm[dfm["family"] == fam]
        plt.hist(sdf["apc"], bins=10, alpha=0.5, label=fam)
    plt.xlabel("Attack-path coverage (APC)")
    plt.ylabel("Count")
    plt.title("Distribution of APC over incidents")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "fig1_right_apc_distribution.png", dpi=200)
    plt.close()


def fig5_rca_by_vector(metrics_jsonl: Path, incidents_csv: Path, out_dir: Path) -> None:
    dfm = _load_metrics_jsonl(metrics_jsonl)
    dfi = pd.read_csv(incidents_csv)
    dfm = dfm[dfm["dataset"] == "DeFiIncidents-CC"].copy()
    dfm = dfm.merge(dfi[["incident_id", "attack_vector"]], left_on="protocol_id", right_on="incident_id", how="left")

    methods = [
        "Securify [32]",
        "Mythril [23]",
        "GPTScan [29]",
        "LLM-SmartAudit (TA) [33]",
        "DeFiGuard (protocol-only)",
        "DeFiGuard (Full)",
    ]
    dfm = dfm[dfm["method"].isin(methods)]

    out = dfm.groupby(["attack_vector", "method"]).rca_hit.mean().reset_index()

    ensure_dir(out_dir)
    plt.figure()
    for m in methods:
        sdf = out[out["method"] == m].sort_values("attack_vector")
        plt.plot(sdf["attack_vector"], sdf["rca_hit"], marker="o", label=m)
    plt.xticks(rotation=25, ha="right")
    plt.ylim(0.0, 1.0)
    plt.ylabel("RCA")
    plt.title("Root-cause accuracy by attack vector")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(out_dir / "fig5_rca_by_vector.png", dpi=200)
    plt.close()


def fig6_runtime_breakdown(runtime_components_csv: Path, out_dir: Path) -> None:
    df = pd.read_csv(runtime_components_csv)
    ensure_dir(out_dir)

    # Stacked bar by components.
    methods = list(df["method"].unique())
    components = [c for c in df.columns if c not in ["method"]]

    bottom = np.zeros(len(methods))
    plt.figure()
    for c in components:
        vals = df.set_index("method").loc[methods, c].values
        plt.bar(methods, vals, bottom=bottom, label=c)
        bottom += vals
    plt.ylabel("Minutes")
    plt.title("Runtime breakdown (median per protocol)")
    plt.xticks(rotation=20, ha="right")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(out_dir / "fig6_runtime_breakdown.png", dpi=200)
    plt.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=str, default="results/paper", help="Output directory (relative to repo root).")
    args = ap.parse_args()

    out_root = (ROOT / args.out).resolve()
    ensure_dir(out_root)

    # Inputs
    incidents_csv = ROOT / "data/DeFiIncidents-CC/incidents.csv"
    metrics_jsonl = ROOT / "results/raw_logs/metrics.jsonl"
    synth_variants_jsonl = ROOT / "results/raw_logs/synth_variants.jsonl"
    runtime_jsonl = ROOT / "results/raw_logs/runtime_tokens.jsonl"
    ablation_csv = ROOT / "results/tables/table8_ablation.csv"
    runtime_components_csv = ROOT / "results/figures/fig6_runtime_components.csv"

    # Tables
    t2 = build_table2(incidents_csv, out_root / "table2_incident_corpus.csv")
    t4 = build_table4(metrics_jsonl, out_root / "table4_overall_performance.csv")
    t5 = build_table5(synth_variants_jsonl, out_root / "table5_etd_atomic_vs_multiblock.csv")
    t6 = build_table6(metrics_jsonl, out_root / "table6_defizero.csv")
    t7 = build_table7(runtime_jsonl, out_root / "table7_overhead.csv")
    t8 = build_table8(ablation_csv, out_root / "table8_ablation.csv")

    # Figures
    fig_dir = out_root / "figures"
    fig1_detection_and_apc(metrics_jsonl, incidents_csv, fig_dir)
    fig5_rca_by_vector(metrics_jsonl, incidents_csv, fig_dir)
    fig6_runtime_breakdown(runtime_components_csv, fig_dir)

    # Also export markdown summaries for quick inspection.
    with (out_root / "SUMMARY.md").open("w", encoding="utf-8") as f:
        f.write("# DeFiGuard paper artifacts\n\n")
        f.write("## Tables\n\n")
        for name, df in [
            ("Table 2", t2),
            ("Table 4", t4),
            ("Table 5", t5),
            ("Table 6", t6),
            ("Table 7", t7),
            ("Table 8", t8),
        ]:
            f.write(f"### {name}\n\n")
            f.write(df.to_markdown(index=False))
            f.write("\n\n")
        f.write("## Figures\n\n")
        f.write("- Figure 1 (left/right): fig1_left_detection_by_vector.png, fig1_right_apc_distribution.png\n")
        f.write("- Figure 5: fig5_rca_by_vector.png\n")
        f.write("- Figure 6: fig6_runtime_breakdown.png\n")

    print(f"Wrote tables/figures to: {out_root}")


if __name__ == "__main__":
    main()
