# 62 — Post-merge cross-unit review (gate-ledger row 11, second half)

Reviewer: Opus 5, read-only, worktree `/Users/edr/code/JouleWise-wt-xunit-d0b83820` at main `6032b9e9`.
Scope: PR #361 `b3abce08`, #360 `0c529f99`, #362 `42d3849e`, #363 `6032b9e9` — effect on units NOT in their diffs.

## Verdict

**FINDINGS — 0 blocker, 3 should_fix, 3 nit.** No merged change is unsound; every finding is a
coverage hole or a bookkeeping row that now contradicts main. Code questions 1 and 2 are clean.

## Q1 — #361 fixture vs #362 semantic check: COHERENT, no orphans

- `GENERATION_LEDGER_HEAD_BYTES` / `_SHA256` are still live and still needed: they back
  `tests/test_campaign_generator_core.py:37` `generation_repository()` and
  `tests/test_arm_readiness_evidence_packauth.py:549-553`. Three packs still byte-pin the head file
  (`LEDGER_HEAD_FILE_SHA256` in `configs/campaigns/d117_floor_qwen25_1p5b_v{1,2,3}/generate_configs.py`),
  so the historical bytes remain the correct declared input for the frozen path. No module imports
  the constants without needing them; no module lost its need for `generation_repository`.
- The two live floor v5 generators now run `verify_ledger_head_pin()` against the REAL committed pin:
  `configs/calibration/calibration_ledger_head.json` is sequence 176 / digest `0f7609ae…`, the r6
  acceptance cutoff is sequence 76 / digest `08456d50…` (= `LEDGER_HEAD_SHA256`), so production takes
  the strictly-advanced branch. `tests/test_generator_head_pin_relation.py` and
  `tests/test_d117_floor_qwen3_v5_generate.py:272` exercise exactly that, with no fixture.
- No test passes only because a fixture supplies historical head bytes where production uses the
  semantic check: every module that calls the fixture helper regenerates FROZEN packs only
  (`tests/test_arm_readiness_registry.py:29-32` `PACKS` = qwen25 `_v1`; `test_d117_decode_contrast_plan.py:31`
  = `d117_contrast_qwen25_1p5b_vs_7b_v1`; packauth emits a `_v4` qwen25 successor).
- **N1 (nit, latent).** `generation_repository()` copies *all* `d117_*/generate_configs.py` from the
  working tree into the clone (`tests/test_campaign_generator_core.py:57`+) while overwriting the head
  file with sequence-76 bytes. The two live v5 floors are therefore present in that clone, and any
  future test in a fixture-using module that regenerates them would silently exercise the
  `sequence == cutoff` branch instead of production's advanced branch. Counterfactual: add a live-v5
  regeneration to `test_arm_readiness_registry.py` and a rollback bug in `verify_ledger_head_pin()`
  stays invisible. Call site: `tests/test_campaign_generator_core.py:37-58`.

## Q2 — manifest consumers after `issued_ledger_head` lost `file_sha256`: NO FINDING

- Repo-wide, `issued_ledger_head` has exactly one reader outside the generators:
  `tests/test_generator_head_pin_relation.py:195`. **No production path reads it at all.**
- The three real `acceptance_policy` readers touch only other keys and cannot KeyError on either shape:
  `joulewise/arm_readiness_evidence.py:897` (`issued_acceptance`/`issued_artifact_id`, Mapping-guarded),
  `joulewise/arm_readiness.py:6192` (`selection`/`issued`, Mapping-guarded),
  `scripts/validate_powermetrics_fiducial.py:899-915` (`issued_acceptance` only, inside a
  `except (… KeyError, TypeError, ValueError)` block).
- Shape coexistence is real but inert: nine frozen packs keep `"file_sha256"` in their committed
  `plan_tree.json`; the two changed packs have **no** committed `plan_tree.json` at all
  (`configs/campaigns/d117_floor_qwen3-{1p7b,8b}_v5/` contain only `generate_configs.py`), so there is
  no old-vs-new committed artifact of the changed generators to diverge.

## Q3 — #360 harness has no callers, and no doc claims an interface: NO FINDING (one stale row)

- Grep over `*.py *.md *.yml *.yaml *.json` (excluding `process_traces/`) finds `sample_quiet_predicate_evidence`
  ONLY in the script itself and its test module. `scripts/run_night.py` and the night chains never name it.
- The CLI matches its own docstring exactly: subcommands `collect`, `load`, `summarize` (+ suppressed
  `_sample`); `collect --state/--repeat/--duration-s/--sample-interval-s/--power-interval-ms/--out/--load-cores/--power|--no-power`;
  `load --cores/--duration-s/--period-ms/--qos/--profile/--seed/--log`; `summarize --in/--reference-state`.
- **F1 (should_fix).** `docs/process/state_kernel.json` (QUIET-PREDICATE-EVIDENCE-01, rank 232) and the
  duplicated `TASK_QUEUE.md` rows A232 (lines 858 and 1072) still read: the harness "is on branch
  `feat/2026-09-18-quiet-predicate-evidence-harness` at `98336969` … **UNMERGED**", "has pull request
  #360 **open**", and "31 offline tests". On main it is merged (`0c529f99`) and the module has 46 tests.
  Counterfactual: the next activation reads the queue row and re-opens a merged lane.
  Call site: `docs/process/state_kernel.json:5839`; `TASK_QUEUE.md:858,1072`.

## Q4 — #363 darwin guards: hosted CI now has ZERO coverage of two real paths

- **F2 (should_fix).** Every runner in `.github/workflows/ci.yml` is `ubuntu-latest` (quick job line 17,
  six-shard matrix line 134, mock-smoke line 102, exclusive jobs lines 237/303); no workflow in
  `.github/workflows/` mentions macOS. After #363, four of the module's 46 tests skip on Linux:
  `test_real_collect_no_power_reaps_all_recorded_workers` (:345, new) — the only real `collect()`
  subprocess test; `test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child` (:658, new) —
  the only real join-ladder / SIGTERM-escalation test; plus the pre-existing
  `test_native_qos_classes_read_back_in_subprocess` (:706) and
  `test_real_load_tracks_point_one_core_and_guards_worker_budget` (:730).
  Net: `load()`'s join ladder, the `worker cleanup escalated:` path, and the real collect path are now
  **bench-only (macOS developer machine)** — no automated gate anywhere. What remains on Linux for
  `load` is `test_load_worker_runs_its_window_after_the_rendezvous` (:639, fake clock, exercises
  `load_worker` not `load()`), the burn-profile test, and the offline stationarity/summary tests.
  This is a deliberate fix-forward, but the coverage loss is not recorded in the kernel — register it,
  or add a Linux-runnable fork-context variant of the ladder.
- **N2 (nit, concrete).** The guard at :656 also swallows the tail block of that method — "N3: `load()`
  `Process.start()` failure must close both real Pipe ends" (:684-705) — which is platform-independent
  (a `Mock` process, `context.Pipe()` never started). Counterfactual: reintroduce a pipe-end leak in
  `load()`'s `except` path and Linux CI stays green. Fix is a 3-line method split.
  Call site: `tests/test_sample_quiet_predicate_evidence.py:656-705`.
- **N3 (nit).** Neither new module is in the quick tier: `scripts/test_timings.json`
  (`seconds_by_module`, 230 entries) has no row for `tests.test_sample_quiet_predicate_evidence` or
  `tests.test_generator_head_pin_relation`, so `quick_suite.select_modules` excludes them as
  "unknown weight" for `--tier quick` (they are selected under `--tier touched`, and they do run in the
  ordinary six-shard matrix at the conservative unknown weight). So the quick job skips the module
  wholesale on Linux — the darwin guards are not what keeps it out of the quick tier.

## Q5 — stale rows contradicting merged state

- **F3 (should_fix).** `docs/process/state_kernel.json` GENERATOR-HEAD-FILE-BYTE-PIN-01 (rank 244) is
  still `"status": "queued"`, and `TASK_QUEUE.md:866,1080` still carry A244 as `READY [AGENT]` asking
  "May the byte pin be replaced by the semantic relation?" with the acceptance "removing the mechanism
  requires the ruling first". The ruling landed (packet 09 → `09a-adjudication-generator-head-file-byte-pin.md`)
  and the removal merged as `42d3849e`. Counterfactual: an agent picks A244 off the queue and re-runs a
  settled cold gate.
- **N4 (nit).** The same row names `configs/campaigns/d117_contrast_v5` as a third byte-pin holder. It
  never was one: that generator carries no `LEDGER_HEAD_FILE_SHA256`, no head-file entry in its
  drift-refusal set, and touches the head file only as a run-time `--head-pin` argv
  (`d117_contrast_v5/generate_configs.py:2134`). The registration overstated scope; #362's two-pack
  scope was correct.
- `RUN_STATE.md:13` still says "PR #363 (CI fix-forward) **open**, checks running"; it merged as
  `6032b9e9`. Bookkeeping only, rolled into the next RUN_STATE block.
- No stale code comment referring to the removed byte pin survives in `tests/` or `configs/campaigns/`
  for the two changed packs; no doc says `cutoff == pin` (grep clean).

## Commands run (all read-only, in the xunit worktree)

```
git log --merges -4 --format='%H %s' origin/main
git diff <merge>^1 <merge> [--stat] (×4)
grep -rn 'GENERATION_LEDGER_HEAD|generation_repository|LEDGER_HEAD_FILE_SHA256|issued_ledger_head|acceptance_policy|sample_quiet_predicate_evidence'
python3 -c "json … calibration_acceptance_d079_v2_n17_r6.json['ledger_cutoff']"   # sequence 76
shasum -a 256 configs/calibration/calibration_ledger_head.json                     # sequence 176
python3 -c "shard_tests.load_timing_map()"                                         # 230 entries, neither new module
scripts/sample_quiet_predicate_evidence.py {collect,load,summarize} --help
.venv/bin/python -B -m unittest tests.test_generator_head_pin_relation     # Ran 11, OK (27.9 s)
.venv/bin/python -B -m unittest tests.test_sample_quiet_predicate_evidence # Ran 46, OK (7.7 s), darwin
```
