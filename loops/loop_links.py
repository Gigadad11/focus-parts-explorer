#!/usr/bin/env python3
"""Link loop: generated retailer/store/reference URLs. Hosts that bot-wall are recorded as 'unverifiable', never as pass."""
import re, time, concurrent.futures as cf
from common import *
d=load(); V=d['VEHICLE']; P=d['PARTS']
BLOCKED=('rockauto.com/en/partsearch','amazon.com','ebay.com','autozone.com','oreillyauto.com','partsgeek.com','1aauto.com','car-part.com','lkqpickyourpart.com','ford.oempartsonline.com','google.com/maps')
def pn_of(p):
    first=(p.get('oe') or [''])[0].split(' ')[0].split('/')[0]; return first if re.match(r'^[A-Z0-9-]{4,}$',first,re.I) else ''
urls={'rockauto-vehicle':V['rockautoVehicle'],'wikimedia-front':'https://commons.wikimedia.org/wiki/File:2003_Ford_Focus_SE_Station_Wagon_in_Light_Tundra_Metallic,_front_right.jpg',
      'youtube-search-sample':'https://www.youtube.com/results?search_query=2003+Ford+Focus+alternator+replacement','autozone-locator':'https://www.autozone.com/locations/id/meridian.html','oreilly-locator':'https://locations.oreillyauto.com/en-us/id/meridian/'}
for p in P:
    pn=pn_of(p)
    if pn: urls[f'rockauto-pn:{p["id"]}']='https://www.rockauto.com/en/partsearch/?partnum='+pn
def probe(kv):
    k,u=kv
    if any(b in u for b in BLOCKED): return {'key':k,'url':u,'status':'unverifiable (bot wall)','ok':None}
    code='000'
    for i in range(3):
        code=head(u)
        if code!='000': break
        time.sleep(3*(i+1))
    if code=='000': return {'key':k,'url':u,'status':'unverifiable (no response / rate-limited)','ok':None}
    return {'key':k,'url':u,'status':code,'ok':code in ('200','301','302')}
with cf.ThreadPoolExecutor(3) as ex: res=list(ex.map(probe,urls.items()))
bad=[r for r in res if r['ok'] is False]
write('links',{'summary':{'checked':len(res),'ok':sum(1 for r in res if r['ok']),'bad':len(bad),'unverifiable':sum(1 for r in res if r['ok'] is None),'blocked_hosts':BLOCKED},'bad':bad,'results':res})
print('bad:',[(r['key'],r['status']) for r in bad][:10])
