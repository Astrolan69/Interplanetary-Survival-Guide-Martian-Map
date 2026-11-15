# v9: real hazard-zone outlines and vector no-go (>15 deg) outlines from the DEMs; routes avoid the real hazard areas (+50 m).
import json, math, numpy as np
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from paths import ROOT, RAW, TOOLS
from PIL import Image
from scipy import ndimage
from skimage import measure
src=open(TOOLS+'/v8.py').read()
exec(src[:src.index('# ---- 1. Spirit DEM')])            # helpers, META
exec(src[src.index('def load(k):'):src.index('# ---- 2.')])  # load()
exec(src[src.index('def dist('):src.index('M=json.load(')])  # dist, G class
M=json.load(open(S+'data/missions.json'))
K={'curiosity':'gale','spirit':'spirit','perseverance':'jezero'}
Z1=np.load(RAW+'/data4/spi_z.npy').astype(float)   # Spirit DEM at ~5 m
def rings(mask,b,minpx=3,tol=0.6):
    H,W=mask.shape; lab,n=ndimage.label(mask); sz=ndimage.sum(mask,lab,range(1,n+1))
    keep=np.isin(lab,np.where(sz>=minpx)[0]+1)
    out=[]
    for c in measure.find_contours(np.pad(keep,1).astype(float),0.5):
        c=measure.approximate_polygon(c,tol)
        if len(c)<4: continue
        out.append([[round(b[3]-(y-1+.5)/H*(b[3]-b[1]),6),round(b[0]+(x-1+.5)/W*(b[2]-b[0]),6)] for y,x in c])
    return out
def hazard_mask(mk,k,s,z,sl,m):
    dx,dy=m['cell']; H,W=z.shape; b=m['bbox']; yy,xx=np.mgrid[0:H,0:W]
    i=int((b[3]-s['lat'])/(b[3]-b[1])*H); j=int((s['lon']-b[0])/(b[2]-b[0])*W); d=np.hypot((yy-i)*dy,(xx-j)*dx)
    pick=lambda lab,msk,dd,i,j: lab[i,j] if lab[i,j] else lab[np.unravel_index(np.argmin(np.where(msk,dd,1e9)),dd.shape)]
    t=s['title']
    if 'Steep' in t:   # connected terrain steeper than 15 deg
        msk=ndimage.binary_opening(sl>15,iterations=1); lab,_=ndimage.label(msk); return 'grid',ndimage.binary_fill_holes(lab==pick(lab,msk,d,i,j)),'connected DEM terrain steeper than 15°'
    if 'Hidden' in t:  # sand-floored valley: local depression on the DEM
        loc=z-ndimage.uniform_filter(z,17); msk=(loc<-1.5)&(sl<14)&(d<700); lab,_=ndimage.label(msk)
        return 'grid',ndimage.binary_fill_holes(lab==pick(lab,msk,d,i,j)),'sand-floored valley floor (local depression on the HiRISE DEM)'
    # Spirit soft soils, on the 1 m DEM (~5 m cells)
    h1,w1=Z1.shape; i1=int((b[3]-s['lat'])/(b[3]-b[1])*h1); j1=int((s['lon']-b[0])/(b[2]-b[0])*w1)
    y1,x1=np.mgrid[0:h1,0:w1]; dd=np.hypot((y1-i1)*dy/2,(x1-j1)*dx/2)
    if 'Troy' in t:
        loc=Z1-ndimage.uniform_filter(Z1,13); msk=(loc<0.15)&(dd<45); why='low ground at the foot of Home Plate where Spirit sank (1 m DEM)'
    else:
        msk=dd<30; why='30 m around the spot where Spirit dug in (the soft patch is too small to outline from orbit)'
    lab,_=ndimage.label(msk); reg=ndimage.binary_fill_holes(ndimage.binary_closing(lab==pick(lab,msk,dd,i1,j1),iterations=2))
    return 'hi',reg,why
HZ={}
for mk,k in K.items():
    g=G(k); m=META[k]; b=m['bbox']; dx,dy=m['cell']
    nogo=rings(g.sl>15,b,minpx=2,tol=0.5)
    hz=[]; block=np.zeros_like(g.block)
    for s in [x for x in M[mk]['sites'] if x['kind']=='hazard']:
        kind,reg,why=hazard_mask(mk,k,s,g.z,g.sl,m)
        poly=rings(reg,b,minpx=1,tol=0.4 if kind=='grid' else 0.8)
        area=reg.sum()*dx*dy/(4 if kind=='hi' else 1)
        gm=reg if kind=='grid' else np.array(Image.fromarray(reg.astype(np.uint8)*255).resize((g.w,g.h),Image.BOX))>0
        block|=ndimage.binary_dilation(gm,iterations=max(1,round(50/dx)))
        s['area_m2']=int(round(area,-1)); s['basis']=why; s.pop('zone',None)
        hz.append(dict(title=s['title'],rings=poly,area=s['area_m2']))
        print(mk,s['title'][:38],'area',s['area_m2'],'rings',len(poly))
    HZ[mk]=dict(hazards=hz,nogo=nogo); print(mk,'no-go rings',len(nogo),sum(len(r) for r in nogo),'pts')
    g.block|=block
    L_=M[mk]['lander']
    for s in M[mk]['sites']+M[mk]['sulfur']:
        if s.get('route'):
            old=s['route']; s['route']=g.route((L_['lat'],L_['lon']),(s['lat'],s['lon'])); r=s['route']
            print('   route',s['title'][:36],old['km'],'->',r and (r['km'],r['walk_h'],r['maxslope']))
json.dump(HZ,open(S+'data/hazards.json','w'),separators=(',',':'))
json.dump(M,open(S+'data/missions.json','w'),separators=(',',':'))
import os; print('hazards.json KB',os.path.getsize(S+'data/hazards.json')//1024)
