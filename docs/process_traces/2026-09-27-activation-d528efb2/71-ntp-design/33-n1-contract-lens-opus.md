LENS: FINDINGS

# Contract lens, seat N1 (NTP-ENFORCE-DESIGN-01), candidate e7371399

Reviewer: Opus 5.5, fresh contract lens. Candidate worktree `/Users/edr/code/JouleWise-wt-ntp-n1suite-d528efb2`, detached at e7371399. Diff reviewed: `git diff 9eab16f8 e7371399 -- joulewise scripts tests`.
Spec: ruling `71-ntp-design/21-coldgate-fable-ruling.md` §3, §4, §5, §6.3 N1, §6.5, §8; addendum A3 `40-sci-a2-network-time/31-addendum-ruling.md` §4.4–4.6.
I made no repository writes, ran no git write, no sudo, no systemsetup, no capture, and no battery read. Every test and probe ran under a subprocess guard that blocks the real `/usr/bin/sudo`, `/usr/sbin/systemsetup`, `/usr/bin/powermetrics` and `/usr/bin/log show`. The guard's call log is empty for every run cited as passing. HOME was a scratch directory, so the marker could never land in the real `~/Library`. Scratch and outputs are in `/tmp/ntp-n1contract/`.

## BLOCKER

### B1. On real `log show` output the parser marks the run invalid, so every capture would be `network_time_unattested`
- **Where:** `joulewise/network_time_window.py:194` (`elif line[:1].isspace() and parent is not None`). Any line that neither parses as a timestamp nor starts with whitespace sets `valid=False`.
- **What the contract says:** ruling §3.4 condition (d) and X3. A continuation line is any line without its own timestamp that follows a timestamped line. Nothing in the ruling requires leading whitespace.
- **Evidence (executed):** I fed the parser the cold judge's real query output, `/tmp/cg-ntpd-d528efb2/q2_utc.txt` (network time ON, 90 minutes, 226 lines). Result: `header=True parsed_valid=False`. Four lines cannot be placed (112, 152, 192, 226). Each is `}`, the closing brace of a multi-line `TMSetAuthenticatedSourceTime` dictionary that `timed` logs. I then ran the whole path end to end (`/tmp/ntp-n1contract/probe_real_log.out`): real OFF receipt, then `run_window_query` returning those bytes, then `capture_verdict` for a capture 620 s after OFF.
  - Real bytes: `('network_time_unattested', 'no_valid_query')`.
  - The same bytes with only the four `}` lines deleted: `('clean', 'valid_query')`.
- **Why this blocks:** the ruled query starts 3,600 s before OFF, which is inside the network-time-ON period. That is exactly when `timed` writes these dictionaries (4 of them in 90 minutes here). So in practice every window's run would be invalid, and no capture could ever be clean. The failure is in the safe direction, but it breaks the mechanism.
- **Why the tests missed it:** every continuation line in the test file is invented and indented (`tests/test_network_time_window.py:114,118`). No test saw real bytes.
- **Suggested cure:** treat any line after a placed line as a continuation. Refuse only (i) a line before the first placed line, or (ii) a line that starts like a timestamp (`^\d{4}-\d\d-\d\d `) but fails the full parse with its offset. Add a regression test built from the real bytes above.

### B2. A test that passes on main now fails: `tests/test_launch_window.py`
- `PackNightLaunchBoundaryTests.test_integrated_driver_arm_go_launcher_consumption_and_replay` fails with `AssertionError: 3 != 0`. It passes on a snapshot of main 9eab16f8 (`Ran 10 tests ... OK`).
- **Cause (executed):** `pack` is not in the empty `NETWORK_TIME_ENFORCED_KINDS`, so the driver now refuses the pack night. With `pack` added to the set and the network-time functions mocked, the same test passes (`with pack enforced + NT mocked: ok = True`).
- **Assessment:** the behaviour is what the ruling requires (§4.4, §6.6 row 2). But the file is outside N1's WRITE_SCOPE. The seat neither stopped with NEEDS_SCOPE (ruling §6.3: "stops and reports the path") nor ran this module; its V1–V3 covered only the four in-scope modules. The candidate cannot merge with this test red. The lead must decide the scope, for example a module-level patch like the one `test_run_night.py` uses, plus one assertion that the pack is refused.

## SHOULD-FIX

### S1. The arm-retry invariant from main was weakened to work around the doc-pinned policy table
- `joulewise/arm_retry.py:89–90` puts the two new reasons straight into `DISPOSITIONS` rather than into `COLD_GATE_CODES`.
- `tests/test_arm_retry.py:120` changes main's `set(COLD_GATE_CODES) == GATE ∪ DRIVER` to `set(COLD_GATE_CODES) | NETWORK_TIME_COLD == ...`, with matching edits at lines 126–127.
- Main's check forced every driver reason to carry a cold-gate explanation (the code's own comment: "registry additions must force review"). `render_policy()` (`arm_retry.py:333`) renders the table that is byte-pinned against the handback and runbook documents. Result: both new reasons are missing from the operator's policy table, and the guard now has a carve-out.
- **Cure:** add both reasons to `COLD_GATE_CODES` with one-line explanations, restore main's assertion, and have the lead update the lead-owned documents (ruling §6.3) in the same merge.

### S2. Tests the ruling requires are absent
Behaviour for items (v) is correct by my probe (`/tmp/ntp-n1contract/probe_conditions.out`); what is missing is the test.
1. **§3.4 step 1:** "a test compares [the widened interval] against the original" (`quiet_predicate_campaign.attestation_window`, lines 610–635). None exists. `_interval` (`network_time_window.py:217–223`) matches the original by reading.
2. **§4.2:** "The new module must call `time.time()` and `time.monotonic()` and no other clock; a test pins this." None exists.
3. **§3.7:** "a test checks the list equals the registered builds other than 25G83." The test hard-codes `25F84` (`test_network_time_window.py:185`). The value itself is correct: `configs/calibration` carries 14 `"os_build": "25F84"` and 2 `"25G83"`. The two session identifiers match `battery_float_verdicts/*.json`.
4. **§4.3 restore-on-every-exit-path, at the driver:** the only driver test is the happy-path order OFF → chain → query → ON (`test_run_night.py:167`). There is no test for:
   - a non-zero chain exit;
   - a census or deadline abort;
   - an exception after OFF;
   - "chain end not proved → no query and no ON, marker stays";
   - `set_network_time_off` raising (the `except (OSError, ValueError)` branch);
   - recovery at driver start refusing on `chain_unproved`;
   - a rehearsal running OFF and ON.
5. **§3.4:** condition (f), a boot-identifier mismatch, and step 3 with the wall clock short and the monotonic clock sufficient have no tests.
6. **§4.1 / C9:** "A test shows the night launching when that refusal is deleted." The seat's recorded mutations cover only `MARKERS` and the `text`→`data` category swap. Nothing shows the `night_refused_network_time_off_unproved` refusal turning red when deleted, and the same holds for the route refusal.

### S3. The driver refuses silently when recovery cannot finish
- `scripts/run_night.py:3000–3004`: on `chain_unproved` or `marker_invalid` the driver returns `EXIT_REFUSED` and writes no refusal, no `result.json`, no courier message and no log line.
- The ruling says "a driver run refuses its own night" (§4.3), and every driver refusal is otherwise recorded under a registered reason (R15).
- A `marker_invalid` marker, for example one from a malformed file, silently refuses every later night until the dead-man job or a human clears it.
- **Cure:** record the refusal. The existing `night_chain_alive` fits `chain_unproved`, so no third new reason is needed.

### S4. `report --h7` computes its own "drift term" and "standing rate", which differ from the estimator's
- `network_time_window.py:399–401` computes a signed wall-minus-monotonic difference between the two endpoint stamps (`pre_spawn`, `post_parse`), and a rate over that monotonic interval.
- The estimator's drift term is part of B. It is `wall_minus_monotonic_span_s`, the envelope over all five stamps (`uncertainty_evidence.py` `_offset_envelope_s`, around lines 1090–1112 and 1318–1325). Its rate is taken over `rate_fit_baseline_s`, the summed native record support.
- A3 §4.6 compares the OFF window's drift terms with the 12 members' drift terms (0.74–1.54 ms), which are the estimator's quantity. As written, H7 would compare two different quantities.
- **Cure:** in `--h7` mode, which runs only after R9, read the estimator's recorded `wall_minus_monotonic_span_s` and rate fields from the evidence, or compute exactly the same definition.

## NIT

- **N1.** The witness category is matched as a substring anywhere in the line (`network_time_window.py:251, 295`). Probe: a `[com.apple.timed:text]` line whose message contains the text `[com.apple.timed:data]` served as witness and gave `clean`. Parse the category token by its position.
- **N2.** If `h5-off.json` exists but is not valid JSON, `capture_verdict` returns `off_not_proved` before it searches for markers (`:268–271`). Ruling §3.4 step 1 would still honour a marker in an authentic run. Both outcomes refuse; only the reason string differs.
- **N3.** The driver's `finally` catches `(OSError, ValueError, KeyError)` around `run_window_query` (`run_night.py` about 3306). A `TypeError` would skip ON and propagate, against §4.3 "the restore never raises". The marker still covers it.
- **N4.** In both OFF-failure branches, `os.close` and `_record_chain_exit` run before the ON attempt. If either raises, ON is skipped and only the marker covers it. Attempt ON first.
- **N5.** `OLD_IDLE_PLANS` lives in this module and must be filled "when that consumer lands", but N3's WRITE_SCOPE does not include this module, and the ruling's lead-owned list names only the `NETWORK_TIME_ENFORCED_KINDS` line. Scope it explicitly.
- **N6.** Ruling §10 asked N1 to confirm the paired-readings path on one real 2026-09-27 bundle. The seat's report does not record doing so. The code's `clock_anchor.clock_stamps` (calibration) and `power.anchor.clock_stamps` (idle) match the writers by reading.
- **N7.** In `tests/test_arm_retry.py`, the new `NetworkTimeRefusalTests` class sits between module-level constants (`COLD` and `INSTALLER`). Style only.

## Confirmed to contract (executed unless marked "read")

- **Scope:** N1's commit touches exactly the 8 files of §6.3. The `tests/test_gen_state.py` change in the range comes from the records merge 921a7953, not from N1.
- **Imports:** the module imports only the standard library (`argparse, hashlib, json, math, os, re, subprocess, time, datetime, pathlib`). No project import. Read.
- **OS boundary:** every command goes through `runner` (default `subprocess.run`); the boot probe, the clock, `process_group_absent` and the marker path are injectable. With guard2 installed as `usercustomize`: `test_run_night`, `test_network_time_window`, `test_arm_retry` and `test_night_gate` gave **405 tests OK with zero guarded calls**. `test_run_night` patches all network-time seams in `setUpModule`.
- **Refusal reasons:** `night_refused_network_time_off_unproved` and `night_refused_network_time_route_unenforced` are registered in `night_gate.NIGHT_DRIVER_REASON_CODES` and classified `cold_gate`, and neither is in `ZERO_CAPTURE_MACHINE_REFUSALS`.
- **Nothing can launch:** `NETWORK_TIME_ENFORCED_KINDS == frozenset()`. Through the real, unmocked module (`/tmp/ntp-n1contract/probe_driver.out`), a plan whose chain is `chain.zsh`, `calibration_derivation_only.zsh` or `quiet_predicate_evidence.zsh` ended each time with exit 3, zero chain spawns, no `chain.started`, no `h5-off.json`, and reason `night_refused_network_time_route_unenforced`. `pack` is refused too (B2).
- **Rehearsal:** a `REHEARSAL_STUB` plan (`/tmp/ntp-n1contract/probe_rehearsal.out`) did the following:
  - it wrote the marker, then ran the OFF command (the guard blocked it);
  - it saved `h5-off.json` with the error;
  - it attempted ON and saved `h5-on.json`;
  - it refused with `off_unproved`;
  - the marker stayed for recovery, and `result.network_time_restore` shows `failed`.
- **H5 receipt:** it holds argv, exit status, exact stdout, stderr, error, the wall and monotonic clocks read after the call, the boot identifier and the plan identifier. It is write-once. The marker is written by exclusive create **before** OFF, at the fixed path, and holds the custody path and plan identifier. `set_network_time_on` removes the marker only when ON exits 0. Recovery removes it after a failed ON (ruling §9 row 11: "do not block").
- **The 600 s rule:** the capture's first reading minus the OFF receipt must be at least 600 s on both clocks. The wall-clock-short and monotonic-short cases each give `off_lead_short`.
- **Recovery calls:** `dead_man` calls recovery as its first action, before both early returns, and again after it proves the chain gone. `run_night` calls it first, before its own OFF. Recovery acts only when `chain.exited` exists or the process group is proved absent. Read, and tested in the module.
- **Query window (§5):** the query starts at `floor(OFF − 3600)` and ends at `ceil(now)`, both passed with `+0000`. A run is valid only if its start is at or before OFF − 3,600 s and a `data` witness is older than OFF. A capture is covered only by a run that started at least 1 s after its last reading on both clocks. A3's seven tests plus the three §5 tests are present; the real-log case of A3 is left to the lead's bench (B2 of §7.2).
- **Precedence:** the order is marker in any authentic run, then `off_not_proved`, then `off_lead_short`, then `no_valid_query`, then `clean`. The verdict strings are exactly `clean`, `network_time_slew_attested` and `network_time_unattested`. The marker edges: a marker exactly 1 s after the last reading counts as slew, while one at 1.5 s after gives `clean`.
- **`report --h6` prints no B:** I ran the CLI on evidence carrying `B`, `uncertainty_s` and `effective_clock_anchor_bound_s` (`/tmp/ntp-n1contract/probe_report.out`). None of those values appears in the output; slew-attested rows print first and are flagged.
- **No other weakened tests:** `tests/test_run_night.py` only adds tests (a module-wide patch plus 4 new tests); its one removed line is the import it extends. `tests/test_night_gate.py` only adds two literals. The one weakening is S1.
- **Wider suite:** I ran 30 driver-adjacent test modules. All pass except `test_launch_window` (B2). The failures in the first pass were artefacts of my own guard blocking fake `sudo` stubs. After I narrowed the guard, `test_install_night_agent` (65), `test_evidence_night` (166), `test_battery_float_consumers` (17) and `test_quiet_predicate_campaign` (203) all passed.
