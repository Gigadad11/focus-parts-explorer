import json, re, os, subprocess, time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36'
CH=os.path.expanduser('~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome')
def html(): return open(os.path.join(ROOT,'index.html'),encoding='utf8').read()
def load():
    h=html(); src=h.split('/* ===== DEFAULT DATA')[1].split('/* ===== STATE')[0]
    src=src[src.index('const VEHICLE'):]+'\nconsole.log(JSON.stringify({VEHICLE,SYSTEMS,PARTS,VIDEOS}))'
    d=json.loads(subprocess.run(['node','-e',src],capture_output=True,text=True,check=True).stdout)
    st=re.search(r'const STORES=\[(.*?)\n\];',h,re.S); d['STORES_SRC']=st.group(1) if st else ''
    return d
def head(url,timeout=20):
    r=subprocess.run(['curl','-s','-o','/dev/null','-w','%{http_code}','-m',str(timeout),'-A',UA,'-L',url],capture_output=True,text=True); return r.stdout.strip()
def get(url,timeout=25):
    r=subprocess.run(['curl','-s','-m',str(timeout),'-A',UA,'-L',url],capture_output=True,text=True); return r.stdout
def write(name,obj):
    os.makedirs(os.path.join(ROOT,'reports'),exist_ok=True)
    obj['_loop']=name; obj['_at']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    json.dump(obj,open(os.path.join(ROOT,'reports',name+'.json'),'w'),indent=1); print(f'[{name}] wrote reports/{name}.json')
def parse_num(s):
    s=s.split(' (')[0].strip(); return s
