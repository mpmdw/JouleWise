# Quiet-Mac Claim-Window Run-Book

**Operator:** Ed

**Lane:** `[QUIET-MAC]`

**Applies to:** claim-bearing Mac measurement windows after PR #85

**Main authorities:** D-077 and D-078 in `docs/decision_log.md`,
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
- [ ] Until FLOOR-BIND-01 closes, perform claim-bearing extraction in the
  same lead-controlled custody session as collection and verdict production.

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

Example `window.env`:

```sh
WINDOW_ID=window_a9_YYYYMMDD
RUNS_ROOT=/Users/edr/code/JouleWise/runs_window_a9_YYYYMMDD
BOUND_RUNS_ROOT=/Users/edr/code/JouleWise/runs_window_a9_YYYYMMDD_bound
CUSTODY_ROOT=/Users/edr/JouleWise-window-custody/window_a9_YYYYMMDD
BACKUP_DEST="/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/window_a9_YYYYMMDD"
POWER_POLICY=ac_high_power
SETTLE_S=180
```

`RUNS_ROOT` holds the claim-window members and calibration bracket.
`BOUND_RUNS_ROOT` holds only the 12-member settled-reference corpus used to
mint this window's bound. Keep the roots separate so the corpus members do
not accidentally enter the claim-window member basis.

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

## 6. The foreground measurement chain

Save the following as `WINDOW_PLAN_ROOT/window-chain.zsh`, review it, and
record its SHA-256 before closing all agents:

```zsh
#!/bin/zsh
set -euo pipefail

WINDOW_PLAN_ROOT="$1"
source "$WINDOW_PLAN_ROOT/window.env"

REPO=/Users/edr/code/JouleWise
PY="$REPO/.venv/bin/python"
POLICY="$REPO/configs/campaign_policies/quiet_mac_p2_production.json"
REF_ROOT="$REPO/configs/campaigns/window_references"
BOUND_CONFIG_ROOT="$REPO/configs/campaigns/neg8_reference_corpus"
BOUND_MANIFEST="$BOUND_CONFIG_ROOT/derivation/settled_corpus.json"
CLAIM_LOG="$RUNS_ROOT/campaign_log.jsonl"
BOUND_LOG="$BOUND_RUNS_ROOT/campaign_log.jsonl"
NEG8_DRIFT_BOUND="$BOUND_RUNS_ROOT/neg8-drift-bound.json"
OPERATOR_LOG_ROOT="$CUSTODY_ROOT/operator_logs"
QUARANTINE_ROOT="$CUSTODY_ROOT/quarantine"

mkdir -p \
  "$RUNS_ROOT/instrument_validation" \
  "$BOUND_RUNS_ROOT" \
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

latest_calibration() {
  /usr/bin/find "$RUNS_ROOT/instrument_validation" \
    -mindepth 1 -maxdepth 1 -type d -print |
    /usr/bin/sort |
    /usr/bin/tail -n 1
}

arm_for_calibration() {
  echo "$(timestamp) calibration display arm: 20-second countdown" \
    >> "$OPERATOR_LOG_ROOT/window-chain.log"
  /bin/sleep 20
  /usr/bin/pmset displaysleepnow \
    >> "$OPERATOR_LOG_ROOT/window-chain.log" 2>&1
  /bin/sleep 5
}

calibrate_once() {
  local label="$1"
  arm_for_calibration
  "$PY" "$REPO/scripts/validate_powermetrics_fiducial.py" \
    --allow-live \
    --output-root "$RUNS_ROOT/instrument_validation" \
    --power-policy "$POWER_POLICY" \
    >> "$OPERATOR_LOG_ROOT/${label}-calibration.log" 2>&1
}

calibrate_with_clock_retry() {
  local label="$1"
  local before candidate rc reasons

  settle
  before="$(latest_calibration)"
  set +e
  calibrate_once "$label"
  rc=$?
  set -e
  candidate="$(latest_calibration)"

  if [ "$rc" -eq 0 ] && [ -n "$candidate" ] && [ "$candidate" != "$before" ]; then
    print -r -- "$candidate"
    return 0
  fi

  [ -n "$candidate" ] || return 1
  reasons="$(/usr/bin/jq -r '.reasons[]?' \
    "$candidate/instrument_evidence.json" | /usr/bin/sort -u)"
  if [ "$reasons" != "clock_anchor_unresolved" ]; then
    echo "$label calibration failed: $reasons" >&2
    return 1
  fi

  settle
  before="$candidate"
  set +e
  calibrate_once "${label}-retry"
  rc=$?
  set -e
  candidate="$(latest_calibration)"
  [ "$rc" -eq 0 ] && [ -n "$candidate" ] && [ "$candidate" != "$before" ] || return 1
  print -r -- "$candidate"
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
    run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REPO/$stage" "$PRE_CAL_DIR" "$stage"
  done < "$list"
}

cd "$REPO"
echo "$(timestamp) chain_start" >> "$OPERATOR_LOG_ROOT/window-chain.log"

PRE_CAL_DIR="$(calibrate_with_clock_retry pre)"
echo "$(timestamp) pre_calibration=$PRE_CAL_DIR" >> "$OPERATOR_LOG_ROOT/window-chain.log"

# The reference corpus and bound are minted inside this same quiet window.
run_stage "$BOUND_RUNS_ROOT" "$BOUND_LOG" "$BOUND_CONFIG_ROOT" "$PRE_CAL_DIR" \
  neg8-bound-corpus

"$PY" "$REPO/scripts/run_campaign.py" \
  --derive-neg8-drift-bound "$BOUND_MANIFEST" \
  --neg8-drift-bound-output "$NEG8_DRIFT_BOUND" \
  --runs-dir "$BOUND_RUNS_ROOT" \
  >> "$OPERATOR_LOG_ROOT/bound-mint.log" 2>&1
echo "$(timestamp) neg8_bound=$NEG8_DRIFT_BOUND" >> "$OPERATOR_LOG_ROOT/window-chain.log"

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/start_triplet" "$PRE_CAL_DIR" \
  start-reference-triplet

run_stage_list "$WINDOW_PLAN_ROOT/before_midpoint_stages.txt"

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/midpoint" "$PRE_CAL_DIR" \
  midpoint-reference

run_stage_list "$WINDOW_PLAN_ROOT/after_midpoint_stages.txt"

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/end_triplet" "$PRE_CAL_DIR" \
  end-reference-triplet

POST_CAL_DIR="$(calibrate_with_clock_retry post)"
echo "$(timestamp) post_calibration=$POST_CAL_DIR" >> "$OPERATOR_LOG_ROOT/window-chain.log"
echo "$(timestamp) measurement_complete" >> "$OPERATOR_LOG_ROOT/window-chain.log"
```

After every agent is closed, launch exactly once:

```sh
caffeinate -is /bin/zsh "$WINDOW_PLAN_ROOT/window-chain.zsh" "$WINDOW_PLAN_ROOT"
```

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
- [ ] Confirm bracket-bound drift is within the production policy's
  `0.01 s`.
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

## 10. Failure playbook

| Symptom or refusal | Meaning | Required action |
|---|---|---|
| Display awake, screensaver engaged, `environment_admission_failed`, or CPU admission failure | The measurement environment was contaminated or unknown. | Lose the affected member. Stop the stage, remove the cause, settle 180 seconds, and rerun into a clean slot. Never waive admission. |
| `clock_anchor_unresolved` on calibration | The calibration capture could not be causally anchored. | Preserve it, settle, and retry once into a new validation directory. Abort after the second failure or any different calibration reason. |
| `pulse_calibration_rollover_gate_timeout` | Native powermetrics time did not advance before the pulse train. | Abort calibration and preserve the evidence. Repair machine state outside the window. |
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
| `incomplete_existing` or an occupied run ID | A failed or interrupted bundle already owns the path. | Strict-validate and preserve it, move it outside the runs root, rerun the exact config, then record supersession. |
| `another campaign appears to be running` | A live process or stale `campaign.lock` owns the root. | Check the PID. Stop for a live PID. Move a dead lock to quarantine; never delete an unreadable lock blindly. |
| Operator touches display, input, lid, or power | The governed state changed during the window. | Lose the active member. If supply identity changed, end the entire window and start a new root with new calibrations and a new bound. |

An anchor-fallback member may be excluded by governed extraction rules when
membership still satisfies policy, but for a planned floor-campaign member
the operator response is still recollection. Never accept a fallback member
as a zero-width floor.

### Slot quarantine and supersession

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

## 11. Back up, then extract in the same custody session

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
  --out "$CUSTODY_ROOT/detection-floor-extraction.json" \
  --hash-bundles
```

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
- the window ID, start/end times, and power-supply identity;
- pre/post calibration IDs, bounds, and bracket drift;
- the 12 bound-corpus bundle IDs, bound derivation SHA-256, mint time, expiry,
  and freshness bindings;
- all seven window-reference bundle IDs, endpoint means and standard errors,
  midpoint value, both family screen results, and both allowances;
- the whole-window evaluation-basis SHA-256 and member occurrence set;
- every failed, quarantined, superseded, or waived occurrence;
- backup destination and exit status;
- extraction artifact path and result;
- member counts by distinct bundle ID, never by campaign-log line.

Call the window **claim-bearing** only when the whole-window verdict is
`passed`, both family allowances are authenticated, the backup succeeds, and
same-custody extraction completes with no refusal. Otherwise preserve the
evidence and report the strongest lower, non-claim-bearing status it actually
earned.
