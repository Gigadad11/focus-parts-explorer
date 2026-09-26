#!/usr/bin/env python3
"""Deterministic build/verify/deploy loop for the Focus Parts Explorer.
Stages (each idempotent, each fails loudly):
  lint     validate the inline data block (parts, systems, geometry bounds, videos map)
  videos   re-check every YouTube link via oEmbed; dead links are removed from index.html and logged
  sheet    regenerate snipe-sheet.html/.csv from index.html
  syntax   node --check on the page's module script
  stamp    write a build id into <meta name="build">
  render   headless Chrome screenshots (5 desktop views + phone), reject blank frames
  smoke    dump the live scene's bounding boxes and assert the car is car-shaped
  deploy   vercel --prod, then fetch the public URL and assert the build id matches (only with --deploy)
Usage: python3 loop.py [--deploy] [--skip-videos] [--skip-render]
Writes BUILD-REPORT.md. Exit code 0 only if every stage passed."""
import json, re, sys, os, subprocess, time, hashlib, concurrent.futures as cf
from datetime import datetime, timezone
ROOT=os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT)
ARGS=set(sys.argv[1:]); REPORT=[]; FAIL=False
CH=os.path.expanduser('~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome')
PUBLIC='https://focus-parts-explorer.vercel.app'
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36'
def stage(name,fn):
    global FAIL; t=time.time()
    try: msg=fn(); ok=True
    except Exception as e: msg=f'{type(e).__name__}: {e}'; ok=False; FAIL=True
    REPORT.append((name,ok,msg,round(time.time()-t,1))); print(f"[{'ok' if ok else 'FAIL'}] {name}: {msg}",flush=True)
def html(): return open('index.html',encoding='utf8').read()
def data_block(h): return h.split('/* ===== DEFAULT DATA')[1].split('/* ===== STATE')[0]
def load():
    src=data_block(html()); src=src[src.index('const VEHICLE'):]+'\nconsole.log(JSON.stringify({VEHICLE,SYSTEMS,PARTS,VIDEOS}))'
    return json.loads(subprocess.run(['node','-e',src],capture_output=True,text=True,check=True).stdout)
def sh(cmd,timeout=120,**kw): return subprocess.run(cmd,capture_output=True,text=True,timeout=timeout,**kw)

def lint():
    d=load(); P=d['PARTS']; ids=[p['id'] for p in P]
    assert len(ids)==len(set(ids)),'duplicate part ids'
    bad=[]
    for p in P:
        for k in ('id','name','sys','shape','size','pos','ex','color','conf'):
            if k not in p: bad.append(f"{p.get('id')} missing {k}")
        if p.get('sys') not in d['SYSTEMS']: bad.append(f"{p['id']} bad system {p.get('sys')}")
        x,y,z=p['pos']
        if not(-9.5<=x<=9.5 and -0.5<=y<=6.5 and -4<=z<=4): bad.append(f"{p['id']} pos out of car bounds {p['pos']}")
        if p.get('conf') not in ('V','K','L'): bad.append(f"{p['id']} conf {p.get('conf')}")
    for k in d['VIDEOS']:
        if k not in ids: bad.append(f'VIDEOS key {k} is not a part')
    assert not bad,'; '.join(bad[:8])+(' …' if len(bad)>8 else '')
    return f"{len(P)} parts, {len(d['SYSTEMS'])} systems, {sum(len(v) for v in d['VIDEOS'].values())} videos, VIN {d['VEHICLE']['vin']}"

def videos():
    if '--skip-videos' in ARGS: return 'skipped'
    d=load(); V=d['VIDEOS']; urls=[(k,i,v['url']) for k,vs in V.items() for i,v in enumerate(vs)]
    def live(u):
        m=re.search(r'v=([A-Za-z0-9_-]{11})',u)
        if not m: return False
        r=sh(['curl','-s','-o','/dev/null','-w','%{http_code}','-m','15',f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={m.group(1)}&format=json'],timeout=30)
        return r.stdout.strip()=='200'
    with cf.ThreadPoolExecutor(12) as ex: res=list(ex.map(lambda t: live(t[2]),urls))
    dead=[(k,u) for (k,i,u),ok in zip(urls,res) if not ok]
    if dead:
        for k,u in dead: V[k]=[v for v in V[k] if v['url']!=u]
        h=html(); line=re.search(r'^const VIDEOS=.*;$',h,re.M); assert line,'VIDEOS line not found'
        h=h[:line.start()]+'const VIDEOS='+json.dumps(V,separators=(',',':'))+';'+h[line.end():]; open('index.html','w',encoding='utf8').write(h)
        with open('dead-videos.log','a') as f:
            for k,u in dead: f.write(f'{datetime.now(timezone.utc).isoformat()} {k} {u}\n')
    return f'{len(urls)-len(dead)} live, {len(dead)} dead removed'

def sheet():
    r=sh(['python3','snipe.py']); assert r.returncode==0,r.stderr[-300:]
    n=open('snipe-sheet.html',encoding='utf8').read().count('<tr><td>'); assert n>=90,f'sheet rows {n}'
    return f'{n} rows'

def syntax():
    h=html(); m=re.search(r'<script type="module">(.*?)</script>',h,re.S).group(1)
    m=re.sub(r'^import .*?;$','',m,flags=re.M)
    open('/tmp/_focus_mod.mjs','w').write('const THREE=new Proxy({},{get:()=>class{}}),OrbitControls=class{},RoomEnvironment=class{};\n'+m)
    r=sh(['node','--check','/tmp/_focus_mod.mjs']); assert r.returncode==0,r.stderr[-300:]
    for tag in ('<div id="panel"','<div id="dial"','id="importFile"','const STORES=','function videoLinks','function snipeLinks'):
        assert tag in h,f'missing {tag}'
    return 'module + required UI present'

BUILD_ID=None
def stamp():
    global BUILD_ID
    h=html(); h=re.sub(r'<meta name="build" content="[^"]*"/>\n','',h)
    body=re.sub(r'<meta name="build" content="[^"]*"/>\n','',h)
    BUILD_ID=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+hashlib.sha1(body.encode()).hexdigest()[:8]
    h=h.replace('<meta name="robots"',f'<meta name="build" content="{BUILD_ID}"/>\n<meta name="robots"',1)
    open('index.html','w',encoding='utf8').write(h); return BUILD_ID

SERVER=None
def serve():
    global SERVER
    if SERVER is None:
        SERVER=subprocess.Popen(['python3','-m','http.server','8797','--bind','127.0.0.1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
def shot(out,query,w=1600,hgt=1000):
    serve(); r=sh([CH,'--headless=new','--no-sandbox','--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--hide-scrollbars',f'--window-size={w},{hgt}','--virtual-time-budget=15000',f'--screenshot={out}',f'http://127.0.0.1:8797/?{query}'],timeout=120)
    assert os.path.exists(out) and os.path.getsize(out)>40000,f'{out} blank or missing'
def render():
    if '--skip-render' in ARGS: return 'skipped'
    assert os.path.exists(CH),'headless chrome missing'
    os.makedirs('renders',exist_ok=True)
    views={'front-quarter':'t=0&cam=19,7,23&target=0,2.4,0','rear-quarter':'t=0&cam=-20,7,-22&target=0,2.4,0','side':'t=0&cam=0,3,32&target=0,2.8,0','exploded':'t=0.6&cam=24,12,28&target=0,3,0','exploded-full':'t=1&cam=28,15,32&target=0,3,0'}
    with cf.ThreadPoolExecutor(3) as ex: list(ex.map(lambda kv: shot(f'renders/{kv[0]}.png',kv[1]),views.items()))
    shot('renders/phone.png','t=0',390,844); shot('renders/phone-exploded.png','t=0.6',390,844)
    return f'{len(views)+2} frames'

def smoke():
    if '--skip-render' in ARGS: return 'skipped'
    serve(); r=sh([CH,'--headless=new','--no-sandbox','--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--window-size=1200,800','--virtual-time-budget=15000','--dump-dom','http://127.0.0.1:8797/?dbg=1&cam=0,3,34&target=0,3,0'],timeout=120)
    m=re.search(r'DBG shell (\{.*?\}) group (\{.*?\}) cam',r.stdout); assert m,'no DBG readout in DOM'
    s=json.loads(m.group(1)); g=json.loads(m.group(2))
    sx=s['max']['x']-s['min']['x']; sy=s['max']['y']-s['min']['y']; sz=s['max']['z']-s['min']['z']
    assert 17<sx<20 and 5<sy<7.5 and 6<sz<8,f'shell not car-shaped: {sx:.1f} x {sy:.1f} x {sz:.1f}'
    assert g['min']['y']>-0.5 and g['max']['y']<7 and g['min']['x']>-10.5 and g['max']['x']<10.5,f'parts out of bounds {g}'
    return f'shell {sx:.1f}L x {sy:.1f}H x {sz:.1f}W, parts within bounds'

def deploy():
    if '--deploy' not in ARGS: return 'skipped (pass --deploy)'
    env=dict(os.environ,PATH=os.path.expanduser('~/.npm-global/bin')+':'+os.environ['PATH'])
    r=sh(['vercel','deploy','--prod','--yes'],timeout=300,env=env); assert r.returncode==0,(r.stderr or r.stdout)[-400:]
    for i in range(12):
        time.sleep(5); p=sh(['curl','-s','-m','20','-A',UA,PUBLIC+'/'],timeout=30).stdout
        if f'content="{BUILD_ID}"' in p: break
    else: raise AssertionError('public page does not carry build id '+str(BUILD_ID))
    for path in ('/ref/front_right.jpg','/snipe-sheet'):
        code=sh(['curl','-s','-o','/dev/null','-w','%{http_code}','-m','20','-A',UA,PUBLIC+path],timeout=30).stdout
        assert code=='200',f'{path} -> {code}'
    return f'{PUBLIC} serving build {BUILD_ID}'

def git():
    if sh(['git','status','--porcelain']).stdout.strip()=='' : return 'clean'
    sh(['git','add','-A']); r=sh(['git','-c','user.name=Torgen','-c','user.email=tsoderlund@protonmail.com','commit','-q','-m',f'loop: build {BUILD_ID}\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>'])
    assert r.returncode==0,r.stderr[-200:]; return 'committed '+sh(['git','rev-parse','--short','HEAD']).stdout.strip()

for name,fn in [('lint',lint),('videos',videos),('sheet',sheet),('syntax',syntax),('stamp',stamp),('render',render),('smoke',smoke),('git',git),('deploy',deploy)]:
    if FAIL and name in ('git','deploy'): REPORT.append((name,False,'skipped: earlier failure',0)); continue
    stage(name,fn)
if SERVER: SERVER.terminate()
with open('BUILD-REPORT.md','w') as f:
    f.write(f'# Build report {BUILD_ID}\n\n{datetime.now(timezone.utc).isoformat()}  args: {" ".join(sorted(ARGS)) or "-"}\n\n| stage | result | detail | s |\n|---|---|---|---|\n')
    for n,ok,msg,t in REPORT: f.write(f'| {n} | {"ok" if ok else "FAIL"} | {msg} | {t} |\n')
print('\nRESULT:','FAIL' if FAIL else 'PASS',BUILD_ID); sys.exit(1 if FAIL else 0)
