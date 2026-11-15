import json, math, heapq, csv
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from paths import ROOT, RAW, TOOLS
import numpy as np
from PIL import Image
from scipy import ndimage
D=RAW+'/data2/'; D1=RAW+'/data/'; S=ROOT+'/'
R=3389500.0; DEG=math.pi/180*R
BOX=dict(region=[130,-20,180,10], gale=[137.32,-4.86,137.47,-4.56], insight=[135.57,4.44,135.68,4.56], spirit=[175.462,-14.612,175.540,-14.552])
META={}
# ---------- color ramps
ELEV=[(0,(36,40,110)),(.15,(40,95,170)),(.3,(60,160,170)),(.45,(110,190,110)),(.6,(225,215,110)),(.75,(220,140,70)),(.88,(170,80,60)),(1,(250,245,240))]
INF=[(0,(0,0,4)),(.25,(87,16,110)),(.5,(188,55,84)),(.75,(249,142,9)),(1,(252,255,164))]
def ramp(t,stops):
    t=np.clip(t,0,1); out=np.zeros(t.shape+(3,))
    for (a,ca),(b,cb) in zip(stops[:-1],stops[1:]):
        m=(t>=a)&(t<=b); f=((t-a)/(b-a))[m][:,None]; out[m]=np.array(ca)*(1-f)+np.array(cb)*f
    return out
def css(stops): return 'linear-gradient(90deg,'+','.join(f'rgb{c} {int(p*100)}%' for p,c in stops)+')'
def cell_m(b,w,h):
    lat=(b[1]+b[3])/2; return (b[2]-b[0])/w*DEG*math.cos(math.radians(lat)), (b[3]-b[1])/h*DEG
def hillshade(z,dx,dy):
    gy,gx=np.gradient(z,dy,dx); sl=np.arctan(np.hypot(gx,gy)); asp=np.arctan2(gy,-gx); az,alt=math.radians(315),math.radians(40)
    return np.clip(np.sin(alt)*np.cos(sl)+np.cos(alt)*np.sin(sl)*np.cos(az-asp),0,1), np.degrees(sl)
def save_layers(key,z,b,lo=None,hi=None,shade=True):
    h,w=z.shape; dx,dy=cell_m(b,w,h); hs,sl=hillshade(z,dx,dy)
    lo=float(np.nanmin(z)) if lo is None else lo; hi=float(np.nanmax(z)) if hi is None else hi
    rgb=ramp((z-lo)/(hi-lo),ELEV)*((0.55+0.5*hs[...,None]) if shade else 1)
    Image.fromarray(np.clip(rgb,0,255).astype(np.uint8)).save(S+f'img/{key}_elev.png',optimize=True)
    v=np.round((z-lo)/(hi-lo)*65535).astype(np.uint32); g=np.zeros((h,w,4),np.uint8); g[...,0]=v>>8; g[...,1]=v&255; g[...,2]=np.clip(sl*4,0,255); g[...,3]=255
    Image.fromarray(g,'RGBA').save(S+f'data/{key}_grid.png',optimize=True)
    META[key]=dict(bbox=b,lo=lo,hi=hi,w=w,h=h,cell=[round(dx,1),round(dy,1)])
    return sl,dx,dy
def thermal(key,src,out):
    a=np.array(Image.open(src).convert('L')).astype(float); lo,hi=np.percentile(a,1),np.percentile(a,99)
    rgb=ramp((a-lo)/(hi-lo+1e-9),INF).astype(np.uint8); im=Image.fromarray(rgb)
    if im.width<400: im=im.resize((im.width*6,im.height*6),Image.BICUBIC)
    im.save(S+f'img/{out}.jpg',quality=86)
# ---------- region
zr=np.load(D+'reg_dem.npy').astype(float)
save_layers('region',zr,BOX['region'],-4500.0,2500.0)
thermal('region',D+'reg_tday.jpg','region_tday'); thermal('region',D+'reg_tnight.jpg','region_tnight')
Image.open(D+'reg_viking.jpg').save(S+'img/region_vis.jpg',quality=82)
# ---------- gale
zg=np.fromfile(D+'gale_dem.i16',dtype='<i2').reshape(600,300).astype(float)
gsl,gdx,gdy=save_layers('gale',zg,BOX['gale'])
Image.open(D+'gale_hirise.jpg').save(S+'img/gale_vis.jpg',quality=80)
thermal('gale',D+'gale_tday.png','gale_tday'); thermal('gale',D+'gale_tnight.png','gale_tnight')
Image.open(D1+'hirise_aoi.jpg').resize((1600,1867)).save(S+'img/gale_boxwork.jpg',quality=78)
# ---------- insight
zi=np.fromfile(D+'ins_dem.i16',dtype='<i2').reshape(120,110).astype(float)
zi=ndimage.zoom(ndimage.gaussian_filter(zi,1.5),4,order=3)
isl,idx,idy=save_layers('insight',zi,BOX['insight'])
Image.open(D+'ins_hirise.jpg').save(S+'img/insight_vis.jpg',quality=80)
Image.open(D+'ins_lander.jpg').save(S+'img/insight_lander.jpg',quality=85)
thermal('insight',D+'ins_tday.png','insight_tday'); thermal('insight',D+'ins_tnight.png','insight_tnight')
# ---------- spirit (calibrated CTX/HiRISE DEM)
g=np.array(Image.open(D+'spi_demgray.png').convert('L')).astype(float)
zc=g*0.283523524-1943.76938
mm=np.fromfile(D+'spi_dem.i16',dtype='<i2').reshape(60,78).astype(float)
mu=np.array(Image.fromarray(mm.astype(np.float32)).resize((g.shape[1],g.shape[0]),Image.BICUBIC))
sat=ndimage.binary_dilation(g>=250,iterations=3)
zc=np.where(sat,np.maximum(zc,mu),zc)
zs=ndimage.gaussian_filter(zc,1.2)
zs=np.array(Image.fromarray(zs.astype(np.float32)).resize((455,350),Image.BILINEAR)).astype(float)
ssl,sdx,sdy=save_layers('spirit',zs,BOX['spirit'])
Image.open(D+'spi_hirise.jpg').save(S+'img/spirit_vis.jpg',quality=80)
thermal('spirit',D+'spi_tday.png','spirit_tday'); thermal('spirit',D+'spi_tnight.png','spirit_tnight')
META['ramps']=dict(elev=css(ELEV),thermal=css(INF))
json.dump(META,open(S+'data/meta.json','w'))
np.savez(RAW+'/data2/grids.npz',zg=zg,gsl=gsl,zi=zi,isl=isl,zs=zs,ssl=ssl)
print({k:(v['lo'],v['hi'],v['w'],v['h'],v['cell']) for k,v in META.items() if k!='ramps'})
