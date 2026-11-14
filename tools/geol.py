import json,numpy as np
from PIL import Image,ImageDraw
g=json.load(open('/home/claude/data5/geology.json'))
units=[r['v'] for r in g['renderer']]
col={r['v']:r['c'][:3] for r in g['renderer']}
lab={r['v']:r['l'] for r in g['renderer']}
W,H=4096,2048
idx=np.zeros((H,W),np.uint8)  # 0 = none, else unit index+1
info={}
for f in g['features']:
    a=f['a']; u=a['Unit']
    if u not in units: continue
    k=units.index(u)+1
    info.setdefault(u,{'name':a['UnitDesc'],'group':a['UnitGroup'],'char':a['PrimaryCharacteristics'],'interp':a['Interpretation'],'c':'#%02x%02x%02x'%tuple(col[u])})
    pts=[[( (x+180)/360*W, (90-y)/180*H) for x,y in r] for r in f['r'] if len(r)>2]
    if not pts: continue
    xs=[p[0] for r in pts for p in r]; ys=[p[1] for r in pts for p in r]
    x0,x1=int(max(0,min(xs)-1)),int(min(W,max(xs)+2)); y0,y1=int(max(0,min(ys)-1)),int(min(H,max(ys)+2))
    if x1<=x0 or y1<=y0: continue
    m=np.zeros((y1-y0,x1-x0),bool)
    for r in pts:
        im=Image.new('1',(x1-x0,y1-y0),0); ImageDraw.Draw(im).polygon([(x-x0,y-y0) for x,y in r],fill=1)
        m^=np.array(im)
    sub=idx[y0:y1,x0:x1]; sub[m]=k
# fill gaps (0) with nearest neighbour
from scipy import ndimage
z=idx==0
if z.any():
    _,(iy,ix)=ndimage.distance_transform_edt(z,return_indices=True); idx=idx[iy,ix]
print('zero px',z.sum())
pal=np.array([[0,0,0]]+[col[u] for u in units],np.uint8)
rgb=pal[idx]
Image.fromarray(rgb).save('/home/claude/site2/img/global_geol.png',optimize=True)
Image.fromarray(rgb).save('/home/claude/site2/img/global_geol.jpg',quality=88)
# hover index grid 2048x1024
small=idx[::2,::2]
Image.fromarray(small).save('/home/claude/site2/data/geol_idx.png',optimize=True)
json.dump({'units':[dict(code=u,**info.get(u,{'name':lab[u],'c':'#%02x%02x%02x'%tuple(col[u])})) for u in units]},open('/home/claude/site2/data/geology.json','w'),ensure_ascii=False)
# legend: units present near mission sites
for name,(lat,lon) in {'curiosity':(-4.59,137.44),'spirit':(-14.57,175.47),'perseverance':(18.44,77.45)}.items():
    y=int((90-lat)/180*H); x=int((lon+180)/360*W); print(name,units[idx[y,x]-1],lab[units[idx[y,x]-1]])
