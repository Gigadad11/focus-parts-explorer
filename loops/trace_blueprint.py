#!/usr/bin/env python3
"""Blueprint tracer: side-view line drawing -> body profile in scene units (1 unit = 0.25 m).
Extracts: silhouette (top outline + rocker), wheel centers/radii, wheel-arch radii, window openings, door panels.
Repeatable for any car: python3 loops/trace_blueprint.py <image> --length-in 178 --wheelbase-in 103 [--out profile.json]
PIL only (no numpy). Writes JSON and prints sanity checks (measured wheelbase vs spec)."""
import sys, json, math, argparse
from PIL import Image
ap=argparse.ArgumentParser(); ap.add_argument('image'); ap.add_argument('--length-in',type=float,required=True); ap.add_argument('--wheelbase-in',type=float,default=None)
ap.add_argument('--height-in',type=float,default=None); ap.add_argument('--out',default='assets/blueprints/profile.json'); ap.add_argument('--front',default='right',choices=['left','right'])
a=ap.parse_args()
im=Image.open(a.image).convert('L'); W,H=im.size; px=im.load()
dark=lambda x,y: 0<=x<W and 0<=y<H and px[x,y]<140
cols=[x for x in range(W) if any(dark(x,y) for y in range(H))]; x0,x1=cols[0],cols[-1]
rows=[y for y in range(H) if any(dark(x,y) for x in range(W))]; y0,y1=rows[0],rows[-1]
L=x1-x0+1; unit=(a.length_in*0.0254/0.25)/L          # scene units per pixel
top={x:next(y for y in range(H) if dark(x,y)) for x in cols}
bot={x:next(y for y in range(H-1,-1,-1) if dark(x,y)) for x in cols}
ground=max(bot.values())
# wheels: columns touching the ground are tire bottoms; expand outward while the bottom outline rises (circle), stop at the jump to the rocker
spans=[]; cur=None
for x in cols:
    if bot[x]>=ground-2: cur=[x,x] if cur is None else [cur[0],x]
    else:
        if cur: spans.append(cur)
        cur=None
if cur: spans.append(cur)
def expand(c):
    l=r=c
    while l-1>=x0 and bot.get(l-1,0)<=bot[l]+1 and bot.get(l-1,0)>ground-0.5*bodyH0: l-=1
    while r+1<=x1 and bot.get(r+1,0)<=bot[r]+1 and bot.get(r+1,0)>ground-0.5*bodyH0: r+=1
    return l,r
bodyH0=ground-y0
merged=[]
for sp in spans:
    c=(sp[0]+sp[1])//2; l,r=expand(c)
    if r-l>L*0.06 and not any(abs((l+r)/2-m[0])<L*0.05 for m in merged): merged.append(((l+r)/2,(r-l)/2))
spans=[[cx-r,cx+r] for cx,r in merged]
wheels=[]
for s in spans:
    cx=(s[0]+s[1])/2; r=(s[1]-s[0])/2; cy=ground-r
    # arch: first dark pixel above the tire top at the wheel center column
    ya=int(cy-r*0.9)                                # start inside the tire ring
    while ya>0 and not dark(int(cx),ya): ya-=1      # up to the tire's top line
    while ya>0 and dark(int(cx),ya): ya-=1          # through it
    while ya>0 and not dark(int(cx),ya): ya-=1      # next line above = fender arch
    wheels.append({'cx':cx,'cy':cy,'r':r,'arch_r':cy-ya})
wheels.sort(key=lambda w:w['cx'])
# flood fill background from the corners to find enclosed white regions (windows, doors)
seen=bytearray(W*H); stack=[(0,0),(W-1,0),(0,H-1),(W-1,H-1)]
while stack:
    x,y=stack.pop()
    if x<0 or y<0 or x>=W or y>=H or seen[y*W+x] or dark(x,y): continue
    seen[y*W+x]=1; stack.extend(((x+1,y),(x-1,y),(x,y+1),(x,y-1)))
blobs=[]
for y in range(H):
    for x in range(W):
        if seen[y*W+x] or dark(x,y): continue
        st=[(x,y)]; pts=[]
        while st:
            u,v=st.pop()
            if u<0 or v<0 or u>=W or v>=H or seen[v*W+u] or dark(u,v): continue
            seen[v*W+u]=1; pts.append((u,v)); st.extend(((u+1,v),(u-1,v),(u,v+1),(u,v-1)))
        if len(pts)>L*L*0.0015: blobs.append(pts)
bodyH=ground-y0
def poly(pts):
    ys={}; 
    for u,v in pts: ys.setdefault(v,[u,u]); ys[v][0]=min(ys[v][0],u); ys[v][1]=max(ys[v][1],u)
    left=[(ys[v][0],v) for v in sorted(ys)]; right=[(ys[v][1],v) for v in sorted(ys,reverse=True)]
    return rdp(left+right,1.5)
def rdp(p,eps):
    if len(p)<3: return p
    a,b=p[0],p[-1]; dm,im_=0,0
    for i in range(1,len(p)-1):
        d=abs((b[0]-a[0])*(a[1]-p[i][1])-(a[0]-p[i][0])*(b[1]-a[1]))/max(1e-9,math.hypot(b[0]-a[0],b[1]-a[1])); 
        if d>dm: dm,im_=d,i
    if dm>eps: return rdp(p[:im_+1],eps)[:-1]+rdp(p[im_:],eps)
    return [a,b]
cands=[]
for b in blobs:
    xs=[u for u,_ in b]; ys=[v for _,v in b]; bx0,bx1,by0,by1=min(xs),max(xs),min(ys),max(ys)
    relBot=(ground-by1)/bodyH; wfrac=(bx1-bx0)/L
    if relBot>0.55 and 0.05<wfrac<0.4 and (bx1-bx0)>(by1-by0)*0.6: cands.append(((bx0,by0,bx1,by1),b))
cands.sort(key=lambda c:-(c[0][2]-c[0][0])*(c[0][3]-c[0][1]))
windows=[]; kept=[]
for bb,b in cands:
    if any(bb[0]>=k[0]-2 and bb[1]>=k[1]-2 and bb[2]<=k[2]+2 and bb[3]<=k[3]+2 for k in kept): continue   # nested inside a kept window
    kept.append(bb); windows.append(poly(b))
belt=max(bb[3] for bb in kept) if kept else int(ground-0.6*bodyH)     # belt line = lowest window bottom
# 3) doors from vertical seam lines between belt and rocker (robust to gaps in the sill line)
rock_y=int(sorted(bot[x] for x in cols if not any(abs(x-(sp[0]+sp[1])/2)<(sp[1]-sp[0])/2+4 for sp in spans))[len(cols)//4]) if spans else ground
seams=[]
for x in cols:
    n=sum(1 for y in range(belt+4,rock_y-4) if any(dark(x+k,y) for k in (-2,-1,0,1,2)))
    if n>(rock_y-belt-8)*0.7: seams.append(x)
groups=[]
for x in seams:
    if groups and x-groups[-1][-1]<=3: groups[-1].append(x)
    else: groups.append([x])
seamx=[sum(g)/len(g) for g in groups]
doors=[]
for i in range(len(seamx)-1):
    w=seamx[i+1]-seamx[i]
    if 0.14*L<w<0.32*L: doors.append([(seamx[i],belt+2),(seamx[i+1],belt+2),(seamx[i+1],rock_y-2),(seamx[i],rock_y-2)])
# fallbacks: arch radius that snapped to the tire line; rear door from the rear-door window when its seam is not drawn
ratio=max((w['arch_r']/w['r'] for w in wheels if w['arch_r']>w['r']*1.08),default=1.18)
for w in wheels:
    if w['arch_r']<w['r']*1.08: w['arch_r']=w['r']*ratio; w['arch_note']='arch radius inferred (ratio %.2f)'%ratio
if len(doors)==1 and seamx:
    fd=doors[0]; b_seam=min(fd[0][0],fd[1][0])
    behind=[k for k in kept if k[2]<=b_seam+6 and k[2]>b_seam-L*0.02-6 and (k[2]-k[0])>L*0.12]
    if behind:
        rear_edge=min(k[0] for k in behind)
        doors.insert(0,[(rear_edge-2,belt+2),(b_seam,belt+2),(b_seam,rock_y-2),(rear_edge-2,rock_y-2)])
# de-duplicate near-identical window polygons (frame ring vs glass traced twice)
uniq=[]; ukept=[]
for bb,w in zip(kept,windows):
    if any(abs(bb[0]-k[0])<6 and abs(bb[2]-k[2])<6 and abs(bb[1]-k[1])<6 for k in ukept): continue
    ukept.append(bb); uniq.append(w)
windows=uniq
out_seams=seamx
# silhouette: top outline (rdp) and rocker between/around wheels
topline=rdp([(x,top[x]) for x in cols],1.2)
rocker=[]
for x in cols:
    inwheel=any(w['cx']-w['arch_r']<=x<=w['cx']+w['arch_r'] for w in wheels)
    if not inwheel: rocker.append((x,bot[x]))
rocker=rdp(rocker,1.5)
def S(p): # pixel -> scene (x fore/aft with +x = front, y up from ground)
    x,y=p; sx=(x-(x0+x1)/2)*unit; sy=(ground-y)*unit
    return [round(sx if a.front=='right' else -sx,3),round(sy,3)]
out={'source':a.image,'length_in':a.length_in,'unit_per_px':unit,'image_size':[W,H],
     'outline_top':[S(p) for p in topline],'rocker':[S(p) for p in rocker],
     'wheels':[{'cx':S((w['cx'],w['cy']))[0],'cy':S((w['cx'],w['cy']))[1],'r':round(w['r']*unit,3),'arch_r':round(w['arch_r']*unit,3)} for w in wheels],
     'windows':[[S(p) for p in w] for w in windows],'doors':sorted([[S(p) for p in d] for d in doors],key=lambda d:min(q[0] for q in d)),'seams':[S((x,0))[0] for x in out_seams],'belt_y':S((0,belt))[1],'rocker_y':S((0,rock_y))[1],
     'extent':{'front':S((x1,0))[0],'rear':S((x0,0))[0],'roof':S((0,y0))[1]}}
if a.front=='right': out['wheels'].sort(key=lambda w:-w['cx'])
json.dump(out,open(a.out,'w'),indent=1)
wb=abs(out['wheels'][0]['cx']-out['wheels'][1]['cx'])/0.0254*0.25 if len(out['wheels'])==2 else None
print(f"traced {a.image}: {len(topline)} top pts, {len(rocker)} rocker pts, {len(wheels)} wheels, {len(windows)} windows, {len(doors)} doors")
print((f"wheelbase measured {wb:.1f} in" + (f" vs spec {a.wheelbase_in} ({(wb-a.wheelbase_in)/a.wheelbase_in*100:+.1f}%)" if a.wheelbase_in else '')) if wb else 'wheelbase: wheels not found', f"| height {out['extent']['roof']*0.25/0.0254:.1f} in"+(f" vs spec {a.height_in}" if a.height_in else ''), (f"| tire r {out['wheels'][0]['r']:.2f} u" if out['wheels'] else ''))
for w in out['wheels']: print('  wheel',w)
print('  windows x-ranges:',[(min(p[0] for p in w),max(p[0] for p in w)) for w in windows]); print('  doors x-ranges:',[(min(p[0] for p in d),max(p[0] for p in d)) for d in doors])
