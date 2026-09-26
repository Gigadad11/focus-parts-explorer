"""Agent helper for the verification loops: runs `claude -p` non-interactively, parses the JSON it returns,
and caches results under reports/.agent-cache by (model, cache_key). Loops pass a cache_key derived from the
data being judged so unchanged inputs never cost a second agent run; --fresh on a loop bypasses the cache."""
import hashlib, json, os, re, subprocess, time
from common import ROOT
CLAUDE=os.path.expanduser('~/.local/bin/claude')
CACHE=os.path.join(ROOT,'reports','.agent-cache')
def h(*parts): return hashlib.sha1('\n'.join(json.dumps(p,sort_keys=True) if not isinstance(p,str) else p for p in parts).encode()).hexdigest()[:16]
def extract_json(txt):
    m=re.search(r'```(?:json)?\s*(.*?)```',txt,re.S)
    if m: txt=m.group(1)
    for a,b in (('{','}'),('[',']')):
        i=txt.find(a); j=txt.rfind(b)
        if i!=-1 and j>i:
            try: return json.loads(txt[i:j+1])
            except Exception: pass
    return None
def ask(prompt,*,model='sonnet',tools='WebSearch,WebFetch,Read',timeout=1800,cache_key=None,fresh=False,max_turns=80,label=''):
    key=h(model,cache_key or prompt); os.makedirs(CACHE,exist_ok=True); cf=os.path.join(CACHE,key+'.json')
    if not fresh and os.path.exists(cf):
        c=json.load(open(cf)); print(f'[agent] {label or key}: cached ({c.get("_at")})'); return c['data']
    env=dict(os.environ); [env.pop(k,None) for k in ('CLAUDECODE','CLAUDE_CODE_ENTRYPOINT')]
    cmd=[CLAUDE,'-p','--model',model,'--output-format','json','--allowedTools',tools,'--disallowedTools','Edit,Write,NotebookEdit,Agent','--max-turns',str(max_turns)]
    last=''
    for attempt in range(2):
        t0=time.time(); print(f'[agent] {label or key}: running {model} (attempt {attempt+1})',flush=True)
        r=subprocess.run(cmd,input=prompt,capture_output=True,text=True,timeout=timeout,env=env,cwd=ROOT)
        try: out=json.loads(r.stdout); txt=out.get('result','') or ''
        except Exception: out={}; txt=r.stdout
        data=extract_json(txt); last=(txt or r.stderr)[-500:]
        if data is not None:
            json.dump({'_key':key,'_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'_model':model,'_label':label,'_secs':round(time.time()-t0),'_cost':out.get('total_cost_usd'),'_turns':out.get('num_turns'),'data':data},open(cf,'w'),indent=1)
            print(f'[agent] {label or key}: done in {round(time.time()-t0)}s, ${out.get("total_cost_usd",0) or 0:.2f}',flush=True); return data
        print(f'[agent] {label or key}: no JSON in reply (rc={r.returncode}): {last[:200]}',flush=True); time.sleep(5)
    raise RuntimeError(f'agent {label or key} returned no JSON: {last}')
