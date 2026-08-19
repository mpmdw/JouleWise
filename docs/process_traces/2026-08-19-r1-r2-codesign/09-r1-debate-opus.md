# R1 DEBATE — ROUND 1 — OPUS SEAT

Read-only at `9f7f091`, worktree `wtTXN`; `git status --short` empty at start and
end; probe scratch removed. All four new experiments below were executed by me
this round.

**Scorecard:** 1 AMEND (conceding terra's substance), 1 MAINTAIN (executed
refutation stands), 1 CONCEDE (new evidence flipped me), 1 SPLIT (both censuses
were incomplete; terra found a site class I missed), 1 MAINTAIN (now proven by
execution). Plus one off-agenda blocker.

---

## Item 1 — REFUSAL VOCABULARY → **AMEND (concede terra's substance)**

Terra is right, and I can now show it is right *empirically* rather than
rhetorically.

**Executed census (E1)** — every `uncertainty_evidence` envelope under
`/Users/edr/code/JouleWise` (1378 total, `os.walk` + JSON parse):

```
745  ('p2-038.2', clock_anchor.status='bounded')
622  ('p2-038.1', 'bounded')
  3  ('p2-038.2', 'unknown')
  8  (no schema_version — trimmed test fixtures)
```

**745 of 748 stored anchor-v2 bundles (99.6%) carry
`clock_anchor.status: "bounded"`** with a numeric admissible interval. Emitting
`clock_anchor_unresolved` against those bundles is not loose wording — it is a
published refusal record that **contradicts the artifact's own published
metadata**. Refusals are reportable results (`CLAIMS_STATUS.md:33-35`: analysis
"preserves refusals as reportable results"), and the reader of that record is a
metrology-expert advisor. Terra's semantic-falseness charge lands.

**Why my precedent argument does not save reuse.** I would have cited
`inputs.py:3671-3678` and `:3696-3700`, where the codebase already reuses
`clock_anchor_unresolved` for supersession and even annotates the mismatch in
comments. But those reuses are *not* analogous: pre-anchor wires
(0.4.x/0.5.0/0.6.0) predate the anchor repair entirely, so "unresolved" is
substantively true of them. For a bounded anchor-v2 record it is false. Reuse
there is defensible; reuse here is a contradiction. Precedent-by-debt is not
precedent-by-ruling.

**Where I correct terra: the cost is lower than "a D-078 closed-registry touch."**
The barrier lives in engine code, not on the reducer wire, so the reason belongs
in `ENGINE_REASON_CODES`, **not** in the D-057/D-078 `REDUCER_REASON_CODES`
vocabulary that terra's phrasing implies. **Executed price check (E2)** — the
registration sites are exactly four, all additive:

| # | Site | Addition |
|---|---|---|
| 1 | `joulewise/analysis_engine/claims.py:74-135` | add to `ENGINE_REASON_CODES` (`ordered_reason_codes` raises `ValueError` on unknown codes, `:218-220` — closed set, hard-failing) |
| 2 | `joulewise/analysis_engine/claims.py:154-191` | add to `_NOT_RESOLVABLE`; without an explicit bucket it falls to the trailing `result.extend(sorted(remaining))` at `:227`, i.e. lowest precedence — wrong, because a superseded capture pipeline is definitively not resolvable (July cannot be re-run) |
| 3 | `joulewise/whole_window.py` (~`:175-205` set) | add |
| 4 | `joulewise/floor_extraction.py` (~`:180-211` tuple) | add |

Sites 3 and 4 are gates I am conceding under Item 4 anyway, so the **marginal**
cost of the new reason is four one-line enum additions.

**Amended clause text (supersedes my R1-2.3):**

> **R1-2.3′.** Register a new engine refusal reason `capture_pipeline_superseded`
> in `ENGINE_REASON_CODES` (`analysis_engine/claims.py:74`) and in
> `_NOT_RESOLVABLE` (`:154`), plus the `whole_window.py` and
> `floor_extraction.py` refusal registries. A bundle whose
> `metadata.uncertainty_evidence.clock_anchor.method` is not in the closed set
> `CLAIM_BEARING_ANCHOR_METHODS = frozenset({CLOCK_METHOD_V3})` contributes
> `capture_pipeline_superseded` — never `clock_anchor_unresolved` — at analysis
> admission, floor extraction, and whole-window member admission. Reserve
> `clock_anchor_unresolved` for its true meaning: an anchor that did not resolve.
> A bundle may of course carry both, independently derived.

Note the two halves are separable and both are required: terra supplied the
**name**, I supply the **predicate**. Neither alone is a spec — see the
off-agenda blocker.

---

## Item 2 — FAILING-TEST ROOT → **MAINTAIN** (executed; terra could not execute)

The experiment stands and terra has not refuted it, because terra could not run
anything: terra's own V3 records `FileNotFoundError: [Errno 2] No usable
temporary directory found` and flag G1 concedes "this read-only sandbox has no
writable temporary directory, so local unittest execution fails during import
before the target test runs." Terra's F3 characterization ("the real
v2-measurement/v3-calibration incompatibility") is therefore argued from the
saved bb81323 log, not executed. Executed evidence beats argued plausibility —
the agenda's own rule.

**My experiment, re-affirmed:** reverting *only*
`joulewise.calibration_bracketing.ACTIVE_CAPTURE_ANCHOR_METHOD` to
`CLOCK_METHOD_V2` in-process, changing nothing else, turns
`test_d079_real_selector_to_real_reducer_embeds_allowance_once` green
(`Ran 1 test in 37.961s … OK`). One comparator, one line, full cure. The
measurement bundle is untouched by that revert, so a *v2-measurement*
incompatibility cannot be the root. The root is the already-landed
calibration-admission comparator (`calibration_bracketing.py:1039-1040`) meeting
`self_consistent_calibration`, which hardcodes `derive_powermetrics_anchor_v2`
(`tests/test_reduce.py:194`) and the v2 binding lexeme (`:233-235`).

**Consequence the ruling must carry:** the fix is in `tests/test_reduce.py` and
lands in **Step 1, before the production flip**. A plan that sequences it after
the flip will watch the flip fail to cure it.

**But terra wins a real sub-point, and I adopt it.** Terra: the retained negative
test must assert a *purposeful* reason, "not an accidental custody error." That
is correct and it exposes a defect I did not name. Today a superseded-era
candidate is dropped silently by `load_calibration_candidate`
(`calibration_bracketing.py:1039-1040` returns `None`), which makes
`len(candidates) != registered_valid` and surfaces as
`calibration_ledger_custody_invalid` (`:1952-1962`) — a **count-mismatch signal
standing in for a method-identity refusal**. The observed refusal is
diagnostically wrong even though the fail-closed outcome is right.

**Amendment (credited to terra):**

> **R1-2.6′.** `discover_calibration_candidates` must distinguish "not a
> candidate" from "candidate of a superseded capture era." A candidate rejected
> solely on `anchor_method_version` is reported as `capture_pipeline_superseded`
> and is excluded from the `registered_valid` reconciliation, so custody
> integrity and era eligibility never masquerade as one another. The retained
> mixed-era regression asserts that reason, not the custody code.

---

## Item 3 — CONTROLLER SEED ENVELOPE → **CONCEDE to terra**

I flagged this as my lowest-confidence item and named the missing evidence: "I
could not establish from the code whether any stored bundle depends on that exact
literal" (my Q3). I went and got it.

**Executed census (E3)** — the controller seed path (`controller.py:1355-1362`)
produces an envelope with `schema_version` + `telemetry_backend` and then only
`idle_drift`/`idle_drift_guard` — no `clock_anchor`, no `sample_phase`. Shape
histogram over all 1378 stored envelopes:

```
748  p2-038.2  ('clock_anchor','idle_drift','idle_drift_guard','sample_phase','schema_version','telemetry_backend')
622  p2-038.1  (same six keys)
  8  (no schema_version)  ('clock_anchor',)  -- tests/fixtures/fcm_r4_real_blocks, trimmed fixtures
```

**Zero stored bundles anywhere carry the seed shape.** The literal at
`controller.py:1357` has no dependents. My only reason for caution is gone, and
with it my position: terra's argument stands unopposed — a fallback that did not
run the v3 pipeline must not claim the v3 pipeline's identity, and stamping the
active era there would manufacture exactly the false identity claim that
`SCHEMA_FOR_ANCHOR_METHOD` exists to prevent. It would also be self-defeating:
my own two-key consistency rule would then face an envelope with an era label and
no `clock_anchor.method` to cross-check it against.

**Amended clause text (supersedes my R1-3.3):**

> **R1-3.3′.** `joulewise/controller.py:1355-1362`: when the telemetry adapter
> produced no uncertainty evidence, do **not** synthesize a capture-pipeline era
> label. For the powermetrics backend, emit the envelope with
> `schema_version` absent (or explicitly `null`) and a recorded
> `capture_pipeline_absent` marker, so `cli.py:1233` fails the bundle closed
> rather than admitting a mislabeled one. Verified safe: zero stored bundles
> depend on the current `p2-038.1` literal (E3).

Q3 is withdrawn from my open-questions list; it is answered.

---

## Item 4 — SITE CENSUS → **SPLIT: MAINTAIN mine, CONCEDE terra's, neither was complete**

The honest verdict the magistrate needs: **my census was more complete on the
capture side, terra's on the claim-consumer side. Ratify the union.**

### Mine, re-verified this round — MAINTAIN all four

| Site | Verified this round |
|---|---|
| `environment_admission.py:307,351` | hardcoded `derive_powermetrics_anchor_v2` re-derives the anchor that timestamps measured records for the thermal-pressure walk. On a v3 bundle it uses a different model than the bundle's own evidence and can hit the v2 knife-edge (`native_intersection_empty`, `01-root-cause.md:126-140`) on a capture v3 resolves — a correct-looking refusal for a wrong reason. **MAINTAIN.** |
| `powermetrics_fiducial.py:1467` | `detection.anchor_method or CLOCK_METHOD_V2` — a silent default naming the falsified estimator. **MAINTAIN.** |
| `analysis_engine/inputs.py:188` | tests `status == "unresolved"`; both emitters produce `status: "unknown"` (`uncertainty_evidence.py:291`, `:701`). Dead comparison. **MAINTAIN** (incidental, bundled). |
| two-key rule `SCHEMA_FOR_ANCHOR_METHOD` + `clock_anchor_era_inconsistent` | `cli.py:1266` dispatches on the label, `reduce.py:1793` on the method — two keys, one identity. **MAINTAIN**; terra's (a)(3) reaches the same conclusion by a different route and its "closed schema → method → deriver mapping" at `uncertainty_evidence.py:1281` is compatible. Merge them. |

### Terra's, verified this round — CONCEDE all four; one is high-value

| Site | Verified | Verdict |
|---|---|---|
| **`arm_readiness.py:4143-4149`** | `_issued_d079` holds a literal allow-list of acceptance ids and gates `successor_acceptance` at **six call sites** (`:5203, :5320, :5539, :6191, :6413, :6452`) **[verified by grep]**. Without `..._r5` an r5-pinned pack routes as a D-102 corpus-GROWTH successor and takes the wrong readiness path — **at arm time, in a live measurement window.** | **CONCEDE — best catch of the round.** Latest-failing site in either design; I missed it entirely. |
| **`floor_extraction.py:1949-1952`** | floor extraction carries its **own** reducer-version barrier (`if reducer_version in {"0.5.0","0.6.0"}`), independent of `analysis_engine/inputs.py`. My single barrier in `inputs.py` would **not** have covered the floor lane. | **CONCEDE — real gap in my design.** |
| **`whole_window.py:709-716`** | member admission loops on `_current_strict_summary(...)` only; strict-summary classification is not an era gate. | **CONCEDE.** |
| `adapters/powermetrics.py:1832` | docstring "the v2 anchor estimator's native evidence" — `NativeAnchorRecord` is shared by v2 and v3; stale identity string. | **CONCEDE** (minor). |

### Bundle census reconciliation — MAINTAIN, with a tightened number

Terra repeated the brief's 54 and carried it into a rejected alternative
("Relabel or mutate the 54 stored bundles"). **Executed census (E1), whole-tree
`os.walk`:** `/Users/edr/code/JouleWise` holds **748** `p2-038.2` envelopes (745
bounded, 3 unknown) and 622 `p2-038.1`; plus 173 in `/Users/edr/JouleWise-backup/
runs` and 35 in `/Users/edr/JouleWise-window-custody`; 1751 across `/Users/edr`
counting iCloud mirrors. Separately, 15 instrument-validation candidates declare
the v2 anchor method. **No population of 54 exists.** This does not change either
design's direction — it strengthens the shared retention position, since the
replay/custody value being preserved is ~14× larger than the brief assumed. I
withdraw my earlier "771"; **748** is the number derived by full-tree parse
rather than `grep -l`, and it is the one the ruling should carry.

---

## Item 5 — STRICT-VERIFY FAIL-OPEN → **MAINTAIN, now proven by execution; BLOCKER inside the flip commit**

I built the real thing rather than arguing it.

**Executed experiment (E4).** Copied
`tests/fixtures/d117_v2_production/strict_seed_bundle` twice into scratch
(outside the repo), wrote identical garbage over `rich_telemetry.jsonl` in both,
and relabeled only the second to what the flip will emit (`p2-038.3` +
`…rate_aware_set_membership_v1`). Then called the real
`joulewise.cli._strict_rich_telemetry_problems` on each:

```
p2-038.2 + corrupted rich telemetry -> ['strict: rich-telemetry: rich_telemetry.jsonl
                                        does not match the anchor-corrected
                                        re-derivation from the raw capture']
p2-038.3 + corrupted rich telemetry -> []
```

**Identical corruption. Caught at `.2`, silently clean at `.3`.** `cli.py:1573-1577`
returns `[]` for any label that is not exactly `P2038_SCHEMA_VERSION_V2`, so
post-flip every production bundle skips rich-telemetry verification entirely.

**Severity — and the asymmetry that makes it the dangerous one.** I checked the
other five cli.py era sites on the same relabeled bundle:

```
p2-038.2: uncertainty-evidence check -> []
p2-038.3: uncertainty-evidence check -> ['unsupported or missing schema_version',
                                         'clock_anchor does not match ...',
                                         'sample_phase does not match ...']
```

`:1233`, `:1290` and `:1547` all fail **closed and loudly** on `.3` — they would
be found on the first bundle of the first window. `:1575` is the **only** site of
the six that fails **open and silently**. A confirmation-shaped test (clean file →
no problem) passes vacuously against it, which is why neither the brief nor terra
named it.

**Verdict: BLOCKER, and the fix belongs in the flip commit — not a follow-up.**
Any head that flips capture without `:1575` ships a production pipeline whose
rich-telemetry gate is off. Attack test **A4** (corrupt the file, assert a
problem) is mandatory, and it must be written as the *corruption* case; the clean
case proves nothing.

---

## OFF-AGENDA BLOCKER (one, as permitted)

**Terra installs three era gates with no shared predicate — the exact defect class
that created this ruling.**

Terra's (b) directs: `analysis_engine/inputs.py` — "enforce
`capture_pipeline_superseded` after strict validation"; `floor_extraction.py:1918`
— "apply the same prospective identity gate"; `whole_window.py:710` — "reject a v2
member before calibration bracket selection." Three sites, three prose
instructions, **no defined predicate and no named constant.** "The same
prospective identity gate" is not a specification; it is three implementers'
readings of one sentence.

This is not a stylistic objection. R1 exists because a single capture identity was
hardcoded independently at 4 adapter sites + 6 cli sites + 2 campaign-gate sites +
2 environment-admission sites + a fiducial default + a controller literal, and
they drifted. Reproducing that topology in the *claim* lane — where the
consequence is an admitted claim rather than a red test — is strictly worse.
`arm_readiness.py:4143-4149`, the site terra itself found, is the living proof:
a literal allow-list that must be edited by hand every generation, at six call
sites, failing at arm time when it is missed.

**Required amendment before ratification (constructive, and it merges cleanly with
terra's vocabulary win):**

> **R1-2.3″.** Define **one** closed predicate in `joulewise/uncertainty_evidence.py`:
> `CLAIM_BEARING_ANCHOR_METHODS = frozenset({CLOCK_METHOD_V3})`, with a single
> shared helper `capture_pipeline_refusal(metadata) -> str | None` returning
> `"capture_pipeline_superseded"` or `None`. `analysis_engine/inputs.py`,
> `floor_extraction.py` and `whole_window.py` each **call** that helper; none
> re-implements the test, and none inlines a method literal. The attack test is
> a mutation check: flipping the helper's return must kill at least one test in
> each of the three lanes independently.

With that, terra's name + my predicate + terra's three sites + my four capture
sites compose into one coherent spec. Without it, we ship the same disease into
the claim lane.

---

## Verification record — this round

| # | Experiment | Result |
|---|---|---|
| **E1** | Full-tree `os.walk` + JSON parse of every `metadata.json` under `/Users/edr/code/JouleWise` (1378 envelopes) | 745 `p2-038.2`/**bounded**, 3 `p2-038.2`/unknown, 622 `p2-038.1`/bounded, 8 unlabeled fixtures → Item 1 concession; Item 4 census |
| **E2** | Read of `analysis_engine/claims.py:39-227`, `whole_window.py:175-205`, `floor_extraction.py:180-211` | new reason costs exactly 4 additive enum entries; `ordered_reason_codes:218-220` hard-fails on unknown; `_NOT_RESOLVABLE` bucket must be named explicitly |
| **E3** | Seed-shape search across all 1378 envelopes | **zero** stored bundles carry the controller seed shape → Item 3 concession; Q3 withdrawn |
| **E4** | Real `_strict_rich_telemetry_problems` on two scratch copies of `d117_v2_production/strict_seed_bundle`, identical corruption, labels `.2` vs `.3` | `.2` → problem raised; `.3` → **`[]`**. Fail-open proven. Companion run shows `:1233/:1290/:1547` fail closed on `.3` |
| **E5** | `grep -n "_issued_d079" joulewise/arm_readiness.py` | 6 gating call sites → terra's `:4143-4149` catch confirmed load-bearing |
| **E6** | `git status --short` in `wtTXN` at start and end; probe scratch removed | clean both times; no repo writes |

Sequencing facts only, per the agenda: r5 must precede R2's consumption of the
live acceptance generation, and `arm_readiness.py:4143-4149` must gain the r5 id
in the same commit — otherwise R2's packs pin a generation the readiness router
does not recognise.
