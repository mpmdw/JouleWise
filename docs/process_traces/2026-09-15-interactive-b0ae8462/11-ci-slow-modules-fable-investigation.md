# CI slow modules — test-code lens (Fable seat, 2026-09-15)

Evidence: CI run 35055941547 (main b3b51a2c, py3.11 `MODULE/UNIT PASS seconds=`); bench = fresh copy of main f4d55d66 on the M3 Max with per-test wall, subprocess spawn count/wait, `time.sleep` totals, per-argv child attribution and cProfile (`scratchpad/seats/prof/*.json|*.prof`). † = measured with 5–8 modules running concurrently (inflated ~1.5–2×).

## Ranked table (CI py3.11 s → projected after the named cut)

| # | module | CI s | bench s | where the time goes | cut | proj. | conf. |
|---|---|---|---|---|---|---|---|
| 1 | test_calibration_exits (exclusive) | ~1080 job (decl. 2036) | 476 | 79% = ONE test running 72 witness cases serially; child attribution: 19 `validate_powermetrics_fiducial.py --allow-live` at 29 s† each = 86%, 7 `--rederive-from` at 7 s; git fixture ≈ 25 s; 154 `/sbin/mount` (darwin-only) | A: 4-worker owned-runner pool over the 72 cases (pattern exists in crash matrix); F1/F2 inside the child; B: git fixture template | ~400 | med |
| 2 | test_p2038_production_path | 619 | 249 | pure CPU: `_fit_pulse` 60% + `plistlib` re-parse of the same capture 57× (15.7k docs) 25%; spawn wait 7 s, real sleeps 8 s | F1 exact-multiset `_pulse_loss` (3.77×, bit-identical) + F2 parsed-plist cache by content digest | ~220 | high |
| 3 | test_reduce (4 units) | 634 | 529† | fitter via `_SELF_CONSISTENT_CALIBRATIONS`; 13 tests >5 s, top two 143/87 s | F1, F2 | ~300 | med |
| 4 | test_receipt_histsem (shard-4 critical path; declared 28.7 s = 17× under-weighted) | 509 | pending | per pack: `git clone --shared` + FULL `checkout --detach` of 7 410 files + ~135 `git cat-file blob` spawns; ×9 packs per `verify_all`, re-run by many tests | H1 `cat-file --batch` (1 spawn/pack, identical bytes); H2 sparse checkout of `pack_relative` only | ~120 | med |
| 5 | test_calibration_writer_crash_matrix (exclusive, K=2) | 348 + 202 (decl. 1990 = 3.6× stale) | — | 71 cells × (1 SIGKILLed writer + ~5 recover CLIs) ≈ 430 python spawns, 4 workers; SIGKILL-at-stage IS the oracle | I1 lazy imports in the 3 CLI scripts (0.28–0.46 s/spawn) | ~420 | med |
| 6 | test_whole_window_selection | 284 | 109 | 77% = one test: 10 rederivations (533 fits, 6.95 M loss evals) | F1 | ~110 | high |
| 7 | test_validate_powermetrics_fiducial_derivation_only | 183 | 181† | 6 writer children ≈ 12 s each (fit inside child) | F1, I1 | ~80 | med |
| 8 | test_run_campaign | 175 | 457† | 4 863 spawns: 626 × the 5-spawn `bundle.py` git-state probe (toplevel, HEAD, `diff --binary`, `diff --cached`, `ls-files --others`); 33 s real `time.sleep` in retry-slack fixtures | R1 merge rev-parse calls (5→4 spawns, exact); inject the fixture sleep | ~140 | low |
| 9 | test_powermetrics_fiducial | 174 (decl. 18.6) | 181† | zero spawn wait; 4 tests = 126 s in-process rederivation | F1 | ~70 | high |
| 10 | test_launch_window | 174 | pending | 14 subprocess sites (install/arm scripts, git) | see install | ~100 | low |
| — | test_install_night_agent (main 25 tests / branch 51) | not top-ten | 11.6 / 88 | branch: 75 zsh runs × 4 interpreters (`python3 -S -c` plan read, version check, `-m night_agent_install`, `run_night.py preflight` 0.57 s) ≈ 1.1 s/run; 408 git fixture spawns; the "600 s" figure did not reproduce | N1 in-process `night_agent_install.main()` for Python-behaviour cases, keep ~10 zsh-contract cases; N2 fixture template | ~35 | high |

## Notes

**F1 — the fitter (`powermetrics_fiducial.py:_fit_pulse/_pulse_loss`) is the one lever on #1–#3, #6, #7, #9.** Per pulse: 2 rounds × (301 coarse + 3 001 fine) × 2 axes = 13 208 loss evaluations, each walking all ~27 local intervals. Every interval fully inside `[on,off]` has overlap exactly 1.0, fully outside exactly 0.0, so its Huber term is a constant float; only the 2–4 straddlers change. Feeding `math.fsum` the identical multiset of terms is bit-exact (fsum is correctly rounded). Bench: 7.4 → 2.0 µs/eval, 3.77×, **bit-identical over 944 grid points**. Risk: none if the term expression is kept verbatim; acceptance = byte-identical replay of every rederivation fixture (the strict-rederivation hash gates flag drift). Do NOT shrink the fine grid to ±coarse-step — that is an estimator revision (D-078 territory), not a speedup.

**F2 — plist re-parse.** p2038 parses one capture 57× (`_powermetrics_documents` → `plistlib.loads` ×15 701) from `derive_powermetrics_anchor_v3`/`_lp2`. Cache parsed documents keyed by bytes digest (never path/mtime, which would be tamper-blind).

**#1 calexits.** The witness corpus is serial by construction (`WitnessCorpusOwner.get_or_execute`); the fake sampler polls at 1 ms and the writer uses a logical clock, so the 29 s per `--allow-live` child is CPU (capture handshake + fit twice + parse), not waiting. Cut A: a `_parallel_worker` pool as `test_every_exact_stage…` already does; keep census-sensitive codes (nonowned-sampler decoys, lease holders) serial exactly as the crash matrix keeps `_ACTUAL_RESERVATION` serial. Risk A: a census-sensitive case observing a sibling's child — audit per code. Cut B (one `git init` template cloned per case) saves ~25 s bench; the maintenance-race tests are separate methods. Job timeout math after A+F1: ~7 min.

**#4 histsem.** `arm_readiness.py:3846` clones `--no-checkout` then `checkout --detach` materialises the whole tree per pack; `:3497` spawns one `cat-file` per file. `--batch` returns identical bytes. Sparse checkout is fail-closed: if verification read anything outside the pack, the missing file refuses loudly rather than passing.

**#5 crash matrix** cannot go in-process; only the per-spawn import (`calibration_epoch_continuation` 0.12 s, `calibration_exits` 0.12 s, `powermetrics_fiducial` 0.04 s) is cuttable. Its weight declaration is stale (runner side).

**Wall-clock sleeps to inject:** p2038 `LogicalDrainTimer.sleep` calls real `time.sleep` (adapter already accepts `drain_sleep`); adapter readiness/capture loops (`powermetrics.py:1284,1574,1651`) sleep `READINESS_POLL_S` with no seam; run_campaign retry-slack fixtures sleep 33 s real. All ≤10% of their modules today; calexits' 6 901 sleeps total 3 s.

**Pending at write time:** per-test splits for test_receipt_histsem and test_launch_window (runs in flight); CI figures stand.
