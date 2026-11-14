# v11: fix black areas in the global THEMIS day/night IR textures used on the globe.
#  - the night mosaic's overview tiles (zoom 2-3) are empty over 45W-0, 0-90S: rebuilt from zoom-4 tiles
#    and zoom-5 tiles (THEMIS_NightIR_ControlledMosaics_100m_v2_oct2018, downsampled, brightness-matched) -> g_tnight_fixed.png
#  - remaining thin orbit-gap streaks near +-60 deg: filled from neighbouring THEMIS pixels (diffusion inpainting)
#  - poles (|lat| > 65 deg) are outside THEMIS coverage: shown as muted gray Basic (Viking) imagery = no thermal data
import numpy as np
from PIL import Image
from scipy import ndimage
S='/home/claude/repo/'; D4='/home/claude/data4/'
INF=[(0,(0,0,4)),(.25,(87,16,110)),(.5,(188,55,84)),(.75,(249,142,9)),(1,(252,255,164))]
def ramp(t,stops):
    t=np.clip(t,0,1); out=np.zeros(t.shape+(3,))
    for (a,ca),(b,cb) in zip(stops[:-1],stops[1:]):
        m=(t>=a)&(t<=b); f=((t-a)/(b-a))[m][:,None]; out[m]=np.array(ca)*(1-f)+np.array(cb)*f
    return out
H,W=1024,2048; LAT=np.repeat((90-(np.arange(H)+.5)/H*180)[:,None],W,1); cov=np.abs(LAT)<=65
vis=np.array(Image.open(S+'img/global_vis.jpg').convert('L').resize((W,H),Image.LANCZOS)).astype(float)
gray=(vis/255)**0.9*150+25; G3=np.stack([gray*0.95,gray*0.93,gray*0.92],-1)
def inpaint(f,known,it=300):
    idx=ndimage.distance_transform_edt(~known,return_distances=False,return_indices=True); f=f[tuple(idx)].copy()
    for _ in range(it): f2=ndimage.uniform_filter(f,3); f[~known]=f2[~known]
    return f
ALPHA=np.load(D4+'themis_alpha.npy')   # exact no-data masks from the PNG tiles (zoom 3, plus zoom 4-5 under the empty block)
for n,src,al in [('tday','g_tday.jpg',ALPHA[1]),('tnight','g_tnight_fixed.png',ALPHA[0])]:
    a=np.array(Image.open(D4+src).convert('L')).astype(float)
    gap=cov&(~al|(a<=3))
    gap=ndimage.binary_dilation(gap,iterations=1)&cov
    m=cov&~gap
    vals=np.sort(a[m]); t=np.searchsorted(vals,a)/len(vals)
    t=np.where(gap,inpaint(t,~gap),t)
    out=ramp(t,INF); out[~cov]=G3[~cov]
    edge=(np.abs(LAT)>63)&cov; w=((np.abs(LAT)-63)/2)[edge][:,None]; out[edge]=out[edge]*(1-w)+G3[edge]*w
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(S+f'img/global_{n}.jpg',quality=85)
    print(n,'filled %.2f%% of the covered area'%(gap.sum()/cov.sum()*100))
