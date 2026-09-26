#!/usr/bin/env python3
"""UI QC loop (agentic): screenshots every sheet of the app at phone and desktop size (via the ?open= test hook),
then asks an agent to review usability and intuitiveness for a non-mechanic owner on a phone. Findings land in
reports/uiqc.json; loop_cross surfaces the high ones as warnings. Cached on the UI source, so it re-runs only when
the markup/CSS/interaction code changes."""
import os, re, sys
from common import *
from agent import ask, h
FRESH='--fresh' in sys.argv
src=ui_source()
shots={'home':'t=0','exploded':'t=0.6','panel':'open=panel:alternator','panel-flagged':'open=panel:water-pump','list':'open=list','systems':'open=systems','system-cooling':'open=systems:Cooling','vehicle':'open=veh','data':'open=data','help':'open=help'}
os.makedirs(os.path.join(ROOT,'renders'),exist_ok=True); paths=[]
with Server(8798):
    for n,q in shots.items():
        for tag,(w,hh) in (('phone',(390,844)),('desk',(1600,1000))):
            out=os.path.join(ROOT,'renders',f'ui-{n}-{tag}.png'); render(out,q,w,hh); paths.append(out)
PROMPT=f"""Usability / intuitiveness review of a single-file web app: an exploded-view 3D parts explorer for ONE car (2003 Ford Focus wagon),
used mostly on a PHONE by the owner, who is NOT a mechanic. He wants to: find a part on the 3D car, learn what it is and does,
see the part number and whether it is trustworthy, watch a how-to video, and find where to buy it locally. There is a Systems sheet
that explains each car system, its parts, how systems interact, with plain-English refreshers; and a Help sheet.
Screenshots (phone 390x844 and desktop 1600x1000) - look at ALL of them with the Read tool:
{chr(10).join(paths)}
UI source (markup, CSS, interaction code):
```html
{src[:60000]}
```
Judge: first-run comprehension, discoverability (explode/tap/search/filter/systems), button labels for a layperson, part-panel reading order
(what it is -> what it does -> is it broken -> number + trust -> how to fix -> where to buy), touch targets, sheets covering the 3D view, contrast,
jargon without gloss, cut-off or overflowing controls on the phone, empty/error states, and whether editing tools are tucked away enough.
Return ONLY JSON: {{"score":1-10,"findings":[{{"rank":1,"severity":"high"|"med"|"low","area":"first-run|nav|panel|labels|touch|jargon|systems|editor|visual","problem":"...","fix":"concrete CSS/markup/copy change"}}],"keep":["..."]}}
10-20 findings, most impactful first, each fix concrete enough to implement directly. Only report what you can actually see or read in the source."""
out=ask(PROMPT,model='opus',tools='Read',cache_key=h('uiqc-v1',src),fresh=FRESH,label='ui qc',timeout=1800,max_turns=60)
F=out.get('findings') or []
write('uiqc',{'summary':{'score':out.get('score'),'findings':len(F),'high':sum(f.get('severity')=='high' for f in F)},'findings':F,'keep':out.get('keep') or []})
print('score',out.get('score')); [print(' ',f.get('severity'),f.get('area'),f.get('problem')) for f in F[:12]]
