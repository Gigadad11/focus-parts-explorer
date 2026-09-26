#!/usr/bin/env python3
"""Part-number loop (merge step). The web-evidence pass is agent-run in four groups (/tmp/pn_group{0..3}_out.json);
this merges them into reports/partnumbers.json with a summary. Re-run the agents to refresh; this only merges."""
import glob, json
from common import *
verdicts=[]
for f in sorted(glob.glob('/tmp/pn_group*_out.json')):
    for v in json.load(open(f)):
        v.setdefault('checked',[]); v.setdefault('wrong',[]); v.setdefault('suggested',[]); v.setdefault('evidence',[]); v.setdefault('note','')
        verdicts.append(v)
ids={p['id'] for p in load()['PARTS']}; unknown=[v['id'] for v in verdicts if v['id'] not in ids]
counts={k:sum(1 for v in verdicts if v['verdict']==k) for k in ('confirmed','plausible','contradicted','unverifiable')}
write('partnumbers',{'summary':{'parts':len(verdicts),**counts,'unknown_ids':unknown},'verdicts':verdicts})
print(counts, 'unknown ids:',unknown)
