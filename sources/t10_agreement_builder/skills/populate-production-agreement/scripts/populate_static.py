"""Populate a fixed DOCX master from saved XLSX inputs using named controls only.
Requires Python 3 and lxml (available in GPT's document execution environment).
"""
import argparse, hashlib, json, re
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from decimal import Decimal
from lxml import etree

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS={'w':W};q=lambda t:'{'+W+'}'+t

def digest(path):
 with ZipFile(path) as z:
  h=hashlib.sha256()
  for name in sorted(z.namelist()):
   data=z.read(name)
   if name=='word/document.xml':
    x=etree.fromstring(data)
    for s in x.xpath('//w:sdt',namespaces=NS):
     c=s.find(q('sdtContent'))
     for child in list(c):
      if child.tag==q('r'):
       for t in child.iter(q('t')):t.text='FIELD_VALUE'
    data=etree.tostring(x,method='c14n')
   h.update(name.encode());h.update(data)
  return h.hexdigest()

def read_inputs(path,allowed_sheets):
 records={};issues=[]
 with ZipFile(path) as z:
  shared=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   shared=[''.join(x.itertext()) for x in etree.fromstring(z.read('xl/sharedStrings.xml')).findall('{'+S+'}si')]
  rel={x.get('Id'):x.get('Target') for x in etree.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
  for sh in etree.fromstring(z.read('xl/workbook.xml')).findall('.//{'+S+'}sheet'):
   if sh.get('name') not in allowed_sheets:continue
   target=rel[sh.get('{'+R+'}id')]
   target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
   xml=etree.fromstring(z.read(target))
   for row in xml.findall('.//{'+S+'}row'):
    cells={}
    for c in row.findall('{'+S+'}c'):
     col=re.match('[A-Z]+',c.get('r')).group();typ=c.get('t')
     v=c.find('{'+S+'}v')
     if c.find('{'+S+'}f') is not None:
      if col in ['A','D','E','F','H']:raise ValueError('Formulas not allowed in input ID, Value, Status, Source or Notes: '+c.get('r'))
     if typ=='inlineStr':value=''.join(c.find('{'+S+'}is').itertext())
     elif typ=='s':value=shared[int(v.text)] if v is not None else ''
     else:value=v.text if v is not None else ''
     cells[col]=value
    fid=cells.get('A','')
    if not re.match(r'^S\d\d_\d{3}_',fid):continue
    if fid in records:raise ValueError('Duplicate Field ID: '+fid)
    records[fid]={'value':cells.get('D',''),'status':cells.get('E',''),'source':cells.get('F',''),'notes':cells.get('H',''),'clause':cells.get('B',''),'context':cells.get('C',''),'type':cells.get('G','')}
 return records

def populate(master,inputs,map_path,output,include_proposed=False):
 master,output=Path(master),Path(output)
 if master.resolve()==output.resolve():raise ValueError('Refusing to overwrite the master')
 manifest=json.loads(Path(map_path).read_text())
 baseline=digest(master)
 if baseline!=manifest['fixed_package_sha256']:raise ValueError('Master differs from approved fixed package')
 records=read_inputs(inputs,{f['sheet'] for f in manifest['fields']})
 expected={f['id'] for f in manifest['fields']}
 if set(records)!=expected:raise ValueError('Workbook Field IDs do not exactly match the master')
 with ZipFile(master) as z:
  x=etree.fromstring(z.read('word/document.xml'))
  controls={s.find(q('sdtPr')).find(q('tag')).get(q('val')):s for s in x.xpath('//w:sdt',namespaces=NS)}
  if set(controls)!=expected:raise ValueError('Content control IDs do not match the field map')
  issues=[];inserted=0
  for f in manifest['fields']:
   fid=f['id'];item=records[fid];value=item['value'];status=item['status']
   if status not in ['Confirmed','Proposed','Unknown','Not applicable']:raise ValueError('Invalid status for '+fid)
   if not value.strip():issues.append((fid,'Missing value',item['source']));continue
   if status=='Unknown':issues.append((fid,'Unknown; value not inserted',item['source']));continue
   if status=='Proposed':
    issues.append((fid,'Proposed term; not a confirmed commitment',item['source']))
    if not include_proposed:continue
   if status in ['Confirmed','Proposed'] and not item['source'].strip():raise ValueError('Supporting source required for '+fid)
   if status=='Not applicable':
    if value!='Not applicable' or not item['notes'].strip():raise ValueError('Not applicable requires exact value and reason: '+fid)
   if '[' in value or ']' in value or '\n' in value or '\r' in value:raise ValueError('Field values must be single-line text without brackets: '+fid)
   if status!='Not applicable' and f['type'] in ['Amount','Number','Rate points']:
    try:
     number=Decimal(value)
     if not number.is_finite():raise ValueError('Non-finite number')
     value=format(number,',.2f') if f['type']=='Amount' else format(number,'f')
     if f['type']!='Amount':value=value.rstrip('0').rstrip('.') if '.' in value else value
    except Exception:raise ValueError('Numeric input required for '+fid)
   texts=controls[fid].find(q('sdtContent')).xpath('.//w:t',namespaces=NS)
   if not texts:raise ValueError('No editable text in '+fid)
   texts[0].text=value;texts[0].set('{http://www.w3.org/XML/1998/namespace}space','preserve')
   for t in texts[1:]:t.text=''
   inserted+=1
  output.parent.mkdir(parents=True,exist_ok=True)
  with ZipFile(output,'w',ZIP_DEFLATED) as dest:
   for info in z.infolist():
    data=etree.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else z.read(info.filename)
    dest.writestr(info,data)
 if digest(output)!=baseline:
  output.unlink();raise ValueError('Fixed package changed; output removed')
 report=output.with_suffix('.completion.txt')
 lines=['DRAFT COMPLETION REPORT','Master '+manifest['master_version'],f'Controls populated: {inserted} of {len(expected)}','Fixed package comparison: unchanged','Evidence, financial reconciliation, legal review and visual layout review: still required','']
 for fid,msg,source in issues:lines.append(f'{fid} | {msg} | Source: {source or "not supplied"}')
 report.write_text('\n'.join(lines))
 return {'populated':inserted,'fields':len(expected),'issues':len(issues),'fixed_content_unchanged':True}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--master',required=True);p.add_argument('--inputs',required=True);p.add_argument('--map',required=True);p.add_argument('--output',required=True);p.add_argument('--include-proposed',action='store_true');a=p.parse_args()
 print(json.dumps(populate(a.master,a.inputs,a.map,a.output,a.include_proposed)))
