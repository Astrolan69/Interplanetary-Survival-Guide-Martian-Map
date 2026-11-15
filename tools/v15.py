# v15: three markers removed from the plan: the Jezero delta science stop, the Husband Hill
# lookout (Spirit) and the Gale boxwork science stop with its route.
import os, json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p=os.path.join(ROOT,'data','missions.json'); M=json.load(open(p))
DROP=('Delta mudstones & carbonates','Husband Hill','Boxwork ridges')
for m in M.values():
    n=len(m['sites']); m['sites']=[s for s in m['sites'] if not s['title'].startswith(DROP)]
    print(n,'->',len(m['sites']))
json.dump(M,open(p,'w'),separators=(',',':'))
