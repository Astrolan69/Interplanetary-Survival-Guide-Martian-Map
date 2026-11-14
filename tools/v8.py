# v8: Spirit DEM rebuilt from the Mars Trek 1 m Columbia Hills DEM (Float32 ImageServer),
# no-go overlays regenerated, all safest routes recomputed with a terrain-slope limit (no cell steeper than 15 deg).
import json, math, heapq, numpy as np
from PIL import Image
from scipy import ndimage
S='/home/claude/repo/'
R=3389500.0; DEG=math.pi/180*R
ELEV=[(0,(36,40,110)),(.15,(40,95,170)),(.3,(60,160,170)),(.45,(110,190,110)),(.6,(225,215,110)),(.75,(220,140,70)),(.88,(170,80,60)),(1,(250,245,240))]
def ramp(t,stops):
    t=np.clip(t,0,1); out=np.zeros(t.shape+(3,))
    for (a,ca),(b,cb) in zip(stops[:-1],stops[1:]):
        m=(t>=a)&(t<=b); f=((t-a)/(b-a))[m][:,None]; out[m]=np.array(ca)*(1-f)+np.array(cb)*f
    return out
def cell_m(b,w,h):
    lat=(b[1]+b[3])/2; return (b[2]-b[0])/w*DEG*math.cos(math.radians(lat)), (b[3]-b[1])/h*DEG
def hillshade(z,dx,dy):
    gy,gx=np.gradient(z,dy,dx); sl=np.arctan(np.hypot(gx,gy)); asp=np.arctan2(gy,-gx); az,alt=math.radians(315),math.radians(40)
    return np.clip(np.sin(alt)*np.cos(sl)+np.cos(alt)*np.sin(sl)*np.cos(az-asp),0,1), np.degrees(sl)
META=json.load(open(S+'data/meta.json'))
def save_layers(key,z,b):
    h,w=z.shape; dx,dy=cell_m(b,w,h); hs,sl=hillshade(z,dx,dy); lo=float(z.min()); hi=float(z.max())
    rgb=ramp((z-lo)/(hi-lo),ELEV)*(0.55+0.5*hs[...,None])
    Image.fromarray(np.clip(rgb,0,255).astype(np.uint8)).save(S+f'img/{key}_elev.png',optimize=True)
    v=np.round((z-lo)/(hi-lo)*65535).astype(np.uint32); g=np.zeros((h,w,4),np.uint8); g[...,0]=v>>8; g[...,1]=v&255; g[...,2]=np.clip(sl*4,0,255); g[...,3]=255
    Image.fromarray(g,'RGBA').save(S+f'data/{key}_grid.png',optimize=True)
    META[key].update(bbox=b,lo=lo,hi=hi,w=w,h=h,cell=[round(dx,1),round(dy,1)])
# ---- 1. Spirit DEM
b=META['spirit']['bbox']
zs=np.load('/home/claude/data4/spi_grid_z.npy')
save_layers('spirit',zs,b)
json.dump(META,open(S+'data/meta.json','w'),separators=(',',':'))
def load(k):
    m=META[k]; a=np.array(Image.open(S+f'data/{k}_grid.png').convert('RGBA')).astype(float)
    z=m['lo']+(a[...,0]*256+a[...,1])/65535*(m['hi']-m['lo']); dx,dy=m['cell']
    gy,gx=np.gradient(z,dy,dx); return z,np.degrees(np.arctan(np.hypot(gx,gy))),m
# ---- 2. no-go overlays (slope > 15 deg), 4x, 45 deg hatch
for k in ['gale','spirit','jezero']:
    z,sl,m=load(k); mask=np.kron((sl>15).astype(np.uint8),np.ones((4,4),np.uint8)).astype(bool)
    H,W=mask.shape; yy,xx=np.mgrid[0:H,0:W]; st=((xx+yy)%6)<2
    o=np.zeros((H,W,4),np.uint8); o[mask&st]=(255,60,60,190); o[mask&~st]=(235,45,45,70)
    Image.fromarray(o,'RGBA').save(S+f'img/{k}_nogo.png',optimize=True); print(k,'no-go %',round((sl>15).mean()*100,1))
# ---- 3. routes
def dist(a,b_):
    p1,p2=math.radians(a[0]),math.radians(b_[0]); dl=math.radians(b_[1]-a[1]); h=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2; return 2*R*math.asin(math.sqrt(h))
VIS={'gale':'gale_vis.jpg','spirit':'spirit_vis.jpg','jezero':'jezero_vis.jpg'}
class G:
    def __init__(s,k):
        s.z,s.sl,m=load(k); s.b=m['bbox']; s.h,s.w=s.z.shape; s.dx,s.dy=m['cell']
        im=np.array(Image.open(S+'img/'+VIS[k]).convert('L')).astype(float)
        hp=im-ndimage.gaussian_filter(im,3); r=np.sqrt(ndimage.gaussian_filter(hp**2,4))
        s.rough=np.array(Image.fromarray(r.astype(np.float32)).resize((s.w,s.h),Image.BOX)).astype(float)
        mean=np.array(Image.fromarray(im.astype(np.float32)).resize((s.w,s.h),Image.BOX)).astype(float)
        s.nod=ndimage.binary_dilation(mean<8,iterations=6)
        q5,q95=np.percentile(s.rough[~s.nod],5),np.percentile(s.rough[~s.nod],95)
        s.rn=np.clip((s.rough-q5)/(q95-q5+1e-9),0,1.5); s.rn[s.nod]=0.5
        yy,xx=np.mgrid[0:s.h,0:s.w]; s.lon=s.b[0]+(xx+.5)/s.w*(s.b[2]-s.b[0]); s.lat=s.b[3]-(yy+.5)/s.h*(s.b[3]-s.b[1])
        s.block=s.sl>15
    def ij(s,lat,lon): return int((s.b[3]-lat)/(s.b[3]-s.b[1])*s.h), int((lon-s.b[0])/(s.b[2]-s.b[0])*s.w)
    def ll(s,i,j): return (round(float(s.lat[i,j]),6),round(float(s.lon[i,j]),6))
    def dmap(s,lat,lon): return np.hypot((s.lat-lat)*DEG,(s.lon-lon)*DEG*math.cos(math.radians(lat)))
    def route(s,a,b_,maxs=15):
        si,sj=s.ij(*a); ti,tj=s.ij(*b_); H,W=s.h,s.w; INF=1e18
        g=np.full((H,W),INF); prev=-np.ones((H,W),np.int64); g[si,sj]=0; pq=[(0,si,sj)]; tm=math.tan(math.radians(maxs))
        free=~s.block; free[ti,tj]=True; free[si,sj]=True
        # allow the last few cells around the target (outcrop edges)
        nb=[(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        while pq:
            c,i,j=heapq.heappop(pq)
            if c>g[i,j]: continue
            if (i,j)==(ti,tj): break
            for di,dj in nb:
                ni,nj=i+di,j+dj
                if ni<0 or nj<0 or ni>=H or nj>=W or not free[ni,nj]: continue
                d=math.hypot(di*s.dy,dj*s.dx); S_=(s.z[ni,nj]-s.z[i,j])/d
                if abs(S_)>tm and (ni,nj)!=(ti,tj): continue
                v=1.0*math.exp(-3.5*abs(S_+0.05))*(0.83)/(1+2.5*s.rn[ni,nj])
                nc=c+d/v
                if nc<g[ni,nj]: g[ni,nj]=nc; prev[ni,nj]=i*W+j; heapq.heappush(pq,(nc,ni,nj))
        if g[ti,tj]>=INF: return None
        path=[]; k=ti*W+tj
        while k!=-1:
            path.append(divmod(k,W)); pi,pj=divmod(k,W); k=prev[pi,pj] if (pi,pj)!=(si,sj) else -1
        path=path[::-1]
        pts=[s.ll(i,j) for i,j in path]; L=sum(dist(pts[q-1],pts[q]) for q in range(1,len(pts)))
        zz=[s.z[i,j] for i,j in path]; up=sum(max(0,zz[q]-zz[q-1]) for q in range(1,len(zz)))
        mx=max(float(s.sl[i,j]) for i,j in path[:-1]) if len(path)>1 else 0
        step=max(1,len(pts)//150); pts=pts[::step]+[pts[-1]]
        return dict(pts=[list(p) for p in pts],km=round(L/1000,2),walk_h=round(float(g[ti,tj])/3600,2),rover_h=round(L/1000/8,2),climb=round(up),maxslope=round(mx,1))
M=json.load(open(S+'data/missions.json'))
K={'curiosity':'gale','spirit':'spirit','perseverance':'jezero'}
for mk,k in K.items():
    g=G(k); m=M[mk]; L_=m['lander']; i,j=g.ij(L_['lat'],L_['lon'])
    kk=max(3,int(400/g.dx)); ms=ndimage.uniform_filter(g.sl,kk)
    L_['elev']=round(float(g.z[i,j])); L_['slope']=round(float(ms[i,j]),1)
    for h in [s for s in m['sites'] if s['kind']=='hazard']:
        g.rn[g.dmap(h['lat'],h['lon'])<(h.get('zone',250)+50)]=1e6
    for s in m['sites']+m['sulfur']:
        if s.get('route'):
            old=s['route']; s['route']=g.route((L_['lat'],L_['lon']),(s['lat'],s['lon']))
            r=s['route']; print(mk,s['title'][:40],'old',old['km'],old['maxslope'],'-> new',r and (r['km'],r['walk_h'],r['climb'],r['maxslope']))
    print(mk,'lander',L_)
json.dump(M,open(S+'data/missions.json','w'),separators=(',',':'))
