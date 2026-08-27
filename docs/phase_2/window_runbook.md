# Quiet-Mac Claim-Window Run-Book

**Operator:** Ed

**Lane:** `[QUIET-MAC]`

**Applies to:** claim-bearing Mac measurement windows after PR #85

**Main authorities:** D-077, D-078, and D-079 in `docs/decision_log.md`,
`docs/phase_2/detection_floor.md`,
`configs/campaign_policies/quiet_mac_p2_production.json`, and
`configs/campaigns/window_references/README.md`

This is the practical procedure for collecting one claim window. A **claim
window** is one uninterrupted measurement session whose members share one
power state, one instrument identity, one fresh NEG-8 drift bound, and one
whole-window verdict. A **member** is one run bundle. A **reference** is the
fixed `df_rq_mid` workload used to detect and budget drift. A **drift
allowance** is the nonzero uncertainty term that a passing window adds to
every floor or claim in the matching energy family.

Do not run this procedure while any agent session is active. The operator
owns the quiet machine from the first calibration through the post
calibration.

## 1. Rules that do not bend

The measurement checkout is named by `MEASUREMENT_REPO`. For the current
three-pack freeze its declared default is
`/Users/edr/JouleWise-measurement-20260813`; future freezes use the same
`/Users/edr/JouleWise-measurement-YYYYMMDD` convention and record the chosen
absolute path in `window.env`. Every repository-relative launch path and each
window runs root resolves from that checkout, never from a development
checkout.

- [ ] Start from reviewed, merged `main` with a clean measurement checkout.
- [ ] Close Claude, Codex, browser automation, periodic monitors, and every
  process that would wake or poll the machine.
- [ ] Launch one foreground shell chain and wait for its one completion
  event. Do not inspect logs while it runs.
- [ ] Keep the approved charger, cable, wattage, and power policy unchanged.
- [ ] Do not touch the keyboard, trackpad, lid, display controls, power
  settings, charger, or cable during the chain.
- [ ] Keep every display asleep and the screensaver disengaged throughout
  each campaign invocation. An awake display is a measurement contaminant,
  not an operator convenience.
- [ ] Use transient display sleep only. Do not change persistent display or
  screensaver preferences as part of a window.
- [ ] Settle for 150–240 seconds after operator activity, stage churn, a
  calibration retry, or a failed attempt. Use 180 seconds unless the frozen
  plan says otherwise.
- [ ] Preserve every failed, incomplete, or aborted artifact. Never delete or
  overwrite evidence to make a window pass.
- [ ] Quarantine an occupied retry slot outside the runs root, recollect the
  exact member, and record the old occurrence with
  `--record-supersession`.
- [ ] Do not waive environment admission, calibration, clock, thermal,
  adapter-continuity, anchor-fallback, mock-telemetry, or drift-allowance
  failures.
- [ ] Back up the immutable corpus before extraction.
- [ ] Until FLOOR-BIND-01 closes, honour registered limitation L1: a
  claim-bearing analysis may consume a floor artifact only when that artifact
  was produced by the governed extraction in the same lead-controlled custody
  session as **the analysis**. L1 binds extraction to analysis, not collection
  to extraction — collection may happen in an earlier session — but extraction
  and the analysis that consumes its floors may never be split.

The practical target is one compact 2–4 hour window. If the work will not fit,
split it into another independently calibrated window. A long window is not
more rigorous: the a5 collection showed that a delayed end reference can be
physically stale.

## 2. The post-PR #85 compatibility gate is satisfied

Merged main now provides all of the surfaces that the earlier draft was
waiting for:

- **Per-family screens and allowances.** The whole-window verdict evaluates
  `gross_energy` and `idle_subtracted_energy` separately. Each family gets
  its own derived repeatability bound and its own recorded drift allowance:
  `max(observed start/midpoint/end excursion, derived bound)`. Passing never
  turns the allowance into zero.
- **Reference triplet protocol.** The governed prospective references are
  under `configs/campaigns/window_references/`: three start members, one
  midpoint member, and three end members. The endpoint means and standard
  errors feed the screens; the midpoint catches an interior excursion.
- **Bound freshness.** The governed dual-family
  `joulewise.neg8_drift_bound.v1` artifact has a fixed 24-hour
  (`86400 s`) horizon and exact OS-build, power-supply-identity, and
  calibration-identity bindings. Expiry, an identity change, or unresolved
  bindings refuse with `neg8_drift_bound_stale`.
- **Anchor-fallback member gate.** A fallback-clock-anchored member cannot
  supply a floor or claim cell. For floor-campaign roles it is an unwaivable
  rerun trigger, reported as `anchor_fallback_member_unusable`.

Therefore a new claim window may proceed. Do not fall back to the old
single-start/single-end practice for new collection.

Before freezing the plan, confirm the command surface:

```sh
.venv/bin/python scripts/run_campaign.py --help
```

The required options are `--arm-quiet-mode`, `--arm-countdown-s`,
`--log`, `--instrument-calibration-dir`, `--instrument-power-policy`,
`--derive-neg8-drift-bound`, `--neg8-drift-bound-output`,
`--whole-window-verdict`, and `--neg8-drift-bound`.

### Decision on the three flags missing from the draft chain

The merged CLI accepts all three. They are deliberately included in every
measurement-campaign invocation in this run-book:

- `--arm-quiet-mode` counts down, calls `pmset displaysleepnow`, and then
  performs the complete governed environment re-probe. It is the merged
  enforcement surface for the display/screen-contamination lesson.
- `--arm-countdown-s 20` is not syntactically required; the CLI default is
  5 seconds. The proven `claim_windows.sh` used 20 seconds, and this run-book
  keeps that operator margin so Ed can step away before display sleep and
  re-probe.
- `--log "$RUNS_ROOT/campaign_log.jsonl"` is also not syntactically required
  because the same path is the default. It remains explicit so collection,
  supersession, verdict, and later consumers all name the same custody log.

The verdict and bound-mint modes do not measure a member, so they receive
`--log` where applicable but not the display-arm flags.

## 3. Time budget in plain language

Budget these pieces before selecting campaign stages:

| Operation | Expected time |
|---|---:|
| Stage settle | 180 seconds |
| Display arm inside each campaign | 20-second countdown plus re-probe |
| Protocol-v3 calibration | about 4 minutes; the commanded schedule alone is 196.7 seconds |
| NEG-8 bound corpus | 12 ordinary reference members plus one 180-second settle |
| Start references | 3 ordinary reference members plus one settle/arm |
| Midpoint reference | 1 ordinary reference member plus one settle/arm |
| End references | 3 ordinary reference members plus one settle/arm |
| Failure margin | at least 20% of the planned window |

Use the dry run and prior measured member durations to budget the ordinary
members. Do not estimate them from model size alone. If the reference corpus,
two calibrations, seven window references, chosen science stages, settles,
and failure margin do not fit in the window, remove science stages before
arming.

The 24-hour freshness horizon is a ceiling, not permission to reuse
yesterday's bound. For this procedure, the 12-member bound corpus must be
collected and the bound must be minted **inside the same quiet window that
uses it**, before the start triplet. This keeps the OS, supply, and
calibration identity aligned and makes the bound causal for that window.

## 4. Freeze the plan before quiet time

Create one plan directory outside the runs roots:

```text
WINDOW_PLAN_ROOT/
├── window.env
├── before_midpoint_stages.txt
├── after_midpoint_stages.txt
├── extraction_spec.json
├── waivers.json
└── window-chain.zsh
```

Each stage-list line is one repository-relative config directory, for
example:

```text
configs/campaigns/p2_015_floors/04_phase_prefill_abba
configs/campaigns/p2_015_floors/03_request_abba
```

Do not put the reference directories in those lists; the chain adds the
governed 3+1+3 references itself.

Example next-generation ALPHA `window.env`, prepared while the `_v4` pack is
committed but **before** that generation receives `freeze-0004.json`. This file
is a frozen literal input to the T-0 producer: it has exactly the keys below,
every path is absolute, and no value contains `$` or a shell expansion.
`FROZEN_PLAN` is R2's execution-boundary literal for the committed pack-relative
`calibration_plan.json`; it is not a custody reservation plan. Replace the
dated path components before review, then freeze the resulting bytes:

```sh
MEASUREMENT_REPO=/Users/edr/JouleWise-measurement-20260813
WINDOW_ID=plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v4
BRACKET_SESSION_ID=d117-alpha-YYYYMMDD-calibration
FROZEN_PLAN=/Users/edr/JouleWise-measurement-20260813/configs/campaigns/d117_floor_qwen25_1p5b_v4/calibration_plan.json
PACK_ROOT=/Users/edr/JouleWise-measurement-20260813/configs/campaigns/d117_floor_qwen25_1p5b_v4
PACK_ID=d117_floor_qwen25_1p5b_v4
PLAN_ID=plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v4
EVIDENCE_ROOT_ID=evidence-d117-floor-qwen25-1p5b-v4
IDENTITY_EPOCH_JSON=/Users/edr/JouleWise-window-custody/d117-alpha-YYYYMMDD/identity-epoch.json
T1_BINDINGS_JSON=/Users/edr/JouleWise-window-custody/d117-alpha-YYYYMMDD/t1-bindings.json
PRE_ATTEMPT_ID=d117-alpha-YYYYMMDD-calibration-pre
POST_ATTEMPT_ID=d117-alpha-YYYYMMDD-calibration-post
RUNS_ROOT=/Users/edr/JouleWise-measurement-20260813/runs_d117_floor_qwen25_1p5b_v4
BOUND_RUNS_ROOT=/Users/edr/JouleWise-measurement-20260813/runs_d117_floor_qwen25_1p5b_v4_bound
CALIBRATION_LEDGER=/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl
LEDGER_HEAD_PIN=/Users/edr/JouleWise-measurement-20260813/configs/calibration/calibration_ledger_head.json
ARM_READINESS_CUSTODY_ROOT=/Users/edr/JouleWise-window-custody/d117-alpha-YYYYMMDD/readiness
CUSTODY_ROOT=/Users/edr/JouleWise-window-custody/d117-alpha-YYYYMMDD/window
WINDOW_CUSTODY_ROOT=/Users/edr/JouleWise-window-custody/d117-alpha-YYYYMMDD/window
QUARANTINE_ROOT=/Users/edr/JouleWise-window-quarantine/d117-alpha-YYYYMMDD
CLAIM_BACKUP_DEST="/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/d117-alpha-YYYYMMDD/claim"
BOUND_BACKUP_DEST="/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/d117-alpha-YYYYMMDD/bound"
WAIVER_PATH=/Users/edr/JouleWise-window-custody/d117-alpha-YYYYMMDD/readiness/window-plan/waivers.json
POWER_POLICY=ac_high_power
SETTLE_S=180
```

`RUNS_ROOT` holds the claim-window members and calibration bracket.
`BOUND_RUNS_ROOT` holds only the 12-member settled-reference corpus used to
mint this window's bound. Keep the roots separate so the corpus members do
not accidentally enter the claim-window member basis.
`ARM_READINESS_CUSTODY_ROOT` holds T-0 sources, evidence, arm receipts, and
consumptions. `WINDOW_CUSTODY_ROOT` is the distinct fresh-empty `custody_root`
bound into `ARM_CONTEXT_JSON` and later receives operator/close-out artifacts.
`QUARANTINE_ROOT` is a third, sibling root outside both custody roots; nesting
it below `WINDOW_CUSTODY_ROOT` would make the arm generator's require-empty
check refuse itself.
`CUSTODY_ROOT` and `WINDOW_CUSTODY_ROOT` are deliberately the same literal:
the former is the T-0 producer/author contract key and the latter is retained
for the foreground chain. `CLAIM_BACKUP_DEST` and `BOUND_BACKUP_DEST` are
distinct. Place `WINDOW_PLAN_ROOT` at
`ARM_READINESS_CUSTODY_ROOT/window-plan`; the author requires the plan root
containing `window.env` and `window-chain.zsh` to remain inside the D-134
custody root.

The v1 ALPHA and BETA `plan_tree.json` bytes carry the superseded
repository-relative spelling; the shared R2 resolver refuses those packs, and
they are never basename-repaired in an operator file. The `_v2` successor
family (amended 2026-08-18) emits the ruled `plan.path:
"calibration_plan.json"` shape in all three profiles, so this example binds
the `_v2` packs; the v1 packs remain historical records behind their
committed freeze-0001 receipts.

Before quiet time:

- [ ] Give every planned bundle one unique run ID.
- [ ] Freeze membership and stage order before looking at outcomes.
- [ ] Create `waivers.json` containing `[]`.
- [ ] Keep quarantine, operator logs, extraction output, and the plan outside
  both runs roots.
- [ ] Validate every config.
- [ ] Dry-run every stage against its intended root.
- [ ] Resolve every doctor warning; do not add `--ack-config-warnings`
  casually.
- [ ] Record `git rev-parse HEAD`.
- [ ] Materialize `RUNS_ROOT`, `BOUND_RUNS_ROOT`, `WINDOW_CUSTODY_ROOT`, and
  `QUARANTINE_ROOT` as four distinct empty directories. The first two live
  under `MEASUREMENT_REPO`; quarantine remains outside window custody.
  `prewindow_check.sh --window` accepts these exact empty roots but refuses
  any matching occupied or non-directory path. The arm-context gate requires
  all four directories to exist, resolve distinctly, and remain empty through
  T-0 authoring and ARM.

### D-134 readiness freeze, committed-pack digest, and rehearsal

For an ALPHA, BETA, or GAMMA night, `PACK_ROOT` means the exact per-plan
campaign-pack directory, and `PACK_ID` means that directory's final path
component, which the readiness implementation records as the pack ID. The
sole authority for which readiness rows belong to those plans is the ruled
live registry `configs/arm_readiness/d117_row_registry_v2.json`; the frozen
`_v1`–`_v3` packs pin the archival `d117_row_registry_v1.json` coordinate in
their immutable plan trees, and neither file is ever edited to match the
other. Record the live registry's path, SHA-256, registry ID, and plan
profile in the plan tree; the Markdown readiness pages are checked human
views, not row authority.

Freeze readiness only with the implemented command:

```sh
python3 scripts/generate_arm_readiness.py freeze \
  --pack-root "$PACK_ROOT" \
  --predecessor-pack-root "$PREDECESSOR_PACK_ROOT"
```

`PREDECESSOR_PACK_ROOT` is the previous-generation sibling pack — for a pack
ID ending `_v<N>`, the `_v<N-1>` directory beside it under the same campaigns
root — and every successor pack refuses to freeze without it; a
first-generation (`_v1`) pack opens its own chain, so it omits the flag
entirely and is refused if it passes one.

The command writes the pack's no-clobber freeze receipt — a first-generation
pack opens its own chain and mints `freeze-0001.json`; a successor generation
`_v<N>` mints `freeze-000<N>.json` and must pass `--predecessor-pack-root` —
and a GNU-style SHA-256 sidecar under the governed
`PACK_ROOT/arm_readiness.freeze.receipts/freeze-NNNN.json` namespace. A freeze receipt
contains only freeze-evaluable rows and always has
`arm_disposition: NOT_APPLICABLE`; even a `PASS` freeze receipt cannot license
a night. `plan_tree.json` pins that receipt's relative path and digest and
declares the future arm-receipt schema, governed namespace, and pack-digest
algorithm through the required D-134 attachment. It deliberately does **not**
name or hash a future arm receipt.

The freeze update to `plan_tree.json` uses the pack generators' established
two-space, insertion-order JSON rendering. This is an intentional,
load-bearing byte contract, not an oversight: changing it to sorted-key
rendering would make the matching pack generator's post-freeze
`generate_configs.py --check` disagree with the frozen bytes. Do not “tidy”
that serialization.

For the three packs frozen on 2026-08-13, the committed D-134 freeze receipt
and its plan-tree pin are authoritative over the legacy `unfrozen_draft`
wording that remains byte-frozen in `draft_status` and `README.md`. Do not
repair those committed bytes. The 2026-08-14 M-2 ruling in
`docs/decision_log.md` requires the generators to emit freeze-aware status and
README text only for future regenerated packs while preserving current-pack
`--check` byte identity.

After the freeze changes and every other pack byte are reviewed and
committed, the final pack digest is
`joulewise.committed_pack_tree_sha256.v1`. It is the SHA-256 of this exact
framing:

```text
b"joulewise.committed_pack_tree_sha256.v1\n" +
for each committed file, sorted by raw UTF-8 path bytes:
  relative_path + NUL + git_mode + NUL + byte_length + NUL +
  lowercase_sha256_of_file_bytes + LF
```

The digest includes every committed file below `PACK_ROOT`, including
`plan_tree.json`, its sidecar, the U11 identity-projection receipt, the freeze
receipt, readiness evidence, and their sidecars. Only ordinary Git blobs with
mode `100644` or `100755` are admitted. Missing, untracked, changed,
non-UTF-8, symlink, submodule, or other special entries refuse. No pack file
stores this digest: the external arm receipt computes and binds it after the
pack is final, which prevents an arm-receipt hash cycle.

Readiness evidence has exactly two governed namespaces. `PACK` means
`PACK_ROOT/arm_readiness.evidence/`; `WINDOW_CUSTODY` means
`ARM_READINESS_CUSTODY_ROOT/PACK_ID/arm_readiness.evidence/`. Evidence paths in receipts are
relative to one of those roots and may not escape it. Every JSON receipt has
its matching `.sha256` sidecar; a missing, extra, malformed, stale, or
unpaired entry refuses rather than being skipped.

After the final pack is committed at the reviewed HEAD, the lead creates the
non-authorizing readiness rehearsal receipt with:

```sh
python3 scripts/generate_arm_readiness.py dry-run \
  --pack-root "$PACK_ROOT" \
  --window-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --rehearsal-id "$REHEARSAL_ID" \
  --synthetic-root "$SYNTHETIC_ROOT"
```

This D-134 dry run is distinct from the campaign-stage `--dry-run` commands
below. It executes the **real** calibration reservation CLI with `--execute`
and the production ledger-writer lifecycle through both reserved calibration
slots, under the real lease implementation. It stops before live MLX or
`powermetrics` capture because entering capture would breach the quiet-machine
fence while an agent or desk session is active. Thus the rehearsal is neither
mock-only nor a live measurement. It writes
`ARM_READINESS_CUSTODY_ROOT/PACK_ID/arm_readiness.dry_run.receipts/dry-run-NNNN.json`, has
`arm_disposition: NOT_APPLICABLE`, may bypass no freeze refusal, and can never
serve as an arm receipt. Require its `PASS` receipt to bind the exact final
reviewed HEAD and final pack digest; any later HEAD or pack-byte change makes
it stale. Synthetic substitution is closed to `LIVE_PRIVILEGE`, `LIVE_CLOCK`,
`LIVE_MACHINE`, `LIVE_POWER`, `PRODUCTION_ROOTS`, `PRODUCTION_BACKUPS`,
`PRODUCTION_LEDGER`, and `LAUNCH_CONSUMPTION`; the receipt must enumerate each
substitution in `omitted_live_domains`.

Useful checks:

```sh
git status --short --branch
git rev-parse HEAD

.venv/bin/python -m joulewise doctor --campaign --json \
  configs/campaigns/neg8_reference_corpus/neg8-refcorpus-*.json \
  configs/campaigns/window_references/start_triplet/neg8-window-start-*.json \
  configs/campaigns/window_references/midpoint/neg8-window-midpoint.json \
  configs/campaigns/window_references/end_triplet/neg8-window-end-*.json

.venv/bin/python scripts/run_campaign.py \
  configs/campaigns/window_references/start_triplet \
  --runs-dir "$RUNS_ROOT" \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
  --dry-run
```

Repeat the dry run for the bound corpus, midpoint, end triplet, and every
science stage. Dry-run mode does not write campaign-log entries.

## 5. Machine and operator preflight

- [ ] Connect the approved charger and cable. Record wattage and
  `POWER_POLICY`.
- [ ] Finish or pause Time Machine, software updates, indexing churn, large
  downloads, and cloud uploads.
- [ ] Confirm `sudo -n powermetrics` succeeds.
- [ ] Perform the pre-window clock stabilization in §5A. It needs
  administrator rights, so only Ed can do it and the chain cannot.
- [ ] Let idle-triggered background daemons run **before** the window, not
  inside it. macOS starts idle-only work — XProtect's scheduled malware scan
  is the documented instance — in roughly the first 10 minutes after the
  machine goes quiet. Leave the machine untouched and idle for at least 10
  minutes **before** the §5C step-2 calibration-ledger pair. The frozen
  `prewindow_check.sh --wait` invocation fulfills this idle and must have
  exited with `READY` before the ledger commands begin. This is in addition
  to the chain-owned 180-second stage settle, not satisfied by it.
- [ ] Confirm the chain carries the §5B pre-flight calibration screen and
  that the frozen plan records the pre-registered retry bound (D-079
  clause 3).
- [ ] Confirm both fresh runs roots do not already contain member bundles.
- [ ] Confirm the backup destination exists and has enough free space.
- [ ] Close every agent and browser-automation session.
- [ ] Explain the single rule to anyone nearby: do not touch the Mac until
  the chain announces completion.

Run the preparation probe once, read its result, and correct any failure
before closing the final terminal:

```sh
bash scripts/quiet_mac_prep.sh
```

That script uses transient display sleep and does not change persistent
display or screensaver settings. The campaign still arms and re-probes on
every invocation; the preparation script is not a certificate for later
members.

An idle-triggered daemon that fires inside the window contaminates the member
it lands on and will fail CPU admission. That is the gate working, not a false
alarm: window a9's first bound-corpus member was lost exactly this way and was
correctly caught. The response is always preserve, quarantine, supersede, then
relaunch (§10). It is never a waiver and never `--environment-override`.

### D-117 §5 amendment — calibration-ledger readiness before arming

This checklist is in force for every prospective calibration bracket. Run the
machine command against the exact frozen reservation plan; `inspect` remains
diagnostic and never authorizes ARM.

- [ ] Run `recover_calibration_ledger.py readiness --phase pre-reserve
  --session-id "$BRACKET_SESSION_ID" --plan "$FROZEN_PLAN"` before reservation
  and the exact `--phase pre-slot --session-id ... --slot ...
  --attempt-id ... --plan "$FROZEN_PLAN"` check before each slot.
- [ ] Treat structured `status: ready` from the public readiness command as
  diagnostic early warning only. Never infer ARM permission from it or from
  `inspection.state`, even when either field says `clean`.
- [ ] Confirm the phase-appropriate pin relation: `exact` at pre-reserve,
  the exact governed session extension at pre-slot, and an authenticated
  terminal candidate at terminal.
- [ ] Confirm the machine reports no active legacy journal, append intent,
  residue, incompatible operation target, partial custody, or live writer.
- [ ] Read the D-117 §10 procedure below and prepare truthful operator identity
  and attestation values before the quiet window begins.
- [ ] Treat `needs_pin_commit: true` absent its valid pre-slot relation — the
  exact governed session extension — as desk work that ends a 2 a.m. attempt.
  At an enforcing pre-slot check reporting that relation, the flag is
  expected and only schedules the pin commit for the desk. It never licenses
  an uncommitted-pin override.

The public readiness, `audit`, `audit-observations`, and `validate-slot`
commands are early warning or validation only and never emit `ready_to_arm`.
Only the reservation CLI's enforcing `pre-reserve` check and the writer's
enforcing `pre-slot` check can emit `ready_to_arm`, and only while holding the
resolved-ledger-identity lease. Both inspect custody across every finalized
session in the authenticated snapshot. The writer holds that same lease
continuously through countdown, capture, finalization, or governed abort.

## 5A. Pre-window clock stabilization (administrator step; Ed performs it)

**This is operational stabilization, not a protocol waiver.** The 5 ms
wall-versus-monotonic anchor ceiling stays exactly where it is. It is never
relaxed, widened, or waived, and a member that trips it is still lost. The
steps below reduce how often the machine trips it. They do not change what
trips it.

### JW-MET-2 keyboard-backlight census control

Before the untouched idle begins, open **System Settings → Keyboard** and set
keyboard brightness to zero, turn **Adjust keyboard brightness in low light**
off, and set **Turn keyboard backlight off after inactivity** to **Never**.
Visually verify the zero level: macOS provides no reliable CLI for the actual
backlight level. Record these four literals exactly:

```text
keyboard_backlight.level=0
keyboard_backlight.automatic_adjust=false
keyboard_backlight.inactivity=never
keyboard_backlight.verification=operator_visual
```

`quiet_mac_prep.sh` inventories whether `ioreg` reports
`KeyboardBacklight`; `prewindow_check.sh` repeats the visual-verification
census note. Neither substitutes for Ed's System Settings observation. Make
no further keyboard or backlight adjustment after authoring T-0 evidence.

### What went wrong, in plain language

Every measured member must be anchored causally in time. The anchor check
compares two clocks: the **wall clock**, which is the machine's idea of the
current date and time and which network time synchronisation adjusts, and the
**monotonic clock**, a counter that only ever counts forward and is never
adjusted. The difference between them must stay within `5 ms`
(`MAX_WALL_MINUS_MONOTONIC_SPAN_S`, `joulewise/uncertainty_evidence.py:22`)
across a member's clock stamps. When it does not, the predicate at
`joulewise/uncertainty_evidence.py:367` refuses the member with the detail
string `wall_minus_monotonic_span_exceeded`.

Two consecutive window-C collection attempts on 2026-07-26 failed on exactly
that, and on nothing else:

| Attempt | Member that failed | Observed span | Implied rate |
|---|---|---:|---:|
| 1 | `p2015-df-cmp-abba-ph-decode-b02-b2` | 5.544 ms | about +110 ppm |
| 2 | `neg8-refcorpus-r11` | 7.769 ms | about −158 ppm |

Rates of that size are what `adjtime(2)` produces. `adjtime(2)` is the system
call network time synchronisation uses to correct the wall clock by speeding
it up or slowing it down by a fraction of a percent, instead of jumping it, so
that time keeps increasing. The evidence shows a **slew** — a gradual change
of rate — and not a demonstrated discrete step: no timestamp ever moved
backward, and the native powermetrics second counter advanced only by 0 or 1
whole seconds. A step hidden inside the roughly 44-second gap between stamps
cannot be categorically excluded.

Two things are unknown and must be written as unknown wherever this is
reported:

- **The responsible process is unknown.** `joulewise/environment.py:908`
  assigns `clock_sync.status = "limited_without_admin"` unconditionally, and
  the `timed_running` field only reports whether `pgrep` found the process.
  Every member, passing and failing alike, reported `timed_running=true`. The
  macOS `timed` daemon is therefore **plausible but unproven**; attributing it
  would require privileged inspection of the unified log.
- **The correlation with time of day is noted but unproven.** Window B had
  zero occurrences across 59 members, collected 23:57–03:15 local. Window C
  ran roughly 7% per member — 2 occurrences across about 30 members, collected
  03:17–05:19 local. Do not assert a nightly maintenance-window cause.

What is established: only a privileged wall-clock adjuster can produce this.
Ordinary sampling load, thermal state, and CPU activity cannot move the wall
clock relative to the monotonic clock. The excursion also self-clears — member
`neg8-refcorpus-r12`, collected immediately after the failing `r11`, anchored
cleanly with a 0.305 ms span.

### Before the window (administrator rights required)

macOS gates both the read and the write of this setting behind administrator
rights (`systemsetup -getusingnetworktime` and
`systemsetup -setusingnetworktime`). E-4's prior-state read remains an
interactive Ed action. D-127 authorizes only the exact `off` and `on` writes;
the capture wrapper and the T-0 author use the `off` vector, and restore uses
the `on` vector. No wildcard or privileged `get` is authorized.

The tracked D-127 fragment must contain exactly these bytes (final newline
included; SHA-256
`7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d`):

```sudoers
# JouleWise D-127: fixed network-time toggle capability for operator edr.
Cmnd_Alias JOULEWISE_NETWORK_TIME = /usr/sbin/systemsetup -setusingnetworktime off, /usr/sbin/systemsetup -setusingnetworktime on
Defaults!JOULEWISE_NETWORK_TIME !requiretty
edr ALL=(root) NOPASSWD: JOULEWISE_NETWORK_TIME
```

- [ ] **ED-OWED:** after the reviewed tracked fragment
  `scripts/joulewise-network-time.sudoers` exists, run the authenticated,
  no-overwrite installer from
  `docs/process_traces/2026-08-08-d127-autonomous-loop/CONSULT-RESPONSE.md`
  with that source path and the digest above. Ed alone installs
  `/etc/sudoers.d/joulewise-network-time`; no repository script runs as root.
- [ ] **ED-OWED:** exercise both exact vectors from a cold credential state,
  restoring `on` at the end:

  ```sh
  /usr/bin/sudo -k
  /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off
  /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on
  ```

  A password prompt, any nonzero exit, or any other permitted
  `systemsetup` argv leaves D-127 unqualified and blocks T-0.

- [ ] **Confirm the system clock is actually correct first.** Disabling
  automatic time on a wrong clock freezes that error in place for the whole
  window. Compare the system clock against an independent trusted source and
  correct it before going further.
- [ ] Record the current setting so it can be restored:

  ```sh
  /usr/bin/sudo /usr/sbin/systemsetup -getusingnetworktime
  ```

- [ ] Disable automatic network time adjustment:

  ```sh
  /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off
  ```

- [ ] Preserve the independent-clock comparison and the captured prior
  `systemsetup` output as source evidence. Require an authenticated exact-key
  `CLOCK_ATTESTATION` receipt in
  `ARM_READINESS_CUSTODY_ROOT/PACK_ID/arm_readiness.evidence/`; its irreducible observation
  is an `OPERATOR_ATTESTATION`, not a hand-entered readiness verdict.
- [ ] After disabling network time, require the T-0 author's fresh,
  idempotent D-127 enforcement call
  `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` and an
  authenticated exact-key `CLOCK_PROBE` receipt in the same namespace. The
  successful exact write, not an operator-entered row value, establishes the
  current off postcondition. For both receipt kinds, “exact-key” means the top-level
  object contains exactly `schema_version`, `evidence_id`, `kind`, `status`,
  `issued_at_utc`, `valid_until_monotonic_ns`, `pack_sha256`, `head_commit`,
  `facts`, `checks`, `reason_codes`, and `assurance`; unknown or missing keys
  refuse.

- [ ] Do **not** hand-count a settle here. §5C removed the separate pre-launch
  settle step: the final 180-second settle is **chain-owned** (the `settle` at
  the top of `window-chain.zsh`, §6), and §5's ≥10-minute untouched idle
  covers this administrator action along with every other operator action
  before the §5C step-2 ledger pair. Your last action is the launch itself;
  step away immediately after it.

  The readiness row `clock.network_time_off` asks only for that fresh exact
  enforcement result.
  It does not introduce another hand-counted settle. The required quiet waits
  remain §5's completed ≥10-minute untouched idle and the chain-owned
  180-second settle after the operator's launch.
- [ ] After the window closes, meaning after `measurement_complete`, the
  whole-window verdict, and the backup, re-enable it:

  ```sh
  /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on
  ```

  The restore comes last because re-enabling automatic network time permits
  the system to slew the wall clock, and the verdict, backup, and close-out
  steps are still reading clock-anchored evidence and custody metadata. Wake
  the display, confirm `measurement_complete`, then hand back — the restore
  is a separate tap after the magistrate's §9 and §11 steps.

- [ ] Record in the close-out that automatic time was disabled, when it was
  disabled, and when it was restored.

Leaving automatic time off is not a protocol state. It is a temporary machine
condition the operator owns for one window, and the close-out must show it was
returned.

### If a single member still fails the anchor

Stabilization lowers the rate; it does not make the failure impossible. When
one member refuses with `wall_minus_monotonic_span_exceeded`, no member-level
anchor retry is adopted. Under D-113 clause 9, no such retry occurs without a
prospective ruling made before the plan freeze:

- [ ] **Do not mint a bound, a verdict, or a floor from a basis that contains
  the invalid occurrence.** An invalid member never becomes a valid one.
- [ ] Preserve and quarantine the invalid member. Valid members already
  collected stay exactly where they are, but no replacement member is
  collected under an unruled retry.
- [ ] Stop the stage under the existing `--max-failures 1` behavior and take
  the disposition to the lead. Do not hand-retry, supersede, or rerun the
  dual-family bound mint as if a member-level retry were licensed.

`--max-failures` stays at 1. Every admission gate, every family screen, and
every refusal stays exactly as written. Calibration-only retry remains
governed as written in §6 and is not changed by this member-level prohibition.

## 5B. Pre-flight calibration screen (D-079 clause 3)

**What this catches, in plain language.** The pre-calibration measures how
badly the power instrument can be wrong about *when* energy was used. It
reduces to one number, the fiducial bound (`b_fiducial_s` in
`instrument_evidence.json`). Most captures land near 27 ms. Occasionally the
GPU is still ramping its clock and voltage up through low-frequency states
while the calibration pulses run — the raw evidence shows the GPU is not
idle — and the estimator, which fits each pulse as a clean rectangle with a
movable start time, absorbs that ramp as an apparent shift in the pulse's
start. The result is an out-of-family calibration. Window B on 2026-07-26 hit
exactly this: a 35.435841 ms pre-calibration, the highest in the entire
corpus, which was only discovered at the post-calibration and cost the whole
3.5-hour campaign. The condition cannot be predicted before a calibration is
taken, but a four-minute calibration detects it reliably. That asymmetry is
the entire point of this step.

**Who performs this.** These four steps are performed **by the chain**, not by
the operator (`screen_pre_calibration` in `window-chain.zsh`, §6; §5C step 1).
They are written out here so the screen's logic, threshold derivation, and
retry rules are auditable — not as a manual procedure. The operator never
inspects logs mid-run and never reads `b_fiducial_s` by hand. The retry rules
below are the **lead's** disposition rules for after a chain-emitted failure.

**The screen.** Immediately after the pre-calibration mints, and before any
member is collected:

1. Read `b_fiducial_s` from the newly minted
   `RUNS_ROOT/instrument_validation/<id>/instrument_evidence.json`.
2. Require `b_fiducial_s <= 0.032898493715362` (32.898493715 ms). This is the
   larger, and so the more conservative, of the prior observed maximum
   (33.558756680 ms) and the 95% Student-t upper level for a new observation
   over the same n=19 corpus (33.353749299 ms).
3. If the value exceeds the threshold, **abort before member 1** and go to
   the retry rules below. Do not proceed and hope the post-calibration
   agrees; it will not save the window, and every member collected after a
   failing pre-calibration is wasted quiet time.
4. If the value passes, continue the chain unchanged.

The threshold is a derived, provenance-bound number, not a house style: it is
valid only for Mac15,9 / macOS 25F84 /
`ac_high_power` / 100 ms cadence / `joint_loss_sublevel_interval_branch_v2`
bindings, and it is re-derived when any of those change (D-079 clause 3).

**Single source of truth.** This value is *derived from* the issued D-079
calibration-acceptance artifact (`d079_calibration_acceptance_v2_n17_r3`, sha
`73f02263…`), not independently chosen. The only stored comparison is two-way:
the chain's frozen `PRE_CAL_FIDUCIAL_MAX_S` literal must equal the
acceptance-derived value. Then execute the writer's authenticated
`_derive_preflight_systematic_screen_s()` path and require its runtime result
to equal that same value. The writer has no copied scalar after CH-1 (PR #142;
2026-08-14 decision-log entry). A successor acceptance before arm therefore
requires a newly derived chain literal and a regenerated pack; record the
two-way check and executed runtime derivation before recording the chain
SHA-256.

This screen is a **level** check on one calibration, and is entirely separate
from the **drift** check between the two calibrations in §8. A level failure
is an out-of-family systematic condition and is never budgeted (D-079
clause 2).

**Retry rules — the cause-removal test.**

- A failing pre-calibration ends **that attempt**, not necessarily the night.
- A retry is permitted **only** when a specific, named cause has been
  identified **and removed**. Record the retry as a deviation in the
  close-out, preserve both attempts as immutable evidence, and stay inside
  the retry count pre-registered in the frozen plan.
- **With no identifiable cause, the window ends.** Stop, preserve everything,
  and take the disposition to the lead.
- The line that matters: re-running until the number passes is selection on
  the **outcome**. That is calibration shopping, it makes the accepted
  calibration the luckiest draw rather than a representative one, and it
  would invalidate every claim built on the window. Re-running after removing
  a named **cause** is legitimate, because the second attempt measures a
  genuinely different machine state.
- Worked example (2026-07-27, window C): Apple's XProtect malware scanner was
  observed at 94% CPU as the window's first member began. The environment
  gate refused the member — correctly. The scanner was identified as the
  cause, the operator waited 14 minutes for it to finish, and the relaunched
  window collected 59/59 clean. Named cause, removed, verified, recorded:
  that is a legitimate retry. "It failed, so I ran it again" is not.

D-079 defines this screen on the pre-calibration only. If the **post**
calibration's level exceeds the same threshold, the members are already
collected and no retry can help: preserve everything, record it in the
close-out, do not budget the excess (D-079 clause 2), and refer the
disposition to the lead.

## 5C. D-117 manual arming and quiet handoff (cold-gate ruling 2026-08-08)

Use this final checklist only after §4 has frozen the plan and you have
read §§5, 5A, and 5B. It exists because the recovery cold gate ruled that
ARM authority is **not** any automated artifact: the witness corpus and
every readiness command are evidence *toward* arming, never the arming
authority. Arming happens only when the plan-bound GO record is green, the
lead has completed the rule-1 desk verification below, and Ed performs the
physical steps himself.

**Entry gate (desk, before the night).**
Confirm `git status --short --branch` shows a clean measurement checkout and
`git rev-parse HEAD` equals the exact reviewed, merged `main` commit. Then
authenticate the two-stage lifecycle:

1. The frozen plan must pin the exact
   `PACK_ROOT/arm_readiness.freeze.receipts/freeze-NNNN.json` path and digest.
   This pack-contained receipt is non-authorizing and cannot carry `GO`.
2. The frozen plan must declare, without populating, the deterministic
   external arm slot
   `ARM_READINESS_CUSTODY_ROOT/PACK_ID/arm_readiness.receipts/arm-<4+ digits>.json` and the
   committed-pack digest algorithm. It must not contain a future arm path or
   digest.
3. Only after the live steps below pass may the generator create the next
   external arm receipt. Only the exact, authenticated, unexpired,
   unsuperseded receipt with `receipt_kind: arm`, `status: PASS`, and
   `arm_disposition: GO` can satisfy the machine gate. A missing receipt,
   placeholder, stale HEAD or pack digest, bad sidecar, incomplete row set,
   refusal, predecessor with a semantic successor, or already-consumed
   capability is NO-GO.

The row authority is the JSON registry named in §4. The ALPHA, BETA, and
GAMMA Markdown matrices are checked human views and never substitute for a
receipt. A `PASS`, `GO`, `READY`, `clean`, or `ready` value is evidence toward
Ed's decision; no automated word performs or authorizes the physical launch.

**Reboot fence.** Version 1 binds both receipt schemas that carry
`valid_until_monotonic_ns`—the external arm receipt and the generic domain
evidence receipt—to the current Darwin boot. Here, `boot_session_id` means the
exact canonical UUID that the readiness commands derive from
`kern.bootsessionuuid` with `/usr/sbin/sysctl -n`; no API argument or
command-line option accepts it. If that value cannot be derived, the operation
fails closed with `readiness_io_error`.

At all three refusal points—the evidence item, the evidence receipt, and the
arm receipt—the machine checks the boot session during verification and
consumption. A mismatch refuses with `readiness_record_expired`, an existing
member of the closed 46-code vocabulary; no new refusal code was added. If the
Mac reboots between freeze and arm, the readiness commands automatically
refuse receipts from the earlier boot session with
`readiness_record_expired`. The operator will see that refusal and must
generate new receipts before readiness can proceed. This is expected, correct
machine behavior: the refusal is evidence that the reboot fence worked, not a
fault to work around. The lead confirmed both the raw `sysctl` read and the
shipped derivation outside a sandbox on the same boot.

**Magistrate-executed terminal-review attestation — required producer step.**
After all repair/freeze review is complete and before the dry run or T-0, the
operator works at the reviewed tree, computes each pack's committed pack-tree
digest, and creates one empty attestation commit carrying the review trailers.

**Owner (amended 2026-08-26 under D-155, NR-12).** The original text read
"This is not delegated and is not an Ed hardware step". The second half
stands: it is still not an Ed hardware step. The first half is amended.
D-150b (Ed, 2026-08-23) delegates the terminal review **by name** to the
magistrate, executed as a mechanical comparison with every digest
independently recomputed from the artifacts rather than accepted from the
producing session's report. So this step **is** delegated — to the
magistrate, and to no one else.

**Placement (amended 2026-08-26 under D-155, NR-12).** For a multi-pack
family under a commit freeze, this commit is the **last commit before
publication**: it is made at the mint tree, after the allowlist contract
closes at `PINSET_MINT_HEAD`, and the head it produces is
`ATTESTATION_HEAD`, which is the published head. `PINSET_MINT_HEAD` remains
the allowlist-contract closure head and the coordinate `hS` is computed
from. An empty commit changes no bytes, so it moves neither the tree nor
`hS`. The real-lane step-by-step sequence lives in
`docs/process_traces/2026-08-22-t20/real-transaction-runbook.md` Phase C11.

**One commit, one trailer line per pack.** The `_v4` family is three packs
that arm against a single frozen head, and each pack has its own committed
pack-tree digest. The producer therefore emits **three**
`JouleWise-Terminal-Review-Pack-Sha256` lines — one per pack, in
ALPHA/BETA/GAMMA order — alongside exactly one `PASS` line and exactly one
`Tree-Oid` line. A single-pack family emits one such line and the block
below is unchanged in shape.

```sh
cd /Users/edr/JouleWise-measurement-20260813
test -z "$(git status --porcelain=v1 --untracked-files=all)"
TREE_OID="$(git rev-parse HEAD^{tree})"
set -- -m 'JouleWise terminal review attestation' \
       -m 'JouleWise-Terminal-Review: PASS' \
       -m "JouleWise-Terminal-Review-Tree-Oid: $TREE_OID"
for PACK_ROOT in \
  configs/campaigns/d117_floor_qwen25_1p5b_v4 \
  configs/campaigns/d117_floor_qwen25_7b_v4 \
  configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4
do
  PACK_SHA256="$(.venv/bin/python3 - "$PACK_ROOT" <<'PY'
import sys
from joulewise.arm_readiness import committed_pack_tree_sha256
print(committed_pack_tree_sha256(sys.argv[1]))
PY
)"
  test -n "$PACK_SHA256" || { echo "empty pack digest for $PACK_ROOT" >&2; exit 1; }
  set -- "$@" -m "JouleWise-Terminal-Review-Pack-Sha256: $PACK_SHA256"
done
git commit --allow-empty --cleanup=verbatim "$@"
```

**AMENDED 2026-08-26 under D-155 (NR-11, NR-12, NR-10). The producer command
block above replaced a single-pack block; the superseded block is preserved
here so that nothing is silently rewritten:**

```sh
cd /Users/edr/JouleWise-measurement-20260813
. /Users/edr/JouleWise-window-custody/d117-alpha-YYYYMMDD/readiness/window-plan/window.env
test -z "$(git status --porcelain=v1 --untracked-files=all)"
TREE_OID="$(git rev-parse HEAD^{tree})"
PACK_SHA256="$(.venv/bin/python - "$PACK_ROOT" <<'PY'
import sys
from joulewise.arm_readiness import committed_pack_tree_sha256
print(committed_pack_tree_sha256(sys.argv[1]))
PY
)"
git commit --allow-empty --cleanup=verbatim \
  -m 'JouleWise terminal review attestation' \
  -m 'JouleWise-Terminal-Review: PASS' \
  -m "JouleWise-Terminal-Review-Tree-Oid: $TREE_OID" \
  -m "JouleWise-Terminal-Review-Pack-Sha256: $PACK_SHA256"
```

Three things changed and nothing else did: the single `$PACK_ROOT` sourced
from one campaign's `window.env` became an explicit loop over the family's
three pack roots emitting one `Pack-Sha256` line each; `.venv/bin/python`
became `.venv/bin/python3`; and a non-empty check on each computed digest was
added so a silent empty value cannot become a trailer. The commit shape —
`--allow-empty`, `--cleanup=verbatim`, one `PASS` line, one `Tree-Oid` line —
is unchanged.

Two details of that block are load-bearing rather than stylistic. The
interpreter is spelled `.venv/bin/python3`, not `.venv/bin/python`: they are
the same interpreter, but the harness permission rules match on the literal
string, so the two spellings prompt differently (D-155, NR-10). And the
window plan's `window.env` is no longer sourced for `$PACK_ROOT`: that file
names one campaign, and this commit must name every pack in the family, so
the pack roots are listed explicitly.

**This three-line form requires the NR-11 membership cure to be on the
reviewed head first.** Both trailer parsers — `_derive_terminal_review` in
`joulewise/arm_readiness_evidence_t0.py` and its twin `_verify_terminal_review`
in `scripts/capture_t0_step.py` — historically required *exactly one*
`Pack-Sha256` value, so a three-line message refuses at both. D-155 rules
`PASS` and `Tree-Oid` to stay exactly-once while `Pack-Sha256` becomes
**non-empty, duplicate-free, and containing the arming pack's digest**; that
change lands as D-155 work order W-2, before the evidence-derivation head. If
W-2 is not on the head being attested, do not emit three lines and do not
work around the refusal — stop, and read the D-151 condition-7 warning in the
real-transaction runbook's C11 step.

The operator then lands that exact commit as reviewed `main`; the
measurement checkout, local `main`, and `origin/main` must all name it. The
tree OID is unchanged by the empty commit. Every `capture_t0_step.py`
invocation verifies that HEAD carries exactly one `PASS` line, exactly one
`Tree-Oid` line matching the current tree, and this pack's digest among the
`Pack-Sha256` lines; the author's terminal-review check independently
repeats the same proof. A later tree change, or a pack whose digest is not
among those lines, requires a new reviewed attestation commit; trailers from
an ancestor do not transfer.

**Lead live verification — desk evidence, not live-night authority
(rule 1, non-delegable).**
On the exact reviewed commit, the lead personally runs the frozen plan's
literal readiness-validator command and its complete under-lease synthetic
rehearsal. The rehearsal must execute the real reservation CLI with
`--execute` and the production ledger-writer lifecycle through both reserved calibration
slots against a synthetic root. Require the resulting D-134 dry-run receipt
at
`ARM_READINESS_CUSTODY_ROOT/PACK_ID/arm_readiness.dry_run.receipts/dry-run-NNNN.json` to
have `status: PASS`, `arm_disposition: NOT_APPLICABLE`, and the same reviewed
HEAD and final committed-pack digest that the arm evaluation will bind.
Record the receipt path and SHA-256 as well as the complete commands, commit
hash, frozen-plan SHA-256, exit codes, stdout, and stderr in §12. Require
`calibration_pre_reserve_authorized`,
`status: reserved`, and the phase-correct
`calibration_writer_arm_authorized` events. Missing commands, a skipped
phase, a stale dry-run receipt, or any identity mismatch is NO-GO. A lead who
has not personally seen these pass on this checkout and pack has not
verified; a subagent's or a prior session's pass does not transfer. The dry
run exercises the production reservation/writer lifecycle but never enters
live MLX or `powermetrics` capture. These desk results are evidence toward
arming; they do not authorize the live night.

**Order of operations at the machine (each step gates the next):**

1. Complete §5 (machine and operator preflight) and Ed's §5A clock
   procedure. §5B is **not** a separate manual step before launch: the
   foreground chain performs it after the pre-slot enforcing gate and
   pre-calibration capture, and before member 1.
2. After all agents are closed, Ed executes the frozen E-step sequence with
   no reordering:

   Run these exact wrapper invocations from the reviewed measurement checkout.
   Each invocation derives its command from frozen `window.env`, brackets the
   subprocess with boot-bound monotonic timestamps, preserves complete stdout
   and stderr, and publishes one no-clobber canonical capture. Do not run the
   wrapped command separately.

   This is a production-interface and ceremony rule, not independent producer
   attestation. When faithfully invoked, the wrapper derives the commands,
   timestamps, identities, and digests; the author authenticates canonical
   bytes, same-boot freshness/order, and fresh current-state probes. Direct
   JSON authorship, modified library invocation, clock/execution substitution,
   or edits to `arm_readiness.t0.inputs` violate procedure but are not
   mechanically detectable in v1. T-0 capture provenance is
   **TRUSTED-OPERATOR**: deliberate operator fabrication is not defended
   against. The real binding to a real quiet window is Ed's human §5A tap, the
   terminal-review attestation, and the single-operator assumption. The
   terminal-review commit attests the reviewed tree and pack, not runtime
   capture provenance.

   ```sh
   WINDOW_PLAN_ROOT=/Users/edr/JouleWise-window-custody/d117-alpha-YYYYMMDD/readiness/window-plan
   . "$WINDOW_PLAN_ROOT/window.env"
   cd "$MEASUREMENT_REPO"
   ```

   - **E-4:** Ed first performs the prior-state read directly in the interactive
     shell (a password prompt is expected; no repository script performs this
     privileged read) and preserves its exact `Network Time: On` or
     `Network Time: Off` output:

     ```sh
     /usr/bin/sudo /usr/sbin/systemsetup -getusingnetworktime
     ```

     Then run the wrapper. At its prompts, enter the independent trusted-clock
     UTC literal and paste the exact prior-state output. The tool derives the
     system timestamp, monotonic observation, boot ID, attestation ID, context,
     and manifest, and records the manual action without executing a privileged
     read itself:

     ```sh
     python3 scripts/capture_t0_step.py clock-prior-state \
       --pack-root "$PACK_ROOT" \
       --custody-root "$ARM_READINESS_CUSTODY_ROOT" \
       --window-plan-root "$WINDOW_PLAN_ROOT"
     ```

   - **E-5:** use D-127's exact noninteractive `off` vector:

     ```sh
     python3 scripts/capture_t0_step.py clock-disable \
       --pack-root "$PACK_ROOT" \
       --custody-root "$ARM_READINESS_CUSTODY_ROOT" \
       --window-plan-root "$WINDOW_PLAN_ROOT"
     ```

   - **E-7a:** capture the reviewed quiet-prep literal:

     ```sh
     python3 scripts/capture_t0_step.py quiet-mac-prep \
       --pack-root "$PACK_ROOT" \
       --custody-root "$ARM_READINESS_CUSTODY_ROOT" \
       --window-plan-root "$WINDOW_PLAN_ROOT"
     ```

   - **E-7b:** capture the profile-derived `--wait --timeout-min 45` command.
     The script must prove at least 600 seconds of continuous clean dwell and
     end in `READY`:

     ```sh
     python3 scripts/capture_t0_step.py prewindow-check \
       --pack-root "$PACK_ROOT" \
       --custody-root "$ARM_READINESS_CUSTODY_ROOT" \
       --window-plan-root "$WINDOW_PLAN_ROOT"
     ```

   - **E-8:** capture diagnostic readiness. Require the returned JSON to bind
     the exact R2 absolute path, pack `plan_id`, and exact-byte SHA-256:

     ```sh
     python3 scripts/capture_t0_step.py ledger-readiness \
       --pack-root "$PACK_ROOT" \
       --custody-root "$ARM_READINESS_CUSTODY_ROOT" \
       --window-plan-root "$WINDOW_PLAN_ROOT"
     ```

   - **E-9a:** capture the full reservation superset. The tool always derives
     `--plan` from the same R2 reference used by E-8 and includes `--ledger`,
     `--head-pin`, every identity/root argument, and `--execute`:

     ```sh
     python3 scripts/capture_t0_step.py ledger-reservation \
       --pack-root "$PACK_ROOT" \
       --custody-root "$ARM_READINESS_CUSTODY_ROOT" \
       --window-plan-root "$WINDOW_PLAN_ROOT"
     ```

   Any nonzero command, invalid result identity, boot change, out-of-order
   call, or existing output path refuses. After E-9a, the private input
   namespace contains exactly the six captures plus `clock-attestation.json`,
   `arm-context.json`, and `launch-manifest.json`.

   The terminal handback record must state:

   > I personally performed §5A and invoked the unmodified production CLI for
   > E-4 through E-9a on the recorded boot; I did not create or edit any
   > `arm_readiness.t0.inputs` file or substitute clock/execution functions;
   > E-7b remained under wrapper control until READY; launch followed
   > successful E-9b authoring, E-9c ARM and verify, and my single E-10
   > invocation of the sole reviewed launcher, which consumed the arm
   > capability atomically — I ran no separate consume command.

   Bind that attestation to the operator identity, boot UUID, HEAD/tree/pack,
   all nine input hashes, and the arm/consumption receipts. This is the human
   record of the trusted-operator ceremony, not mechanically independent
   producer attestation.

   Do not look for a visible `ready_to_arm` field: the enforcing checks are
   internal to reservation and writer, and no diagnostic word (`clean`,
   `ready`) licenses anything. `needs_pin_commit: true` is desk work and ends
   the attempt; no override exists at night.

   - **E-9b:** immediately after E-9a, author the fifteen T-0 source/evidence
   pairs:

   ```sh
   python3 scripts/author_arm_evidence_t0.py \
     --pack-root "$PACK_ROOT" \
     --custody-root "$ARM_READINESS_CUSTODY_ROOT"
   ```

   Eleven volatile evidence kinds carry a **20-minute monotonic horizon**
   beginning at E-9b. That is the operator's visible clock: do not start any new
   agent, browser, `caffeinate`, monitor, maintenance, or other polling
   process after authoring. Run ARM immediately, verify it, stop for Ed's
   inspection, and then invoke E-10. The four procedural evidence kinds
   retain their separate six-hour horizon;
   they do not extend the volatile evidence.

   A reboot or any HEAD change voids the authored receipts. Before
   re-authoring, use the governed cleaner for the exact three pack-specific T-0
   namespaces so no no-clobber collision can masquerade as a retry. The command
   authenticates `PACK_ROOT` as the committed
   `configs/campaigns/$PACK_ID` pack, refuses a partial or anomalous namespace
   set, and refuses before cleanup if the pack's current `_vN` generation has a
   committed `freeze-NNNN.json`. There is no force mode:

   ```sh
   python3 scripts/reauthor_clean.py \
     --pack-root "$PACK_ROOT" \
     --namespace "$ARM_READINESS_CUSTODY_ROOT/$PACK_ID/arm_readiness.t0.sources" \
     --namespace "$ARM_READINESS_CUSTODY_ROOT/$PACK_ID/arm_readiness.evidence" \
     --namespace "$ARM_READINESS_CUSTODY_ROOT/$PACK_ID/arm_readiness.t0.inputs"
   ```

   Before the first namespace rename, the cleaner writes and fsyncs an immutable
   `state-<state_id>.manifest.json` below
   `$ARM_READINESS_CUSTODY_ROOT/$PACK_ID/reauthor-clean.operations/`. The state
   ID is derived from a 32-byte random nonce plus the authenticated pack,
   request paths, and custody/source inode anchors; wall-clock time is
   informational only. Progress authority is a no-clobber, fsynced, hash-linked
   sequence of individual event files, never mutable JSONL. Before any rename,
   a disposable descriptor sentinel must prove immutable-flag set, clear,
   post-unlink set, `st_flags` observation, and cleanup; there is no subprocess
   or path-based fallback.

   A successful clean prints the immutable terminal
   `state-<state_id>.receipt.json` path and SHA-256. Record both. The receipt
   binds the manifest, Git/plan/pack identity, exact request, frozen descriptor
   inventory, and every durable post-unlink verification event. The receipt
   claims **VERIFIED LOGICAL NAMESPACE DELETION**, never secure erase or
   hostile-process exclusion. The four pack mint-custody
   namespaces — `PACK_ROOT/arm_readiness.evidence`,
   `PACK_ROOT/arm_readiness.freeze.receipts`,
   `PACK_ROOT/arm_readiness.sources`, and
   `PACK_ROOT/identity_pin_projection.receipts` — are not cleanup targets and
   remain untouched; only the separately rooted T-0 `arm_readiness.evidence`
   path listed above is removed.

   A generation with its committed `freeze-NNNN.json` refuses cleanup because
   frozen bytes are immutable; the lawful route is to create and commit a new
   family generation, clean/re-author it before its freeze, and then freeze that
   successor.

   Cleanup atomically renames the three inode-anchored trees into
   `$ARM_READINESS_CUSTODY_ROOT/$PACK_ID/.reauthor_clean.quarantine/<state_id>/`,
   recursively sets `UF_IMMUTABLE` on every quarantined directory and regular
   file, and inventories the frozen tree through descriptors. It then deletes
   bottom-up with directory FDs and `O_NOFOLLOW`: each regular-file FD remains
   open across `unlink`, is re-frozen, hashed through that descriptor, and is
   closed only after its `DELETE_VERIFIED` event is durable. No `rmtree` is
   permitted.

   If interrupted before unlink, inspect the named state and repeat the same
   command with `--resume-removal`; resume revalidates the canonical manifest,
   current pack tree/unfrozen generation, custody/source/quarantine inode
   anchors, exact source/quarantine location, complete event chain, and every
   remaining frozen object. An intent whose object remains is safely re-frozen,
   rehashed, and retried. An intent whose object is missing permanently returns
   `reauthor_clean_destroyed_unverified` with an
   `INCOMPLETE_DESTROYED_UNVERIFIED` incident receipt and never deletes the
   remainder. A post-unlink hash difference similarly terminates as
   `INCOMPLETE_DESTROYED_MISMATCH`; neither incomplete state can be upgraded by
   retry. After all verified events, a missing terminal receipt is rebuilt
   deterministically; after its fsync, rerun returns `ALREADY_COMPLETE` with the
   same receipt hash. Legacy partial `rmtree` state is preserved as
   destroyed-unverified incident custody and is never resumed.

   Then repeat E-4 through E-9b; never reuse a pre-reboot or pre-HEAD-change
   receipt. **E-9c** is ARM followed by verify, and ARM must be the next new
   process after the author exits:

   ```sh
   python3 scripts/generate_arm_readiness.py arm \
     --pack-root "$PACK_ROOT" \
     --arm-context "$ARM_CONTEXT_JSON" \
     --window-custody-root "$ARM_READINESS_CUSTODY_ROOT"
   ```

   `ARM_CONTEXT_JSON` is the exact JSON object itself, not a path. Its keys are
   exactly `bracket_session_id`, `pre_attempt_id`, `post_attempt_id`,
   `clock_route`, `claim_runs_root`, `bound_runs_root`, `custody_root`,
   `quarantine_root`, `claim_backup_destination`,
   `bound_backup_destination`, and `waiver_path`; the generator derives row
   verdicts, applicability, identities, and digests. Bind `custody_root` to
   the fresh-empty `WINDOW_CUSTODY_ROOT` and `quarantine_root` to the distinct
   sibling `QUARANTINE_ROOT`; neither is the populated
   `ARM_READINESS_CUSTODY_ROOT`. Require the
   derived `arm-NNNN.json` plus sidecar to pass the implemented verifier:

   ```sh
   python3 scripts/generate_arm_readiness.py verify \
     --pack-root "$PACK_ROOT" \
     --arm-receipt "$ARM_RECEIPT"
   ```

   Require the exact unexpired, unsuperseded `PASS`/`GO` result. That result
   remains necessary evidence, never launch authority. Stop at this boundary
   so Ed can personally inspect the complete `PASS`/`GO` result. No verdict,
   author, verifier, or other automated command may cross this boundary.
3. **E-10 — Ed's deliberate physical launch:** after that inspection, Ed
   personally invokes the sole reviewed launcher exactly once.

   **Two values the command needs, built before they appear in it.** The freeze
   transaction that produced this pack family published a small JSON file named
   `d117_step6_confirmation_table_v4.json`. It records Ed's `YES` over that
   family, and in a section called `successor_pinset` it records the SHA-256 of
   one specific repository file — the successor-pinset file — as that file was
   committed at the reviewed head. Call the JSON file **the table**; the
   variable `$STEP6_CONFIRMATION_TABLE` below is its absolute path. Separately,
   the same transaction computed the SHA-256 **of the table's own bytes** and
   recorded it in transaction custody. That digest is written `hC` in the
   transaction record, and the variable `$ED_STEP6_CONFIRMED_SHA256` below
   holds it. Path and digest are two different things about the same file, and
   the launcher needs both.

   **Why both.** Before it consumes anything, the launcher re-derives the arm
   receipt's contents from the repository and compares them to what the receipt
   says — a replay, to prove the receipt still describes reality. That replay
   reaches a check which refuses to treat the successor-pinset file as reviewed
   unless Ed's table vouches for it. The check will not read a single field out
   of the table until it has hashed the table's bytes and found them equal to
   `hC`, so it needs the file to hash and the digest to compare against, and it
   refuses when it has one without the other.

   ```sh
   .venv/bin/python scripts/launch_window.py \
     --pack-root "$PACK_ROOT" \
     --arm-receipt "$ARM_RECEIPT" \
     --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
     --launch-manifest "$LAUNCH_MANIFEST" \
     --step6-confirmation-table "$STEP6_CONFIRMATION_TABLE" \
     --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
   ```

   **`hC` is carried here, never recomputed here.** Take
   `$ED_STEP6_CONFIRMED_SHA256` from the freeze transaction's custody record of
   Ed's step-6 confirmation — the `085-ed-step6-confirmed-sha256.txt`
   transcript, written at the moment that confirmation was executed. Do **not**
   produce it with `shasum -a 256 "$STEP6_CONFIRMATION_TABLE"`. That would hash
   the file under test to make the value the file under test is then checked
   against, so it would agree no matter what the file contained; the table's own
   contract calls that out and forbids it. The digest is worth something only
   because it reached this command from Ed's out-of-band confirmation rather
   than from the bytes it is meant to authenticate.

   **What omitting the path argument does.** `--step6-confirmation-table` is
   optional. Omitted, the launcher looks for the table at
   `$ARM_READINESS_CUSTODY_ROOT/family_publication/d117_step6_confirmation_table_v4.json`
   and proceeds if it finds it there — so omitting the flag is not itself a
   refusal, and only a missing digest, or a table that is neither supplied nor
   present at that default location, is. Pass the path anyway: it makes the
   exact file under test explicit in the command Ed is inspecting rather than
   implied by a default, and it is the only route when custody keeps the table
   somewhere else.

   This one invocation generates the anonymous-FD handoff, atomically creates
   and fsyncs the no-clobber consumption primary (the single-use
   linearization point), publishes its sidecar, replays
   `verify_consumed_launch`, and calls `execve` on the exact frozen foreground
   argv. It neither spawns and returns nor retries. The chain begins with the
   frozen 180-second settle; Ed steps away immediately after invoking E-10 and
   does not touch or monitor the machine. Standalone `consume`, direct
   `window-chain.zsh`, and direct stage invocations are not production routes.
   The retained `generate_arm_readiness.py consume` CLI now refuses with
   registered `readiness_usage_invalid` and points to
   `scripts/launch_window.py`; it is not a compatibility launch path.
   This supersedes the pre-D-117 §5A instruction to settle 180 seconds by
   hand before launching: the settle is inside the chain.
   **Current implementation boundary (2026-08-15 fix round):** the launcher
   enforces consume → revalidate → exact `execve`, and marker-bearing campaign
   collection enforces exact pack-config membership plus outer/inner lineage
   agreement. Calibration-slot writer enforcement is not implemented yet;
   neither the three frozen D-117 packs nor their current configs may be
   changed in place to add the marker. Calibration-side stage 2, downstream
   reduce/extract/mint stages 3–4, and the Phase-2 successor-family marker
   freeze remain required. Therefore this E-10 command is a documented target
   procedure, **not current authority to launch**: every D-117 physical launch
   remains NO-GO until those gates and the full review gauntlet close. The
   automatic §5B screen gates member 1 only after that launch-readiness state
   exists.
   "Exactly once" means once per frozen bracket-session attempt; a
   prospectively licensed new attempt (below) is a new frozen session,
   never a relaunch of the same one. If consumption succeeds but the physical
   launch does not start, do not reuse the consumed capability.
4. **If anything refuses:** any refusal stops forward progress
   immediately. Preserve the exact stdout, stderr, and durable evidence.
   For a registered ledger refusal, follow only its §10 row; continue
   only when that route returns `operation_completed` and the documented
   phase is repeated from its entry point. `night_stopped_preserved`,
   `needs_pin_commit: true`, an unmapped failure, or failed preservation
   ends the night. A §5B level failure ends the current attempt; only a
   pre-registered retry after a named cause has been removed may begin a
   newly frozen session. Any failure after the no-clobber consumption primary
   burns the attempt permanently, including sidecar publication, replay, or
   `execve` failure. For non-ledger failures, send the lead the
   exact observed condition and complete output (plus the operator ABORT
   alias if using the packet's reporting table). A refused night is
   evidence, not an obstacle course.

**Limitation carried into this procedure (cold-gate L1, surfaced to Ed).**
The calibration-ledger witness corpus certifies the recovery code against
production regression and witness drift; it does not certify against a
future adversarial rewrite of the tests themselves. That residual class
is carried by review discipline — and it is one of the reasons the entry
gate and lead verification above are human gates: the corpus feeds the
desk verdict, it never replaces it.

## 6. The foreground measurement chain

`window-chain.zsh` is private to `scripts/launch_window.py`. It is never an
operator entrypoint. Its first executable action authenticates the inherited
anonymous-FD handoff against the v2 consumption receipt and atomically emits
the immutable start receipt before any settle, directory mutation, or
collection. The implemented campaign gate applies only when a config already
carries the exact `launch_lineage_required` run-metadata tag. No current
frozen D-117 config carries that marker. Adding it is a Phase-2 successor-pack
freeze transaction, never an in-place repair of frozen bytes; calibration-side
stage 2 and downstream stages 3–4 also remain open. Until they land and pass
review, the private chain is not launch-ready and E-10 remains NO-GO.

### D-117 §6 amendment — durable bracket dispatch and slot resume

The frozen plan, ledger capability, and exact custody locators are the only
dispatch authority. Shell-local directory discovery and a lexicographically
"latest" calibration are prohibited. On supervisor restart, run
`session-status`; dispatch only its exact `next_slot`/`attempt_id`. Complete
custody uses `resume-finalize`; partial custody uses `abort-session`. Both
commands run in a fresh process and preserve the custody directory.

Before quiet time, authenticate R2's `FROZEN_PLAN` tuple: pack ID,
`calibration_plan.json` as the canonical pack-root-relative path, the plan's
exact `plan_id`, and SHA-256 of its exact committed bytes. Record that tuple
together with `window.env`, the exact identity-epoch JSON, and the exact
T1-bindings JSON. Never create or select a second custody reservation JSON.
The six §5C wrapper calls are the sole live execution route; the E-8 and E-9
calls render these exact commands from the one authoritative reference:

```sh
. "$WINDOW_PLAN_ROOT/window.env"
REPO=/Users/edr/JouleWise-measurement-20260813
cd "$REPO"

.venv/bin/python scripts/recover_calibration_ledger.py readiness \
  --phase pre-reserve \
  --session-id "$BRACKET_SESSION_ID" \
  --plan "$FROZEN_PLAN"

.venv/bin/python scripts/reserve_calibration_window_bracket.py \
  --ledger "$CALIBRATION_LEDGER" \
  --head-pin "$LEDGER_HEAD_PIN" \
  --session-id "$BRACKET_SESSION_ID" \
  --window-id "$WINDOW_ID" \
  --plan-id "$PLAN_ID" \
  --plan-sha256 "2afabe9854a8ac8c9d3d212bb0236fa787d660cf5ef452c66f2d84f97d4f227d" \
  --plan "$FROZEN_PLAN" \
  --evidence-root-id "$EVIDENCE_ROOT_ID" \
  --runs-root "$RUNS_ROOT" \
  --pre-attempt-id "$PRE_ATTEMPT_ID" \
  --post-attempt-id "$POST_ATTEMPT_ID" \
  --pre-custody-locator "$RUNS_ROOT/instrument_validation/$PRE_ATTEMPT_ID" \
  --post-custody-locator "$RUNS_ROOT/instrument_validation/$POST_ATTEMPT_ID" \
  --identity-epoch-json "$IDENTITY_EPOCH_JSON" \
  --t1-bindings-json "$T1_BINDINGS_JSON" \
  --execute
```

The displayed digest is the current ALPHA example, not an operator-entered
input: `capture_t0_step.py` derives it from committed bytes and constructs the
argv. A successor pack uses its derived digest. Require readiness output to
echo the same absolute path, `plan_id`, and SHA-256, and require the
reservation output to say `status: reserved`. On restart, do not reserve
again from remembered shell state: run `session-status` with the exact
session and frozen plan and dispatch only its durable `next_slot`.
The reservation argv is deliberately the superset: `--ledger` and
`--head-pin` select the authenticated production ledger state, while
`--plan` supplies the exact frozen reservation bytes. Omitting any one of the
three is a launch-procedure error.

Save the following as `WINDOW_PLAN_ROOT/window-chain.zsh`, review it, and
record its SHA-256 before closing all agents. `window.env` must additionally
bind the absolute `ARM_RECEIPT`, `ARM_READINESS_CUSTODY_ROOT`, and
`LAUNCH_MANIFEST` paths used by E-10:

> **OPEN DEFECT — the chain has no supply line for three of its own inputs
> (registered 2026-08-27; NEEDS A MAGISTRATE RULING; do not launch a `_v4`
> window on this chain until it is ruled).** Two separate problems meet here,
> and both are about getting a value into a chain that runs after Ed has walked
> away.
>
> *First, the two that predate this note.* The paragraph immediately above tells
> the operator to bind `ARM_RECEIPT` and `LAUNCH_MANIFEST` in `window.env`, and
> the chain below dereferences both under `set -u`. But `window.env` is read by
> `scripts/capture_t0_step.py`, whose `_parse_window_environment` compares the
> file's keys against an exact 25-key allowlist, `_ENV_KEYS`, and refuses with
> `evidence_author_t0_capture_environment_invalid` on any key that is missing
> *or* unknown. `ARM_RECEIPT` and `LAUNCH_MANIFEST` are not in that allowlist.
> So binding them makes T-0 refuse, and not binding them makes the chain abort
> on an unbound variable at its first launcher call. There is no third option
> today.
>
> *Second, the confirmation pair.* The chain's `--lifecycle-event start` call
> below replays the consumption, so it crosses the same table check E-10
> crosses and refuses without the table and `hC`. It cannot inherit them from
> E-10: E-10 replaced itself with this chain by calling `execve`, which carries
> open file descriptors across but not the argument vector, so the chain's
> launcher call has to state the pair in its own argv. `window.env` cannot
> carry them either, for the exact-allowlist reason above. And no operator is
> present to type them — the chain begins after Ed steps away, which is the
> whole point of the frozen chain.
>
> The pair is therefore **deliberately absent from the `start` command below**:
> writing the flags in against undefined variables would only move the abort
> from the gate to `set -u`. Naming a supply line is a design decision with a
> recorded history — `docs/process_traces/2026-08-24-d153-sweep/01-opus-contract-lens-seat.md`
> "Cure for 3a-3d" holds that `hC` is operator-pasted per use and never stored
> in an environment file, and `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md`
> §2 Phase E4 keeps `hC` in transaction custody only — so it belongs to the
> magistrate, not to this document. E-10 above is unaffected: Ed types that
> command himself and can supply both values.

```zsh
#!/bin/zsh
set -euo pipefail

WINDOW_PLAN_ROOT="$1"
source "$WINDOW_PLAN_ROOT/window.env"

REPO=/Users/edr/JouleWise-measurement-20260813
PY="$REPO/.venv/bin/python"

# First executable action: consume the inherited one-use FD and mint start
# custody. Direct shell invocation has no FD 198 and refuses
# launch_handoff_invalid before settle or collection.
#
# INCOMPLETE, BY DECISION: this call replays the consumption, so it also needs
# --step6-confirmation-table and --expected-confirmation-digest and will refuse
# without them. It cannot inherit them from E-10 (execve does not carry argv),
# window.env cannot hold them (exact-key allowlist), and no operator is here to
# type them. See the OPEN DEFECT note above this chain; the supply line is a
# magistrate ruling, not something to improvise at the bench.
"$PY" "$REPO/scripts/launch_window.py" \
  --pack-root "$PACK_ROOT" \
  --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST" \
  --lifecycle-event start

POLICY="$REPO/configs/campaign_policies/quiet_mac_p2_production.json"
REF_ROOT="$REPO/configs/campaigns/window_references"
BOUND_CONFIG_ROOT="$REPO/configs/campaigns/neg8_reference_corpus"
BOUND_MANIFEST="$BOUND_CONFIG_ROOT/derivation/settled_corpus.json"
CLAIM_LOG="$RUNS_ROOT/campaign_log.jsonl"
BOUND_LOG="$BOUND_RUNS_ROOT/campaign_log.jsonl"
NEG8_DRIFT_BOUND="$BOUND_RUNS_ROOT/neg8-drift-bound.json"
OPERATOR_LOG_ROOT="$WINDOW_CUSTODY_ROOT/operator_logs"

mkdir -p \
  "$RUNS_ROOT/instrument_validation" \
  "$BOUND_RUNS_ROOT" \
  "$WINDOW_CUSTODY_ROOT" \
  "$OPERATOR_LOG_ROOT" \
  "$QUARANTINE_ROOT"

timestamp() {
  TZ=UTC date '+%Y-%m-%dT%H:%M:%SZ'
}

settle() {
  /bin/sleep "$SETTLE_S"
}

quarantine_stale_lock() {
  local root="$1"
  local lock="$root/campaign.lock"
  [ ! -e "$lock" ] && return 0

  local pid
  pid="$(/usr/bin/sed -n 's/^pid=\([0-9][0-9]*\).*/\1/p' "$lock")"
  if [ -z "$pid" ]; then
    echo "Unreadable campaign lock: $lock" >&2
    return 1
  fi
  if /bin/kill -0 "$pid" 2>/dev/null; then
    echo "Live campaign PID $pid owns $lock" >&2
    return 1
  fi

  /bin/mv "$lock" \
    "$QUARANTINE_ROOT/$(basename "$root").campaign.lock.$(TZ=UTC date '+%Y%m%dT%H%M%SZ')"
}

calibrate_slot() {
  local slot="$1"
  local attempt_id="$2"
  "$PY" "$REPO/scripts/validate_powermetrics_fiducial.py" \
    --allow-live \
    --arm-countdown-s 20 \
    --sleep-display-before-capture \
    --output-root "$RUNS_ROOT/instrument_validation" \
    --ledger "$CALIBRATION_LEDGER" \
    --head-pin "$LEDGER_HEAD_PIN" \
    --session-id "$BRACKET_SESSION_ID" \
    --slot "$slot" \
    --attempt-id "$attempt_id" \
    --power-policy "$POWER_POLICY" \
    >> "$OPERATOR_LOG_ROOT/${slot}-calibration.log" 2>&1
  "$PY" "$REPO/scripts/recover_calibration_ledger.py" session-status \
    --session-id "$BRACKET_SESSION_ID" \
    --plan "$FROZEN_PLAN" |
    /usr/bin/jq -er --arg slot "$slot" '.slots[$slot].custody_locator'
}

# D-079 clause 3: pre-flight calibration screen. Refuses an out-of-family
# pre-calibration before any member is collected. Derived from the issued
# acceptance artifact d079_calibration_acceptance_v2_n17_r3 (sha 73f02263...).
# If a successor acceptance issues before arm, regenerate and re-hash this
# chain with it (freeze-plan Q4); bindings and derivation are in §5B.
PRE_CAL_FIDUCIAL_MAX_S=0.032898493715362

screen_pre_calibration() {
  local dir="$1"
  local b

  b="$(/usr/bin/jq -r '.b_fiducial_s // empty' \
    "$dir/instrument_evidence.json")"
  if [ -z "$b" ]; then
    echo "pre-calibration has no fiducial bound: $dir" >&2
    return 1
  fi
  echo "$(timestamp) pre_calibration_fiducial_s=$b" \
    >> "$OPERATOR_LOG_ROOT/window-chain.log"
  if (( b > PRE_CAL_FIDUCIAL_MAX_S )); then
    echo "pre-calibration fiducial $b exceeds D-079 screen $PRE_CAL_FIDUCIAL_MAX_S" >&2
    echo "$(timestamp) pre_calibration_screen=failed" \
      >> "$OPERATOR_LOG_ROOT/window-chain.log"
    return 1
  fi
  echo "$(timestamp) pre_calibration_screen=passed" \
    >> "$OPERATOR_LOG_ROOT/window-chain.log"
}

run_stage() {
  local root="$1"
  local log="$2"
  local config_dir="$3"
  local calibration_dir="$4"
  local label="$5"

  settle
  quarantine_stale_lock "$root"
  echo "$(timestamp) stage_start=$label" >> "$OPERATOR_LOG_ROOT/window-chain.log"

  "$PY" "$REPO/scripts/run_campaign.py" "$config_dir" \
    --runs-dir "$root" \
    --log "$log" \
    --campaign-policy "$POLICY" \
    --instrument-calibration-dir "$calibration_dir" \
    --instrument-power-policy "$POWER_POLICY" \
    --arm-quiet-mode \
    --arm-countdown-s 20 \
    --max-failures 1

  echo "$(timestamp) stage_end=$label" >> "$OPERATOR_LOG_ROOT/window-chain.log"
}

run_stage_list() {
  local list="$1"
  local stage
  while IFS= read -r stage; do
    [ -z "$stage" ] && continue
    [[ "$stage" = \#* ]] && continue
    run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REPO/$stage" "$PRE_CAL_CUSTODY" "$stage"
  done < "$list"
}

cd "$REPO"
echo "$(timestamp) chain_start" >> "$OPERATOR_LOG_ROOT/window-chain.log"

# Final settle is chain-owned (D-117 §5C): operator activity ends at launch,
# and §1's post-activity settle happens here, before the pre-calibration.
settle
# No confirmation pair here, and none at completion below, even once the open
# defect above is ruled: only the start event replays the consumption, so
# settle and completion never reach the table check. Their omission is
# deliberate.
"$PY" "$REPO/scripts/launch_window.py" \
  --pack-root "$PACK_ROOT" \
  --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST" \
  --lifecycle-event settle
# Settle publishes BOTH fixed locators, each with its GNU SHA-256 sidecar:
#   $RUNS_ROOT/.joulewise-launch-lineage.json
#   $BOUND_RUNS_ROOT/.joulewise-launch-lineage.json
# Publication is canonical, no-clobber, file-fsynced, and directory-fsynced.
# Any primary/sidecar/root failure burns this attempt and set -e stops here,
# before pre-calibration or collection; never repair a partial publication.
echo "$(timestamp) launch_settle_complete" >> "$OPERATOR_LOG_ROOT/window-chain.log"

PRE_CAL_CUSTODY="$(calibrate_slot pre "$PRE_ATTEMPT_ID")"
echo "$(timestamp) pre_calibration=$PRE_CAL_CUSTODY" >> "$OPERATOR_LOG_ROOT/window-chain.log"

# Abort before member 1 if the pre-calibration is out of family (§5B).
screen_pre_calibration "$PRE_CAL_CUSTODY"

# The reference corpus and bound are minted inside this same quiet window.
run_stage "$BOUND_RUNS_ROOT" "$BOUND_LOG" "$BOUND_CONFIG_ROOT" "$PRE_CAL_CUSTODY" \
  neg8-bound-corpus

"$PY" "$REPO/scripts/run_campaign.py" \
  --derive-neg8-drift-bound "$BOUND_MANIFEST" \
  --neg8-drift-bound-output "$NEG8_DRIFT_BOUND" \
  --runs-dir "$BOUND_RUNS_ROOT" \
  >> "$OPERATOR_LOG_ROOT/bound-mint.log" 2>&1
echo "$(timestamp) neg8_bound=$NEG8_DRIFT_BOUND" >> "$OPERATOR_LOG_ROOT/window-chain.log"

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/start_triplet" "$PRE_CAL_CUSTODY" \
  start-reference-triplet

run_stage_list "$WINDOW_PLAN_ROOT/before_midpoint_stages.txt"

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/midpoint" "$PRE_CAL_CUSTODY" \
  midpoint-reference

run_stage_list "$WINDOW_PLAN_ROOT/after_midpoint_stages.txt"

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/end_triplet" "$PRE_CAL_CUSTODY" \
  end-reference-triplet

POST_CAL_CUSTODY="$(calibrate_slot post "$POST_ATTEMPT_ID")"
echo "$(timestamp) post_calibration=$POST_CAL_CUSTODY" >> "$OPERATOR_LOG_ROOT/window-chain.log"
"$PY" "$REPO/scripts/launch_window.py" \
  --pack-root "$PACK_ROOT" \
  --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST" \
  --lifecycle-event completion
echo "$(timestamp) measurement_complete" >> "$OPERATOR_LOG_ROOT/window-chain.log"
```

E-10's launcher `execve`s the manifest's exact
`/usr/bin/caffeinate -is /bin/zsh …/window-chain.zsh …` argv. That
`caffeinate` is the one reviewed keep-awake process for the window. The T-0
census in §5 is taken before E-10 and must find no `caffeinate` at all; after
E-10, exactly one exists and it is the chain's parent. Do not invoke that argv
directly or start a second one for any reason.

Every marker-bearing campaign invocation derives the constant locator from
its resolved `--runs-dir`. The outer campaign preflight authenticates both
root locators, the consumption→arm→start→settle chain, the current collection
boot and reviewed HEAD, the frozen recipe and exact argv, the authenticated
pack config membership, the selected arm-context root, and completion
absence before taking the campaign lock or creating provenance. The inner
bundle writer independently authenticates the exact CLI-selected config bytes
as a member of the frozen inventory before creating each bundle. It stamps the
full authenticated object at `metadata.json` → `extra` → `launch_lineage` and
the selected locator's authenticated content digest at
`launch_lineage_locator_sha256`. After each child returns, the outer campaign
reopens that metadata and requires canonical lineage-byte and locator-digest
equality with its retained preflight result; disagreement is terminal
`launch_lineage_conflict`, with the bundle preserved. No receipt path, lineage
JSON, or token is transported in argv or environment. Writer authentication
proves that consumption occurred within the arm horizon; it does not reapply
that short T-0 horizon during a multi-hour window. This paragraph describes
the implemented marker-bearing campaign gate only, not the still-deferred
calibration or downstream gates and not present launch authority.

Expected visible behavior: each stage pauses for the 180-second settle, prints
a 20-second arming countdown, sleeps the display, re-probes the governed
environment, and then begins members. The two calibrations use their own
20-second transient display arm. Do not wake the display to check progress.

## 7. Display and screen governance

The production policy requires AC power, an externally connected source,
low-power mode off, all online displays asleep, the screensaver disengaged,
and Nominal thermal pressure.

`--arm-quiet-mode` is intentionally repeated for every campaign invocation.
It is not redundant: every invocation gets a new enforcing preflight after
the previous stage's process churn. The controller also records governed
environment evidence and observes the display after capture. If the display
wakes or the screensaver engages, the correct outcome is refusal or loss of
the affected member.

Do not work around an environment failure with `--environment-override`.
That option records an override and makes every resulting member universally
claim-ineligible.

## 8. Check the fresh bound and calibration bracket

After `measurement_complete`, wake the display once.

- [ ] Confirm the pre and post artifacts are valid protocol v3.
- [ ] Confirm pre is at or before the first claim member and post is at or
  after the last.
- [ ] Confirm both are under
  `RUNS_ROOT/instrument_validation/`.
- [ ] Confirm both are within 24 hours and share the same power-policy and
  instrument bindings.
- [ ] Confirm bracket-bound drift against the **derived** screen of
  `0.009724 s` (9.723589289 ms), not the old underived `0.010 s`
  constant (D-079 clause 1). Drift within the screen passes clean.
- [ ] If drift is slightly above the screen, the window is **not**
  discarded: the FULL allowance `max(|B_pre − B_post|, 0.009724 s)` — not
  merely the excess above the screen — is added once to the larger endpoint
  bound and carried into every floor and claim the window produces, so the
  floor publishes wider. Drift above `0.012093166090593858 s` refuses the
  window outright.
  Do not compute or apply that allowance by hand — the governed verdict and
  extraction own it, exactly as they own the NEG-8 drift allowances.
- [ ] Confirm the excess being budgeted is ordinary repeatability scatter and
  **not** a known systematic defect (D-079 clause 2). A budget may never
  absorb a measurement already known to be wrong for an identified reason;
  that would launder the defect into a respectable-looking interval. In
  particular, a pre-calibration that failed the §5B level screen is never
  budgetable, and its window is not claim-bearing — window B (2026-07-26,
  drift 11.581436 ms on a 35.435841 ms pre-calibration) is the standing
  example, and `instrument_calibration_mismatch` is the correct verdict for
  it.
- [ ] Confirm the bound artifact was minted during this window from all 12
  members in `BOUND_RUNS_ROOT`.
- [ ] Confirm the bound freshness block says `max_age_s: 86400` and matches
  the claim members' OS build, supply identity, and calibration identity.

Do not hand-calculate or patch a family bound or allowance. The governed
verdict computes both family screens and both allowances.

## 9. Emit exactly one whole-window verdict

Run the verdict only after the post calibration and fresh bound are ready:

```sh
.venv/bin/python scripts/run_campaign.py \
  --whole-window-verdict \
  --runs-dir "$RUNS_ROOT" \
  --log "$RUNS_ROOT/campaign_log.jsonl" \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
  --neg8-drift-bound "$BOUND_RUNS_ROOT/neg8-drift-bound.json"
```

Add `--waivers "$WINDOW_PLAN_ROOT/waivers.json"` only when the frozen basis
contains a waiver that the current contract permits. A waiver makes the
whole-window verdict `flagged`; claim-bearing extraction requires `passed`.

- [ ] Require `status: passed`.
- [ ] Record `evaluation_basis.sha256`, the exact member-occurrence set, the
  calibration bracket, and policy SHA-256.
- [ ] Require both `gross_energy` and `idle_subtracted_energy` screens to
  pass.
- [ ] Require both authenticated entries under `drift_allowances`.
- [ ] Confirm every member's CPU admission is `admitted`.
- [ ] Confirm adapter wattage continuity is `stable`.
- [ ] Treat the gross corner statistic as diagnostic, not gating.
- [ ] Do not append a semantically different verdict for the same basis.

A passing screen is not a declaration of zero drift. The allowance is the
budget carried into every matching floor or claim envelope.

### D-100 §9 amendment — explicit salvage-dangler verdict dispatch

The ordinary command above never consumes a terminally absent member and
never selects a salvage row. A D-100 re-evaluation is a separate, licensed
operation performed only after an audited `joulewise.salvage_closure.v1` and
an exhaustive `joulewise.whole_window_membership_binding.v1` have been
lead-verified. It appends one new row; it does not edit a failed row:

```sh
.venv/bin/python scripts/run_campaign.py \
  --whole-window-verdict \
  --runs-dir "$RUNS_ROOT" \
  --log "$RUNS_ROOT/campaign_log.jsonl" \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
  --neg8-drift-bound "$BOUND_RUNS_ROOT/neg8-drift-bound.json" \
  --consumption-semantics-id salvage_dangler_exclusion_v1 \
  --window-membership-binding "$WINDOW_PLAN_ROOT/window-membership-binding.json" \
  --salvage-closure "$WINDOW_CUSTODY_ROOT/salvage-closure.json"
```

The new basis consumes every surviving member under authenticated
max-bracket re-derivation plus exactly one D-100 exclusion. Every downstream
consumer must name both `salvage_dangler_exclusion_v1` and that row's exact
64-hex `evaluation_basis.sha256`. `--waivers` is forbidden in this mode.
Creating the artifacts or running this command does not itself license a
historical window; that remains a separate lead-controlled step.

## 10. Failure playbook

### D-117 §10 amendment — calibration-ledger refusals and governed exits

Use the emitted refusal `code`, never prose recognition. For any
operator-emitted code, the registry route is available as structured JSON:

```sh
.venv/bin/python scripts/recover_calibration_ledger.py explain "$REFUSAL_CODE"
```

Registry rows classified `internal_invariant` are deliberately absent from
this operator table: public workflows supply those arguments from authenticated
durable state, so the corresponding guards have focused unit evidence rather
than an operator command.

| Registered code / exit | Required command and terminal result |
|---|---|
| `calibration_ledger_recovery_required` / `repair` | Run `repair`; require `operation_completed` or another registered code. |
| `calibration_tail_requires_abandon` / `abandon-tail-then-repair` | Run `abandon-tail --operator-identity "$OPERATOR_ID" --attestation-reason "$ATTESTATION_REASON"`, then `repair`; require `operation_completed`. If this advanced the physical head, follow the desk-only pin row before readiness can become `ready_to_arm`. |
| `calibration_intent_target_malformed` / `abandon-tail-then-repair` | Treat the admitted malformed intent and any target bytes as quarantine-only residue. Run the same operator-attested `abandon-tail`, then `repair`; require `operation_completed`. Never execute, replay, admit, or finalize the malformed target. |
| `calibration_custody_complete_use_resume` / `resume-finalize` | Run `resume-finalize --session-id "$BRACKET_SESSION_ID" --slot "$SLOT" --plan "$FROZEN_PLAN"`; require `operation_completed`. |
| `calibration_custody_partial` / `abort-session` | Run `abort-session --session-id "$BRACKET_SESSION_ID" --plan "$FROZEN_PLAN" --reason "$ABORT_REASON"`; require `session_aborted` and `custody_preserved: true`. |
| `calibration_live_writer_contention` | Wait for or intentionally stop the live holder. Never run `abort-session` underneath it. After a crash, the kernel releases the lease; rerun `session-status`, then its exact `resume-finalize` or `abort-session` route. |
| `calibration_ledger_head_mismatch` with `needs_pin_commit: true` / guarded advancement | End the 2 a.m. attempt. At the desk, review the candidate, run `advance-head-pin` with its exact sequence/digest plus operator attestation and `--execute`, commit the pin, require a clean checkout, and repeat readiness. |
| malformed ledger, unsafe lock inode, unreadable/archive-conflicting legacy journal, unreadable custody, divergent pin, or nonconvergent recovery | `night_stopped_preserved`: stop, preserve all ledger/lock/journal/custody/pin bytes, and escalate. Hash before and after the mapped exit; require byte identity and the same lock inode. Never delete a lock inode or integrity evidence. |
| torn `manifest.json` after a writer crash | `session-status` must report unreadable custody, never complete or resumable. A fresh `resume-finalize` attempt must emit the registered `calibration_custody_unreadable` hard stop with `night_stopped_preserved`; verify ledger, pin, lock inode, and all custody bytes are unchanged. |

`inspect` is diagnostic only. So are `audit`, `audit-observations`, and
`validate-slot`; none is an ARM-permission route. A `clean` parser state with
a non-null `legacy_journal_path` is blocked. No night command accepts an
uncommitted-pin override.

Fresh-process recovery examples:

```sh
.venv/bin/python scripts/recover_calibration_ledger.py session-status \
  --session-id "$BRACKET_SESSION_ID" --plan "$FROZEN_PLAN"
.venv/bin/python scripts/recover_calibration_ledger.py resume-finalize \
  --session-id "$BRACKET_SESSION_ID" --slot "$SLOT" --plan "$FROZEN_PLAN"
.venv/bin/python scripts/recover_calibration_ledger.py abort-session \
  --session-id "$BRACKET_SESSION_ID" --plan "$FROZEN_PLAN" \
  --reason "$ABORT_REASON"
```

| Symptom or refusal | Meaning | Required action |
|---|---|---|
| Display awake, screensaver engaged, `environment_admission_failed`, or CPU admission failure | The measurement environment was contaminated or unknown. | Lose the affected member. Stop the stage, remove the cause, settle 180 seconds, and rerun into a clean slot. Never waive admission. |
| `clock_anchor_unresolved` on calibration | The calibration capture could not be causally anchored. | Preserve it, settle, and retry once into a new validation directory. Abort after the second failure or any different calibration reason. |
| `pulse_calibration_rollover_gate_timeout` | Native powermetrics time did not advance before the pulse train. | Abort calibration and preserve the evidence. Repair machine state outside the window. |
| Pre-calibration fiducial above `0.032898493715362` (chain aborts before member 1) | The pre-calibration is out of family — typically a GPU clock/voltage ramp aliased into the fitted pulse start (D-079 clause 3). | Do not collect. Retry only after naming and removing a specific cause, within the pre-registered retry count, recording both attempts as evidence (§5B). With no identifiable cause, end the window. Never re-run merely to obtain a passing number. |
| Bracket drift above `0.009724 s` (D-079 derived screen) | Either ordinary repeatability scatter slightly over the screen, or an out-of-family systematic. | If the pre-calibration passed the §5B level screen, the window survives: the excess is carried by the governed extraction as an added uncertainty term and floors publish wider. If the §5B level screen failed, the excess is not budgetable and the window is not claim-bearing (D-079 clause 2). Never hand-apply an allowance. |
| `instrument_calibration_bracket_missing` | The claim members lack a valid causal pre/post calibration pair. | Mark the window non-claim-bearing. Never borrow a calibration from another power or machine state. |
| `calibration_bracket_exceeds_minted_bound` | The post calibration's bound is larger than one or more member envelopes minted under the pre calibration. | Do not patch metadata. Re-reduce only through a governed prospective path; otherwise recollect. |
| `neg8_drift_bound_underived` or `neg8_idle_sub_drift_bound_underived` | One family has no authenticated derived bound. | Collect the complete settled-reference corpus and mint the dual-family artifact. Never insert a constant or borrow the other family. |
| `neg8_drift_bound_stale` | The 24-hour horizon expired, a bound identity changed, or current bindings are missing/conflicting. | Mint a new corpus and bound inside the quiet window that will use it. |
| `neg8_bracket_abs_delta_exceeded` or `neg8_bracket_idle_sub_abs_delta_exceeded` | The gross or idle-subtracted point-drift screen failed. | Reject this claim basis. Preserve it and collect a shorter or better-controlled new window. |
| `anchor_fallback_member_unusable` in a floor cell | A floor member used unresolved or fallback clock anchoring. | This is an unwaivable rerun trigger. Preserve the fragment, quarantine the occupied slot, rerun the exact member, and record supersession. |
| `bundle_strict_invalid` from telemetry identity | The custody-bound config, metadata adapter, and summary telemetry source disagree by backend class. | Stop. Do not choose the convenient label. Repair custody or recollect the bundle. |
| `mock_telemetry_claim_ineligible` | A custody-bound config identifies mock telemetry. | Terminally refuse the member for claims. Mock data is development evidence and has no claim waiver. |
| `whole_window_drift_allowance_unrecorded` | A passing basis lacks an authenticated family allowance, or a claim omitted its named allowance term. | Refuse the affected floor/claim. Never substitute zero; rerun the governed verdict/extraction path or recollect if provenance cannot be restored. |
| `whole_window_campaign_membership_unresolved` | Campaign-log provenance is missing, ambiguous, duplicated, or unbound. | Repair custody or recollect. Do not replace manifest evidence with a directory scan. |
| `whole_window_verdict_conflict` | Different stored verdict rows purport to govern one basis, or verdict history is malformed. | Stop. Latest-wins is forbidden; preserve the conflict and mint a genuinely new basis if needed. |
| `launch_consumption_missing` | A marker-bearing claim input lacks its required v2 consumption reference, primary, or sidecar. | Refuse the stage. Preserve any bytes only as diagnostic evidence; issue a newly frozen bracket session and ARM receipt. Never reconstruct or attach a receipt after collection. |
| `launch_consumption_invalid` | Consumption or lifecycle custody is noncanonical, schema-invalid, has a bad sidecar/digest, or has an invalid predecessor chain. | Stop and preserve the entire namespace. The attempt is burned; no repair-in-place or retry exists. |
| `launch_binding_mismatch` | Valid receipts disagree on pack, plan, HEAD, arm context, collection boot, session, roots, launch-recipe bytes, or argv. | Refuse the claim basis and preserve the mismatch. Recovery is a new frozen session and capability, never a relabel. |
| `launch_lineage_conflict` | Members or artifacts name more than one consumption/pack/boot lineage. | Refuse the aggregate. Never choose latest or majority lineage; recollect one coherent window. |
| `launch_lifecycle_incomplete` | Start or settle is absent, or completion is absent at verdict/extraction/mint. | Treat the attempt as burned and non-claim-bearing. Preserve partial receipts and any collected bytes as diagnostics only. |
| `launch_handoff_invalid` | Chain entry lacks FD 198, the one-use token hash disagrees, or the handoff/start is replayed. | Refuse before settle or collection. Do not pass a token by argv, environment, or file and do not retry the consumed attempt. |
| `incomplete_existing` or an occupied run ID | A failed or interrupted bundle already owns the path. | Strict-validate and preserve it, move it outside the runs root, rerun the exact config, then record supersession. |
| `another campaign appears to be running` | A live process or stale `campaign.lock` owns the root. | Check the PID. Stop for a live PID. Move a dead lock to quarantine; never delete an unreadable lock blindly. |
| Operator touches display, input, lid, or power | The governed state changed during the window. | Lose the active member. If supply identity changed, end the entire window and start a new root with new calibrations and a new bound. |

An anchor-fallback member may be excluded by governed extraction rules when
membership still satisfies policy, but for a planned floor-campaign member
the operator response is still recollection. Never accept a fallback member
as a zero-width floor.

### Slot quarantine and supersession

Readiness and session supersession are append-only and semantic. A later
filename alone does not supersede anything: each successor arm receipt must
bind the immediately prior receipt's ID, relative path, receipt SHA-256, pack
ID, and pack SHA-256. Once that valid successor exists, the predecessor
refuses. Never overwrite, edit, delete, or silently skip a receipt or its
sidecar.

A used bracket-session ID, pre- or post-attempt ID, or launch capability is
never reused. A consumed capability stays consumed even if the foreground
launch fails to start. A changed pack, row registry, acceptance artifact,
freeze evidence, or identity projection requires a new pack ID and new pack
and custody roots. A refusal caused only by live pre-launch state may reuse
unchanged committed pack bytes only through a new bracket session and a new
external arm receipt that semantically supersedes its predecessor, and only
when the frozen attempt policy permits that successor. Preserve every prior
receipt as evidence.

Inspect the occupied bundle:

```sh
.venv/bin/python -m joulewise validate-bundle --strict \
  "$RUNS_ROOT/$BUNDLE_ID"
```

Move it outside the runs root:

```sh
mv "$RUNS_ROOT/$BUNDLE_ID" \
  "$QUARANTINE_ROOT/${BUNDLE_ID}__$(TZ=UTC date '+%Y%m%dT%H%M%SZ')"
```

After the exact replacement exists and is strict-valid, record the old
occurrence:

```sh
.venv/bin/python scripts/run_campaign.py \
  --record-supersession "$BUNDLE_ID" \
  --quarantine-path "$QUARANTINED_BUNDLE_PATH" \
  --reason "Aborted occupied slot; old occurrence preserved and strict-valid replacement selected" \
  --runs-dir "$RUNS_ROOT" \
  --log "$RUNS_ROOT/campaign_log.jsonl" \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Two present bundles for one occurrence always refuse.

### D-100 §10 amendment — terminally absent salvage is exceptional

Zero present bundles is `terminal_absent`, not a successful retry. It refuses
by default. The only non-refusing disposition is capped at one absent member
and requires three same-failure D-087 occurrences bound by byte-derived
signatures and exhaustive evidence. Each occurrence must mechanically prove
one of these branches:

- a hash-bound launcher refusal with no bytes for the member anywhere in the
  closure-declared custody universe (the runs root plus every declared
  quarantine/custody root); or
- a pre-workload admission abort whose only `stage_started` prefix is
  `validate`, `prepare`, `idle_baseline`, whose metadata records
  `environment_admission.decision: abort`, a nonempty ordered attempt list
  with every `admitted: false`, and
  `claim_reason: environment_admission_failed`, and whose failed summary has
  every measurand field null.

For the second branch, powermetrics/rich telemetry may end at most **0.250 s**
after the idle-baseline failure event. The observed 136–171 ms final flush is
teardown evidence; a later sample, a missing or truncated event stream, any
workload/measurement stage, any non-null measurand, an unknown non-null
summary field, an unreadable file, a symlink/duplicate artifact, or a fourth
occurrence voids the license. Preserve original failed bundles and verdict
rows byte-for-byte.

### Post-calibration failure and the a10 recorded deviation

The pre-D-117 chain retried a calibration exactly once when the sole reason
was `clock_anchor_unresolved`. The D-117 durable-session chain does not infer
or dispatch a retry from a shell directory; it stops at the registered exit
and requires a newly frozen session when the prospective plan licenses one.

Window a10 recorded an operator deviation against that rule. Its first post
calibration, `20260725T055825`, failed with pulse-detection reasons rather
than `clock_anchor_unresolved`; the frozen run-book said abort and repair the
machine outside the window. The lead instead settled and retried, and the
retry, `20260725T060617`, was valid. Both captures are preserved.

What kept that deviation from corrupting the record is the discipline that
still binds every operator here:

- [ ] Preserve every failed calibration attempt under
  `RUNS_ROOT/instrument_validation/`. Never delete or overwrite one.
- [ ] Consume the **earliest valid causal post calibration**. Never select
  among valid captures on the basis of the bound each one produces. In a10 no
  such selection occurred, and that is why the retry was recoverable.
- [ ] Record any retry, its reason, and both directory names in the close-out
  as a deviation.

Whether a post-calibration retry is permitted for a non-clock failure is not
settled by this run-book. Until Ed rules (§13.2), the standing instruction
remains abort and repair outside the window, and any retry is a recorded
deviation rather than a licensed step.

## 11. Record duration margins, back up, then extract in the same custody session

Immediately after the finalized post-calibration slot and passing whole-window
verdict, before backup or extraction, record the comparative-cell duration
margins from the frozen pack and authenticated run bytes:

```sh
.venv/bin/python scripts/record_window_duration_margins.py \
  --repository-root "$REPO" \
  --pack-root "$PACK_ROOT" \
  --runs-root "$RUNS_ROOT" \
  --receipt-root "$WINDOW_CUSTODY_ROOT" \
  --pack-identity "$WINDOW_ID"
```

`PACK_ROOT` is the frozen campaign pack containing `plan_tree.json`;
`WINDOW_PLAN_ROOT` is not a valid substitute. The operator supplies only
roots and the frozen pack identity. The recorder
derives the registered cells, membership, evidence values, status, and
deterministic output path. `REFUSE` stops close-out without writing a receipt.
`PASS` means every registered member was uniquely found and every required
value was derived from authenticated bytes; it does not require a positive
margin. Preserve the reported receipt path and SHA-256 as their own close-out
fields.

Back up the claim corpus:

```sh
bash scripts/backup_runs.sh "$RUNS_ROOT" "$BACKUP_DEST"
```

Require exit code 0 and keep the source root unchanged.

Then run governed extraction:

```sh
.venv/bin/python scripts/extract_detection_floors.py \
  --runs-root "$RUNS_ROOT" \
  --spec "$WINDOW_PLAN_ROOT/extraction_spec.json" \
  --out "$WINDOW_CUSTODY_ROOT/detection-floor-extraction.json" \
  --evaluation-basis-sha256 "$WHOLE_WINDOW_BASIS_SHA256" \
  --consumption-semantics-id d078_minted_envelopes_v1 \
  --hash-bundles
```

`--evaluation-basis-sha256` and `--consumption-semantics-id` are required
together, and the id must name the exact consumption semantics of the
verdict row being consumed: `d078_minted_envelopes_v1` for the ordinary §9
verdict above, or `salvage_dangler_exclusion_v1` for a licensed D-100
salvage basis.

- [ ] Require exit code 0 and `all_cells_extractable: true`.
- [ ] Require no `spec_membership_refusals` or
  `idle_admission_refusals`.
- [ ] Confirm extraction consumes the exact passing whole-window basis.
- [ ] Confirm each floor cell carries the matching
  `whole_window_drift_allowance`.
- [ ] Confirm no anchor-fallback or mock member entered a claim-bearing cell.
- [ ] Confirm custody-bound config, metadata, and summary telemetry identities
  agree.
- [ ] Confirm every campaign member is included, superseded, quarantined, or
  explicitly refused.
- [ ] Keep extraction output outside immutable bundle directories.

The allowance widens the already guarded/corner-widened floor. It does not
replace instrument uncertainty, and it is never silently omitted.

## 12. Close-out record

Record:

- the exact Git commit and policy hash;
- the freeze-receipt path and SHA-256;
- the reviewed-head dry-run receipt path and SHA-256;
- the final arm-receipt path and SHA-256;
- the launch-consumption receipt path and SHA-256;
- the linked launch-start, launch-settle, and launch-completion receipt paths
  and SHA-256 values (completion is mandatory before verdict, extraction, or
  mint);
- the one consumption SHA-256 carried byte-for-byte by every marker-bearing
  bundle/calibration metadata record, whole-window basis, extraction report,
  and mint input;
- the root-preflight receipt path and SHA-256;
- the waiver receipt path and SHA-256;
- the backup-preflight receipt path and SHA-256;
- each successful postcollection backup receipt path and SHA-256, recorded
  separately from backup preflight and separately for the claim and bound
  roots;
- the §5C lead live-verification record: the literal commands, commit hash,
  frozen-plan SHA-256, exit codes, and the observed
  `calibration_pre_reserve_authorized` / `status: reserved` /
  `calibration_writer_arm_authorized` outputs from the desk rehearsal;
- the window ID, start/end times, and power-supply identity;
- pre/post calibration IDs, bounds, and bracket drift;
- the 12 bound-corpus bundle IDs, bound derivation SHA-256, mint time, expiry,
  and freshness bindings;
- all seven window-reference bundle IDs, endpoint means and standard errors,
  midpoint value, both family screen results, and both allowances;
- the whole-window evaluation-basis SHA-256 and member occurrence set;
- every failed, quarantined, superseded, or waived occurrence;
- the comparative-cell window-duration-margin receipt path and SHA-256,
  recorded separately from bound-mint, backup, and extraction outputs;
- backup destination and exit status;
- extraction artifact path and result;
- whether automatic network time was disabled for this window, when it was
  disabled, and when it was restored (§5A);
- every calibration attempt, including failed ones, and any retry recorded as
  a deviation;
- member counts by distinct bundle ID, never by campaign-log line.

Call the window **claim-bearing** only when the whole-window verdict is
`passed`, both family allowances are authenticated, the backup succeeds, and
same-custody extraction completes with no refusal. Otherwise preserve the
evidence and report the strongest lower, non-claim-bearing status it actually
earned.

## 13. Open questions for Ed (recorded, not adopted)

Nothing in this section is in force. Do not act on any of it during a window.
It is recorded here so the argument is not lost between sessions.

### 13.1 A governed member-level retry for `clock_anchor_unresolved`

**Observation (historical pre-D-117 chain).** The former shell chain treated
`clock_anchor_unresolved` as the one retryable condition **for calibrations**,
retrying once after a settle. There is no equivalent retry for **members**. A
single member that hits the same transient clock condition fails that member,
and under `--max-failures 1` that one failure aborts the whole stage.

**For.** The condition is demonstrably transient and self-clearing: in §5A,
`neg8-refcorpus-r11` failed at a 7.769 ms span and `r12`, collected
immediately after it, anchored cleanly at 0.305 ms. A governed member-level
retry — once only, after a full settle, restricted to
`clock_anchor_unresolved` alone, with the failed occurrence quarantined and
superseded exactly as today — would have saved both lost windows.

**Against.** Any retry loosens the fail-closed posture. A systematic clock
problem would present as a run of individually retried transients, and the
retry would mask it: the window would look healthy while producing members
collected under a drifting clock. The current behaviour makes the problem
loud, which is the only reason it was diagnosed at all.

This is a protocol change affecting claim-bearing data, so it is explicitly
Ed's call. Do not implement it, and do not treat a hand retry as an
equivalent.

### 13.2 Post-calibration retry shape for a non-clock failure

Raised by the window-a10 deviation recorded in §10, "Post-calibration failure
and the a10 recorded deviation". The question is whether a post calibration
that fails for a reason other than `clock_anchor_unresolved` may be retried
once after a settle, or must abort the window as the current text requires.
Undecided; the current text stands.
