#!/usr/bin/env python3
"""Sheet loop: the flat snipe sheet must agree with the page (every part present, same first OE number, same video count, store line present)."""
import re, html as H
from common import *
subprocess.run(['python3','snipe.py'],cwd=ROOT,check=True,capture_output=True)
d=load(); sheet=open(os.path.join(ROOT,'snipe-sheet.html'),encoding='utf8').read()
rows=re.findall(r'<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>',sheet,re.S)
findings=[]; seen=set()
for sysn,name,oe,best,vids,links in rows:
    nm=H.unescape(re.sub(r'<.*?>',' ',name)).split('\n')[0].strip(); nm=re.sub(r'\s+(verified|catalog #|lookup|FLAGGED WRONG).*$','',nm).strip()
    p=next((p for p in d['PARTS'] if p['name']==nm),None)
    if not p: findings.append({'row':nm,'problem':'row has no matching part'}); continue
    seen.add(p['id'])
    first=(p.get('oe') or [''])[0]
    if first and H.escape(first) not in oe: findings.append({'id':p['id'],'problem':f'first OE number mismatch: page {first!r}'})
    nv=vids.count('youtube.com/watch'); want=len(d['VIDEOS'].get(p['id'],[]))
    if nv!=want: findings.append({'id':p['id'],'problem':f'video count sheet {nv} vs page {want}'})
    for host in ('rockauto.com','autozone.com','oreillyauto.com','ebay.com','amazon.com'):
        if host not in links: findings.append({'id':p['id'],'problem':f'missing {host} link'})
missing=[p['id'] for p in d['PARTS'] if p['id'] not in seen]
if missing: findings.append({'problem':'parts missing from sheet','ids':missing})
if '888-1430' not in sheet: findings.append({'problem':'store line missing'})
write('sheet',{'summary':{'rows':len(rows),'parts':len(d['PARTS']),'findings':len(findings)},'findings':findings})
print('findings',len(findings))
