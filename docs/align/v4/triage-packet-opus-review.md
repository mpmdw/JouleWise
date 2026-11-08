# R12 next-arm packet builder: Opus cross-family cold review

- **Reviewed:** `origin/align/2026-11-08-triage-packet` @ `f1b90f950` (Sol 6.1 built it).
  The new file is `scripts/align_v4_next_arm_packet.py`, plus its consumer edits in
  `v4_cadence.py` and `align_v4_session.py`.
- **Judged against:** the current v4 head consumer, `origin/align/2026-11-08-v4-r11` @
  `2cce80ede`. That head has lead_ruling rows, `meter_reader_live` (gating),
  `meter_coverage` (non-gating), `record_commit` binding, the battery-log top-up and
  artifact-set-digest change detection.
- **Reviewer:** Claude Opus 5.5, cold. I read the code only, not the Sol report.
- **Date:** 2026-11-08.

## Verdict: HOLD

The builder's core is sound. Each previous-window entry comes from committed Git
blobs. Sources are read by exact digest and raw evidence digests are kept. The
per-entry refusals do what the docs say. Three problems block it:

1. **HIGH-1.** Neither consumer binds the packet to anything. An edited packet with
   valid statuses arms the machine. This is the smoke-kit finding, and it is still
   open on both branches. One edit can also forge `calibration_complete`, which
   opens a test arm.
2. **HIGH-2.** A stale packet can arm. On the packet branch the expiry check is
   skipped when the expiry key is missing. On the v4 head there is no expiry check
   at all.
3. **HIGH-3.** The builder emits the pre-r11 wire. Merged onto the v4 head, no
   packet it builds can ever admit, and `build_packet` crashes before it returns.

None of these touch blinding or prereg fidelity. HIGH-1 and HIGH-2 are about whether
the frozen triage gate is real. Under "proportionate care" the gate is one of the
guards worth keeping (Opus cold review, "Proportionality").

## Tests (one module per process, `python3.13 -B -m unittest`)

| Tree | Module | Result |
|---|---|---|
| packet `f1b90f950` | `tests.align.test_v4_next_arm_packet` | 19 OK |
| packet `f1b90f950` | `tests.align.test_v4_cadence` | 16 OK |
| packet `f1b90f950` | `tests.align.test_v4_next_arm_packet_opus_witnesses` (new) | **3 FAIL**, 1 pass (see below) |
| scratch merge (v4 `2cce80ede` + packet; consumer files taken from v4) | `test_v4_next_arm_packet` | **1 fail, 31 errors** (`next_arm_triage() got an unexpected keyword argument 'now_epoch_s'`; old lead-ruling rows rejected) |
| scratch merge | `test_v4_next_arm_packet_opus_witnesses` | **4 errors** (same TypeError) |
| scratch merge | `test_v4_cadence`, `test_v4_registration` (21), `test_v4_receipt_tiers`, `test_v4_executed_closure`, `test_v4_opus_cold_witnesses`, `test_v4_topup`, `test_v4_w1_synthetic` (14 skipped), `test_r11_delta_sol1`, `test_r11_delta_sol2`, `test_protocol_v4_doc` | all OK |

The merge conflicts in three files: `v4_cadence.py`, `align_v4_session.py` and
`pilot_protocol_v4.md`. I resolved all three to the v4 head, because the v4 head is
the consumer of record. The builder and its tests merge cleanly.

I ran a scratch probe with a one-line shim that drops `now_epoch_s`, then fed builder
packets to the v4 head `next_arm_triage`. Synthetic W1, R1→W1 and C1 packets all
refuse, with the same three reasons:

```
triage packet code_or_config_changed=False contradicts the derived value True
triage packet carries unlisted or arm-computed checks: meter_samples_clock
triage meter_reader_live missing or malformed
```

I then adapted the packet to the v4 head wire by hand: I split the meter check, set
`last_desk_passed_artifact_set_sha256` and dropped the flag. On the v4 head consumer:

| Packet | Admitted |
|---|---|
| honest W1, `quiet_start_state` failing | False |
| same packet, quiet status edited to `pass` | **True** |
| same, plus `record_commit` swapped to an unrelated commit that exists | **True** |
| honest C1 | True |
| C1, eight fabricated 7/7 calibration rows and `next_window_role: test` | **True** |
| C1, `full_desk_gate: deferred` with `last_desk_passed_artifact_set_sha256` taken from the packet | **True** |

## Findings

### HIGH-1: the packet is not bound to the committed record; edited packets arm

- **Packet branch.** `align_v4_session.py:301-326` keeps the packet bytes, their
  SHA-256 and `record_commit`, and `v4_cadence.py:76-170` judges the packet's own
  statuses. Nothing compares the packet with the record, series state or evidence
  it names. `record_sha256`, `series_sha256` and `evidence[]` are informational.
- **v4 head.** `v4_cadence.py:154-155` checks only that `record_commit` exists as a
  commit. `align_v4_session.py:307-321` keeps the file digest. The checks, the
  calibration rows (`calibration_stop` is labelled "derived" but derives from
  packet rows) and `last_desk_passed_artifact_set_sha256` are all packet text.
- **Effect.** Edited packet text with valid statuses is accepted, which is the
  smoke-kit finding. The worst case is a forged `calibration_complete`, which
  enters a test arm before calibration. A wrong desk-passed digest also defers the
  mandatory full desk after a code change.
- **Witnesses** (fail at `f1b90f950`):
  - `test_edited_status_on_a_refusing_packet_refuses`
  - `test_fabricated_calibration_rows_cannot_open_a_test_arm`
- **Fix.** Make the packet a cache, not an authority. The arm calls `build_packet`
  itself on `measurement_root`, using the five identities the packet names
  (`record_commit`/`record_path`/`series_commit`/`series_path`/`pushed_ref`).
  Then either:
  - use the rebuilt packet and ignore the supplied one; or
  - require canonical equality, excluding only `pushed_tip` and `packet_preflight`,
    and refuse with `packet does not match its committed sources`.

  This is cheap and deterministic: `test_w1_record_admits...` already asserts
  `packet == s.build()`. It reads only small committed JSON blobs, and raw captures
  are digest-only locators. The v4 head already requires the record commit in the
  MBP repository. A lead signature would not fix this, because
  `valid_lead_signature` (`align_v4_kit.py:702`) checks the format only.

### HIGH-2: a stale packet arms

- **Packet branch.** `v4_cadence.py:95` checks expiry only
  `if 'valid_until_epoch_s' in packet`. Deleting the key removes the check. The
  builder also omits the key whenever either expiry is not numeric
  (`align_v4_next_arm_packet.py:540-542`).
- **v4 head.** Has no expiry check at all. The quiet-state and live-meter
  observations can be any age, even though both are statements about the machine
  now.
- **Witness:** `test_stale_packet_cannot_drop_its_expiry` (armed at `now=10**9`).
- **Fix.** If the arm rebuilds (HIGH-1), it recomputes `valid_until_epoch_s` from
  the committed observations and compares it with its own clock. Make it mandatory
  and refuse when it is absent. The better fix is in MED-1.

### HIGH-3: the builder cannot integrate with the v4 head consumer

All of these come from the v4 r11 changes made while the builder was being written:

- **(a) Meter check id.** `align_v4_next_arm_packet.py:501` emits
  `meter_samples_clock`. The v4 head refuses it as unlisted and requires
  `meter_reader_live` (gating) plus `meter_coverage` (status `recorded`, non-gating,
  `gaps`) (`v4_cadence.py@2cce80ede:44-49,179-187`). Split `meter()` (`:357-377`):
  - coverage goes into `meter_coverage`, `recorded`, with `gaps`;
  - live samples and clock go into `meter_reader_live`.
- **(b) Change detection.** The builder sets `code_or_config_changed` from its own
  `state_digest` over an exporter-chosen `code_config` list (`:276-282`, `:404`,
  `:407-416`). The v4 head derives "changed" from
  `v4_registration.artifact_set_digest(measurement_root)` and
  `last_desk_passed_artifact_set_sha256`, and refuses a flag that disagrees.
  - The builder never emits that digest, so every packet refuses.
  - The builder must compute it from committed bytes: the same `ARTIFACTS` list,
    read at the last desk-passed record's code commit (`_committed_bytes`, which
    already exists).
  - Drop the exporter-chosen inventory. If its path list is incomplete, a changed
    tree reads as "unchanged".
- **(c) Lead-ruling wire.** The builder copies `{"type":"lead_ruling",...}` rows into
  `calibration_windows` (`:516-518`). The v4 head rejects rows without `window`. It
  requires a separate `lead_rulings` list with
  `{ruling_id, text_sha256, resets: zero_capture_escalation, after_window, lead_signature}`
  (`v4_cadence.py@2cce80ede:227-239`). See MED-4.
- **(d) Consumer signature.** `build_packet` calls
  `next_arm_triage(..., now_epoch_s=...)` (`:543-544`), which the v4 head does not
  accept, so it raises TypeError. Pass `identity`, and move expiry per HIGH-2.
- **(e) Window ids.** The v4 head requires `WINDOW_ID`
  (`^(R1|W1|[CTD][1-9][0-9]*)$`). `WindowRecord` accepts any nonblank string
  (`:139-141`). The doc and test examples `C1-refusal-1`/`-2` are invalid there.
  Validate with `cadence.WINDOW_ID`. This leaves an open protocol question for the
  lead: what id does a zero-capture attempt carry? Ids must be unique, and a `Cn`
  retry would shift the frozen order.
- **(f) Session conflict.** The packet branch's `next_arm_triage_source` (base64
  bytes) conflicts with the v4 head's `packet_file_sha256` + `identity`. Keep the
  v4 head version. Under HIGH-1 the retained bytes matter less, because the rebuilt
  packet is the evidence.
- **(g) Entry count.** There are now 15 entries: 14 gating plus `meter_coverage`.
  Update the docstring/doc "14-entry" text and
  `test_each_of_fourteen_entries...`.
- **Witness:** `test_honest_synthetic_w1_packet_admits_on_the_consumer_in_tree`
  passes at `f1b90f950` and errors on the merge.

### MED-1: quiet_start_state and meter_reader_live inputs are exporter-shaped, not native

- `quiet()` (`:342-355`) and `meter()` (`:368-374`) read `series.quiet` and
  `series.meter_live`. These are free JSON blobs: `cooldown_s`, `display_off_s`,
  `dwell_s`, `active_work`, `sample_count`, `raw_offset_ns`, `observed_at_epoch_s`.
- No native producer of that shape exists in the tree. A search of `joulewise/` and
  `scripts/` found none, and `next_arm_packet.md` says "no automatic export adapter".
- `prepared_at_epoch_s` is a lead-entered time. It acts as "now" for
  `terminal_window_release` (`:325-328`) and for every freshness bound.
- So two of the 14 gating entries can be hand-entered, which item 1 forbids. Both
  are current-hardware states.
- **Fix (proportionate).** Make `quiet_start_state` and `meter_reader_live`
  arm-computed:
  - the arm is on the MBP and can poll the KM003C reader;
  - the arm can read display/idle state and the process census;
  - there is no export lane, no expiry and no packet field for these.
  If they must stay in the packet, name a native producer schema and digest-bind
  its output.

### MED-2: history completeness is lead-asserted

`series.history` (`:510-533`) is a lead-written list. The builder checks that each
record is an ancestor of the previous one and is calibration-role. It cannot detect
an omitted attempt (a counted window or a zero-capture refusal), and an omission
changes `calibration_stop`. Fix: give each record index a `previous_record`
`{commit,path,sha256}` link and have the builder walk that hash chain from the
previous record back to W1, instead of reading a list. Counted calibration ids must
then be C1..Ck in order.

### MED-3: MED-2b only partly honored; a missing meter tabulation still gates

Gaps are non-gating, which is correct. But `:360-361` requires the KM003C report and
an exact roster match before the live check runs, all inside one gating check. A
PILOT without a `km003c` tabulation therefore blocks the next arm, as does a
malformed or partial one. The R1 → W1 case falls here: the doc says R1 needs an
adapter that does not exist yet. MED-2b and the v4 head make coverage non-gating.
The split in HIGH-3(a) fixes this: a missing tabulation becomes a
`meter_coverage` row with status `recorded` and basis "tabulation missing", and
never a refusal.

### MED-4: lead ruling copied verbatim, not derived

- **Packet branch.** The builder copies the ruling row from series history
  (`:516-518`) with nothing behind it.
- **v4 head.** Requires `text_sha256` and `lead_signature`.
- **Fix.** The builder should read the ruling text from a committed blob named in
  the series row (`{ruling_id, after_window, text:{path,sha256}, lead_signature}`),
  compute `text_sha256` from those bytes, and emit the v4 head row into
  `packet['lead_rulings']`. That meets item 1 for this row.
- **Note.** `lead_signature` is a format check, not authentication.
- **Keep.** Keep the v4 head `calibration_stop` semantics. The ruling resets only
  the trailing count after the named window; counts and the fixed-8 cap are
  unchanged; two more zeros escalate again. Both branches already agree on that.

### LOW

- **L1 (`:239-242`).** A benign member of a model whose U1-U3 did not all pass
  counts 0 eligible. Protocol §"U1–U3 failure" (`pilot_protocol_v4.md:501`) bars
  only *held-out pool entry*. That differs from calibration eligibility unless the
  lead rules that they are the same. The rule is conservative, since it cannot
  inflate counts, but it can push the series to `insufficient_calibration`. It
  needs a cited rule or a lead ruling.
- **L2 (`:304-307`).** `pushed_ref` is a local remote-tracking ref, so
  `git update-ref` can create it. This is documented. A cheap fix: the arm checks
  `git ls-remote` for the records branch on the MBP by day, or a by-day fetch
  receipt.
- **L3.** If the arm imports the builder (HIGH-1), the builder joins the executed
  closure. Add it to `v4_registration.EXECUTED_CLOSURE` / `ARTIFACTS` before the
  receipt is generated. That avoids a later re-registration, the cost MED-1 of the
  Opus cold review warned about.
- **L4 (blinding: passes).** The packet copies capture metadata for each member,
  including sabotage members: `flags`, `coverage`, `calibration_exclusions`,
  `pm_period_s`, `pm_max_gap_s` and `turn_observation`. `turn_observation` holds
  thermal-state booleans and the gap per turn (`thermal_desk.py:224`). There is no
  energy, residual or score. Token ids are compared and never emitted. The sealed
  KM003C rows of the v4 head keep `status`/`flags`, which is all the builder reads.

## The six checks

| Check | Result |
|---|---|
| 1. All entries computed from authoritative source | **Partly.** These come from committed record blobs: record_committed, terminal_completion, capture_faults, thermal_escalation, cohort_pool_rules, sentinel_roster, member_eligibility, full_desk_gate and the calibration counts. The counts are taken from roster, captures, thermal PILOT and final exclusions, and series assertions are ignored (tested). The three ARM entries are left to the arm. **Exceptions:** quiet and meter-live (MED-1), the code/config inventory (HIGH-3b), the history list (MED-2) and the ruling row (MED-4). |
| 2. Bound to committed record digest; stale/edited refuses | **Fails** on both consumers (HIGH-1, HIGH-2). |
| 3. Raw evidence digests included | **Met.** `evidence[]` holds commit, path, sha256 and bytes for every blob read. Custody locators are kept as `committed_digest_inventory_only` and never opened (tested). |
| 4. Zero-capture rule and lead_ruling rows | **Rule met.** Zero capture is not counted, carries zero eligible, and two in a row escalate. **Wire incompatible** with the v4 head (HIGH-3c, HIGH-3e, MED-4). |
| 5. Synthetic W1 admits; each entry refuses with documented reason | **Met at `f1b90f950`** (19/19). **Not met on the v4 head**: nothing admits (HIGH-3). |
| 6. Opus cold MED-2a / MED-2b | **2a:** semantics agree, but the wire differs; adopt the v4 head's signed `lead_rulings` list. **2b:** gaps are non-gating, but tabulation presence still gates (MED-3). |

## What must change to integrate with the v4 head (in order)

1. Rebase the builder onto `align/2026-11-08-v4-r11` and drop the packet branch's
   edits to `v4_cadence.py`, `align_v4_session.py` and the protocol table. The v4
   head consumer is the one of record.
2. Split the meter check (HIGH-3a, MED-3).
3. Emit `last_desk_passed_artifact_set_sha256`, computed with the
   `ARTIFACTS`/`artifact_set_digest` rule from committed bytes at the last
   desk-passed state. Drop `code_config` as a state identity (HIGH-3b).
4. Emit `lead_rulings` in the v4 head shape, with `text_sha256` computed from a
   committed ruling text (HIGH-3c, MED-4). Validate window ids with `WINDOW_ID`
   (HIGH-3e).
5. Call `next_arm_triage(packet, internal, identity)` for the preflight (HIGH-3d).
6. Bind the packet in the arm: rebuild and compare, or rebuild and use (HIGH-1).
   Expiry becomes mandatory or moves to the arm (HIGH-2, MED-1). Register the
   builder in the executed closure before the receipt (L3).
7. Make the four witnesses in `tests/align/test_v4_next_arm_packet_opus_witnesses.py`
   pass, and update the "14" text and test names (HIGH-3g).

Steps 2-5 are mechanical, about 60 lines in the builder. Step 6 is the substantive
one, about 20 lines in `arm_checks`, and it touches receipt-bound files, so land it
before the registration receipt is generated.
