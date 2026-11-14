import json, math, heapq, csv
import numpy as np
from PIL import Image
from scipy import ndimage
D='/home/claude/data2/'; D1='/home/claude/data/'; S='/home/claude/site2/'
R=3389500.0; DEG=math.pi/180*R
META=json.load(open(S+'data/meta.json')); G=np.load(D+'grids.npz')
def dist(a,b): # (lat,lon)
    p1,p2=math.radians(a[0]),math.radians(b[0]); dl=math.radians(b[1]-a[1]); dp=p2-p1
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2; return 2*R*math.asin(math.sqrt(h))
class Grid:
    def __init__(s,key,z,sl,vis):
        m=META[key]; s.b=m['bbox']; s.z=z; s.sl=sl; s.h,s.w=z.shape; s.dx,s.dy=m['cell']
        im=np.array(Image.open(vis).convert('L')).astype(float)
        hp=im-ndimage.gaussian_filter(im,3); r=np.sqrt(ndimage.gaussian_filter(hp**2,4))
        s.rough=np.array(Image.fromarray(r.astype(np.float32)).resize((s.w,s.h),Image.BOX)).astype(float)
        mean=np.array(Image.fromarray(im.astype(np.float32)).resize((s.w,s.h),Image.BOX)).astype(float)
        s.nod=ndimage.binary_dilation(mean<8,iterations=6)
        q5,q95=np.percentile(s.rough[~s.nod],5),np.percentile(s.rough[~s.nod],95)
        s.rn=np.clip((s.rough-q5)/(q95-q5+1e-9),0,1.5); s.rn[s.nod]=0.5
        yy,xx=np.mgrid[0:s.h,0:s.w]; s.lon=s.b[0]+(xx+.5)/s.w*(s.b[2]-s.b[0]); s.lat=s.b[3]-(yy+.5)/s.h*(s.b[3]-s.b[1])
    def ij(s,lat,lon): return int((s.b[3]-lat)/(s.b[3]-s.b[1])*s.h), int((lon-s.b[0])/(s.b[2]-s.b[0])*s.w)
    def ll(s,i,j): return (round(float(s.lat[i,j]),6),round(float(s.lon[i,j]),6))
    def dmap(s,lat,lon): return np.hypot((s.lat-lat)*DEG,(s.lon-lon)*DEG*math.cos(math.radians(lat)))
    def lander(s,targets,dmin,dmax,win_m=400,extra=None):
        k=max(3,int(win_m/s.dx)); ms=ndimage.uniform_filter(s.sl,k); mr=ndimage.uniform_filter(s.rough,k)
        rn=(mr-np.percentile(mr,5))/(np.percentile(mr,95)-np.percentile(mr,5)+1e-9)
        zn=(s.z-s.z.min())/(s.z.max()-s.z.min()+1e-9)
        score=ms/2+2.0*rn+0.6*zn
        dd=np.min([s.dmap(*t) for t in targets],axis=0)
        score=score+dd/4000.0
        score[(dd<dmin)|(np.max([s.dmap(*t) for t in targets],axis=0)>dmax)]=1e9
        if extra is not None: score[extra]=1e9
        score[s.nod]=1e9
        e=k; score[:e,:]=1e9; score[-e:,:]=1e9; score[:,:e]=1e9; score[:,-e:]=1e9
        i,j=np.unravel_index(np.argmin(score),score.shape)
        return dict(lat=float(s.lat[i,j]),lon=float(s.lon[i,j]),elev=round(float(s.z[i,j])),slope=round(float(ms[i,j]),1),rough_pct=int(100*(mr<=mr[i,j]).mean()))
    def route(s,a,b,maxs=15):
        si,sj=s.ij(*a); ti,tj=s.ij(*b); H,W=s.h,s.w; INF=1e18
        g=np.full((H,W),INF); prev=-np.ones((H,W),np.int64); g[si,sj]=0; pq=[(0,si,sj)]; tm=math.tan(math.radians(maxs))
        nb=[(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        while pq:
            c,i,j=heapq.heappop(pq)
            if c>g[i,j]: continue
            if (i,j)==(ti,tj): break
            for di,dj in nb:
                ni,nj=i+di,j+dj
                if ni<0 or nj<0 or ni>=H or nj>=W: continue
                d=math.hypot(di*s.dy,dj*s.dx); S_=(s.z[ni,nj]-s.z[i,j])/d
                if abs(S_)>tm and (ni,nj)!=(ti,tj): continue
                v=1.0*math.exp(-3.5*abs(S_+0.05))*(0.83)/(1+2.5*s.rn[ni,nj])
                nc=c+d/v
                if nc<g[ni,nj]: g[ni,nj]=nc; prev[ni,nj]=i*W+j; heapq.heappush(pq,(nc,ni,nj))
        if g[ti,tj]>=INF: return None
        path=[]; k=ti*W+tj
        while k!=-1: path.append(divmod(k,W)); k=prev[k//W,k%W] if (k//W,k%W)!=(si,sj) else -1
        path.append((si,sj)); path=path[::-1]
        pts=[s.ll(i,j) for i,j in path]; L=sum(dist(pts[k-1],pts[k]) for k in range(1,len(pts)))
        zz=[s.z[i,j] for i,j in path]; up=sum(max(0,zz[k]-zz[k-1]) for k in range(1,len(zz)))
        mx=max([math.degrees(math.atan(abs(zz[k]-zz[k-1])/max(1,dist(pts[k-1],pts[k])))) for k in range(1,len(pts))]+[0])
        step=max(1,len(pts)//150); pts=pts[::step]+[pts[-1]]
        return dict(pts=pts,km=round(L/1000,2),walk_h=round(g[ti,tj]/3600,2),rover_h=round(L/1000/8,2),climb=round(up),maxslope=round(mx,1))
out={}
# ---------------- GALE / Curiosity
w=json.load(open(D1+'mm_waypoints.json')); rows=w['rows']
def at(s): c=[r for r in rows if r[0]<=s]; return c[-1] if c else rows[0]
gg=Grid('gale',G['zg'],G['gsl'],S+'img/gale_vis.jpg')
ev=[(0,'Landing: Bradbury Landing','6 Aug 2012. Curiosity lands on the Aeolis Palus plain in Gale crater.'),
    (182,'Yellowknife Bay: ancient lake','Feb 2013. First drill sample (John Klein) shows an ancient freshwater lake environment that could have supported microbes.'),
    (753,'Pahrump Hills: base of Mount Sharp','Sep 2014. Arrival at the mountain; start of the climb through lake-deposited mudstone layers.'),
    (1802,'Vera Rubin ridge','Sep 2017. A hematite-rich ridge, studied for more than a year.'),
    (2290,'Glen Torridon: clay unit','Jan 2019. Clay-bearing layers seen from orbit; the best-preserved record of water.'),
    (4199,'Gediz Vallis: pure sulfur','30 May 2024. The rover crushes a rock and reveals elemental sulfur crystals, a first for Mars.'),
    (4563,'Boxwork region','2025. Mineral ridges 1–2 m tall left by groundwater; ridge and hollow drill samples.'),
    (5073,'Today: latest position','Last reported drive, sol 5073 (NASA MMGIS feed).')]
cur_events=[dict(sol=s,title=t,text=x,lat=at(s)[4],lon=at(s)[3]) for s,t,x in ev]
tr=json.load(open('/home/claude/site/data/mission.json'))['traverse']
box=at(4718); sul=at(4199)
k5=max(3,int(500/gg.dx)); msl=ndimage.uniform_filter(gg.sl,k5); m2=msl.copy(); m2[gg.dmap(box[4],box[3])>3000]=-1; m2[gg.nod]=-1
hi_,hj_=np.unravel_index(np.argmax(m2),m2.shape); hz=gg.ll(hi_,hj_); hzs=float(msl[hi_,hj_])
lz=gg.lander([(box[4],box[3]),(sul[4],sul[3])],2500,9000)
r1=gg.route((lz['lat'],lz['lon']),(sul[4],sul[3])); r2=gg.route((lz['lat'],lz['lon']),(box[4],box[3]))
out['curiosity']=dict(events=cur_events,traverse=[[p[1],p[0]] for p in tr],lander=lz,
 sites=[dict(kind='isru',title='Water & sulfur feedstock: Gediz Vallis sulfate unit',lat=sul[4],lon=sul[3],why='Curiosity found a field of pure elemental sulfur stones (2024) inside the hydrated sulfate layer of Mount Sharp. Hydrated sulfates release water when heated; sulfur is a raw material for sulfur concrete. My pick for the first ISRU (in-situ resource) pilot plant.',route=r1),
        dict(kind='science',title='Groundwater record: boxwork ridges',lat=box[4],lon=box[3],why='Ridge (clay) and hollow (carbonate) drill sites ~10 m apart record long-lived groundwater high on Mount Sharp. Best place for crew sampling: a one-day EVA covers what the rover needed months for.',route=r2),
        dict(kind='hazard',title='Steep Mount Sharp flank: avoid on foot',lat=hz[0],lon=hz[1],why=f'Steepest ~500 m patch within 3 km of the boxwork site: mean slope {hzs:.0f}° on the HiRISE DEM. Route crews along the valley floors Curiosity used.',route=None)])
# ---------------- INSIGHT
ii=Grid('insight',G['zi'],G['isl'],S+'img/insight_vis.jpg')
INS=(4.502384,135.623447)
lzi=ii.lander([INS],1200,3000)
ri=ii.route((lzi['lat'],lzi['lon']),INS,maxs=12)
out['insight']=dict(lander_hist=dict(lat=INS[0],lon=INS[1]),events=[
  dict(title='Landing in Elysium Planitia',text='26 Nov 2018. InSight lands on a flat, smooth, rock-poor plain, picked for its safety, low elevation and equatorial sunlight. The lander sits in a degraded ~27 m crater nicknamed "Homestead hollow".',lat=INS[0],lon=INS[1]),
  dict(title='Seismometer on the ground',text='Dec 2018. SEIS (CNES) is placed on the surface. Over four years it records more than 1,300 marsquakes; the largest is magnitude 4.7 (May 2022).',lat=INS[0],lon=INS[1]),
  dict(title='The "mole" stalls',text='2019–Jan 2021. The HP3 heat probe could not grip the unexpectedly cohesive, clumpy soil and only reached ~40 cm. Lesson for crews: plan powered excavation, not hammering.',lat=INS[0],lon=INS[1]),
  dict(title='Mars has a large liquid core',text='Seismic waves showed a liquid core with a diameter of roughly 3,600–3,700 km, plus the thickness of the crust and mantle.',lat=INS[0],lon=INS[1]),
  dict(title='End of mission',text='Dec 2022. Dust on the solar panels drained the power; NASA declared the mission over on 21 Dec 2022.',lat=INS[0],lon=INS[1])],
 lander=lzi,
 sites=[dict(kind='heritage',title='InSight lander: revisit and study hardware',lat=INS[0],lon=INS[1],why='Four-plus years of dust, UV and thermal cycling on solar panels, cables and seals: unique engineering data for crewed hardware design. Treat it as a heritage site and approach on foot only.',route=ri),
        dict(kind='isru',title='Regolith construction site',lat=round(lzi['lat']+0.004,5),lon=round(lzi['lon']+0.002,5),why='Very smooth plain (HiRISE) and a fine, cohesive regolith (as the mole showed). Good for bulldozing regolith berms over habitats as radiation shielding. Needs powered excavation because of the cemented duricrust.',route=None)])
# ---------------- SPIRIT
ss=Grid('spirit',G['zs'],G['ssl'],S+'img/spirit_vis.jpg')
rr=list(csv.DictReader(open(D1+'MERA_traverse.csv'))); k=59275.06
sp=[(int(x['START_SOL']),round(float(x['CORRECTED_Y'])/k,6),round(175.5+float(x['CORRECTED_X'])/k,6)) for x in rr]
def sat(sol): c=[p for p in sp if p[0]<=sol]; return c[-1]
spt=[]; [spt.append([p[1],p[2]]) for p in sp if not spt or spt[-1]!=[p[1],p[2]]]
sev=[(1,'Landing: Columbia Memorial Station','4 Jan 2004. Spirit lands on the basaltic plains of Gusev crater.'),
     (65,'Bonneville crater rim','Mar 2004. The ~200 m crater shows no lake sediments; the team turns east toward the hills.'),
     (156,'Arrival at the Columbia Hills','Jun 2004. After a ~3 km drive, Spirit starts climbing West Spur and Husband Hill.'),
     (690,'Comanche outcrop: carbonates','2005 (identified 2010). Carbonate-rich rocks form in wet, non-acidic water.'),
     (1150,'Home Plate: almost pure silica','2007. A dragging wheel exposes soil with up to ~90% silica, typical of hot springs or fumaroles. Strong evidence for a hydrothermal environment.'),
     (1892,'Troy: stuck in soft soil','1 May 2009. Wheels break through a crust into sulfate-rich sand. Spirit becomes a stationary station; last contact 22 Mar 2010.')]
spev=[dict(sol=s,title=t,text=x,lat=sat(s)[1],lon=sat(s)[2]) for s,t,x in sev]
hp=sat(1150); troy=sat(1892); comanche=sat(690)
troy_mask=ss.dmap(troy[1],troy[2])<400
lzs=ss.lander([(hp[1],hp[2])],1500,3500,extra=troy_mask)
rs=ss.route((lzs['lat'],lzs['lon']),(hp[1],hp[2]),maxs=15)
# winter power: north-facing slopes 8-20 deg near Home Plate
gy,gx=np.gradient(ss.z,ss.dy,ss.dx); north=(gy<0)  # z increases southward -> faces north
cand=(ss.sl>8)&(ss.sl<20)&north&(ss.dmap(hp[1],hp[2])<900)
ws=None
if cand.any():
    ci=np.argwhere(cand); dd=[ss.dmap(hp[1],hp[2])[i,j] for i,j in ci]; i,j=ci[int(np.argmin(dd))]; ws=ss.ll(i,j)
out['spirit']=dict(traverse=spt,events=spev,lander_hist=dict(lat=sp[0][1],lon=sp[0][2]),lander=lzs,
 sites=[dict(kind='science',title='Home Plate: hydrothermal silica',lat=hp[1],lon=hp[2],why='Ancient hot-spring or fumarole deposits are among the best places on Mars to look for preserved biosignatures. Top astrobiology target for a crew.',route=rs),
        dict(kind='hazard',title='Troy: soft sulfate sand, no-go zone',lat=troy[1],lon=troy[2],why='A thin crust over loose ferric-sulfate sand trapped Spirit for good. Keep crewed rovers out of the ~50 m bright-soil patch; the Spirit rover itself is a heritage site here.',route=None),
        dict(kind='isru',title='Sulfate-rich soils: water source',lat=round(troy[1]+0.0015,6),lon=round(troy[2]-0.002,6),why='The bright soils Spirit churned up near Home Plate are rich in hydrated sulfates. Low-temperature heating can release bound water. Excavate the margins, not the trap.',route=None)]+
       ([dict(kind='power',title='Winter power: north-facing slope',lat=ws[0],lon=ws[1],why='At ~14.6°S, Spirit survived winters by parking on north-tilted slopes facing the Sun (3rd winter on Home Plate\'s north edge). Selected from the DEM: a 8–20° north-facing slope next to Home Plate for solar arrays.',route=None)] if ws else [])+
       [dict(kind='comms',title='Husband Hill: lookout & relay mast',lat=sat(582)[1],lon=sat(582)[2],why='The highest point Spirit reached (summit, Aug 2005). Line of sight across the plains to the landing zone: a natural place for a comms relay and weather mast.',route=None)])
json.dump(out,open(S+'data/missions.json','w'),separators=(',',':'))
for k,v in out.items(): print(k, v['lander'], [ (s['title'][:25], s['route'] and (s['route']['km'],s['route']['walk_h'],s['route']['maxslope'])) for s in v['sites']])
