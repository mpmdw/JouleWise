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

**A packet is a pointer, never trusted data.** At the arm, `arm_checks` rebuilds the packet with
`build_packet` from the identities the supplied packet names (`record_commit`, `record_path`,
the series commit and path, the pushed ref), using the arm's own clock and its own
artifact-set digest (`rebuild_and_compare`). It requires canonical equality with the supplied
packet, ignoring only `pushed_tip` (top level and the nested copy in `checks.record_committed`) and `packet_preflight`; any other changed, removed or added
field, or edited basis text, refuses. A rebuild that fails (a bad hash, a broken chain) refuses.
The arm judges its own build and retains it in the arm record as `rebuilt_packet`
(`rebuilt_packet_sha256`), with `supplied_packet_matches_rebuild`, the packet file digest and the
live-meter evidence. `packet_preflight.ready` is only desk readiness. The builder is strict-tier
and part of the executed closure.

The arm itself computes `series_powermode`, `external_volume`, `charging_battery` and
`meter_reader_live` (a short live KM003C probe, which must end before the quiet/display dwell starts: the arm records `quiet_dwell` with both timestamps and refuses otherwise) from current hardware; the packet cannot assert
them. The complete 16-entry source map (15 gating; `meter_coverage` is recorded, non-gating) is
retained in `entry_sources`, and the consumer computes `calibration_stop` from the authenticated
counts. `prepared_at`, the live meter check and the battery evidence are never lead-entered.
Expiry is mandatory: the builder sets `valid_until_epoch_s` to the earlier quiet/meter observation
expiry, a missing or non-numeric value refuses, and the arm clock must be before it. The
quiet start state is the committed observation until the R16 condition-waits evaluator receipt
(`align/2026-11-08-condition-waits-impl`) lands; then the arm uses that receipt.

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
* **Final adjudication (R17 review F4).** `pilot`, `desk` and `exclusions` (the
  record's own, or the successor's `previous_final`) count as final only when
  they evidence a completed, plan-bound harvest: `desk.harvest_status` is `ok` or
  `members_excluded` (never the `running_off_mbp` placeholder), `desk.plan_id` and
  `PILOT.json`'s `plan_id` equal this record's `sources.plan.plan_id`,
  `PILOT.json`'s `status` is `instrument_ok` or `instrument_incomplete`, and any
  `members_excluded` the desk or PILOT recorded equals the exclusions source.
  A completed desk that did not pass stays final. Window binding is the thermal
  section's `model/window` keys and roster. Otherwise the record is provisional
  (it needs `sources.light_triage`), and every window of the hash chain other than
  the previous one, test windows included, must be final (R17: k final before
  the arm of k+2), or `member_eligibility` fails.
* `finalized_manifest` (required after R1, R17 review F2): descriptor of the
  record-bound tree manifest `harvest_offload.finalized_manifest` wrote at
  finalize (`joulewise.align_v4.finalized_manifest.v2`, canonical JSON bytes, so
  its SHA-256 is the digest `unpack --finalized-sha256` checks). It binds the
  restore namespace, every tree entry and the finite external-input closure.
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
* The window records are **hash-chained**: each record names its predecessor
  (`previous_record`: `commit`, `path`, `sha256`) and the series ledger `series/state.json`
  names the latest one (`previous_record`, `series_sha256`). The builder walks the chain back to
  R1/W1, so an omitted attempt cannot be skipped. Counts come from each record's roster, capture
  artifacts, thermal PILOT and final exclusions; no entry supplies counts. The packet lists
  every attempt in `window_chain` (including zero-capture ones such as `C3#1`);
  W1/development/test records never count toward calibration.
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
| series_powermode | arm-computed powermode observation | triage series_powermode failed or unevaluated |
| external_volume | current arm mount census | triage external_volume failed or unevaluated |
| charging_battery | current arm AC/battery/top-up/OBC observation | triage charging_battery failed or unevaluated |
| meter_reader_live | arm-computed live KM003C probe (aligned stream, trailer, consistent offset); gating | meter not verified live |
| meter_coverage | exact previous roster coverage tabulation; recorded, non-gating | (never refuses) |
| capture_faults | exact roster sidecar/powermetrics coverage, flags and exclusion lists | capture coverage or X1-X8 tabulation missing |
| thermal_escalation | U1–U3 per gated model; prospective ladder when failed/unevaluated | U1-U3 failure needs prospective recorded escalation |
| cohort_pool_rules | native D slot/identity assertion; failed/excluded pool bar; next configuration equality | previous D four-slot cohort inconsistent; U1-U3 failure bars pool entry |
| sentinel_roster | U4 consequence (A15 / R21: U5 never triggers) and exact next roster | next frozen roster must include two extra sentinels after a U4 inconclusive |
| member_eligibility | final exclusions, X5/token comparisons and capture inventory | desk and final exclusions disagree; identity X5/U3 pair unresolved |
| calibration_stop | count-only fixed-eight predicate over authenticated history | escalate_to_lead; pending_final_eligibility; insufficient_calibration; role mismatch |
| battery_window | the desk's `v4_B_bar` for the previous record; `consecutive_non_pass` is the trailing non-passing run on the hash-linked chain (missing evidence is a non-pass; R1 has no B bar); the consumer turns a first non-pass into an automatic resume and needs a signed `battery_rulings` row for the second | previous B window did not pass; no signed battery ruling after the second |
| full_desk_gate | passing native desk and matching computed code/config state | full desk must complete and pass after W1 or a code/config change |

Coverage/fault **tabulation** gates; a historic fault itself is retained and
adjudicated under the registered exclusions. In particular, KM003C coverage gaps
are listed under `gaps` and never veto powermetrics eligibility (MED-2b).
An unverified **current** meter still refuses. Four hardware checks always stay
arm-computed. Previous-window thermal/cohort/sentinel/eligibility checks alone
may be `not_applicable` before W1 (`previous_window=R1`). The full desk is mandatory
after W1 or any code/config change; an unchanged later window can defer it.

The local remote-tracking ref proves reachability from a previously fetched push,
not fresh remote availability. The builder makes no network call. Custody must
refresh that ref through the ordinary authorized transport before building.

## Zero-capture rulings

Zero captured members consume no calibration slot and carry zero eligible counts. The retry keeps
the same window id with an attempt suffix: `C3#1` then `C3#2` (`v4_cadence.WINDOW_ID` accepts
`#k`); the frozen order is unchanged. One captured member consumes a slot even when no member
remains eligible. Two consecutive zero-capture attempts return `escalate_to_lead`. The lead's
prospective ruling is a `lead_rulings` row in the series ledger:

```json
{"ruling_id":"LEAD-RULING-ID","after_window":"C1#2","text":"rulings/LEAD-RULING-ID.md","lead_signature":"lead: ..."}
```

`text` names a committed ruling text file at the series commit; the builder computes
`text_sha256` from its bytes (never entered by hand) and emits
`{ruling_id, text_sha256, resets: "zero_capture_escalation", after_window, lead_signature}`.
`calibration_stop` consumes it to reset only the trailing refusal count. The id must be nonblank
and unique and `after_window` must match the current two-zero tail. It changes no captured count,
eligibility, order, eight-window cap or 39/pair target. Two further zeros escalate again; it cannot
admit a ninth counted window or repair insufficient calibration. A U1-U3 failure gives that model
0 eligible from that window (R15, RUN_STATE 226).

## Battery rulings (lead ruling 9, W1-BLOCKERS)

A second consecutive non-passing B window needs a `battery_rulings` row in the series ledger,
shaped like a lead ruling: `{"ruling_id","after_window","text","lead_signature"}`, where `text`
names a committed ruling text file at the series commit. The builder emits
`{ruling_id, text_sha256 (computed from those bytes), after_window, lead_signature}`; the
consumer admits it only when `after_window` is the previous window. A false `v4_B_bar` alone does
not fail the full desk (`full_desk_gate.pass` from the native desk, else the recorded checks minus
the exempt key); `battery_window` governs it.

## Series history, supplemental sentinels and the desk ceiling (delta5)

The packet's `series_history` is derived from the hash-linked records. For a calibration attempt the
counts come from the frozen calibration pool only (ordinary and supplemental sentinels, anchors, known-H
and test members never enter the eligible counts); `captured_members` counts authenticated captures
minus the supplemental diagnostics (R20), so a window with only supplemental captures counts zero. Each
calibration record must commit the desk's provisional `series_desk_row` (`pilot.extra_checks`); its
`desk_eligible_benign` is carried into the history as an upper bound that the final counts may lower,
never raise. A retry's previous window (`C1#2`) is compared with the series by its slot (`C1`), while
the full attempt id stays in the chain, the records and any ruling.

## Replacement windows (R22-2)

A calibration record can be **barred for a structural reason only**: `u1_u3_fail` (the desk's U1-U3 verdict FAILed
for a gated model), `whole_window_capture_failure` (the committed terminal result is not a completed GO chain),
or a zero-capture refusal beyond the retry (`C3` and `C3#2` both captured nothing). The builder derives each bar
from the committed record (never from a score or an eligible count), zeroes the barred window's eligible counts and
carries `barred` into `calibration_windows` and `series_history`. A barred window is not counted and owes one of up to six
replacement windows (R24), C9 through C14 in order, which the series arms only after C8 and only while fewer than 8
windows are counted. `calibration_decision` reports `barred_windows` and `replacements_used`.

**courier_delivery source (F-09; research lead RL-35):** the run path writes `night/courier.delivery.json`, and the next-arm release check reads it. A dead-man-delivered night whose `courier.json` still says `sent: false` is released on that delivery receipt. Exercised by native check 8.
