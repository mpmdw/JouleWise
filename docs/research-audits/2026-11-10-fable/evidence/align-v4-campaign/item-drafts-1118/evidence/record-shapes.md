# Draft gate inputs; no live record or issue authority

These are builder-defined inputs to the draft's executable checks, implementing the cited rulings. The lead owns their content, pointers and admission; a literal placeholder, a mock receipt or a builder PASS never supplies it. Fill quoted `<LEAD FILLS: ...>` assignments inside each item only when issuing. The magistrate supplies fresh operational observations for both Start and Run, from the lead's current issued items/records and native readbacks. Do not reuse a cached eligibility answer. All external paths below are instructions for a later authorized magistrate, never paths opened by this builder.

| Input | Required observation / owner / authority |
|---|---|
| ISSUED_EPOCH; WATCH_UNTIL_EPOCH | Lead: actual issue stamp; hand watcher observation +86400, re-read every arm; RL-173 D.5/C.5. An Actions watcher needs a new C.4 read path, not this stamp. |
| FREEZE2_COMMIT / COEF_PATH / COEF_SHA256 | Lead: full 40-char commit and 64-char hash of the coefficient file. Commit ancestor of fetched audit or main, contains exact hash. Coefficient contents are never printed. RL-165 §8.1; RL-173 E. |
| COLD_SEAT_RECORD; QUAL_COLD_SEAT=ADMIT; COLD_SEAT_KIT_SHA | Lead records cold-seat pointer per kit and exact kit hash; not the builder re-check. RL-149 §2.8 line 1 / RL-165 §8.1. |
| FIRST_CAPTURE_CONFIRMED=yes | Cold seat's RL-167 Part B Q2 finding: own-shaped first G0 equals capture code; five consumers read it. |
| LINE2_RECORD; LINE2_EQUAL=yes; LINE2_PIN; LINE2_BASE | Lead: full-suite frozen-byte equality and final red-set comparison test for test; pin=e1b85a59c..., base=c3f4bacd8... (the W1-line commit actually merged). RL-165 §8.1. |
| HOST_EVENT_RECORD; HOST_EVENT_DISPOSITION | Lead: readback of RL-174 C’s four lines, with done / waived / deferred describing the historical attempt. No new hygiene action, restart or visit is a gate. An unplanned restart is recorded and the next arm refreshes the lines. |
| HOST_STATE_ID; FREEZE2_HOST_STATE_ID; CURRENT_HOST_STATE_ID | Lead records the hygiene settings at freeze 2; magistrate confirms them. The identity excludes boot time: RL-174 C permits an unplanned restart with an event and fresh four lines, without a restart hold. No hygiene setting changes through qual-03 close. |
| INCLUSION_RECORD; QUAL_INCLUSION_UNCHANGED=yes | Filled by RL-174 B.5 at `ebff15ad27e831499dd65796b3727d8c5d451e21`: six rules unchanged, overlaps print-only. By-job counts through dev-05 are appended after desk-final and gate nothing. A changed rule is outside this draft. |
| QUEUE_COMMIT | Lead records authenticated audit commit containing the exact queue bytes. Gate binds hash/roster, ancestor, finite expiry and ≤7 days from that commit. The supplied queue expires Nov23 00:00 PST, conservative for a Nov16 commit. No `next` command grants new authority. |
| LINE6_RECORD; STOPS_CLEAR=yes | Lead: all applicable stops disposed under RL-149 §2.4/§2.8 line 6. Re-read before launch. |
| VETO_RECORD; VETO_CLEAR=yes | Magistrate: current halt/veto and directive-notice read, not an old no-veto answer. RL-149 §2.8 lines 5/6. |
| CHECKLIST_RECORD; CHECKLIST_OK=yes; CHECKLIST_OBSERVATIONS | Magistrate: every native kit checklist line and measurement_mode exception checked, record path and fresh observations JSON; pinned `checklist` executes in Start and Run. Native failure stops regardless of a prior yes. |
| PILOT_PASSED=yes | Lead: development pilot gate already passed under RL-149 §2.8 line 8; class B qualification has no class A smoke. |
| SAMPLE_HAND_RECORD; SAMPLE_HAND_CLEAR=yes | Lead: RL-172 (c)/RL-173 E sampled hand table completed where due; disagreement holds the next arm. |
| COPY_KEY_SAFE=yes; OFFLOAD_CLEAR=yes | Lead: encryption key in a second off-MBP place; no failed/unverified offload. Gate requires the campaign marker or an exact latest non-campaign Check/copy proof. RL-173 A. |
| HOST_RESTORE_OK=1; GROUPS_ABSENT=1 | Magistrate: latest close's complete Check proved every restore line and child-process-group absence. RL-171 §6.1; RL-149 §2.4. |
| PRIOR_CLOSE_EPOCH; OTHER_CLOSE_EPOCH; LAST_CLOSE_KIND | Magistrate: epochs rounded up; PRIOR ≥ named predecessor close; OTHER explicit 0 if none outside receipt roots. LAST_CLOSE_KIND=campaign (300 s) or other (1200 s); F0/F2/non-campaign always other. |
| NONCAMPAIGN_COPY_OK=yes; NONCAMPAIGN_COPY_RECEIPT; NONCAMPAIGN_COPY_CLOSE_EPOCH; NONCAMPAIGN_COPY_RECORD | Latest non-campaign Check proves copy complete, bound to exact EFF_PATH and EFF_EPOCH from the latest-close census (or OTHER). No fixed F0 marker is assumed or created. A prior F0 run's proof cannot satisfy a later receipt. RL-171 §6.1; RL-173 A. |
| SESSION_READY; SESSION_RECORD | Lead's current READY census record pointer and yes/no. yes immediately cedes; unknown holds. RL-172 (f). |
| QUAL01_SOAK_HAND_READ=SAME; QUAL01_SOAK_RECORD | Lead: first qualification soak's fields/reference schema hand-compared to dev-05; required before any later span in these conservative drafts. Difference goes to research lead. RL-172a F1. |
| LINE9_RECORD | Lead: path to the typed debt record below, updated in actual machine order, across every campaign queue; F0/F2/Part C/v4 excluded. RL-165 §6; RL-172 (c); RL-173 E Q1. |

The typed debt file is a lead-produced **operational record**, not a new repository schema or a substitute for authentication. Include the full machine-order census up to the named predecessor. For every entry through k−2, `desk_final_record` points to the authenticated final table with exact leg order/count/attempt/kit/plan/reference identity, no missing/duplicate record and no empty table. Each v1.1 entry through k−2 also needs the separate typed `q1_complete_record`. RL-174 E.5 additionally names dev-05-s01’s desk-final/Q1 records for qual-01-s01 and dev-05-s02’s for qual-01-s02; an omitted named row cannot pass. The immediate predecessor's clean close is a separate gate; its desk/Q1 may remain pending until k+2. Example shape (unfilled, not usable):

```json
{
  "next_span": "qual-01-s01",
  "authenticated_roster_identity_checks": "RL-172 (c)",
  "machine_order": [
    {"span_id": "<LEAD FILLS: every prior campaign span in order>", "runner_kind": "cadence-legs-v1", "desk_final_record": "<LEAD FILLS: authenticated FINAL pointer>"},
    {"span_id": "dev-05-s01", "runner_kind": "cadence-legs-v1.1", "desk_final_record": "<LEAD FILLS: FINAL>", "q1_complete_record": "<LEAD FILLS: typed Q1 completion>"},
    {"span_id": "dev-05-s02", "runner_kind": "cadence-legs-v1.1"}
  ]
}
```

The current kit's native observation JSON uses the pinned validator's existing keys: `measurement_head`, `frozen_path_sha256`, `kit_sha256`, `ac_power`, `powermode`, `network_time`, `freq_word`, `stray_monitors`, `other_agents`, `night_labels_loaded`, `high_power_marker`, `sudo_kill_rc`, `km003c_ready`, `disk_free_gb`, `previous_span`, `halts`, `t0_epoch_s`, `end_by_epoch_s`. Populate from actual readbacks; no synthetic template is an arm record. RL-167 Part B Q8 requires the observed HEAD beside the kit's frozen.commit. All six caps are listed by item; its one short leg is intentional (Q6).
