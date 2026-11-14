import json,numpy as np,math
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/home/claude/repo/'; D='/home/claude/data9/'
meta=json.load(open(S+'data/meta.json'))
# ---------- 1. TES thermal inertia
rgb=Image.open(D+'ti_rgb.png').convert('RGBA'); rgb.save(S+'img/global_ti.png',optimize=True)
ti=np.load(D+'ti.npy')
idx=np.where(np.isnan(ti),255,np.clip(np.round((ti-25)/575*250),0,250)).astype(np.uint8)
Image.fromarray(idx).save(S+'data/ti_grid.png',optimize=True)
print('ti grid',idx.shape)
# ---------- 2. temperatures (REMS ground + air, MEDA air)
w=json.load(open(D+'weather.json'))
A=[r for r in w['msl'] if r[4] is not None and r[5] is not None and r[1] is not None]
# drop obvious sensor outliers: daily min below -110 C or max above 40 C
A=[r for r in A if -110<=r[4] and r[5]<=40]
months=[]
for m in range(12):
    s=[r for r in A if int(r[1]//30)==m]
    months.append(dict(m=m+1,ls=f'{m*30}-{m*30+30}',n=len(s),gmin=round(float(np.median([r[4] for r in s]))),gmax=round(float(np.median([r[5] for r in s]))),
                       amin=round(float(np.median([r[2] for r in s if r[2] is not None]))),amax=round(float(np.median([r[3] for r in s if r[3] is not None])))))
cold=min(A,key=lambda r:r[4]); warm=max(A,key=lambda r:r[5]); last=max(A,key=lambda r:r[0])
temps=dict(curiosity=dict(src='NASA/JPL-Caltech · CAB (INTA-CSIC) REMS daily reports (outreach data)',nsols=len(A),sol0=min(r[0] for r in A),sol1=last[0],
   gmin_med=round(float(np.median([r[4] for r in A]))),gmax_med=round(float(np.median([r[5] for r in A]))),
   gmin_p5=round(float(np.percentile([r[4] for r in A],5))),gmax_p95=round(float(np.percentile([r[5] for r in A],95))),
   coldest=dict(sol=cold[0],date=cold[6],t=cold[4]),warmest=dict(sol=warm[0],date=warm[6],t=warm[5]),
   last=dict(sol=last[0],date=last[6],gmin=last[4],gmax=last[5],amin=last[2],amax=last[3]),months=months),
 perseverance=dict(src='NASA/JPL-Caltech · CAB MEDA daily reports (outreach data)',sols=[dict(sol=r[0],date=r[4],amin=r[2],amax=r[3]) for r in w['m20'] if r[2] is not None]))
json.dump(temps,open(S+'data/temps.json','w'),separators=(',',':'))
print(json.dumps(temps)[:900])
# ---------- 3. minerals (Ehlmann & Edwards 2014 aqueous classes; Carter et al. 2013 hydrous detections)
mn=json.load(open(D+'minerals.json')); C=['phyllosilicate','sulfate','chloride','silica','carbonate']
aq=[[r[0],r[1],C.index(r[2])] for r in mn['aq'] if r[2] in C]
json.dump(dict(classes=C,aq=aq,hyd=mn['hyd']),open(S+'data/minerals.json','w'),separators=(',',':'))
print('aq',len(aq),'hyd',len(mn['hyd']))
# ---------- 4. contours
def grid(k):
    m=meta[k]; a=np.asarray(Image.open(S+f'data/{k}_grid.png').convert('RGB')).astype(float)
    z=m['lo']+(a[...,0]*256+a[...,1])/65535*(m['hi']-m['lo']); return z,m['bbox']
cfg={'global':(2000,None),'overview':(1000,None),'gale':(100,None),'spirit':(10,None),'jezero':(50,None)}
out={}
for k,(step,_) in cfg.items():
    z,b=grid(k); H,W=z.shape
    from scipy import ndimage
    zs=ndimage.gaussian_filter(z,{'global':0.8,'overview':2.0}.get(k,1.0))
    lo_,hi_=meta[k]['lo'],meta[k]['hi']
    levels=[v for v in np.arange(math.ceil(zs.min()/step)*step,zs.max(),step) if lo_+0.3*step<v<hi_-0.3*step]
    fig=plt.figure(); cs=plt.contour(np.arange(W),np.arange(H),zs,levels=levels); plt.close(fig)
    lines=[]
    for lev,segs in zip(cs.levels,cs.allsegs):
        for sgm in segs:
            if len(sgm)<(12 if k in ('global','overview') else 6): continue
            pts=[[round(b[3]-(y+.5)/H*(b[3]-b[1]),5),round(b[0]+(x+.5)/W*(b[2]-b[0]),5)] for x,y in sgm]
            # decimate
            st=max(1,len(pts)//(120 if k in ('global','overview') else 300)); pts=pts[::st]+[pts[-1]]
            pts=[[round(a,3 if k in ('global','overview') else 5),round(c,3 if k in ('global','overview') else 5)] for a,c in pts]
            lines.append([int(lev),pts])
    # spot heights: min and max cells
    i0,j0=np.unravel_index(np.argmin(z),z.shape); i1,j1=np.unravel_index(np.argmax(z),z.shape)
    ll=lambda i,j:[round(b[3]-(i+.5)/H*(b[3]-b[1]),4),round(b[0]+(j+.5)/W*(b[2]-b[0]),4)]
    out[k]=dict(step=step,lines=lines,lo=dict(z=round(float(z[i0,j0])),p=ll(i0,j0)),hi=dict(z=round(float(z[i1,j1])),p=ll(i1,j1)))
    print(k,step,len(lines),out[k]['lo'],out[k]['hi'])
zg,bg=grid('global'); H,W=zg.shape; b=meta['overview']['bbox']
lons=bg[0]+(np.arange(W)+.5)/W*360; lats=bg[3]-(np.arange(H)+.5)/H*180
mi=np.where((lats>=b[1])&(lats<=b[3]))[0]; mj=np.where((lons>=b[0])&(lons<=b[2]))[0]
sub=zg[np.ix_(mi,mj)]; a0=np.unravel_index(np.argmin(sub),sub.shape); a1=np.unravel_index(np.argmax(sub),sub.shape)
out['overview']['lo']=dict(z=round(float(sub[a0])),p=[round(float(lats[mi[a0[0]]]),3),round(float(lons[mj[a0[1]]]),3)])
out['overview']['hi']=dict(z=round(float(sub[a1])),p=[round(float(lats[mi[a1[0]]]),3),round(float(lons[mj[a1[1]]]),3)])
print('overview spots',out['overview']['lo'],out['overview']['hi'])
json.dump(out,open(S+'data/contours.json','w'),separators=(',',':'))
import os;print('contours KB',os.path.getsize(S+'data/contours.json')//1024)
