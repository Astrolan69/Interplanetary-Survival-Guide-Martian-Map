import json, math, numpy as np
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from paths import ROOT, RAW, TOOLS
from PIL import Image
from scipy import ndimage
src=open('tools/v2.py').read(); exec(src[:src.index('# ---------- region')])
D4=RAW+'/data4/'
META.update(json.load(open(S+'data/meta.json')))
d=np.fromfile(D4+'g_dem10.d16',dtype='<i2').reshape(1024,2048).astype(np.int32)
z=np.cumsum(d,axis=1).astype(float)*10
print('dem',z.min(),z.max())
b=[-180,-90,180,90]; h,w=z.shape
# hillshade in deg-space: dx varies with latitude
lat=np.linspace(90,-90,h)[:,None]; dx=(360/w)*DEG*np.maximum(np.cos(np.radians(lat)),0.05); dy=180/h*DEG
gy=np.gradient(z,axis=0)/dy; gx=np.gradient(z,axis=1)/dx
sl=np.arctan(np.hypot(gx,gy)); asp=np.arctan2(gy,-gx); az,alt=math.radians(315),math.radians(40)
hs=np.clip(np.sin(alt)*np.cos(sl)+np.cos(alt)*np.sin(sl)*np.cos(az-asp)*6,0,1)  # exaggerate relief
lo,hi=-8000.0,12000.0
rgb=ramp((z-lo)/(hi-lo),ELEV)*(0.5+0.55*hs[...,None])
Image.fromarray(np.clip(rgb,0,255).astype(np.uint8)).save(S+'img/global_elev.jpg',quality=86)
GL,GH=-8200.0,21200.0
zs=z[::2,::2]; ss=np.degrees(sl)[::2,::2]
v=np.round((zs-GL)/(GH-GL)*65535).astype(np.uint32); g=np.zeros(zs.shape+(4,),np.uint8); g[...,0]=v>>8; g[...,1]=v&255; g[...,2]=np.clip(ss*4,0,255); g[...,3]=255
Image.fromarray(g,'RGBA').save(S+'data/global_grid.png',optimize=True)
META['global']=dict(bbox=b,lo=GL,hi=GH,leg=[lo,hi],w=zs.shape[1],h=zs.shape[0],cell=[20800,20800])
for n in ['tday','tnight']:
    a=np.array(Image.open(D4+f'g_{n}.jpg').convert('L')).astype(float)
    m=a>3; vals=np.sort(a[m]); t=np.searchsorted(vals,a)/len(vals)
    out=ramp(t,INF); out[~m]=(20,16,14)
    Image.fromarray(out.astype(np.uint8)).save(S+f'img/global_{n}.jpg',quality=85)
Image.open(D4+'g_vis.jpg').save(S+'img/global_vis.jpg',quality=82)
Image.open(D4+'g_vis.jpg').resize((2048,1024),Image.LANCZOS).save(S+'img/globe_vis.jpg',quality=85)
json.dump(META,open(S+'data/meta.json','w'))
print(META['global'])
