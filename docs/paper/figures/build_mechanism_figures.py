#!/usr/bin/env python3
"""Regenerate the paper-M SVG mechanisms from the repository root.

Run reproduce_worked_examples.py first to refresh the registered data sidecar.
Figures A3–A5 are synthetic; Figure A6 uses historical pulse-9 inputs.
"""
from pathlib import Path
from html import escape
import json
F=Path('docs/paper/figures')
def begin(title,w=1000,h=500):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><rect width="100%" height="100%" fill="white"/>',f'<g font-family="sans-serif" fill="#20252b">']
def t(s,x,y,label,size=15,color=None): s.append(f'<text x="{x}" y="{y}" font-size="{size}"'+(f' fill="{color}"' if color else '')+'>'+escape(label)+'</text>')
def line(s,x,y,a,b,color='#58616c',dash=''): s.append(f'<line x1="{x}" y1="{y}" x2="{a}" y2="{b}" stroke="{color}" stroke-width="2"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def rect(s,x,y,w,h,color,stroke='#58616c'): s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="{stroke}"/>')
def save(s,name): (F/name).write_text('\n'.join(s+['</g></svg>'])+'\n')
s=begin('Figure 1. Boundary movement reallocates assigned energy',1000,530)
t(s,35,32,'Figure 1. A boundary shift within one 30-W record transfers 0.30 J',21)
t(s,35,58,'SYNTHETIC: power levels and times are illustrative; no physical phase-power shape is inferred.')
x=lambda v:100+(v-1)*6000;y=lambda v:350-v*7
for v in [0,10,20,30]:line(s,100,y(v),700,y(v),'#e2e6ea');t(s,64,y(v)+5,str(v),13)
rect(s,100,140,600,210,'#e7ebef')
# area is exactly 0.010 s wide, full 30 W high
rect(s,x(1.040),140,60,210,'#c4def3','#1b6ca8')
for yy in range(145,346,12):line(s,x(1.04),yy,x(1.05),yy-5,'#1b6ca8')
line(s,x(1.04),115,x(1.04),370,'#222');line(s,x(1.05),115,x(1.05),370,'#1b6ca8','5 4')
line(s,100,350,710,350);line(s,100,350,100,110)
t(s,100,95,'Power (W)');t(s,735,155,'Assigned-energy slice',16)
t(s,735,180,'0.010 s × 30 W',17);t(s,735,205,'= 0.30 J',20)
t(s,735,240,'Full record-average height,',14);t(s,735,260,'not a power-step difference.',14)
for v in [1,1.04,1.05,1.1]:line(s,x(v),350,x(v),359);t(s,x(v)-20,387 if v==1.05 else 374,f'{v:.3f}',13)
t(s,245,414,'Time (s); one record spans [1.000, 1.100]')
t(s,35,454,'Solid line: recorded boundary 1.040 s → prefill 1.20 J; decode 1.80 J.')
t(s,35,479,'Dashed line: moved boundary 1.050 s → prefill 1.50 J; decode 1.50 J.')
t(s,35,507,'The request total remains 3.00 J. Blue hatching is the energy reassigned under held averages.')
save(s,'fig1_boundary_attribution.svg')
# Existing diagrams: repair claims and title numbers without changing empirical marks.
p=F/'fig2_window_timeline.svg';a=p.read_text().replace('Figure 2.', 'Figure A2.').replace('not cancel this way. It is bounded by the whole-window','not cancel this way. References sample selected times;').replace('drift allowance, tracked by the reference runs above.','their allowance cannot bound any rise and fall between.');p.write_text(a)
p=F/'fig5_phase_record_overlap.svg';a=p.read_text().replace('Figure 5.','Figure 3.').replace('Figure 4.','Figure 3.');p.write_text(a)
p=F/'fig3_decision_gates.svg';a=p.read_text().replace('Figure 3.', 'Figure P1.').replace('no result of any kind','no authorized comparison result').replace('font-size="12.5" fill="#333333" text-anchor="middle">no authorized','font-size="11.5" fill="#333333" text-anchor="middle">no authorized').replace('does the whole uncertainty','do both intervals point the').replace('interval point one way?','registered way AND Holm pass?').replace('y="310" font-family="sans-serif" font-size="13"','y="310" font-family="sans-serif" font-size="11.5"').replace('interval does not settle direction,','interval or Holm does not pass,').replace('Gate two asks whether the whole uncertainty interval points one way','Gate two asks whether both intervals point the registered way and the Holm-adjusted test passes');p.write_text(a)
# Convex endpoint enumeration diagram with all four numerical corners.
s=begin('Figure A3. Block endpoint enumeration',1000,410)
t(s,30,32,'Figure A3. SYNTHETIC: form block intervals, then enumerate their corners',20)
t(s,30,64,'Member limits → δ lower = (B1L + B2L − A1U − A2U)/2; δ upper reverses limits.')
rect(s,50,112,260,140,'#f0f3f6');t(s,70,144,'Inputs: n = 2 block intervals',16);t(s,70,175,'δ1 ∈ [−1, 1] J; δ2 ∈ [1, 3] J');t(s,70,209,'Four choices = 2², not 2⁸');line(s,315,181,365,181)
rect(s,370,100,330,178,'#eef6fc');t(s,390,128,'Corners → complete bound (J)',16)
for j,label in enumerate(['(−1, 1) → 22.007438','(−1, 3) → 45.014875  MAXIMUM','(  1, 1) →   1.000000','(  1, 3) → 24.007438']):t(s,390,159+j*29,label)
line(s,707,181,750,181);t(s,760,150,'At every corner:',16);t(s,760,180,'mean, SD, largest |δ|');t(s,760,210,'t = 12.706; √(1+1/2)')
t(s,30,321,'The formula is convex: absolute linear means + a norm of centered differences; maxima preserve convexity.')
t(s,30,350,'A box point is a weighted average of corners, so no interior value exceeds their largest bound.')
t(s,30,380,'n > 16 refuses exact enumeration. This two-block example is diagnostic only, below the five-unit publication minimum.')
save(s,'figA3_block_corners.svg')
# synthetic clock polygon all vertices satisfy displayed rows.
s=begin('Figure A5. Clock constraint intersection',1000,500)
t(s,30,32,'Figure A5. SYNTHETIC clock constraints after eliminating the offset',20)
t(s,30,60,'Coordinates: x = (β − 1) × 10⁶ ppm; y = (A − Aref) in milliseconds. Aref is an arbitrary origin.')
X=lambda x:110+x*90;Y=lambda y:385-y*65
for v in range(5):line(s,X(v),Y(0),X(v),Y(4),'#eceff2');t(s,X(v)-5,407,str(v),13)
for v in range(5):line(s,X(0),Y(v),X(4),Y(v),'#eceff2');t(s,86,Y(v)+4,str(v),13)
# box 0<=x<=4 0<=y<=4; 1<= y-x <=2 => vertices (0,1),(0,2),(2,4),(3,4)
s.append('<polygon points="'+ ' '.join(f'{X(x)},{Y(y)}' for x,y in [(0,1),(0,2),(2,4),(3,4)])+'" fill="#c4def3" stroke="#1b6ca8" stroke-width="2"/>')
for c in (1,2):line(s,X(0),Y(c),X(4-c),Y(4),'#1b6ca8')
line(s,X(0),Y(0),X(4.2),Y(0));line(s,X(0),Y(0),X(0),Y(4.2))
t(s,180,436,'Rate departure x (ppm)');t(s,45,102,'Anchor y (ms)')
for j,l in enumerate(['Rows: 0 ≤ x ≤ 4; 0 ≤ y ≤ 4','and 1 ≤ y − x ≤ 2.','Blue lines: y = x + 1 and y = x + 2.','Shaded polygon: intersection of every row.','Vertices: (0,1), (0,2), (2,4), (3,4).','Projections: x ∈ [0,3]; y ∈ [1,4].','Add y − x ≥ 3: empty set → refuse.','This drawing is illustrative, not the retained capture.']):t(s,545,125+37*j,l,15)
t(s,30,479,'The real solver uses all native labels and five stamp brackets; Table A3 and its sidecar identify those inputs.')
save(s,'figA5_clock_polygon.svg')
d=json.loads((F/'worked-examples.json').read_text());h=d['historical'];sy=d['synthetic']
s=begin('Figure A4. Shared and local signs',1000,425)
t(s,30,32,'Figure A4. SYNTHETIC two-block shared-sign / local-corner calculation',20)
t(s,30,60,'Within each block: shared start shifts and shared end shifts are swept separately over record-edge breakpoints.')
for j,b in enumerate(sy['blocks']):
 x=30+j*485;rect(s,x,95,460,153,'#f0f3f6');t(s,x+15,123,f'Block {j+1}: δ = {b["delta"]:.10f} J',17)
 t(s,x+15,153,f'Extrema → q{j+1} = {b["q"]:.10f} J')
 t(s,x+15,183,f'Four local residuals / 2 → ℓ{j+1} = {b["local"]:.10f} J')
 t(s,x+15,218,'Shift candidates → scalar allowance; timing coordinates are lost.',13)
t(s,30,282,'One shared sign s; independent signs e1,e2 → δ′j = δj + s qj + ej ℓj → eight rows in Table 4.')
t(s,30,319,'Maximum: (s,e1,e2) = (+1,−1,+1) → (0.4278157324, 1.1582423076) J.',17)
t(s,30,352,'Recompute mean, SD and largest magnitude → Ucmp,shared = 8.8304376431 J.',17)
t(s,30,392,"A shared energy sign does not replay one timing shift across all blocks or prove its limit covers that shift's effect.")
save(s,'figA4_shared_signs.svg')
s=begin('Figure A6. Current-anchor pulse 9 fit and projected enclosure',1100,615)
t(s,30,32,'Figure A6. Historical pulse 9 under the current anchor: records, fit, enclosure',20)
t(s,30,58,'Epoch origin 1784757381 s. Gray: observed interval averages; blue: model averages at the best pair.',14)
X=lambda v:70+(v+0.6)*340;Y=lambda v:330-v*4.8
for v in (0,10,20,30,40,50):line(s,70,Y(v),1010,Y(v),'#e5e8eb');t(s,40,Y(v)+4,str(v),12)
for r in h['local_records']:
 a=r['start_s']-1784757381;b=r['end_s']-1784757381
 rect(s,X(a),Y(r['gpu_w']),max(.2,X(b)-X(a)),r['gpu_w']*4.8,'#e1e5e9','#88929c')
 line(s,X(a),Y(r['predicted_w']),X(b),Y(r['predicted_w']),'#1b6ca8')
for v,label in [(h['command_on']['epoch_s']-1784757381,'on command'),(h['command_off']['epoch_s']-1784757381,'off command')]:
 line(s,X(v),80,X(v),345,'#333','5 4');t(s,X(v)+5,95,label,13)
for v in (0,.5,1,1.5,2):t(s,X(v)-6,350,str(v),12)
t(s,420,374,'Seconds from epoch origin');t(s,35,78,'GPU W',12)
# inset projected rectangle - labelled enclosure only
rect(s,80,420,250,120,'#eef6fc','#1b6ca8');t(s,90,444,'Retained enclosing rectangle',14)
t(s,90,467,'on ∈ [25.449389, 28.932935] ms',13);t(s,90,490,'off ∈ [−8.607395, −5.308621] ms',13)
s.append('<circle cx="210" cy="513" r="4" fill="#1b6ca8"/>');t(s,222,518,'best (27, −7) ms',13)
t(s,365,433,'Search axes: onset shift, offset shift. Candidate pairs predict each record average.',15)
t(s,365,463,'Split rectangles; discard a rectangle only when its loss lower bound exceeds Λ.',15)
t(s,365,493,'Projections are the surviving outer minima/maxima, widened for command stamps.',15)
t(s,365,523,'The inset prints an enclosure; it does not depict the shape of the accepted set.',15)
t(s,30,575,'Loss* = 13724.280241; Λ = 14410.494253. This tolerance defines a model set, not a confidence or physical-edge guarantee.',14)
save(s,'figA6_pulse_fit.svg')
