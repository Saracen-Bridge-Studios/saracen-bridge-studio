"""Validate structured project inputs, then populate only fixed-master controls."""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib, json, re
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from populate_static import populate, read_inputs, digest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
STATUSES = {'Confirmed', 'Proposed', 'Unknown', 'Not applicable'}

def verify_assets():
    lock = json.loads((ASSETS / 'asset_lock.json').read_text())
    for filename, expected in lock.items():
        actual = hashlib.sha256((ASSETS / filename).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('Bundled asset changed: ' + filename + '; use an authorised master release')

def validate(inputs, include_proposed=False):
    verify_assets()
    manifest = json.loads((ASSETS / 'field_map.json').read_text())
    if digest(ASSETS / manifest['master_file']) != manifest['fixed_package_sha256']:
        raise ValueError('Master fingerprint differs from field map')
    sheets = {f['sheet'] for f in manifest['fields']}
    records = read_inputs(inputs, sheets)
    baseline = read_inputs(ASSETS / 'TKE_SB_Project_Input_Workbook.xlsx', sheets)
    expected = {f['id'] for f in manifest['fields']}
    errors, warnings = [], []
    def issue(collection, code, message, fields=()):
        collection.append({'code': code, 'message': message, 'fields': list(fields)})
    if set(records) != expected:
        issue(errors, 'FIELD_IDS', 'Workbook IDs must exactly match the master', sorted(set(records)^expected))
    numeric = {}
    for f in manifest['fields']:
        fid = f['id']
        if fid not in records: continue
        r = records[fid]
        for key in ('clause', 'context', 'type'):
            if r[key] != baseline[fid][key]:
                issue(errors, 'FIXED_WORKBOOK_METADATA', 'Fixed workbook '+key+' changed', [fid])
        status, value = r['status'], r['value'].strip()
        if status not in STATUSES:
            issue(errors, 'STATUS', 'Invalid field status', [fid]); continue
        if status == 'Unknown':
            issue(warnings, 'UNKNOWN', 'Missing or unresolved; keep the master placeholder', [fid])
            if value: issue(warnings, 'IGNORED_VALUE', 'Unknown field has a value which will not be inserted', [fid])
            continue
        if not value:
            issue(errors, 'EMPTY_VALUE', status+' requires a value; use Unknown for missing information', [fid]); continue
        if status in ('Confirmed', 'Proposed') and not r['source'].strip():
            issue(errors, 'SOURCE_REQUIRED', 'Provide a traceable source or explicit user instruction', [fid])
        if status == 'Not applicable':
            if value != 'Not applicable' or not r['notes'].strip():
                issue(errors, 'NA_REASON', 'Use the exact value Not applicable and explain why in Notes', [fid])
            continue
        if any(c in r['value'] for c in ('[', ']', '\n', '\r', '\t')):
            issue(errors, 'FIELD_TEXT', 'Use single-line text without placeholder brackets or tabs', [fid])
        if status == 'Proposed':
            issue(warnings, 'PROPOSED', 'Proposed term is not evidence of agreement or commitment', [fid])
        if len(r['value']) > 350:
            issue(warnings, 'LONG_TEXT', 'Long field text requires careful page review; do not shrink the master font', [fid])
        if f['type'] in ('Amount', 'Number', 'Rate points'):
            try:
                if not re.fullmatch(r'-?\d+(?:\.\d+)?', value): raise InvalidOperation
                n = Decimal(value)
                if not n.is_finite(): raise InvalidOperation
                numeric[fid] = n
                if f['type'] == 'Amount' and n < 0 and fid != 'S08_039_AMOUNT':
                    issue(errors, 'NEGATIVE_AMOUNT', 'Amounts must be non-negative', [fid])
                if f['type'] == 'Rate points' and not 0 <= n <= 100:
                    issue(errors, 'RATE_RANGE', 'Enter percentage points from 0 to 100, e.g. 4 for 4%', [fid])
                if f['type'] == 'Number' and (n != n.to_integral_value() or n < 1):
                    issue(errors, 'INTEGER', 'Enter a positive whole number', [fid])
                if f['type'] == 'Number' and fid.startswith('S10_') and n > 10:
                    issue(errors, 'TIER_RANGE', 'A referenced waterfall tier must be 1 to 10', [fid])
            except InvalidOperation:
                issue(errors, 'NUMERIC', 'Enter a finite plain number without currency signs, commas or percent signs', [fid])
    if include_proposed and any(r['status']=='Proposed' and r['value'].strip() for r in records.values()):
        version=records.get('S00_003_VERSION', {})
        if version.get('status') not in ('Confirmed','Proposed') or 'draft' not in version.get('value','').lower():
            issue(errors, 'DRAFT_LABEL', 'A document containing proposed terms must have DRAFT in its version field', ['S00_003_VERSION'])
    def active_number(fid):
        r=records.get(fid,{})
        if r.get('status')=='Confirmed' or (include_proposed and r.get('status')=='Proposed'):
            return numeric.get(fid)
        return None
    def equal_sum(ids, target, code, message):
        values=[active_number(fid) for fid in ids]
        if all(v is not None for v in values) and abs(sum(values)-target)>Decimal('0.02'):
            issue(errors, code, message, ids)
    pool_ids=['S15_001_RATE','S15_002_RATE']
    equal_sum(pool_ids,Decimal(100),'POOL_TOTAL','Producer/Talent and Financier pools must total 100%')
    allocation_ids=['S15_004_RATE','S15_006_RATE','S15_008_RATE','S15_010_RATE']
    equal_sum(allocation_ids,Decimal(100),'ALLOCATION_TOTAL','Explicit Producer/Talent Pool allocations must total 100%')
    funding_ids=[f'S08_{i:03d}_AMOUNT' for i in (2,6,10,14,18,22,26,30,34)]
    funding=[]
    for fid in funding_ids:
        n=active_number(fid)
        if records.get(fid,{}).get('status')=='Not applicable': n=Decimal(0)
        funding.append(n)
    total=active_number('S08_037_TOTAL')
    if total is not None and all(n is not None for n in funding) and abs(sum(funding)-total)>Decimal('0.02'):
        issue(errors,'FUNDING_TOTAL','Funding lines do not reconcile to the stated total within two cents',funding_ids+['S08_037_TOTAL'])
    elif any(n is not None for n in funding) and any(n is None for n in funding):
        issue(warnings,'FUNDING_INCOMPLETE','Funding reconciliation cannot pass until every line is entered or explicitly Not applicable',funding_ids)
    budget=active_number('S08_038_BUDGET'); delta=active_number('S08_039_AMOUNT')
    if all(n is not None for n in (total,budget,delta)) and abs((total-budget)-delta)>Decimal('0.02'):
        issue(errors,'FUNDING_DIFFERENCE','Shortfall/surplus must equal total funding minus budget',['S08_037_TOTAL','S08_038_BUDGET','S08_039_AMOUNT'])
    project_budget=active_number('S01_006_AMOUNT')
    if budget is not None and project_budget is not None and abs(budget-project_budget)>Decimal('0.02'):
        issue(errors,'BUDGET_MISMATCH','Project budget and funding schedule budget differ',['S01_006_AMOUNT','S08_038_BUDGET'])
    if records.get('S22_001_YES_NO',{}).get('value','').upper()=='YES':
        incomplete=[f['id'] for f in manifest['fields'] if f['section']=='22' and (records.get(f['id'],{}).get('status') in ('Unknown','Not applicable') or not records.get(f['id'],{}).get('value','').strip())]
        if incomplete: issue(warnings,'EXCLUSIVITY_INCOMPLETE','YES selected with incomplete particulars; do not describe exclusivity as effective',incomplete)
    issue(warnings,'MANUAL_REVIEW','Verify source documents, authority, execution, duplicate funding/bridge counts, cash-flow timing, fee bases/caps, tax assumptions, waterfall priorities and legal suitability. Automated checks do not establish these facts.')
    return {'master_version':manifest['master_version'],'fields':len(expected),'status_counts':dict(Counter(r['status'] for r in records.values())), 'include_proposed':include_proposed,'errors':errors,'warnings':warnings,'technical_validation_passed':not errors,'ready_for_signature':False}

def run(inputs, output, include_proposed=False, validate_only=False):
    output=Path(output)
    if output.suffix.lower()!='.docx': raise ValueError('Output must have .docx extension')
    reserved=[ASSETS/'TKE_SB_Static_Master_v1.docx', ASSETS/'TKE_SB_Project_Input_Workbook.xlsx', Path(inputs)]
    if output.resolve() in [p.resolve() for p in reserved]: raise ValueError('Refusing to overwrite master, template workbook or inputs')
    if output.exists(): raise ValueError('Output already exists; choose a new draft version')
    result=validate(inputs,include_proposed)
    output.parent.mkdir(parents=True,exist_ok=True)
    report_path=output.with_suffix('.validation.json')
    if report_path.exists(): raise ValueError('Validation report already exists; choose a new version')
    report_path.write_text(json.dumps(result,indent=2)+'\n')
    if result['errors']: raise ValueError('Validation failed; see '+str(report_path))
    if not validate_only:
        result['population']=populate(ASSETS/'TKE_SB_Static_Master_v1.docx',inputs,ASSETS/'field_map.json',output,include_proposed)
        report_path.write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--include-proposed',action='store_true')
    p.add_argument('--validate-only',action='store_true')
    a=p.parse_args()
    try:
        result=run(a.inputs,a.output,a.include_proposed,a.validate_only)
        print(json.dumps({'technical_validation_passed':result['technical_validation_passed'],'ready_for_signature':False,'errors':len(result['errors']),'warnings':len(result['warnings']),'population':result.get('population')}))
    except (ValueError, KeyError) as e:
        p.exit(1,str(e)+'\n')
