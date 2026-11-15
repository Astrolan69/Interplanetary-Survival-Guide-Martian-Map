import json,glob,re,sys,os,base64,gzip
# Rebuilds files that were downloaded in base64 chunks marked @@<tag><n>@@ ... @@E@@.
# usage: python3 tools/assemble.py <tag> <out-dir> <folder-with-chunk-files>
tag=sys.argv[1]; out=sys.argv[2]; src_dir=sys.argv[3]
parts={}
for f in glob.glob(os.path.join(src_dir,'**','*'),recursive=True):
    if not os.path.isfile(f): continue
    try: t=open(f).read()
    except: continue
    if '@@'+tag not in t: continue
    try:
        d=json.loads(t); s=''.join(x.get('text','') for x in d)
    except Exception: s=t
    try: s=json.loads(s) if s.startswith('"') else s
    except Exception: pass
    for m in re.finditer(r'@@'+tag+r'(\d+)@@(.*?)@@E@@',s,re.S):
        parts[int(m.group(1))]=m.group(2)
print('parts',sorted(parts))
blob=''.join(parts[i] for i in sorted(parts)).replace('\\"','"')
o=json.loads(blob)
os.makedirs(out,exist_ok=True)
for k,v in o.items():
    b=base64.b64decode(v)
    if k.endswith('.gz'): b=gzip.decompress(b); k=k[:-3]
    open(os.path.join(out,k),'wb').write(b); print(k,len(b))
