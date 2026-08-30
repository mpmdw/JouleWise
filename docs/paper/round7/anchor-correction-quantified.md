# How far did the corrected clock model move the calibration bound?

**Round-7 desk analysis, reviewer item 11.** Supporting material for the paper;
not a claim, and not part of the frozen draft.

Every number in this document comes from
`docs/paper/round7/anchor-correction-quantified.json`, which is produced by:

```
/Users/edr/code/JouleWise/.venv/bin/python \
    scripts/paper_anchor_correction_quantified.py \
    --corpus-root /Users/edr/code/JouleWise \
    --out docs/paper/round7/anchor-correction-quantified.json
```

The run takes about six and a half minutes, reads roughly 1.3 GB of retained
instrument traces, and writes byte-identical output on repeat runs.

---

## 1. The question, and why a reviewer asked it

A reviewer of the frozen draft put the problem this way:

> The ratios that motivate the entire paper were computed with the estimator
> whose error the paper's first contribution fixes … report, over the retained
> diagnostic captures, the distribution of `B_fiducial` change under
> re-derivation with the corrected model. That both defends the diagnostic
> ratios and honestly sizes contribution #1, which as written implies a
> correction whose numerical effect on the published bound may be under 4 % and
> whose real effect was on *admissibility*.

The concern is circularity. The paper's first contribution is a repair to one
estimator. The measurements that motivate the paper were taken *before* that
repair, using the broken estimator. So either the repair barely changed those
measurements — in which case the reader is entitled to ask what the contribution
is worth — or it changed them a lot, in which case the reader is entitled to ask
why the pre-repair measurements are shown at all. Neither answer can be given
without doing the arithmetic, and the draft as frozen does not do it.

This document does it, on every retained capture.

---

## 2. The four terms this analysis rests on

**The clock anchor.** The `powermetrics` tool reports power samples on its own
internal timeline. The experiment issues its commands on the operating system's
wall clock. To compare the two, something must decide *which instant of wall
clock time the first row of the trace corresponds to*. That decision is the
clock anchor, and the procedure that makes it is the anchor estimator. If the
anchor is wrong by 5 ms, then every event in the trace — these captures hold
about 1,660 samples each — is misplaced by 5 ms relative to the commands that
caused it.

Two anchor estimators appear below. They are identified in the code and in the
JSON by exact strings, and this document uses short names for them:

| short name | identity string in the evidence files | what it assumes |
| --- | --- | --- |
| **v2 anchor** | `powermetrics_native_second_censored_intersection_v1` | the instrument's internal clock advances at exactly the same rate as the wall clock; only the *offset* between them is unknown |
| **v3 anchor** | `powermetrics_native_second_rate_aware_set_membership_v1` | both the *offset* and the *rate* between the two clocks are unknown and must be bounded from evidence |

The v3 anchor is the paper's first contribution. Every capture in the population
below was stamped, on the day it was taken, by the v2 anchor.

**`B_fiducial`, the calibration bound.** Each capture runs a fixed protocol: 59
commanded power pulses, each with a switch-on edge and a switch-off edge, so 118
edges in all. For every edge the analysis measures the disagreement between when
the pulse was *commanded* and when the trace *shows* it. `B_fiducial` is the
largest of those 118 disagreements, widened by the anchor term (defined next),
and reported in seconds. It is a bound, not an average: it says *the instrument's
timeline is pinned to the experiment's timeline to within this much, worst case*.
Smaller is better.

**The anchor term.** The anchor estimator does not return a single instant. It
returns an interval of instants that the evidence cannot rule out. The width of
that interval is the anchor term (`effective_clock_anchor_bound_s` in the JSON),
and it is added to the worst edge disagreement to form `B_fiducial`. So

> `B_fiducial` = (worst of the 118 edge disagreements) + (anchor term).

**Admissible.** A capture is *admissible* when its calibration evidence can be
used at all: the anchor estimator must return a bounded interval rather than
giving up, all 59 commanded pulses must be found in the trace, and the detector
must return no refusal reasons. A capture that fails any of those is refused. A
refusal is a result, not a gap in the data — it is the analysis saying *this
capture cannot be trusted to time anything* — and it is reported separately from
the numbers below rather than being dropped silently.

---

## 3. Method: three numbers per capture, and why the third one is needed

For each capture the script produces:

| name | what it is |
| --- | --- |
| `stored` | the `B_fiducial` written into `instrument_evidence.json` on capture day, by the v2 anchor and the detector code of that day |
| `rederived_v2` | `B_fiducial` recomputed **today**, from the same retained bytes, holding the anchor at v2 |
| `rederived_v3` | `B_fiducial` recomputed **today**, from the same retained bytes, under the corrected v3 anchor |

The reviewer's question is about `rederived_v3` minus `stored`. But that
difference on its own cannot tell the anchor correction apart from any unrelated
drift in the detector code between capture day and today. Both changes would show
up in the same subtraction.

`rederived_v2` is the control that separates them. It runs today's code at the
old anchor. If `rederived_v2` equals `stored` to the last bit, the detector is
unchanged and the whole difference is attributable to the anchor model. The
script checks that equality per capture and reports it rather than assuming it.

**Control result: it holds.** On all 14 captures where the v2 anchor resolves at
all, `rederived_v2` equals `stored` exactly — identical binary64 values, not
merely close. (The fifteenth capture, `20260722T213749-563b9849`, is refused by
the v2 anchor too, so there is nothing to compare; it is discussed in §6.) The
recorded detector identity, `joint_loss_sublevel_interval_branch_v2`, is also
still the current one in the code. Every difference reported below is therefore
the anchor model and nothing else.

### Reproduction gate

The frozen draft prints one calibration bound, for the worked capture
`20260722T145535-e941c821`. The script refuses to write any output unless its v3
path reproduces that value exactly:

| quantity | value |
| --- | --- |
| frozen draft prints | `0.030067931757111657` |
| this script's v3 re-derivation | `0.030067931757111657` |
| matches exactly | **yes** |

This is a hard stop, not a diagnostic. If the script cannot reproduce the one
number the draft publishes, it is not computing what the draft computed, and none
of its other numbers would mean anything.

---

## 4. Per-capture results

All values in milliseconds. The delta is signed: positive means the v3 anchor
produced a **larger** (more conservative, worse-looking) bound.

| capture | stored `B_fiducial` (v2 anchor) | v3 `B_fiducial` | delta | delta |
| --- | ---: | ---: | ---: | ---: |
| `20260722T145535-e941c821` | 30.190 | 30.068 | -0.122 | -0.40 % |
| `20260722T194118-9dc0749d` | 26.301 | 27.365 | +1.064 | +4.05 % |
| `20260722T213749-563b9849` | 207.918 | refused (`anchor_unresolved`) | — | — |
| `20260722T214220-1acdbbc0` | 33.120 | 32.898 | -0.222 | -0.67 % |
| `20260722T215127-eeef661a` | 22.741 | 23.175 | +0.434 | +1.91 % |
| `20260722T222332-901c5c13` | 33.559 | refused (`anchor_unresolved`) | — | — |
| `20260722T232509-82642517` | 27.654 | 28.745 | +1.091 | +3.94 % |
| `20260723T023058-8732d1c9` | 24.753 | 25.550 | +0.796 | +3.22 % |
| `20260723T052051-d9358c8a` | 25.965 | 26.113 | +0.148 | +0.57 % |
| `20260723T183306-4ce692b4` | 27.262 | refused (`anchor_unresolved`) | — | — |
| `20260723T194632-d04e038e` | 24.593 | 25.120 | +0.527 | +2.14 % |
| `20260723T195730-bc4ba14a` | 25.305 | 25.463 | +0.158 | +0.62 % |
| `20260723T221449-e9ae755e` | 27.703 | 27.201 | -0.501 | -1.81 % |
| `20260723T223406-314f6d9e` | 26.174 | 25.993 | -0.180 | -0.69 % |
| `20260724T014109-57844352` | 25.476 | 25.627 | +0.151 | +0.59 % |

Every capture in the population is stamped with the v2 anchor; there is no
second, already-corrected group to separate out. All 15 have their retained raw
bytes available and hash-verified, so none was dropped as un-re-derivable.

---

## 5. The distribution: the numerical effect is small

Over the 12 captures that the v3 anchor admits (`n = 12`):

| statistic | relative change | absolute change |
| --- | ---: | ---: |
| minimum | -1.81 % | -0.501 ms |
| first quartile | -0.47 % | -0.136 ms |
| **median** | **+0.61 %** | **+0.154 ms** |
| third quartile | +2.41 % | +0.594 ms |
| maximum | +4.05 % | +1.091 ms |
| inter-quartile range | 2.88 points | 0.731 ms |
| largest change in either direction | 4.05 % | 1.091 ms |
| direction | 8 up, 4 down, 0 unchanged | |

The reviewer's estimate was right in magnitude. The correction moves the
published-style bound by well under half a percent at the median, and never by
more than 4.05 % or 1.1 ms on any capture it admits. It moves the bound in both
directions, so it is not a uniform inflation or a uniform shrinkage.

### Why the bound sometimes gets *smaller*

The v3 anchor is the more conservative estimator: on 11 of the 12 admitted
captures its anchor term is *wider* than v2's — it admits more uncertainty about
where the first sample sits. Yet four of those captures end up with a smaller
total bound. That is not a contradiction, and the worked capture shows the
arithmetic:

| component of `B_fiducial`, capture `20260722T145535-e941c821` | v2 anchor | v3 anchor |
| --- | ---: | ---: |
| anchor term | 0.982 ms | 1.135 ms |
| worst of the 118 edge disagreements (the remainder) | 29.208 ms | 28.933 ms |
| **total `B_fiducial`** | **30.190 ms** | **30.068 ms** |

Re-anchoring does not merely add a wider safety margin. It slides the
instrument's entire timeline relative to the experiment's, which changes all 118
edge disagreements. Here the worst edge disagreement fell by 0.275 ms while the
anchor term grew by 0.153 ms, so the total fell by 0.122 ms. The bound went down
even though the estimator became more honest about the clock.

---

## 6. The real effect was on admissibility

This is the finding, and it is the part the frozen draft does not say.

| population | count |
| --- | ---: |
| retained captures | 15 |
| raw bytes present and hash-verified (re-derivable) | 15 |
| admissible as stamped on capture day (v2 anchor) | 14 |
| still admissible under the v3 anchor | 12 |
| **admissibility flips** | **2** |
| direction of every flip | admitted by v2, **refused** by v3 |

Two of the fourteen captures that the v2 anchor declared valid —
`20260722T222332-901c5c13` and `20260723T183306-4ce692b4` — are refused outright
by the corrected estimator. That is one in seven of the captures the old pipeline
was willing to use. No capture flips the other way: the correction never rescues
a capture, it only rejects.

A third capture, `20260722T213749-563b9849`, is refused by *both* estimators. It
was already marked `invalid` on capture day with an unresolved clock anchor, and
its stored bound of 207.918 ms is a degraded artefact of that failure rather than
a measurement. It is not an admissibility flip; it was never admissible.

### What the refusal actually is

All three refusals carry the same cause, recorded in the JSON as
`affine_clock_fit_empty`:

> The v3 estimator looks for a straight-line relation between the instrument's
> internal monotonic clock and the wall clock — a constant offset plus a
> constant rate ratio, one rate for the whole capture with no mid-capture step.
> That line must be consistent with *every* whole-second label the instrument
> emitted and every causally-bracketed timestamp taken during the capture, where
> each whole-second label is allowed to sit up to 250 µs off the line (a fixed
> allowance, charged in full rather than fitted). For these three captures no
> such line exists: the constraints are mutually contradictory, no
> (offset, rate) pair satisfies all of them even with the 250 µs slack, so the
> solution set is empty and the estimator refuses to return an anchor. That is
> the `affine_clock_fit_empty` condition.

The v2 estimator could not detect this, because it never solved for a rate. It
assumed the rate ratio was exactly 1 and solved only for the offset, and an
offset-only problem still had a solution. The evidence that the two clocks were
drifting apart was present in the retained bytes the whole time; the old
estimator had no term in which to express it, and so returned a confident number
instead of an error. For `20260722T222332-901c5c13`, that confident number was an
anchor term of 4.533 ms — the widest in the population, and in hindsight the old
estimator straining against evidence it could not represent.

**This is the honest size of contribution #1.** On the captures it accepts, the
corrected anchor moves the calibration bound by a median of 0.61 % and at most
4.05 % — a small numerical correction. Its consequential effect is that it
detects a class of clock-drift failure the old estimator was structurally unable
to see, and rejects 2 of 14 previously-accepted captures because of it. The
contribution is a change in what counts as admissible evidence, not a change in
the third decimal place of a published bound. A paper that presents it as the
latter undersells it and invites exactly the circularity objection the reviewer
raised.

---

## 7. Standing of these numbers

**The energy values from this era are voided for claim use.** Decision D-078
voided claim use of every `powermetrics` energy corpus collected before the
time-anchor repair, precisely because of the defect analysed here. Nothing in
this document un-voids them, and no energy figure appears in it. The population
is used only as *pilot* evidence — evidence about the behaviour of the anchor
estimators themselves, on retained bytes whose custody hashes still verify. The
quantities compared here (`B_fiducial`, the anchor term) are properties of the
timing calibration, not of any energy result.

What this analysis does establish is narrower and sound: on the retained
population, the correction the paper contributes is numerically small where it
applies, and its real work is refusing captures that the previous estimator could
not tell were broken.

**Custody.** The raw `powermetrics` traces (~88 MB each, 1.31 GB in total) are
not stored in git. The evidence file for each capture lives under
`runs/instrument_validation/`, but the trace bytes themselves sit in the
per-window run directory the capture was taken in. The script searches every
`runs*` directory in the corpus root, plus the iCloud backup mirror as a
fallback, and accepts a file **only** if its SHA-256 matches the hash recorded in
that capture's `instrument_evidence.json`. A file that does not match is never
used, however plausibly it is named.

All 15 were located and verified, and in this run every one resolved inside the
repository — the backup mirror was not needed:

| source directory | captures |
| --- | ---: |
| `runs_window_a5_20260723` | 3 |
| `runs_window_a4_20260722`, `runs_window_a6_20260723`, `runs_window_a7_20260723`, `runs_window_a8_20260723` | 2 each |
| `runs`, `runs_window_a_20260722`, `runs_window_a2_20260722`, `runs_window_a3_20260722` | 1 each |

Each capture's `events.jsonl` is likewise hash-checked against the evidence
before use. The exact paths, hashes, and byte counts are in the JSON under
`primary_bytes`.

---

## 8. Open remainder, not approximated

The reviewer's phrasing tied this analysis to three ratios that appear in the
draft — **10.92, 5.92, and 7.02**. Those are floor-level quantities: they derive
from the extracted phase energy floors, not from the calibration bound this
document re-derives. **This analysis does not recompute them, and does not offer
an estimate of how the corrected anchor would move them.**

Doing so honestly requires re-extracting the phase floors under the v3 anchor,
which is a separate piece of work with its own inputs and its own gates. It is
recorded here as an open item so that no reader takes the small deltas in §5 as
implying small deltas in those ratios. They are different quantities computed
from different intermediate products, and the relationship between them has not
been established. Extrapolating from one to the other would be exactly the kind
of unearned inference this analysis exists to remove.

---

## 9. Files

| file | contents |
| --- | --- |
| `scripts/paper_anchor_correction_quantified.py` | the analysis; deterministic, sorted-key JSON output |
| `docs/paper/round7/anchor-correction-quantified.json` | per-capture rows and the summary; source of every number above |
| `docs/paper/round7/anchor-correction-quantified.md` | this document |

Related: `scripts/paper_excursion_decomposition.py` and
`docs/paper/round7/excursion-decomposition.md` decompose the worked capture's
30.068 ms bound into its per-edge components. This document reuses that script's
re-derivation approach and reproduces its calibration gate value exactly.
