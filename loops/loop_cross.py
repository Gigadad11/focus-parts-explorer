#!/usr/bin/env python3
"""FINAL cross-verification loop. Reads every loop report and the page data, checks them against each other,
writes CROSS-REPORT.md + reports/cross.json, and with --apply performs only the deterministic safe fixes:
  - duplicate numbers in oe/aft            -> deduped (always idempotent)
  - confirmed part numbers                 -> conf V, note carries the evidence URL, confirmed number moved first
  - contradicted numbers                   -> conf X (flagged wrong), wrong-fit numbers removed, suggestion added ONCE
  - wrong-fit numbers on a confirmed part  -> removed, note explains
  - wrong-engine/gen videos                -> removed from VIDEOS
With --apply-model the agent model-QC suggestions (pos/size/ex) of severity error are applied too (off by default:
an agent's geometry opinion should be looked at, not trusted blindly). Errors (exit 1) block the deploy; warnings do not."""
import json, re, sys, os
from common import *
APPLY='--apply' in sys.argv; APPLY_MODEL='--apply-model' in sys.argv
TAG=' (suggested by verification, confirm on car)'
def strip(x): return x.replace(TAG,'').strip()
R={}
for n in ('partnumbers','videos','links','geometry','sheet','stores','systems','modelqc','uiqc'):
    p=os.path.join(ROOT,'reports',n+'.json'); R[n]=json.load(open(p)) if os.path.exists(p) else None
d=load(); P=d['PARTS']; byid={p['id']:p for p in P}; V=d['VIDEOS']
errors=[]; warns=[]; fixes=[]; agentnotes=[]
def err(m): errors.append(m)
def warn(m): warns.append(m)
REQUIRED=('partnumbers','videos','links','geometry','sheet','stores','systems')
for n in REQUIRED:
    if R[n] is None: err(f'report missing: {n}')
for n in ('modelqc','uiqc'):
    if R[n] is None: warn(f'agent report missing: {n} (run loops/loop_{n}.py)')
# 0. dedupe is always a safe fix
for p in P:
    for k in ('oe','aft'):
        a=p.get(k) or []
        if len(a)!=len(dict.fromkeys(a)) or any(strip(x)==strip(y) and x!=y for x in a for y in a): fixes.append(('dedupe',p['id'],k)); break
# 1. counts must agree across loops
if R['geometry'] and R['geometry']['summary']['parts']!=len(P): err(f"geometry saw {R['geometry']['summary']['parts']} parts, page has {len(P)}")
if R['sheet'] and R['sheet']['summary']['rows']!=len(P): err(f"sheet has {R['sheet']['summary']['rows']} rows, page has {len(P)}")
if R['videos'] and R['videos']['summary']['videos']!=sum(len(v) for v in V.values()): err('video loop count differs from page VIDEOS')
# 2. part numbers vs page confidence
pn={v['id']:v for v in (R['partnumbers'] or {}).get('verdicts',[])}
for p in P:
    v=pn.get(p['id'])
    if not v:
        if p.get('oe') or p.get('aft'): warn(f"{p['id']}: no part-number verdict")
        continue
    wrong=[w.split(' (')[0].strip() for w in (v.get('wrong') or [])]
    def bad(x): return any(w and (w in strip(x) or strip(x) in w) for w in wrong)
    if v['verdict']=='contradicted':
        if p['conf']=='V': err(f"{p['id']}: page says verified but numbers contradicted: {v['note']}")
        elif p['conf']!='X': warn(f"{p['id']}: numbers contradicted ({', '.join(v.get('wrong') or [])}) -> flag X")
        fixes.append(('flag',p['id'],v))
    elif v['verdict']=='confirmed':
        if p['conf']!='V': fixes.append(('confirm',p['id'],v))
        if any(bad(x) for x in (p.get('oe') or [])+(p.get('aft') or [])): warn(f"{p['id']}: confirmed, but wrong-fit numbers still listed ({', '.join(v['wrong'])}) -> remove"); fixes.append(('unwrong',p['id'],v))
    elif v['verdict']=='unverifiable' and p['conf']=='V': warn(f"{p['id']}: page says verified but loop could not verify")
# 3. videos vs parts
if R['videos']:
    S=R['videos']['summary']
    for x in S['dead']: err(f"dead video {x['id']} {x['url']}")
    for x in S.get('wrong',[]): warn(f"wrong engine/generation video {x['id']}: {x['title']}"); fixes.append(('dropvideo',x['id'],x['url']))
    for x in S['weak']:
        if x not in S.get('wrong',[]): warn(f"weak title match {x['id']}: {x['title']}")
    for x in S.get('sibling',[]): warn(f"2005-07 facelift video (same platform, check the part differs) {x['id']}: {x['title']}")
    for pid in S['parts_without_video']:
        if pid in byid and byid[pid]['sys']!='Body': warn(f"{pid}: no how-to video")
# 4. links / geometry / sheet / stores / systems
if R['links']:
    for b in R['links']['bad']: err(f"broken link {b['key']} -> {b['status']}")
    for r in R['links']['results']:
        if r['ok'] is None and 'no response' in r['status']: warn(f"link not reachable right now (rate-limited?) {r['key']}")
if R['geometry']:
    for f in R['geometry']['findings']: err(f"geometry {f['id']}: {'; '.join(f['problems'])}")
if R['sheet']:
    for f in R['sheet']['findings']: err(f"sheet: {f}")
if R['stores']:
    for s in R['stores']['results']:
        if s['verdict']=='not found on page': err(f"store {s['chain']} {s['addr']}: not on chain page")
        elif s['verdict']!='confirmed': warn(f"store {s['chain']} {s['addr']}: {s['verdict']}")
if R['systems']:
    for e in R['systems']['errors']: err(f"systems: {e}")
    for w in R['systems']['warnings']: warn(f"systems: {w}")
# 5. agent QC (model + UI): opinions, surfaced not enforced
if R['modelqc']:
    m=R['modelqc']; agentnotes.append(f"Model QC ({m['summary'].get('lh_side_z')} = LH): {m['summary'].get('overall','')}")
    for f in m['findings']:
        line=f"model {f['severity']} {f['id']}: {f['problem']}"+(f" -> suggest {json.dumps(f['suggest'])}" if f.get('suggest') else '')
        (warn if f['severity']=='error' else agentnotes.append)(line)
        if f['severity']=='error' and f.get('suggest') and f['id'] in byid: fixes.append(('model',f['id'],f['suggest']))
if R['uiqc']:
    u=R['uiqc']; agentnotes.append(f"UI QC score {u['summary'].get('score')}/10, {u['summary']['findings']} findings")
    for f in u['findings']:
        (warn if f.get('severity')=='high' else agentnotes.append)(f"ui {f.get('severity')} [{f.get('area')}]: {f.get('problem')} -> {f.get('fix')}")
# 6. cross: a part whose number is confirmed must have that number FIRST so snipe links use it
for kind,pid,v in fixes:
    if kind=='confirm' and v.get('checked'):
        p=byid[pid]; first=(p.get('oe') or [''])[0]
        if not any(c in first for c in v['checked']): warn(f"{pid}: confirmed number {v['checked'][0]} is not the primary OE number -> reorder")
# apply
applied=[]
if APPLY and fixes:
    h=html(); lines=h.split('\n')
    def edit(pid,fn):
        for i,l in enumerate(lines):
            m=re.match(r'^\{"id":"([^"]+)"',l)
            if m and m.group(1)==pid:
                p=json.loads(l.rstrip(',')); fn(p); lines[i]=json.dumps(p,separators=(',',':'),ensure_ascii=False)+(',' if l.endswith(',') else ''); return True
        return False
    def dedupe(p):
        for k in ('oe','aft'):
            out=[]
            for x in (p.get(k) or []):
                if not any(strip(x)==strip(y) for y in out): out.append(x)
                elif x.endswith(TAG)==False and any(y.endswith(TAG) and strip(y)==strip(x) for y in out): out=[x if strip(y)==strip(x) else y for y in out]
            p[k]=out
    def remove_wrong(p,v):
        wrong=[w.split(' (')[0].strip() for w in (v.get('wrong') or [])]
        def bad(x): return any(w and (w in strip(x) or strip(x) in w) for w in wrong)
        removed=[x for x in (p.get('oe') or []) if bad(x)]+[x for x in (p.get('aft') or []) if bad(x)]
        p['oe']=[x for x in (p.get('oe') or []) if not bad(x)]; p['aft']=[x for x in (p.get('aft') or []) if not bad(x)]
        return removed
    for kind,pid,v in fixes:
        if kind=='dedupe': edit(pid,dedupe); applied.append(f'dedupe {pid}')
        elif kind=='confirm':
            def f(p,v=v):
                p['conf']='V'; ev=(v.get('evidence') or [''])[0]
                if 'Verified by loop' not in p.get('notes',''):
                    p['notes']=(p.get('notes','')+' ' if p.get('notes') else '')+f"Verified by loop: {', '.join(v['checked'])}{' ('+ev+')' if ev else ''}."
                oe=p.get('oe') or []; conf_first=[x for x in oe if any(cc in x for cc in v['checked'])]; p['oe']=conf_first+[x for x in oe if x not in conf_first]
            edit(pid,f); applied.append(f'confirm {pid}')
        elif kind=='unwrong':
            def f(p,v=v):
                removed=remove_wrong(p,v)
                if removed and 'Removed wrong-fit' not in p.get('notes',''): p['notes']=(p.get('notes','')+' ' if p.get('notes') else '')+f"Removed wrong-fit numbers: {', '.join(removed)}."
            edit(pid,f); applied.append(f'unwrong {pid}')
        elif kind=='flag':
            def f(p,v=v):
                p['conf']='X'; removed=remove_wrong(p,v)
                have={strip(x) for x in (p.get('oe') or [])+(p.get('aft') or [])}
                for sgt in (v.get('suggested') or []):
                    if strip(sgt) not in have: p['oe'].append(sgt+TAG); have.add(strip(sgt))
                if 'Loop flagged' not in p.get('notes',''):
                    p['notes']=(p.get('notes','')+' ' if p.get('notes') else '')+f"Loop flagged: {v['note']}"+(f" Removed wrong-fit numbers: {', '.join(removed)}." if removed else '')
                dedupe(p)
            edit(pid,f); applied.append(f'flag {pid}')
        elif kind=='dropvideo':
            V[pid]=[x for x in V.get(pid,[]) if x['url']!=v]; applied.append(f'dropvideo {pid}')
        elif kind=='model' and APPLY_MODEL:
            def f(p,v=v):
                for k in ('pos','size','ex'):
                    if k in v and isinstance(v[k],list): p[k]=v[k]
            edit(pid,f); applied.append(f'model {pid} {json.dumps(v)}')
    h='\n'.join(lines)
    line=re.search(r'^const VIDEOS=.*;$',h,re.M); h=h[:line.start()]+'const VIDEOS='+json.dumps(V,separators=(',',':'))+';'+h[line.end():]
    open(os.path.join(ROOT,'index.html'),'w',encoding='utf8').write(h)
# report
pnS=(R['partnumbers'] or {}).get('summary',{}); pnS={k:v for k,v in pnS.items() if k not in ('rechecked','unknown_ids')}
def S(n,k,dflt='-'): return (R[n] or {}).get('summary',{}).get(k,dflt) if R[n] else dflt
md=['# Cross-verification report',f"{time.strftime('%Y-%m-%d %H:%M UTC',time.gmtime())}  apply={APPLY} apply-model={APPLY_MODEL}",'',
    f"Loops: partnumbers {pnS or 'missing'} | videos {S('videos','live')}/{S('videos','videos')} live | links {S('links','ok')} ok, {S('links','unverifiable')} bot-walled | geometry {S('geometry','flagged')} flagged | sheet {S('sheet','findings')} findings | stores {S('stores','confirmed')}/{S('stores','claimed')} confirmed | systems {S('systems','errors')} errors | model-qc {S('modelqc','findings')} findings | ui-qc score {S('uiqc','score')}",'',
    f'## Errors ({len(errors)})']+[f'- {e}' for e in errors]+['',f'## Warnings ({len(warns)})']+[f'- {w}' for w in warns]+['',f'## Agent QC notes ({len(agentnotes)})']+[f'- {a}' for a in agentnotes]+['',f'## Fixes {"applied" if APPLY else "proposed"} ({len(applied) if APPLY else len(fixes)})']+[f'- {a}' for a in (applied if APPLY else [f"{k} {pid}" for k,pid,_ in fixes])]
open(os.path.join(ROOT,'CROSS-REPORT.md'),'w').write('\n'.join(md)+'\n')
write('cross',{'errors':errors,'warnings':warns,'agent_notes':agentnotes,'fixes':[(k,pid) for k,pid,_ in fixes],'applied':applied})
print(f'errors {len(errors)}  warnings {len(warns)}  fixes {len(fixes)}  applied {len(applied)}')
for e in errors[:10]: print('  ERR',e)
sys.exit(1 if errors else 0)
