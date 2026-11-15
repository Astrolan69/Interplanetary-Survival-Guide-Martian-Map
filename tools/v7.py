import json, math, numpy as np
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from paths import ROOT, RAW, TOOLS
src=open(TOOLS+'/v6.py').read(); exec(src[:src.index("targets=")])
def find(lst,pre): return [s for s in lst if s['title'].startswith(pre)][0]
jobs={'curiosity':[('sulfur','Sulfate-bearing unit')],
      'spirit':[('sulfur','Arad'),('sulfur','Gusev plains'),('sites','Sulfate-rich soils')]}
for k,js in jobs.items():
    g=grids[k]; m=M[k]; lz=m['lander']
    for h in [s for s in m['sites'] if s['kind']=='hazard']:
        g.rn[g.dmap(h['lat'],h['lon'])<(h.get('zone',250)+50)]=1e6
    for lst,pre in js:
        t=find(m[lst],pre); r=g.route((lz['lat'],lz['lon']),(t['lat'],t['lon']),maxs=15); t['route']=r
        print(k,t['title'],r and {x:r[x] for x in r if x!='pts'})
json.dump(M,open(S+'data/missions.json','w'),separators=(',',':'))
