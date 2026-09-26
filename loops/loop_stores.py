#!/usr/bin/env python3
"""Store loop: re-derive the store list from the chains' own location pages and compare to what the page claims."""
import re
from common import *
d=load(); src=d['STORES_SRC']
claimed=re.findall(r"chain:(?:'([^']+)'|\"([^\"]+)\"),addr:'([^']+)',tel:'([^']+)'",src); claimed=[(a or b,c,d) for a,b,c,d in claimed]
res=[]
for chain,addr,tel in claimed:
    street=addr.split(',')[0]
    if chain=='AutoZone': url='https://www.autozone.com/locations/id/meridian/'+street.lower().replace(' ','-')+'.html'
    else: url='https://locations.oreillyauto.com/en-us/id/meridian/'
    code=head(url); body=get(url) if code=='200' else ''
    digits=re.sub(r'\D','',tel); found_tel=digits in re.sub(r'\D','',body) if body else False
    found_addr=street.lower().split(' ')[1] in body.lower() if body else False
    res.append({'chain':chain,'addr':addr,'tel':tel,'url':url,'http':code,'tel_on_page':found_tel,'street_on_page':found_addr,'verdict':'confirmed' if (found_tel or found_addr) else ('unverifiable' if code not in ('200',) else 'not found on page')})
write('stores',{'summary':{'claimed':len(claimed),'confirmed':sum(r['verdict']=='confirmed' for r in res),'unverifiable':sum(r['verdict']=='unverifiable' for r in res),'not_found':sum(r['verdict']=='not found on page' for r in res)},'results':res})
for r in res: print(' ',r['chain'],r['addr'],'->',r['verdict'],r['http'])
