#!/usr/bin/env python3
"""Geometry loop: render the page headless, dump every part's world bounding box, and check each part sits in the zone its system implies."""
import json, re, subprocess, time, os
from common import *
ZONES={'Engine':dict(x=(3.0,9.0),y=(0.5,4.0)),'Cooling':dict(x=(5.0,9.4),y=(0.5,4.0)),'Fuel & Air':dict(x=(-6.5,9.4),y=(0.3,4.0)),'Ignition & Electrical':dict(x=(1.5,9.4),y=(0.3,4.2)),
 'Exhaust':dict(x=(-9.4,5.0),y=(0.0,3.5)),'Transmission & Drive':dict(x=(3.0,8.0),y=(0.5,4.0)),'Suspension':dict(x=(-7.0,8.0),y=(0.0,4.5)),'Brakes':dict(x=(-7.0,9.0),y=(0.0,4.0)),
 'Steering':dict(x=(1.0,9.0),y=(0.3,4.5)),'HVAC':dict(x=(1.5,9.4),y=(0.3,4.5)),'Body':dict(x=(-9.5,9.5),y=(0.0,6.5)),'Lighting':dict(x=(-9.5,9.5),y=(1.5,4.5)),'Interior':dict(x=(-5.0,4.5),y=(0.5,6.0)),'Wheels & Tires':dict(x=(-7.0,7.0),y=(-0.1,2.6))}
srv=subprocess.Popen(['python3','-m','http.server','8798','--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
try:
    r=subprocess.run([CH,'--headless=new','--no-sandbox','--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--window-size=1200,800','--virtual-time-budget=15000','--dump-dom','http://127.0.0.1:8798/?dbgparts=1'],capture_output=True,text=True,timeout=120)
finally: srv.terminate()
m=re.search(r'DBGPARTS (\[.*?\]) END',r.stdout,re.S); assert m,'no DBGPARTS readout'
boxes=json.loads(m.group(1)); byid={p['id']:p for p in load()['PARTS']}
findings=[]
for b in boxes:
    p=byid.get(b['id']); 
    if not p: continue
    cx=(b['min'][0]+b['max'][0])/2; cy=(b['min'][1]+b['max'][1])/2; z=ZONES[p['sys']]
    probs=[]
    if not(z['x'][0]<=cx<=z['x'][1]): probs.append(f'x center {cx:.1f} outside {p["sys"]} zone {z["x"]}')
    if not(z['y'][0]<=cy<=z['y'][1]): probs.append(f'y center {cy:.1f} outside {p["sys"]} zone {z["y"]}')
    zlim=4.5 if p['sys']=='Body' else 3.9
    if b['max'][2]>zlim or b['min'][2]<-zlim: probs.append(f'pokes outside body width z {b["min"][2]:.1f}..{b["max"][2]:.1f}')
    if b['max'][1]>6.6 or b['min'][1]<-0.2: probs.append(f'outside height {b["min"][1]:.1f}..{b["max"][1]:.1f}')
    if probs: findings.append({'id':b['id'],'name':p['name'],'sys':p['sys'],'bbox':b,'problems':probs})
write('geometry',{'summary':{'parts':len(boxes),'flagged':len(findings)},'findings':findings})
for f in findings[:12]: print(' ',f['id'],f['problems'])
