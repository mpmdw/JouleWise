# D/calibration/test executable series — Sol build

> **Superseded for use by the merged build** (`align/2026-11-08-dct-series-merged`, [DCT-SERIES-MERGED.md](DCT-SERIES-MERGED.md)) under RUN_STATE 226 R15. This record of the independent build is kept unchanged below.

2026-11-08. Base `origin/align/2026-11-08-v4-r11` (`05b6d04cb`).
Branch `align/2026-11-08-dct-series-sol`. **PROVISIONAL; requires the
independent Opus build, agreement and lead admission before native use.**
No measurement, weights, network or Block-5 outcome was accessed. R1 and the
blinded analysis job were not inspected or operated.

The implementation supplies one selected-window route:
`align_v4_series materialize` → `align_v4_session prepare --window-id …` →
the existing `bytes_h_session` view and plan writer → shared installer →
`run_night` HAZARD_PACK → the actual rendered zsh stage graph → terminal
record → the selected-window desk → bound R12 packet. W1 retains its exact
existing kit. There is no D-specific shell launcher or v5 runtime dependency.
Materialization alone does not make the incomplete native registration pass.

Read authority: both critical-path audits at
`origin/perf/2026-11-08-critical-path-sol{1,2}` (their dated reports),
`origin/main:RUN_STATE.md` items 214–221, the base's active stop card (NONE),
status/workspace/queue/do-not-do projections, Mission M0, orchestration,
`pilot_protocol_v4.md` roster, seed, U1–U6, R11 and R12 clauses, the owning
kit/registration/cadence/thermal-desk code. The older series proposal on
`origin/align/2026-11-08-v5-series-plan` is an input, not authority: its
seven-plus-reserve calibration and interleaved/adaptive-v5 test sheets are not
used. Coordination state is untouched under the brief's explicit exception.

## Frozen candidate and alternatives

The executable allocation is
`configs/campaigns/align_v4/series/series_manifest.json`. Its canonical bytes
bind kits, admission and triage. A plain edit to an unsupported allocation
refuses validation; change the reviewed builder and freeze again.

| Choice | Checked-in candidate | Other supported choice; ruling needed |
|---|---|---|
| D/F/C mapping | Separate D1–D3 fit windows, then C1–C8 | `alias_calibration`: D1=C1, D2=C2, D3=C3; requires an independently specified fit source |
| Order | W1, D1, D2, D3, C1…C8, T1…T3 | Alias mode removes the three separate D windows; no interleaving |
| Fit seeds | 101–107, 108–114, 115–121 | Reserved exclusively for fit; only used with separate D |
| Calibration seeds | C1 2–8; C2 9–15; C3 16–22; C4 23–29; C5 30–36; C6 37–43; C7 44–50; C8 51–57 | Prospective proposal, not an installed seed ruling |
| Test seeds | T1 201–207; T2 208–214; T3 215–221 | Six-test mode adds 222–228, 229–235, 236–242 |
| Test shape | Same 22-member v4 shape, 7 benign + 1 sabotage per pair | Shape and 3 vs 6 windows remain lead-owned |

Each later window has four **byte-identical original anchors** at ordinals
1–4; early W1:5 sentinel at 5; fresh benign alternating spam/bank at 6–19;
sabotage spam/bank at 20–21; late sentinel at 22. Midpoint follows ordinal
11. Both conditions use the first index of their window for the sabotage
member; the seed law deliberately omits condition. This is an allocation
proposal, not a common-random-number inference. All fresh F/C/T seed sets are
disjoint, exclude development 1/91/92/93, and retain the D seed-law tag
`qwen3.8-27b`. Every seed and first-turn seed is written numerically in the
manifest. W1's full 18-member selection roster is enumerated too.

Anchors, sentinels, W1 and fit members never enter `m`. A calibration window
is never relabelled fit or test. All eight calibration windows are used; no
first-39 selection, ninth counted window, conditional reserve, score-driven
extension or adaptive-v5 attack/control is present. Separate D is a conservative
**proposal** to make F/C/T separation concrete; it costs three extra windows
and has not been funded by a lead ruling. Alias mode avoids that cost only
after the scorer's fit source and allocation are settled.

Every generated kit preserves the complete 12-stage W1 scaffold: reservation,
pre capture/screen, 18-member corpus and bound derivation, start references,
science half A, midpoint reference, science half B, end references, post
capture, verdict and backup. Member 5 captures its own last-60-second idle
reference; subsequent heavy members consume its run ID and normalized config
digest across stage/process boundaries. The late sentinel replays member 5.
All D settings come from W1, including 300-second idle, 12 turns, 4,096 token
cap, B_D/T_dead, sampler/effort, G0/G1/holds and checkpointing off. Pending
values stay pending. No model directory is opened by materialization.

Per-window sizing uses the existing pilot-3 disk law, 25 scaffold members,
four anchor allowances and eighteen 1,800-second heavy-member allowances.
It yields 47 total members, 40,527 programmed seconds, 58,260 seconds by the
existing window-maximum formula (within 59,520), and 52,889,269,446 planning
bytes for two copies. These are programmed/reservation figures, not measured
duration, qualified native capacity or new energy evidence. The shared
prepare still encodes/checks the whole physical allocation and the existing
daytime disk/offload gate still runs. No unused ceiling is slept out.

## Concrete preparation and arm route

Before native preparation, the lead resolves the rulings below, admits the
manifest bytes and finishes the owning native W1 registration. Generate the
selected kits off the MBP, commit them in the measuring checkout and qualify
that exact head. For example, these are **off-window preparation commands**,
not authorization to run them while R1 or another measurement is active:

```sh
python3.13 -B scripts/align_v4_series.py candidate --d-mapping separate_fit --test-windows 3 --out configs/campaigns/align_v4/series/series_manifest.json
python3.13 -B scripts/align_v4_series.py materialize --window-id D1
python3.13 -B scripts/align_v4_series.py materialize --window-id C1
python3.13 -B scripts/align_v4_series.py materialize --window-id T1
python3.13 -B scripts/align_v4_series.py materialize --window-id C1 --check
```

Repeat materialization/check for every window in the selected `order`.
W1 uses `scripts/align_v4_kit.py --check` as before. Generated later kits live
at `configs/campaigns/align_v4_<window-id-in-lower-case>`; pack IDs use
`align-v4-<id>`. Source configs and manifest hashes must be reviewable before
install. Native `prepare` checks generated bytes rather than silently
regenerating a changed kit on the MBP.

`series/admission.json` has schema `joulewise.align_v4.series_admission.v1`,
`manifest_sha256`, `w1_collection_sha256`, and a `lead_signature` in the
existing `lead: <seat/session> YYYY-MM-DD` format. Its `choices` must equal
the manifest's `d_mapping`, `test_windows`, `test_shape` and `sentinel` objects.
Its `evidence` entries are explicit JSON locators
`{"path": "…", "sha256": "<64 hex>", "pointer": "/status"}` whose selected
value must be `"pass"`: `scorer_fit_contract`, `seed_allocation`,
`r13_r14_gate`, `paired_build_agreement`, and, after W1, `w1_clearance`.
These must be actual admitted source records, never a placeholder pass file.
The signature is the existing trusted-lead convention, not cryptographic
authentication. Hashes establish byte identity, not scientific truth.

```sh
python3.13 -B scripts/align_v4_session.py prepare --window-id C1 --measurement-root "$MEASUREMENT_ROOT" --session-root "$SESSION_ROOT"
python3.13 -B scripts/align_v4_session.py install --session-root "$SESSION_ROOT" --w1-disk-config "$DISK_CONFIG" --obc-off-attested-by "$OPERATOR" --topup-completed-at "$COMPLETION_TIME" --topup-source "$COMPLETION_SOURCE" --next-arm-triage "$TRIAGE_PACKET"
python3.13 -B scripts/align_v4_session.py desk --session-root "$SESSION_ROOT"
```

The disk flag retains its legacy W1 name. It is still the existing production
gate, in addition to selected-kit physical sizing; it is not permission to
reuse a stale W1 receipt. Native notice, PREQUAL, physical setup, charge/volume
rules, launchd observations, quiet/display dwell, meter, terminal/courier and
watchdog empty-process release remain mandatory. Do not execute any native
arm from an active agent session. No commit/push/offload overlaps measurement.

Selection is stored in `session.json`. Install checks the original source
root, the exact prepared manifest/admission digests, selected role and kit
bytes before the same shared installer is called. A changed admission needs
a new session. This also fixes D identity projection in the shared view:
ALIGN's frozen `align-model=` tag supplies the model ID, since the older
BYTES roster does not contain D. D no longer becomes `neg8_reference-<run>`.

## Between-window triage and desk

The selected-window desk uses the same harvest, immutable bundle reader,
meter diagnostics and U1–U3/battery/cohort checks. It carries the actual
window ID and separates anchor/sentinel/fit/calibration/test roster IDs.
It never infers final calibration eligibility from a successful CLI or from
counts alone. W1-specific contrast evidence remains W1 evidence. Existing
pending B/U3 gates stay pending; this stream does not supply numerical bars.

Build R12 packets off the MBP:

```sh
python3.13 -B scripts/align_v4_series.py packet --root "$MEASUREMENT_ROOT" --window-id C2 --sources "$TRIAGE_SOURCES" --out "$TRIAGE_PACKET"
```

`TRIAGE_SOURCES` is JSON with `history`, `checks`, and the mandatory boolean
`code_or_config_changed`. `checks` contains exactly the existing PACKET
source IDs from `v4_cadence.NEXT_ARM_TRIAGE`, with `status`, nonempty `basis`
and the JSON evidence locator above. The pointed value must equal `status`.
Use the committed finalizer/terminal/quiet/desk/adjudication records produced
by their owners. The producer embeds their exact UTF-8 JSON bytes under each
locator's `content_utf8`, rechecking SHA-256. The transported packet therefore
does not depend on Air-only paths existing on the MBP. Install preserves the
packet and source snapshots in the arm record; original locators remain
provenance text. The packet builder verifies source bytes; it does not replace
the owner's derivation or authorize hand-typed PASS. ARM checks are always
re-observed by production `arm_checks` and cannot be supplied by the packet.
The old consumer-only assertion format still serves legacy W1 callers;
`--window-id` enables these stronger bindings for the selected series.

`history` excludes W1 and contains every later attempt, in exact frozen order:
`window_id`, unique `attempt_id`, `status` (`final`/`provisional`),
`captured_members`, `eligible_benign` (`spam`, `bank`) and `evidence`. That
locator selects the exact five-field object without the locator itself from
the final/provisional eligibility record. F/T entries have zero calibration
counts. Captures cannot exceed the roster and eligible counts cannot exceed
captures. A zero-capture final refusal retries the same slot under a new
attempt ID; two consecutive refusals hold for the lead. A nonzero capture
consumes its slot even with zero eligible members. Source records remain
immutable, including lost attempts; a retry is never a replacement member.

The builder and actual install both reject skipped/reordered windows, wrong
next role, another manifest, detached history/counts, changed evidence and an
incorrect previous-W1 flag. Full desk must pass after W1 or changed code/config;
only an unchanged later window may defer it. From C6 onward prior calibration
eligibility must be final, preserving RUN_STATE 216's stricter fence. C8's
fixed-eight predicate requires all final counts and at least 39 **per pair**
before any test. Insufficient/provisional counts hold without another slot.

Before T1, add an admission evidence locator `test_threshold_freeze` selecting
an object with `status: "pass"`, `manifest_sha256` and
`calibration_rows_sha256`. The last digest is SHA-256 of canonical
`raw_json(calibration_rows)` as returned by `calibration_rows(manifest, history)`;
it binds the exact eight final counted attempts, including attrition/retry
history in the attempt identities. The actual scorer/threshold artifacts and
source digests belong in that signed source record. Every T arm rechecks this
binding; thresholds cannot silently follow new C counts.

U4–U6 are not certified by routing a per-window desk. Their existing portable
`v4_desk_evidence`/`align_v4_thermal_desk --compare-session` interface still
requires authenticated R1/W1 reference, frozen residual/scorer inputs and
final eligibility. This build does not invent those statistics or promote
legacy selection residuals into a qualified scorer.

## Lead rulings still needed (NEEDS_RULING)

| Question / options considered | Sol recommendation | Work held |
|---|---|---|
| D1–D3=C1–C3 vs separate fit D windows; what supplies F? | Admit separate F only if a frozen scorer actually needs it and fund the three extra windows; otherwise use alias mode with an explicitly qualified independent fit source. Never use C as F by relabelling. | Freeze/admit series before D1 |
| Test 3 vs 6; ordinary v4 benign/sabotage vs old v5 attack/control roster | Prefer six ordinary v4 windows for more empirical FPR evidence (42 benign/pair vs 21); decide power/precision/cost with R14. The checked-in three-window candidate remains unsigned. | Final T allocation/registration |
| Exact F/C/T seeds and benign/sabotage reuse | Admit the disjoint ranges above and deliberate within-role condition seed reuse prospectively, or change the reviewed builder before use. | Native series admission |
| R14 frozen scorer, F unit, LOTO/full-fit asymmetry, dependence and threshold source | Require the owning independent scorer/common-shift oracle and admitted fit support before D1; maximum/strict `>` and counts alone are insufficient. Freeze actual thresholds after C8 before T1. | Scorer/registration gates |
| W1 sentinel/cohort and U4 E_ref | Admit W1:5 only after completed, ≥3 turns, no X flags, exact identity and unchanged final policy; retain R1 replay + W1 5/17 E_ref. Ordinal 18 needs its own matched reference/recovery. | Later-window clearance |
| U4/U5 inconclusive requires two extra sentinels; where and with what sizing? | Preserve the consequence; freeze an explicit extra-sentinel variant and its bounds before a dependent arm. This builder currently supports the 22-member shape only. It must HOLD rather than claim a 24-member roster fits the old ceiling. | Conditional enlarged kit/desk |
| U3 predictive bar, B battery window consequence, U5 consequence and escalation/cohort amendments | Resolve in their owning registration lanes; do not turn the existing unconditional pending U3/B diagnostics into PASS here. A changed scientific configuration needs a new qualified manifest/cohort. | W1/native desk and later admission |
| Terminal, final eligibility, code/config-change and quiet-source receipts | Use source-bound finalizer/watchdog/adjudication outputs with named owners and declared semantics; the generic locator builder is not an independent authentication or physical check. | Actual R12 packet production |
| Sol/Opus agreement and native smoke | Compare independent builds and record the exact agreed route/head. Run final-head PREQUAL and ≤45-min non-registrable smoke before any long changed-code block. | All native use |

The software boundary is intentionally explicit: primary 22-member kits and
both mapping/count alternatives are implemented. No extra-sentinel placement,
alternate sentinel, new scorer or numerical scientific gate is silently
chosen. The anti-idle next step is to settle these decisions while R1 runs,
materialize/commit every admitted kit, then hand the magistrate a qualified
next-two-window packet. It is not to spend an MBP window discovering a pending
receipt or use a synthetic result as live qualification.

## Synthetic verification and remaining native checks

`python3.13 -B -m unittest tests.align.test_v4_series` replays the proposed
W1 → D1–D3 → C1–C8 → T1–T3 route. FakeWorld uses the real selected-session
prepare/install, plan writer, zsh graph and HAZARD_PACK driver. Native R1/U3/W1
readiness, model presence, identity producer, disk capacity/offload, launchd,
hazard/OS probes, collectors, meter/courier and measurement tools are synthetic.
The shared installer **call** is exercised; actual launchd installation is not.
Settle is zero through the writer's existing test seam, never in production.
Process census is synthetic because this sandbox refuses native `ps`/signals;
fake monitors have a bounded natural lifetime. No native process-group proof,
hardware performance, energy/thermal result or false-refusal rate is claimed.

The lead must run on the agreed final measuring head, outside agent load:
native installer/launchd and process-group tests, final-head PREQUAL and the
owning smoke kit; real W1/D generator/timing/memory qualification; real
meter/clock/volume/battery/terminal/quiet observations and signed registration
gates. Tiny MLX checks, no weights/data:

```sh
JW_ALIGN_MLX_NATIVE_TESTS=1 .venv/bin/python -B -m unittest tests.align.test_thermal_mlx
PYTHONPATH=. .venv/bin/python -B scripts/align_cache_checkpoint_native.py
.venv/bin/python -B -m unittest tests.test_run_night.HazardPackPrimitiveTests
```

The first two require usable native Metal and remain unrun here. They do not
qualify the real D model. Exact executed targeted tests/results and any failed
development attempts are recorded in the dated run report. No full suite is
run under the task's blinded-job resource rule.
