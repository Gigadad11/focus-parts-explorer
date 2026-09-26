import json, re, os, subprocess, time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36'
CH=os.path.expanduser('~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome')
def html(): return open(os.path.join(ROOT,'index.html'),encoding='utf8').read()
def load():
    h=html(); src=h.split('/* ===== DEFAULT DATA')[1].split('/* ===== STATE')[0]
    src=src[src.index('const VEHICLE'):]+"\nconsole.log(JSON.stringify({VEHICLE,SYSTEMS,PARTS,VIDEOS,SYSTEM_INFO:typeof SYSTEM_INFO==='undefined'?null:SYSTEM_INFO,PART_NOTES:typeof PART_NOTES==='undefined'?null:PART_NOTES}))"
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
def ui_source():
    """The UI-facing parts of index.html (head/markup + interaction script), used to key the UI QC cache."""
    h=html(); head=h.split('<script type="importmap">')[0]
    ui=h.split('/* ===== STATE')[1] if '/* ===== STATE' in h else ''
    return head+'\n'+ui
def render(out,query,w=1600,hgt=1000,port=8798):
    """Headless screenshot of the page at ?query (caller must be serving ROOT on port)."""
    r=subprocess.run([CH,'--headless=new','--no-sandbox','--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--hide-scrollbars',f'--window-size={w},{hgt}','--virtual-time-budget=15000',f'--screenshot={out}',f'http://127.0.0.1:{port}/?{query}'],capture_output=True,text=True,timeout=120)
    assert os.path.exists(out) and os.path.getsize(out)>20000,f'{out} blank or missing'
class Server:
    def __init__(self,port=8798): self.port=port
    def __enter__(self): self.p=subprocess.Popen(['python3','-m','http.server',str(self.port),'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1); return self
    def __exit__(self,*a): self.p.terminate()
