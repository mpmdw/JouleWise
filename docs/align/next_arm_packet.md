# R12 next-arm packet builder

Run `scripts/align_v4_next_arm_packet.py` on the desk machine after custody
export and record commit. It reads explicit Git blobs only: no directory
discovery, harvest, model loading, outcome analysis, hardware commands or network.
It never follows a path embedded in a night plan, PILOT or result. All evidence
must already be available in the desk repository. Preserve raw bundles unchanged.

```sh
python3.13 -B scripts/align_v4_next_arm_packet.py --emit-triage-template
python3.13 -B scripts/align_v4_next_arm_packet.py \
  --repo DESK_REPO \
  --record-commit FULL_RECORD_COMMIT --record-path records/W1/record.json \
  --series-commit FULL_SERIES_COMMIT --series-path series/state.json \
  --pushed-ref refs/remotes/origin/records \
  --output next-arm.json
```

The template includes record and series source inventories and a refusing packet
skeleton. It is a schema aid, never an armable packet. The command creates a new
output file exclusively. Exit 0 means packet preflight passes; exit 2 means an
evidence or gating refusal. A built refusing packet still contains every packet
check and its diagnostic basis. Invalid root schemas, missing commits or mismatched
record/series identity refuse before a packet can be built.

Pass the resulting JSON to `align_v4_session.py install --next-arm-triage`.
`packet_preflight.ready` is only desk readiness: the arm still computes
`series_powermode`, `external_volume` and `charging_battery` from current hardware.
The packet cannot assert those three checks. The complete 14-entry source map is
retained in `entry_sources`; the arm supplies the three pending values, and the
consumer computes `calibration_stop` from the authenticated counts.
The builder sets `valid_until_epoch_s` to the earlier quiet/meter observation
expiry. The consumer rechecks it at arm time; rebuilding from the same expired
observations cannot refresh it. Native quiet admission still runs at collection.
The persisted arm record also retains exact packet bytes (base64), their SHA-256
and `record_commit` under `next_arm_triage_source`, alongside the triage evaluation.
Direct Python dict callers get canonical sorted JSON bytes; CLI file callers retain
the original bytes, including whitespace.

## Committed inputs

Every descriptor is `{"path": "repository/relative/file", "sha256": "64 hex"}`.
Paths refer to **regular blobs at the specified commit**, never working-tree
files or custody locators. Absolute paths, traversal, symlinks and sealed-directory
names are refused. Digests are SHA-256 of exact source bytes, including newlines.
The builder verifies them and retains commit, path, byte length and digest in the
packet's `evidence` inventory. Each packet check lists the sources it used.
Repeated reads reuse immutable blobs. Duplicate JSON keys and non-finite values
refuse.

Large raw captures need not be committed to Git. For `captures` and
`raw_evidence` only, the exporter may instead supply
`{"locator":"opaque custody location","sha256":"64 hex","bytes":123}`.
That metadata is authenticated by the record commit and retained verbatim with
`verification: committed_digest_inventory_only`. The builder never opens or stats
the locator and makes no byte-verification claim for it. Raw hashing/export custody
owns those digests. This keeps real traces out of Git while including their exact
recorded identities in the packet. A null capture means none; a positive recorded
byte length means capture occurred even if excluded later.

The record index is packaging metadata, not a list of triage verdicts. Export
tools/record custodians supply the following named artifacts and byte digests;
do not enter triage pass/fail values or eligible totals in the index:

* `schema`: `joulewise.align_v4.window_record.v1`; `window`: the attempt id
  (`R1`, `W1`, or a series attempt id); `role`: `development`, `calibration`
  or `test`; `finalized_at_epoch_s`: the custody finalization timestamp.
* `sources.plan`: original native night plan; `collection_plan`: exact member
  roster (`members[].run_id`, model, role, condition, task_pair). For escalation,
  its `thermal_policy` projection names `idle_s`, `delta_slow_c` and
  `quantization_bits` from the frozen configuration.
* `sources.result`, `chain_started`, `chain_exited`, `courier`, `courier_sent`,
  `watchdog_state`: native terminal artifacts. Absent chain-start/exit artifacts
  are omitted or null only for a genuine pre-chain refusal. The watchdog source
  is its state snapshot with `released_terminal_windows`, including the native
  `plan_id:custody_root:result_sha256` release key. This latch is the watchdog's
  proof of the empty agent/driver/plan-process census, not a child-exit claim.
* `sources.pilot`: the v4 session `PILOT.json` (thermal data under
  `extra_checks.thermal`, meter under `extra_checks.km003c`). The portable thermal
  PILOT shape is also accepted, with a `km003c` addendum. R1 must have the same
  off-machine coverage/fault and meter tabulations over its exported roster;
  it does not need U1–U3, pool, sentinel or eligibility verdicts to arm W1.
  This is an explicit adapter input requirement: the builder does not run an R1
  desk or invent those tabulations from the R1 driver's aggregate slots.
* `sources.desk`: unmodified native `desk.json`, with `plan_id`, `checks`,
  `pilot_status`, `harvest_status`. A later off-machine desk may instead record
  `status: running_off_mbp` while deferred. `sources.exclusions` is the final
  harvest `exclusions.json`, with `members_excluded[].run_id` and `codes`.
* `captures`: an exhaustive map from every planned run id to a descriptor for
  its captured measurement artifact, or null for no capture. A nonempty captured
  artifact counts even if its member later fails; eligibility is separate.
  The exporter must identify actual measurement artifacts, not directory markers
  or transcripts. Empty artifacts refuse instead of being guessed as zero capture.
* `raw_evidence`: nonempty list of descriptors for raw supporting evidence,
  including meter/sidecar/powermetrics and fault journals used by the desk. These
  and every named source/capture digest are checked before `record_committed`
  passes: exported blobs byte-for-byte, opaque raw entries as authenticated digest
  metadata. The index never modifies those artifacts.
* `code_config`: exhaustive descriptor list of the installed code/configuration
  state the full desk assessed. `code_config_commit` may pin a separate full
  commit id when the installed tree differs from the record commit. A sorted
  path/digest projection computes state identity; no free `changed` flag is read.

The series file (`joulewise.align_v4.series_state.v1`) is prospective lead-owned
state at `--series-commit`, with:

* `previous_record` and `last_passed_record`: full `commit`, `path`, `sha256`
  bindings to record indexes. The former must match the CLI record exactly.
  The latter supplies the last passing native desk and its code/config inventory.
* `prepared_at_epoch_s`: the preparation timestamp; `quiet` and `meter_live`:
  descriptors for exported post-terminal observations. Quiet observations have
  numeric `cooldown_s`, `display_off_s`, `dwell_s`, `observed_at_epoch_s`, and
  `active_work` (empty only after desk, hashing and evidence traffic stop on MBP).
  `quiet_requirements` freezes positive minima for the three durations and a
  positive `max_age_s`. No duration is defaulted. Meter observations carry positive
  integer `sample_count`, resolved numeric `raw_offset_ns`, `observed_at_epoch_s`.
  Both must follow terminal completion, precede preparation and satisfy freshness.
  These are observations exported by the hardware/quiet-state lane, not operator
  triage verdicts; this off-machine builder cannot make them live itself.
* `next_plan`: descriptor for the frozen next-window projection: `window`,
  `role` (`calibration` or `test`, or `development` for W1 following R1),
  `members` with sentinel roles, `configuration`
  (the four D slots plus `cohort_identity`), `thermal_policy`, and `code_config`
  (optional `code_config_commit`). It must be the projection of the installed
  plan, not a proposed configuration. Scorer/series registration remains lead-owned.
* `history`: attempts in the frozen order, each a `record_commit` and
  `record_path`. Counts come from each record's roster, capture artifacts, thermal
  PILOT and final exclusions. No history entry supplies counts. Include the current
  calibration attempt at the tail; W1/development/test records never count.
* `pool_members`: prior-window D member ids being admitted to the held-out pool;
  `sentinel_ids`: ordered frozen next-window sentinel ids; `escalations`: prospective
  rows with previous `window`, `ruling_id`, `next_plan_sha256`. A failed U1–U3
  window enters no pool. The ladder requires the idle step, then directional
  0.5 °C steps (≤2 °C), then the D 8→4 bit step, recorded before use.

The builder consumes explicit committed inputs. Exporting the record index,
native observation snapshots and next-plan projection remains the custody/series
lane's responsibility; it does not yet have an automatic export adapter here.
No native collection readiness is claimed by the synthetic tests.

## Entry authority and refusal reasons

| Entry | Source and computation | Representative refusal basis |
|---|---|---|
| record_committed | finalization, record/raw SHA-256, commit reachability from the named remote-tracking ref | record finalization missing; source SHA-256 mismatch; Git evidence unavailable |
| terminal_completion | shared `terminal_window_release`, native delivery, exact watchdog release latch | courier delivery missing; chain_open; watchdog empty-process terminal latch missing |
| quiet_start_state | post-terminal quiet snapshot versus frozen minima and freshness | quiet start short/stale; desk, hashing or evidence traffic remains |
| series_powermode | current arm powermode observation | triage series_powermode failed or unevaluated |
| external_volume | current arm mount census | triage external_volume failed or unevaluated |
| charging_battery | current arm AC/battery/top-up/OBC observation | triage charging_battery failed or unevaluated |
| meter_samples_clock | exact previous roster coverage tabulation plus live sample/clock observation | meter tabulation roster mismatch; meter not verified live |
| capture_faults | exact roster sidecar/powermetrics coverage, flags and exclusion lists | capture coverage or X1-X8 tabulation missing |
| thermal_escalation | U1–U3 per gated model; prospective ladder when failed/unevaluated | U1-U3 failure needs prospective recorded escalation |
| cohort_pool_rules | native D slot/identity assertion; failed/excluded pool bar; next configuration equality | previous D four-slot cohort inconsistent; U1-U3 failure bars pool entry |
| sentinel_roster | U4/U5 consequence and exact next roster | next frozen roster must include two extra sentinels after U4/U5 inconclusive |
| member_eligibility | final exclusions, X5/token comparisons and capture inventory | desk and final exclusions disagree; identity X5/U3 pair unresolved |
| calibration_stop | count-only fixed-eight predicate over authenticated history | escalate_to_lead; pending_final_eligibility; insufficient_calibration; role mismatch |
| full_desk_gate | passing native desk and matching computed code/config state | full desk must complete and pass after W1 or a code/config change |

Coverage/fault **tabulation** gates; a historic fault itself is retained and
adjudicated under the registered exclusions. In particular, KM003C coverage gaps
are listed under `gaps` and never veto powermetrics eligibility (MED-2b).
An unverified **current** meter still refuses. Three hardware checks always stay
arm-computed. Previous-window thermal/cohort/sentinel/eligibility checks alone
may be `not_applicable` before W1 (`previous_window=R1`). The full desk is mandatory
after W1 or any code/config change; an unchanged later window can defer it.

The local remote-tracking ref proves reachability from a previously fetched push,
not fresh remote availability. The builder makes no network call. Custody must
refresh that ref through the ordinary authorized transport before building.

## Zero-capture rulings

Zero captured members consume no calibration slot and carry zero eligible counts.
One captured member consumes a slot even when no member remains eligible. Two
consecutive zero-capture attempts return `escalate_to_lead`. Keep both attempts
and append the lead's actual prospective ruling in `history`:

```json
{"type":"lead_ruling","ruling_id":"LEAD-RULING-ID","after_window":"C1-refusal-2"}
```

The builder retains that row verbatim; `calibration_stop` consumes it to reset
only the trailing refusal count (MED-2a). The id must be nonblank and unique and
`after_window` must match the current two-zero tail. It changes no captured count,
eligibility, order, eight-window cap or 39/pair target. Two further zeros escalate
again. It cannot admit a ninth counted window or repair insufficient calibration.
This wire addition preserves the current fixed-eight rule; do not import the cold
review branch's older count-stop implementation when integrating its findings.
