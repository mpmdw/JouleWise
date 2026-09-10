```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a preregistered derivation-only capture lane, an authenticated extension of the canonical ledger, and generation-specific prospective issuance; scientific rules require Ed and cold-gate approval.",
  "workspace": {
    "base_requested": "origin/bookkeeping/2026-09-10-activation-96bfeca7",
    "base_mode": "informational",
    "head_start": "078a13a461abd124c29796798da5107fe00190a6",
    "head_end": "078a13a461abd124c29796798da5107fe00190a6",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "Design adjudication", "action": "needs_ruling"},
      {"row": "Bootstrap implementation", "action": "wait_for", "wait_for": "Recorded cold-gate ruling and Ed's scientific decisions"},
      {"row": "Derivation capture", "action": "wait_for", "wait_for": "Installed reviewed mechanism, frozen registration, rehearsal clearance and agent-free window"},
      {"row": "Successor issuance", "action": "wait_for", "wait_for": "Complete authenticated corpus, scientific acceptance and atomic fan-out"},
      {"row": "Current G2-a chain", "action": "do_not_start"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --exit-code HEAD origin/main -- scripts/validate_powermetrics_fiducial.py joulewise/calibration_ledger.py joulewise/calibration_bracketing.py scripts/calibration_ledger_bootstrap.py scripts/reissue_calibration_acceptance.py tests/verify_calibration_acceptance_corpus.py docs/contracts/calibration_ledger.md docs/contracts/powermetrics_fiducial.md docs/decision_log.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --exit-code 4aca5f84ea83c7d22c7684c674e83dc9024fa0cf a97648fe87eb8c54b802756bb3d50283ef6de59d -- docs/process_traces/2026-09-10-activation-96bfeca7/38-consult-acceptance-epoch-astra-report.md docs/process_traces/2026-09-10-activation-96bfeca7/39-lead-record-os-build-epoch-blocker.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Execution requires a bootstrap authority, prospective-prefix rule, and scientific registration. The retained D-125 envelope conflict and D-126 n>=19 licensing clause cannot be resolved by the magistrate implicitly.",
      "needs": "Present the questions and recommended preregistration below to Ed and the cold gate before implementation and capture."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Checkout is detached at 078a13a4; origin/main is d84da72e. Listed core mechanisms are byte-identical. Later G2-a producer and activation records were read through Git objects. The bookkeeping ref advanced during consultation; reports 38 and 39 were unchanged between the inspected endpoints.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only design consult. No files changed, suite run, custody replay, hardware capture, arming, or cross-model callback. Calendar and effort figures are conditional planning estimates.",
      "needs": "Lead owns implementation verification, custody authentication, final review and live gates."
    }
  ]
}
```

## Scheduling matrix

All recommendations below are **proposed rules**, not execution authority. Dates are PDT. References use this checkout unless prefixed `d84da72e:`; `A/` abbreviates `docs/process_traces/2026-09-10-activation-96bfeca7/`.

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Ed’s scientific decisions and cold-gate ruling | needs_ruling | D3 registration, D-125 treatment, ledger/issuance authority | Scientific policy; no resident-magistrate amendment |
| Bootstrap mechanism and offline verification | wait_for | Recorded ruling | Writer, ledger, acceptance validator |
| Rehearsal harvest and ownership clearance | wait_for | Actual September 11 harvest | Existing stub, launch agents, measurement checkout |
| New-epoch corpus | wait_for | Reviewed capture head, committed registration, fresh plan/notice, agent-free window | Canonical ledger; exclusive measurement ownership |
| Successor preparation and science review | wait_for | Complete corpus and authenticated terminal head | Corpus selection, statistics, exclusions |
| Atomic issuance | wait_for | Science approval and complete D-138 transaction | Acceptance/default/registry, estimator and downstream pins |
| G2-a | do_not_start | Issued matching acceptance, rebuilt inputs, successful desk bind/check and ordinary arm gates | Fresh calibration brackets; existing G2-a allocation superseded |

| Design | Earliest conditional corpus | Earliest conditional issuance | Earliest credible G2-a |
|---|---|---|---|
| One night, 20 scheduled attempts | September 12 | September 12 afternoon/evening | Arm September 13; capture September 14 |
| **Recommended first bootstrap:** two nights, 10 attempts each | September 12 and 13 | September 13 afternoon/evening | Arm September 14; capture September 15 |

These dates require the mechanism and preregistration to clear the September 11 installation opportunity. Budget **14–28 focused desk hours before capture**, including implementation, adversarial verification and integration; **8–16 desk hours after the final harvest**, including raw replay, scientific review, issuance, fan-out and clone proof. Review queues or failures add calendar time. September 12 is an optimistic earliest opportunity, not a commitment.

The existing schedule places installation at 03:00–06:30 and acquisition at 02:56, with a 13,500-second allocation and courier completion before 07:00 (`d84da72e:A/12-arm-runbook-68-g2a-20260912.md:37`). The lead has superseded its G2-a arm steps pending this bootstrap (`A/39-lead-record-os-build-epoch-blocker.md:35`). A new derivation plan must replace that allocation explicitly.

## Critical path

**D1 — Use a dedicated derivation-only mode of the existing writer, orchestrated by a new pinned chain under `DIAGNOSTIC_NO_PACK`.**

Retain the existing pulse capture and physics implementation. Add `--derivation-only`, requiring an authenticated, committed bootstrap registration and exact scheduled slot. Reject combinations with bracket slots, legacy rederivation, or live use of test overrides. The mode authorizes acquisition only; it supplies no substitute acceptance or provisional numeric screen.

The ordinary path must continue calling `_derive_preflight_systematic_screen_s()` unchanged. Its exact-epoch refusal is at `scripts/validate_powermetrics_fiducial.py:394`; both current capture paths invoke it before acquisition at `:1701`. The new branch authenticates its **capture registration** at that point instead of attempting acceptance derivation.

Record for every attempt:

- The five existing evidence artifacts, raw native plist, complete paired-clock events, trace, anchor diagnostics, pulse fits and decimal bound lexeme (`docs/contracts/powermetrics_fiducial.md:129`; `scripts/validate_powermetrics_fiducial.py:2155`).
- Measured six-field epoch and complete T1 vector, including actual powermetrics SHA-256, MLX, anchor and protocol identities; compare reservation versus capture bindings. Current projections and measured bindings are at `scripts/validate_powermetrics_fiducial.py:656` and `:2129`; finalization already checks their equality at `joulewise/calibration_ledger.py:5608`.
- Registration digest, slot ID, acquisition source hashes, night/chain identity, reservation/finalization receipts, environmental admission and network-time provenance, all failures and terminal ledger boundary. Authenticate observed power policy; the present writer’s `args.power_policy` label alone is insufficient (`scripts/validate_powermetrics_fiducial.py:2138`; `docs/contracts/powermetrics_fiducial.md:155`).
- A distinct proposed evidence schema, `status="non-claim-bearing"`, `physics_status`, and `screen_evaluation="not_applicable_no_issued_epoch_screen"`. Never emit a parallel ordinary `status="valid"` evidence document.

The last distinction is executable protection: attachment requires `status=="valid"` (`joulewise/controller.py:439`), candidate loading requires the ordinary evidence schema (`joulewise/calibration_bracketing.py:1157`), and shared claim-physics verification requires valid status (`joulewise/powermetrics_fiducial.py:1293`). The derivation issuer uses authenticated raw replay through `rederive_detection_from_artifacts()` (`:1095`), not the claim verifier with a bypass switch.

Add an authenticated derivation-purpose marker to ledger reservations and finalizations. Ledger `valid` may mean intrinsic protocol validity **only within that marked observation kind**; it must not mean acceptance-screen passage. Candidate discovery explicitly skips that kind, avoiding both accidental endpoint selection and the current “unloadable valid candidate empties discovery” behavior (`joulewise/calibration_bracketing.py:1332`).

**Necessary unattended extension rule:** a simple shell loop is insufficient. `append_pending_receipt()` requires the physical head to equal the committed pin (`joulewise/calibration_ledger.py:5495`). After one standalone observation, that equality no longer holds.

Authorize subsequent slots only when, under the existing writer lease and append lock:

1. The registered committed baseline is an exact ancestor.
2. Every intervening attempt belongs to this registration, is in its prescribed order, and is completely finalized.
3. The next slot is unused and within the registered bound.
4. There is no foreign extension, unresolved attempt, binding change or journal ambiguity.

Keep reservation-before-hardware, crash recovery, and exactly one terminal result. Emit terminal pin candidates; the night never commits Git. Claim consumers continue requiring the committed physical-head agreement. Existing lifecycle/lease integration is at `scripts/validate_powermetrics_fiducial.py:1303`; append/finalization boundaries are at `joulewise/calibration_ledger.py:5459` and `:5563`.

No new night class is needed. `DIAGNOSTIC_NO_PACK` still requires C1 and C3–C5 (`joulewise/night_gate.py:435`). **C1 currently authenticates D-166**, so do not replace its registration path with the bootstrap plan (`:1300`). Bind and check the additional bootstrap registration inside the reviewed chain, whose exact digest the driver verifies (`scripts/run_night.py:1577`). A passing night receipt establishes execution conditions, not calibration acceptance.

**D2 — Keep one canonical ledger; introduce a generation-specific prospective-prefix representation.**

| Choice | Advantages | Contract costs |
|---|---|---|
| **Canonical mixed-epoch ledger** | Preserves chronology, omissions, previous refusals and rollback protection under one head; avoids choosing between competing histories | Requires a new issuance-prefix rule and epoch catalog validation |
| Separately anchored epoch ledger | Locally simple epoch-pure inventory; isolates capture bookkeeping | Needs authoritative rollover linking old terminal digest to new genesis, ledger routing for every consumer, and cross-ledger omission/rollback checks; does not remove the live-prefix issuer gap |

Recommend the first. Per-row epoch already exists (`joulewise/calibration_ledger.py:320`). Preserve the original sequence-76 prefix and all issued historical artifacts unchanged; append actual new-epoch observations.

The successor’s history must cover **every finalized observation through its authenticated cutoff**, across epochs. Its derivation corpus is a separate, preregistered subset restricted to the target epoch, target T1 profile and registered slots. Do not filter the history down to the retained corpus.

Implement the new prefix rule only for explicitly registered prospective generations. Existing generations retain their historical-import-only rule. Current restrictions include one `d079_epoch` (`joulewise/calibration_bracketing.py:522`), exactly 38 observations and a `2 × observation_count` cutoff (`:590`), and rejection of any live observation in the prefix (`:1366`). New cutoffs must use the actual authenticated terminal sequence, including journal/control receipts.

Require unique epoch-catalog mappings, exact member-to-receipt/content linkage, matching target epoch/T1, and a complete exclusion/disposition record. Pending or unresolved attempts remain issuance-blocking until governed recovery/disposition; never omit them to make the prefix pass. D-126 requires explicit disposition before an observation ceases being “new” (`docs/decision_log.md:8205`).

Leave historical bootstrap untouched. Its `:289` check requires **each receipt to map to exactly one catalog epoch**; that invariant remains useful. It is the surrounding historical-only builder and fixed inventory that cannot issue this corpus (`scripts/calibration_ledger_bootstrap.py:289`; `docs/contracts/calibration_ledger.md:253`).

This preserves the ledger contract’s independent committed head and exact-prefix protections (`docs/contracts/calibration_ledger.md:206`). It also follows D-124’s relevant single-source principle: derive an operative value once and thread its projections, rather than introduce independently selected ledger or bound authorities (`docs/decision_log.md:8145`). D-124 itself does not grant ledger-rollover authority.

**D3 — Proposed preregistration text, to approve and commit before capture.**

> **Objective and universe.** Derive an acceptance for the observed 25G83 epoch and one exact authenticated T1 profile. Freeze the complete epoch, executable/protocol/source hashes, power policy, admission requirements, acquisition head, slot inventory and ledger baseline before slot 1. Every acquired observation remains permanently non-claim-bearing.
>
> **Sample.** Schedule exactly 20 attempts. Preferred design: 10 on each of two separately admitted nights. One-night alternative: all 20, selected before any capture. Retain every content-distinct, intrinsically valid observation satisfying the frozen eligibility rule; require at least 19 retained, and at least nine from each night under the two-night design. Do not select the “best 19.”
>
> **Schedule.** After the existing 600-second post-operator settle, start slots at 600-second intervals. Each observation uses the frozen three warmups and 59 measured pulses, with its existing within-train spacing and baselines. The slot interval includes capture and therefore leaves approximately 2–6 minutes idle at the supplied 4–8-minute duration. It is not an additional ten-minute settle after every observation.
>
> **Admission and exclusions.** Require authenticated network-time OFF and the registered quiet, AC/power, thermal and clock conditions. Exclude hash-complete observations only for the enumerated protocol/clock invalidities; retain their full evidence and exact reason. In particular, apply the frozen affine-anchor feasibility/rate/residual rules—never remove a high bound merely because it would enlarge the screen.
>
> **Stopping.** Complete the fixed slots regardless of favorable bound values. No top-ups, retries, early “enough precision” stop, or outcome-driven extra night. Stop acquisition on custody/identity changes, agent intrusion, unresolved writer state, an unregistered failure, or when two exclusions make n≥19 impossible. A missed/overrun slot is recorded and not compressed or replaced. A stopped registration requires a new recorded disposition before another capture plan.
>
> **Systematic failures.** There is no numeric acceptance-level screen for this epoch during bootstrap. A large but otherwise valid bound is retained. A new detector/clock/admission failure mechanism, or evidence contradicting the registered transfer/model assumptions, is a screen-design challenge: preserve it, halt automatic issuance and refer it to the science gate. No threshold may be raised to reclassify that failure.
>
> **Analysis.** Pool all eligible registered observations under the approved two-draw prediction model; report each night’s distribution, acquisition order, exclusion reasons and clock residual margins. These diagnostics do not authorize trimming or post hoc regrouping. If the model is unsupported, refuse issuance rather than silently fit a different model.
>
> **Prospective use.** The resulting acceptance can judge only subsequent ordinary captures. It cannot license these derivation observations or retrospectively rescue a workload. Subsequent trigger observations remain judged under the prior issued artifact.

Why 20 rather than 17: r6’s 17 resulted from two specifically substantiated clock exclusions, not a new-epoch sample-size study (`docs/process_traces/2026-08-18-anchor-v3-science-review/03-cold-science-review.md:53`). D-126 separately retains an n≥19 licensing clause (`docs/decision_log.md:8213`). Twenty scheduled attempts provide room for one eligible technical exclusion; this is an operational proposal, not a statistical power calculation.

The 59-pulse argument is within-observation: `1−0.95^59 = 0.9515054747505769`; it does not establish independence or adequacy of 19–20 observations (`docs/contracts/powermetrics_fiducial.md:58`). Two nights offer some between-session coverage, but only two night clusters and less coverage than the original four-day corpus (`docs/decision_log.md:6484`).

| Arithmetic | One night | Two nights |
|---|---:|---:|
| Scheduled observations | 20 | 10 + 10 |
| Measured pulses / warmups | 1,180 / 60 | 590 / 30 per night |
| Active capture at 4–8 minutes each | 80–160 min | 40–80 min/night |
| Initial settle + fixed start spacing + last capture | `10 + 19×10 + 4–8 = 204–208 min` | `10 + 9×10 + 4–8 = 104–108 min/night` |
| Remaining in 225-minute allocation | 17–21 min | 117–121 min/night |

If Ed instead requires a fresh 600-second settle **before every observation**, one night needs `20×(10+4–8)=280–360 minutes`, exceeding the existing allocation; two nights need 140–180 minutes each. The current 600-second post-operator settle is explicit at `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:302` and `:534`; the proposed inter-observation cadence requires its own approval.

Keep frozen clock allowances; do not widen them after failure. Network-time ON/unknown is only validation material under the existing model (`joulewise/uncertainty_evidence.py:827`), and the science review explicitly prohibits widening its 250 µs/±50 ppm constants after observed failures without a new method identity (`03-cold-science-review.md:115`).

**D4 — Add a prospective-corpus issuer; do not stretch the predecessor-reissue tool.**

The existing reissuer copies the predecessor’s member set and validates science-neutral reconstruction (`scripts/reissue_calibration_acceptance.py:249`); it cannot supply new-member issuance authority. Add a separate candidate-preparation command, using shared production arithmetic and the registered prospective-prefix validator.

The candidate preparation must:

1. Authenticate the committed terminal head and complete history; reopen the five evidence files for every registered attempt.
2. Recompute physics from raw bytes, enforce the preregistered selection, and produce a complete retained/excluded table.
3. Compute source Decimal lexemes, min/max/range, mean and sample SD at explicit precision; record deterministic `t(0.975,n−1)` and `t(0.995,n−1)` derivations and the two-draw values `t·s·√2`.
4. Derive the level screen and ruled drift-screen/budget semantics, retain exact sources separately from rounded operatives, and hash the complete derivation and rounding rules.
5. Emit candidate bytes with no production authority; issue only after independent replay and the cold science decision.

D-102 clause 4 requires decimal comparison semantics and separates source numbers from presentation (`docs/decision_log.md:6491`). There is a real compatibility detail: r6 records binary64 evaluation of its prediction products (`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:476`). Recommend explicit all-Decimal semantics for the new generation, leaving historical bytes/replay frozen; have the gate approve that treatment. Its quantile implementation must support both possible degrees of freedom, 18 and 19, rather than copy r6’s even-df-only method.

**Resolve D-125 before choosing drift arithmetic.** Installed validation equates the screen with the rounded sample range (`joulewise/calibration_bracketing.py:674`), whereas D-125 adopts lineage-monotone prediction envelopes and the genesis floor (`docs/decision_log.md:8176`). The queue explicitly reserves that conflict to Ed (`TASK_QUEUE.md:655`).

Recommend retaining the ruled lineage conservatism: `S=max(inherited S,Q95)`, `C=max(inherited C,Q99)`, `cap=C−S`, with strict `S<C`; inherit the lawful envelope including its genesis floor, not r6’s lower scalar alone. The precise rule and comparator quantum are at `docs/process_traces/2026-08-07-u2-coldgate/Q1Q13-REMAND-CONSULT.md:73`. Cross-epoch inheritance of conservative operatives does **not** import old observations into the new statistical corpus; Ed must explicitly approve that lineage treatment. The level screen remains a separately derived quantity.

Register `calibration_acceptance_d079_v2_n<N>_<gen>.json` with the actual retained N and an Ed-authorized identity. Add production generation metadata and exact byte pins; bank independently verified expectations in `tests/verify_calibration_acceptance_corpus.py:25`. Update `verify()` for prospective raw-derived values: its present “re-derived values must differ from stored scalars” condition is inappropriate when a fresh capture reproduces its stored value (`:94`).

The **one D-138 transaction** carries:

- Successor bytes, predecessor relation, scientific decision, exact ledger cutoff, committed terminal head and issuance custody.
- Active default, production registry, generation arithmetic and corpus verification expectations (`joulewise/calibration_bracketing.py:132`, `:174`, `:218`).
- Applicable successor pack/extraction acceptance pins, T1 projections, readiness evidence and regenerated chain digests. Preserve frozen predecessor pack bytes; generate successors where necessary (`configs/campaigns/d117_contrast_v5/generate_configs.py:434`; `03-cold-science-review.md:111`).
- Explicit readiness treatment for a **new corpus**, rather than automatically adding its ID to the science-neutral reissue list (`joulewise/arm_readiness.py:6154`).
- `A/15-r2-coverage-ulp-staged-for-d138.patch`, its `run_bundle_layout.md` amendment, and all four regressions in `A/15-r2-tests-staged-for-d138.py.txt` (`d84da72e:A/15-lead-note-r2-staged-for-d138.md:9`).

Declare R2’s intended issuance-head inclusion before capture. Apply it on the transaction branch before final corpus replay and source hashing; retain acquisition hashes separately. Any unexpected physics/member change returns to the gate. D-138 forbids landing changed governed estimator bytes separately or defeating the live pin invariant with fixture substitutions (`docs/decision_log.md:10074`).

Cold science review must examine complete exclusions, raw-replay deltas, clock residuals, between-night/order diagnostics, the prediction model’s assumptions, rounding and envelope choices, and absence of self-licensing. Lead verification then runs focused behavioral checks, the corpus verifier, `python3 -m unittest discover -s tests`, final diff review and a fresh-clone bind/check.

**Exact minimal change map — proposed implementation, not this session’s write scope.**

| File:function or contract section | Necessary change |
|---|---|
| `scripts/validate_powermetrics_fiducial.py:main` (`:1523` vicinity); `_CaptureLedgerLifecycle.__init__`, `_begin_once`, `finalize` (`:1260`, `:1347`, `:1438` vicinity) | Explicit derivation branch, registration/slot plumbing, nonclaim evidence, intrinsic disposition and capture provenance; ordinary acceptance preflight unchanged |
| `joulewise/calibration_ledger.py:_valid_receipt_shape`, `_new_receipt`, `_attempts_and_observations`, `_observation_from_receipt`, `append_pending_receipt`, `finalize_attempt_receipt` (`:1031`, `:2105`, `:1654`, `:1467`, `:5459`, `:5563`) | Strict optional derivation-registration fields, reservation/finalization equality, derivation observation kind and locked registered-extension admission |
| `joulewise/calibration_bracketing.py:_valid_acceptance_bound`, `_prior_set_matches_import_cutoff_prefix`, `_capture_pipeline_refusal_for_observation`, `evaluate_calibration_bracket` (`:404`, `:1349`, `:1296`, `:1398`) | Generation-indexed prospective history, epoch-pure basis, endpoint exclusion, explicit trigger/disposition semantics; retain historical validation branches |
| Same file: new `derive_acceptance_statistics`; generation/default/registry declarations (`:132`, `:174`, `:218`) | One production arithmetic implementation plus registered new-generation rules and pins |
| **New** `scripts/bootstrap_calibration_epoch.py:check`, `capture`, `prepare_candidate` | Registration authentication, admission/provenance, fixed-slot orchestration, complete custody replay and candidate output |
| `tests/verify_calibration_acceptance_corpus.py:EXPECTED_BY_ACCEPTANCE_ID`, `verify` (`:25`, `:70`) | Banked generation and independently replayed prospective value semantics |
| `tests/test_calibration_ledger.py`; `tests/test_calibration_bracketing.py`; `tests/test_calibration_writer_crash_matrix.py`; **new** `tests/test_bootstrap_calibration_epoch.py` | Mutation/refusal tests for omitted/foreign slots, rollback, crash/pending state, wrong epoch, altered registration, exclusions and derivation evidence presented to claim consumers |
| `docs/contracts/calibration_ledger.md:9`, `:48`, `:191`; `docs/contracts/powermetrics_fiducial.md:129`; `docs/decision_log.md:D-102/D-125/D-126 addenda` | Capture-purpose semantics, registered extension, prospective issuance prefix, scientific rule and authority |
| New committed bootstrap registration and derivation chain | Exact slot schedule, bindings, baseline, eligibility/stopping rule and review authority |
| D-138 fan-out: `configs/campaigns/d117_contrast_v5/generate_configs.py:acceptance_pin` (`:459`); `joulewise/arm_readiness.py:_issued_d079` (`:6142`); applicable generated packs/extractions, T1/readiness artifacts and `scripts/floor_mint_pinsets/schema_v2.json` | Successor-specific routing and regenerated authenticated projections |
| Staged R2: `joulewise/reduce.py:_anchor_coverage_ok`; `docs/contracts/run_bundle_layout.md:522`; `tests/test_reduce.py` | Apply the already staged patch and four regressions inside issuance |

No change is required to `calibration_ledger_bootstrap.py`, ordinary `_derive_preflight_systematic_screen_s()`, or the night-class/C1 machinery. The consumer census must verify the nonclaim barrier end to end; any additional discovered consumer is an implementation scope item, not permission to weaken its check.

**D5 — Standing recurrence template, proposed for later ratification.**

Authorize a reusable **new-epoch bootstrap lane** whose variable inputs are the actual epoch/T1 vector, executable and source hashes, dates, slot IDs and ledger baseline. Freeze its capture restrictions, sample design, extension proof, disposition policy, numerical derivation, review gates and atomic issuance checklist. Next time, instantiate that template rather than reopen the mechanism design.

A standing one-night option can target the 204–208-minute design once Ed accepts its sampling limitations. The first bootstrap’s two-night evidence may inform that decision; it cannot establish universal cross-night stability. “One night” is the clean-execution target, not permission for outcome-driven retries.

The desk mismatch check already exists: `_derive_live_vectors()` checks acceptance freshness during binding, and `check` rederives identity/T1 (`d84da72e:scripts/generate_g2a_probe_inputs.py:638`, `:1226`). Preserve both.

Move a lightweight identity/T1 inspection to the beginning of night preparation, before expensive probe construction and notice authoring; repeat after reboot/update and at final arm preparation. Report the mismatched fields, binary hash and required lane. Runtime checks remain necessary because the machine can change after the desk check.

**Risks and questions for Ed**

- **Sampling:** approve two nights of 10, or the one-night 20-slot alternative? Confirm minimum retained n≥19 and the distinction between initial settle and inter-observation spacing.
- **Scientific stopping:** approve the exact exclusion/failure list and no-top-up rule? Large valid bounds remain included; novel failures require adjudication.
- **Arithmetic:** retain D-125 lineage envelopes across epochs, or explicitly supersede them? Approve new-generation Decimal prediction semantics and resolve the existing lower-screen conflict before issuance.
- **Authority:** approve canonical mixed history, prospective-prefix issuance, acceptance identity and the permanent nonclaim status of bootstrap observations.
- **Recurrence:** which parts may the magistrate instantiate mechanically next time, and which remain Ed/cold-science decisions?

The main residual risks are correlated observations, newly exposed OS/binary behavior, failure-taxonomy gaps, and incomplete pin fan-out. The magistrate may implement the ruled mechanism, schedule within granted authority, authenticate custody and carry the transaction; it may not select scientific rules after seeing the data.