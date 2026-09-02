import csv, sys
from decimal import Decimal
from collections import defaultdict
p="runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv"
rows=list(csv.DictReader(open(p)))
groups=defaultdict(list)
for r in rows: groups[r["timestamp_s"]].append(r)
print("rows",len(rows),"records",len(groups))
bad=[t for t,g in groups.items() if len(g)!=3 or sorted(x["rail"] for x in g)!=["ane_power","cpu_power","gpu_power"] or len({(x["interval_start_s"],x["interval_end_s"]) for x in g})!=1]
print("records not exactly {cpu,gpu,ane} with identical interval:",len(bad))
maxdec=max(len(r["timestamp_s"].split(".")[1]) for r in rows); print("max decimals in timestamp_s",maxdec)
def q7(xs,f):
    xs=sorted(xs); n=len(xs); h=(n-1)*f; i=int(h); 
    return xs[i]+(h-i)*(xs[min(i+1,n-1)]-xs[i])
def stats(xs): return [round(q7(xs,f)*1000,6) for f in (0.25,0.5,0.75)]
w_rows=[float(r["interval_end_s"])-float(r["interval_start_s"]) for r in rows]
w_rec=[float(g[0]["interval_end_s"])-float(g[0]["interval_start_s"]) for g in groups.values()]
print("float64 rows(1218) q1/med/q3 ms",stats(w_rows),"iqr",round(stats(w_rows)[2]-stats(w_rows)[0],6))
print("float64 recs(406)  q1/med/q3 ms",stats(w_rec),"iqr",round(stats(w_rec)[2]-stats(w_rec)[0],6))
d_rec=[Decimal(g[0]["interval_end_s"])-Decimal(g[0]["interval_start_s"]) for g in groups.values()]
def q7d(xs,f):
    xs=sorted(xs); n=len(xs); h=Decimal(n-1)*Decimal(f); i=int(h)
    return xs[i]+(h-i)*(xs[min(i+1,n-1)]-xs[i])
sd=[q7d(d_rec,Decimal(f))*1000 for f in ("0.25","0.5","0.75")]
print("Decimal recs(406) q1/med/q3 ms",[str(x) for x in sd],"iqr",str(sd[2]-sd[0]))
# float64 error bound: ulp at 1.78e9
import math; print("ulp(1.78e9) s =",math.ulp(1.78e9),"=> ms",math.ulp(1.78e9)*1000)
ts=sorted(float(t) for t in groups); d=[b-a for a,b in zip(ts,ts[1:])]
print("DG-075 float64 405 q1/med/q3 ms",stats(d))
print("widths[1:] == diffs?", all(abs(a-b)<1e-9 for a,b in zip(w_rec[1:],d)), "n",len(d))
print("min width ms",min(w_rec)*1000,"count<112.5ms",sum(1 for x in w_rec if x*1000<112.5),"in band 111.8-112.5",sum(1 for x in w_rec if 111.8<=x*1000<=112.5))
# tiling check: interval_start_s of record k vs timestamp_s of record k-1 (text compare)
ks=list(groups); mism=[i for i in range(1,len(ks)) if groups[ks[i]][0]["interval_start_s"]!=ks[i-1]]
print("records whose interval_start_s != previous timestamp_s:",len(mism),"max gap us",max(abs(float(groups[ks[i]][0]["interval_start_s"])-float(ks[i-1]))*1e6 for i in mism) if mism else 0)
print("interval_end_s == timestamp_s for all records:", all(g[0]["interval_end_s"]==t for t,g in groups.items()))
