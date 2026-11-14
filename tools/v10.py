# v10: no-go slope areas in two classes (15-25 deg and >25 deg), vector outlines only.
import json, numpy as np
src=open('/home/claude/tools/v9.py').read()
exec(src[:src.index('HZ={}')])
HZ=json.load(open(S+'data/hazards.json'))
for mk,k in K.items():
    z,sl,m=load(k); b=m['bbox']
    HZ[mk].pop('nogo',None)
    HZ[mk]['nogo15']=rings((sl>15)&(sl<=25),b,minpx=2,tol=0.5)
    HZ[mk]['nogo25']=rings(sl>25,b,minpx=2,tol=0.5)
    print(mk,'15-25 %.1f%%'%(((sl>15)&(sl<=25)).mean()*100),len(HZ[mk]['nogo15']),'| >25 %.1f%%'%((sl>25).mean()*100),len(HZ[mk]['nogo25']))
json.dump(HZ,open(S+'data/hazards.json','w'),separators=(',',':'))
import os; print('KB',os.path.getsize(S+'data/hazards.json')//1024)
