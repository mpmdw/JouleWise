DELTA: FINDINGS

N1 fix round 2c delta re-audit (Opus 5.5 seat; I wrote no part of the fix), 2026-09-29. Charge: A2 ruling §6.2, rows 1-7.
New head c895f28b (worktree /Users/edr/code/JouleWise-wt-n1d3-new-ff50b201), old head 36e8ba6e (/Users/edr/code/JouleWise-wt-n1d3-old-ff50b201). Both clean and unmoved at the end.
Scratch: /private/tmp/claude-501/-Users-edr-code-JouleWise/ff50b201-b458-48cc-8d86-bb1b4bb19e19/scratchpad/n1delta3/ (= S below).
Pre-check: `ps -axo pid,comm` showed no powermetrics binary, before the probes and again before the deletions. (`pgrep -fl powermetrics` only matched shell command text.) No sudo/systemsetup/sntp/log/powermetrics was run. Every sleeper was killed by PID, and a final pgrep found none left.
Short verdict: the 2c cures are correct and every regression is sound. The FINDINGS come from the row-6 hunt: one pre-existing dead-man record gap reported under stop condition 8 (F1), plus three nits. None was introduced by 2c except F3.

## Rows
1. Judge's probes. PASS. I copied them to S/probe_r1_r5.py and S/probe_nit1_pgrep.py with CAND set by env and three edits: (a) the scratch path; (b) the R2 mock leak the judge disclosed in §0 item 8 is fixed with a `with` block; (c) [K] is called the way each head's driver calls it (new head: cleanup_only=True). Logs: S/probe_r1_r5.{new,old}.log and S/probe_nit1.new.log.
   - R1: missing_both and missing_pid are refused on new (driver_accepts=False, `chain_unproved`, no ON, proof not called). On old both were `restored` with ON. Complete nulls are still accepted, and pid=123 is still refused.
   - R2: two_groups with batch exit 0 and empty output gives `(False, {'check':'P2', groups:{...'census_ambiguous: exit 0 with no lines'}})`; old gave `(True, ...)`. Real pgrep on absent groups: exit 1, empty. A live non-ancestor sleeper group: exit 0 with one line, and `_group_census_batch` answers False (present).
   - R3-A: after [K] there is no document. Final: one `refusal.json` = night_chain_alive, and result.json agrees. Old: refusal.json = night_probe_error plus refusal-01.json.
   - R3-B: the chain's `refusal.json` = night_probe_error is untouched. The driver's `refusal-01.json` = night_chain_alive carries prior_documents=['refusal.json']. result.json = night_chain_alive.
   - R3-C: unchanged on both heads.
   - R4 (2.7/3.6/5.4 s, proved), R5 (exit 6) and NIT-2 (4/4 prefix matches) are identical on both heads.
   - NIT-1 matches the judge's X10: 2 s survivor with 2 groups refused at 0.95 s after 4 passes; 1 group refused at 1.83 s; 0 groups proved at 2.22 s; 3.5 s refused at 3.04 s; 0.5 s proved; an already-ended child proved in 1 pass.
2. §3.5 regressions on both heads. PASS. `bash S/row2.sh` ran the 15 IDs listed in S/row2.tests.
   - New head: 15/15 ok.
   - Old head: I overlaid the new test files on a `git archive` of 36e8ba6e (S/oldov). 10 failures, every one by AssertionError: R1 recovery x2 (`'restored' != 'chain_unproved'`); R1 driver x2 subtests (`True is not false`); R1 dead-man (`0 != 3`); R2 exit-0-empty (`True is not false`); R2 attribution (`{456: ['101 child']} != {}`); R3-A and the real-driver [K] test (`[.../refusal.json] != []`); R3-B (`None != ['refusal.json']`).
   - Controls pass on both heads: R1 explicit-null recovery, the dead-man null-pgid courier test, R2 exit-1-empty, R3-C, and the unchanged deadline and census stops with `_assert_one_chain_alive_cause`.
3. Real-driver [K] case. EXECUTED, PASS. Test: `CaptureRefusalRecordTests.test_R3_real_driver_idle_chain_crash_runs_cleanup_before_failed_proof`. It uses the real chain Popen, a journaled separately grouped path-signature child, a schema-valid C5 `quiet_predicate_evidence` receipt, and a real proof.
   - New head: ok. Query and ON were not called, the marker was kept, and there is exactly one `refusal.json` = night_chain_alive.
   - Old head: fails by assertion inside the [K] wrapper, because a refusal already exists.
   - Call chain I read on the new head (the ruling's :3346/:3347/:3357/:3359/:3417 moved): run_night.py:3353 registry exists → :3354 `_evidence_cleanup_error(..., cleanup_only=True)` → :1407-1412, which saves the cleanup record and returns before any outcome repair or write_refusal → :3355 `_chain_never_launched` → :3364 `_prove_capture_absent` → :3366 `_capture_unproved_abort` → :3424-3432 the result step writes `refusal.json`. Courier prep at :1460 keeps the full repair.
4. The three deletions. PASS (S/mut.py, S/mut.log, on an archive copy of c895f28b). Each named test went red by AssertionError: restoring the early [K] write turns R3-A red; dropping the key-presence test turns the four R1 tests red; dropping the exit-0-empty clause turns R2 red. The unmutated copy passes the same 6 tests.
5. Earlier regressions, earlier deletions, and the modules run whole. PASS.
   - Modules: all five run whole on the new head outside any sandbox, without the guard (S/mods/*.log): network_time_window 51 OK, run_night 290 OK (185 s), night_gate 104 OK, arm_retry 37 OK, launch_window 39 OK (585 s). Total 521, 0 failures, including all 16 BindSupervisionProcessTests.
   - Earlier regressions: record 45's 35 regression IDs and the 42 IDs of A1 §7.3 row 5 (77 unique, taken from /tmp/ntp-n1delta2-exec/*.txt) are all ok, except the two IDs record 45 row 5 says were replaced. Their replacements pass.
   - Deletions: record 45's seven deletions (S/deletions45.py, S/deletions45.log) repeat record 45 exactly. P1_in_proof: 2 red, and the two driver same-group tests stay green (the known caveat). P1 plus the post-exit census: 2 red (`['off','query','on'] != ['off']`, `3 != 6`). P2, P3, C5 and never_launched_claim: 2 red each. E2_replace: deadline red (`'night_window_exceeded' != 'night_chain_alive'`), census green as expected. All are AssertionErrors, and the files were restored byte-identical.
   - Protected functions are AST-identical across the heads: `_prove_capture_absent`, `_capture_proof_pass`, `_capture_pass_calls`, both census functions, the sweep, and `_write_driver_refusal`. There is one `supersede=True` call site (run_night.py:3547).
6. Own hunt over refusal writers after OFF. FINDINGS (F1, F2, F4). Cases are in S/hunt/delta_hunt_cases.py (NightDriverTests fixture), run on both heads; logs S/hunt/{new,old}.log.
   - Watchdog (:860): its document is superseded and names itself in prior_documents (SS, nit F4). If the supersede fails, the §3.3 rule breaks (SF, nit F2).
   - Census stop: holds (the unchanged live test).
   - [K] early: holds (rows 2 and 3). `cleanup_record` writes only evidence_cleanup.json (quiet_predicate_campaign.py:315-324).
   - Chain `write_refusal`: holds (R3-B).
   - `calibration_refusal` (:3413-3416): writes only when abort is None. A chain-written calibration-refusal.json is listed by `_refusal_paths` and so is named in prior_documents (read, not executed).
   - rerun.refusal.json (:1860): a second driver invocation's own refusal. It is outside the refusal.json/refusal-NN.json naming and outside `_refusal_paths` (read).
   - Dead-man (:3600, :3621, :3639, :3663) and the courier-prep [K] (:1460): F1.
7. Signatures.
   - **E2:** NO on every path §3.3 governs, where the proof is the driver's own proof in run_night. R3-A/B, the real-driver case, and the deadline and census live tests all executed on the new head. YES, in the letter of the signature, on the dead-man path (DM3, F1) and in the injected supersede failure (SF, F2). Both reproduce identically on 36e8ba6e, so neither was introduced by 2c. I do not judge whether they trigger A2 §6.3; that is for the lead or the cold gate.
   - **D1:** NO. No executed case ran the query or ON beside a live capture-signature process: R1 malformed claims, the real-driver [K] case, the 290 run_night tests including every live detached test, DM2 and DM3 (query and ON withheld, marker kept), and NIT-1. The DM1 widening (F3) restores ON without a proof only for a claim shape that no production writer emits.

## Findings
F1 should-fix. Lead to classify; reported under A2 §3.6 stop condition 8. The dead-man leaves no night_chain_alive record after its own recovery proof fails.
   - Where: `dead_man`, scripts/run_night.py:3570-3690, including the census refusal writer at :3663.
   - What happens: the recovery proof fails and recovery answers `chain_unproved`, withholding ON and keeping the marker. The dead-man writes nothing naming night_chain_alive. It then continues to the census and the courier and exits 0.
   - DM2a: no document at all and no result.json.
   - DM2b: the census refusal writes `refusal.json` = night_aborted_agent_present. When a hung driver later resumes, it adds `refusal-01.json` = night_chain_alive with prior_documents=['refusal.json'].
   - DM3, the watchdog-fired-but-main-loop-never-resumed case of `_WindowDeadline`'s docstring (~:846-852): the only document is the watchdog's `refusal.json` = night_window_exceeded. There is no result.json, and the courier runs.
   - Read, not executed: the courier-prep full [K] (:1460) would add night_probe_error when an idle night has no documents (DM2a's shape).
   - Reachable only when the driver is dead or hung past the completion epoch before its result step. Never beside a capture. Identical on 36e8ba6e.
F2 nit (pre-existing from round 2b). In the supersede-failure fallback (:3549-3556), with an injected OSError on the supersede `os.replace`, the watchdog's `refusal.json` = night_window_exceeded remains and `refusal-01.json` = night_chain_alive is added; result.json = night_chain_alive (SF). This needs a custody write failure; replacing a file you cannot write cannot fix it. Candidate registered limit.
F3 nit (introduced by 2c, as the one-predicate instruction implies). The dead-man now accepts `{"pid":null,"pgid":null,"popen_attempted":false}` without launch_error (network_time_window.py:352-358 via run_night.py:3619). DM1: new exit 0 and writes chain.exited launch_failed; old exit 3 with a night_chain_alive refusal. Recovery then restores ON with no proof (probe R1 complete_nulls). No production writer emits that shape: :621-627 always adds launch_error, as do :600-612. The acceptance set is widened only for non-production claims.
F4 nit. When the watchdog's document is superseded, prior_documents includes that document's own name (`refusal.json` names `refusal.json`, SS; :3539-3541). Literal to A2 §3.3; cosmetic.
Not re-derived: the fix seat's claimed 35 inherited failures and 17 sandbox-only IDs. Outside the sandbox and without the guard, all 521 passed here.
