import datetime as dt
UTC=dt.timezone.utc; PDT=dt.timezone(dt.timedelta(hours=-7))
def T(s): return dt.datetime.strptime(s,'%Y%m%dT%H%M%S').replace(tzinfo=UTC)
# stage: (start, end, first_ordinal, n)
AB = lambda c: [  # campaign start list for alpha/beta
 ('decode_abs',c[1],c[2],0,10),('decode_abba_01_05',c[2],c[3],10,20),('decode_abba_06_10',c[3],c[4],30,20),
 ('prefill_abs',c[5],c[6],50,10),('prefill_abba_01_05',c[6],c[7],60,20),('prefill_abba_06_10',c[7],c[8],80,20)]
win={
 'alpha':AB([T(x) for x in ['20261010T002350','20261010T003131','20261010T005647','20261010T015106','20261010T024605','20261010T024912','20261010T031313','20261010T040153','20261010T045035']]),
 'beta':AB([T(x) for x in ['20261011T212025','20261011T212807','20261011T215310','20261011T224456','20261011T233543','20261011T234022','20261012T001013','20261012T010308','20261012T020040']]),
 'gamma':[('decode_01_05',T('20261012T053131'),T('20261012T062247'),0,20),('decode_06_10',T('20261012T062556'),T('20261012T071449'),20,20),
          ('prefill_01_05',T('20261012T071759'),T('20261012T081039'),40,20),('prefill_06_10',T('20261012T081348'),T('20261012T090356'),60,20)]}
def est(w,ordinal):
    for name,s,e,f,n in win[w]:
        if f<=ordinal<f+n:
            per=(e-s)/n
            return name,s+per*(ordinal-f+0.5),per.total_seconds()
flags=[('alpha','prefill 1.7B abba b07',84,87),('alpha','prefill 1.7B abba b10',96,99),('alpha','prefill 1.7B abs r08',57,57),
('beta','decode 8B abba b10',46,49),('beta','decode 8B abs r03',2,2),('beta','decode 8B abs r06',5,5),('beta','decode 8B abs r10',9,9),
('beta','prefill 8B abba b03',68,71),('beta','prefill 8B abba b07',84,87),('beta','prefill 8B abba b08',88,91),('beta','prefill 8B abba b09',92,95),
('gamma','decode b01-b1 (8B)',1,1),('gamma','decode b05-b1 (8B)',17,17),('gamma','prefill b04-a1 (1.7B)',52,52),('gamma','prefill b06-b2 (8B)',62,62),('gamma','prefill b09-b1 (8B)',73,73),('gamma','prefill b10-b1 (8B)',77,77)]
for w,lab,o1,o2 in flags:
    n,t,per=est(w,(o1+o2)/2)
    print(f'{w:6s} {lab:26s} ord {o1:3d}-{o2:3d} {n:20s} ~{t.strftime("%H:%M")}Z = {t.astimezone(PDT).strftime("%a %H:%M")} PDT (member cadence {per:.0f}s)')
for w in win:
    for name,s,e,f,n in win[w]:
        print(w,name,s.astimezone(PDT).strftime('%a %H:%M'),'-',e.astimezone(PDT).strftime('%H:%M'),f'{(e-s).total_seconds()/n:.0f}s/member')
