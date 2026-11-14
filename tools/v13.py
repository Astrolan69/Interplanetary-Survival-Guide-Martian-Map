# v13: EVA budget + boxwork science stop.
#  - every safest route gets back_h: the time to walk the SAME path in reverse (target -> lander),
#    with the same slope/roughness speed model as walk_h (uphill legs become downhill and vice versa).
#  - new Gale science stop at the boxwork ridges (Curiosity rover position on sol 4563, 2025),
#    with a least-time route from the crew lander that never crosses terrain steeper than 15 deg.
# Run from the repo root:  python3 tools/v13.py
import json, math, os, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
HERE=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(HERE,'v8.py')).read()
S=os.path.dirname(HERE)+'/'
pre=src[:src.index('# ---- 1. Spirit DEM')].replace("S='/home/claude/repo/'","")
exec(pre)                                                     # helpers, META
exec(src[src.index('def load(k):'):src.index('# ---- 2.')])   # load()
exec(src[src.index('def dist('):src.index('M=json.load(')])   # dist, G class (route())

def speed(g,a,b):
    """walking speed (m/s) from cell a to cell b: same model as G.route()"""
    (i,j),(ni,nj)=a,b; d=math.hypot((ni-i)*g.dy,(nj-j)*g.dx); S_=(g.z[ni,nj]-g.z[i,j])/d
    return d, 1.0*math.exp(-3.5*abs(S_+0.05))*0.83/(1+2.5*g.rn[ni,nj])

def path_cells(g,a,b_,maxs=15):
    """re-run G.route() but keep the full cell path (G.route() only returns a thinned polyline)"""
    r=g.route(a,b_,maxs)
    if r is None: return None,None
    # rebuild the full path: route() leaves no handle, so redo the search with a tiny wrapper
    si,sj=g.ij(*a); ti,tj=g.ij(*b_)
    import heapq
    H,W=g.h,g.w; INF=1e18; gg=np.full((H,W),INF); prev=-np.ones((H,W),np.int64); gg[si,sj]=0; pq=[(0,si,sj)]
    tm=math.tan(math.radians(maxs)); free=~g.block; free[ti,tj]=True; free[si,sj]=True
    nb=[(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    while pq:
        c,i,j=heapq.heappop(pq)
        if c>gg[i,j]: continue
        if (i,j)==(ti,tj): break
        for di,dj in nb:
            ni,nj=i+di,j+dj
            if ni<0 or nj<0 or ni>=H or nj>=W or not free[ni,nj]: continue
            d=math.hypot(di*g.dy,dj*g.dx); S_=(g.z[ni,nj]-g.z[i,j])/d
            if abs(S_)>tm and (ni,nj)!=(ti,tj): continue
            v=1.0*math.exp(-3.5*abs(S_+0.05))*(0.83)/(1+2.5*g.rn[ni,nj]); nc=c+d/v
            if nc<gg[ni,nj]: gg[ni,nj]=nc; prev[ni,nj]=i*W+j; heapq.heappush(pq,(nc,ni,nj))
    path=[]; k=ti*W+tj
    while k!=-1:
        path.append(divmod(k,W)); pi,pj=divmod(k,W); k=prev[pi,pj] if (pi,pj)!=(si,sj) else -1
    return r,path[::-1]

def back_hours(g,path):
    rev=path[::-1]; t=0.0
    for q in range(1,len(rev)):
        d,v=speed(g,rev[q-1],rev[q]); t+=d/v
    return round(t/3600,2)

M=json.load(open(S+'data/missions.json')); HZ=json.load(open(S+'data/hazards.json'))
K={'curiosity':'gale','spirit':'spirit','perseverance':'jezero'}

BOX=dict(kind='science',title='Boxwork ridges: groundwater science stop',lat=-4.799847,lon=137.383541,sol=4563,
  why='Curiosity explored these web-like mineral ridges (1–2 m tall, sandy hollows between them) from mid-2025: ancient groundwater hardened the ridge edges. '
      'X-ray analysis found clay minerals in a ridge sample and carbonates in a hollow sample, and the area lies in the sulfate-rich layer of Mount Sharp. '
      'A crew stop here samples the youngest groundwater record in Gale on the way along the sulfate unit.',
  src='NASA/JPL, 23 Jun 2025 and 23 Feb 2026 (Curiosity boxwork releases); position = Curiosity on sol 4563 (NASA/JPL MMGIS)',
  link='https://www.nasa.gov/missions/mars-science-laboratory/curiosity-rover/nasas-curiosity-rover-sees-martian-spiderwebs-up-close/')
cs=M['curiosity']['sites']
if not any(s['title']==BOX['title'] for s in cs):
    cs.insert(1,dict(BOX,route={}))

for mk,k in K.items():
    g=G(k); m=META[k]; b=m['bbox']
    # hazard zones (as in v9): rasterise the stored outlines, keep 50 m away
    mask=Image.new('L',(g.w,g.h),0); dr=ImageDraw.Draw(mask)
    for h in HZ[mk]['hazards']:
        for ring in h['rings']:
            dr.polygon([((lo-b[0])/(b[2]-b[0])*g.w,(b[3]-la)/(b[3]-b[1])*g.h) for la,lo in ring],fill=1)
    hz=np.array(mask)>0
    g.block|=ndimage.binary_dilation(hz,iterations=max(1,round(50/g.dx)))
    L_=M[mk]['lander']
    for s in M[mk]['sites']+M[mk]['sulfur']:
        if s.get('route') is None: continue
        old=s['route']; r,path=path_cells(g,(L_['lat'],L_['lon']),(s['lat'],s['lon']))
        if r is None: print('NO ROUTE',s['title']); continue
        if old and abs(old.get('km',0)-r['km'])>0.02: print('  !! route changed',s['title'][:40],old.get('km'),'->',r['km'])
        r['back_h']=back_hours(g,path); s['route']=r
        print(mk,s['title'][:42].ljust(42),'km',r['km'],'out',r['walk_h'],'back',r['back_h'],'climb',r['climb'],'max',r['maxslope'])
json.dump(M,open(S+'data/missions.json','w'),separators=(',',':'))
