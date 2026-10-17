"""Load Saracen Bridge reference data from recalculated source workbooks into SQLite.
Every row keeps provenance: source file, its SHA-256 (of the ORIGINAL file), sheet, row number."""
import sqlite3, re, sys, json, hashlib, pathlib, openpyxl, warnings
warnings.filterwarnings('ignore')
R = pathlib.Path(sys.argv[1]); RECALC = pathlib.Path(sys.argv[2]); DRY = '--dry' in sys.argv
SPEC = [  # (workbook stem, sheet, table, header_row or None=auto)
 ('10_Saracen_Bridge_Production_Incentive_Model_Stage_2_Audited_v1_1','Programme Rules','inc_programme_rules',None),
 ('10_Saracen_Bridge_Production_Incentive_Model_Stage_2_Audited_v1_1','Incentive Database','inc_programme_database',4),
 ('10_Saracen_Bridge_Production_Incentive_Model_Stage_2_Audited_v1_1','FX & Financing','inc_fx_financing',None),
 ('10_Saracen_Bridge_Production_Incentive_Model_Stage_2_Audited_v1_1','Coverage Gaps','inc_coverage_gaps',None),
 ('10_Saracen_Bridge_Production_Incentive_Model_Stage_2_Audited_v1_1','Sources & Audit','inc_sources_audit',4),
 ('10_Saracen_Bridge_Production_Incentive_Model_Stage_2_Audited_v1_1','Audit Regression','inc_audit_regression',None),
 ('SB_Global_Production_Rate_Database_v1_2','Jurisdiction Index','rate_jurisdictions',None),
 ('SB_Global_Production_Rate_Database_v1_2','Crew Rates','rate_crew',None),
 ('SB_Global_Production_Rate_Database_v1_2','Cast Rates','rate_cast',None),
 ('SB_Global_Production_Rate_Database_v1_2','Supplemental Roles','rate_supplemental_roles',None),
 ('SB_Global_Production_Rate_Database_v1_2','Non-Labour Rates','rate_non_labour',None),
 ('SB_Global_Production_Rate_Database_v1_2','Regional Factors','rate_regional_factors',None),
 ('SB_Global_Production_Rate_Database_v1_2','Labour Rules','rate_labour_rules',None),
 ('SB_Global_Production_Rate_Database_v1_2','Sources','rate_sources',None),
 ('SB_Global_Production_Rate_Database_v1_2','Validation Issues','rate_validation_issues',None),
 ('SB_Master_Feature_Film_Chart_of_Accounts_v1_0 (1)','Chart of Accounts','coa_accounts',6),
 ('SB_Master_Feature_Film_Chart_of_Accounts_v1_0 (1)','Controlled Lists','coa_controlled_lists',None),
 ('SB_Filmustage_Budget_Mapping_Specification_v1_0 (1)','Category Mapping','fs_category_mapping',None),
 ('SB_Filmustage_Budget_Mapping_Specification_v1_0 (1)','Account Mapping','fs_account_mapping',None),
 ('SB_Filmustage_Budget_Mapping_Specification_v1_0 (1)','Field Mapping','fs_field_mapping',None),
 ('SB_Filmustage_Budget_Mapping_Specification_v1_0 (1)','Import Validation','fs_import_validation',None),
 ('Saracen_Bridge_Actor_Value_Database_v2_2_Three_Actor_Update','Actor Database','talent_actors',None),
 ('Saracen_Bridge_Actor_Value_Database_v2_2_Three_Actor_Update','Tier Assumptions','talent_actor_tiers',None),
 ('Saracen_Bridge_Director_Value_Database_V4_3_Fully_Reverified_with_Fee_Model','Director Master','talent_directors',None),
 ('Saracen_Bridge_Director_Value_Database_V4_3_Fully_Reverified_with_Fee_Model','Scorecard','talent_director_scorecard',None),
 ('Saracen_Bridge_Director_Value_Database_V4_3_Fully_Reverified_with_Fee_Model','Director Fee Summary','talent_director_fees',None),
 ('Saracen_Bridge_Director_Value_Database_V4_3_Fully_Reverified_with_Fee_Model','Lists & Weights','talent_director_weights',None),
 ('Saracen_Bridge_Sales_Valuation_Engine_v4_1_Integrated_Imports','CONTROL_PANEL','sales_control_panel',None),
 ('Saracen_Bridge_Sales_Valuation_Engine_v4_1_Integrated_Imports','TERRITORY_BASELINES','sales_territory_baselines',None),
 ('Saracen_Bridge_Sales_Valuation_Engine_v4_1_Integrated_Imports','TERRITORY_OVERLAYS','sales_territory_overlays',None),
 ('Saracen_Bridge_Sales_Valuation_Engine_v4_1_Integrated_Imports','PROXY_ASSUMPTIONS','sales_proxy_assumptions',None),
 ('Saracen_Bridge_Sales_Valuation_Engine_v4_1_Integrated_Imports','FX_RATES','sales_fx_rates',None),
 ('Saracen_Bridge_Sales_Valuation_Engine_v4_1_Integrated_Imports','DATA_DICTIONARY','sales_data_dictionary',None),
 ('Saracen_Bridge_Sales_Valuation_Engine_v4_1_Integrated_Imports','LISTS','sales_lists',None),
 ('Saracen_Bridge_Brand_Integration_Database_Next_10_Options','Brands','brand_accounts',None),
 ('Saracen_Bridge_Brand_Integration_Database_Next_10_Options','Film Integration Evidence','brand_film_evidence',None),
 ('Saracen_Bridge_Brand_Integration_Database_Next_10_Options','HubSpot Mapping','brand_hubspot_mapping',None),
 # Contacts sheet deliberately NOT loaded: named individuals; lawful basis unconfirmed (register G-17).
]
def norm(h, i):
    h = re.sub(r'[^0-9a-zA-Z]+', '_', str(h or '').strip()).strip('_').lower()
    return h or f'col_{i}'
def header_row(ws):
    best, br = -1, 1
    for r in range(1, 9):
        vals = [c.value for c in ws[r]]
        n = sum(1 for v in vals if isinstance(v, str) and v.strip())
        nxt = sum(1 for v in ws[r+1] if v.value is not None) if r < ws.max_row else 0
        if n >= 2 and n + min(nxt, n) > best: best, br = n + min(nxt, n), r
    return br
orig = {p.stem: p for p in (R/'sources').rglob('*.xlsx')}
db = None if DRY else sqlite3.connect(R/'data'/'studio_reference.db')
report = []
for stem, sheet, table, hr in SPEC:
    wb = openpyxl.load_workbook(RECALC/f'{stem}.xlsx', data_only=True, read_only=False)
    ws = wb[sheet]; hr = hr or header_row(ws)
    heads, seen = [], set()
    for i, c in enumerate(ws[hr]):
        h = norm(c.value, i)
        while h in seen: h += '_x'
        seen.add(h); heads.append(h)
    keep = [i for i, c in enumerate(ws[hr]) if c.value is not None]
    rows = []
    for r in range(hr+1, ws.max_row+1):
        vals = [ws.cell(r, i+1).value for i in keep]
        if all(v is None or (isinstance(v, str) and not v.strip()) for v in vals): continue
        rows.append([r] + [v.isoformat() if hasattr(v, 'isoformat') else v for v in vals])
    cols = ['source_row'] + [heads[i] for i in keep]
    src = orig[stem]; h = hashlib.sha256(src.read_bytes()).hexdigest()
    report.append({'table': table, 'sheet': sheet, 'header_row': hr, 'rows': len(rows), 'cols': len(cols)-1,
                   'source': str(src.relative_to(R)), 'sha256': h, 'headers': cols[1:9]})
    if db:
        db.execute(f'DROP TABLE IF EXISTS "{table}"')
        db.execute(f'CREATE TABLE "{table}" ({", ".join(chr(34)+c+chr(34) for c in cols)})')
        db.executemany(f'INSERT INTO "{table}" VALUES ({",".join("?"*len(cols))})', rows)
if db:
    db.execute('DROP TABLE IF EXISTS _provenance')
    db.execute('CREATE TABLE _provenance (table_name, source_file, source_sha256, sheet, header_row, row_count, loaded_note)')
    db.executemany('INSERT INTO _provenance VALUES (?,?,?,?,?,?,?)',
        [(x['table'], x['source'], x['sha256'], x['sheet'], x['header_row'], x['rows'], 'values from LibreOffice recalculation of the original file') for x in report])
    db.commit()
for x in report: print(f"{x['table']:28} hdr={x['header_row']} rows={x['rows']:5} cols={x['cols']:3} {x['headers']}")
