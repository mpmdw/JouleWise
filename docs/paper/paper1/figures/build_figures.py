# Generates the Paper 1 schematic figures (no measured data). Run from the repository root.
import os
out='docs/paper/paper1/figures'
CSS='''<style>
text{font-family:Helvetica,Arial,sans-serif;fill:#1a1a1a}
.t{font-size:15px;font-weight:bold}.s{font-size:12px}.xs{font-size:10.5px}.note{font-size:10.5px;font-style:italic;fill:#555}
.box{fill:#f2f4f7;stroke:#4a5568;stroke-width:1.2}.blue{fill:#dbe8f7;stroke:#2b6cb0;stroke-width:1.2}
.orange{fill:#fdebd3;stroke:#c05621;stroke-width:1.2}.green{fill:#dcf2e3;stroke:#2f855a;stroke-width:1.2}
.grey{fill:#e2e8f0;stroke:#4a5568;stroke-width:1}.red{fill:#fde2e2;stroke:#c53030;stroke-width:1.2}
.line{stroke:#1a1a1a;stroke-width:1.2;fill:none}.dash{stroke:#1a1a1a;stroke-width:1.2;stroke-dasharray:5 4;fill:none}
.arrow{stroke:#333;stroke-width:1.3;fill:none;marker-end:url(#ah)}
</style>
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker>
<pattern id="hatch" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#2b6cb0" stroke-width="2"/></pattern></defs>
'''
def svg(name,w,h,body,title):
    s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">\n<title>{title}</title>\n{CSS}<rect width="{w}" height="{h}" fill="#ffffff"/>\n{body}\n<text x="{w-10}" y="{h-8}" text-anchor="end" class="note">Schematic. No measured data; all values and widths illustrative, not to scale.</text>\n</svg>\n'
    open(os.path.join(out,name),'w').write(s)

def T(x,y,t,c='s',a='start'): return f'<text x="{x}" y="{y}" class="{c}" text-anchor="{a}">{t}</text>'
def R(x,y,w,h,c='box',rx=4): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="{c}" rx="{rx}"/>'
def L(x1,y1,x2,y2,c='line'): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{c}"/>'

# Fig 1 phase split
b=[T(20,26,'Phase split by time overlap, and the energy moved when an edge moves','t')]
x0,y0=80,300  # axis origin
b.append(L(x0,y0,860,y0)); b.append(L(x0,y0,x0,60))
b.append(T(880,y0+4,'time','s','end')); b.append(f'<text x="30" y="180" class="s" transform="rotate(-90 30 180)" text-anchor="middle">average power</text>')
recs=[(120,250,90,'record 1'),(250,380,170,'record 2'),(380,510,200,'record 3'),(510,640,150,'record 4'),(640,770,140,'record 5')]
for a,c,hgt,lab in recs:
    b.append(R(a,y0-hgt,c-a,hgt,'grey',0)); b.append(T((a+c)/2,y0+18,lab,'xs','middle'))
edge=430; g=40
b.append(f'<rect x="{edge-g}" y="{y0-200}" width="{g}" height="200" fill="url(#hatch)" opacity="0.8"/>')
b.append(L(edge,70,edge,y0)); b.append(L(edge-g,90,edge-g,y0,'dash'))
b.append(T(edge+6,84,'recorded edge (first output token)','xs')); b.append(T(edge-g-8,150,'edge moved by g','xs','end'))
b.append(T(250,60,'PREFILL','s','middle')); b.append(T(640,60,'DECODE','s','middle'))
b.append(f'<path d="M{edge-g} 118 L{edge} 118" class="arrow"/>'); b.append(T(edge-g/2,132,'g','xs','middle'))
b.append(R(560,330,320,64,'box')); b.append(T(570,350,'Each record shares its energy between phases','xs'))
b.append(T(570,366,'in proportion to its time overlap with each.','xs'))
b.append(T(570,382,'Hatched: energy reassigned if the edge moves by g.','xs'))
b.append(R(80,330,450,64,'box')); b.append(T(90,350,'Assigned prefill energy = sum over records of power × overlap.','xs'))
b.append(T(90,366,'Moving an edge moves energy between phases; the request','xs')); b.append(T(90,382,'total is unchanged. Power within a record is unknown.','xs'))
svg('fig_p1_phase_split.svg',900,420,'\n'.join(b),'Phase split by overlap, schematic')

# Fig 2 session shape
b=[T(20,26,'Shape of one measurement session (identical in every pack)','t')]
segs=[('settle',40,'box'),('opening\ncapture',70,'orange'),('reference\ncorpus (18)',110,'green'),('start\ntriplet',60,'green'),
      ('DECODE HALF',190,'blue'),('mid-\npoint',45,'green'),('PREFILL HALF',190,'blue'),('end\ntriplet',60,'green'),('closing\ncapture',70,'orange')]
x=20
for lab,w,c in segs:
    b.append(R(x,60,w,60,c,2))
    for i,ln in enumerate(lab.split('\n')): b.append(T(x+w/2,86+i*14,ln,'xs','middle'))
    x+=w+4
b.append(f'<path d="M20 140 L{x-4} 140" class="arrow"/>'); b.append(T(x-4,156,'time (about six hours)','xs','end'))
b.append(T(20,190,'Floor pack, each half:','s')); 
xx=180
for i in range(10): b.append(R(xx+i*16,176,13,18,'blue',1))
b.append(T(xx+10*16+6,190,'10 repeats','xs'))
xx=418
for q in range(10):
    for k,c in enumerate(['A','B','B','A']): b.append(R(xx+q*40+k*9,176,8,18,'orange' if c=='B' else 'blue',1))
b.append(T(xx+10*40+2,190,'10 null quads','xs'))
b.append(T(20,230,'Contrast pack, each half:','s'))
xx=180
for q in range(5):
    for k,c in enumerate(['1.7B','8B','8B','1.7B']): b.append(R(xx+q*44+k*10,216,9,18,'orange' if '8' in c and c!='1.7B' else 'blue',1))
b.append(R(xx+5*44+2,216,12,18,'green',1)); xx2=xx+5*44+20
for q in range(5):
    for k,c in enumerate(['1.7B','8B','8B','1.7B']): b.append(R(xx2+q*44+k*10,216,9,18,'orange' if c=='8B' else 'blue',1))
b.append(T(xx2+5*44+6,230,'5 + 5 contrast quads, one reference between','xs'))
b.append(R(20,260,860,52,'box')); b.append(T(30,280,'Calibration captures (orange) bound edge timing; reference runs (green) set the drift screen and allowance;','xs'))
b.append(T(30,296,'blue/orange squares are science runs (blue = side A, orange = side B). The midpoint reference separates the halves.','xs'))
svg('fig_p1_session_shape.svg',900,340,'\n'.join(b),'Session shape, schematic')

# Fig 3 session ledger (no outcomes)
b=[T(20,26,'Order of collection (registered rotation; outcomes are filled from harvest records)','t')]
cols=['round','1st','2nd','3rd','then']
xs=[20,140,320,500,680]
for c,x in zip(cols,xs): b.append(T(x,60,c,'s'))
rows=[('Primary block','1.7B floor','8B floor','contrast','re-arm a pack until claim-usable'),
      ('Replication 1','1.7B floor','8B floor','contrast','BYTES sub-packs'),
      ('Replication 2','8B floor','contrast','1.7B floor','BYTES sub-packs'),
      ('Replication 3','contrast','1.7B floor','8B floor','BYTES sub-packs'),
      ('Replication 4+','rotation continues, skipping packs at target','','','')]
for i,r in enumerate(rows):
    y=80+i*44
    b.append(T(20,y+22,r[0],'s'))
    for j in range(1,5):
        if r[j]:
            c='orange' if r[j]=='contrast' else ('green' if 'BYTES' in r[j] else ('box' if j==4 or 'rotation' in r[j] else 'blue'))
            w=170 if j<4 else 190
            if 'rotation' in r[j]: w=530
            b.append(R(xs[j],y,w,32,c)); b.append(T(xs[j]+8,y+15,r[j],'xs'))
            if j<4 and 'rotation' not in r[j]: b.append(T(xs[j]+8,y+28,'outcome: filled at release','xs'))
b.append(R(20,310,860,48,'box'))
b.append(T(30,328,'Each replication contrast session takes floors from the same round\'s counting floor sessions, else the next, else the previous,','xs'))
b.append(T(30,344,'else the primary block\'s. The replication block closes at 3 counting sessions per pack or at the end of 1 November 2026 (Pacific).','xs'))
svg('fig_p1_session_ledger.svg',900,380,'\n'.join(b),'Session ledger, schematic')

# Fig 4 BYTES design
b=[T(20,26,'BYTES: three rival lines fixed on the fit set, then tested on held-out models','t')]
# left panel axes
ox,oy=70,300
b.append(L(ox,oy,380,oy)); b.append(L(ox,oy,ox,60)); b.append(T(380,oy-6,'x = b, R or τ','xs','end'))
b.append(f'<text x="40" y="180" class="xs" transform="rotate(-90 40 180)" text-anchor="middle">energy per decode pass e</text>')
pts=[(110,250),(160,215),(230,170)]
for px,py in pts: b.append(f'<circle cx="{px}" cy="{py}" r="5" fill="#2b6cb0"/>'); b.append(L(px,py-10,px,py+10))
b.append(L(90,265,360,92)); b.append(L(90,258,360,102,'dash')); b.append(L(90,272,360,84,'dash'))
b.append(T(120,280,'fit set: 3 dense models','xs')); b.append(T(200,70,'committed line + corner lines','xs'))
b.append(f'<path d="M335 110 L335 75" class="line"/>'); 
b.append(R(310,96,50,24,'blue',2)); b.append(T(335,112,'pred.','xs','middle'))
b.append(R(320,140,30,30,'orange',2)); b.append(T(335,182,'measured','xs','middle'))
b.append(T(220,322,'Prediction interval at a held-out x vs the measured interval','xs','middle'))
# right panel decision
rx=430
b.append(R(rx,60,440,150,'box'))
b.append(T(rx+10,80,'For each held-out model and boundary (rails, DC input, rest):','s'))
for i,(w,d) in enumerate([('bytes / resident / time','exactly one line consistent'),('unresolved','two or more consistent (expected for dense models)'),('neither','no line consistent; log ratios show the misses')]):
    b.append(T(rx+20,104+i*22,w,'s')); b.append(T(rx+190,104+i*22,d,'xs'))
b.append(T(rx+10,180,'MoE models only: active / resident / mixed','s'))
b.append(T(rx+10,198,'H2: decode power vs bandwidth (and resident bytes per second)','xs'))
# stages
stg=['blinded:\nrails, fit set,\nreferences','stage 1:\nfit lines\ncomputed','commit\npredictions\n(SHA-256)','held-out\nagreement,\nstill blinded','stage 2:\nheld-out\nunblinded']
x=430
for i,sname in enumerate(stg):
    c='red' if i==2 else 'green'
    b.append(R(x,230,80,64,c,3))
    for k,ln in enumerate(sname.split('\n')): b.append(T(x+40,248+k*13,ln,'xs','middle'))
    if i<4: b.append(f'<path d="M{x+80} 262 L{x+90} 262" class="arrow"/>')
    x+=90
b.append(T(430,316,'Held-out rows stay withheld, with no clock times, until the commitment is recorded.','xs'))
svg('fig_p1_bytes_design.svg',900,350,'\n'.join(b),'BYTES design, schematic')

# Fig 5 pipeline
b=[T(20,26,'The research pipeline: who may touch what','t')]
b.append(R(20,50,280,300,'blue',6)); b.append(T(30,70,'CLOUD (agents)','s'))
for i,t in enumerate(['registrations, judged and refuted','code, executing reviews (2 families)','synthetic full-size tests, CI','independent recompute and twin (built)','paper text with placeholders']):
    b.append(R(35,84+i*50,250,38,'box')); b.append(T(45,107+i*50,t,'xs'))
b.append(R(330,50,260,300,'orange',6)); b.append(T(340,70,'MEASUREMENT LAPTOP (no agents)','s'))
for i,t in enumerate(['agent census + hazard arm','session (about 6 h)','harvest: flags, exclusions','structure only leaves','hash-verified packaging']):
    b.append(R(345,84+i*50,230,38,'box')); b.append(T(355,107+i*50,t,'xs'))
b.append(R(620,50,260,300,'green',6)); b.append(T(630,70,'ANALYSIS HOST (restricted)','s'))
for i,t in enumerate(['blind dry run: structure only','release event (digests tied)','registered analysis','independent recompute + compare','fill placeholders, print']):
    b.append(R(635,84+i*50,230,38,'box')); b.append(T(645,107+i*50,t,'xs'))
b.append(f'<path d="M285 103 L345 103" class="arrow"/>'); b.append(T(315,96,'sealed','xs','middle'))
b.append(f'<path d="M575 303 L635 103" class="arrow"/>'); b.append(T(605,190,'data','xs','middle'))
b.append(f'<path d="M575 253 C 600 380, 160 380, 160 340" class="arrow"/>'); b.append(T(400,372,'structure only (verdicts, counts)','xs','middle'))
svg('fig_p1_pipeline.svg',900,400,'\n'.join(b),'Research pipeline, schematic')
