import json, math, numpy as np, sys
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from paths import ROOT, RAW, TOOLS
sys.path.insert(0,TOOLS)
src=open(TOOLS+'/v2b.py').read(); exec(src[:src.index('out={}')])
S=ROOT+'/'
G3=np.load(RAW+'/data3/grids3.npz')
M=json.load(open(S+'data/missions.json'))
def mk(key,z,sl,vis):
    if sl is None:
        dx,dy=META[key]['cell']; gy,gx=np.gradient(z,dy,dx); sl=np.degrees(np.arctan(np.hypot(gx,gy)))
    return Grid(key,z,sl,vis)
grids={'curiosity':mk('gale',G['zg'],G['gsl'],S+'img/gale_vis.jpg'),
       'spirit':mk('spirit',G['zs'],G['ssl'],S+'img/spirit_vis.jpg'),
       'perseverance':mk('jezero',G3['zj'],None,S+'img/jezero_vis.jpg')}
targets={'curiosity':'Bagnold dunes','spirit':'Paso Robles','perseverance':'Observation Mountain'}
for k,g in grids.items():
    m=M[k]; lz=m['lander']
    # block hazard zones (+50 m margin) by making them impassable: raise roughness to huge and flag
    for h in [s for s in m['sites'] if s['kind']=='hazard']:
        dm=g.dmap(h['lat'],h['lon']); g.rn[dm<(h.get('zone',250)+50)]=1e6
    t=[s for s in m['sulfur'] if s['title'].startswith(targets[k])][0]
    r=g.route((lz['lat'],lz['lon']),(t['lat'],t['lon']),maxs=15)
    print(k,t['title'],r and {x:r[x] for x in r if x!='pts'})
    t['route']=r
json.dump(M,open(S+'data/missions.json','w'),separators=(',',':'))
