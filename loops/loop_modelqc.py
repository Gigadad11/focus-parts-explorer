#!/usr/bin/env python3
"""Model QC loop (agentic): renders x-ray top/side/front views and an exploded view, then asks an agent that knows
the real 2000-04 Zetec Focus layout to judge every part's position, size and explode direction. Findings land in
reports/modelqc.json; loop_cross reports them as warnings and can apply suggested moves with --apply-model.
Cached on the geometry fields, so it only re-runs when a part is moved/resized/added."""
import json, os, sys
from common import *
from agent import ask, h
FRESH='--fresh' in sys.argv
d=load(); P=d['PARTS']
geo=[{k:p.get(k) for k in ('id','name','sys','shape','size','pos','ex','body')} for p in P]
views={'qc-top':'t=0&xray=1&cam=0.01,40,0.01&target=0,1,0','qc-side':'t=0&xray=1&cam=0,3,34&target=0,2.8,0','qc-front':'t=0&xray=1&cam=34,4,0&target=0,2.5,0','qc-exploded':'t=0.6&cam=24,12,28&target=0,3,0','qc-rear-quarter':'t=0&xray=1&cam=-20,9,-22&target=0,2.4,0'}
os.makedirs(os.path.join(ROOT,'renders'),exist_ok=True)
with Server(8798):
    for n,q in views.items(): render(os.path.join(ROOT,'renders',n+'.png'),q)
paths=', '.join(os.path.join(ROOT,'renders',n+'.png') for n in views)
PROMPT=f"""QC a procedural three.js 3D parts model of a 2003 Ford Focus WAGON, 2.0 DOHC Zetec, FWD, transverse engine.
Coordinate frame: x = fore/aft with POSITIVE X = FRONT (radiator x~8.3, engine x~5, fuel tank/muffler negative x); y = height (0 = ground); z = left/right.
Work out which sign of z is the driver (LH) side from the LH/RH-named parts and check it is consistent everywhere.
Real-car facts to judge against: Zetec Focus has the INTAKE manifold toward the firewall and the EXHAUST manifold toward the radiator; battery front-left of the bay (driver side, US LHD); airbox driver side; degas bottle passenger side; alternator, PS pump, A/C compressor and the timing belt on the passenger (belt) end of the engine; transaxle on the driver end; fuel tank under the rear seat ahead of the rear axle; muffler at the rear; Control Blade rear suspension; blower and heater core behind the dash on the passenger side; PCM in the bay near the battery; CJB fuse box at the driver-side of the bay.
Look at these renders with the Read tool: {paths}
Then judge each part's pos, size and explode direction (ex) for plausibility and relative scale, and whether the rest layout overlaps absurdly.
Parts (scene units, shell ~18.3 long x 5.7 high x 6.8 wide):
{json.dumps(geo,separators=(',',':'))}
Return ONLY JSON: {{"lh_side_z":"+z"|"-z"|"inconsistent","lh_evidence":"...","findings":[{{"id":"<part id>","severity":"error"|"warn"|"nit","problem":"...","suggest":{{"pos":[x,y,z]}}|{{"size":[...]}}|{{"ex":[x,y,z]}}|null,"why":"one line of real-car knowledge"}}],"overall":"2-4 sentences"}}
error = wrong side / wrong end of car / grossly wrong size; warn = questionable; nit = cosmetic. Be numeric and specific; only list real problems."""
out=ask(PROMPT,model='opus',tools='Read',cache_key=h('mqc-v1',geo),fresh=FRESH,label='model qc',timeout=1800,max_turns=40)
F=out.get('findings') or []
for f in F: f.setdefault('severity','warn')
byid={p['id'] for p in P}; F=[f for f in F if f.get('id') in byid]
write('modelqc',{'summary':{'parts':len(P),'findings':len(F),'errors':sum(f['severity']=='error' for f in F),'warnings':sum(f['severity']=='warn' for f in F),'lh_side_z':out.get('lh_side_z'),'overall':out.get('overall','')},'lh_evidence':out.get('lh_evidence',''),'findings':F})
print(out.get('overall','')); [print(' ',f['severity'],f['id'],f['problem']) for f in F[:15]]
