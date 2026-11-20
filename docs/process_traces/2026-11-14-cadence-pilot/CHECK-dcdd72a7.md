# Cadence pilot cl-dev-01 (L001-L003): magistrate check, activation dcdd72a7

Magistrate dcdd72a7 (headless, Opus 5.5), 2026-11-14 16:27-16:35 PST. Runs RUN_STATE item 317's "Check" on the span launched by 7745bc38. Reports; decides nothing.

- OUT `/Users/edr/campaign-out/cl-dev-01/cq-dev-01-s01-a1-20261114T224427Z`; head `b4b6aeb19`; kit sha `c76344c5…66d7`; launcher rc 0 (custody `cadence-pilot-out-7745bc38.txt`).
- Span: receipt `started` 14:44:43 PST, `ended` 16:22:39 PST (5,876 s; plan expected 6,903 s, worst 16,650 s). Fence gone; watchdog FENCED → LAUNCHING at 16:26:47.
- Blinding: only `runner_receipt.json`, `desk-bundle/`, `soak/soak_reference.json`, the soak sensors journal, each leg's `leg_record.json`, `outputs/align_window_reference.json` and `outputs/align_thermal.jsonl` were opened, by the two item-317 scripts verbatim. No energy, power, meter-stream, hazards or episode file was opened.

## Receipt (script 1: all asserts passed)

```
{"batch_windows": ["02:00-02:35"], "error": null, "legs_finished": 3, "legs_planned": 3, "load_redos_used": 0, "meter": {"bad_polls": 0, "elapsed_s": 5875.013382125, "polls": 29375, "present": true, "proven_stopped": true, "usb_errors": 0}, "rc": 0, "roster": ["L001", "L002", "L003"], "runner_kind": "cadence-legs-v1", "span_result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "3/3 legs run"}}
[('deadline', 0), ('frozen', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('plan', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-L001-volumes', 0), ('L001.a1', 0), ('before-L002-volumes', 0), ('L002.a1', 0), ('before-L003-volumes', 0), ('L003.a1', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
L001 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794699638.807987, "g0_outcome": "released", "g0_s": 205.933801041, "leg_id": "L001", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 2746676187, "start_band": "q0", "started_epoch_s": 1794698387.341322, "wall_s": 1251.466147184372}
L002 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794700892.708166, "g0_outcome": "released", "g0_s": 210.21839423, "leg_id": "L002", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 1842278611, "start_band": "q0", "started_epoch_s": 1794699639.472996, "wall_s": 1253.2347531318665}
L003 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794702144.7276502, "g0_outcome": "released", "g0_s": 205.06245075, "leg_id": "L003", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 2298666168, "start_band": "q0", "started_epoch_s": 1794700893.366057, "wall_s": 1251.361170053482}
result {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "3/3 legs run"}
meter {"bad_polls": 0, "elapsed_s": 5875.013382125, "polls": 29375, "present": true, "proven_stopped": true, "usb_errors": 0}
RECEIPT OK
```

Receipt `mock` is `false`. Every leg prints `pm_nominal: false` and `os_level_max: 2`; recorded as printed, for the lead's hand-read.

## RL-150 R9

1. Three closes with complete records: yes (`legs_finished` 3, every step rc 0, desk bundle has exactly the five expected files, every non-meter feed file re-hashed equal).
2. Admitted: 3 of 3 (L001, L002, L003).
3. Excluded legs: none.
4. Left to the lead's hand-read of the journal table beside the Air desk. No named stop is visible to the magistrate (`fault` false, no redo, no G0 timeout); the Air desk's `stops.json` is the authority.

## RL-150 R1 part 3 print (script 2, as printed; gates nothing)

```
soak_reference {'TV0h': 34.05124227887487, 'TV1h': 34.05124227887487} Tf08_last1200s_mean 25.847349047760087
L001 {"g0": {"duration_s": 205.933801041, "outcome": "released", "release": {"TV0h": 34.82252502441406, "TV1h": 34.82252502441406, "Tf08": 34.18937683105469}, "row_reference": {"fast_c": 34.10357093811035, "slow_c": 34.10357093811035, "source_member": "cadence-cl-dev-01-l001", "span_ns": [2683081786161312, 2683141786161312]}, "row_release": {"fast_c": 34.82252502441406, "slow_c": 34.82252502441406}}, "own_reference": {"TV0h": 34.10357093811035, "TV1h": 34.10357093811035, "Tf08_median": 26.479687690734863, "status": "captured"}}
L002 {"g0": {"duration_s": 210.21839423, "outcome": "released", "release": {"TV0h": 35.01938247680664, "TV1h": 35.01938247680664, "Tf08": 36.19187545776367}, "row_reference": {"fast_c": 34.71154022216797, "slow_c": 34.71154022216797, "source_member": "cadence-cl-dev-01-l002", "span_ns": [2684329530663084, 2684389530663084]}, "row_release": {"fast_c": 35.01938247680664, "slow_c": 35.01938247680664}}, "own_reference": {"TV0h": 34.71154022216797, "TV1h": 34.71154022216797, "Tf08_median": 32.775625228881836, "status": "captured"}}
L003 {"g0": {"duration_s": 205.06245075, "outcome": "released", "release": {"TV0h": 35.08877944946289, "TV1h": 35.08877944946289, "Tf08": 36.685935974121094}, "row_reference": {"fast_c": 34.70344543457031, "slow_c": 34.70344543457031, "source_member": "cadence-cl-dev-01-l003", "span_ns": [2685584232557624, 2685644232557624]}, "row_release": {"fast_c": 35.08877944946289, "slow_c": 35.08877944946289}}, "own_reference": {"TV0h": 34.70344543457031, "TV1h": 34.70344543457031, "Tf08_median": 32.65953063964844, "status": "captured"}}
```

## Restore lines (16:27 PST)

- Runner close steps: `restore` 0, `stop-volumes` 0, `stop-meter` 0, `stop-agents` 0, `close-volumes` 0.
- No `desk_fence.json`; `com.joulewise.align-r0` labels loaded: 0; no `com.joulewise.night*` label or plist.
- powermode 0; Network Time Off; kernel frequency word 0 (measurement_mode PASS line); no High Power marker; no stray monitor; no root powermetrics.
- measurement_mode verify rc 1: one FAIL, `agent process present: 85597;85593 …codex-mcp-server.mjs;85594 …server-pdf`. All three PIDs are this magistrate's own tree (85578 → 85593 node → 85596 node → 85597 codex; 85578 → 85594), so NOTE 1 applies. WARN lines: battery charge limit (want 80, got none); softwareupdate schedule (want off, got on). All other lines PASS or SKIP.
- 00:00: the span ran 14:44-16:22 PST and did not cross local midnight (it crossed 00:00 UTC).

## Housekeeping

- Canonical root fast-forwarded `b07a18779` → `29d5b19b3` (only `scripts/air/night_results_watch.py` changed under code paths) after confirming no night label or plist.
- No unread owner mail; no open STOP/NO/HALT/VETO directive; no open `cadence-stop` issue.
- Nothing re-run, nothing queued, nothing armed. Next: the lead's desk hand-read and R9 verdict (item 317 "After").
