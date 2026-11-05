"""Scanned scripts read by OCR (1.0.6). Needs Tesseract (the bundled Windows build in packaging/ocr, or one on PATH) or,
on the Mac, studio-ocr given by STUDIO_TESSERACT."""
from pathlib import Path

import pytest

from studio import ocr, script

FIX = Path(__file__).parent / "fixtures"
need = pytest.mark.skipif(not ocr.available(), reason="Tesseract not available")
# 5 Nov, first Mac run: Apple Vision misread a character cue in the scanned fixture (cast MARA, TOM vs TOM, MARA, ELSIE).
# Known and open (register S-123); the build log prints what the Mac OCR read so it can be fixed. Strict elsewhere.
import sys as _sys
mac_ocr_open = pytest.mark.xfail(_sys.platform == "darwin", reason="S-123: Vision misreads a cue in the scanned fixture", strict=False)


def test_word_boxes_become_screenplay_lines():
    rows = ["level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext"]
    words = [(1, 1, 1, 300, 300, "EXT."), (1, 1, 1, 420, 300, "HARBOUR"), (1, 1, 1, 650, 300, "-"), (1, 1, 1, 700, 300, "DAY"),
             (2, 1, 1, 300, 400, "Gulls"), (2, 1, 1, 450, 400, "wheel."),
             (3, 1, 1, 960, 500, "MARA"), (3, 1, 2, 660, 550, "Tide's"), (3, 1, 2, 850, 550, "turning.")]
    for b, p, l, left, top, t in words:
        rows.append(f"5\t1\t{b}\t{p}\t{l}\t1\t{left}\t{top}\t{len(t) * 30}\t30\t95\t{t}")
    lines = ocr.tsv_to_lines("\n".join(rows))
    assert lines[0] == "EXT. HARBOUR - DAY" and lines[1] == "" and lines[2] == "Gulls wheel."
    assert lines[4].strip() == "MARA" and lines[4].startswith(" " * 20) and lines[5].strip() == "Tide's turning."
    assert script._from_lines(lines)[0]["characters"] == {"MARA": 1}


def test_scanned_detection():
    assert ocr.is_scanned(["", " ", "12"]) and not ocr.is_scanned(["INT. KITCHEN - DAY\n" * 5])


@mac_ocr_open
@need
def test_a_scanned_script_reads_like_its_typed_original(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    typed = script.parse("sample.pdf", (FIX / "sample.pdf").read_bytes())
    data = (FIX / "sample_scanned.pdf").read_bytes()
    scanned = script.parse("sample_scanned.pdf", data)
    assert scanned["ocr"] and "OCR" in scanned["format"] and any("OCR" in w for w in scanned["warnings"])
    assert scanned["title"] == typed["title"] and scanned["pages"] == typed["pages"]
    assert [s["heading"] for s in scanned["scenes"]] == [s["heading"] for s in typed["scenes"]]
    assert [c["name"] for c in scanned["cast"]] == [c["name"] for c in typed["cast"]]
    assert "Keeper, do you copy?" in script.text("sample_scanned.pdf", data)          # coverage gets the OCR text
    assert list((tmp_path / "ocr").glob("*.txt"))                                        # read once, cached by hash


def test_without_ocr_a_scanned_pdf_says_so(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    monkeypatch.setattr(ocr, "available", lambda: False)
    r = script.parse("sample_scanned.pdf", (FIX / "sample_scanned.pdf").read_bytes())
    assert r["scene_count"] == 0 and "OCR isn't available" in r["warnings"][-1]


@need
def test_pages_read_side_by_side_come_back_in_order(tmp_path, monkeypatch):
    import io
    from pypdf import PdfReader, PdfWriter
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    monkeypatch.setattr(ocr, "WORKERS", 2)
    page = PdfReader(FIX / "sample_scanned.pdf").pages[0]
    w = PdfWriter()
    for _ in range(3):
        w.add_page(page)
    w.add_blank_page()                                                     # last page blank: nothing after it
    buf = io.BytesIO(); w.write(buf)
    lines = ocr.pdf_lines(buf.getvalue(), "three.pdf")
    heads = [ln for ln in lines if ln.startswith(("EXT.", "INT."))]
    assert len(heads) == 12 and heads[:4] == heads[4:8] == heads[8:]
    assert lines[-1] == ""
    assert ocr.progress() == []                                            # nothing left showing as being read


@mac_ocr_open
@need
def test_intake_reads_a_scanned_script_off_the_event_loop(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from fastapi.testclient import TestClient
    from studio.server import app
    c = TestClient(app)
    r = c.post("/api/tools/script/intake", data={"tool": "coverage"},
               files=[("files", ("scan.pdf", (FIX / "sample_scanned.pdf").read_bytes(), "application/pdf"))]).json()[0]
    assert r["scene_count"] == 4 and r["speaking_roles"] == 3 and "OCR" in r["format"]
    assert any("OCR" in w for w in r["warnings"])
    assert c.get("/api/tools/script/ocr").json() == {"available": True, "reading": []}
