# v14: no separate "resources (water)" marker type. The three sites that used it get the
# marker of what was actually found there.
import os, json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p=os.path.join(ROOT,'data','missions.json'); M=json.load(open(p))
NEW={'Water & sulfur feedstock':'sulfur',      # Gediz Vallis: pure sulfur field (Curiosity 2024)
     'Sulfate-rich soils':'sulfate',           # Gusev: Paso Robles / Tyrone sulfate soils (Spirit)
     'Delta mudstones & carbonates':'science'} # Jezero delta: Perseverance's main science target
for m in M.values():
    for s in m['sites']:
        for k,v in NEW.items():
            if s['title'].startswith(k): print(s['title'][:40],s['kind'],'->',v); s['kind']=v
json.dump(M,open(p,'w'),separators=(',',':'))
