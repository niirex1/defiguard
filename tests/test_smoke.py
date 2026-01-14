from pathlib import Path
import subprocess
import sys

def test_make_paper_outputs():
    repo = Path(__file__).resolve().parents[1]
    out_rel = "results/_tmp_test_paper"
    cmd = [sys.executable, "-m", "defiguard.scripts.make_paper_tables_figs", "--out", out_rel]
    p = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    assert (repo / out_rel / "SUMMARY.md").exists()
