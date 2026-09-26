#!/usr/bin/env python3
"""Video loop: every YouTube link live (oEmbed) AND relevant (title mentions Focus and a keyword of the part)."""
import re, concurrent.futures as cf, json
from common import *
d=load(); V=d['VIDEOS']; byid={p['id']:p for p in d['PARTS']}
STOP={'and','the','with','for','kit','set','pair','assembly','front','rear','lh','rh','left','right','new','oem','type','in','of','a','to','on','driver','passenger','side'}
SYN={'headlamp':['headlight'],'mirrors':['mirror'],'pcm':['ecm','pcm','computer'],'trans':['transmission','transaxle'],'transaxle':['transmission'],'shocks':['shock'],'lamp':['light'],'taillamp':['tail','taillight'],'wheel':['tire','tyre','wheel'],'tire':['tyre'],'bench':['seat'],'liftgate':['hatch','tailgate','liftgate'],'bulb':['bulb','headlight'],'muffler':['muffler','exhaust'],'pipe':['exhaust','pipe'],'resonator':['exhaust'],'hub':['bearing'],'cv':['axle','cv'],'blade':['trailing','control arm','rear arm'],'serp':['serpentine','belt'],'spark':['spark','plug'],'mounts':['mount'],'lugs':['lug'],'ckp':['crank','crankshaft'],'maf':['mass air','maf'],'o2':['o2','oxygen'],'abs':['abs'],'ps':['power steering'],'ac':['a/c','ac ','air conditioning','compressor'],'rack':['rack','steering'],'regulators':['regulator','window'],'latches':['latch','lock'],'key':['key','pats','transponder'],'fluid':['fluid','oil change','transmission'],'pcv':['pcv'],'degas':['coolant','reservoir','overflow'],'cabin':['cabin','filter'],'heater':['heater core'],'blower':['blower'],'thermostat':['thermostat'],'hoses':['hose'],'injectors':['injector'],'plugs':['plug'],'switch':['switch','ignition'],'rotors':['rotor'],'drums':['drum'],'shoes':['shoe'],'pads':['pad'],'calipers':['caliper'],'cylinder':['cylinder'],'strut':['strut'],'shifter':['shifter','shift cable'],'cover':['cover','gasket'],'pan':['pan','gasket'],'timing':['timing'],'block':['engine'],'radiator':['radiator'],'condenser':['condenser'],'fan':['fan'],'starter':['starter'],'alternator':['alternator'],'battery':['battery'],'airbox':['air filter','air box','intake'],'intake':['intake','manifold'],'throttle':['throttle'],'exh':['exhaust','manifold','catalytic'],'manifold':['manifold'],'flex':['flex'],'tank':['tank'],'pump':['pump'],'filter':['filter'],'sensors':['sensor'],'sensor':['sensor'],'module':['module'],'fuse':['fuse'],'box':['box'],'windshield':['windshield','windscreen'],'roof':['roof'],'hood':['hood','bonnet'],'bumper':['bumper'],'fender':['fender','wing'],'door':['door'],'wipers':['wiper'],'seat':['seat'],'dash':['dash','cluster','instrument'],'sway':['sway','stabilizer'],'links':['link'],'bearing':['bearing'],'axle':['axle'],'clutch':['clutch'],'water':['water pump'],'oil':['oil'],'coolant':['coolant'],'fuel':['fuel'],'brake':['brake'],'wheel':['wheel','tire','tyre']}
def kw(name):
    ws=[w for w in re.findall(r'[a-z0-9/]+',re.sub(r'\(.*?\)','',name).lower()) if len(w)>1 and w not in STOP]
    out=set()
    for w in ws:
        out.add(w[:5] if len(w)>5 else w)
        for s in SYN.get(w,[]): out.add(s)
    return sorted(out)
WRONG=re.compile(r'\b(ranger|mazda|escape|fiesta|mondeo|fusion|f-?150|explorer|spi|cvh|duratec|mk ?2|mk ?3|2008|2009|201\d|202\d)\b')
def check(k,v):
    m=re.search(r'v=([A-Za-z0-9_-]{11})',v['url']); vid=m.group(1) if m else None
    body=get(f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json') if vid else ''
    try: j=json.loads(body); title=j.get('title',''); author=j.get('author_name','')
    except Exception: return {'id':k,'url':v['url'],'live':False,'title':'','relevant':False,'focus':False}
    t=title.lower(); words=kw(byid[k]['name']); hit=[w for w in words if w in t]
    years=[int(y) for y in re.findall(r'\b(19\d\d|20\d\d)\b',t)]
    for a,b in re.findall(r'\b(\d\d)[-–](\d\d)\b',t): years+= [2000+int(a) if int(a)<50 else 1900+int(a), 2000+int(b) if int(b)<50 else 1900+int(b)]
    gen1=any(1998<=y<=2004 for y in years) or bool(re.search(r'\b(1st gen|first gen|zetec|zx3|zx5|ztw|mk ?1)\b',t))
    sibling=(not gen1) and bool(years) and all(2005<=y<=2007 for y in years)
    wrong=(bool(WRONG.search(t)) and not gen1) or (bool(years) and all(y>=2008 for y in years))
    return {'id':k,'url':v['url'],'live':True,'title':title,'author':author,'focus':('focus' in t) or ('ford' in t),'relevant':len(hit)>0,'hits':hit,'kw':words,'gen1':gen1,'sibling_2005_07':sibling,'wrong_engine_or_gen':wrong}
items=[(k,v) for k,vs in V.items() for v in vs]
with cf.ThreadPoolExecutor(10) as ex: res=list(ex.map(lambda t: check(*t),items))
per={}
for r in res: per.setdefault(r['id'],[]).append(r)
summary={'videos':len(res),'live':sum(r['live'] for r in res),'relevant':sum(r['relevant'] for r in res),'focus':sum(r['focus'] for r in res),
 'weak':[{'id':r['id'],'url':r['url'],'title':r['title']} for r in res if r['live'] and not r['relevant']],
 'dead':[{'id':r['id'],'url':r['url']} for r in res if not r['live']],
 'wrong':[{'id':r['id'],'url':r['url'],'title':r['title']} for r in res if r.get('wrong_engine_or_gen')],
 'sibling':[{'id':r['id'],'url':r['url'],'title':r['title']} for r in res if r.get('sibling_2005_07')],
 'parts_without_video':[p['id'] for p in d['PARTS'] if not V.get(p['id'])]}
write('videos',{'summary':summary,'per_part':per})
print(json.dumps({k:v for k,v in summary.items() if k not in ('weak',)},indent=0)[:400]); print('weak titles:',len(summary['weak']))
