"""Production Agreement Builder: Jon's own scripts, run in-process (works inside the frozen app)."""
from __future__ import annotations

import importlib
import sys
import tempfile
from pathlib import Path

from . import refdata

SKILL = refdata.app_root() / "sources" / "t10_agreement_builder" / "skills" / "populate-production-agreement"
BLANK_WORKBOOK = SKILL / "assets" / "TKE_SB_Project_Input_Workbook.xlsx"


def _workflow():
    scripts = str(SKILL / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    keep, sys.dont_write_bytecode = sys.dont_write_bytecode, True   # leave Jon's source folder exactly as shipped
    try:
        return importlib.import_module("run_workflow")
    finally:
        sys.dont_write_bytecode = keep


def build(inputs_xlsx: bytes, draft_name: str, include_proposed: bool = False) -> dict:
    wf = _workflow()
    with tempfile.TemporaryDirectory() as tmp:
        inp = Path(tmp) / "inputs.xlsx"
        inp.write_bytes(inputs_xlsx)
        out = Path(tmp) / f"{draft_name}.docx"
        try:
            result = wf.run(str(inp), str(out), include_proposed=include_proposed)
        except (ValueError, KeyError) as e:
            report = out.with_suffix(".validation.json")
            detail = report.read_text() if report.exists() else ""
            error, problems = _plain_failure(str(e), detail)
            return {"ok": False, "error": error, "problems": problems, "validation": detail}
        except Exception:                 # not a workbook at all (renamed file, damaged download)
            return {"ok": False, "error": "This file can't be opened as an Excel workbook. Use Download input workbook, fill that in, and upload it.",
                    "problems": [], "validation": ""}
        files = {out.name: out.read_bytes()}
        for extra in Path(tmp).glob(f"{draft_name}.*"):
            if extra.suffix != ".docx":
                files[extra.name] = extra.read_bytes()
        return {"ok": True, "result": result, "files": files}


def _plain_failure(error: str, detail: str) -> tuple[str, list[str]]:
    """Jon's validator reports codes and field IDs; say what went wrong in words (15 Oct audit: the Studio showed the raw
    report and a temporary path that no longer exists)."""
    import json
    import re
    error = re.sub(r";?\s*see \S+\.validation\.json", "", error).strip() or "Validation failed"
    try:
        errs = json.loads(detail).get("errors", []) if detail else []
    except ValueError:
        errs = []
    if any(e.get("code") == "FIELD_IDS" for e in errs):
        return ("This isn't the Studio's input workbook: its field IDs don't match the master. Use Download input workbook, "
                "fill that in, and upload it.", [])
    problems = []
    for e in errs[:12]:
        f = e.get("fields") or []
        problems.append(e.get("message", e.get("code", "Problem")) + (f" ({', '.join(f[:4])}{' …' if len(f) > 4 else ''})" if f else ""))
    if len(errs) > 12:
        problems.append(f"…and {len(errs) - 12} more")
    return error + ". Nothing was built.", problems
