# Cadence sub-span dev-01-s03 (L004-L007): magistrate check, activation b418e121

Magistrate b418e121 (headless, Opus 5.5), 2026-11-14 21:02-21:10 PST. Runs RUN_STATE item 321's "Check" on the span launched by e4e64e98 (item 323). Reports; decides nothing.

- OUT `/Users/edr/campaign-out/cl-dev-01/cq-dev-01-s03-a1-20261115T030242Z`; head `b4b6aeb19`; kit sha `c76344c5…66d7`; launcher rc 0 (custody `cadence-dev01-s03-out-e4e64e98.txt`).
- SPAN `dev-01-s03`, LEGS `L004,L005,L006,L007`.
- Span: receipt `started` 19:03:13 PST, `ended` 21:01:49 PST (7,116 s; plan expected 8,154 s, worst 19,350 s). `runner_receipt.json` mtime 1794718908 (21:01:48 PST). Fence gone; no `align-r0` label loaded.
- Blinding: only `runner_receipt.json`, `desk-bundle/`, `soak/soak_reference.json`, the soak sensors journal, each leg's `leg_record.json`, `outputs/align_window_reference.json` and `outputs/align_thermal.jsonl` were opened, by the two item-321 scripts verbatim. No energy, power, meter-stream, hazards or episode file was opened.

## Receipt (script 1: all asserts passed)

```
{"batch_windows": ["02:00-02:35"], "error": null, "legs_finished": 4, "legs_planned": 4, "load_redos_used": 0, "meter": {"bad_polls": 0, "elapsed_s": 7114.81260675, "polls": 35574, "present": true, "proven_stopped": true, "usb_errors": 0}, "rc": 0, "roster": ["L004", "L005", "L006", "L007"], "runner_kind": "cadence-legs-v1", "span_result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "4/4 legs run"}}
[('deadline', 0), ('frozen', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('plan', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-L004-volumes', 0), ('L004.a1', 0), ('before-L005-volumes', 0), ('L005.a1', 0), ('before-L006-volumes', 0), ('L006.a1', 0), ('before-L007-volumes', 0), ('L007.a1', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
L004 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794715142.7890959, "g0_outcome": "released", "g0_s": 201.896139417, "leg_id": "L004", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 3703962298, "start_band": "q0", "started_epoch_s": 1794713897.077899, "wall_s": 1245.7107949256897}
L005 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794716396.561687, "g0_outcome": "released", "g0_s": 209.014619062, "leg_id": "L005", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 786901938, "start_band": "q0", "started_epoch_s": 1794715143.451694, "wall_s": 1253.109589099884}
L006 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794717649.131453, "g0_outcome": "released", "g0_s": 210.104579541, "leg_id": "L006", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 2578335113, "start_band": "q0", "started_epoch_s": 1794716397.2151308, "wall_s": 1251.9158482551575}
L007 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794718894.0626729, "g0_outcome": "released", "g0_s": 199.980166334, "leg_id": "L007", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 395415709, "start_band": "q0", "started_epoch_s": 1794717649.782642, "wall_s": 1244.2795362472534}
result {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "4/4 legs run"}
meter {"bad_polls": 0, "elapsed_s": 7114.81260675, "polls": 35574, "present": true, "proven_stopped": true, "usb_errors": 0}
RECEIPT OK
```

## Legs

- Run 4 of 4; admitted 4 of 4 (L004, L005, L006, L007), each `admitted: true`, one attempt, G0 released (199.98-210.10 s), band q0 reached, no redo, no contaminated redo.
- Excluded legs: none.
- Named stops: none visible to the magistrate (`fault` false, `error` null, no redo, no G0 timeout, no leg over its 1,251 s budget by more than 2.1 s: L005 wall 1,253.1 s). The Air desk's `stops.json` is the authority.
- Every leg prints `pm_nominal: false` and `os_level_max: 2`, as the pilot's did; reported as printed.

## RL-150 R1 part 3 print (script 2, as printed; gates nothing)

```
soak_reference {'TV0h': 34.15706272761027, 'TV1h': 34.15706272761027} Tf08_last1200s_mean 27.02586380004883
L004 {"g0": {"duration_s": 201.896139417, "outcome": "released", "release": {"TV0h": 34.861328125, "TV1h": 34.861328125, "Tf08": 34.55437469482422}, "row_reference": {"fast_c": 34.171775817871094, "slow_c": 34.171775817871094, "source_member": "cadence-cl-dev-01-l004", "span_ns": [2698587653446896, 2698647653446896]}, "row_release": {"fast_c": 34.861328125, "slow_c": 34.861328125}}, "own_reference": {"TV0h": 34.171775817871094, "TV1h": 34.171775817871094, "Tf08_median": 27.278124809265137, "status": "captured"}}
L005 {"g0": {"duration_s": 209.014619062, "outcome": "released", "release": {"TV0h": 35.0515251159668, "TV1h": 35.0515251159668, "Tf08": 36.571876525878906}, "row_reference": {"fast_c": 34.72988319396973, "slow_c": 34.72988319396973, "source_member": "cadence-cl-dev-01-l005", "span_ns": [2699833562263645, 2699893562263645]}, "row_release": {"fast_c": 35.0515251159668, "slow_c": 35.0515251159668}}, "own_reference": {"TV0h": 34.72988319396973, "TV1h": 34.72988319396973, "Tf08_median": 32.98921775817871, "status": "captured"}}
L006 {"g0": {"duration_s": 210.104579541, "outcome": "released", "release": {"TV0h": 35.06169128417969, "TV1h": 35.06169128417969, "Tf08": 36.39125061035156}, "row_reference": {"fast_c": 34.76690673828125, "slow_c": 34.76690673828125, "source_member": "cadence-cl-dev-01-l006", "span_ns": [2701086705660749, 2701146705660749]}, "row_release": {"fast_c": 35.06169128417969, "slow_c": 35.06169128417969}}, "own_reference": {"TV0h": 34.76690673828125, "TV1h": 34.76690673828125, "Tf08_median": 33.326717376708984, "status": "captured"}}
L007 {"g0": {"duration_s": 199.980166334, "outcome": "released", "release": {"TV0h": 35.10929870605469, "TV1h": 35.10929870605469, "Tf08": 36.959373474121094}, "row_reference": {"fast_c": 34.713884353637695, "slow_c": 34.713884353637695, "source_member": "cadence-cl-dev-01-l007", "span_ns": [2702338988285333, 2702398988285333]}, "row_release": {"fast_c": 35.10929870605469, "slow_c": 35.10929870605469}}, "own_reference": {"TV0h": 34.713884353637695, "TV1h": 34.713884353637695, "Tf08_median": 32.775779724121094, "status": "captured"}}
```

## Restore lines (21:03 PST)

- Runner close steps: `restore` 0, `stop-volumes` 0, `stop-meter` 0, `stop-agents` 0, `close-volumes` 0.
- No `desk_fence.json`; `com.joulewise.align-r0` labels loaded: 0; no `com.joulewise.night*` label or plist.
- powermode 0; Network Time Off; kernel frequency word 0 (measurement_mode PASS line); no High Power marker; no stray monitor; no root powermetrics.
- measurement_mode verify rc 1: one FAIL, `agent process present: 30959;30955 …codex-mcp-server.mjs;30956 …server-pdf`. All three PIDs are this magistrate's own tree (30940 → 30955 node → 30958 node → 30959 codex; 30940 → 30956), so NOTE 1 applies. WARN lines: battery charge limit (want 80, got none); softwareupdate schedule (want off, got on). All other lines PASS or SKIP.
- No "restore unproven" and no host-state stop.
- 00:00: the span ran 19:03-21:01 PST and did not cross local midnight.

## Housekeeping

- Canonical root fast-forwarded `065bed242` → `1e753e327` (docs only) after confirming no night label or plist. The canonical `git fetch` ran before the pointer was read (slip, as e4e64e98 noted; nothing armed, no fence, harmless).
- No unread owner mail; no open STOP/NO/HALT/VETO directive; no open `cadence-stop` issue.
- Nothing re-run, nothing queued from this span. Next for this span: the lead copies the desk bundle to the Air, builds the automatic desk table, and issues the s04 item for Sun 02:40 with RAN = `dev-01-s03` (item 321 "After").
