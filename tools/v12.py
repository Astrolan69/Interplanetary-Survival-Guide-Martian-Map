# v12: "Ground" layer = walking conditions interpreted from MGS TES thermal inertia (Mars Trek TES_Thermal_Inertia).
# Classes (J m-2 K-1 s-1/2): <100 soft dust, 100-250 sand, 250-400 coarse sand / duricrust / scattered rock, >400 rock & bedrock.
import numpy as np
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from paths import ROOT, RAW, TOOLS
from PIL import Image
S=ROOT+'/'
CL=[(0,100,(224,71,60)),(100,250,(242,182,50)),(250,400,(156,204,74)),(400,1e9,(47,174,97))]
idx=np.array(Image.open(S+'data/ti_grid.png')).astype(float); nod=idx==255; ti=25+idx/250*575
H,W=ti.shape; rgba=np.zeros((H,W,4),np.uint8)
for lo,hi,c in CL:
    m=(ti>=lo)&(ti<hi)&~nod; rgba[m,:3]=c; rgba[m,3]=255
Image.fromarray(rgba,'RGBA').save(S+'img/global_ground.png',optimize=True)
# globe texture: class colors over the grayscale Basic image; no-data (poles) = plain grayscale
vis=np.array(Image.open(S+'img/globe_vis.jpg').convert('L').resize((2048,1024),Image.LANCZOS)).astype(float)
cls=np.array(Image.fromarray(rgba,'RGBA').resize((2048,1024),Image.NEAREST)).astype(float)
g=np.stack([vis]*3,-1)*0.85; a=(cls[...,3:4]/255)*0.62
out=g*(1-a)+cls[...,:3]*a*(0.55+0.45*vis[...,None]/255*1.6)
Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(S+'img/globe_ground.jpg',quality=86)
for lo,hi,c in CL: print(lo,hi,'%.1f%%'%((((ti>=lo)&(ti<hi)&~nod).sum())/(~nod).sum()*100))
