VERDICT: BLOCKER 0 / SHOULD-FIX 5 / NIT 5

Opus 5 counter-review (gate item 6, CONTRACT lens) — PR #276, `feat/2026-09-02-paper-d`, head `8ab397b5`.
Read-only in `/Users/edr/code/JouleWise-wt-paper-d2`; scratch under `<scratchpad>/opus-249`.
Retained bundle verified before any read:

```
$ shasum -a 256 /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv
6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9  …/power_trace.csv
```

**No blocker.** All eight values of record replicate exactly against my own
independent Decimal/type-7 implementation, the producer replays byte-identically
into the committed artifact, and both of file 21's mutation-kill claims reproduce
with exactly the named single failure. The findings below are one untested
contract sentence class (with an escalation-trigger implication), one
contract-document number that disagrees with a published field, four pedagogy /
ledger defects, and five nits.

---

## Findings

**C-1 — SHOULD-FIX — `tests/test_issue_dg071_dg075_statistics.py` (whole module,
23 tests) — two further value-of-record-changing mutants survive; SAME SIGNATURE
as terra 248, one round later.**
I built four mutants beyond terra 248's three. Two survive all 23 tests and each
changes a *published* number in `docs/paper/round7/dg071-dg075-statistics.json`.
(a) Rendering the IQR as `render_ms(Q3) − render_ms(Q1)` instead of
`render_ms(Q3 − Q1)` (producer line 188) survives, and issues DG-071
`iqr_ms = "5.9507"` instead of `"5.9508"` — this is precisely the addendum item 3
sentence "IQR = Q3 − Q1 computed exactly before rendering (so the rendered IQR
may differ from the difference of the rendered quartiles by one unit in the last
place)", the one clause of the contract for which no fixture exists (§5 names the
fixture). (b) Changing `sum(gap != Decimal(0) …)` to `sum(gap > TILING_TOLERANCE_S …)`
(producer line 361) survives, and issues `tiling_gap_nonzero_boundaries: 0`
instead of `100`. Counterfactual reader: a maintainer refactors `_describe` or
`_verify_tiling`, the suite stays green, and the artifact silently publishes
5.9507 / 0 — the round-7 fill would then carry a wrong IQR digit with a green
gate behind it. **Escalation note (rule 11):** delta 2 (terra 248) found two
surviving mutants that change values of record; those two were patched at the
bench with two fixtures; one round later I find two more of the *same class*
(a value-of-record field with no mutation-adequate test). Two consecutive delta
rounds failing with the same signature is the standing escalation trigger — the
next spend is a consult on how the producer's reported fields get systematic
coverage, not a third pair of hand-added fixtures.

**C-2 — SHOULD-FIX — `docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md`
item 4 ("≤ 2.4e-7 s, 100 of 405 boundaries differ by exactly that") vs
`docs/paper/round7/dg071-dg075-statistics.md:8` ("Maximum absolute tiling gap
(s): 0.0000004").** The contract sentence is true — but only of the *float64*
values, which I confirmed to a degree the trace never showed: all 100 nonzero
boundaries differ by *exactly* one ulp, 2.384185791015625e-07 s, none by more or
less. Measured on the *decimal literals* — which the same addendum's item 2
declares to be the values of record — the same 100 boundaries differ by 1e-7 (×4),
2e-7 (×49), 3e-7 (×46) and 4e-7 (×1); the maximum is 4e-7 s, which **exceeds** the
addendum's stated ≤ 2.4e-7 s bound, and no boundary equals 2.384e-7 s. Neither
document says which object its number describes. Counterfactual reader: a
replicator who writes the addendum's bound as an assertion over the retained
bytes (the only bytes the artifact pins) gets a failure on the pinned bundle;
a reader who lays the addendum beside the artifact sees 2.4e-7 and 4e-7 for
"the gap" and cannot tell which is wrong. Cure is a dated correction line naming
the two objects, not a producer change — the operative rule the producer
implements (≤ 1e-6 s) is stated correctly in both documents and correctly coded.

**C-3 — SHOULD-FIX — `docs/paper/round7/dg071-dg075-statistics.md:14-28` and
`scripts/issue_dg071_dg075_statistics.py:2-47` — six terms of art used before
they are built (first-use test).** `literal`, `contiguous`, `order statistics`,
`round-half-even`, `values of record`, and `the retained writer's endpoint
convention` all appear in the Method section (and the docstring) with no gloss.
Two are load-bearing: the entire exactness argument rests on *literal* meaning
"the character string as written in the file, before any numeric conversion" —
and the tiling test is literal (string) equality, not numeric — while
*round-half-even* is the single rule that decides the last published digit of
every millisecond value (terra 248 built a whole regression around it). Full list
with suggested glosses in §2. Counterfactual reader: Rivoire, or any replicator
outside this repo's vocabulary, reaches "byte-identical `interval_start_s` …
literals" in sentence 1 and must guess whether byte-identity or numeric equality
is meant — and the guess changes what their re-implementation refuses.

**C-4 — SHOULD-FIX — `docs/paper/round7/dg071-dg075-statistics.md:8-9` — "tiling"
names two published fields and is defined nowhere in the artifact.** `grep -i
'tiling\|tile'` over the issued Markdown returns exactly the two header bullets;
the word never appears in `## Method`, and the JSON `method` object has no
`tiling` key. The condition is described eight paragraphs later without ever being
called tiling. Counterfactual reader: sees "Maximum absolute tiling gap (s):
0.0000004" as the fourth line of the artifact with no way to know what was
measured between what — and, per Ed's standard, will read the unnamed thing as
whatever they already believe and be right to.

**C-5 — SHOULD-FIX — PR #276 gate ledger, rows 5 and 8 — cited evidence does not
contain the labelled check.** Row 5 ("Same-signature statement from every delta")
cites `21-delta-2-disposition.md`; `grep -in signature` over files 10, 20 and 21
returns nothing — no delta report or disposition in this lane makes a
same-signature statement, and neither delta brief (09, 19) asked for one. Row 8
("Overbuild / merge-ability prune") cites `15-blind-fable-seat-ruling.md`, whose
own contamination disclosure states "I did not read … the producer script, its
tests, or any other file" — a ruling that did not read the code cannot be the
overbuild prune of the code. Counterfactual reader: the merge reviewer treats
both gate items as discharged when neither was performed. (Substantively, no
escalation was in fact owed at the time — delta 1 was CLEAN — but see C-1, where
the signature now *has* recurred; and the overbuild pass is §6 of this review.)

**C-6 — NIT — `scripts/issue_dg071_dg075_statistics.py:108, 124` — two write-only
dataclass fields.** `_ParsedRow.row_number` is assigned at line 320 and never
read (every `row {row_number}` message uses the local parameter, not the field);
`SamplerRecord.interval_start_literal` is assigned at line 239 and never read
(`_verify_tiling` reads only `interval_end_literal` and `timestamp_literal`).
A maintainer must work out that neither is load-bearing.

**C-7 — NIT — addendum item 4 vs `scripts/issue_dg071_dg075_statistics.py:347`.**
The addendum writes the check as `interval_end_s == timestamp_s`; the code (and
fix brief C4, and the artifact's Method) require *literal* equality, which is
strictly stronger — `"10.0"` vs `"10.00"` refuses. terra 248 D4 saw this and
declined to flag it ("changing this to numeric equality would be a new policy
decision"), which I endorse; the residue is that the ONE home still states the
weaker rule. One word ("literal") in the addendum closes it.

**C-8 — NIT — `18-fix-round-2-disposition-and-reissue.md` and
`21-delta-2-disposition.md` — cited envelope byte counts are not reproducible
from the stored reports.** File 18 says "envelope 4251 bytes" for file 17; the
fenced JSON in file 17 measures 4165 bytes. File 21 says "envelope 3557 bytes"
for file 20; file 20's measures 3386. Nothing turns on it (both are far under the
8192 protocol limit), but a stated byte count that the custodied artifact
contradicts is a fact a later reader cannot check.

**C-9 — NIT — `docs/process_traces/2026-09-02-paper-d-dg071/19-delta-2-brief.md:12`
— unredacted session scratchpad path.** 15 of the 16 dg071 trace files that
reference the scratchpad use `<scratchpad>`; file 19 carries the full
`<scratchpad>`.
(Out of lane but for the record: the same raw path appears in
`2026-09-02-projection-02/` ×9, `2026-09-02-coldgate-dx-t26a/` ×2, and
`RUN_STATE.md` ×21 with older session UUIDs.)

**C-10 — NIT — `docs/paper/round7/dg071-dg075-statistics.json` `method.iqr`.**
The Markdown carries Sol 247's accepted extra sentence ("A separately rendered
IQR can differ from the difference of rendered quartiles by one unit in the last
place"); the JSON `method` object does not. A JSON-only consumer sees
5.9508 alongside 122.9227 − 116.9720 = 5.9507 with no explanation.

---

## §1 — Addendum ↔ producer ↔ artifact fidelity

Bundle and script identity first. The producer is byte-identical between the
producer commit `29181d6c` and the PR head, and its hash is the one the artifact
publishes:

```
$ git diff --stat 29181d6c 8ab397b5 -- scripts/issue_dg071_dg075_statistics.py
                       (no output — identical)
$ shasum -a 256 scripts/issue_dg071_dg075_statistics.py
d769f05b050d56e49e55b1aac3d30a21e1a1ad7ddd181f7d15ad62988edf4899  scripts/issue_dg071_dg075_statistics.py
$ grep script_sha256 docs/paper/round7/dg071-dg075-statistics.json
    "script_sha256": "d769f05b050d56e49e55b1aac3d30a21e1a1ad7ddd181f7d15ad62988edf4899",
```

**Item 1 — Population.** Operative: *"'Every retained record' means every SAMPLER
RECORD: the rows sharing one `timestamp_s`, collapsed to one width. The producer
REFUSES (`record_rail_set_mismatch`) unless every record has exactly the three
rails above with byte-identical `interval_start_s`/`interval_end_s`; it never
averages or picks a rail. … The artifact reports 'sampler records: 406; rail rows:
1218' and never calls a rail row a record."*
Code: `_read_records` (lines 264-338) accumulates `current_group` while the
`timestamp_s` **literal** is unchanged; `_record_from_group` (lines 217-243)
raises `record_rail_set_mismatch` unless `len(group) == 3`, `set(rails) ==
{cpu,gpu,ane}`, `len(starts) == 1` and `len(ends) == 1`, then takes `group[0]`
— a pick that is only reached after all three are proven identical, so no
averaging and no rail preference. `build_payload:468` emits exactly one width per
record. Artifact: `sampler_record_count: 406`, `rail_row_count: 1218`, Markdown
lines 6-7 "Sampler records: 406 / Rail rows: 1218". The word "record" is never
applied to a rail row anywhere in either file. **No drift.**
Independent confirmation that the grouping is the right one:

```
rail rows: 1218
records: 406
all groups 3 rails w/ identical endpoints: True
distinct timestamp literals: 406 distinct values: 406
```

**Item 2 — Arithmetic and digits.** Operative: *"Endpoints are parsed from the CSV
literals with exact decimal arithmetic (`decimal.Decimal(<string>)`, never through
`float`); widths, spacings, quantiles and IQR are computed exactly. The VALUES OF
RECORD are the exact decimal seconds, written in the JSON as strings.
Milliseconds are renderings: value × 1000 rounded to FOUR decimals,
round-half-to-even, the rule stated in the artifact, which also states that a
float64 replication … is guaranteed to agree only to three decimals … (worked
example in the artifact: median 120.9186 ms exact vs 120.9185 ms float). The
digits characterise the retained bytes, not the sampler's physical timing
resolution, and the artifact says so."*
Code: `_parse_decimal_literal:203` `Decimal(value)` on the raw string; `float`
appears nowhere in the module (`grep -w float` → no hits outside the docstring's
prose); `_describe:167-188` computes q1/median/q3/IQR in Decimal and only then
renders `(value*1000).quantize(Decimal("0.0001"), ROUND_HALF_EVEN)`;
`_decimal_string` uses `format(v,"f")` so no exponent notation leaks.
Artifact: all `*_s` and `*_ms` are JSON strings; Markdown ¶4 states the rendering
rule, ¶5 the three-decimal float64 guarantee verbatim from the addendum plus the
"characterise the retained bytes" sentence, ¶6 the worked example. **No drift.**
The float64 guarantee is itself sound: float64 spacing at 1.78e9 s is 2.4e-7 s =
2.4e-4 ms < 5e-4 ms, so the third decimal survives and the fourth need not.

**Item 3 — Method disclosure.** Operative: *"order the n values ascending;
quantile at fraction p = the value at position h = (n−1)·p (0-based), linearly
interpolated between the two neighbouring order statistics (Hyndman–Fan type 7 …
library names are cross-references, the formula is the definition); median = the
p = 0.5 quantile (for even n, the mean of the two middle values); IQR = Q3 − Q1
computed exactly before rendering (so the rendered IQR may differ from the
difference of the rendered quartiles by one unit in the last place). The artifact
states this definition in full."*
Code: `_quantile:146-161` is exactly that, in Decimal, with the exact-integer-h
short circuit; `_describe:171` `iqr_s = q3_s - q1_s` before any rendering.
Artifact: Markdown ¶3 carries the formula, the 0-based h, the "cross-references"
framing, the even-n median, and the exact-IQR rule; ¶4 carries the last-place
caveat. JSON `method.quantile/median/iqr` carry all but the last-place caveat
(**C-10**). **No drift in the operative rule**; the ulp caveat is Markdown-only.

**Item 4 — DG-075 dependence.** Operative: *"it is the DG-071 distribution minus
the first record, because every record's `interval_end_s` equals its
`timestamp_s` and its `interval_start_s` equals the previous record's
`timestamp_s` to within one float64 ulp (≤ 2.4e-7 s, 100 of 405 boundaries differ
by exactly that …). The producer verifies tiling on the pinned bytes … and
REFUSES (`records_do_not_tile`) otherwise."*
Code: `_verify_tiling:341-361` — literal equality for end↔timestamp (**C-7**),
`abs(start(k) − timestamp(k−1)) > Decimal("0.000001")` for the boundary, one
`records_do_not_tile` refusal for either. Artifact: Markdown ¶7 states both
conditions with the 0.000001 s number. **Drift: C-2** (the addendum's ≤ 2.4e-7 /
"exactly that" parenthetical vs the artifact's published 0.0000004).
I also tested how far the "minus the first record" sentence can be pushed, since
it is the one identity claim in the artifact. It is not a multiset identity — but
it is harmless, and I could not make it bite:

```
values differing: 100 of 405   max |diff| s: 4E-7
sorted-multiset equal? False
issued DG-075 (timestamp diffs):        n=405 exact s ['0.1170321','0.1209224','0.122927','0.0058949']  ms ['117.0321','120.9224','122.9270','5.8949']
reader's "DG-071 minus the first record" = widths[1:]: n=405 exact s ['0.1170321','0.1209224','0.122927','0.0058949']  ms ['117.0321','120.9224','122.9270','5.8949']
```

All four quartiles agree in **exact seconds**, not merely at four ms decimals, so
a reader who takes the sentence literally publishes the same numbers. The
sentence survives; only its unglossed hedge is a pedagogy defect (**C-3**).

No field the addendum requires is absent from either artifact file. The
un-withdrawn body of the 2026-08-31 ratification also holds: path + SHA-256 are
recorded, the "111.8–112.5 ms" band is not resurrected anywhere in the artifact,
and the PR correctly defers the registry-row fill ("Follow-ups NOT in this PR")
so STOP_FILL / VALUE_UNISSUED is not silently discharged. DG-075's statistic
name ("consecutive differences of sorted distinct `timestamp_s` literals") is
equivalent to the ratification's "consecutive unique `timestamp_s` values" here,
because the monotonicity and contiguity refusals make file order and sorted order
the same order.

## §2 — Method section as a replication contract (first-use test)

Run mechanically over `## Method` (Markdown lines 14-28) and the docstring
(lines 2-47). Terms that are built or glossed at first use — **pass**: "sampler
record" (defined in sentence 1); "Hyndman–Fan type 7" (formula precedes it, and
it is explicitly labelled a cross-reference — the exemplary case in this
document); "renderings" (defined by construction); "worked example".

Fails, each with the sentence that should gloss it:

| Term | First use | Gloss it needs |
|---|---|---|
| `literal` | Md ¶1 s.1 "sharing an exact `timestamp_s` literal" | "…literal (the character string as written in the CSV, before any numeric conversion)" — the whole exactness claim and the tiling test both depend on string, not numeric, identity |
| `contiguous` | Md ¶1 s.1 | "…one contiguous group — consecutive rows in file order; a timestamp literal that reappears after another record has begun is refused" |
| `order statistics` | Md ¶3 "between the two neighbouring order statistics" | "…between the sorted values at 0-based positions ⌊h⌋ and ⌊h⌋+1" (this one is inferable, hence the softest of the six) |
| `round-half-even` | Md ¶4 | "…round-half-even (a value exactly halfway between two four-decimal renderings goes to the one whose last digit is even)" — the rule that decides every published last digit |
| `values of record` | Md ¶4 "JSON-string values of record" | "…are the authoritative values; the millisecond columns are renderings of them and are not re-used as inputs" |
| `the retained writer's endpoint convention` | Md ¶7, JSON `method.dg075_dependence` | The phrase is the only thing preventing "DG-075 *is* DG-071 minus the first record" from being a false identity (100 of 405 values differ). Build it: "…because the writer formatted the interval endpoints and the timestamp from two separately rounded floats, 100 of the 405 boundaries differ in the seventh decimal; the quartiles are unaffected" |

Plus **C-4**: `tiling`, used to name two published fields and defined nowhere.

Positive finding on the replication bar itself: terra 248 D9 rebuilt the DG-071
median and IQR from the Method section alone in 24 lines, and my own independent
implementation (written from the addendum + Method, not from the producer)
reproduced all eight values first try — so the *arithmetic* is replicable. The six
terms above are what a reader outside this repo's vocabulary must guess at, not
compute.

## §3 — Trace integrity

**(a) File 18's Executed evidence replays.** Recipe per file 10 V1 — a
`git clone --no-checkout` with HEAD pinned to the producer commit:

```
$ git clone --quiet --no-checkout /Users/edr/code/JouleWise-wt-paper-d2 <scratchpad>/opus-249/clone
$ git -C …/clone update-ref --no-deref HEAD 29181d6cdf7bcea89540c52eba39965363f5446f
$ for r in a b; do … python scripts/issue_dg071_dg075_statistics.py --repository-root …/clone --out …/replay-$r/dg071-dg075-statistics.json; done
DG-071 median_ms=120.9186 iqr_ms=5.9508
DG-075 median_ms=120.9224 iqr_ms=5.8949
exit=0                                    (identical for run b)
$ cmp replay-a/*.json replay-b/*.json && cmp replay-a/*.md replay-b/*.md && echo BYTE-IDENTICAL
BYTE-IDENTICAL
$ cmp replay-a/…json docs/paper/round7/dg071-dg075-statistics.json && echo JSON-MATCH
JSON-MATCH
$ cmp replay-a/…md  docs/paper/round7/dg071-dg075-statistics.md  && echo MD-MATCH
MD-MATCH
$ shasum -a 256 replay-a/dg071-dg075-statistics.*
5d96505f7940a9306e9e03c574329bcce6fa5c3d179a5fb76f8ea9b44a693b0d  …json
357410c69e6a32b210979aedc7782a3c5319c598957bd4aabef0b4ae7363969d  …md
```

Both hashes equal the ones file 18 records, and the replay is byte-identical to
the artifact committed at the PR head. **File 18 replays exactly.**

Independent replication of the values of record (my own Decimal/type-7 code,
written from the contract, reading the CSV directly):

```
DG-071 n 406  s ['0.116971950','0.12091860','0.122922700','0.005950750']  ms ['116.9720','120.9186','122.9227','5.9508']
DG-075 n 405  s ['0.1170321','0.1209224','0.122927','0.0058949']          ms ['117.0321','120.9224','122.9270','5.8949']
  rendered-q3 − rendered-q1 = 5.9507  vs rendered IQR 5.9508      (DG-071 — the last-place caveat, live)
end==timestamp literal for all: True
boundaries: 405  nonzero: 100  max gap s: 0.0000004
```

All eight `*_s` and all eight `*_ms` strings match the JSON character for
character. Suite at head: `Ran 23 tests … OK`.

**(b) File 21's mutation evidence reproduces.** Two files copied into a scratch
git repo with one commit; the two mutants applied as file 21 describes:

```
== halfup   (rounding=ROUND_HALF_EVEN → ROUND_HALF_UP)
FAIL: test_millisecond_rendering_ties_round_half_even_through_main
Ran 23 tests in 0.156s
FAILED (failures=1)
== starts   (delete the line "        or len(starts) != 1")
FAIL: test_record_rail_set_mismatch_refusal_reaches_main
Ran 23 tests in 0.179s
FAILED (failures=1)
== base
Ran 23 tests … OK
```

Exactly one failure each, and the failing test is the one file 21 names. **File 21
reproduces exactly.**

**(c) Seat-report envelopes.** Files 04, 06, 08, 10, 12, 17, 20 each open with a
fenced ```json envelope that parses, and each carries `status`/`completion`
matching the disposition that cites it (04 `clean`/`complete`; 06 `findings`;
08 `clean`; 10 `clean` + `"decision":"DELTA CLEAN"`; 12 `findings` with
blocker 1/should_fix 3; 17 `clean`/`complete` with C1–C7 all `done`, matching
file 18's quoted `semantic_status=clean completion=complete`; 20 `findings` with
`{"blocker":0,"should_fix":2,"nit":1}`, matching file 21's "SHOULD-FIX 2 / NIT 1").
**File 13 (`13-opus-246-physics-refute.md`) has no fenced envelope** — it opens
`VERDICT: BLOCKER 1 / SHOULD-FIX 4 / NIT 1`. This is *not* a protocol failure:
13 is an Opus subagent report, not a codex-bridge run, and no disposition claims
an envelope for it. Recorded as an observation, not a finding. The one
discrepancy is the byte counts (**C-8**): file 17's envelope measures 4165 bytes
against file 18's "4251"; file 20's measures 3386 against file 21's "3557".

**(d) Redaction.** One leak in this lane: `19-delta-2-brief.md:12`
(**C-9**). The other 15 dg071 files that mention the scratchpad all use
`<scratchpad>`.

## §4 — PR body vs trace

Every `RUN <path>` in the ledger exists at `8ab397b5` (all seven are files in
`docs/process_traces/2026-09-02-paper-d-dg071/`, confirmed by directory listing).
Rows 1, 2, 3, 4 and 7 are the artifacts their labels describe. Rows 5 and 8 are
not (**C-5**). Rows 6, 9, 10, 11, 12 are honestly `NOT-RUN`, and the Verification
paragraph says so ("Items 6, 9, 10, 11, 12 are filled before merge") — row 6 is
this review.

Summary numbers, each checked:

```
$ perl -0ne 'while(/IssuanceRefused\(\s*"([a-z_0-9]+)"/gs){print "$1\n"}' scripts/… | sort -u | wc -l
      16                              → "16 refusals each bound through main" ✓ (16 distinct names; 16 refusal-named tests)
$ grep -c '    def test_' tests/test_issue_dg071_dg075_statistics.py tests/test_docs_freshness.py tests/test_gen_state.py
      23 + 6 + 41 = 70                → "Ran 70, OK" ✓ (static count; I did not run the other two modules — outside my authorized test list)
$ git show a3dadadd:docs/paper/round7/dg071-dg075-statistics.json | grep -E 'sample_count|median_ms|schema_version'
  "schema_version": "…v1"  "median_ms": 120.918512  "sample_count": 1218   → "the a3dadadd issue (n = 1218, six-decimal float64 renderings)" ✓
```

n = 406 / 405, median 120.9186 / 120.9224 ms, IQR 5.9508 / 5.8949 ms — all
present in the artifact and independently reproduced above. The replay hashes in
the Verification paragraph are the two I reproduced. The dispositioned-not-applied
paragraph is accurate: Sol 247's extra sentence is in the Markdown and its
arithmetic (122.9227 − 116.9720 = 5.9507 vs 5.9508) is exactly what I measured;
terra's NIT-EXEC-01 is recorded in file 21 as a correction rather than by
rewriting file 18, per the custody rule. The R-167-1 provenance paragraph matches
file 03 and the addendum's withdrawal clause, and `grep R-167-1` over the
producer returns nothing, as file 18 claims.

No sentence in the Summary overstates. The two overstatements are ledger row
labels (**C-5**), not prose.

## §5 — Test adequacy on the contract's boundaries

The addendum sentence with **no** test that would fail if the producer violated
it, exactly as C-1(a): item 3's *"IQR = Q3 − Q1 computed exactly before rendering
(so the rendered IQR may differ from the difference of the rendered quartiles by
one unit in the last place)"*. Every fixture in the suite has quartiles whose
renderings are exact (widths 1–5 s, ties at 1.2344/1.2346 ms), so
`render(Q3 − Q1)` and `render(Q3) − render(Q1)` coincide everywhere the tests
look. **Missing fixture:** three or more records whose Q1 and Q3 each need a
non-terminating quarter-position interpolation — e.g. the retained bundle's own
shape, widths chosen so Q1 = 0.11697195 s and Q3 = 0.1229227 s — asserting
`iqr_ms == "5.9508"` while `Decimal(q3_ms) - Decimal(q1_ms) == Decimal("5.9507")`.
Two records is enough if their widths differ by an odd multiple of 5e-8 s.

Second untested boundary (C-1(b)): `tiling_gap_nonzero_boundaries` and
`max_tiling_gap_s` are asserted only in the all-zero-gap fixture
(`"0.0"` / `0`). **Missing fixture:** a bundle whose boundaries carry nonzero
gaps *within* the 1e-6 s tolerance — e.g. gaps of 2e-7, 3e-7 and 4e-7 s — issuing
successfully and asserting `max_tiling_gap_s == "0.0000004"` and
`tiling_gap_nonzero_boundaries == 3`. That one fixture pins both fields and is
the retained bundle's actual shape in miniature.

Two further mutants I ran are **killed**, which is worth recording because they
are the regressions that matter most: tripling each width to simulate the
withdrawn 1218-row reading fails 2 tests (the Markdown row assertion catches the
sample_count), and loosening `TILING_TOLERANCE_S` by 10⁴ fails 1. The headline
defect this PR exists to cure is genuinely regression-guarded.

Refusal↔test coverage is complete: 16 refusal names, 16 tests driving `main`,
each docstring naming its counterfactual input. That part of C5 holds.

## §6 — Scope / overbuild

The producer is 671 lines for one statistic over one SHA-pinned file, which
invites the question. My judgement: **it earns its place, with two exceptions.**

- *Earns it.* The 16 refusals look like a lot for a file that can only ever
  process one pinned byte-string, but the pin is the point: each refusal is the
  named failure mode of an evidence artifact (path substitution, content
  substitution, schema drift, interleaved rows, non-monotone time, a rail
  dropped), and every one is bound through `main` by a test with a stated
  counterfactual. `_absolute_without_symlink_resolution` deliberately does *not*
  resolve symlinks and says why in a docstring. `--repository-root` is what makes
  the `git_commit` field reproducible from a detached worktree — I used it in §3.
- *Two write-only dataclass fields* (**C-6**) — `_ParsedRow.row_number` and
  `SamplerRecord.interval_start_literal`. Delete both; a future maintainer would
  otherwise have to prove they are inert, as I did.
- *`--bundle` is marginal.* Because `build_payload` refuses any path other than
  `PINNED_BUNDLE_PATH`, the flag can only ever be passed its own default; it
  exists so `test_bundle_path_mismatch_refusal_reaches_main` can drive the
  refusal. That is a legitimate reason, but the `help=` string ("exact retained
  R03P path") does not say so. One clause — "must equal the pinned path; exists
  so the mismatch refusal is testable" — retires the question. Below nit level;
  recorded here rather than as a finding.
- *`SamplerRecord` as a frozen dataclass* rather than a tuple: earns it, the
  field names are the contract vocabulary.
- Nothing in the module is unreachable except the dropped `statistic_sample_empty`
  refusal that file 18 already dispositioned as removed-because-unreachable.

## What this review did NOT check

- **The physics/measurement lens.** Whether a 120.9 ms median record interval and
  a 5.95 ms IQR mean what the round-7 draft says they mean about the sampler,
  and whether these rows should be claim-bearing at all. Files 12 and 13 own that
  lens; I read them only for the four cured defects.
- **The round-7 draft.** The "sampler pauses" mechanism sentence the addendum says
  is "already scheduled for correction (parked structural edits)" — I did not
  verify that the parked edit exists or that the draft is consistent with the
  issued numbers. `docs/paper/draft-v2-skeleton.md` (+581 lines in this PR) was
  not reviewed.
- **Everything in the PR outside the DG-071 lane** — `joulewise/identity_pins.py`,
  `joulewise/adapters/mlx_runtime.py`, `scripts/run_night.py`,
  `docs/contracts/identity_pin_projection.md`, `docs/process/state_kernel.json`,
  README/RUN_STATE/TASK_QUEUE, and the `2026-09-02-projection-02` and
  `2026-09-02-coldgate-dx-t26a` traces. `git diff --stat a63d45bd..8ab397b5` is
  79 files; I reviewed 5 of them plus the dg071 trace.
- **Tests I was not authorized to run**: `tests.test_docs_freshness` and
  `tests.test_gen_state` (the PR's "Ran 70, OK" was verified by static method
  count only), and the canonical full-suite discover. CI status was not checked.
- **The registry itself.** Whether DG-071/DG-075 are still correctly held at
  STOP_FILL / VALUE_UNISSUED on `feat/2026-09-02-dx-registry`, and whether the
  round-7 fill sentences the addendum contemplates match the issued numbers.
- **Blind-seat independence.** I read file 15's contamination disclosure and took
  it at its word; I did not attempt to verify what that seat actually read.
- **The bundle's provenance.** I verified its SHA-256 against the pin and read it
  read-only; I did not audit how it was captured or whether it is the right
  bundle (the "cited-bundle multiplicity" hazard the ratification closes by
  path+SHA).
