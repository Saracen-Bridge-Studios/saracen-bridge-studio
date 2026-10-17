"""Regression checks using temporary synthetic workbooks, never live project files."""
import json, tempfile
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from run_workflow import ASSETS, validate, run
from populate_static import digest
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
ns={'s':S}

def fixture(output, updates, formula=None):
    template=ASSETS/'TKE_SB_Project_Input_Workbook.xlsx'
    with ZipFile(template) as z:
        shared=[''.join(x.itertext()) for x in etree.fromstring(z.read('xl/sharedStrings.xml')).findall('{'+S+'}si')] if 'xl/sharedStrings.xml' in z.namelist() else []
        changes={}
        for name in z.namelist():
            if not name.startswith('xl/worksheets/sheet') or not name.endswith('.xml'): continue
            tree=etree.fromstring(z.read(name)); changed=False
            for row in tree.findall('.//{'+S+'}row'):
                cells={''.join(filter(str.isalpha,c.get('r'))):c for c in row.findall('{'+S+'}c')}
                if 'A' not in cells: continue
                c=cells['A'];v=c.find('{'+S+'}v')
                fid=shared[int(v.text)] if c.get('t')=='s' and v is not None else ''.join(c.itertext())
                if fid not in updates: continue
                for col,value in updates[fid].items():
                    c=cells.get(col)
                    if c is None:
                        c=etree.SubElement(row,'{'+S+'}c',r=col+row.get('r'))
                    for child in list(c): c.remove(child)
                    c.set('t','inlineStr')
                    st=etree.SubElement(c,'{'+S+'}is');etree.SubElement(st,'{'+S+'}t').text=str(value)
                    if formula==(fid,col):
                        c.attrib.pop('t',None)
                        for child in list(c):c.remove(child)
                        etree.SubElement(c,'{'+S+'}f').text='1+1'
                        etree.SubElement(c,'{'+S+'}v').text='2'
                changed=True
            if changed: changes[name]=etree.tostring(tree)
        with ZipFile(output,'w',ZIP_DEFLATED) as out:
            for item in z.infolist():out.writestr(item,changes.get(item.filename,z.read(item.filename)))
    return output

def active(value,status='Confirmed'):
    return {'D':value,'E':status,'F':'Synthetic test instruction; not a real production'}

if __name__=='__main__':
    passed=[]
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder)
        def check(name, updates, code=None, include=False, formula=None):
            path=fixture(root/(name+'.xlsx'),updates,formula)
            try:
                r=validate(path,include)
            except ValueError:
                if code!='EXCEPTION':raise
            else:
                codes=[e['code'] for e in r['errors']]
                assert (code in codes) if code else not codes,(name,codes)
            passed.append(name)
            return path
        check('empty-draft',{})
        check('confirmed-missing-source',{'S00_001_PROJECT_TITLE':{'D':'Test','E':'Confirmed','F':''}},'SOURCE_REQUIRED')
        check('confirmed-missing-value',{'S00_001_PROJECT_TITLE':{'D':'','E':'Confirmed','F':'Test'}},'EMPTY_VALUE')
        check('unknown-value-ignored',{'S00_001_PROJECT_TITLE':{'D':'Unverified','E':'Unknown'}})
        check('bad-status',{'S00_001_PROJECT_TITLE':{'D':'Test','E':'Executed'}},'STATUS')
        check('changed-context',{'S00_001_PROJECT_TITLE':{'C':'Altered context'}},'FIXED_WORKBOOK_METADATA')
        check('changed-type',{'S00_001_PROJECT_TITLE':{'G':'Amount'}},'FIXED_WORKBOOK_METADATA')
        check('formula-in-value',{'S01_006_AMOUNT':active('2')},'EXCEPTION',formula=('S01_006_AMOUNT','D'))
        check('numeric-comma',{'S01_006_AMOUNT':active('1,000')},'NUMERIC')
        check('numeric-nan',{'S01_006_AMOUNT':active('NaN')},'NUMERIC')
        check('negative-budget',{'S01_006_AMOUNT':active('-1')},'NEGATIVE_AMOUNT')
        check('rate-too-high',{'S04_001_RATE':active('104')},'RATE_RANGE')
        check('fractional-tier',{'S10_001_NUMBER':active('1.5')},'INTEGER')
        check('tier-over-ten',{'S10_001_NUMBER':active('11')},'TIER_RANGE')
        check('multiline-value',{'S00_001_PROJECT_TITLE':active('Test\nProject')},'FIELD_TEXT')
        check('bracket-value',{'S00_001_PROJECT_TITLE':active('[Test]')},'FIELD_TEXT')
        check('na-without-reason',{'S01_006_AMOUNT':{'D':'Not applicable','E':'Not applicable'}},'NA_REASON')
        check('numeric-na',{'S01_006_AMOUNT':{'D':'Not applicable','E':'Not applicable','H':'Synthetic unused field'}})
        check('bad-pool-total',{'S15_001_RATE':active('40'),'S15_002_RATE':active('50')},'POOL_TOTAL')
        check('good-pool-total',{'S15_001_RATE':active('40'),'S15_002_RATE':active('60')})
        check('bad-allocation-total',{f:active('20') for f in ['S15_004_RATE','S15_006_RATE','S15_008_RATE','S15_010_RATE']},'ALLOCATION_TOTAL')
        check('budget-mismatch',{'S01_006_AMOUNT':active('100'),'S08_038_BUDGET':active('101')},'BUDGET_MISMATCH')
        check('bad-funding-difference',{'S08_037_TOTAL':active('120'),'S08_038_BUDGET':active('100'),'S08_039_AMOUNT':active('10')},'FUNDING_DIFFERENCE')
        funding={f'S08_{i:03d}_AMOUNT':active('10') for i in (2,6,10,14,18,22,26,30,34)}
        check('bad-funding-total',dict(funding, S08_037_TOTAL=active('100')),'FUNDING_TOTAL')
        check('rounded-funding-total',dict(funding, S08_037_TOTAL=active('90.01')))
        check('proposals-require-draft',{'S04_001_RATE':active('4','Proposed')},'DRAFT_LABEL',include=True)
        values={'S00_001_PROJECT_TITLE':active('SYNTHETIC REGRESSION PROJECT'),'S00_003_VERSION':active('DRAFT TEST'),'S04_001_RATE':active('4','Proposed'),'S01_006_AMOUNT':active('1000.12')}
        path=check('synthetic-population',values)
        result=run(path,root/'synthetic.docx')
        assert result['population']['populated']==3
        assert digest(root/'synthetic.docx')==digest(ASSETS/'TKE_SB_Static_Master_v1.docx')
        passed.append('confirmed-only-and-fixed-package')
        result=run(path,root/'synthetic-proposed.docx',True)
        assert result['population']['populated']==4
        passed.append('proposed-draft-and-fixed-package')
        with ZipFile(root/'synthetic.docx') as z:
            x=etree.fromstring(z.read('word/document.xml'))
            text=''.join(x.itertext())
            assert '1,000.12' in text
        passed.append('amount-display')
        try:run(path,root/'synthetic.docx')
        except ValueError:passed.append('refuse-existing-output')
        else:raise AssertionError('Overwrote output')
        try:run(path,ASSETS/'TKE_SB_Static_Master_v1.docx')
        except ValueError:passed.append('refuse-master-overwrite')
        else:raise AssertionError('Overwrote master')
        with ZipFile(root/'synthetic.docx') as z:
            contents={name:z.read(name) for name in z.namelist()}
        x=etree.fromstring(contents['word/document.xml'])
        fixed=x.find('.//{'+W+'}t');fixed.text=(fixed.text or '')+' UNAUTHORISED CHANGE'
        contents['word/document.xml']=etree.tostring(x)
        tampered=root/'tampered.docx'
        with ZipFile(tampered,'w') as z:
            for name,data in contents.items():z.writestr(name,data)
        assert digest(tampered)!=digest(ASSETS/'TKE_SB_Static_Master_v1.docx')
        passed.append('detect-fixed-clause-tamper')
    print(json.dumps({'passed':len(passed),'checks':passed},indent=2))
