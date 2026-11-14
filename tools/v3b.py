import json, math, numpy as np
src=open('tools/v2b.py').read(); exec(src[:src.index('out={}')])
D3='/home/claude/data3/'; G3=np.load(D3+'grids3.npz')
out=json.load(open(S+'data/missions.json'))
m=json.load(open(D3+'m20.json')); wp=m['wp']; hw=m['hw']
def at(s): c=[r for r in wp if r[0]<=s]; return c[-1] if c else wp[0]
def ll(r): return (r[2],r[1])
# simplify traverse
pts=[]
for sol,line in sorted(m['tr'],key=lambda t:t[0]):
    for c in line:
        p=[c[1],c[0]]
        if not pts or abs(pts[-1][0]-p[0])+abs(pts[-1][1]-p[1])>0.00004: pts.append(p)
ev=[(0,'Landing: Octavia E. Butler Landing','18 Feb 2021. Perseverance lands on the floor of Jezero crater, a 45 km basin that once held a lake fed by a river delta.'),
    (58,'Ingenuity: first powered flight on another planet','19 Apr 2021. The 1.8 kg helicopter lifts off from "Wright Brothers Field".','heli1'),
    (190,'First rock core: "Rochette"','Sep 2021. The first sample sealed for a possible return to Earth.'),
    (410,'Arrival at the delta front','Apr 2022. The rover reaches the layered sediments of the ancient river delta.'),
    (1036,'Ingenuity\'s last flight (#72)','Jan 2024. After 72 flights a damaged rotor ends the mission; the helicopter stays here as a weather and test station.','heli72'),
    (1215,'Cheyava Falls: potential biosignature','21 Jul 2024. Core "Sapphire Canyon" from a leopard-spotted mudstone in Neretva Vallis. Published Sep 2025 as the best candidate so far for signs of ancient microbial life.'),
    (1356,'Climbing out of the crater','Dec 2024. Perseverance climbs the crater rim to reach some of the oldest rocks it has seen.'),
    (2022,'Today: latest position','Last reported drive, sol 2022 (NASA MMGIS feed).')]
def evpos(e):
    if len(e)>3: h=[x for x in hw if x[0]==(1 if e[3]=='heli1' else 72)][0]; return (h[3],h[2])
    return ll(at(e[0]))
pev=[dict(sol=e[0],title=e[1],text=e[2],lat=evpos(e)[0],lon=evpos(e)[1]) for e in ev]
jg=Grid('jezero',G3['zj'],None,S+'img/jezero_vis.jpg') if False else None
# build slope for jezero grid
z=G3['zj']; dx,dy=META['jezero']['cell']; gy,gx=np.gradient(z,dy,dx); sl=np.degrees(np.arctan(np.hypot(gx,gy)))
jg=Grid('jezero',z,sl,S+'img/jezero_vis.jpg')
chey=evpos(ev[5]); delta=evpos(ev[3]); h72=evpos(ev[4])
lz=jg.lander([chey,delta],1500,7000)
r1=jg.route((lz['lat'],lz['lon']),chey,maxs=15); r2=jg.route((lz['lat'],lz['lon']),delta,maxs=15); r3=jg.route((lz['lat'],lz['lon']),h72,maxs=15)
k5=max(3,int(500/jg.dx)); msl=ndimage.uniform_filter(jg.sl,k5); m2=msl.copy(); m2[jg.nod]=-1; i,j=np.unravel_index(np.argmax(m2),m2.shape); hz=jg.ll(i,j)
out['perseverance']=dict(traverse=pts,events=pev,lander=lz,heli=[[h[3],h[2]] for h in hw],
 sites=[dict(kind='science',title='Cheyava Falls: return for the biosignature',lat=chey[0],lon=chey[1],why='The strongest candidate yet for signs of ancient life. A crew with a field lab can sample the whole outcrop and test it in-situ, instead of waiting for sample return.',route=r1),
        dict(kind='isru',title='Delta mudstones & carbonates: water source',lat=delta[0],lon=delta[1],why='Clay- and carbonate-bearing delta sediments hold bound water. Close to a flat crater floor for a processing plant. My second pick after Utopia ice for water.',route=r2),
        dict(kind='heritage',title='Ingenuity: first Mars aircraft',lat=h72[0],lon=h72[1],why='Heritage site: the first aircraft on another world. Inspect the blades and electronics to learn how they fail after years of cold, dust and UV. Valuable for future crewed drones.',route=r3),
        dict(kind='hazard',title='Steepest slopes in view: crater rim / delta scarp',lat=hz[0],lon=hz[1],why=f'Steepest ~500 m patch on the DEM (mean {float(msl[i,j]):.0f}°). Route crews around delta scarps and the rim.',route=None)])
# ---------- Viking 2
VK=(47.6735,134.2993)
z=G3['zv']; dx,dy=META['viking2']['cell']; gy,gx=np.gradient(z,dy,dx); sl=np.degrees(np.arctan(np.hypot(gx,gy)))
vg=Grid('viking2',z,sl,S+'img/viking2_vis.jpg')
lzv=vg.lander([VK],1000,3000)
rv=vg.route((lzv['lat'],lzv['lon']),VK,maxs=12)
out['viking2']=dict(events=[
  dict(title='Landing in Utopia Planitia',text='3 Sep 1976. Viking Lander 2 touches down on a boulder-strewn plain at ~48°N, west of Mie crater. The second successful US landing on Mars.',lat=VK[0],lon=VK[1]),
  dict(title='Searching for life',text='1976–77. Biology experiments test soil for metabolism. The results stay debated to this day; the organic-molecule experiment found none at the time.',lat=VK[0],lon=VK[1]),
  dict(title='Frost on the ground',text='Winters 1977–79. Lander cameras image thin coatings of water-ice frost on the surface: direct evidence of water at this latitude.',lat=VK[0],lon=VK[1]),
  dict(title='Located from orbit',text='2006. HiRISE finds the ~3 m lander plus heat shield and backshell. The polygonal ground around it may be due to deep subsurface ice.',lat=VK[0],lon=VK[1]),
  dict(title='End of mission',text='Apr 1980. Battery failure ends 3.5 years of surface operations.',lat=VK[0],lon=VK[1])],
 lander_hist=dict(lat=VK[0],lon=VK[1]),lander=lzv,
 sites=[dict(kind='heritage',title='Viking Lander 2: 50-year hardware study',lat=VK[0],lon=VK[1],why='Nearly 50 years of exposure: the longest natural test of materials on Mars. Approach on foot only; position from the Mars Trek bookmark (approximate).',route=rv),
        dict(kind='isru',title='Polygonal ground: shallow-ice drilling test',lat=round(lzv['lat']-0.006,5),lon=round(lzv['lon']+0.008,5),why='Polygon-cracked ground at 48°N is typical of ice-cemented soil. First target for an ice drill next to the lander: low walk distance, flat terrain.',route=None)])
json.dump(out,open(S+'data/missions.json','w'),separators=(',',':'))
for k in ['perseverance','viking2']: print(k,out[k]['lander'],[(s['title'][:22],s['route'] and (s['route']['km'],s['route']['walk_h'])) for s in out[k]['sites']])
