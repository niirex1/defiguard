from __future__ import annotations

import argparse
from pathlib import Path
import shutil

from .export_tables import main as export_tables_main


EXPECTED_FIGURES = [
    "defiguard_attack_type_accuracy.pdf",
    "defiguard_tool_coverage.pdf",
    "defiguard-searchflow.pdf",
    "multi-agent-architecture.pdf",
    "defiguard_collaboration.pdf",
]


def write_summary(out_dir: Path) -> None:
    summary = out_dir / "SUMMARY.md"
    tables = sorted((out_dir).glob("table*.csv"))
    figures = sorted((out_dir / "figures").glob("*"))
    lines = [
        "# Reproduced paper artifacts",
        "",
        "## Tables",
    ]
    lines.extend([f"- {p.name}" for p in tables])
    lines.append("")
    lines.append("## Figures")
    lines.extend([f"- {p.name}" for p in figures])
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_figures(fig_src: Path, fig_out: Path) -> None:
    fig_out.mkdir(parents=True, exist_ok=True)
    if not fig_src.exists():
        return
    for path in fig_src.iterdir():
        if path.is_file():
            shutil.copy2(path, fig_out / path.name)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate paper tables and figures from deterministic inputs.")
    ap.add_argument("--config", required=True)
    ap.add_argument("--eval_dir", required=True)
    ap.add_argument("--manifest_dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tables_source", default="results/tables")
    ap.add_argument("--figures_source", default="results/figures")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Export tables
    import sys
    old_argv = sys.argv[:]
    try:
        sys.argv = [
            "export_tables.py",
            "--source", args.tables_source,
            "--manifest_dir", args.manifest_dir,
            "--out", str(out_dir),
        ]
        export_tables_main()
    finally:
        sys.argv = old_argv

    # Copy figures into paper directory
    copy_figures(Path(args.figures_source), out_dir / "figures")

    write_summary(out_dir)
    print(f"Wrote paper tables and figures to {out_dir}")


if __name__ == "__main__":
    main()
