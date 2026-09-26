#!/usr/bin/env python3
"""Systems loop (deterministic): the Systems sheet content must be complete and consistent with the parts data.
Every system in SYSTEMS has a SYSTEM_INFO entry with all fields; every interaction names a real, different system and
is reciprocated; every part has a PART_NOTES entry (does/fails/diy/tip); every system has at least one part;
no orphan keys. Errors block the deploy."""
from common import *
d=load(); S=d['SYSTEMS']; P=d['PARTS']; SI=d.get('SYSTEM_INFO') or {}; PN=d.get('PART_NOTES') or {}
E=[]; W=[]
if not SI: E.append('SYSTEM_INFO missing from index.html')
if not PN: E.append('PART_NOTES missing from index.html')
ids={p['id'] for p in P}; bysys={}
for p in P: bysys.setdefault(p['sys'],[]).append(p['id'])
for s in S:
    if not bysys.get(s): E.append(f'system {s} has no parts')
    i=SI.get(s)
    if not i: E.append(f'SYSTEM_INFO missing {s}'); continue
    for k in ('does','how','interacts','watch','refresher'):
        if not i.get(k): E.append(f'SYSTEM_INFO[{s}] missing {k}')
    seen=set()
    for x in i.get('interacts') or []:
        w=x.get('with')
        if w not in S: E.append(f'SYSTEM_INFO[{s}] interacts with unknown system {w!r}')
        elif w==s: E.append(f'SYSTEM_INFO[{s}] interacts with itself')
        elif w in seen: W.append(f'SYSTEM_INFO[{s}] lists {w} twice')
        elif not any(y.get('with')==s for y in (SI.get(w) or {}).get('interacts') or []): W.append(f'{s} -> {w} interaction is not reciprocated in {w}')
        seen.add(w)
        if not x.get('how'): E.append(f'SYSTEM_INFO[{s}] -> {w}: empty how')
    if len(i.get('interacts') or [])<2: W.append(f'{s} lists fewer than 2 interactions')
for k in SI:
    if k not in S: E.append(f'SYSTEM_INFO has unknown system {k!r}')
for p in P:
    n=PN.get(p['id'])
    if not n: E.append(f'PART_NOTES missing {p["id"]}'); continue
    for k in ('does','fails','tip'):
        if not n.get(k): E.append(f'PART_NOTES[{p["id"]}] missing {k}')
        elif len(n[k])>200: W.append(f'PART_NOTES[{p["id"]}].{k} is {len(n[k])} chars (>200)')
    if n.get('diy') not in (1,2,3,4,5): E.append(f'PART_NOTES[{p["id"]}] diy must be 1-5')
for k in PN:
    if k not in ids: E.append(f'PART_NOTES has unknown part {k!r}')
write('systems',{'summary':{'systems':len(S),'parts':len(P),'errors':len(E),'warnings':len(W)},'errors':E,'warnings':W,'parts_per_system':{s:len(bysys.get(s,[])) for s in S}})
print('errors',len(E),'warnings',len(W)); [print('  ERR',e) for e in E[:15]]
import sys; sys.exit(1 if E else 0)
