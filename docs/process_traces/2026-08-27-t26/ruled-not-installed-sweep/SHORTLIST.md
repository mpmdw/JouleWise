# Transaction-blocking shortlist — S9 sweep

Ranked by what each one costs if the `_v4` transaction proceeds without it being
cured. Every item here survived at least one independent seat whose brief was to
prove it installed; the two BLOCKERs survived two seats with distinct lenses.

Baseline: code identical to `origin/main` `0dd3b6dc`; docs at `f4eac40b`
(two later commits are consult custody only, no code).

Legend for the cure column: **CODE** = a code change; **RUNBOOK** = a document
the operator follows on the night; **W-LIST** = a new pre-window worklist entry
gating the transaction; **ED** = needs Ed's ruling.

## At a glance

| # | Finding | Severity | Cure | Gates the mint? |
| --- | --- | --- | --- | --- |
| S9-01 | Collector never records the analysis-manifest identity → claim edge joins to nothing | **BLOCKER** | CODE + W-LIST | No — gates the first collection window |
| S9-01b | The prospective refusal registry is consumer-only: 16 reason codes, no producer check | **BLOCKER** | already D-157 R-2 — do not descope | Yes, via W-10 |
| S9-02 | W-10 scope: the p256 floor dependency is in a different file, and `m=1` is at three sites | **BLOCKER** | CODE, inside W-10 | Yes |
| S9-03 | The gamma prefill prompt is a candidate where it is owned, ratified where it is consumed | should-fix | ED + CODE | Yes |
| S9-04 | The gamma four-unit roster is a literal nothing checks | should-fix | CODE | Yes |
| S9-05 | Live calibration screen `0.009724` sits under D-125's ruled `0.010818` floor | **NEEDS-RULING** | ED, then CODE | Yes |
| S9-06 | A window can launch with no T-0 GO receipt | should-fix | CODE or explicit RUNBOOK acceptance | No — gates windows |
| S9-07 | The finalizer has no operator step; post-window analysis unreachable | should-fix | RUNBOOK | No — gates the analysis |
| S9-08 | `window.env` contradiction (a) and the twin parsers disagreeing (b) | should-fix ×2 | RUNBOOK + CODE | No — gates later windows |
| S9-09 | The fixed-point allowlist rule is two literal substrings | should-fix | CODE | No |
| S9-10 | Ruled transaction artifacts that do not exist (`campaign-close.json`, fixation guard, changed-set endpoints) | should-fix | CODE + RUNBOOK | Partly |
| S9-11 | The reissue tool can overwrite anchor-v3 pins with v2 values | should-fix | CODE | No — but it writes the mint's estimator pin |
| S9-12 | The L10 sacrificial rehearsal ruled to precede any spent window has no schedule | should-fix | RUNBOOK + W-LIST | No — gates windows |
| S9-13 | The recorder's single-operator rule points at a runbook §11 that has no such section | should-fix | RUNBOOK | No |

**Three items gate the mint and are not yet all in hand: S9-01b and S9-02 ride
W-10; S9-03 and S9-05 need Ed.** S9-01 does not have to gate the mint, but it is
much cheaper to land before it than after, because a mid-campaign non-config cure
forces a new family generation.

---

## S9-01 — BLOCKER — the collector never records the analysis-manifest identity, so the `_v4` claim edge joins to nothing

**Status: B** (rule exists at the consumer; no producer-side check).
**Cure needs: CODE + W-LIST.**
**Refuted by two seats with distinct lenses; both failed to break it.**

### The chain, each link read at HEAD

1. The collector resolves its analysis manifest by a fixed basename:
   `scripts/run_campaign.py:195` — `ANALYSIS_MANIFEST_NAME = "analysis_manifest.json"`;
   `:1201-1204` builds `config_dir / ANALYSIS_MANIFEST_NAME` and returns `None`
   if it is not a file.
2. Its version dispatch (`:1226-1240`) has exactly two branches — the AXI v2
   schema, else the v1 validator. **There is no v3 branch.**
3. The gamma pack ships `analysis_manifest_v3.json`, written by the generator
   **only at the pack root** (`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:2110`).
   `find configs -name "analysis_manifest.json"` returns nothing anywhere in the
   repository.
4. **The break is two-level, not one.** The window chain passes each numbered
   *science-stage* directory to the collector
   (`docs/phase_2/window_runbook.md:1456,1480`), and stages receive only their
   configs and `order_manifest.json` (`generate_configs.py:647`). Renaming the
   file would still not put it in the collector's `config_dir`.
5. So `new_campaign_provenance` writes `"analysis_manifest_id": null`
   (`scripts/run_campaign.py:3002-3004`) for every `_v4` campaign.
6. At claim time the finalized manifest supplies a **non-null** collection
   identity — `lineage.collection_manifest_id`, set from the prospective
   manifest's id at `joulewise/analysis_manifest_v3.py:3646` and read at
   `joulewise/analysis_engine/inputs.py:634` — and the cooldown join filters on
   exact equality (`inputs.py:2143`, `:2191`).
7. Result: zero campaign manifests selected; every bundle lands on
   `campaign_cooldown_evidence_missing` (`inputs.py:3443`) and is ineligible.

### Why it is not merely theoretical

- **142 of 142** campaign manifests on disk across every `runs_*` directory carry
  `analysis_manifest_id: null`. There is not one non-null instance in the repo.
- The collector's own ratified contract requires the recording:
  `docs/specs/c027/analysis_engine_trio.md:466` — *"Once `run_campaign` records
  its `manifest_id`, a changed manifest is a different campaign design"* — and
  `:1859-1861` states that null is contractually the **calibration** case, not an
  alternative encoding for a production campaign.
- The finalizer's own comment assumes the collector already did it
  (`analysis_manifest_v3.py:3643-3646`).
- `joulewise/campaign_provenance.py` (839 lines) contains **zero** occurrences of
  `analysis_manifest_id`. It is unpoliced in both directions.
- D-100 refuter R11 already observed this exact symptom on Window B — *"all eight
  window B manifests carry `analysis_manifest_id: null`"* (`docs/decision_log.md:6228-6231`)
  — and the installed cure only groups them under a `"<none>"` sentinel
  (`run_campaign.py:4965-4966`, `:5373-5374`). **No fail-closed refusal on null was
  ever added.** The one prior ruling that touched this did not close it.

### Not cured by D-157 / W-10

D-157 R-1 and R-2 touch the generator and the freeze/readiness path; neither
names `run_campaign`. The current gamma prospective manifest has no `manifest_id`
key at all, so there is nothing to record today — and after W-10 regenerates one
**the collector still will not read it.**

### Cure

In `scripts/run_campaign.py`: resolve the prospective manifest from the **pack
root** (the parent of the stage `config_dir`) as `analysis_manifest_v3.json`, add
a v3 branch to the version dispatch, record its `manifest_id` into
`new_campaign_provenance` (`:3002-3004`), and **refuse the campaign** when a
production (campaign-policy-bound) run would write `analysis_manifest_id: null`.
Regression: a v3 pack whose stage run records null is refused at the collector.

### Sequencing note

This defect fires on the **collection windows**, not on the freeze transaction
itself — the transaction night's Phase G is dry-run-only
(`docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1416-1418`). It
does not have to gate the mint. It **must** gate the first collection window, and
it is cheaper to land before the mint than after, because a mid-campaign
non-config cure forces a new family generation (D-140 no-repair, D-153).

### The meta-fact

The magistrate's own pipeline-smoke consult found this hours ago —
`docs/process_traces/2026-08-27-t26/pipeline-smoke-consult/03-fable-seat.md:13`
names it, `:37` calls it "the S5 hole" — and that consult directory is **the only
T26 consult with no `04-MAGISTRATE-RULING.md`**. The finding appears in no
decision-log entry, no `TASK_QUEUE.md` row, and no `RUN_STATE.md` line. Found,
never carried: the sweep's own thesis, happening in real time.

---

## S9-01b — BLOCKER — the entire prospective refusal registry is consumer-only: sixteen reason codes, no producer-side counterpart

**Status: B ×16. Cure: already ruled as D-157 R-2. Do not descope it.**

The G8 seat enumerated the D-078 analysis-manifest consumption-edge refusal
registry (`docs/decision_log.md:9160-9214`) clause by clause and found that
**sixteen registered refusal reasons have no producer-side check whatsoever**:

`analysis_prospective_schema_invalid`, `analysis_prospective_unknown_key`,
`analysis_prospective_not_frozen`, `analysis_prospective_identity_mismatch`,
`analysis_prospective_plan_tree_mismatch`,
`analysis_prospective_source_hash_mismatch`, `analysis_prospective_unsafe_path`,
`analysis_prospective_member_cover_mismatch`,
`analysis_prospective_block_cover_mismatch`,
`analysis_prospective_contrast_cover_mismatch`,
`analysis_prospective_family_invalid`,
`analysis_prospective_multiplicity_invalid`,
`analysis_prospective_floor_dependency_unresolved`,
`analysis_prospective_unresolved_slot`, `analysis_prospective_internal_error`,
and the rejection of placeholder `postcollection_attachments`.

Each is a refusal the consumer will raise on bytes the producer had no way to
know were bad. D-157 was one instance of this list —
`analysis_prospective_multiplicity_invalid` and
`analysis_prospective_unresolved_slot`, specifically. **There are fourteen more
doors of the same kind on the same wall.**

D-157 R-2 already ruled the cure: *"the freeze/readiness path gains an admission
check: it runs `validate_prospective_analysis_manifest_v3` (and null-p-value
multiplicity admission) on the manifest it is about to pin, and REFUSES the mint
on any finding with a registered reason."* That single check closes all sixteen.

**The action this finding demands is negative: R-2 must not be trimmed to "fix
the m=1 case."** If W-10 lands R-1 (the resolver) and drops or narrows R-2 (the
admission check) to save time, the project keeps fifteen live instances of the
defect that cost it this transaction night. The sweep's number — sixteen — is the
argument for spending the R-2 half.

---

## S9-02 — BLOCKER (scope correction to the in-flight W-10 cure) — D-139 A2's dedicated p256 floor lives in a different file than the `families` block, and `m=1` lives at three sites

**Status: C** for the floor-dependency half. **Cure needs: CODE, inside W-10's existing scope.**

D-157's W-10 installs D-139 A2 into the gamma generator. If W-10 is scoped to the
`families` block alone it will produce an m=2 family **whose prefill member still
has no floor dependency**, and it will not compile against the validator.

1. **A different artifact.** D-139 A2 clause (3) ruled the p256 floor a
   *dedicated artifact* — "no p128→p256 transport rule … the funded fixed-256-token
   prefill floor cells are already in the frozen packs (#138)". The generator still
   emits `prefill_p256_floor_dependency.cell_ids = EMPTY` with the TODO *"D-122
   does not identify ruled 256-token prefill floor cells"*
   (`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:797-808`),
   and those EMPTY bytes are already committed in
   `consumer_family_declaration.json`. **The cells the ruling points at do exist
   and are frozen**: `d117-qwen25-1p5b-prefill-p256-floor-v3` and
   `d117-qwen25-7b-prefill-p256-floor-v3`.
2. **`m=1` is hardcoded at three sites, not one.** Beyond the campaign generator:
   `joulewise/analysis_manifest_v3.py:476` hardcodes
   `{"method":"holm","alpha":0.05,"q":None,"m":1}` in `_family_and_contrast()`,
   and the **validator** at `:968-971` compares against that same value with the
   error string *"manifest.families: must be the frozen Holm alpha=0.05 m=1
   family"*. Installing m=2 requires changing the checker too, or the regenerated
   manifest fails its own validation.
3. **Blocks are decode-only.** `analysis_manifest_v3.py:566-578` builds blocks
   only for `sw-decode-contrast-bNN` — no prefill arm — while
   `joulewise/analysis_engine/__init__.py:1392` hard-refuses a multi-contrast
   family whose cross-arm strata are absent. An m=2 family with decode-only blocks
   is refused at the claim edge.

### Cure

Hand this section to the S8 stream on `fix/d139-a2-gamma-families` as a scope
amendment before it opens its PR. No new ruling is needed — all three sites are
inside D-157 R-1's "install D-139 A2 by a production resolver."

---

## S9-03 — SHOULD-FIX / ED — the gamma prefill prompt is a *candidate* in the pack that owns it and *ratified* in the packs that consume it

**Status: B. Cure needs: ED + CODE.**

`prefill_prompt_candidate.json:4` reads `"candidate_status":
"PROPOSED-PENDING-LEAD-RATIFICATION"`, `:6` reads `"prompt_text": "TODO(lead): no
named authority pins text"`, and `:22` reads
`"lead_rerun_required_before_ratification": true`. No tokenizer is ever run to
prove the prompt is 256 tokens.

Meanwhile the alpha and beta floor packs **already consume this same artifact as
Q1-ratified**, pinned by byte SHA with six real refusals
(`configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:719-738`).

The pack that owns the prompt calls it a candidate; the packs that consume it
call it ratified. D-122 ruled the arm "PROSPECTIVELY FROZEN … frozen prompt"
(`docs/decision_log.md:7920-7925`). One of the two readings has to give before
the mint, and which one is Ed's call.

---

## S9-04 — SHOULD-FIX — the gamma four-unit roster is a hand-written literal that nothing checks

**Status: B. Cure needs: CODE.**

D-131 clause 2a (`docs/decision_log.md:8390-8393`) ruled: *"Gamma carries exactly
four ordered units: `A/decode`, `A/prefill_p256`, `B/decode`, and
`B/prefill_p256`; A references the 1.5B producer and B references the 7B
producer."*

The generator emits the right four as a literal tuple
(`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:1622-1626`),
but `validate_identity_pin_projection` (`joulewise/identity_pins.py:469-544`,
called at `:1676`) enforces only exact keys, lifecycle state, null-pins-before-
projection and id uniqueness — **no cardinality, no ordering, no per-family
roster**. A gamma pack with three units, or `B/decode` before `A/decode`, or an
extra `C/decode`, validates clean, freezes clean, and arms clean: the arm-side
comparison at `joulewise/arm_readiness.py:5205-5208` compares the receipt's unit
list to the *pack's* list — self-consistency, never the ruled roster.

---

## S9-05 — NEEDS-RULING — the live calibration screen sits below the genesis lower bound D-125 ruled it could never go under

**Status: C. Cure needs: ED ruling first, then CODE.**

D-125 (`docs/decision_log.md:8125-8127`) ruled that screens and ceilings become
*"lineage-monotone t-family envelopes inheriting the genesis screen 0.010818 as a
lower bound — the allowance can only strengthen."*

No envelope, no monotonicity, and no `max(screen, genesis)` exists — `grep -rn
"envelope"` over `calibration_bracketing.py` and `calibration_ledger.py` returns
nothing. What exists is a flat per-generation registry, and **the live
generation's screen is below the ruled floor**: `calibration_bracketing.py:172`
resolves `ACTIVE_ACCEPTANCE_ID` to `ANCHOR_V3_R6`, whose `bracket_screen_s` is
`0.009724` (`:199,:211,:225-227`) against the ruled genesis `0.010818`.

This screen is the D-102 never-zero allowance floor inside
`registered_common_mode_operative_bound` — it sets **every comparative floor the
`_v4` mint issues.** D-145 calls the n=17 screens deliberately "TIGHTENED" and
D-145/D-147 consciously installed a *different* mechanism (a generation-indexed
resolver), so this may be intended. But **no decision vacates D-125's "can only
strengthen"**, and nothing in code checks either rule. The magistrate should
either record the supersession or restore the bound before the mint.

Related and unfixed: D-125 also ruled that *"D-117 clause 1 is AMENDED"* from
`max(drift, 0.010818)` to the envelope rule. That amendment was never written
into D-117 — `docs/decision_log.md:7686-7688` still states the superseded literal
as binding. A reader consulting D-117 for the mint rule today gets a number the
live code disagrees with.

---

## S9-06 — SHOULD-FIX — a window can launch with no T-0 GO receipt and nothing refuses

**Status: C. Cure needs: CODE or an explicit RUNBOOK acceptance.**

D-149 clause 1 (`docs/decision_log.md:8884-8890`) ruled that T-0 GO is
*"AUTO-ISSUED when ALL of the following hold, evaluated mechanically at T-0 and
written into the window's custody record as a GO receipt."*

`grep -rn "D-149\|d149" scripts joulewise tests` returns **zero hits in code**.
`scripts/launch_window.py:38-60` takes no GO-receipt argument, and `launch()` at
`:239-268` validates the arm receipt and then `execve`s. The template says so
itself (`docs/process/d149-go-receipt-template.md:62-66`: *"a mechanical evaluator
script MAY be built… until then the issuer fills the receipt by running the
runbook commands"*) and it is registered unbuilt as `WO-D149-GO-EVALUATOR`
(`TASK_QUEUE.md:415-420`).

Two of D-149's own conditions are worse than un-evaluated. **Clock discipline is
not mechanical at all** — `grep -rn "usingnetworktime" joulewise scripts` returns
nothing; it is a checkbox with attached command output. That is precisely the
defect class that refused 2 of 19 calibration members. And the **quiet single-writer
machinery is present but disabled**: `joulewise/quiet_guard.py:835-847`
`arm_refusal()` returns `failure_mapping("live_promotion_disabled", "Commit 1 has
no production promotion capability")`, with no caller outside its own CLI.

---

## S9-07 — SHOULD-FIX — the finalizer has no operator step, so post-window analysis is unreachable as documented

**Status: B. Cure needs: RUNBOOK.** (Refuter: PARTIAL — the *night* is not
blocked; the desk work after it is.)

`analyze-claims` requires a **finalized** v3 manifest
(`joulewise/analysis_engine/inputs.py:34,593`). The only thing that can produce
one is `finalize_prospective_analysis_manifest_v3`
(`joulewise/analysis_manifest_v3.py:3722`), exposed by
`scripts/finalize_analysis_manifest.py`. Every non-definition reference to that
function in the tree is a test. And
`grep -c "finalize_analysis_manifest|analyze-claims|finalize_prospective"`
returns **0** for the real-transaction runbook, the transaction runsheet, the
window runbook, the rehearsal operator card, the evening checklist, and
`prewindow_check.sh`.

The contract lens confirms the timing is correct by design — the finalizer is
ruled post-collection, consuming the whole-window verdict, bracket, ledger head
and aggregate floor artifact (`docs/decision_log.md:9119-9127`;
`docs/process/state_kernel.json:4032` calls it a "post-collection finalizer").
What is missing is the **scheduled desk route**: the only kernel/queue row
schedules its implementation and an L10 rehearsal, never its execution after a
window (`state_kernel.json:4032-4038`, `TASK_QUEUE.md:588`).

**This was already found on 2026-08-19 and recorded rather than fixed** —
`docs/process_traces/2026-08-19-prep-sprint/ready-packet-rows/19-ROW-L10-sacrificial-lifecycle.md:521-524`,
`.../ready-packet/OPEN-ITEMS.md:785`.

### Cure

Add a post-window desk closeout to the runbook with named ownership: invoke
`scripts/finalize_analysis_manifest.py` with its four attachment paths, validate
its output, then invoke `analyze-claims`.

---

## S9-08 — SHOULD-FIX (×2) — the `window.env` contradiction, and the twin parsers that disagree

**Status: B. Cure needs: RUNBOOK (the contradiction) + CODE (the twins).**

**(a) The contradiction.** `docs/phase_2/window_runbook.md:1337-1340` tells the
operator that `window.env` "must additionally bind the absolute `ARM_RECEIPT`,
`ARM_READINESS_CUSTODY_ROOT`, and `LAUNCH_MANIFEST` paths used by E-10", and the
chain dereferences `"$ARM_RECEIPT"` and `"$LAUNCH_MANIFEST"` under `set -euo
pipefail` (`:1343-1359`). But `_ENV_KEYS` in `scripts/capture_t0_step.py:102-129`
is an exhaustive 25-key set containing neither, and the parser refuses unknown
keys (`:259-265`). Obey the runbook and T-0 capture refuses; disobey it and the
chain aborts on an unbound variable.

The refuter settles the reachability: D-155 makes
`real-transaction-runbook.md` the governing document for the freeze transaction,
whose Phase G is dry-run-only, so **the contradiction does not block the
transaction night** — it blocks the later measurement windows, where the handoff
to `window_runbook.md` occurs (`real-transaction-runbook.md:1394-1401`). PR #205
preserves the instruction and restates it as an open defect; it does not cure it.

Known and recorded rather than fixed since 2026-08-19:
`docs/process/rehearsal-operator-card.md:5` documents the divergence and works
around it; `docs/process_traces/2026-08-19-prep-sprint/ready-packet/17-ROW-L8-operator-recovery.md:224-233`
recorded it.

**Cure:** delete the "additionally bind" instruction from the runbook and derive
and export `ARM_RECEIPT` and `LAUNCH_MANIFEST` after ARM and before E-10,
mirroring the operator card. Do not widen `window.env`.

**(b) NEW — the twins disagree.** Found by the refuter, not by the enumeration.
`scripts/capture_t0_step.py:259-265` enforces **exact** key equality, while
`joulewise/arm_readiness_evidence_t0.py:578-599,657-673` accepts arbitrary
syntactically valid assignments and checks only eleven expected bindings. Two
producers reading the same file under two different contracts is the shape that
D-155 NR-11 was ruled to close for the terminal-review parser — and it is still
live here.

**Cure:** share one exact parser and key contract between both callers; add
unknown-key and missing-key regressions at both boundaries.

---

## S9-09 — SHOULD-FIX — the fixed-point allowlist principle is enforced by two literal substrings

**Status: B. Cure needs: CODE.**

D-151 clause 7 ruled a standing rule: *"no authenticator path ever enters any
allowlist, in any transaction. A proposal to add one is a V-1(vi) tripwire
event."* `tests/test_arm_readiness_schemas.py:459-460` bars exactly two named
substrings (`d117_step6_confirmation`, `family_publication`). A new authenticator
class under any other name passes both checks and lands in the allowlist
unnoticed — which is precisely what the standing rule was written to prevent.

---

## S9-10 — SHOULD-FIX — ruled artifacts of the transaction that do not exist

**Status: C. Cure needs: CODE + RUNBOOK.**

- **D-155 NR-8**: a canonical `campaign-close.json` in transaction custody. No
  schema, no writer, no validator — `grep -rn "campaign-close" joulewise scripts
  tests` returns zero. The runbook itself concedes it at `:1122`: *"one ruled
  artifact does not exist yet."* (The record-order procedure IS installed, at
  `:1191-1212`.)
- **D-153 A1**: *"the fixation commit is the first commit after window close and
  carries EXACTLY the successor pinset SHA literal + its loud-fail guard."* No
  literal and no guard exist in the tree; there is a runbook slot, and nothing
  refuses a first-post-freeze commit that is not the fixation commit.
- **D-153 A6**: the changed-set window "CLOSES AT THE LAST CONSUMING ARM". No code
  computes or asserts either endpoint; the `arm_readiness.py` gate never learns
  the window closed.

---

## S9-11 — SHOULD-FIX — the reissue tool can silently overwrite anchor-v3 pins with superseded v2 values

**Status: C (the stated incapacity is nowhere a guard). Cure needs: CODE.**

D-145 clause 3 states plainly: *"The reissue TOOL compares stored scalars and
cannot check v3 generations — bespoke derive/build scripts are the r3/r4 route."*
That incapacity is documented and unguarded: `grep -n "v3\|anchor_v3\|n17"
scripts/reissue_calibration_acceptance.py` returns 0 hits in 606 lines. Run
against an r3+ predecessor, it would overwrite anchor-v3 member values with
superseded v2 stored lexemes (`:265-267`) and still pass `_valid_acceptance_bound`
(`:280`) — writing the estimator pin that every `_v3`/`_v4` pack binds at birth.

Cure: make the tool refuse a predecessor whose generation it cannot check.

---

## S9-12 — SHOULD-FIX — the L10 sacrificial rehearsal that is ruled to precede any spent window has no schedule

**Status: C. Cure needs: RUNBOOK + W-LIST.**

The freeze-evidence lifecycle ruling requires that *"the L10 sacrificial
rehearsal re-runs the full edge at the same head before any window is spent."*
No runbook phase and no kernel row schedules that re-run for the `_v4`
transaction. Given S9-01 and S9-07 — a claim edge that has never been executed
end to end against a v3 pack — this is the check that would have caught both
before a window was spent, and it is the one not being run.

---

## S9-13 — SHOULD-FIX — the recorder's single-operator bounding rule was ruled into a runbook section that does not contain it

**Status: C. Cure needs: RUNBOOK.**

The recorder authorization ruling states: *"the recorder runs single-operator
with no concurrent repo-writing process during a close-out; this is documented in
the runbook §11 close-out preamble (propagation owed with the WO)."* The
propagation was never done — §11 has no close-out preamble carrying the rule.
Note this compounds with D-156's Q3 item (S9-10), which also names a §11 step
that does not exist: two separate rulings both point at the same absent section.

---

## Already in flight — verify, do not re-open

| Item | Where |
| --- | --- |
| **D-156** supersession write-time refusal — the sweep found it entirely absent from code at HEAD, which is correct: it is ruled but not yet merged | PR **#206**, `fix/supersession-dup-refusal-01` |
| **D-154 R-3** mint-checkout declaration (`MINT-CHECKOUT-DECLARATION-01`) — kernel row registered, zero code at HEAD | PR **#208**, fenced "do not merge while the `_v4` transaction is open" |
| **D-157 R-1/R-2** the gamma families cure | branch `fix/d139-a2-gamma-families` (W-10) — **see S9-02, it needs a scope amendment** |
| **CONSUME-CONFIRMATION-SUPPLY-01** launcher supply line | merged, `2bc5daab` (#204) |

---

## Process-level, not transaction-blocking, but the largest single gap found

**The D-118 / D-121 merge gate has no mechanical existence.** D-118 enumerates an
eleven-item gate and states that *"every PR description must carry a GATE LEDGER
listing items 1-11 with the evidence path or commit for each"*, that *"a PR
without a complete gate ledger is not merge-eligible regardless of CI state"*,
and that *"the D-072 self-merge authority is CONDITIONED on this ledger being
complete."* D-121 adds item 12, the magistrate's terminal review, with a
prescribed ledger form.

The ledger was never created in any form. There is no PR template (`.github`
holds only `workflows/`), no CI job, and **no mention of D-118 in
`docs/orchestration.md`, `docs/agent_playbook.md`, or any loaded skill** — the
`operation-loop` skill still carries the older four-item shape. Every merge since
D-118 has been gated by memory.

**A second instance of the same class:** D-144's co-design protocol — no design
implemented without independent Sol and Opus designs, bounded debate, then a
Fable ruling — has its ONE home in a dated process-trace note
(`docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md:423`) and
appears in no skill and no process doc a future session loads.

Both are the same defect as the code findings above, one level up: a rule that
exists in the decision log and nowhere a future session will encounter it.
