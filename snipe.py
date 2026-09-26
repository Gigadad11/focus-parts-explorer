#!/usr/bin/env python3
"""Build the snipe sheet: every part with its OE/interchange numbers and direct search links
on RockAuto, eBay, Amazon, PartsGeek, 1A Auto, Ford OEM, Car-Part and LKQ.
Live price scraping is NOT done here: RockAuto/eBay/Amazon/AutoZone/O'Reilly all serve bot walls
or JS-only listings to a plain script (checked 2026-09-25). The links open the filtered, price-sorted
pages directly, which is the fastest honest path. Fill prices.json by hand as you find them.
Usage: python3 snipe.py   -> writes snipe-sheet.html + snipe-sheet.csv"""
import json, re, csv, subprocess, html
from urllib.parse import quote as q
def load():
    h=open('index.html',encoding='utf8').read()
    src=h.split('/* ===== DEFAULT DATA')[1].split('/* ===== STATE')[0]
    src=src[src.index('const VEHICLE'):]+'\nconsole.log(JSON.stringify({PARTS,VEHICLE,VIDEOS}))'
    return json.loads(subprocess.run(['node','-e',src],capture_output=True,text=True,check=True).stdout)
def nm_of(p): return re.sub(r'\(.*?\)','',p['name']).strip()
def links(p,V):
    nm=re.sub(r'\(.*?\)','',p['name']).strip(); yr='2003 Ford Focus 2.0 DOHC Zetec'
    pn=(p.get('oe') or [''])[0].split(' ')[0].split('/')[0]
    pn=pn if re.match(r'^[A-Z0-9-]{4,}$',pn,re.I) else ''
    qq=(pn+' ' if pn else '')+nm+' '+yr
    L=[('RockAuto catalog',V['rockautoVehicle'])]
    if pn: L.append(('RockAuto #'+pn,'https://www.rockauto.com/en/partsearch/?partnum='+q(pn)))
    L+= [('AutoZone','https://www.autozone.com/searchresult?searchText='+q(qq)),("O'Reilly",'https://www.oreillyauto.com/search?q='+q(qq)),('eBay low→high','https://www.ebay.com/sch/i.html?_nkw='+q(qq)+'&_sacat=6030&_sop=15'),
         ('Amazon','https://www.amazon.com/s?k='+q(qq)+'&i=automotive'),
         ('PartsGeek','https://www.partsgeek.com/catalog/2003/ford/focus.html'),
         ('1A Auto','https://www.1aauto.com/2003-ford-focus-parts/v-2003-ford-focus'),
         ('Ford OEM','https://ford.oempartsonline.com/search?search_str='+q(pn or nm)),
         ('Car-Part.com','https://www.car-part.com/'),('LKQ Boise','https://www.lkqpickyourpart.com/inventory/')]
    return pn,L
def main():
    d=load(); P,V,VID=d['PARTS'],d['VEHICLE'],d.get('VIDEOS',{})
    try: prices={r['id']:r for r in json.load(open('prices.json'))}
    except Exception: prices={}
    rows=[]; H=['<!DOCTYPE html><meta charset=utf-8><title>Snipe sheet — 2003 Focus Wagon Zetec</title>',
      '<style>body{font:13px system-ui;background:#0a0a0a;color:#ddd;padding:12px}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #222;padding:6px 8px;vertical-align:top;text-align:left}th{color:#c67a30;font-size:11px;letter-spacing:.1em;text-transform:uppercase}a{color:#e8a56a;text-decoration:none;margin-right:8px;white-space:nowrap}code{color:#fff;background:#1a1a1a;padding:1px 4px;border-radius:3px}small{color:#777}.V{color:#8f8}.K{color:#fd8}</style>',
      f'<h2>Snipe sheet · {V["year"]} {V["make"]} {V["model"]} {V["body"]} · {V["engine"]}</h2><p>VIN {V["vin"]} · <a href="/">← 3D explorer</a></p><p><b>Meridian counters:</b> AutoZone 1626 N Main St (208) 888-1430 · O&#39;Reilly 1915 Fairview Ave (208) 288-2114 · O&#39;Reilly 24 E Calderwood Dr (208) 888-4815 · O&#39;Reilly 3420 N Eagle Rd (208) 888-0805 · O&#39;Reilly 3377 N Ten Mile Rd (208) 888-1200 · all Mon-Sat 7:30a-10p, Sun 8a-8p</p>',
      '<table><tr><th>System</th><th>Part</th><th>OE / interchange</th><th>Best price found</th><th>How-to video</th><th>Snipe</th></tr>']
    for p in P:
        pn,L=links(p,V); pr=prices.get(p['id'],{})
        oe='<br>'.join(f'<code>{html.escape(x)}</code>' for x in (p.get('oe') or []))
        aft='<br>'.join(f'<small>{html.escape(x)}</small>' for x in (p.get('aft') or []))
        best=html.escape(str(pr.get('best',''))) if pr else ''
        vids=' '.join(f'<a href="{v["url"]}" target=_blank>▶ {html.escape(v["title"][:40])}</a>' for v in VID.get(p['id'],[]))+f' <a href="https://www.youtube.com/results?search_query={q("2003 Ford Focus "+nm_of(p)+" replacement")}" target=_blank>search</a>'
        H.append(f'<tr><td>{p["sys"]}</td><td>{html.escape(p["name"])}<br><small class="{p.get("conf","L")}">{ {"V":"verified","K":"catalog #","L":"lookup"}[p.get("conf","L")] }</small>'+(f'<br><small>{html.escape(p["notes"])}</small>' if p.get('notes') else '')+f'</td><td>{oe}{"<br>" if oe and aft else ""}{aft}</td><td>{best}</td><td>{vids}</td><td>'+' '.join(f'<a href="{u}" target=_blank>{a}</a>' for a,u in L)+'</td></tr>')
        rows.append([p['sys'],p['name'],pn,' | '.join(p.get('oe') or []),' | '.join(p.get('aft') or []),p.get('notes',''),' | '.join(v['url'] for v in VID.get(p['id'],[])),*[u for _,u in L[:4]]])
    H.append('</table>'); open('snipe-sheet.html','w').write('\n'.join(H))
    with open('snipe-sheet.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['system','part','primary_pn','oe_numbers','aftermarket','notes','videos','rockauto','rockauto_pn','ebay','amazon']); w.writerows(rows)
    print(f'wrote snipe-sheet.html and snipe-sheet.csv for {len(P)} parts')
if __name__=='__main__': main()
