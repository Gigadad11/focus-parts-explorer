#!/usr/bin/env python3
"""Inject the plain-English reference layer into index.html: SYSTEM_INFO from a systems JSON and PART_NOTES from a
part-notes JSON (defaults: docs/systems.json, docs/part-notes.json). Idempotent: replaces the two const lines.
Usage: python3 loops/inject_content.py [systems.json] [part-notes.json]"""
import json, re, sys, os
from common import ROOT, html
S=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,'docs','systems.json')
N=sys.argv[2] if len(sys.argv)>2 else os.path.join(ROOT,'docs','part-notes.json')
si=json.load(open(S)); pn=json.load(open(N))
h=html()
h,c1=re.subn(r'^const SYSTEM_INFO=.*;$','const SYSTEM_INFO='+json.dumps(si,separators=(',',':'),ensure_ascii=False)+';',h,flags=re.M)
h,c2=re.subn(r'^const PART_NOTES=.*;$','const PART_NOTES='+json.dumps(pn,separators=(',',':'),ensure_ascii=False)+';',h,flags=re.M)
assert c1==1 and c2==1,(c1,c2)
open(os.path.join(ROOT,'index.html'),'w',encoding='utf8').write(h); print(f'injected {len(si)} systems, {len(pn)} part notes')
