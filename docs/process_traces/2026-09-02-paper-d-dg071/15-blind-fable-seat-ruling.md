# Sealed ruling — blind Fable seat — DG-071 / DG-075 statistic convention amendment

Date: 2026-09-02. Seat: fresh Fable instance, no loop context.

## Disclosure of contamination

Read, as named by the packet: the packet itself; the 2026-08-31 ratification
(`docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md`);
the issued artifact (`docs/paper/round7/dg071-dg075-statistics.md`); the two
refuter reports (`out/245-sol-paper-d-physics.md`, `out/246-opus-paper-d-physics.md`);
the magistrate's bench script (`scratchpad/dg071-bench.py`).

Read OUTSIDE the packet, deliberately and minimally, because Q1 turns on the
exact paper wording and I would not rule on a quotation relayed by a refuter:
`docs/paper/draft-v1.md` line 256 only (via `sed -n 256p`) and the four
`grep` hits for `DG-071|DG-075` in `docs/paper/results-fill-registry.md`
(lines 545, 643, 647, 848, 906; first 400 characters each), both in
`/Users/edr/code/JouleWise-wt-paper-d` at HEAD `a46000da`. I did not read
README, RUN_STATE, TASK_QUEUE, orchestration docs, CLAUDE*.md, memory, the
producer script, its tests, or any other file. Nothing was written under any
git checkout; scratch is in `scratchpad/seat-blind-dg071/`. No codex or
claude process was launched. `unittest discover` was not run.

## Executed evidence (my own script, `seat-blind-dg071/verify.py`, run with the repo venv Python)

Every packet fact I rely on was re-executed against the bundle
(SHA-256 re-hashed: `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`):

```
rows 1218  records 406  group sizes {3: 406}  rail sets {(ane,cpu,gpu): 406}
records with non-identical intervals across rails: 0
interval_end_s == timestamp_s (as strings) for all 1218 rows: True
max decimals ts/start/end: 7 / 7 / 7      timestamps ascending in file order: True
float64 rows(1218)  q1/med/q3/iqr ms  116.951942 120.918512 122.926950 5.975008   (= issued artifact)
float64 recs(406)   q1/med/q3/iqr ms  116.971970 120.918512 122.922659 5.950689
Decimal recs(406)   q1/med/q3/iqr ms  116.97195  120.9186   122.9227   5.95075
Decimal rows(1218)  q1/med/q3/iqr ms  116.9519   120.9186   122.9270   5.9751
n=406 even; middle two widths 120.9148 / 120.9224 ms (NOT equal)
ulp(1.785e9 s) = 2.384e-07 s = 2.384e-04 ms; max |float width - exact width| = 1.851e-07 s
DG-075 float64 (405) 117.032051 120.922327 122.926950 5.894899   (= issued artifact)
DG-075 Decimal (405) 117.0321   120.9224   122.9270   5.8949
widths[1:] stats == DG-075 stats: True (float) and True (Decimal)
boundaries with interval_start_s != previous timestamp_s: 100 of 405; gaps in {±1e-7..±4e-7 s}; max 4e-7 s
first record (dropped by DG-075) width 111.8886 ms = 2nd smallest of 406
sum of 406 record widths 48.8018768 s; trace span 48.8018784 s; sum of 1218 row widths 146.4056304 s
numpy 2.5.1: my type-7 == np.quantile(method="linear") exactly; nearest/inverted_cdf/hazen on 406 recs
  reproduce the OLD issued 1218-row digits (116.951942 / 122.926950)
Rendering at 4 dp: float64 recs -> 116.9720 120.9185 122.9227 5.9507 ; exact -> 116.9720 120.9186 122.9227 5.9508
Rendering at 3 dp: float64 and exact agree (116.972 120.919 122.923 5.951)
```

All packet facts confirmed. Two facts the packet did not state that bear on
the rulings: (i) at FOUR rendered decimals float64 and exact arithmetic
disagree on the median (120.9185 vs 120.9186) and the IQR (5.9507 vs 5.9508);
at three they agree; (ii) for n=405 the type-7 positions (101, 202, 303) are
integers, so DG-075's quartiles are exact order statistics, while for n=406
the positions (101.25, 202.5, 303.75) interpolate, which is why exact Q1
carries a fifth millisecond decimal (116.97195).

---

## Q1 — Population: AMEND to 406 sampler records, rails collapsed, refusal-guarded

**Verdict: AMEND.** The paper sentence requires the record reading; the row
reading is not a candidate to "keep and disclose."

**Why the sentence decides it.** Draft line 256 defines the quantity in
words before naming it: "how long one power record covers — the width of
its support in time." A power record here is one sampler emission; the CSV
stores it long-format as three rows (one per rail) that carry the same
support. A rail row is a column of the record, not a record. The ratification
itself already treats records as the tiling unit ("records tile with no
sampler pause") — a property that is true of the 406 supports and false of
the 1218 rows, whose summed support is 146.41 s inside a 48.80 s trace. So
"over every retained record" in the 08-31 text was ambiguous English, and
its only physically coherent reading was always the 406. The amendment
clarifies the ratified text to match the ratified physics; it does not change
the statistic.

**Operative text (for the addendum):**

> DG-071 population. The statistic is taken over the bundle's SAMPLER
> RECORDS, one width per record, not over CSV rows. A sampler record is the
> set of rows sharing one `timestamp_s` literal. The producer MUST group rows
> by the exact string triple (`timestamp_s`, `interval_start_s`,
> `interval_end_s`) and REFUSE issuance (reason `record_rail_multiplicity`)
> unless every group contains exactly three rows whose `rail` values are
> exactly {`cpu_power`, `gpu_power`, `ane_power`} and whose interval strings
> are byte-identical; it MUST also refuse if any `timestamp_s` literal occurs
> in more than one group. The artifact reports `rail_row_count` (1218) and
> `sampler_record_count` (406) as separate fields, and the statistic's
> `sample_count` is the record count. The 08-31 phrase "every retained
> record" is superseded by this paragraph; the artifact issued at commit
> `681f30ce` over 1218 rows is WITHDRAWN and must not be cited.

**Biting counterfactual.** (a) A fixture in which one record carries two
rails must be REFUSED, not silently collapsed by timestamp; (b) a fixture in
which one rail's `interval_end_s` differs from its siblings by 1e-7 s must be
REFUSED; (c) the 1218-row artifact read aloud fails a one-line check any
reviewer can do — 1218 × 0.1209 s = 147 s of record support in a 48.8 s
trace — which is why "keep and disclose" is not an option: disclosure would
be disclosing a contradiction. Tests must exercise (a) and (b) through the
CLI and must be shown to fail against a producer that groups by
`timestamp_s` alone.

**Numerical consequence.** Median unchanged (120.9186 ms exact); Q1 rises
0.02 ms, Q3 falls 0.004 ms, IQR falls 0.024 ms (float64: 116.971970 /
122.922659 / 5.950689 ms). The 6 low widths in the old 111.8–112.5 ms band
were each counted three times, which is the direct cause of the Q1 shift.

**Does NOT decide:** the long-format CSV layout (rows per rail) is not
being ruled wrong for any other consumer; nothing is decided about other
bundles or about rail-level power statistics; the median value's
correctness under the old population is not a defence of the old artifact.

---

## Q2 — Precision: option (a), exact Decimal seconds of record, milliseconds rendered to FOUR decimals

**Verdict: (a).**

**Reasoning, built from the file.** The CSV stores every endpoint with at
most seven decimals of seconds, i.e. a literal resolution of 1e-7 s
(1e-4 ms). At magnitude 1.785e9 s a float64 has a spacing (ulp) of
2.384e-7 s — coarser than the literal. Parsing an endpoint to float64
therefore rounds it by up to 1.19e-7 s BEFORE any subtraction; the
subtraction itself is then exact (verified: every width equals the
difference of its parsed endpoints), so the error is entirely in the parse
and is up to 1.85e-7 s per width in this file. Exact decimal arithmetic on
the literals has no such step: widths are exact multiples of 1e-7 s, and the
type-7 interpolants for n=406 are exact multiples of 2.5e-8 s. The
statistic then depends only on the retained bytes, which is what a value of
record must be. Under float64 two correct implementations (Python `float`,
R `read.csv`) agree with each other but disagree with the bytes; the median
demonstrates it at exactly the rendering in question: exact 120.9186 ms
(the mean of the two middle literals 0.1209148 s and 0.1209224 s), float64
120.918512 ms → renders 120.9185. The file says 120.9186. Option (b) would
therefore render a fourth digit that is wrong, or would have to retreat to
three decimals and throw away one digit the file actually carries.

**Operative text:**

> Arithmetic. Endpoints are parsed from the CSV literals with exact decimal
> arithmetic (Python `decimal.Decimal(<string>)`, never via `float`); widths,
> spacings, quantiles, and IQR are computed exactly. The VALUES OF RECORD are
> the exact decimal seconds, written in the JSON as strings (not JSON
> numbers) so no consumer re-rounds them. Milliseconds are RENDERINGS:
> value × 1000, rounded to four decimals under round-half-to-even
> (`Decimal.quantize(Decimal("0.0001"), ROUND_HALF_EVEN)`); the rounding
> rule is stated in the artifact. IQR is computed exactly as Q3 − Q1 and
> rendered separately; the artifact states that the rendered IQR may differ
> from the difference of the rendered quartiles by one unit in the last place
> (here DG-071: 5.9508 vs 122.9227 − 116.9720 = 5.9507).

**Digits a reader may trust, and why.** All four rendered decimals are exact
statements about the retained bytes. A reader who replicates with exact
decimal arithmetic reproduces every digit. A reader who replicates with
float64 (numpy, R defaults) is guaranteed agreement only to THREE decimals
(per-width parse error ≤ 2.4e-4 ms < the 5e-4 ms half-unit of the third
decimal) and may differ in the fourth — the artifact says so explicitly,
with the median as the worked example (120.9185 float vs 120.9186 exact).
What the fourth decimal is NOT: a claim that the sampler resolved 0.1 ms.
The 1e-7 s literals are the writer's formatting of a clock; the artifact
must say the digits characterise the file, and the physical timing
resolution of the sampler is a separate, undecided question.

**Biting counterfactual.** A producer that parses with `float` and renders
four decimals issues 120.9185 for the median; the test fixture must contain
two middle literals whose exact mean differs from their float mean at the
fourth millisecond decimal (the real bundle does) and assert 120.9186.

**Does NOT decide:** the resolvability arithmetic elsewhere in §6, the
physical sampler resolution, and whether other paper producers must move to
Decimal (only these two rows are ruled).

---

## Q3 — Method disclosure: YES, in both places, and the even-n median convention IS part of it

**Verdict: REQUIRED in the addendum AND in the issued artifact.**

"Median with IQR" does not identify a number. On the 406-record sample,
eleven standard quantile definitions give six distinct Q1 values (executed:
116.936982 … 117.032051 ms); three of them (`nearest`, `inverted_cdf`,
`hazen`) on the CORRECT population reproduce the digits of the WITHDRAWN
1218-row artifact, so an unpinned method lets a replicator "confirm" the
wrong artifact by coincidence. The even-n median convention is not
pedantry here: n=406 is even and the two middle widths differ
(120.9148 vs 120.9224 ms), so low-median, high-median, and mean-of-middle
are three different numbers; only the last equals type-7 Q(0.5).

**Operative text (both documents; the artifact may not cite a library name
in place of the definition, because library defaults are not a definition):**

> Quantile definition: Hyndman–Fan type 7. For a sorted sample
> x(1) ≤ … ≤ x(n) and probability p, let h = (n − 1)·p, i = ⌊h⌋; then
> Q(p) = x(i+1) + (h − i)·(x(i+2) − x(i+1)), with Q(p) = x(n) when i = n − 1.
> Median = Q(0.5), which for even n is the mean of the two middle values.
> Q1 = Q(0.25), Q3 = Q(0.75), IQR = Q3 − Q1, all on exact decimal values
> before rendering. Equivalent to numpy `method="linear"` and R `type = 7`
> (stated as cross-references, not as the definition).

The producer's docstring citation to "R-167-1" (a ruling both refuters
searched for and found nowhere but in the producer) must be replaced by the
path of this addendum; a convention traceable only to the code that
implements it is not ratified.

**Biting counterfactual.** A replicator using R's `quantile(type = 6)` or
numpy `hazen` must be able to see from the artifact alone why their Q1
differs; a test computing Q1 with `nearest` on the five-record fixture must
give a different number from the producer's, proving the fixture
discriminates methods (a fixture on which all methods agree — as the 1218-row
tripled sample did, where all eleven methods coincide — proves nothing).

**Does NOT decide:** type 7 as a project-wide convention for other rows;
whether the median should be reported with anything other than IQR.

---

## Q4 — DG-075: KEEP as a separate issued row, with a dependence sentence conditioned on an executed tiling check

**Verdict: KEEP (as ratified), NOT retired; the fill sentence must declare
the dependence, and the producer must verify the tiling that makes the
dependence true.**

Why keep: the frozen draft has two `[PENDING]` slots on line 256 and the
second names "record spacing" as a distinct quantity; retiring the row now
leaves a placeholder with no supplier, and rewriting the sentence is a
round-7 draft edit outside this packet (that edit is already scheduled to
correct the "sampler pauses" mechanism). Why the dependence must be
stated: `interval_end_s` equals `timestamp_s` for all 406 records and
`interval_start_s` equals the previous record's `timestamp_s` exactly for
305 of 405 boundaries and to within 4e-7 s (the writer's last digit) for
the other 100; hence the 405 spacings are the widths of records 2–406 to
within writer noise, and all four statistics coincide with those of
widths[2..406] (executed, float and exact). Set beside DG-071, DG-075's
median (120.9224 vs 120.9186 ms) is LARGER — which a reader of the frozen
"pauses" sentence will take as numerical confirmation of a pause that does
not exist. The whole difference is the exclusion of the first record, the
second-smallest width in the bundle.

**Operative text — registry row and fill sentence:**

> DG-075 (record spacing) is the same record-period distribution as DG-071
> minus the first record, not independent evidence: because every record's
> `interval_end_s` equals its `timestamp_s` and every record's
> `interval_start_s` equals the previous record's `timestamp_s` to within
> 4e-7 s, the 405 consecutive-timestamp differences are the widths of
> records 2–406. The two rows differ only by that excluded first record and
> by endpoint convention. The values are median 120.9224 ms, IQR 5.8949 ms
> (Q1 117.0321, Q3 122.9270; n = 405; exact order statistics since the
> type-7 positions 101/202/303 are integers).

> Producer condition. The dependence sentence is issued ONLY IF the producer
> verifies, on the pinned bytes, that max |`interval_start_s`(k) −
> `timestamp_s`(k−1)| ≤ 1e-6 s over all 405 boundaries (ten times the
> writer's last digit; observed 4e-7 s) and that `interval_end_s` ==
> `timestamp_s` for every record. If either fails, the producer REFUSES
> (`records_do_not_tile`) rather than issuing a spacing row whose relation
> to the width row is unknown.

**Biting counterfactual.** A fixture in which one record starts 5 ms after
the previous timestamp (a real pause) must be refused; on such a bundle the
dependence sentence would be false, and the refusal is what keeps a true
sentence from being copied onto a bundle where it is not true. The
registry row's status should mark DG-075 DERIVED-FROM DG-071.

**Does NOT decide:** whether round 7 collapses the two draft sentences into
one number (that is the draft edit's decision, and this seat leans toward
one number with the tiling stated in prose, but the frozen draft forbids it
now); the draft's endpoint convention ("start times" in the sentence versus
`timestamp_s` = end times in the ratification) — identical multisets here
up to writer noise, but the round-7 sentence should say which.

---

## Q5 — Process: a dated addendum is the right instrument, with named limits

A dated addendum by the same authority is correct here, and a fuller cold
gate is not required, for four reasons that should be written into the
addendum's header so the choice is auditable: the rows are DIAGNOSTIC-era
and registered non-claim-bearing; nothing reverses a verdict or
reinterprets a stop signal (the 08-31 ratification's own physics — "records
tile" — already implied the record population, so this is a clarification
that makes the text agree with itself); two independent refuters with
distinct lenses plus this blind seat concur on the same four defects from
executed evidence, which is the three-family diversity the cold gate exists
to supply; and the threat model is honest drift, where the cure is
disclosure plus refusal guards, not custody. The addendum must be APPENDED
under a date, must quote the superseded sentence and state why it was
wrong, must be the document the producer cites (replacing "R-167-1"), and
the withdrawn 1218-row artifact must be marked withdrawn rather than
deleted. Three conditions convert this into a cold-gate matter: if the
re-issued artifact fails its delta re-audit with the same signature (wrong
population or undisclosed method again) — that is the standing
two-strikes trigger and the next spend is a consult, not round three; if
round 7 proposes to change the draft's definitions of width or spacing
(a paper-text change, not a fill); or if either row is ever promoted to
claim-bearing. The re-issue itself still needs one execution-lens delta
re-audit that runs the counterfactual fixtures named in Q1, Q2, and Q4
against the amended producer before the registry rows leave STOP_FILL.

---

## Verdict lines

Q1: AMEND — population is the 406 sampler records, rails collapsed, producer refuses on any non-{cpu,gpu,ane}/non-identical-interval record; the paper sentence ("how long one power record covers") requires it and the 1218-row artifact is withdrawn.
Q2: (a) — exact Decimal parse; exact decimal seconds (as JSON strings) are the values of record; milliseconds rendered to FOUR decimals under round-half-even; all four rendered digits are facts about the bytes, float64 replication is guaranteed only to three (median 120.9185 vs 120.9186 proves it).
Q3: YES, both — addendum and artifact must state Hyndman–Fan type 7 by formula (h=(n−1)p, linear interpolation), median = Q(0.5) = mean of the two middle values for even n (n=406 and the middle values differ), IQR = Q3−Q1 before rendering; library names are cross-references only; the "R-167-1" citation is replaced by the addendum path.
Q4: KEEP DG-075 as a separate issued row with a fill sentence stating it is the DG-071 distribution minus the first record (tiling: end==timestamp, start==previous timestamp to ≤4e-7 s), issued only if the producer verifies tiling (≤1e-6 s) and refuses otherwise; retirement/merger deferred to the round-7 draft edit.
Q5: DATED ADDENDUM is the right instrument (diagnostic-era rows, clarification not reversal, three concurring seats on executed evidence, honest-drift threat model); a cold gate is required only on a same-signature re-audit failure, a change to the draft's definitions, or promotion to claim-bearing; one execution-lens delta re-audit of the re-issue is still required.
