# Draft gate inputs; no live record or issue authority

These are builder-defined inputs to the draft's executable checks, implementing the cited rulings. The lead owns their content, pointers and admission; a literal placeholder, a mock receipt or a builder PASS never supplies it. Fill quoted `<LEAD FILLS: ...>` assignments inside each item only when issuing. The magistrate supplies fresh operational observations for both Start and Run, from the lead's current issued items/records and native readbacks. Do not reuse a cached eligibility answer. All external paths below are instructions for a later authorized magistrate, never paths opened by this builder.

| Input | Required observation / owner / authority |
|---|---|
| ISSUED_EPOCH | Lead: actual issue epoch, used as the earliest authorized t0. |
| FREEZE2_COMMIT / COEF_PATH / COEF_SHA256 | Lead: full 40-char commit and 64-char hash of the coefficient file. Commit ancestor of fetched audit or main, contains exact hash. Coefficient contents are never printed. RL-165 §8.1; RL-173 E. |
| COLD_SEAT_RECORD; QUAL_COLD_SEAT=ADMIT; COLD_SEAT_KIT_SHA | Lead records cold-seat pointer per kit and exact kit hash; not the builder re-check. RL-149 §2.8 line 1 / RL-165 §8.1. |
| FIRST_CAPTURE_CONFIRMED=yes | Cold seat's RL-167 Part B Q2 finding: own-shaped first G0 equals capture code; five consumers read it. |
| LINE2_RECORD; LINE2_EQUAL=yes; LINE2_PIN; LINE2_BASE | Lead: full-suite frozen-byte equality and final red-set comparison test for test; pin=`6e9d42f1dd3d308bc9239143d0d634ab965e50e1`, base=c3f4bacd8... (the W1-line commit actually merged). RL-165 §8.1. |
| HOST_EVENT_RECORD; HOST_EVENT_DISPOSITION | Lead: readback of RL-174 C’s four lines, with done / waived / deferred describing the historical attempt. No new hygiene action, restart or visit is a gate. An unplanned restart is recorded and the next arm refreshes the lines. |
| HOST_STATE_ID; FREEZE2_HOST_STATE_ID; CURRENT_HOST_STATE_ID | Lead records the hygiene settings at freeze 2; magistrate confirms them. The identity excludes boot time: RL-174 C permits an unplanned restart with an event and fresh four lines, without a restart hold. No hygiene setting changes through qual-03 close. |
| INCLUSION_RECORD; QUAL_INCLUSION_UNCHANGED=yes | Filled by RL-174 B.5 at `ebff15ad27e831499dd65796b3727d8c5d451e21`: six rules unchanged, overlaps print-only. By-job counts through dev-05 are appended after desk-final and gate nothing. A changed rule is outside this draft. |
| QUEUE_COMMIT | Lead records authenticated audit commit containing the exact queue bytes. Gate binds hash, roster, kit, attempt 1, span date, ancestor and the queue’s finite expiry. The default queue expires Nov23 00:00 PST. |
| QUAL_DATES | Six span-to-local-date entries. Every recorded qualification t0 must match its own entry. On recovery, preserve s01's date, re-date missing s02 and move later untouched blocks whole. |
| BATCH OK / RL-175 C.4 | Record fresh boot and predicted batch epochs, planned soak end, expected close and both bounds from Start and Run. A held arm waits until batch start plus 27 minutes. Run hands the bounds and sleep-inclusive clock anchor to the child. Its receipt carries `started.epoch_ns`, `started.continuous_ns` and the date and bounds in `t0_authority`. |
| LINE6_RECORD; STOPS_CLEAR=yes | Lead: all applicable stops disposed under RL-149 §2.4/§2.8 line 6. Re-read before launch. |
| VETO_RECORD; VETO_CLEAR=yes | Magistrate: current halt/veto and directive-notice read, not an old no-veto answer. RL-149 §2.8 lines 5/6. |
| CHECKLIST_RECORD; CHECKLIST_OK=yes; CHECKLIST_OBSERVATIONS | Magistrate: every native kit checklist line and measurement_mode exception checked, record path and fresh observations JSON; pinned `checklist` executes in Start and Run. Native failure stops regardless of a prior yes. |
| PILOT_PASSED=yes | Lead: development pilot gate already passed under RL-149 §2.8 line 8; class B qualification has no class A smoke. |
| SAMPLE_HAND_RECORD; SAMPLE_HAND_CLEAR=yes | Lead: RL-172 (c)/RL-173 E sampled hand table completed where due; a disagreement holds the affected kit (RL-179 F-3). |
| COPY_KEY_SAFE=yes; OFFLOAD_CLEAR=yes | Lead: encryption key in a second off-MBP place; no failed/unverified offload. Gate requires the campaign marker or an exact latest non-campaign Check/copy proof. RL-173 A. |
| ATTEMPT_LEDGER | Lead supplies the complete host launch/start-plan ledger described below. Include launches outside these items and attempts without a receipt. |
| CLOSE_PROOF_RECEIPT; HOST_RESTORE_OK=1; FEEDS_STOPPED=1; GROUPS_ABSENT=1; FOREIGN_PROCESSES_ABSENT=1 | The magistrate binds the Check's shutdown evidence to the selected attempt's own receipt. The gate also checks the restore result in that receipt. |
| LAST_CLOSE_KIND | Campaign or other, according to the selected receipt. |
| NONCAMPAIGN_COPY_OK=yes; NONCAMPAIGN_COPY_RECEIPT; NONCAMPAIGN_COPY_CLOSE_NS; NONCAMPAIGN_COPY_RECORD | The non-campaign Check binds copy proof to the exact selected receipt path and close epoch in nanoseconds. RL-173 A. |
| SESSION_READY; SESSION_RECORD | Lead's current READY census record pointer and yes/no. yes immediately cedes; unknown holds. RL-172 (f). |
| Registered `lm-qual-01` manifest and ledger row | Lead confirms both on main with the exact qualification kit hashes before qual-01-s01 arms (RL-181 §1.0). |
| QUAL01_SOAK_HAND_READ=SAME; QUAL01_SOAK_RECORD | Before qual-01-s02, record the comparison of soak fields and reference schema with dev-05. The first same-pin filler hand-read may supply it. A difference goes to the research lead (RL-172a F1; RL-181 §4(a)). |
| QUAL01_TYPES_HAND_READ=PASS; QUAL01_TYPES_HAND_RECORD | Before qual-01-s02, record the RL-181 §4(a) hand-read covering capture G0, each consumer’s release and wait, and each decode count against its cap. Name qual-01-s01 or the earlier passing q0 capture-and-consumer filler or pilot, and bind the record to the exact pin. If it has not passed by s02’s latest t0, re-date under RL-175 C.3. |

Seed the operational attempt ledger's JSON `attempts` list in actual launch
order starting with `sequence: 1`. Every row carries a unique positive integer
`sequence`, the `span_id`, and an absolute `close_receipt` path unique to
that attempt. Include starts outside these items and attempts without receipts.
All writers use the shared desk fence lock. The launcher selects the highest
sequence and publishes the next row before bootstrap, even if bootstrap
later fails.

Before qual-01-s01, the lead supplies the latest pre-qualification attempt's
**identity-bound close Check**, for dev-05-s02 or for a more recent filler on
an older pin. Its older runner receipt lacks `span_id`, which the pinned
`close-proof` command requires. Preserve the original receipt and point that
attempt's ledger row to the close Check. It carries the row's exact `span_id`,
the observed `ended.epoch_ns` (or exact nanosecond-representable `ended.epoch_s`),
and a nonempty `restore_readbacks` object with each named restore result set
to true after verification. Keep the source attempt identity with the Check.
Keep newly written Checks outside immutable run bundles. The gate uses
`LAST_CLOSE_KIND=other` for a Check staged outside a recognized campaign
output. Supply the separate copy proof with the exact Check path and close
stamp and retain the original attempt’s copy evidence. An existing Check
at a recognized campaign output path uses the verified campaign copy marker.
New qualification runner receipts carry their own span id and passing
restore step.

**rc 3 recovery.** The child refuses before creating the output directory or
a runner receipt. The published ledger row still blocks every successor.
The lead verifies the refusal and that the fence is gone, restore is proven,
feeds are stopped and the process group and foreign processes are absent.
Write the identity-bound close Check above outside the counted-output census,
keep the original reserved output identity with the Check, and bind only
that row's `close_receipt` to the Check under the shared desk fence lock.
Keep the row and its sequence. Supply the separate copy proof with that exact
Check path and epoch. Re-run `close-proof` before the next arm. A new attempt
still needs lead authority under the applicable stop, date and predecessor rules.

The current kit's native observation JSON uses the pinned validator's existing keys: `measurement_head`, `frozen_path_sha256`, `kit_sha256`, `ac_power`, `powermode`, `network_time`, `freq_word`, `stray_monitors`, `other_agents`, `night_labels_loaded`, `high_power_marker`, `sudo_kill_rc`, `km003c_ready`, `disk_free_gb`, `previous_span`, `halts`, `t0_epoch_s`, `end_by_epoch_s`. Populate from actual readbacks; no synthetic template is an arm record. RL-167 Part B Q8 requires the observed HEAD beside the kit's frozen.commit. All six caps are listed by item; its one short leg is intentional (Q6).
