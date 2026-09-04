# REFUTE-E — FACT-AND-REGISTRY lens (Opus, read-only)

Object: branch `feat/2026-09-02-paper-e` in `/Users/edr/code/JouleWise-wt-paper-e`, head
`0857bd59`, diffed against main `33290b8b`.
Brief: `docs/process_traces/2026-09-02-paper-e/00-brief.md`.
Seat report: `docs/process_traces/2026-09-02-paper-e/01-seat-E-landing-report.md`.
No writes were made under the checkout; the worktree was `git status --porcelain` clean
before and after this audit.

## Verdict

The five charges resolve as follows.

| Charge | Result |
|---|---|
| 1. Every §6 number traces to a MEASURED/ISSUED registry row or the PR #276 artifact, hashes recomputed, every digit compared | **SUSTAINED — not falsified.** 12 distinct numeric tokens, all traced; both SHA-256 digests recomputed and matching; all six statistics digit-identical. |
| 2. DG-071/DG-075 ISSUED flips complete and consistent everywhere referenced | **PARTIALLY FALSIFIED.** Registry, fill-checklist and CLAIMS_STATUS are consistent; two in-scope round-7 docs still assert the superseded `[PENDING]` state. |
| 3. Round-7 artifact fence passes | **SUSTAINED — not falsified.** `Ran 45 tests … OK`, exit 0, with the corpus root supplied as the charge specifies (E9). |
| 4. Diff touched nothing outside WRITE_SCOPE | **PARTIALLY FALSIFIED.** 6 of 8 changed files are in scope; 2 process-trace files are outside the enumerated WRITE_SCOPE. |
| 5. "No desk-computed number" holds | **SUSTAINED — not falsified.** Every numeral in the added prose appears verbatim in a registry row or the issued artifact; the only other numerals are cross-references ("Section 1", "Figure 5") and the ledger row count, which the shipped test derives mechanically. |

Findings: **0 blockers, 1 should-fix, 4 nits.**

---

## Findings

### SF-1 (SHOULD-FIX) — the landing report's recorded SHA-256 for the new SVG does not match the committed file

`docs/process_traces/2026-09-02-paper-e/01-seat-E-landing-report.md:195`

> The additional untracked SVG is 97 lines / 7,736 bytes, SHA-256
> `35edfb8bcc5ced0d12b2270f0120153c9e761d5067d7939ae58a7f5a70a1ddfc`.

Falsifying evidence — the committed blob and the working-tree file are the same bytes, and
both hash to a different digest, while the line and byte counts the report gives are exactly
right:

```
$ git status --porcelain                     # (empty — tree clean)
$ shasum -a 256 docs/paper/figures/fig5_phase_record_overlap.svg
6a5aed4e20996d8239b0b108fbb95943e393b8dfb011e59a1aa08b416aaed1b3  docs/paper/figures/fig5_phase_record_overlap.svg
$ wc -l -c docs/paper/figures/fig5_phase_record_overlap.svg
      97    7736 docs/paper/figures/fig5_phase_record_overlap.svg
$ git show 0857bd59:docs/paper/figures/fig5_phase_record_overlap.svg | shasum -a 256
6a5aed4e20996d8239b0b108fbb95943e393b8dfb011e59a1aa08b416aaed1b3  -
$ git show 0857bd59:docs/paper/figures/fig5_phase_record_overlap.svg | wc -l -c
      97    7736
```

Because the size and line count match to the byte while the digest does not, this is either a
mis-transcribed digest or a same-length edit made after the report was written; the report
gives no way to tell which. Under the standing rule that a packet fact labelled with a hash
must be reproducible at the bench, a recorded digest that does not reproduce is a custody
defect in the custodied report, independent of whether the figure itself is correct.

Blast radius is bounded: the SVG carries no measured value (verified — its only numerals are
the illustrative counts 2 and 3 and the rule minimum 3), it is not a fenced R7F artifact, and
no registry row or prose sentence depends on this digest. Nothing scientific turns on it.
The cure is to correct line 195 to the actual digest (or to re-state it after confirming no
post-report edit occurred). This is the only finding in this lens that asks for an edit.

### N-1 (NIT) — two in-scope round-7 documents still assert the superseded `[PENDING]` state

Charge 2 asks that the flips be consistent "everywhere they are referenced". They are not,
in two files that sit inside the brief's WRITE_SCOPE (`docs/paper/round7/`) and so could have
been corrected in this landing:

- `docs/paper/round7/prefill-resolvability-projection.md:190-195` — "Row DG-071 records record
  width as \"measured 111.8–112.5 ms\" and row DG-075 records spacing as 120.922 ms, with the
  difference attributed to a sampler pause… Both rows are `[PENDING]` in the draft, so nothing
  published is wrong yet; the supplier notes need correcting before those…"
- `docs/paper/round7/prefill-resolvability-projection.md:474-477` — "Registry rows DG-071 and
  DG-075 attribute the width/spacing difference to a pause… Both sites are `[PENDING]`, so
  nothing published is wrong, but the supplier notes need correcting before they are filled."
- `docs/paper/round7/survival-map.md:275-277` — "Consume `DG-067`–`DG-077`; render `DG-071` and
  `DG-075` with their exact registered omission sentences until their path- and SHA-pinned
  statistic artifacts issue."

All three sentences are now false or vacuous as written: the registry no longer records
111.8–112.5 ms as the width, no longer attributes anything to a pause, no longer marks either
row `[PENDING]`, and no longer carries the "registered omission sentences" the survival map
tells a writer to render.

Rated a nit rather than a should-fix for three reasons. The projection document is explicitly
framed as a dated evidence snapshot — its own header says its tables "remain valid as the
EVIDENCE that forced the ruling; they are not the binding rule" — and its stale sentences sit
in a section titled "Anomalies and corrections for the record", i.e. a record of what was true
when the anomaly was found. The survival-map sentence is a conditional whose antecedent
("until… artifacts issue") has now lapsed, so it directs no wrong action. And neither file
feeds a shipped gate or reader-facing prose. The seat's report is candid about the boundary it
drew — it claims only to have updated "the registry and round-7 fill checklist" — so this is
incomplete coverage honestly declared, not a misstatement.

### N-2 (NIT) — the diff includes two files outside the enumerated WRITE_SCOPE

WRITE_SCOPE is `[docs/paper/draft-v2-skeleton.md, docs/paper/results-fill-registry.md,
docs/paper/figures/, docs/paper/figures-plan.md, docs/paper/round7/,
docs/paper/fill-rehearsal/, tests/]`. Mechanical classification of the eight changed paths:

```
IN-SCOPE   docs/paper/draft-v2-skeleton.md
IN-SCOPE   docs/paper/figures-plan.md
IN-SCOPE   docs/paper/figures/README.md
IN-SCOPE   docs/paper/figures/fig5_phase_record_overlap.svg
IN-SCOPE   docs/paper/results-fill-registry.md
IN-SCOPE   docs/paper/round7/fill-checklist.md
OUT-SCOPE  docs/process_traces/2026-09-02-paper-e/00-brief.md
OUT-SCOPE  docs/process_traces/2026-09-02-paper-e/01-seat-E-landing-report.md
```

`docs/process_traces/` appears nowhere in WRITE_SCOPE. This is not attributable to the seat:
its own envelope declares a six-path `pathspec` that excludes both trace files, reports
`unowned_dirty: []`, and its recorded `git status` at hand-off lists exactly the six paper
files plus the untracked SVG. Its scope check ran the enumerated scope and returned
`SCOPE_OK; HEAD unchanged; 6 persistent paths in scope`. The two trace files are the brief and
the landing report themselves, added by the orchestrator when custodying the commit — the
commit subject says so ("brief (00) and landing report (01) custodied"). Recorded because
charge 4 asks for it, not as a seat violation.

### N-3 (NIT) — `docs/paper/fill-rehearsal-2026-08-27.md` still shows both rows as `[PENDING]`, and the report's disclaimer is narrower than it reads

The seat reports "No reference occurred under `docs/paper/fill-rehearsal/`." That is exactly
true of the *directory* (which holds only synthetic JSON fixtures and rendered outputs — zero
DG-071/DG-075 hits). But a same-stem *file*, `docs/paper/fill-rehearsal-2026-08-27.md`, does
carry both rows at lines 244-245, still describing them as "256, first/second diagnostic
`[PENDING]`" and "not reached; atomic stop occurred first".

No edit is warranted. That file is a dated record of what one rehearsal run actually did on
2026-08-27; "not reached; atomic stop occurred first" is a historical execution fact that
would be falsified, not corrected, by an update. It is also outside WRITE_SCOPE (the scope
names the directory `docs/paper/fill-rehearsal/`, not this sibling file), so the seat was right
not to touch it. Flagged only so the next reader does not mistake the report's directory-scoped
sentence for a repository-wide one.

### N-4 (NIT) — §6 restates §1's definition with one changed preposition, and introduces a timestamp/end-time equivalence it does not justify in the prose

Two small fidelity points in the new prose, neither a numeric defect:

1. `docs/paper/draft-v2-skeleton.md:919` opens "Section 1 introduced a sampling record as one
   sampler output that averages processor power from its recorded start time **through** its
   recorded end time." Section 1 (`:87-89`) says "**to** its recorded end time." The
   paraphrase is offered as a recall of §1, so the wording should match §1 exactly; the
   semantics are unchanged.
2. The prose renders DG-075 as "the 405 differences between consecutive records' **recorded
   end times**", whereas both the registry row and the artifact define the statistic over
   "consecutive unique/sorted distinct `timestamp_s` differences". The equivalence is real and
   producer-enforced — the artifact's tiling method requires each record's `interval_end_s`
   literal to be identical to its `timestamp_s` literal and refuses the bundle otherwise — but
   the prose never tells the reader that the timestamp *is* the end label, so a reader
   replicating from the text alone cannot see why a spacing statistic computed on timestamps
   is a statistic on end times. One clause would close it.

---

## Executed evidence

All commands run from `/Users/edr/code/JouleWise-wt-paper-e` unless shown otherwise.

### E1 — worktree identity and diff surface

```
$ git log --oneline -3
0857bd59 Paper seat E (Sol xhigh, audited): §6 printed negative result as reader-facing prose + fig5 overlap diagram; DG-071/DG-075 ISSUED in the registry; brief (00) and landing report (01) custodied
33290b8b NIGHT_HANDBACK: rehearsal-20260903 RE-ARM (fresh audit: daytime pulls moved canonical HEAD past the pinned repo_head — gate would refuse night_plan_stale; plan re-pinned to this commit, plists re-rendered, courier pin refreshed)
b81a2ac5 Merge pull request #274 from mpmdw/feat/2026-09-02-t26-liveness

$ git diff 33290b8b --stat
 docs/paper/draft-v2-skeleton.md                    |  88 ++++--
 docs/paper/figures-plan.md                         |   5 +
 docs/paper/figures/README.md                       |  17 +-
 docs/paper/figures/fig5_phase_record_overlap.svg   |  97 +++++++
 docs/paper/results-fill-registry.md                |  28 +-
 docs/paper/round7/fill-checklist.md                |  25 +-
 docs/process_traces/2026-09-02-paper-e/00-brief.md |  53 ++++
 .../2026-09-02-paper-e/01-seat-E-landing-report.md | 298 +++++++++++++++++++++
 8 files changed, 560 insertions(+), 51 deletions(-)

$ git status --porcelain
(no output — clean)
```

### E2 — CHARGE 1a: artifact digests recomputed

```
$ shasum -a 256 docs/paper/round7/dg071-dg075-statistics.md docs/paper/round7/dg071-dg075-statistics.json
041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b  docs/paper/round7/dg071-dg075-statistics.md
9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7  docs/paper/round7/dg071-dg075-statistics.json
```

Both match the digests quoted in `results-fill-registry.md:646`, `:650`, the registry
discrepancy note (`:540-547`), `round7/fill-checklist.md:254-258`, and the seat report's V3 —
character for character, in every one of those five placements.

### E3 — CHARGE 1b: every digit of n, median and IQR, prose vs artifact

From `docs/paper/round7/dg071-dg075-statistics.json` (`statistics` object):

```
"DG-071": { "sample_count": 406, "median_ms": "120.9186", "iqr_ms": "5.9508",
            "q1_ms": "116.9720", "q3_ms": "122.9227",
            "statistic": "interval_end_s - interval_start_s per sampler record" }
"DG-075": { "sample_count": 405, "median_ms": "120.9224", "iqr_ms": "5.8949",
            "q1_ms": "117.0321", "q3_ms": "122.9270",
            "statistic": "consecutive differences of sorted distinct timestamp_s literals" }
"sampler_record_count": 406,  "rail_row_count": 1218,  "tiling_gap_nonzero_boundaries": 100,
"max_tiling_gap_s": "0.0000004",
"input_bundle": { "path": "runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv",
                  "sha256": "6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9" }
```

| Value as printed in §6 prose | Artifact / registry authority | Digit-by-digit |
|---|---|---|
| `406` sampler records | `sampler_count`/`sample_count` DG-071 = 406; registry `:646` "n = 406" | match |
| median `120.9186` ms | `median_ms` DG-071 = "120.9186"; registry `:646` | match |
| IQR `5.9508` ms | `iqr_ms` DG-071 = "5.9508"; registry `:646` | match |
| `405` differences | `sample_count` DG-075 = 405; registry `:650` "n = 405" | match |
| median `120.9224` ms | `median_ms` DG-075 = "120.9224"; registry `:650` | match |
| IQR `5.8949` ms | `iqr_ms` DG-075 = "5.8949"; registry `:650` | match |

No transposition, no truncation, no rounding drift; the prose reproduces the four-decimal
millisecond rendering the artifact's `millisecond_rendering` note declares authoritative.
The prose's qualitative tiling claim ("each support begins where the preceding record ends,
apart from an endpoint convention in which separately rounded time labels can differ in their
final printed digit") is backed by the artifact's `tiling` note: 100 of 405 boundaries have a
nonzero gap, the largest `0.0000004` s, on files written with 1e-7 s literals — i.e. the
seventh and final printed decimal. The prose omits those two numbers but asserts nothing they
contradict.

### E4 — CHARGE 5: exhaustive numeral sweep of the added prose

Every added line of `docs/paper/draft-v2-skeleton.md` was extracted and every numeric token
counted:

```
$ git diff 33290b8b -- docs/paper/draft-v2-skeleton.md | grep '^+' | grep -v '^+++' | sed 's/^+//' > added.txt
$ grep -oE '[0-9][0-9,.]*' added.txt | sort | uniq -c | sort -rn
   2 50
   2 5.
   2 37
   2 13
   2 0.121
   1 5.9508
   1 5.8949
   1 5,
   1 5
   1 406
   1 405
   1 227
   1 2
   1 120.9224
   1 120.9186
   1 1
   1 0.121034145
   1 0.
```

Disposition of every token:

| Token | Authority | Status |
|---|---|---|
| `0.121034145` | registry DG-070 (`:645`), value `0.121034145 s`, MEASURED-class DERIVE | traced |
| `0.121` (×2) | registry DG-074 (`:649`), value `0.121` | traced |
| `406` | artifact DG-071 `sample_count`; registry `:646` | traced |
| `120.9186`, `5.9508` | artifact DG-071 `median_ms`, `iqr_ms`; registry `:646` | traced |
| `405` | artifact DG-075 `sample_count`; registry `:650` | traced |
| `120.9224`, `5.8949` | artifact DG-075 `median_ms`, `iqr_ms`; registry `:650` | traced |
| `37` (×2) | registry DG-076 (`:651`) two-overlap population = 37, and DG-067 (`:642`) not-resolvable = 37 | traced (two independent rows back the two distinct assertions) |
| `13` (×2) | registry DG-077 (`:652`) three-overlap = 13, and DG-069 (`:644`) identifiable = 13 | traced |
| `50` (×2) | registry DG-068 (`:643`) bundle count = 50 | traced |
| `2` (spelled and numeric), `three` | registry DG-072 (`:647`) "two; 2" and DG-073 (`:648`) "three; 3" | traced |
| `227` | ledger audit sentence, not reader-facing prose; the shipped test derives it — see E5 | traced |
| `5.`, `5,`, `5`, `1`, `0.` | residual matches inside "Figure 5", "Figure 5.", "fig5_phase_record_overlap.svg", "Section 1", and the decimal points of the values above — confirmed by locating each line | not quantities |

Line-level confirmation that no unlisted numeral hides in the residue:

```
$ grep -nE '(^|[^0-9.])[125](\.|,|$|[^0-9])' added.txt | grep -v '120\.9\|0\.121\|5\.9508\|5\.8949\|406\|405\|227\|37\|13\|50'
1:Section 1 introduced a sampling record as one sampler output that averages
18:Figure 5, the phase–record overlap diagram, names the phase edges, tiled record
22:![Figure 5. Phase–record overlap diagram.](figures/fig5_phase_record_overlap.svg)
24:*Figure 5. Phase–record overlap diagram. The two rows apply the positive-time
58:prefill length selected by G2-a before collection rather than reusing this
```

All five are cross-references. **The seat's "no desk-computed number" claim holds.** The
arithmetic identities the prose relies on (37 + 13 = 50; 406 − 1 = 405) are each independently
registered rather than computed: 50 is DG-068, 13 is DG-069/DG-077, and the 405/406 relation is
stated in the registry row itself ("the DG-071 record-period distribution minus the first
record") and in the artifact's `dg075_dependence` note.

No `[FILL:…]`, `[PENDING]` or `STOP_FILL` marker survives inside the rewritten §6 prose; the
nearest such markers (`[FILL:V5-ID-001]`, `[FILL:V5-WL-001…003]`) are at `:982-985`, inside the
following section, which this diff did not touch.

### E5 — the ledger count `227` is mechanically derived, not asserted

`docs/paper/draft-v2-skeleton.md:1830` changed from "Terms inventoried: 224; FAILS: 0." to
"Terms inventoried: 227; FAILS: 0." The shipped test binds that integer to the parsed row
count rather than to a human count
(`tests/test_paper_first_use_ledger.py:137-141`):

```python
count_sentences = re.findall(r"Terms inventoried: (\d+); FAILS: (\d+)\.", self.text)
self.assertEqual(len(count_sentences), 1, "expected one mechanical count sentence")
row_count, fail_count = map(int, count_sentences[0])
self.assertEqual(row_count, len(self.rows))
self.assertEqual(fail_count, len(failures))
```

The diff replaces one ledger row with four, i.e. +3 rows, and 224 + 3 = 227. Consistent, and
enforced. (Observation only, pre-existing and out of this lens's charge: the sentence says
"Terms inventoried" while the test counts *rows*, and each row may hold several
slash-separated terms — the replaced row carried 4 terms and the four new rows carry 11, so the
sentence's noun is looser than its number. The seat inherited this wording; it did not
introduce it.)

### E6 — CHARGE 2: completeness of the ISSUED flip

Every file in the repository mentioning either row was enumerated
(`grep -rln 'DG-071\|DG-075' . --exclude-dir=.git`, 62 files). Excluding
`docs/process_traces/` (historical seat records) the live surfaces are:

| Surface | State after the diff |
|---|---|
| `docs/paper/results-fill-registry.md:646` (DG-071 row) | `ISSUED`, value `n = 406; median 120.9186 ms; IQR 5.9508 ms`, both artifact paths + both SHA-256 pins, `ISSUED_ARTIFACT (PR #276); DIAGNOSTIC_ERA; NON_CLAIM_BEARING` — consistent |
| `docs/paper/results-fill-registry.md:650` (DG-075 row) | same shape, `n = 405; median 120.9224 ms; IQR 5.8949 ms` — consistent |
| `docs/paper/results-fill-registry.md:540-547` (discrepancy note) | rewritten to record the PR #276 issuance with both digests — consistent |
| `docs/paper/results-fill-registry.md:911` (open-gaps table) | flipped to "RESOLVED by PR #276" — consistent |
| `docs/paper/results-fill-registry.md:969-971` (lead checklist) | flipped from "Ratify or replace… before either fill" to "Keep… bound to the exact… paths and SHA-256" — consistent |
| `docs/paper/round7/fill-checklist.md:254-258` (Batch 4 preamble) | flipped to "issued by PR #276", both digests quoted — consistent |
| `docs/paper/round7/fill-checklist.md:266-267` (placement rows) | carry the issued n/median/IQR verbatim — consistent |
| `docs/paper/round7/fill-checklist.md:378-379` (pending census) | 37 → 35, and the printed banner updated to match — verified in E7 |
| `docs/paper/round7/fill-checklist.md:401-406` (open gaps) | the "Diagnostic issuance" gap deleted and items renumbered 5,6 with no gap or duplicate — consistent |
| `CLAIMS_STATUS.md` | zero occurrences of either row id — nothing to flip, no stale state |
| `docs/paper/fill-rehearsal/` (directory) | zero occurrences — the seat's claim is exactly true of the directory |
| `docs/paper/round7/prefill-resolvability-projection.md:190-195, 474-477` | **still asserts `[PENDING]` and the retired pause mechanism — N-1** |
| `docs/paper/round7/survival-map.md:275-277` | **still directs rendering "registered omission sentences… until… artifacts issue" — N-1** |
| `RUN_STATE.md:35`, `TASK_QUEUE.md:673,814`, `docs/process/state_kernel.json:1295` | mention the rows only as the subject of the follow-on provenance-test task A94; no `[PENDING]`/`STOP_FILL` status assertion — no stale state |

The old omission sentences the registry used to mandate ("The sampling-record width is
omitted: its median-with-IQR statistic is ratified but not issued…") are fully gone from the
draft:

```
$ grep -n 'is omitted: its median-with-IQR' docs/paper/draft-v2-skeleton.md
(no output)
```

Informational, not a finding: `docs/process_traces/2026-08-31-registry-v5/01-verify-registry-v5.py:180-187`
asserts that both rows contain `VALUE_UNISSUED`, which would now fail if re-run. It is a
one-shot change-record verifier pinned to the 2026-08-31 registry-v5 transition — it also
asserts `DRAFT_LINES 672` and `KEY_CENSUS old=109 new=126` for that specific diff — it lives
under `docs/process_traces/`, is not in `tests/`, is not part of the paper suite, and is
referenced by no live gate. Re-running it is not expected and its failure would not indicate a
defect in this branch.

### E7 — the fill-checklist's own pending census re-derived independently

The checklist's embedded assertion was changed from 37 to 35. Re-running its regex against the
edited registry:

```
$ python3 - <<'PY'
import re
registry = open('docs/paper/results-fill-registry.md',encoding='utf-8').read()
n = len(re.findall(r"^\| (?:DS|PG|DG)-[0-9]+[a-z]? — .*[[](?:PENDING|RESULT PENDING ISSUED ARTIFACTS|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)", registry, re.M))
print("RF PENDING CENSUS ACTUAL:", n, "| checklist asserts 35 ->", "MATCH" if n==35 else "MISMATCH")
PY
RF PENDING CENSUS ACTUAL: 35 | checklist asserts 35 -> MATCH
```

Two rows left the `[PENDING]` census, 37 − 2 = 35, and both the assertion and its printed
banner were updated together.

### E8 — the figure carries no measured value

Every text node in `docs/paper/figures/fig5_phase_record_overlap.svg`:

```
Phase-record overlap count and the three-record minimum
A fully labelled schematic with two time-axis rows. Three gray rectangles in each row are tiled sampler-record supports. A blue prompt-processing interval has labelled start and end edges. Dark-blue portions show positive overlap. The upper row overlaps two supports and is not resolvable; the lower row overlaps three and is resolvable. Counts illustrate the rule, while all widths and positions are not to scale and contain no measured timing values.
Figure 5. Phase–record overlap is a count of shared time intervals
Rule schematic: counts illustrate the fixed rule; widths and edge positions are not to scale; no measured timing value is shown.
Two-support example — below the minimum
time axis (illustrative; not to scale)
record support R1 / sampler average over start–end
record support R2 / sampler average over start–end
record support R3 / sampler average over start–end
tiled supports: adjacent rectangles share a boundary; there is no drawn pause
prompt-processing interval
phase start edge
phase end edge
blue segment = positive overlap
overlap count = 2
2 < minimum 3
not resolvable
Three-support example — meets the minimum
[same label set repeated]
overlap count = 3
meets minimum 3
resolvable
Fixed decision rule: count record supports that share positive time with the phase; require at least three.
```

The only numerals are `R1/R2/R3` identifiers, the illustrative counts 2 and 3, and the rule
minimum 3. The prose caption's claims are therefore true as written: "Every rectangle, edge,
shared portion, count, decision, and axis is labelled" (each has a text node, including both
time axes), and "the diagram contains no measured timing value" (no time axis tick values, no
durations). The figure is registered in `docs/paper/figures-plan.md:248-252` and described in
`docs/paper/figures/README.md:63-74`, and the README's "Three… figures" was correctly updated
to "Four" in both places it appears.

### E8b — the two artifact files agree, and every abbreviation the flipped rows use resolves

The registry rows cite both artifact files; their values agree with each other, so a reader
following either path lands on the same numbers
(`docs/paper/round7/dg071-dg075-statistics.md:34-35`):

```
| DG-071 | 406 | 116.9720 | 120.9186 | 122.9227 | 5.9508 |
| DG-075 | 405 | 117.0321 | 120.9224 | 122.9270 | 5.8949 |
```

Every column matches the JSON's `statistics` object field for field, including the two
quartiles the prose does not print. The Markdown header also independently states "Sampler
records: 406" (`:5`).

Both abbreviations the flipped rows introduce are defined in the registry's own exact-path
block (`docs/paper/results-fill-registry.md:553-570`; `NR` at `:561`, `R03P` at `:563`):

```
- NR   = docs/process_traces/2026-08-09-prefill-phase-proof/results.json
- R03P = /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv
```

`R03P` resolves to exactly the artifact's pinned `input_bundle.path`
(`runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`, SHA-256
`6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`), so the rows' "over every
retained record in R03P" and the artifact's input pin name the same bytes. This matters because
`prefill-resolvability-projection.md:481-484` records that the bundle *name*
`p2015-df-ph-decode-abs-r03` resolves five ways across retained corpora with prefill durations
from 0.1210 s to 0.1374 s; the corpus-rooted abbreviation plus the artifact's input SHA-256
disambiguate it, and the §6 prose never names the bundle at all, so the ambiguity is not
exposed to the reader.

### E9 — CHARGE 3: round-7 artifact fence

```
$ cd /Users/edr/code/JouleWise-wt-paper-e && R7F_CORPUS_ROOT=/Users/edr/code/JouleWise \
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_round7_artifacts
.............................................
----------------------------------------------------------------------
Ran 45 tests in 609.261s

OK

[exited with code 0]
```

**The round-7 artifact fence passes on this branch: 45 tests, `OK`, exit code 0, zero
failures, zero errors, zero skips.** Charge 3 is sustained, not falsified.

This independently corroborates the seat's V4 (`R7F COMPARED 184 / MISMATCHES 0` via
`scripts/check_paper_round7_artifacts.py --corpus-root /Users/edr/code/JouleWise`) by the route
the charge specified, and it confirms the seat's reasoning that no fence pin needed re-cutting:
the diff placed no DX marker (the `R7F PLACED 0/16` count is unchanged) and altered no pinned
XD/AQ/F4 source or producer script. Note that the corpus root must be supplied — the seat's V5
recorded exit 3 (`R7F CORPUS UNAVAILABLE`) for the bare command, which is an artifact of running
inside an isolated worktree that does not carry the retained corpora, not a defect. The
`R7F_CORPUS_ROOT` form required by this charge is the correct invocation there, and it passes.

### E10 — CHARGE 4: WRITE_SCOPE classification

```
$ git diff --name-only 33290b8b | while read f; do case "$f" in
    docs/paper/draft-v2-skeleton.md|docs/paper/results-fill-registry.md|docs/paper/figures/*|\
    docs/paper/figures-plan.md|docs/paper/round7/*|docs/paper/fill-rehearsal/*|tests/*)
      echo "IN-SCOPE   $f";; *) echo "OUT-SCOPE  $f";; esac; done
IN-SCOPE   docs/paper/draft-v2-skeleton.md
IN-SCOPE   docs/paper/figures-plan.md
IN-SCOPE   docs/paper/figures/README.md
IN-SCOPE   docs/paper/figures/fig5_phase_record_overlap.svg
IN-SCOPE   docs/paper/results-fill-registry.md
IN-SCOPE   docs/paper/round7/fill-checklist.md
OUT-SCOPE  docs/process_traces/2026-09-02-paper-e/00-brief.md
OUT-SCOPE  docs/process_traces/2026-09-02-paper-e/01-seat-E-landing-report.md
```

See N-2: the two out-of-scope paths are the brief and the landing report, custodied by the
orchestrator, and are excluded from the seat's own declared `pathspec`.

### E11 — §1 cross-reference checked verbatim

```
$ sed -n '86,89p' docs/paper/draft-v2-skeleton.md
This capstone asks a measurement question before it asks a model-comparison
question. macOS `powermetrics` is the power sampler used here. A sampling record
is one sampler output that averages processor power from its recorded
start time to its recorded end time. A phase edge is the runtime time that
```

§6 recalls this as "…from its recorded start time **through** its recorded end time" — see
N-4.1. Semantics unchanged; wording differs by one preposition.

---

## What this lens did NOT find

Stated so the next reviewer does not re-spend on it:

- No numeric error anywhere in the new §6 prose. All 12 quantities reproduce their sources
  exactly.
- No hash error in the registry or the fill-checklist. Both artifact digests reproduce, in all
  five placements.
- No orphan or fabricated registry citation: DG-067 through DG-077 all exist, all carry the
  claimed values, and the two flipped rows carry a coherent ISSUED status quartet
  (value / supplier+pins / class / consumers).
- No reader-facing internal shorthand introduced by this diff: no registry row id, decision id,
  campaign codename, or seat name appears in the new prose. `G2-a` does appear (`:976`) but is
  a pre-existing built term with a ledger row at `:1612` and a bold definition at `:891`,
  well before its §6 use; the brief's own build note prescribed that sentence.
- No cross-run splice. The prose attributes the 0.121034145 s duration and the 406-record
  width/spacing statistics to one and the same "retained run". That holds: DG-070's supplier is
  `NR#bundles[bundle=p2015-df-ph-decode-abs-r03].boundary.prefill_duration_s` and DG-071/DG-075
  are computed over `R03P`, the `power_trace.csv` of that same bundle id under the same corpus
  root. A statistic quietly taken from a different bundle than the duration would have been the
  most damaging defect available here, and it is not present.
- No claim-bearing leakage: the prose states the diagnostic-era, non-claim-bearing status and
  the forbidden conclusions ("does not show zero prompt-processing energy, make a model
  comparison, or establish a limitation of the prospective demonstration") in line with both
  flipped rows' `DIAGNOSTIC_ERA; NON_CLAIM_BEARING` class.
