"""Controlled vocabularies and rule tables that live in Jon's documents rather than workbooks."""
import sqlite3, re, hashlib, pathlib, docx, sys
R = pathlib.Path(sys.argv[1]); d = sqlite3.connect(R/'data'/'studio_reference.db')
# BFI Cultural Test criteria from 02_BFI_Summary_of_Cultural_Test_Points-july-2026.docx
src = next((R/'sources').rglob('02_BFI_Summary_of_Cultural_Test_Points*.docx'))
rows = []
for t in docx.Document(src).tables:
    for r in t.rows:
        c = [x.text.strip() for x in r.cells]
        if re.fullmatch(r'[A-D]\d?(\([a-c]\))?', c[0]):
            mx = re.search(r'(\d+)', c[2]); rows.append((c[0], c[0][0], c[1], int(mx.group(1)), c[2].lower().startswith('up to')))
d.execute('DROP TABLE IF EXISTS bfi_cultural_test'); d.execute('CREATE TABLE bfi_cultural_test (ref, section, criterion, max_points, graduated)')
d.executemany('INSERT INTO bfi_cultural_test VALUES (?,?,?,?,?)', rows)
d.execute("INSERT INTO _provenance VALUES ('bfi_cultural_test',?,?,'tables',NULL,?,'parsed from docx; guidance checked 12 Jul 2026')",
          (str(src.relative_to(R)), hashlib.sha256(src.read_bytes()).hexdigest(), len(rows)))
# Controlled vocabularies (02 Shared Incentive Protocol; FPM SKILL; FFA SKILLs; Agreement Builder)
V = {
 'eligibility_status': ['Eligible','Excluded','Manual Review','Unknown'],
 'evidence_status': ['Confirmed','Assumption','Unresolved','Superseded'],
 'gate_status': ['PASS','PRELIMINARY','FAIL'],
 'rag': ['Green','Amber','Red'],
 'recommendation_status': ['INDICATIVE','PRELIMINARY','CONDITIONALLY PREFERRED','VALIDATED'],
 'finance_source_status': ['Confirmed cash','Signed but conditional','Draft / conditional','LOI / non-binding','User instruction / to document','Assumption only','Missing'],
 'cp_matrix_status': ['Not Received','Under Review','Deficient','Draft','Awaiting Signature','Executed','Satisfied','Waived','Not Applicable'],
 'evidence_class': ['Verified/executed','Documented/conditional','Draft','Indicative','Represented','Assumed','Not received/unable to verify'],
 'greenlight_decision': ['GREENLIGHT READY','CONDITIONAL GREENLIGHT','HOLD – MATERIAL CLOSING BLOCKERS','DEVELOPMENT / NOT YET CLOSABLE'],
 'agreement_field_status': ['Confirmed','Proposed','Unknown','Not applicable'],
 'workstream': ['Development','Prep','Principal Photography','Second Unit','Stage','Virtual Production','SFX','Post','VFX','CGI','Animation','Sound','Music','Dubbing/Localisation','AI/Software/R&D','Training','Travel/Accommodation','Other'],
 'attachment_status': ['Wish list','Informal interest','Availability confirmed','Offer submitted','LOI','Conditional agreement','Signed agreement'],
}
d.execute('DROP TABLE IF EXISTS vocab'); d.execute('CREATE TABLE vocab (vocab, ordinal, value)')
d.executemany('INSERT INTO vocab VALUES (?,?,?)', [(k,i,v) for k,vs in V.items() for i,v in enumerate(vs)])
# Attachment certainty ladder (#4 SKILL.md)
d.execute('DROP TABLE IF EXISTS sales_attachment_certainty'); d.execute('CREATE TABLE sales_attachment_certainty (attachment_status, certainty)')
d.executemany('INSERT INTO sales_attachment_certainty VALUES (?,?)', list(zip(V['attachment_status'], [0,.15,.30,.50,.70,.85,1.0])))
d.commit(); print('bfi rows', len(rows), [r[:2]+(r[3],) for r in rows]); print('vocabs', len(V))
