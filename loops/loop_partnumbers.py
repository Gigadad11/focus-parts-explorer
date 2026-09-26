#!/usr/bin/env python3
"""Part-number loop (agentic). For every part whose claimed numbers changed since the last verdict (or all with --all,
or --ids a,b,c, or older than --stale-days N), an agent web-checks the claimed OE / aftermarket numbers against
fitment listings for THIS car and returns a verdict per part. Verdicts are merged into reports/partnumbers.json,
keyed by a hash of the claim so unchanged parts are never re-checked. Legacy agent output in /tmp/pn_group*_out.json
is absorbed once (treated as covering the current claims) if the report has no hashes yet."""
import glob, json, os, sys, time, concurrent.futures as cf
from common import *
from agent import ask, h
ARGS=sys.argv[1:]; ALL='--all' in ARGS; FRESH='--fresh' in ARGS
IDS=set(next((a.split('=')[1] for a in ARGS if a.startswith('--ids=')),'').split(',')) - {''}
STALE=int(next((a.split('=')[1] for a in ARGS if a.startswith('--stale-days=')),'0'))
TAG=' (suggested by verification, confirm on car)'
def strip(x): return x.replace(TAG,'').strip()
def claim(p): return {'name':p['name'],'oe':[strip(x) for x in (p.get('oe') or [])],'aft':[strip(x) for x in (p.get('aft') or [])]}
d=load(); P=d['PARTS']; V=d['VEHICLE']
rp=os.path.join(ROOT,'reports','partnumbers.json')
old={v['id']:v for v in (json.load(open(rp)).get('verdicts',[]) if os.path.exists(rp) else [])}
if not old:
    for f in sorted(glob.glob('/tmp/pn_group*_out.json')):
        for v in json.load(open(f)): old[v['id']]=v
byid={p['id']:p for p in P}
for pid,v in old.items():   # legacy verdicts (no hash) are taken as covering the current claim
    if 'claim_hash' not in v and pid in byid: v['claim_hash']=h(claim(byid[pid])); v.setdefault('checked_at','legacy')
now=time.time()
def stale(v):
    if not STALE or v.get('checked_at') in (None,'legacy'): return False
    try: return now-time.mktime(time.strptime(v['checked_at'],'%Y-%m-%dT%H:%M:%SZ'))>STALE*86400
    except Exception: return False
need=[p for p in P if ALL or p['id'] in IDS or p['id'] not in old or old[p['id']].get('claim_hash')!=h(claim(p)) or stale(old[p['id']])]
need=[p for p in need if claim(p)['oe'] or claim(p)['aft']]
print(f'[partnumbers] {len(P)} parts, {len(need)} need a verdict'+(f': {[p["id"] for p in need][:12]}' if need else ''))
PROMPT="""You are verifying replacement part numbers for ONE specific car:
2003 Ford Focus WAGON (body code P36), 2.0L DOHC 16-valve Zetec-E (VIN engine code 3, 130 hp), FWD, built at Wayne MI.
Transmission unknown (MTX-75 5-speed manual or 4F27E automatic). Front vented discs / rear drums unless ABS-equipped.
NOT the 2.0 SOHC SPI (CVH), NOT the 2.3 Duratec, NOT the SVT, NOT the 2005-07 facelift, NOT a Ranger/Escape/Mazda.

For EACH part below, web-check every claimed number (search RockAuto, Amazon, eBay, Ford OEM parts sites, PartsGeek, 1A Auto, focaljet/focusfanatics forums, Motorcraft catalogs). Decide per part:
- "confirmed": at least one claimed number has a listing whose fitment includes 2003 Focus 2.0L DOHC (Zetec). Put those numbers in "checked" with the URL in "evidence".
- "contradicted": a claimed number demonstrably fits a DIFFERENT vehicle/engine (put it in "wrong" as "NUMBER (what it really fits)") and you found no claimed number that fits. If you found the correct number for this car, put it in "suggested" as "NUMBER (source/fitment)".
- "plausible": listings exist for a Focus but the engine/year is not explicit.
- "unverifiable": you could not find listings either way (say so; do not guess).
A number can be both confirmed and another in the same part wrong; then verdict is "confirmed" but still fill "wrong".
Never mark confirmed from memory alone; you need a page you actually fetched or a search result snippet that names the fitment.

Return ONLY a JSON array, one object per part, exactly this shape:
[{"id":"<id>","verdict":"confirmed|plausible|contradicted|unverifiable","checked":["..."],"wrong":["..."],"suggested":["..."],"evidence":["url",...],"note":"one or two sentences"}]

Parts:
"""
def run_group(gi,grp):
    body='\n'.join(json.dumps({'id':p['id'],**claim(p),'system':p['sys']}) for p in grp)
    out=ask(PROMPT+body,model='sonnet',cache_key=h('pn-v2',[claim(p) for p in grp]),fresh=FRESH,label=f'pn group {gi} ({len(grp)} parts)',timeout=2400,max_turns=150)
    if isinstance(out,dict): out=out.get('verdicts') or out.get('results') or [out]
    return out
verdicts=dict(old)
if need:
    n=max(1,min(4,(len(need)+15)//16)); groups=[need[i::n] for i in range(n)]
    with cf.ThreadPoolExecutor(n) as ex: results=list(ex.map(lambda t: run_group(*t),enumerate(groups)))
    ts=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    for grp,res in zip(groups,results):
        got={v.get('id'):v for v in res if isinstance(v,dict)}
        for p in grp:
            v=got.get(p['id'])
            if not v or v.get('verdict') not in ('confirmed','plausible','contradicted','unverifiable'):
                v={'id':p['id'],'verdict':'unverifiable','note':'agent returned no verdict'}
            for k in ('checked','wrong','suggested','evidence'): v[k]=[str(x) for x in (v.get(k) or []) if x]
            v['note']=str(v.get('note','')); v['claim_hash']=h(claim(p)); v['checked_at']=ts; verdicts[p['id']]=v
ids={p['id'] for p in P}; vl=[verdicts[i] for i in verdicts if i in ids]; unknown=[i for i in verdicts if i not in ids]
counts={k:sum(1 for v in vl if v['verdict']==k) for k in ('confirmed','plausible','contradicted','unverifiable')}
write('partnumbers',{'summary':{'parts':len(vl),**counts,'unknown_ids':unknown,'rechecked':[p['id'] for p in need]},'verdicts':vl})
print(counts,'rechecked',len(need))
