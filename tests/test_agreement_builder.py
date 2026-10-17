"""Jon's Production Agreement Builder already runs offline: run its own 33-check suite on a temp copy."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "sources" / "t10_agreement_builder" / "skills" / "populate-production-agreement"


def test_agreement_builder_suite(tmp_path):
    work = tmp_path / "skill"
    shutil.copytree(SRC, work)
    out = subprocess.run([sys.executable, "scripts/test_workflow.py"], cwd=work,
                         capture_output=True, text=True, timeout=300)
    assert out.returncode == 0, out.stderr
    report = json.loads(out.stdout)
    assert report["passed"] == len(report["checks"]) == 33
