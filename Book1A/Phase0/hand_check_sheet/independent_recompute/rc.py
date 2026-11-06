# Independent recompute for the Book 1A hand-check sheet (written from the rule text, not the runner's code).
import gzip, os, math, pickle, struct, glob, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd
K=os.path.expanduser('~/mnt/k/Databento_BackTesting')
TAPES=K+'/tapes'; CACHE=os.path.expanduser('~/chk/cache'); os.makedirs(CACHE,exist_ok=True)
T=0.25; CT=ZoneInfo('America/Chicago'); UTC=ZoneInfo('UTC')
def rt(p): return round(p/T)*T          # half-even like C# Math.Round
def load_tape(d):  # d = date of file (UTC day); timestamps in the file are CT wall time
    f=f"{TAPES}/tape_{d:%Y%m%d}.csv.gz"; c=f"{CACHE}/t{d:%Y%m%d}.pkl"
    if os.path.exists(c): return pd.read_pickle(c)
    if not os.path.exists(f): return None
    x=pd.read_csv(f,header=None,names=['ts','px','bid','ask','sz','side'],usecols=[0,1,4,5])
    x['ts']=pd.to_datetime(x['ts'],format='%Y-%m-%d %H:%M:%S.%f')
    x=x[x.sz>0].reset_index(drop=True); x.to_pickle(c); return x
def ticks(a,b):  # CT naive datetimes, [a,b)
    out=[]; d=a.date()
    while d<=b.date()+dt.timedelta(days=1):
        x=load_tape(d)
        if x is not None: out.append(x[(x.ts>=a)&(x.ts<b)])
        d+=dt.timedelta(days=1)
    x=pd.concat(out).sort_values('ts',kind='stable').reset_index(drop=True); return x
def S(td):  # session start (17:00 CT of the previous calendar day; Monday -> Sunday)
    return dt.datetime.combine(td-dt.timedelta(days=1),dt.time(17))
def prev_td(td):
    d=td-dt.timedelta(days=1)
    while d.weekday()>=5: d-=dt.timedelta(days=1)
    return d
def at(td,h,m): return dt.datetime.combine(td,dt.time(h,m))
# ---- profiles
EPOCH=dt.datetime(2000,1,1)
def profile(x):
    key=np.rint(x.px.values/T).astype(np.int64)
    vol=pd.Series(x.sz.values).groupby(key).sum().to_dict()
    per=((x.ts-EPOCH).dt.total_seconds()//1800).astype(np.int64).values
    row=np.floor_divide(key,20)
    tp=pd.DataFrame({'r':row,'p':per}).drop_duplicates().groupby('r').size().to_dict()
    side=x.side.values; sz=x.sz.values
    d=np.where(side=='B',sz,np.where(side=='S',-sz,0))
    r5=pd.Series(sz).groupby(row).sum().to_dict(); d5=pd.Series(d).groupby(row).sum().to_dict()
    return dict(vol=vol,tpo=tp,hi=float(x.px.max()),lo=float(x.px.min()),r5=r5,d5=d5,n=len(x))
def va_rows(src,rowticks,pct=70):
    keys=sorted(src); mn,mx=keys[0],keys[-1]; n=mx-mn+1
    rows=[0.0]*n
    for k,v in src.items(): rows[k-mn]+=v
    tot=sum(rows); mid=(n-1)/2; poc=0
    for i in range(1,n):
        if rows[i]>rows[poc] or (rows[i]==rows[poc] and abs(i-mid)<abs(poc-mid)): poc=i
    tgt=tot*pct/100; lo=hi=poc; acc=rows[poc]
    while acc<tgt and (lo>0 or hi<n-1):
        up=rows[hi+1] if hi+1<n else -1; dn=rows[lo-1] if lo-1>=0 else -1
        if up>=dn: hi+=1; acc+=up
        else: lo-=1; acc+=dn
    span=(rowticks-1)*T
    return dict(poc=rt((mn+poc)*rowticks*T+span/2), vah=(mn+hi)*rowticks*T+span, val=(mn+lo)*rowticks*T)
def vva(p): return va_rows(p['vol'],1)
def tva(p): return va_rows(p['tpo'],20)
def rows5(p): return {k*5.0:v for k,v in p['r5'].items()}
def drows5(p): return {k*5.0:v for k,v in p['d5'].items()}
def map4(rows):
    pk=max(rows,key=lambda k:(rows[k],))  # peak row (first max by value; ties checked separately)
    ties=[k for k in rows if rows[k]==rows[pk]]
    thr=0.7*rows[pk]; lo=pk
    while lo-5 in rows and rows[lo-5]>=thr: lo-=5
    hi=pk+5
    while hi in rows and rows[hi]>=thr: hi+=5
    c=pk+2.5
    if hi-lo>40: lo,hi=c-20,c+20
    if hi-lo<10: lo,hi=c-5,c+5
    return dict(peak=pk,peak_ties=ties,lo=lo,hi=hi)
def dbands(rows):
    keys=sorted(k for k,v in rows.items() if v!=0)
    nt=max(1,math.ceil(0.2*len(keys))); thr=sorted((abs(rows[k]) for k in keys),reverse=True)[nt-1]
    top={k for k in keys if abs(rows[k])>=thr}; bands=[]; run=[]
    def fl(run):
        if len(run)>=2:
            lo,hi=run[0],run[-1]+5
            if hi-lo>40:
                w=8; b=max(range(len(run)-w+1),key=lambda s:sum(abs(rows[r]) for r in run[s:s+w])); lo,hi=run[b],run[b+w-1]+5
            bands.append([lo,hi,'SELL' if rows[run[0]]<0 else 'BUY'])
    for k in keys:
        if k in top and run and k==run[-1]+5 and (rows[k]>0)==(rows[run[-1]]>0): run.append(k)
        else:
            fl(run); run=[k] if k in top else []
    fl(run); m=[]
    for b in sorted(bands):
        if m and m[-1][2]==b[2] and b[0]<=m[-1][1]+5: m[-1][1]=max(m[-1][1],b[1])
        else: m.append(b)
    return m
def hvn_lvn(rows5d):  # rows keyed by 5-pt row lo
    keys=sorted(rows5d); mn=keys[0]; n=int((keys[-1]-mn)/5)+1
    raw=[rows5d.get(mn+5*i,0) for i in range(n)]
    s=[((raw[i-1] if i>0 else 0)+raw[i]+(raw[i+1] if i<n-1 else 0))/3 for i in range(n)]
    pk=max(s); hT=0.7*pk; lT=0.3*pk
    H=[i for i in range(n) if s[i]>=hT]
    def runs(a,b,test):
        out=[];st=None
        for i in range(a,b+2):
            inr=i<=b and test(s[i])
            if inr and st is None: st=i
            if not inr and st is not None: out.append((mn+5*st,mn+5*i-T,st,i-1)); st=None
        return out
    hv=runs(0,n-1,lambda v:v>=hT); lv=runs(H[0],H[-1],lambda v:v<=lT) if len(H)>1 and H[-1]>H[0] else []
    return dict(mn=mn,n=n,raw=raw,s=s,peak=pk,peak_row=mn+5*s.index(pk),hT=hT,lT=lT,hvn=hv,lvn=lv)
def single_prints(p,minrows=2):
    tp={k*5.0:v for k,v in p['tpo'].items()}; keys=sorted(tp); out=[];run=[]
    allk=[keys[0]+5*i for i in range(int((keys[-1]-keys[0])/5)+1)]
    for k in allk+[None]:
        if k is not None and tp.get(k,0)==1: run.append(k)
        else:
            if len(run)>=minrows: out.append((run[0],run[-1]+5-T))
            run=[]
    return out
def vwap(x):
    v=x.sz.sum(); pv=(x.px*x.sz).sum(); p2=(x.px*x.px*x.sz).sum(); m=pv/v; sd=math.sqrt(max(0,p2/v-m*m)); return m,m+sd,m-sd
def bars(x):  # 1-minute bars stamped at their END time (a tick at hh:mm:00.000 opens the bar ending hh:mm+1)
    e=x.ts.dt.floor('min')+pd.Timedelta(minutes=1)
    d=np.where(x.side=='B',x.sz,np.where(x.side=='S',-x.sz,0))
    g=pd.DataFrame({'e':e,'px':x.px,'sz':x.sz,'d':d}).groupby('e')
    b=pd.DataFrame({'o':g.px.first(),'h':g.px.max(),'l':g.px.min(),'c':g.px.last(),'v':g.sz.sum(),'d':g.d.sum()})
    return b
def accept(b,edge,level,other,price,asof):
    lo,hi=(level,other) if edge=='VAL' else (other,level)
    if lo<=price<=hi: return dict(state='INSIDE')
    out=price<level if edge=='VAL' else price>level
    if not out: return dict(state='INSIDE')
    u=b[b.index<=asof]; beyond=(u.c<level) if edge=='VAL' else (u.c>level)
    bv=beyond.values; k=len(bv)-1; first=None
    while k>=0 and bv[k]: first=k; k-=1
    if first is None: return dict(state='TESTING')
    since=u.iloc[first:]; bs=bv[first:]
    mins=int((asof-u.index[first]).total_seconds()//60); cs=bs.mean(); vs=since.v.values[bs].sum()/since.v.sum()
    acc=mins>=60 and cs>=0.8 and vs>=0.2
    return dict(state=(('ACCEPTED_BELOW' if edge=='VAL' else 'ACCEPTED_ABOVE') if acc else 'TESTING'),first=str(u.index[first]),first_close=float(u.c.iloc[first]),minutes=mins,closes=round(cs,4),vol=round(vs,4))
# ---- HTF composite from Databento ohlcv-1m (NQ.v.0), volume spread evenly over each minute's range
def htf_bars():
    c=CACHE+'/nq1m.pkl'
    if os.path.exists(c): return pd.read_pickle(c)
    import subprocess
    recs=[]
    files={}
    for f in sorted(glob.glob(K+'/raw/block1/nq_ohlcv_1m/*/*.ohlcv-1m.dbn.zst')): files[os.path.basename(f)[10:18]]=f
    for f in sorted(glob.glob(K+'/raw/block1/roll_NQ*_ohlcv_1m_202*/*/*.ohlcv-1m.dbn.zst')): files[os.path.basename(f)[10:18]]=f  # roll fix wins
    for d in sorted(files):
        f=files[d]
        b=subprocess.run(['zstd','-dc',f],capture_output=True).stdout
        assert b[:3]==b'DBN'; ml=struct.unpack('<I',b[4:8])[0]; o=8+ml
        while o<len(b):
            ln=b[o]*4; rtyp=b[o+1]
            if rtyp in (0x20,0x21,0x22,0x23,0x24) and ln==56:
                iid,ts=struct.unpack('<IQ',b[o+4:o+16]); op,hi,lo,cl,v=struct.unpack('<qqqqQ',b[o+16:o+56])
                recs.append((ts,iid,op/1e9,hi/1e9,lo/1e9,cl/1e9,v,rtyp))
            o+=ln
    x=pd.DataFrame(recs,columns=['ts','iid','o','h','l','c','v','rt'])
    x['start']=pd.to_datetime(x.ts,unit='ns',utc=True).dt.tz_convert(CT).dt.tz_localize(None)
    x['end']=x.start+pd.Timedelta(minutes=1); x.to_pickle(c); return x
def trading_date(ts):
    d=ts.date()
    if ts.time()>=dt.time(17): d+=dt.timedelta(days=1)
    while d.weekday()>=5: d+=dt.timedelta(days=1)
    return d
def htf(first_day,asof,want=60,minmin=None):
    # frozen definition: each minute's volume spread evenly over the 5-pt rows of its range; per trading day rows rounded;
    # the last `want` complete prior trading days (days with too few minutes skipped); today's partial session not used
    x=htf_bars(); x=x[(x.end<=asof)].copy(); x['td']=[trading_date(t) for t in x.start]
    D=trading_date(asof); x=x[x.td<D]
    cnt=x.groupby('td').size()
    HOL={dt.date(2025,9,1),dt.date(2025,11,27),dt.date(2025,12,25),dt.date(2026,1,1),dt.date(2026,1,19),dt.date(2026,2,16),dt.date(2026,4,3)}
    days=[d for d in sorted(cnt.index,reverse=True) if d not in HOL and (minmin is None or cnt[d]>=minmin)][:want]
    comp={}
    for d,g in x[x.td.isin(days)].groupby('td'):
        rows={}
        for h,l,v in zip(g.h.values,g.l.values,g.v.values):
            if v<=0 or h<l: continue
            r0=int(round(l/T))//20; r1=int(round(h/T))//20; sh=v/(r1-r0+1)
            for r in range(r0,r1+1): rows[r]=rows.get(r,0.0)+sh
        for r,v in rows.items(): comp[r]=comp.get(r,0)+int(round(v))
    va=va_rows(comp,20); va['days']=len(days); va['first']=str(min(days)); va['last']=str(max(days)); va['rows']=comp
    return va
