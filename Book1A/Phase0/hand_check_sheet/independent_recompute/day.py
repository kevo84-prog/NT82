import sys, json, datetime as dt, rc, pandas as pd
def compute(D, bars_from, htf_first):
    A=rc.at(D,8,10); PD=rc.prev_td(D); PD2=rc.prev_td(PD)
    mon=D-dt.timedelta(days=D.weekday()); W0=rc.S(mon)
    allx=rc.ticks(min(rc.S(PD2),W0,bars_from),A)
    def win(a,b): return allx[(allx.ts>=a)&(allx.ts<b)]
    out={}
    b=rc.bars(win(bars_from,A)); out['price']=float(b.c.iloc[-1]); out['last_bar']=str(b.index[-1])
    out['bars_hi']=float(b.h.max()); out['bars_lo']=float(b.l.min())
    on=win(rc.S(D),A); wk=win(W0,A)
    out['vwap']=rc.vwap(on); out['wkvwap']=rc.vwap(wk)
    P={}
    for nm,(a,bb) in {'PD2':(rc.at(PD2,8,30),rc.at(PD2,15,0)),'PD':(rc.at(PD,8,30),rc.at(PD,15,0)),'ON':(rc.S(D),A),'WK':(W0,A)}.items():
        p=rc.profile(win(a,bb)); P[nm]=p
        out[nm]=dict(vva=rc.vva(p),tva=rc.tva(p),hi=p['hi'],lo=p['lo'],map4=rc.map4(rc.rows5(p)),dbands=rc.dbands(rc.drows5(p)))
    for nm,d in {'PDfull':PD,'PD2full':PD2}.items():
        x=win(rc.S(d),rc.at(d,16,0)); out[nm]=(float(x.px.max()),float(x.px.min()))
    st=win(rc.at(PD,15,0)-dt.timedelta(seconds=30),rc.at(PD,15,0)); out['settle']=rc.rt((st.px*st.sz).sum()/st.sz.sum())
    # balance
    def ov(a,c):
        o=min(a['vah'],c['vah'])-max(a['val'],c['val']); w=max(rc.T,min(a['vah']-a['val'],c['vah']-c['val'])); return 0 if o<=0 else min(100,100*o/w)
    o1=ov(out['PD2']['vva'],out['PD']['vva']); o2=ov(out['PD']['vva'],out['ON']['vva']); out['ov_pd2_pd']=o1; out['ov_pd_on']=o2
    if o2>0:
        mem=['PD','ON']+(['PD2'] if o1>0 else []); vol={}
        for m in mem:
            for k,v in P[m]['vol'].items(): vol[k]=vol.get(k,0)+v
        out['balance']=dict(members=mem,va=rc.va_rows(vol,1),hi=max(P[m]['hi'] for m in mem),lo=min(P[m]['lo'] for m in mem))
    # weekly acceptance, weekly DD inputs
    wv=out['WK']['vva']; pr=out['price']
    out['wkval_state']=rc.accept(b,'VAL',wv['val'],wv['vah'],pr,A); out['wkvah_state']=rc.accept(b,'VAH',wv['vah'],wv['val'],pr,A)
    out['wk_hvn']=rc.hvn_lvn(rc.rows5(P['WK'])); out['wk_sp']=rc.single_prints(P['WK']); out['wk_tpo5']={k*5.0:v for k,v in P['WK']['tpo'].items()}
    out['pd_hvn']=rc.hvn_lvn(rc.rows5(P['PD'])); out['pd_sp']=rc.single_prints(P['PD'])
    h=rc.htf(htf_first,A,60,900); out['htf']=h
    out['htfval_state']=rc.accept(b,'VAL',h['val'],h['vah'],pr,A); out['htfvah_state']=rc.accept(b,'VAH',h['vah'],h['val'],pr,A)
    g=pd.read_csv(rc.K+'/gex_levels_block1.csv'); g=g[g.session==str(D)].iloc[0]
    out['gex']={c:g[c] for c in ['call_resistance_nt','put_support_nt','hvl_nt','call_resistance_0dte_nt','put_support_0dte_nt','hvl_0dte_nt','regime','report_date']}
    out['_bars']=b; out['_P']=P
    return out
if __name__=='__main__':
    import pickle
    D=dt.date.fromisoformat(sys.argv[1]); bf=dt.datetime.fromisoformat(sys.argv[2]); hf=dt.date.fromisoformat(sys.argv[3])
    o=compute(D,bf,hf); pickle.dump(o,open(f'out_{D}.pkl','wb'))
    for k,v in o.items():
        if k.startswith('_') or k in('wk_hvn','pd_hvn','wk_tpo5'): continue
        print(k,v)
