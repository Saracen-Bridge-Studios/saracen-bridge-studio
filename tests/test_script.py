"""Screenplay parsing details that the intake fixtures don't cover."""
from pathlib import Path

from studio import script


def test_production_draft_scene_numbers_are_not_part_of_the_heading():
    """13 Oct: a 100-page Final Draft PDF of Tim's read as 0 scenes, because every heading carried its scene
    number at both margins (pypdf layout text keeps them)."""
    u = script._unnumber
    assert u("1   EXT. MANHATTAN CITY STREETS - NIGHT                           1") == "EXT. MANHATTAN CITY STREETS - NIGHT"
    assert u("12A   INT. RESTAURANT, NEW YORK - NIGHT     12A *") == "INT. RESTAURANT, NEW YORK - NIGHT"
    assert u("A7 INT./EXT. CAR - DAY A7") == "INT./EXT. CAR - DAY"
    assert u("EXT. ROUTE 66 - DAY") == "EXT. ROUTE 66 - DAY"            # no scene number: untouched
    assert u("EXT. ROUTE 66") == "EXT. ROUTE 66"
    assert u("23   OMITTED   23") == "23   OMITTED   23"              # not a heading: untouched
    assert u("2 men walk in.") == "2 men walk in."


def test_numbered_pdf_layout_lines_give_scenes_and_cast():
    lines = [
        "1   EXT. MANHATTAN CITY STREETS - NIGHT                           1",
        "",
        "    Our CAMERA ROAMS the streets.",
        "",
        "2   INT. RESTAURANT, NEW YORK - NIGHT                             2",
        "",
        "                        EMILY",
        "              I heard that over at Capital Securities--",
        "",
        "                        BRAD",
        "              Anyway.",
        "",
    ]
    scenes = script._from_lines(lines)
    assert [s["heading"] for s in scenes] == ["EXT. MANHATTAN CITY STREETS - NIGHT", "INT. RESTAURANT, NEW YORK - NIGHT"]
    assert scenes[1]["time_of_day"] == "NIGHT" and scenes[1]["int_ext"] == "INT"
    assert list(scenes[1]["characters"]) == ["EMILY", "BRAD"]


def test_location_ignores_same_time_resuming_and_curly_apostrophes():
    a = script._split_heading("INT. BILL & MARLA'S APARTMENT - SAME TIME")
    b = script._split_heading("INT. BILL & MARLA’S APARTMENT - RESUMING")
    assert a["location"] == b["location"] == "BILL & MARLA'S APARTMENT"
    assert a["time_of_day"] == "SAME TIME" and b["time_of_day"] == "RESUMING"


def test_title_page_typography_is_undone():
    """Tim's Library, 13 Oct: "S N O W S T O R M" and "ASSASSINATIONASSASSINATION"."""
    from studio.script import clean_title
    assert clean_title("S N O W S T O R M") == "SNOWSTORM"
    assert clean_title("T H E  L O N G  N I G H T") == "THE LONG NIGHT"
    assert clean_title("ASSASSINATIONASSASSINATION") == "ASSASSINATION"
    for keep in ("AND LOVE KNOCKED", "Bora Bora", "Liar Liar", "CAN-BC-PSTC", "M*A*S*H", "BOBO", "A B"):
        assert clean_title(keep) == keep


def test_titles_saved_before_the_fix_are_cleaned_on_start(tmp_path, monkeypatch):
    import json
    from studio import store
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    rec = store.save_run("coverage", "S N O W S T O R M", {}, {"breakdown": {"title": "S N O W S T O R M"}}, summary={"pages": 117})
    store.enqueue("coverage", "coverage", rec["id"], "S N O W S T O R M")
    store._TITLES_CLEANED.clear()                       # as on the next start of the Studio
    assert store.list_runs("coverage")["runs"][0]["title"] == "SNOWSTORM"
    assert store.list_jobs("coverage", 10)["jobs"][0]["title"] == "SNOWSTORM"
    saved, _ = store.get_run("coverage", rec["id"])
    assert saved["title"] == "SNOWSTORM" and saved["outputs"]["breakdown"]["title"] == "SNOWSTORM"


def test_numbers_glued_to_headings_and_a_logo_title_page():
    """Tim's WEREWOLF draft, 13 Oct: '1     1EXT. DEEP FOREST - NIGHT' (the right-hand number printed first, glued
    to the heading) read as 1 scene of 133, and the title came out as the credit 'Written and Created b y'."""
    lines = ["Written and Created b                         y", "        Stan Lee", "", "28-08-2026, Final Edit", "",
             "1                                       1EXT. DEEP FOREST - NIGHT", "", "A shape moves.", "",
             "                 IGUANA", "        Move!", "", "2A        2AINT. UNDERGROUND LAB", "", "                 NYX",
             "        Ready.", "", "3     INT. CORBIN HOUSE - AFTERNOON     3", "", "Quiet."]
    scenes = script._from_lines(lines)
    assert [s["heading"] for s in scenes] == ["EXT. DEEP FOREST - NIGHT", "INT. UNDERGROUND LAB", "INT. CORBIN HOUSE - AFTERNOON"]
    assert script._pick_title(lines) == ""                                   # no title in the text: a logo
    assert script.title_from_filename("WEREWOLF Script 28-08-26") == "WEREWOLF"
    assert script.title_from_filename("The_Lighthouse_Keeper_v3_FINAL") == "The Lighthouse Keeper"
    assert script._pick_title(["THE LIGHTHOUSE KEEPER", "", "Written by", "Mara Quill"]) == "THE LIGHTHOUSE KEEPER"


def test_scripts_read_by_an_older_reader_are_read_again(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from studio import store
    from studio.server import app
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    data = (Path(__file__).parent / "fixtures" / "sample.fountain").read_bytes()
    c = TestClient(app)
    first = c.post("/api/tools/script/intake", data={"tool": "coverage"}, files=[("files", ("sample.fountain", data))]).json()[0]
    rec, folder = store.get_run("coverage", first["run_id"])
    old = dict(rec["outputs"]["breakdown"], parser=1, scenes=rec["outputs"]["breakdown"]["scenes"][:1], title="Written and Created b y")
    store.update_run("coverage", first["run_id"], outputs={"breakdown": old}, summary={"scene_count": 1}, title="Written and Created b y")
    again = c.post("/api/tools/script/intake", data={"tool": "coverage"}, files=[("files", ("sample.fountain", data))]).json()[0]
    assert again["duplicate"] and again["scene_count"] == 4 and again["title"] == first["title"]
    assert store.get_run("coverage", first["run_id"])[0]["outputs"]["breakdown"]["parser"] == script.PARSER_VERSION


def test_colon_style_headings_and_dated_file_names():
    """15 Oct audit: Tim's 'Ultimate Feature' draft writes most headings 'INT: KITCHEN - DAY' and read as 12 scenes
    of 162; the title fell back to the file name with its draft note and date still on it."""
    lines = ["INT: KITCHEN - DAY", "", "Kettle on.", "", "EXT.: HARBOUR WALL - NIGHT", "", "Wind.", "",
             "INT. HALLWAY - CONTINUOUS", "", "EXT: ", "", "I/E: VAN - MOVING - DAY", "", "Bumps."]
    scenes = script._from_lines(lines)
    assert [s["location"] for s in scenes] == ["KITCHEN", "HARBOUR WALL", "HALLWAY", "", "VAN - MOVING"]
    assert [s["int_ext"] for s in scenes] == ["INT", "EXT", "INT", "EXT", "INT/EXT"]
    assert scenes[1]["time_of_day"] == "NIGHT"
    for not_heading in ("INTERIOR DESIGN IS HER THING.", "EXTRA: A CROWD", "INTO THE DARK", "EXTERIOR"):
        assert not script.HEADING.match(not_heading)
    t = script.title_from_filename
    assert t("Ultimate Feature - FINAL Sept 2026") == "Ultimate Feature"
    assert t("AND LOVE KNOCKED - 04-26-23-1") == "AND LOVE KNOCKED"
    assert t("Known Associate - MF - 04.26.26 (1)") == "Known Associate - MF"
    assert t("1917 Final Draft") == "1917"


def test_library_refresh_fixes_a_colon_heading_title_and_flags_the_coverage(tmp_path, monkeypatch):
    """Tim's Library, 15 Oct: the 'Ultimate Feature' coverage run is titled with its first scene heading
    ('EXT: MOUNTAIN HIGHWAY – LATE AFTERNOON') and its coverage was written from 12 scenes of 162."""
    from fastapi.testclient import TestClient
    from studio import store
    from studio.server import app, fresh_breakdown
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    text = "\n\n".join(f"{'INT' if i % 2 else 'EXT'}: PLACE {i} – DAY\n\nSomething happens.\n\nANNA\nLine {i}." for i in range(20))
    name = "Ultimate Feature - FINAL Sept 2026.fountain"
    c = TestClient(app)
    first = c.post("/api/tools/script/intake", data={"tool": "coverage"}, files=[("files", (name, text.encode()))]).json()[0]
    assert first["scene_count"] == 20 and first["title"] == "Ultimate Feature"
    rid = first["run_id"]
    rec, _ = store.get_run("coverage", rid)
    old = dict(rec["outputs"]["breakdown"], parser=2, scene_count=2, title="EXT: PLACE 0 – DAY")
    store.update_run("coverage", rid, outputs={"breakdown": old, "coverage": {"sections": {}}}, summary={"scene_count": 2}, title="EXT: PLACE 0 – DAY")
    rec = fresh_breakdown("coverage", rid)
    assert rec["title"] == "Ultimate Feature" and rec["summary"]["scene_count"] == 20 and rec["summary"]["coverage_stale"] is True
    assert "coverage" in rec["outputs"]                                   # kept: Write again replaces it
    assert store.list_runs("coverage")["runs"][0]["title"] == "Ultimate Feature"


def test_a_leading_full_stop_forces_a_heading_only_in_fountain():
    pdf_lines = ["EXT. HARBOUR - DAY", "", "Mara loads the", ".45 calibre pistol and waits.", "", ".", "", "MARA", "Now."]
    sc = script._from_lines(pdf_lines)
    assert [s["heading"] for s in sc] == ["EXT. HARBOUR - DAY"] and sc[0]["characters"] == {"MARA": 1}
    fountain = script.parse_fountain("EXT. HARBOUR - DAY\n\nGulls.\n\n.FLASHBACK - MARA AS A GIRL\n\nShe runs.\n\n.\n\nEnd.\n")
    assert [s["heading"] for s in fountain["scenes"]] == ["EXT. HARBOUR - DAY", "FLASHBACK - MARA AS A GIRL"]


def test_a_fountain_saved_on_windows_reads_the_same_as_one_from_a_mac():
    """5 Nov: the first Windows test run read the sample .fountain as 0 scenes. Windows editors end lines with \\r\\n,
    which hid the blank line after the title page, so the whole script was taken for a title page. Notepad also
    adds a byte-order mark."""
    FIX = Path(__file__).parent / "fixtures"
    mac = (FIX / "sample.fountain").read_bytes().replace(b"\r\n", b"\n")
    windows = b"\xef\xbb\xbf" + mac.replace(b"\n", b"\r\n")
    a, b = script.parse("sample.fountain", mac), script.parse("sample.fountain", windows)
    assert a["scene_count"] == 4 and a["title"] == "The Lighthouse Keeper"
    assert {k: b[k] for k in ("scene_count", "title", "speaking_roles", "scenes")} == {k: a[k] for k in ("scene_count", "title", "speaking_roles", "scenes")}
    assert script.text("sample.fountain", windows) == script.text("sample.fountain", mac)
    assert script.scene_texts("sample.fountain", windows) == script.scene_texts("sample.fountain", mac)
