"""Branded Word reports on Jon's Saracen Bridge Analytics master template.

Jon's rule: every report is built by editing the master template, never from a blank document, and the cover,
header, footer, palette, panels and table styles are preserved. So the body is rebuilt from clones of the
template's own elements (heading styles, callout panels, label/value tables, data tables, caption lines, page
breaks); only project content changes.
"""
from __future__ import annotations

import copy
import io
from datetime import date

import docx
from docx.oxml.ns import qn

from . import refdata

TEMPLATE = refdata.app_root() / "sources" / "shared" / "Saracen_Bridge_Analytics_Master_Report_Template.docx"


def _set_text(p, text: str) -> None:
    """Replace a paragraph's text, keeping the first run's formatting."""
    runs = p.findall(qn("w:r"))
    for r in runs[1:]:
        p.remove(r)
    if not runs:
        r = p.makeelement(qn("w:r"), {})
        p.append(r)
    else:
        r = runs[0]
    for t in r.findall(qn("w:t")) + r.findall(qn("w:br")):
        r.remove(t)
    t = r.makeelement(qn("w:t"), {})
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)


def _cell_paras(tc):
    return tc.findall(qn("w:p"))


def _set_cell(tc, lines) -> None:
    """Fill a cell: first line uses the first paragraph's format, the rest the last paragraph's."""
    lines = [lines] if isinstance(lines, str) else list(lines) or [""]
    paras = _cell_paras(tc)
    proto_first, proto_rest = paras[0], paras[-1]
    for p in paras:
        tc.remove(p)
    for i, line in enumerate(lines):
        p = copy.deepcopy(proto_first if i == 0 else proto_rest)
        _set_text(p, line)
        tc.append(p)


def _rows(tbl):
    return tbl.findall(qn("w:tr"))


def _cells(tr):
    return tr.findall(qn("w:tc"))


class Builder:
    def __init__(self):
        self.doc = docx.Document(str(TEMPLATE))
        body = self.doc.element.body
        self.kids = list(body.iterchildren())
        k = self.kids
        find_p = lambda style, text: next(e for e in k if e.tag == qn("w:p")
                                          and docx.text.paragraph.Paragraph(e, self.doc).style.name == style
                                          and docx.text.paragraph.Paragraph(e, self.doc).text.strip().startswith(text))
        tables = [e for e in k if e.tag == qn("w:tbl")]
        text_of = lambda e: "".join(t.text or "" for t in e.iter(qn("w:t")))
        tbl = lambda start: next(t for t in tables if text_of(t).strip().startswith(start))
        self.proto = {
            "h1": find_p("Heading 1", "1. Executive Summary"),
            "h2": find_p("Heading 2", "1.1"),
            "body": find_p("Body Text", "[State the recommended"),
            "bullet": find_p("List Bullet", "[Finding one"),
            "caption": find_p("Normal", "KEY REPORT METRICS"),
            "panel": tbl("EXECUTIVE CONCLUSION"),
            "metrics": tbl("Overall assessment"),
            "labels": tbl("TITLE / PROJECT"),
            "data": tbl("Comparable / Benchmark"),
            "pagebreak": next(e for e in k if e.tag == qn("w:p") and e.find(f".//{qn('w:br')}[@{qn('w:type')}='page']") is not None),
            "spacer": k[k.index(tbl("EXECUTIVE CONCLUSION")) + 1],
        }
        self.proto = {n: copy.deepcopy(e) for n, e in self.proto.items()}
        self.toc = tbl("1. Executive Summary")
        self.cover_meta = tbl("PREPARED FOR")
        self.control = tbl("Version")
        self.standard = tbl("DOCUMENT STANDARD")
        start = k.index(find_p("Heading 1", "1. Executive Summary")) - 1          # the page break before section 1
        self.anchor = find_p("Normal", "PREPARED BY")
        for e in k[start:k.index(self.anchor)]:
            body.remove(e)
        for e in (self.standard, find_p("Placeholder", "The table of contents")):
            body.remove(e)
        self.body = body
        self.first_h1 = True

    # -- primitives (inserted before the closing PREPARED BY block)
    def _add(self, el):
        self.anchor.addprevious(el)
        return el

    def _para(self, kind, text):
        p = copy.deepcopy(self.proto[kind])
        _set_text(p, text)
        return self._add(p)

    def h1(self, text):
        self._add(copy.deepcopy(self.proto["pagebreak"]))
        self._para("h1", text)

    def h2(self, text):
        self._para("h2", text)

    def body_text(self, text):
        for chunk in [t for t in str(text).split("\n") if t.strip()] or ["Not materially applicable."]:
            self._para("body", chunk.strip())

    def bullets(self, items):
        for it in items or ["Not materially applicable."]:
            self._para("bullet", str(it).strip())

    def caption(self, text):
        self._para("caption", text.upper())

    def panel(self, label, lines):
        t = copy.deepcopy(self.proto["panel"])
        tc = _cells(_rows(t)[0])[0]
        _set_cell(tc, [label] + ([lines] if isinstance(lines, str) else list(lines)))
        self._add(t)
        self._add(copy.deepcopy(self.proto["spacer"]))

    def metrics(self, pairs):
        """Four headline metrics: labels on top, values below (the template's KEY REPORT METRICS table)."""
        t = copy.deepcopy(self.proto["metrics"])
        head, vals = _rows(t)
        for (label, value), hc, vc in zip(pairs, _cells(head), _cells(vals)):
            _set_cell(hc, label)
            _set_cell(vc, value)
        self._add(t)
        self._add(copy.deepcopy(self.proto["spacer"]))

    def labels(self, pairs):
        """Label/value rows (the template's project overview table)."""
        t = copy.deepcopy(self.proto["labels"])
        rows = _rows(t)
        proto_row = rows[1]
        for r in rows:
            t.remove(r)
        for label, value in pairs:
            r = copy.deepcopy(proto_row)
            a, b = _cells(r)
            _set_cell(a, label.upper())
            _set_cell(b, value or "Not materially applicable.")
            t.append(r)
        self._add(t)
        self._add(copy.deepcopy(self.proto["spacer"]))

    def data(self, headers, rows):
        """Header row plus data rows (the template's comparables table), resized to the column count."""
        t = copy.deepcopy(self.proto["data"])
        n = len(headers)
        grid = t.find(qn("w:tblGrid"))
        cols = grid.findall(qn("w:gridCol"))
        total = sum(int(c.get(qn("w:w"))) for c in cols)
        for c in cols[n:]:
            grid.remove(c)
        while len(grid.findall(qn("w:gridCol"))) < n:
            grid.append(copy.deepcopy(cols[-1]))
        for c in grid.findall(qn("w:gridCol")):
            c.set(qn("w:w"), str(total // n))
        all_rows = _rows(t)
        head_proto, row_proto = all_rows[0], all_rows[1]
        for r in all_rows:
            t.remove(r)

        def fit(r, values):
            tcs = _cells(r)
            for tc in tcs[n:]:
                r.remove(tc)
            while len(_cells(r)) < n:
                r.append(copy.deepcopy(_cells(r)[-1]))
            for tc, v in zip(_cells(r), values):
                w = tc.find(f"{qn('w:tcPr')}/{qn('w:tcW')}")
                if w is not None:
                    w.set(qn("w:w"), str(total // n))
                _set_cell(tc, str(v))
            return r
        t.append(fit(copy.deepcopy(head_proto), headers))
        for values in rows:
            t.append(fit(copy.deepcopy(row_proto), values))
        self._add(t)
        self._add(copy.deepcopy(self.proto["spacer"]))

    # -- cover, header, contents
    def cover(self, report_title, project, recipient, toc_entries):
        k = self.kids
        replace = {"[REPORT TITLE]": report_title, "[PROJECT / CLIENT]": project,
                   "[CLIENT / AUTHORISED RECIPIENT]": recipient, "[D MONTH YYYY]": _long_date(),
                   "[FINAL / V1.0]": "V1.0", "[ANALYST / EXECUTIVE]": "Development Executive", "[REPORT TITLE]  |  [PROJECT]": f"{report_title}  |  {project}"}
        parts = [self.body] + [s.header._element for s in self.doc.sections] + [s.footer._element for s in self.doc.sections]
        for root in parts:
            for p in root.iter(qn("w:p")):
                txt = "".join(t.text or "" for t in p.iter(qn("w:t"))).strip()
                if txt in replace:                                   # placeholder split across runs
                    _set_text(p, replace[txt])
                    continue
                for t in p.iter(qn("w:t")):                          # placeholder inside one run
                    for old, new in replace.items():
                        if t.text and old in t.text:
                            t.text = t.text.replace(old, new)
        rows = _rows(self.toc)
        proto_row = rows[0]
        for r in rows:
            self.toc.remove(r)
        for entry in toc_entries:
            r = copy.deepcopy(proto_row)
            a, b = _cells(r)
            _set_cell(a, entry)
            _set_cell(b, "")
            self.toc.append(r)
        del k

    def bytes(self) -> bytes:
        settings = self.doc.settings.element
        if settings.find(qn("w:updateFields")) is None:          # page numbers refresh when Word opens it
            u = settings.makeelement(qn("w:updateFields"), {qn("w:val"): "true"})
            settings.append(u)
        buf = io.BytesIO()
        self.doc.save(buf)
        return buf.getvalue()


def _long_date(d: date | None = None) -> str:
    d = d or date.today()
    return f"{d.day} {d.strftime('%B %Y')}"


SECTIONS = ["1. Executive Summary", "2. Revised Logline and 5-Sentence Pitch", "3. Synopsis", "4. Creative Analysis",
            "5. Market Positioning Snapshot", "6. Risk Assessment", "7. Development Notes", "8. Strengths and Weaknesses",
            "9. Budget Band Guidance", "10. Weighted Scoring Matrix", "11. Final Recommendation"]


def coverage_docx(r: dict, recipient: str = "Authorised recipient") -> bytes:
    s = r["sections"]
    st, cr, mk, dv, vd = s["story"], s["creative"], s["market"], s["develop"], s["verdict"]
    b = Builder()
    b.cover("SCRIPT COVERAGE REPORT", r["title"], recipient, SECTIONS)

    b.h1(SECTIONS[0])
    b.panel("EXECUTIVE CONCLUSION", [st["concept_sentence"], vd["overall_assessment"]])
    b.caption("Key report metrics")
    b.metrics([("Verdict", vd["verdict"]), ("Commercial readiness", f"{r['commercial_readiness']} / 100"),
               ("Composite score", f"{r['composite']:.2f} / 10"), ("Budget band", dv["budget_band"])])
    b.h2("1.1 Commercial Potential")
    b.body_text(vd["commercial_potential"])
    b.h2("1.2 Major Creative Strengths")
    b.bullets(vd["major_strengths"])
    b.h2("1.3 Primary Creative and Commercial Issues")
    b.bullets(vd["primary_issues"])

    b.h1(SECTIONS[1])
    b.h2("2.1 Logline")
    b.body_text(st["logline"])
    b.h2("2.2 Five-Sentence Pitch")
    b.body_text(" ".join(x.strip() for x in st["pitch"]))

    b.h1(SECTIONS[2])
    for para in st["synopsis"]:
        b.body_text(para)

    b.h1(SECTIONS[3])
    for title, key in [("A. Concept and Premise", "concept_and_premise"), ("B. Story and Structure", "story_and_structure"),
                       ("C. Characters", "characters")]:
        b.h2(title)
        b.body_text(cr[key])
    if cr.get("casting"):
        b.caption("Casting suggestions for principal roles")
        b.data(["Role", "Suggestions"], [[c["role"], ", ".join(c["names"])] for c in cr["casting"]])
    for title, key in [("D. Dialogue", "dialogue"), ("E. Themes and Tone", "themes_and_tone"),
                       ("F. Worldbuilding", "worldbuilding"), ("G. Production Feasibility", "production_feasibility")]:
        b.h2(title)
        b.body_text(cr[key])

    b.h1(SECTIONS[4])
    b.labels([("Target demographic", mk["target_demographic"]), ("Audience profile", mk["audience_profile"]),
              ("Release pathway", mk["release_pathway"]), ("Sales agent tier", mk["sales_agent_tier"]),
              ("Distributor / platform", mk["distributor_suitability"]),
              ("Awards / festival potential", mk["awards_festival_potential"]),
              ("Current market fit", mk["current_market_fit"])])
    b.h2("5.1 Comparable Titles")
    from .coverage import comparable_text
    b.bullets([comparable_text(c) for c in mk["comparables"]])

    b.h1(SECTIONS[5])
    b.bullets(mk["risks"])

    b.h1(SECTIONS[6])
    b.h2("7.1 Top 3 Rewrite Priorities")
    b.bullets(dv["rewrite_priorities"])
    b.h2("7.2 Development Notes")
    b.bullets(dv["development_notes"])
    for title, key in [("7.3 Character", "character_notes"), ("7.4 Dialogue", "dialogue_notes"),
                       ("7.5 Structure and Pacing", "structure_notes"), ("7.6 Commercial Sharpening", "commercial_notes")]:
        b.h2(title)
        b.body_text(dv[key])

    b.h1(SECTIONS[7])
    b.h2("8.1 Strengths")
    b.bullets(dv["strengths"])
    b.h2("8.2 Weaknesses")
    b.bullets(dv["weaknesses"])

    b.h1(SECTIONS[8])
    b.labels([("Estimated budget band", dv["budget_band"]), ("Risk if the budget is too low", dv["risk_if_budget_too_low"]),
              ("Risk if the budget is too high", dv["risk_if_budget_too_high"]),
              ("To justify a higher budget", dv["to_justify_higher_budget"])])
    b.h2("9.1 Budget Pressure Points")
    b.bullets(dv["budget_pressure_points"])
    b.h2("9.2 Cost-Control Opportunities")
    b.bullets(dv["cost_control_opportunities"])
    b.body_text("Indicative only, and subject to a full budget, schedule and production review.")

    b.h1(SECTIONS[9])
    rows = [[k, str(r["scores"][k]), f"{int(w * 100)}%", f"{r['scores'][k] * w:.2f}"] for k, w in r["weights"].items()]
    rows.append(["Composite Score", "", "100%", f"{r['composite']:.2f}"])
    b.data(["Category", "Score 1–10", "Weight", "Weighted Score"], rows)
    b.labels([("Composite score", f"{r['composite']:.2f} / 10"),
              ("Commercial readiness score", f"{r['commercial_readiness']} / 100")])

    b.h1(SECTIONS[10])
    b.panel("FINAL RECOMMENDATION", [f"Final verdict: {vd['verdict']}", vd["reason_for_verdict"]])
    b.labels([("Commercial readiness", f"{r['commercial_readiness']} / 100"),
              ("Development priority", vd["development_priority"]), ("Best next step", vd["best_next_step"])])
    return b.bytes()


LB_SECTIONS = ["1. Executive Snapshot", "2. One-Sentence Sales Proposition", "3. Logline Review and Rewrite", "4. Story Sell",
               "5. Character Sell", "6. Director Positioning", "7. Visual Tone Analysis", "8. Design and Presentation Analysis",
               "9. Genre and Audience Positioning", "10. Film / TV Comparables", "11. Budget Signals and Production Scale",
               "12. Sales Agent / Distributor Usefulness", "13. Recommended Look Book Structure", "14. Priority Improvements",
               "15. Scored Assessment", "16. Final Verdict"]


def lookbook_docx(r: dict, recipient: str = "Authorised recipient") -> bytes:
    """Jon's Look Book Sales Tool Analysis on his master template."""
    s = r["sections"]
    sn, st, vi, mk, rb, sc = s["snapshot"], s["story"], s["visual"], s["market"], s["rebuild"], s["scores"]
    b = Builder()
    b.cover("LOOK BOOK SALES TOOL ANALYSIS", r["title"], recipient, LB_SECTIONS)

    b.h1(LB_SECTIONS[0])
    b.panel("EXECUTIVE SNAPSHOT", [sn["immediate_impression"], f"Verdict: {r['verdict_text']}"])
    b.caption("Key report metrics")
    b.metrics([("Look Book sales score", f"{r['final_score']} / 100"), ("Verdict", r["verdict"]),
               ("Sales tool usefulness", f"{mk['sales_tool_usefulness_score']} / 100"), ("Pages reviewed", str(r["pages"]))])
    b.labels([("Project format", sn["format"]), ("Genre", sn["genre"]), ("Tone", sn["tone"]),
              ("Core story proposition", sn["core_proposition"]), ("Primary audience", sn["primary_audience"]),
              ("Likely market lane", sn["market_lane"]), ("Main strength", sn["main_strength"]), ("Main weakness", sn["main_weakness"])])

    b.h1(LB_SECTIONS[1])
    b.labels([("Current proposition", sn["current_proposition"] or "Not stated in the look book."),
              ("Improved proposition", sn["improved_proposition"]), ("Commercial hook", sn["commercial_hook"])])

    b.h1(LB_SECTIONS[2])
    b.labels([("Logline as presented", sn["current_logline"] or "No logline in the look book.")])
    b.body_text(sn["logline_review"])
    b.panel("REVISED LOGLINE", [sn["revised_logline"]])

    b.h1(LB_SECTIONS[3])
    b.body_text(st["story_sell"])
    for title, key in [("4.1 What Is Clear", "clear"), ("4.2 What Is Unclear or Underdeveloped", "unclear"), ("4.3 Should Appear Earlier", "move_earlier")]:
        if st[key]:
            b.h2(title)
            b.bullets(st[key])

    b.h1(LB_SECTIONS[4])
    b.data(["Character", "Function and hook", "Actor type", "Status", "Names"],
           [[c["character"], f"{c['function']} {c['emotional_hook']}".strip(), c["actor_type"], c["status"], ", ".join(c["names"]) or "None"]
            for c in st["characters"]])
    b.body_text("Suggested names are proposals for discussion only and are not attachments.")

    b.h1(LB_SECTIONS[5])
    if st["director_named"]:
        b.labels([("Director", st["director_named"])])
    b.body_text(st["director_assessment"])
    if st["director_suggestions"]:
        b.caption("Suggested directors (not attached)")
        b.data(["Director", "Why"], [[d["name"], d["why"]] for d in st["director_suggestions"]])

    b.h1(LB_SECTIONS[6])
    b.body_text(vi["visual_tone"])
    b.labels([("Does it visually sell the project?", vi["sells_visually"]), ("Does the tone match the story?", vi["tone_matches_story"]),
              ("Cinematic or generic?", vi["cinematic_or_generic"]), ("Does it show the finished film?", vi["shows_finished_film"]),
              ("Castable and directable?", vi["castable_and_directable"])])

    b.h1(LB_SECTIONS[7])
    b.body_text(vi["design_presentation"])
    pages = [[f"Strongest: page {p['page']}", p["why"]] for p in vi["strongest_pages"]] + \
            [[f"Weakest: page {p['page']}", p["why"]] for p in vi["weakest_pages"]]
    if pages:
        b.data(["Page", "Why"], pages)
    b.h2("8.1 Cut, Simplify or Redesign")
    b.bullets(vi["cut_simplify_redesign"])

    b.h1(LB_SECTIONS[8])
    b.labels([("Primary genre", mk["primary_genre"]), ("Secondary genre", mk["secondary_genre"]), ("Audience", mk["audience"]),
              ("Likely buyers and distributors", mk["buyers"]), ("Theatrical potential", mk["theatrical_potential"]),
              ("Streamer / broadcaster potential", mk["streamer_broadcaster_potential"]),
              ("International appeal", mk["international_appeal"]), ("Is positioning clear?", mk["positioning_verdict"])])

    b.h1(LB_SECTIONS[9])
    b.body_text(mk["comparables_assessment"])
    if mk["better_comparables"]:
        b.data(["Comparable", "Year", "Why it helps"], [[c["title"], str(c["year"]), c["why"]] for c in mk["better_comparables"]])

    b.h1(LB_SECTIONS[10])
    b.labels([("Budget", mk["budget_summary"]), ("Budget feel", mk["budget_feel"])])
    b.bullets(mk["scale_signals"])

    b.h1(LB_SECTIONS[11])
    b.body_text(mk["sales_usefulness"])
    b.labels([("Sales tool usefulness score", f"{mk['sales_tool_usefulness_score']} / 100")])

    b.h1(LB_SECTIONS[12])
    b.data(["Slide", "Title", "Purpose", "Content", "Visual direction"],
           [[str(x["slide"]), x["title"], x["purpose"], x["content"], x["visual_direction"]] for x in rb["slides"]])

    b.h1(LB_SECTIONS[13])
    b.h2("14.1 Must Fix")
    b.bullets(rb["must_fix"])
    b.h2("14.2 Should Improve")
    b.bullets(rb["should_improve"])
    if rb["optional_enhancement"]:
        b.h2("14.3 Optional Enhancement")
        b.bullets(rb["optional_enhancement"])

    b.h1(LB_SECTIONS[14])
    b.data(["Category", "Score / 100"], [[k, str(v)] for k, v in r["scores"].items()] + [["Average score", f"{r['average']:.1f}"]])
    b.labels([("Average score", f"{r['average']:.1f} / 100"), ("Final Look Book sales score", f"{r['final_score']} / 100")])

    b.h1(LB_SECTIONS[15])
    b.panel("FINAL VERDICT", [r["verdict_text"], sc["verdict_reason"]])
    return b.bytes()
