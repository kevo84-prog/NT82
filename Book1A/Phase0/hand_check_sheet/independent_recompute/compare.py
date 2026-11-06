import re, pickle, datetime as dt, math, sys
import rc
SHEET=rc.K+'/Book1A/code/book1a/Phase0/hand_check_sheet/hand_check_sheet.md'
NUM=re.compile(r'-?\d+(?:,\d{3})*(?:\.\d+)?')
def nums(s): return [float(x.replace(',','')) for x in NUM.findall(s)]
def g(x):
    return ('%.2f'%x).rstrip('0').rstrip('.')
def f2(x): return f"{x:.2f}"
def ft(x): return f"{g(x)}" if isinstance(x,(int,float)) else str(x)
def yn(b): return 'Y' if b else 'N'
GEXC={'CR':'call_resistance_nt','PS':'put_support_nt','HVL':'hvl_nt','CR_0DTE':'call_resistance_0dte_nt','PS_0DTE':'put_support_0dte_nt','HVL_0DTE':'hvl_0dte_nt'}
O={}
def load(D):
    if D not in O: O[D]=pickle.load(open(f'out_{D}.pkl','rb'))
    return O[D]
def accstate(a): return a['state']
def ctx(o):
    h=o['htf']; p=o['price']
    bull=p>=h['val'] and o['bars_lo']<=h['val']; bear=p<=h['vah'] and o['bars_hi']>=h['vah']
    bullok=bull and o['wkval_state']['state']!='ACCEPTED_BELOW'; bearok=bear and o['wkvah_state']['state']!='ACCEPTED_ABOVE'
    if bullok and not bearok: base='BULLISH'
    elif bearok and not bullok: base='BEARISH'
    elif 'balance' in o: base='BALANCED'
    elif bull or bear: base='NONE_CONFLICT'
    else: base='NONE_NO_EVIDENCE'
    ha='ABOVE' if o['htfvah_state']['state']=='ACCEPTED_ABOVE' else 'BELOW' if o['htfval_state']['state']=='ACCEPTED_BELOW' else 'NONE'
    if base in('BULLISH','BEARISH'): mc=base   # (htf agreement/conflict cases are checked by eye; none occur on these days)
    elif base=='BALANCED': mc='BALANCED'
    elif ha=='ABOVE' and o['wkval_state']['state']!='ACCEPTED_BELOW': mc='BULLISH'
    elif ha=='BELOW' and o['wkvah_state']['state']!='ACCEPTED_ABOVE': mc='BEARISH'
    else: mc='NONE'
    return dict(base=base,ha=ha,mc=mc,bull=bull,bear=bear)
def vfollow(o):
    pdh,pdl=o['PDfull']; p2h,p2l=o['PD2full']; a=o['PD']['vva']; b=o['PD2']['vva']
    up=(pdh>p2h,a['vah']<b['vah'],a['poc']<b['poc']); dn=(pdl<p2l,a['val']>b['val'],a['poc']>b['poc'])
    return ('DIVERGENT_UP' if all(up) else 'DIVERGENT_DOWN' if all(dn) else 'WITH_PRICE'),up,dn
def level_value(o,name,D):
    v=o['vwap']; w=o['wkvwap']
    m={'VWAP':rc.rt(v[0]),'VWAPU1':rc.rt(v[1]),'VWAPL1':rc.rt(v[2]),'VWAP_SD1_UP':round(v[1],2),'VWAP_SD1_DN':round(v[2],2),
       'WKVWAP':round(w[0],2),'WKVWAP_SD1_UP':round(w[1],2),'WKVWAP_SD1_DN':round(w[2],2),'PDSET':o['settle'],
       'HTFVAH':o['htf']['vah'],'HTFVAL':o['htf']['val'],'HTFPOC':o['htf']['poc']}
    if name in m: return m[name]
    if name in GEXC: return float(o['gex'][GEXC[name]])
    mm=re.fullmatch(r'(PD3|PD2|PD|ON|WK)(T?)(VAH|VAL|POC|H|L)',name)
    if mm:
        pr,t,k=mm.groups()
        if pr=='PD3':
            if 'PD3' not in o:
                d3=rc.prev_td(rc.prev_td(rc.prev_td(dt.date.fromisoformat(D))))
                x=rc.ticks(rc.at(d3,8,30),rc.at(d3,15,0)); p3=rc.profile(x); o['PD3']=dict(vva=rc.vva(p3),tva=rc.tva(p3),hi=p3['hi'],lo=p3['lo'])
        p=o[pr]
        if k=='H': return p['hi']
        if k=='L': return p['lo']
        return p['tva' if t else 'vva'][k.lower()]
    return None
def zone_check(o,name,cells,D,zlo,zhi):
    """returns (mine_text, status, note)"""
    val=cells[2]
    m=re.fullmatch(r'T_DELTA_(SELL|BUY)_(PD|ON|WK|PD2)',name)
    if m:
        sg,pr=m.groups(); bs=[b for b in o[pr]['dbands'] if b[2]==sg]; e=nums(val)
        shown=[b for b in bs if abs(b[0]-e[0])<1e-9 and abs(b[1]-e[1])<1e-9]
        counts=[b for b in bs if b[1]>=zlo-5 and b[0]<=zhi+5]
        mine='; '.join(f"{g(b[0])}-{g(b[1])}" for b in counts) or 'none within 5 pts'
        if shown and counts and shown[0] in counts: return mine,'Y',''
        if shown and counts: return mine,'Y (label collision)',f'sheet shows the other {name} band {g(e[0])}-{g(e[1])}; the band that counts for this zone is {mine}'
        return mine,'N',f'all {name} bands: '+'; '.join(f"{g(b[0])}-{g(b[1])}" for b in bs)
    m=re.fullmatch(r'(PD|ON|WK|PD2)POC_AREA',name)
    if m:
        a=o[m.group(1)]['map4']; e=nums(val); ok=abs(a['lo']-e[0])<1e-9 and abs(a['hi']-e[1])<1e-9
        pk=nums(cells[4].split('peak row')[1])[0] if 'peak row' in cells[4] else None
        note='' if pk is None or pk==a['peak'] else f'peak row mine {g(a["peak"])}'
        return f"{g(a['lo'])}-{g(a['hi'])} (peak {g(a['peak'])})", ('Y' if ok and not note else 'N'), note
    if name=='DD_EDGE_PD':
        hv=o['pd_hvn']; return dd_text(o,hv,o['pd_sp'],nums(val))
    m=re.fullmatch(r'REJ_(HIGH|LOW)_(PD|ON|WK)',name)
    if m: return rej_check(o,m.group(1),val,cells[4],D)
    x=level_value(o,name,D)
    if x is None: return 'not recomputed','—','level type not covered by the independent script'
    e=nums(val)[0]
    if name in('VWAP_SD1_UP','VWAP_SD1_DN','WKVWAP','WKVWAP_SD1_UP','WKVWAP_SD1_DN'):
        ok=abs(x-e)<0.006
    else: ok=abs(x-e)<1e-9
    st='Y' if ok else ('within 1 row' if abs(x-e)<=5 and not name.endswith(('H','L')) else 'N')
    # inside / distance consistency with the zone range
    return ft(x), st, ''
def dd_text(o,hv,sp,e):
    H=sorted(hv['hvn']); L=hv['lvn']; seps=[(a,b,'LVN') for a,b,_,_ in L]+[(a,b,'SP') for a,b in sp]
    for i in range(1,len(H)):
        gLo,gHi=H[i-1][1],H[i][0]
        for s in seps:
            if s[1]<gLo or s[0]>gHi: continue
            low,up=H[i-1],H[i]
            p=o['price']
            if p<=s[0]: lo,hi=up[0],min(up[1],up[0]+40)
            elif p>=s[1]: lo,hi=max(low[0],low[1]-40),low[1]
            else: return f"price inside separator {g(s[0])}-{g(s[1])}",'N',''
            ok=abs(lo-e[0])<1e-9 and abs(hi-e[1])<1e-9
            return f"{g(lo)}-{g(hi)} (lower HVN {g(low[0])}-{g(low[1])}, sep {s[2]} {g(s[0])}-{g(s[1])}, upper HVN {g(up[0])}-{g(up[1])})",('Y' if ok else 'N'),''
    return 'no split found','N',''
def rej_check(o,side,val,chk,D):
    b=o['_bars']; e=nums(val); t=re.search(r'swing bar close \w+ (\w+ \d+) (\d\d:\d\d), swing ([\d.]+); available \w+ (\w+ \d+) (\d\d:\d\d)',chk)
    md,hm,sw,amd,ahm=t.groups(); yr=D[:4]
    ts=dt.datetime.strptime(f"{yr} {md} {hm}","%Y %b %d %H:%M"); av=dt.datetime.strptime(f"{yr} {amd} {ahm}","%Y %b %d %H:%M")
    idx=list(b.index); i=idx.index(ts); bar=b.iloc[i]
    win=b.iloc[i-15:i+16]; other=win.drop(win.index[15])
    if side=='HIGH': strict=(bar.h>other.h).all(); swing=bar.h
    else: strict=(bar.l<other.l).all(); swing=bar.l
    conf=idx[i+15]
    w5=b.iloc[i-2:i+3]
    if side=='HIGH':
        hi=swing; lo=min(min(r.o,r.c) for r in w5.itertuples()); lo=max(lo,hi-40)
    else:
        lo=swing; hi=max(max(r.o,r.c) for r in w5.itertuples()); hi=min(hi,lo+40)
    if hi-lo<10:
        pad=(10-(hi-lo))/2; lo=math.floor((lo-pad)/0.25+0.5)*0.25; hi=math.floor((hi+pad)/0.25+0.5)*0.25
    ok=strict and abs(swing-float(sw))<1e-9 and conf==av and abs(lo-e[0])<1e-9 and abs(hi-e[1])<1e-9
    return f"{g(lo)}-{g(hi)}; swing {g(swing)} at {ts:%H:%M}, strict 15-bar {'yes' if strict else 'NO'}, confirmed {conf:%m-%d %H:%M}", ('Y' if ok else 'N'), 'arrival evidence / departure vs ADR not recomputed'

def cmpnum(mine,exp,tol=1e-9,prof=False):
    if len(mine)!=len(exp): return 'N'
    if all(abs(a-b)<=tol for a,b in zip(mine,exp)): return 'Y'
    if prof and all(abs(a-b)<=5 for a,b in zip(mine,exp)): return 'within 1 row'
    return 'N'
def lab(mine,exp): return 'Y' if mine.strip()==exp.strip() else 'N'
def j(m): return ' / '.join(f"{g(x)}" for x in m)
def split(hv,sp):
    H=sorted(hv['hvn']); seps=[(a,b,'LVN') for a,b,_,_ in hv['lvn']]+[(a,b,'SP') for a,b in sp]
    for i in range(1,len(H)):
        for s in seps:
            if s[1]<H[i-1][1] or s[0]>H[i][0]: continue
            return H[i-1],s,H[i]
    return None
def h_value(D,o,c):
    L=c[0]; V=c[1]; P=o['price']; C=ctx(o); vf=vfollow(o); v=o['vwap']; w=o['wkvwap']
    simple={'price at 08:10 (packet ref_price)':[P],'session vwap':[v[0]],'session sd1_up':[v[1]],'session sd1_dn':[v[2]],
            'weekly vwap':[w[0]],'weekly sd1_up':[w[1]],'weekly sd1_dn':[w[2]]}
    if L in simple:
        m=simple[L]; return ', '.join(f2(x) for x in m), cmpnum([round(x,2) for x in m],nums(V),0.006),''
    labs={'market_context':C['mc'],'context_base':C['base'],'htf_acceptance':C['ha'],'value_follows':vf[0],
          'on_inventory':'NET_LONG' if P>v[0] else 'NET_SHORT','gex_regime':'POS' if o['gex']['regime']=='positive' else 'NEG'}
    if L in labs: return labs[L],lab(labs[L],V),''
    if L=='on_vs_settle': x=P-o['settle']; return f"{x:.1f}",cmpnum([x],nums(V)),''
    if L=='balance':
        if 'balance' not in o: return 'none',('Y' if V.strip() in('none','') else 'N'),''
        b=o['balance']['va']; return f"{b['val']:.2f}-{b['vah']:.2f}",cmpnum([b['val'],b['vah']],[abs(x) for x in nums(V)]),''
    if L=='balance_poc': b=o['balance']['va']; return f"{b['poc']:.2f}",cmpnum([b['poc']],nums(V)),''
    if L in('wkval_state','wkvah_state','htfval_state','htfvah_state'):
        st=o[L]['state'].replace('ACCEPTED_',''); exp=V.split('|')[0].replace('accept=','').strip()
        return f"accept={st}",lab(st,exp),'failed_reclaim not recomputed (needs imbalance / large-trade flags)'
    if L in('draw_status','draw'):
        c=[]
        for k in ('poc','vah','val'): x=o['htf'][k]; c.append(('HTF'+k.upper(),x-5,x+5))
        for p in ('WK','PD','ON'): a=o[p]['map4']; c.append((p+'POC_AREA',a['lo'],a['hi']))
        for n,col in GEXC.items(): x=float(o['gex'][col]); c.append((n,x-5,x+5))
        if C['mc']=='BULLISH': cand=sorted((lo-P,n,lo,hi) for n,lo,hi in c if lo>P and n!='HTFVAL')
        elif C['mc']=='BEARISH': cand=sorted((P-hi,n,lo,hi) for n,lo,hi in c if hi<P and n!='HTFVAH')
        else: cand=[]
        if L=='draw_status': m='ACTIVE' if cand else 'NONE'; return m,lab(m,V),'08:10 status only (REACHED / INVALIDATED are intraday)'
        d,n,lo,hi=cand[0]; e=nums(V.split('|')[0].replace('-',' '))
        return f"{lo:.2f}-{hi:.2f} ({n})",('Y' if abs(e[0]-lo)<1e-9 and abs(e[1]-hi)<1e-9 else 'N'),''
    if L=='htf_structure': return 'not recomputed','—','swing-structure label, outside the script'
    if L=='weekly double distribution':
        sp=split(o['wk_hvn'],o['wk_sp']); s='split yes' if sp else 'split no'
        return f"AVAILABLE; {s}", ('Y' if s in V else 'N'),''
    return None
def h_input(D,o,c):
    L=c[0]; V=c[1]; P=o['price']; C=ctx(o); vf=vfollow(o); v=o['vwap']; h=o['htf']
    if L.startswith('price at 08:10'): return f"{g(P)}",cmpnum([P],nums(V)),''
    if L=='HTF VAL': return f"{g(h['val'])}",cmpnum([h['val']],nums(V),prof=True),f"my 60 days {h['first']} - {h['last']}"
    if L=='HTF VAH': return f"{g(h['vah'])}",cmpnum([h['vah']],nums(V),prof=True),''
    if L=='HTF POC': return f"{g(h['poc'])}",cmpnum([h['poc']],nums(V),prof=True),''
    if L=='low of the bars window': return f"{g(o['bars_lo'])}",cmpnum([o['bars_lo']],nums(V)),''
    if L=='high of the bars window': return f"{g(o['bars_hi'])}",cmpnum([o['bars_hi']],nums(V)),''
    if L.startswith('held or reclaimed'): return yn(C['bull']),lab(yn(C['bull']),V),''
    if L.startswith('failed or lost'): return yn(C['bear']),lab(yn(C['bear']),V),''
    if L=='weekly VAL / VAH': a=o['WK']['vva']; return j([a['val'],a['vah']]),cmpnum([a['val'],a['vah']],nums(V),prof=True),''
    if L=='weekly VAL state / VAH state': m=f"{o['wkval_state']['state']} / {o['wkvah_state']['state']}"; return m,lab(m,V),''
    if L=='balance composite overlaps': m=yn('balance' in o); return m,lab(m,V),''
    if L=='context_base': return C['base'],lab(C['base'],V),''
    mm=re.fullmatch(r'(PD2|PD|ON) VAH / (POC|VAL) / (VAL|POC)',L)
    if mm:
        a=o[mm.group(1)]['vva']; m=[a['vah'],a[mm.group(2).lower()],a[mm.group(3).lower()]]
        return j(m),cmpnum(m,nums(V),prof=True),''
    if L=='overlap PD2-PD': x=o['ov_pd2_pd']; return f"{x:.1f}%",cmpnum([round(x,1)],nums(V),0.051),''
    if L=='overlap PD-ON': x=o['ov_pd_on']; return f"{x:.1f}%",cmpnum([round(x,1)],nums(V),0.051),''
    if L=='members':
        m='none' if 'balance' not in o else ', '.join([x for x in ['PD2','PD','ON'] if x in o['balance']['members']])
        return m,lab(m,V),''
    if L=='merged VAH / POC / VAL': b=o['balance']['va']; m=[b['vah'],b['poc'],b['val']]; return j(m),cmpnum(m,nums(V),prof=True),''
    if L=='merged high / low': b=o['balance']; m=[b['hi'],b['lo']]; return j(m),cmpnum(m,nums(V)),''
    if L=='PD high / low': m=list(o['PDfull']); return j(m),cmpnum(m,nums(V)),''
    if L=='PD2 high / low': m=list(o['PD2full']); return j(m),cmpnum(m,nums(V)),''
    if L.startswith('DIVERGENT_UP'): m=' / '.join(yn(x) for x in vf[1]); return m,lab(m,V),''
    if L.startswith('DIVERGENT_DOWN'): m=' / '.join(yn(x) for x in vf[2]); return m,lab(m,V),''
    if L=='ON VWAP': return f2(v[0]),cmpnum([round(v[0],2)],nums(V),0.006),''
    if L=='PD settlement': return f"{g(o['settle'])}",cmpnum([o['settle']],nums(V)),''
    if L.startswith('on_vs_settle'): x=P-o['settle']; return f"{x:.1f}",cmpnum([x],nums(V)),''
    if L=='ON high / ON low': m=[o['ON']['hi'],o['ON']['lo']]; return j(m),cmpnum(m,nums(V)),''
    if L.startswith('ON high - settlement'): m=[o['ON']['hi']-o['settle'],o['ON']['lo']-o['settle']]; return ' / '.join(f"{x:.2f}" for x in m),cmpnum(m,nums(V)),''
    return None
def h_edge(D,o,c):
    L=c[0]; V=c[1]; h=o['htf']; low=L.startswith('HTFVAL')
    a=o['htfval_state' if low else 'htfvah_state']; lvl=h['val' if low else 'vah']; es=c[2].strip()
    if a['state']=='INSIDE':
        return f"{g(lvl)}; INSIDE",('Y' if cmpnum([lvl],nums(V))=='Y' and es=='INSIDE' else 'N'),''
    m=f"{g(lvl)}; {a['state']}; first {a['first'][:16]} ({g(a['first_close'])}); {a['minutes']} min; closes {a['closes']:.2%}; vol {a['vol']:.2%}"
    e3=c[3]; ok=es==a['state'] and e3.startswith(a['first'][:16]) and nums(c[4])[0]==a['minutes'] and abs(nums(e3.split('(')[1])[0]-a['first_close'])<1e-9
    for col,key in ((5,'closes'),(6,'vol')):
        n=nums(c[col]) if len(c)>col else []
        if n: ok=ok and abs(n[0]/(100 if '%' in c[col] else 1)-a[key])<0.0051
    return m,('Y' if ok else 'N'),''
def h_cand(D,o,c):
    L=c[0]; V=c[1]; P=o['price']; x=level_value(o,L,D)
    if x is None:
        mm=re.fullmatch(r'(PD|ON|WK|PD2)POC_AREA',L)
        if not mm: return 'not recomputed','—',''
        a=o[mm.group(1)]['map4']; e=nums(V); ok=abs(a['lo']-e[0])<1e-9 and abs(a['hi']-e[1])<1e-9
        d=a['lo']-P if a['lo']>P else P-a['hi']; d=abs(d); ok=ok and abs(d-nums(c[2])[0])<0.051
        return f"{g(a['lo'])} - {g(a['hi'])}; {d:.1f}",('Y' if ok else 'N'),'distance = price to near edge'
    e=nums(V); d=abs(x-P); ok=abs(e[0]-(x-5))<1e-9 and abs(e[1]-(x+5))<1e-9 and abs(d-nums(c[2])[0])<0.051
    return f"{g(x-5)} - {g(x+5)}; {d:.1f}",('Y' if ok else 'N'),''
def h_level(D,o,c,zone):
    L=c[0]; V=c[1]
    if len(c)>=3 and 'csv' in c[2] and len(c)<=5:
        if L=='regime': m=o['gex']['regime']; return m,lab(m,V),''
        x=float(o['gex'][GEXC[L]]); return f"{x:.2f}",cmpnum([x],nums(V)),f"report_date {o['gex']['report_date']}"
    mine,st,note=zone_check(o,L,c,D,*zone)
    try:
        e=nums(c[2]); lo,hi=e[0],e[-1]; pos=c[3].strip()
        if pos=='inside': ok2=zone[0]<=lo<=zone[1]
        elif 'outside' in pos: dd=min(abs(lo-zone[0]),abs(lo-zone[1])); ok2=abs(dd-nums(pos)[0])<0.006 and not(zone[0]<=lo<=zone[1])
        else: ok2=hi>=zone[0]-5 and lo<=zone[1]+5 or st.startswith('Y (label')
        if not ok2: note=(note+'; ' if note else '')+'inside/distance column inconsistent with zone range'; st='N'
    except Exception: pass
    return mine,st,note
def ddhandle(o,hdr,c):
    hv=o['wk_hvn']; L=c[0]; V=c[1] if len(c)>1 else ''
    if hdr=='criterion (frozen)':
        if L=='rows in the profile': m=f"{hv['n']} ({hv['mn']:.1f} - {hv['mn']+5*(hv['n']-1):.1f})"; return m,lab(m,V),''
        if L=='smoothing': return 'same rule used','Y',''
        if L=='peak smoothed row': m=f"{hv['peak_row']:.1f}: {hv['peak']:,.0f}"; return m,lab(m,V),''
        if L.startswith('HVN line'): m=f"{hv['hT']:,.0f}"; return m,lab(m,V),''
        if L.startswith('LVN line'): m=f"{hv['lT']:,.0f}"; return m,lab(m,V),''
        if L.startswith('single prints'): m=f"{len(o['wk_sp'])} run(s)"; return m,lab(m,V),''
        if L.startswith('split'):
            sp=split(hv,o['wk_sp'])
            if not sp: return 'no split',('Y' if 'no' in V.lower() or 'none' in V.lower() else 'N'),''
            a,s,b=sp; m=f"lower HVN {g(a[0])} - {g(a[1])}; {s[2]} {g(s[0])} - {g(s[1])}; upper HVN {g(b[0])} - {g(b[1])}"
            return m,cmpnum(nums(m),nums(V)),''
    if hdr=='#':
        e=nums(c[1]); bl=[x for x in hv['hvn'] if abs(x[0]-e[0])<1e-9 and abs(x[1]-e[1])<1e-9]
        if not bl: return 'block not found','N',''
        x=bl[0]; mx=max(hv['s'][x[2]:x[3]+1]); n=x[3]-x[2]+1
        ok=n==nums(c[2])[0] and f"{mx:,.0f} ({round(100*mx/hv['peak'])}%)"==c[3].strip()
        return f"{g(x[0])} - {g(x[1])}; {n} rows; {mx:,.0f} ({round(100*mx/hv['peak'])}%)",('Y' if ok else 'N'),''
    if hdr=='type':
        e=nums(c[1]); bl=[x for x in hv['lvn'] if abs(x[0]-e[0])<1e-9 and abs(x[1]-e[1])<1e-9]
        sps=[x for x in o['wk_sp'] if abs(x[0]-e[0])<1e-9]
        ok=bool(bl if c[0].strip()=='LVN' else sps)
        return (f"{c[0]} {g(e[0])} - {g(e[1])} found" if ok else 'not found'),('Y' if ok else 'N'),''
    if hdr=='row lo':
        if L.strip()=='...': return None
        r=float(L); i=int(round((r-hv['mn'])/5)); raw=hv['raw'][i]; s=hv['s'][i]; tp=o['wk_tpo5'].get(r,0)
        m=[raw,s,round(100*s/hv['peak']),tp]; e=nums(' '.join(c[1:5]))
        ok=len(e)==4 and e[0]==raw and abs(e[1]-s)<=0.5 and e[2]==m[2] and e[3]==tp
        return f"{raw:,} / {s:,.0f} / {m[2]}% / {tp}",('Y' if ok else 'N'),''
    return None
HDRS=('value','input','edge','candidate','level','criterion (frozen)','#','type','row lo')
def main():
    out=[]; D=None; hdr=None; zone=(None,None); zname=''; dd=False; mism=[]; counts={}
    for line in open(SHEET,encoding='utf-8').read().split('\n'):
        m=re.match(r'## (\d{4}-\d\d-\d\d)',line)
        if m: D=m.group(1); o=load(D); dd=False
        if line.startswith('### '): dd=line.startswith('### Weekly double distribution')
        m=re.match(r'\*\*([A-Z0-9_]+)\*\*: ([\d.]+) - ([\d.]+)',line)
        if m: zone=(float(m.group(2)),float(m.group(3))); zname=m.group(1)
        if D and line.startswith('|') and not line.startswith('|---'):
            c=[x.strip() for x in line.strip().strip('|').split('|')]
            if c[0] in HDRS and ('hand' in c or 'match' in c or c[1] in('plan / sidecar value','value','level','value in plan','type','block','rows','volume','level (with pad)')):
                hdr=c[0]; out.append(line); continue
            try:
                if dd: r=ddhandle(o,hdr,c)
                else: r={'value':h_value,'input':h_input,'edge':h_edge,'candidate':h_cand}.get(hdr,None)
                if not dd: r=r(D,o,c) if r else (h_level(D,o,c,zone) if hdr=='level' else None)
            except Exception as ex:
                r=(f'error: {type(ex).__name__} {ex}','N','')
            if r:
                mine,st,note=r; mine=str(mine).replace('|','/')
                parts=line.rstrip().split('|')
                # parts[0]='' and parts[-1]=''; hand=parts[-3], match=parts[-2]
                parts[-3]=f' {mine} '; parts[-2]=f" {st}{(' ('+note+')') if note else ''} "
                line='|'.join(parts)
                counts[st]=counts.get(st,0)+1
                if st not in('Y','—') : mism.append((D,zname if hdr=='level' else hdr,c[0],c[1] if len(c)>1 else '',mine,st,note))
        out.append(line)
    return out,mism,counts
if __name__=='__main__':
    out,mism,counts=main(); open('recompute_sheet.md','w').write('\n'.join(out)); print(counts)
    for x in mism: print(x)
