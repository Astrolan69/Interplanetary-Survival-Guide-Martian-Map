import json,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
g=json.load(open('data5/geology.json'))
units=[r['v'] for r in g['renderer']];col={r['v']:r['c'][:3] for r in g['renderer']}
x0g,y0g,x1g,y1g=70,-20,180,52; ppd=36
W,H=(x1g-x0g)*ppd,(y1g-y0g)*ppd
idx=np.zeros((H,W),np.uint8)
for f in g['features']:
    u=f['a']['Unit']
    if u not in units: continue
    k=units.index(u)+1
    pts=[[((x-x0g)*ppd,(y1g-y)*ppd) for x,y in r] for r in f['r'] if len(r)>2]
    xs=[p[0] for r in pts for p in r]; ys=[p[1] for r in pts for p in r]
    if not xs or max(xs)<0 or min(xs)>W or max(ys)<0 or min(ys)>H: continue
    bx0,bx1=int(max(0,min(xs)-1)),int(min(W,max(xs)+2)); by0,by1=int(max(0,min(ys)-1)),int(min(H,max(ys)+2))
    m=np.zeros((by1-by0,bx1-bx0),bool)
    for r in pts:
        im=Image.new('1',(bx1-bx0,by1-by0),0);ImageDraw.Draw(im).polygon([(x-bx0,y-by0) for x,y in r],fill=1);m^=np.array(im)
    idx[by0:by1,bx0:bx1][m]=k
z=idx==0
if z.any():
    _,(iy,ix)=ndimage.distance_transform_edt(z,return_indices=True);idx=idx[iy,ix]
pal=np.array([[0,0,0]]+[col[u] for u in units],np.uint8)
Image.fromarray(pal[idx]).save('site2/img/overview_geol.png',optimize=True)
Image.fromarray(idx).save('site2/data/geol_idx_ov.png',optimize=True)
print(W,H,z.sum())
for n,(la,lo) in {'gale':(-4.7,137.4),'spirit':(-14.58,175.5),'jez':(18.45,77.35)}.items():
    print(n,units[idx[int((y1g-la)*ppd),int((lo-x0g)*ppd)]-1])
