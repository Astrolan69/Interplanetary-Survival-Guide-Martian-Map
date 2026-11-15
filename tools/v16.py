# v16: Jezero: Ingenuity site removed; safest routes added from the crew lander to the two
# visible sulfate deposits (Hogwallow Flats and Yori Pass / Hidden Harbor). Same rules as
# every other route (v8/v9/v13): least-time walk on the DEM, no cell steeper than 15 deg,
# 50 m away from hazard zones, back_h = the same path walked back.
import os, json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
HERE=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(HERE,'v13.py')).read()
exec(src[:src.index("M=json.load(open(S+'data/missions.json'))")])   # helpers, G, path_cells, back_hours
M=json.load(open(S+'data/missions.json')); HZ=json.load(open(S+'data/hazards.json'))
P=M['perseverance']
P['sites']=[s for s in P['sites'] if not s['title'].startswith('Ingenuity')]
g=G('jezero'); b=META['jezero']['bbox']
mask=Image.new('L',(g.w,g.h),0); dr=ImageDraw.Draw(mask)
for h in HZ['perseverance']['hazards']:
    for ring in h['rings']:
        dr.polygon([((lo-b[0])/(b[2]-b[0])*g.w,(b[3]-la)/(b[3]-b[1])*g.h) for la,lo in ring],fill=1)
g.block|=ndimage.binary_dilation(np.array(mask)>0,iterations=max(1,round(50/g.dx)))
L_=P['lander']
for s in P['sulfur']:
    if s['title'].startswith(('Hogwallow','Yori')):
        r,path=path_cells(g,(L_['lat'],L_['lon']),(s['lat'],s['lon']))
        r['back_h']=back_hours(g,path); s['route']=r
        print(s['title'][:40],'km',r['km'],'out',r['walk_h'],'back',r['back_h'],'climb',r['climb'],'max',r['maxslope'])
json.dump(M,open(S+'data/missions.json','w'),separators=(',',':'))
