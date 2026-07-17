# Run report — Window A shakedown, floors, and advisor brief (2026-07-17)

Date: 2026-07-17  
Status: **LEAD-ACCEPTED 2026-07-17** (Sol-drafted from retained evidence;
lead-reviewed; kernel closures in the same commit: P2-038 + P2-015-SMOKE
completed, P2-015 partial pending P2-039 artifact + P2-037 adjudication)  
Repository head covered: `6510c36`  
Measurement boundary for every energy value below: **Apple M3 Max /
powermetrics SoC rails (CPU + GPU + ANE)**

## Deliverable check

The accepted deliverable increment exists and shipped in the repository:

- `docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json`
  records the independently verified Window-A floor table. All four extraction
  families received verdict `confirmed`; no numeric discrepancy was found.
- `docs/advisor_briefs/2026-07-17-window-a-brief.html` is the self-contained
  advisor deliverable. Commit `6510c36` records palette validation, light/dark
  render inspection, and the bundle-accounting and claim-readiness callouts.
- P2-038 is closed by the canonical merged-main shakedown pin in
  `docs/phase_2/detection_floor.md`; Window A is open.

This increment is calibration and communication evidence, not a promoted
research claim. The corpus contains 222 distinct strict-valid,
collection-usable bundles, but every one is claim-evidence-flagged. P2-037
claim adjudication therefore remains pending.

## Measurement narrative

### Production-shaped gate: four failures that protected the corpus

The gate did not pass by ignoring failed runs. Four retained failed attempt
directories precede the passing directory, and each failure prevented the
floor chain from starting with an invalid assumption.

| attempt | retained verdict | what it caught | resulting disposition |
|---|---|---|---|
| `runs/window_a_shakedown` | `request_ineligible`; request cadence unrecorded | The native trace ended about 0.53 s before `sampling_stopped`, so no right-edge bracketing gap or cadence could be established. | PR #72 added a bounded post-marker powermetrics drain while preserving marker-bounded energy integration and sampler termination. |
| `runs/window_a_shakedown_r2` | `drift_evidence_missing`; `idle_window_suspect=true` | The idle sentinels rejected a contaminated idle window instead of treating strict-valid collection as usable drift evidence. | Preserve the failure; retry only after restoring the quiet/display environment. |
| `runs/window_a_shakedown_r3` | `drift_evidence_missing`; `idle_window_suspect=true` | A second independent run showed the idle contamination persisted; the repeat demonstrated that the fail-closed result was not a one-off parser or runner artifact. | Preserve the second failure; do not waive the idle-drift requirement. |
| `runs/window_a_shakedown_r4` | `request_ineligible`; request cadence unrecorded | The reconstructed support endpoint remained 0.034621 s short of `sampling_stopped`: the prior wall-time drain budget omitted 0.518879 s of measured startup-anchor lag. | PR #74 moved the success condition into the reconstructed trace domain and added measured anchor lag to the bounded deadline, with fail-closed clock-pathology guards. |

The final lead-owned run first issued `pmset displaysleepnow`, then used
`caffeinate -is` so the display stayed asleep while the system could not idle-
sleep. `runs/window_a_shakedown_final` passed
`production_uncertainty_v1` with `request_eligible: true`, reasons `[]`, strict
validation before and after reduction, and backup exit 0. The detection-floor
pin classifies this as plumbing evidence only: it establishes neither a floor
nor claim readiness.

### Floor campaign execution and accounting

The floor inputs covered normal telemetry and the planned request, phase,
suite, comparative, and start/end-reference cells. DF-TELEM remained honestly
unavailable because no extra sampler was enabled. Optional block 08 was not
run, so no long-prompt or long-decode request floor exists. An Ed-requested
pause stopped the chain cleanly at 112 succeeded bundles; the resumable runner
then skipped completed members and continued from the interrupted phase-ABBA
block. Completed bundles were retained and backed up per block.

The final log accounting is:

- 248 campaign-log lines;
- 222 distinct bundle directories and distinct strict-valid bundle IDs;
- 17 resumed `status=skipped` rows that re-list already completed phase-ABBA
  members; and
- 9 campaign-verdict rows.

Thus “248 bundles” is not used as a corpus count. All 222 distinct bundles are
strict-valid, `collection=usable`, and `claim_evidence_classification=flagged`.
The start/end reference bundles span 9.40 hours and differ only by run ID at
the config level.

## Verified floor results

All energy values are false-effect guard floors in joules at the **Apple M3
Max / powermetrics SoC-rail boundary (CPU + GPU + ANE)**. Gross is the D-067
headline basis. Idle-subtracted request energy is a labeled within-device
secondary view on the same boundary. Each primary cell has `n=10`, where `n`
means strict-valid bundles for absolute cells or strict-valid ABBA blocks for
comparative cells.

| cell / energy basis and boundary | absolute floor | comparative floor | computed `floor_gate_j` / status |
|---|---:|---:|---:|
| mid request, gross — M3 Max / powermetrics SoC rails | 0.527197 J | 0.909237 J | 0.909237 J |
| mid request, idle-subtracted — M3 Max / powermetrics SoC rails | 0.536632 J | 0.894215 J | 0.894215 J; within-device secondary |
| short request, gross — M3 Max / powermetrics SoC rails | 0.052484 J | — | absolute floor only |
| short request, idle-subtracted — M3 Max / powermetrics SoC rails | 0.058879 J | — | absolute floor only; within-device secondary |
| prefill phase, gross — M3 Max / powermetrics SoC rails | 1.476788 J | 1.738940 J | 1.738940 J |
| decode phase, gross — M3 Max / powermetrics SoC rails | 0.786337 J | 1.026892 J | 1.026892 J |
| short-prefill stress, gross — M3 Max / powermetrics SoC rails | 0.026694 J | — | smoke-only; `not_resolvable_sample_count` |
| suite item, gross — M3 Max / powermetrics SoC rails | 0.332774 J | 4.922865 J | 4.922865 J; drift review required |
| suite level, gross — M3 Max / powermetrics SoC rails | 1.663966 J | 24.618735 J | 24.618735 J; drift review required |

The NEG-8 start/end pair is an `n=2` drift-anchor diagnostic, not a campaign
floor. On the Apple M3 Max / powermetrics SoC-rail boundary, gross request
energy changed by 7.658896 J. The idle-subtracted within-device secondary view
changed by 6.608040 J on the same boundary. The diagnostic confirms meaningful
session-scale state drift and is not eligible to gate L2/L3 claims.

### Evidence ceiling and anomalies retained

- Universal claim-evidence flags: all 222 bundles carry
  `cadence_ratio_unrecorded`, `clock_bound_exceeds_quarter_window`, and
  `insufficient_in_window_samples`; 92 also carry
  `cadence_ratio_below_threshold`. Strict validation and collection usability
  therefore do not make the floors claim-ready.
- Request-window gross and idle-subtracted L2/L3 prechecks are ineligible
  pending P2-037 claim adjudication. The short request cell additionally misses
  the cadence threshold.
- Request ABBA late blocks change sign; the comparative mid-request floor is
  higher than the absolute floor, consistent with ordering/drift sensitivity.
- Decode ABBA's largest deltas are in flagged blocks, so its comparative floor
  is conservative and plausibly drift-inflated.
- Suite ABBA b01/b02 contain a six-member low-energy regime that drives the
  comparative item and level floors to about 15 times their absolute floors.
  Those gates require drift review before claim use.
- Short prefill is not resolvable at the observed sample count; its numeric
  floor is smoke evidence only.
- Optional block 08 has zero rows; no long-request floor may be inferred.

## Mechanism verdicts and landed history

- PR #72 and PR #74 landed the bounded drain and anchor-lag-aware follow-up
  exercised by the passing P2-038 shakedown.
- PR #73 landed AXI-SC's `unsupported_for_joulewise` pinned-runtime verdict:
  the external-draft path lacks complete proposal/acceptance/decode-boundary
  observability, and native MTP lacks a generation surface. No Mac energy leg
  was minted.
- AXI-SB remains `supported` for native static batching at runtime with
  request-scoped observability. This is functionality evidence, not an energy
  measurement or claim-bearing campaign.

## Spend

The only self-contained spend record in the supplied floor-extraction evidence
is the extraction/verification workflow: 8 agents, 482,950 workflow-reported
tokens, and 142 tool calls. This is a workflow receipt, not the WO-022
`codex-usage` arc snapshot and not billing truth.

Full overnight cross-family token, dollar, active-hour, and per-work-order
attribution is `accounting_unknown` in this draft because no complete
`codex-usage`/lead accounting receipt was supplied. It is intentionally not
reported as zero. **Lead closeout action:** replace or supplement this section
with the canonical spend snapshot before removing `DRAFT-FOR-LEAD`.

## Process catch / yield draft

| layer | applicable evidence | unique yield / disposition |
|---|---|---|
| lead-owned production shakedown | five retained attempt directories | four fail-closed attempts before one pass: one missing-bracket defect, two independently rejected idle-contamination attempts, one anchor-lag defect |
| implementation/review chain | merge history for the two drain PRs | bounded drain, scheduler-stable prefix selection, final-anchor correction, trace-domain endpoint condition, and fail-closed lag guards landed before live acceptance |
| independent floor verification | four extraction families | four `confirmed` verdicts; every numeric row replayed; no numeric discrepancy; minor prose-precision notes only |
| advisor-deliverable QA | advisor-brief commit and ledger | bundle-accounting correction, honesty callouts, palette validation, light/dark render inspection, and axis-label correction retained |

This table is evidence-level narration, not the lead's final D-061 or
delegation-calibration accounting. The lead must add any omitted invocation
rows, rework minutes, and final disposition labels.

## Restart pointers

1. There is no active stop card. Window A remains open; the floor corpus and
   advisor brief are shipped evidence, not the end of claim adjudication.
2. P2-037 must adjudicate the universal request-window evidence flags and the
   drift-sensitive comparative cells before any floor-backed L2/L3 claim.
3. The generated `RUN_STATE.md` header at this draft's head still names
   P2-015-SMOKE as the `[QUIET-MAC]` lane head and AXI-SB-ADAPTER as the
   `[AGENT]` lane head. That selector predates the completed floor extraction
   and advisor brief. The lead must reconcile the state kernel/queue before
   treating this narrative as a next-work instruction; this delegated draft
   was explicitly barred from kernel, queue, and generated-region edits.
4. Once the authoritative selector is reconciled, any further quiet-Mac work
   still requires Ed, a clean quiet-machine session, the display-sleep pin, and
   no active agent load.
5. The status site is stale against the floors and advisor brief. Agents do not
   regenerate or deploy it; `docs/site/DRIFT.md` informs Ed's manual decision.
6. Lead closeout: edit this draft, attach canonical spend/accounting and final
   process-ledger rows, reconcile the live selector, and only then remove the
   `DRAFT-FOR-LEAD` marker.

## Evidence index

| claim | source |
|---|---|
| floor values, 222/248 accounting, flags, anomalies, four-family verification, extraction workflow receipt | `docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json` |
| advisor deliverable shipped and honesty framing | `docs/advisor_briefs/2026-07-17-window-a-brief.html`; commit `6510c36` |
| P2-038 canonical pass command, display-sleep pin, acceptance fields, plumbing-only ceiling | `docs/phase_2/detection_floor.md` §1 Ordering Preconditions |
| four failed attempts and passing attempt | `runs/window_a_shakedown*/campaign_log.jsonl` |
| missing-bracket, final-anchor, and anchor-lag diagnoses | commits `f04d8f6`, `1fa05e3`, `f13c109`; `docs/stream_logs/2026-07-17-p2038-drain*.md` |
| PR #72/#73/#74 and AXI verdict history | `git log --oneline 15727dd..HEAD` |
| Window A open / no stop card / live lane pointers | `RUN_STATE.md` generated header at `6510c36` |

## Draft deviations requiring lead attention

- The current generated work selector predates the completed floors and brief;
  no kernel/queue/generated-region edit was authorized here.
- The canonical detection-floor pin says the final shakedown used reducer
  0.4.2, while the campaign-prep ledger records reducer acceptance-text
  staleness against the executable 0.5.0 head. This draft repeats the canonical
  pin's acceptance fields without attempting to re-adjudicate reducer history;
  the lead should reconcile the version wording.
- Complete overnight WO-022 spend accounting was not present in the supplied
  evidence and remains `accounting_unknown`, not zero.

## Draft verification

- `python3 -m unittest tests.test_docs_freshness` — 6 tests, pass.
- `python3 scripts/claims_lint.py --mode all --json` — exit 0, zero errors;
  warning-only review tokens are in pre-existing reader/history wording and no
  new floor claim triggered a warning.
- `git diff --check` — exit 0.
- Focused evidence spot-check against the verified JSON — workflow receipt,
  four `confirmed` verdicts, corpus wording, three representative floor values,
  draft marker, and Ed-manual deploy wording all present.
- The canonical Python suite was not rerun for this docs-only delegated stream:
  no code, schema, contract, kernel, queue, or generated artifact changed, and
  the focused freshness/claims checks directly cover the edited surfaces.

## ADDENDUM — exploratory block, extension axes, and deploy closeout draft

Date: 2026-07-17
Status: **FINAL RE-WRAP DRAFT; lead owns the final diff gate, selector
reconciliation, commit, and any future deploy.**
Repository evidence through: `c6cf3e5`
Measurement boundary for every addendum energy value: **Apple M3 Max /
powermetrics SoC rails (CPU + GPU + ANE)**

### Exploratory observation block

The follow-on corpus contains nine strict-valid, collection-usable bundles:
three repetitions each for OLMoE-1B-7B BF16, Qwen3-4B INT4, and
Qwen3.5-122B-A10B INT4 on the five-item `jw_mixed_v1_sentinel` shape. Every
bundle is claim-evidence-flagged and the repetition protocol is below the
headline threshold. These are explicitly **EXPLORATORY / L1-legacy,
unmatched, no-claim observations**.

| unmatched model/config | gross suite energy — M3 Max / SoC rails, mean ± sample SD (range) | gross energy/generated output token — same boundary, mean (range) | idle-subtracted energy/generated output token — same boundary, within-device secondary, mean (range) | runtime-observed output tok/s, mean (range) |
|---|---:|---:|---:|---:|
| OLMoE-1B-7B BF16 | 229.028 ± 2.445 J (227.141–231.790 J) | 178.928 mJ (177.454–181.086 mJ) | 177.900 mJ (176.706–179.537 mJ) | 122.361 (122.261–122.481) |
| Qwen3-4B INT4 | 362.772 ± 0.131 J (362.642–362.903 J) | 283.416 mJ (283.314–283.518 mJ) | 282.308 mJ (281.875–282.675 mJ) | 106.519 (106.470–106.545) |
| Qwen3.5-122B-A10B INT4 | 1072.273 ± 11.882 J (1061.722–1085.144 J) | 837.713 mJ (829.471–847.769 mJ) | 831.787 mJ (819.319–845.298 mJ) | 39.473 (39.349–39.569) |

Each bundle emitted exactly 1,280 generated output tokens across five fixed
256-token items. The stored `energy_output_token_j` uses the idle-subtracted
numerator; the gross mJ/output-token values above are therefore derived from
`gross_energy_j / 1280` rather than silently relabeling the stored field.

For the floor-compatible suite-level gross window on the Apple M3 Max /
powermetrics SoC-rail boundary, the OLMoE-versus-Qwen3-4B mean gap is
133.720 J, which clears the published 24.619 J suite-level gross
`floor_gate_j`. The other two pairwise descriptive gaps also clear that guard.
This is floor context only: the floor row requires drift review, the bundles
are claim-evidence-flagged, and the model/config points are unmatched in
architecture, scale, tokenizer, artifact, and quantization. No efficiency,
MoE, model-size, or architecture conclusion follows.

The verified extraction, all raw repetition values, denominator audit,
Qwen thinking-policy/config caveats, floor-compatible pairwise table, and
per-number bundle pointers are in
`docs/process_traces/2026-07-17-exploratory-block/results.md`.

### DSpark/DFlash feasibility smokes and D-075 fold-in

The separate lead-run MLX feasibility trace established that both DSpark and
DFlash execute natively with per-round acceptance observability. At the exact
small-target, 24-new-token smoke point, DSpark recorded 45.8 tok/s and 2.60
accepted tokens/round, DFlash 40.4 tok/s and 2.45 accepted tokens/round, and
baseline greedy 113.0 tok/s. Thinking mode was engaged and outputs were
unmatched. These are throughput/observability smokes, not energy measurements;
the baseline-faster inversion is hypothesis-generating input to
C5-2.5c's drafter-overhead break-even question, not its answer. Evidence:
`docs/process_traces/2026-07-17-dspark-dflash-smoke/`.

D-075 folds the six-axis evaluation into existing homes rather than minting a
new thesis per suggestion. It admits C5-2.5c as the primary speculative-
decoding Q4 break-even rider, C5-2.5b as proposal-work secondary, and
C5-2.5d as a mandatory contamination control while deferring C5-2.5a as a
bank-only cross-method rider. It also admits C5-2.11 on-device quantized KV and
one named hybrid-pair row, while attaching context/KV, prompt-cache,
module-nonattribution, kernel, and backend provenance refinements to existing
questions. All remain floor-gated candidate work, at or below L2 for this
intake, with named forbidden upgrades and unresolved NEEDS-WEB items. D-070
continues to reserve commitment and quiet-Mac ordering authority to Ed.

### Ed's deployment and current drift

Ed completed the manual site deployment represented by `b641f26`; the site
was current at that deploy snapshot. The real extension-axis synthesis,
DSpark/DFlash smoke, D-075 rows, exploratory inputs, and this reader-doc
re-wrap postdate it. `docs/site/DRIFT.md` now resets the baseline accordingly
and recommends folding these exploratory/agenda updates into the next natural
Ed-manual deploy, unless an imminent advisor review needs them sooner. No
agent regenerated or deployed the site in this re-wrap.

### Process notes retained without laundering

- **Stale-lock runner wart:** the lead reports that a stale campaign lock
  produced an exit-0 path instead of a clear failure. The retained exploratory
  campaign log contains only the three successful campaign rows plus their
  verdict rows, so this addendum records the wart as lead-reported rather than
  inventing a repository evidence pointer. The nine bundles themselves were
  independently strict-revalidated for this re-wrap.
- **Forced-report placeholder:** the fold-in round refused to treat a thin
  forced-report placeholder as the extension-axis synthesis. The real content
  was re-persisted in `f656c90` before D-075 consumed it. The refusal prevented
  placeholder text from becoming agenda authority.
- **Scope-check trip:** the fold-in scope check observed the lead's stray
  `scripts/quiet_mac_prep.sh`. It was adjudicated as benign parent-bench work
  and later committed in `4d20aad`; the check did its job by stopping silent
  ownership inference. This delegated re-wrap did not edit that script or any
  out-of-scope path.

### Addendum evidence and verification

| item | evidence |
|---|---|
| nine bundle values, token denominators, flags, and strict replay | `runs/exploratory_2026_07_17/`; `docs/process_traces/2026-07-17-exploratory-block/results.md` |
| DSpark/DFlash commands and smoke values | `docs/process_traces/2026-07-17-dspark-dflash-smoke/` |
| D-075 dispositions and candidate ceilings | D-075 in `docs/decision_log.md`; `docs/stream_logs/2026-07-17-axes-foldin.md` |
| deploy baseline and later commits | `git log b641f26..c6cf3e5`; `docs/site/DRIFT.md` |
| re-wrap drafting decisions and deviations | `docs/stream_logs/2026-07-17-rewrap.md` |

Verification commands for the addendum are recorded in the final delegated
return envelope. This remains a docs-only re-wrap: raw evidence, campaign
inputs, the state kernel, task queue, research-question rows, decision log,
and generated site were not modified.
