# Cold final-pass verdict (Fable 5.1), candidate 45889885 — A234+A212 refusal early release (F3)

Judge worktree `/Users/edr/code/wt-f2d6899b-finalpass` detached at `45889885`, 2026-09-23. One non-interactive session, foreground only, no subagents, no background tasks, no watchers, nothing committed, no tracked file edited. Scratch worktree `/tmp/f2d6899b-final-judge` (45889885) created for tests and probes and removed at the end. Wall time ≈ 33 min.

## 0. Contamination disclosure

Loaded beyond this charge, all by the harness before I acted: the user-level `/Users/edr/.claude/CLAUDE.md` (playbook names, writing standard), the project `CLAUDE.md` at 45889885 (bridge policy), and the auto-memory index `MEMORY.md` (one-line pointers; it names lane A234, the 5fe5a59b harvest and a "live F3 defect"). I opened no memory file body, no RUN_STATE.md, no TASK_QUEUE.md, no council log, no skill. Read this session: the merge diff `git diff origin/main...45889885`; records 09, 10 (head), 12 (head), 16, 19 and 23 from `origin/docs/2026-09-23-f2d6899b`; the base `plan_span_active`/`plan_is_armed` on `origin/main`; `tests/test_magistrate_watchdog.py` lines 100–260 and the delivered-refusal tests; the two launchd templates; `NIGHT_HANDBACK.md` term positions. NOT read: the earlier cold verdict 04 of activation 5fe5a59b (out of time; ruling 16 already carries its packet hash), record 21 (fix2b seat report), `/Users/edr/night-custody`.

## 1. Ruling 16 Q1 and ruling 19 against the code

Diff scope confirmed: `scripts/magistrate_watchdog.py`, `joulewise/arm_retry.py`, two test modules, two doc paragraphs (6 files, +725/−29; commits 31124f68 → 4c76ab69 → 3e27057a → merge 14c0e06b → 45889885).

| Clause | Code | Test (all new, all executed green) | Status |
|---|---|---|---|
| F1 driver probe, bracketed, release needs census AND driver empty on the same tick | `DRIVER_PROBE_ARGV = ("/usr/bin/pgrep","-lf","[r]un_night\\.py")`; `production_driver_probe` (empty ⇔ exit 1); `decide()` takes both probes only for `pending` candidates, latches only `if release_census.empty and release_driver.empty`; missing probe → `CensusObservation(False, -1, …)` (hold) | `test_live_driver_without_agent_census_match_holds_then_releases`, `test_production_driver_probe_uses_bracketed_run_night_argv` | implemented |
| F2 latch key `plan_id:custody_root:sha256(result.json)` | `_release_key` exactly that; unreadable result → `None` → never observed | `test_replaced_result_same_plan_and_root_requires_new_census`, `test_unreadable_replacement_result_cannot_reuse_release` | implemented |
| F3 zero capture from custody, receipt veto-only | `_zero_capture_disk_facts`: `chain.started` absent; `*.consumed.json` absent at any depth under custody (and RUNS_ROOT for calibration); `RUNS_ROOT/instrument_validation` empty (calibration) or `night/evidence` empty + index absent/empty (evidence); payload kind and RUNS_ROOT via `probe_payload_kind`/`chain_literal`; every other case `False`. `terminal_zero_capture_refusal` docstring carries the bare-C5 clause; positive capture claim in any row vetoes | `test_f3_*` (14 tests) incl. nested marker, RUNS_ROOT marker, calibration file, evidence file, index, chain.started, clean bare C5 releases, no-C5 neither licenses nor vetoes, unreadable chain, ambiguous kind, relative/ambiguous RUNS_ROOT | implemented; ruling 19's two payload branches and "every other case no release" match line for line |
| S1 base tail for undelivered chain-started refusal | `plan_is_armed`: chain-started+exited+REFUSED → `now <= completion or (no courier.sent and now <= deadman + COURIER_LOCK_FRESH_S)` | `test_undelivered_chain_refusal_keeps_deadman_tail` | implemented |
| S3 docs glosses | five codes listed; tick = "one pass … launchd starts one every 300 seconds, the watchdog job's `StartInterval`" (template line 25: `<integer>300</integer>`); notice, owner veto, harvest glossed; interval stated as t0−8 min … t0+window_max_s+5 min courier deadline (`PLAN_LEAD_S = 8*60`, `COURIER_DEADLINE_S = 300`) | n/a | implemented |
| REQUIRED TEST 5 (Opus N1 chain-field guard) | — | `test_result_chain_fields_veto_zero_capture_release` (watchdog) + arm_retry test module +20 lines | present |
| REQUIRED TEST 6 (suites green) | — | see §2 | 269 passed here |
| Record 23 F1 cure (symlink-safe absence) | `_tree_has_match`: `os.lstat(root)`; only `FileNotFoundError` at the root is absence; non-directory root (file or any symlink) is a match; `scandir` with `is_dir(follow_symlinks=False)`, so a symlinked entry is a file-match; `_evidence_capture_absent` reads the index with `os.lstat` and requires `S_ISREG and size == 0` | `test_f3_broken_symlinks_never_stand_in_for_absent_capture` | implemented; my probes b5–b8, b11 confirm |
| Record 23 F2 (docs claim vs probe boundary) | docs now say "The driver probe exists only for this early release; after the interval ends, or once the release is latched, no driver probe runs" | — | cured in prose, matches `decide()` |

Ruling 16's single-fact mutants (collapse each disk check to True) were NOT EXECUTED by me; record 23 V4/V5 and the seat report cover them, and each fact has a dedicated failing-input test that I ran.

## 2. Counterexamples through decide() (executed, scratch worktree at 45889885)

Suite:
```
tests/test_magistrate_watchdog.py tests/test_arm_retry.py      159 passed, 227 subtests passed in 5.61s
tests/test_evidence_night.py::LifecycleTests                      78 passed, 70 subtests passed in 188.79s
tests/test_evidence_night.py (remaining classes, --deselect)      32 passed, 78 deselected, 57 subtests passed in 518.66s
```
(the evidence module was split into two foreground runs because one run exceeds the 600 s tool limit; 269 total = record 23's 268 + the new symlink regression.)

Probe `/tmp/f2d6899b/judge_probe.py`, a `FenceTests` subclass calling the production `wd.decide()`, delivered bare-C5 `night_refused_not_quiet` refusal at t0+60 s inside the nominal span unless stated:
```
a1 courier alive (census non-empty)                          decide=HOLD_CENSUS  armed=True  span=True  latch=0 census_calls=1 driver_calls=1
a2 driver alive, no census substring                         decide=HOLD_CENSUS  armed=True  span=True  latch=0 census_calls=1 driver_calls=1
a3 driver probe unavailable                                  decide=HOLD_CENSUS  armed=True  span=True  latch=0 census_calls=1 driver_calls=0
a4 driver probe errors (exit 2)                              decide=HOLD_CENSUS  armed=True  span=True  latch=0 census_calls=1 driver_calls=1
a5 census empty + driver empty (control)                     decide=LAUNCHING    armed=False span=False latch=1 census_calls=1 driver_calls=1
a6 release then magistrate alive (one-way, by design)        decide=LAUNCHING    armed=False span=False latch=1
a6b next tick census non-empty after latch                   decide=LAUNCHING    armed=False span=False latch=1 census_calls=1 driver_calls=1
b1 consumed marker deep under custody                        decide=FENCED       armed=False span=True  latch=0 driver_calls=0
b2 consumed marker under RUNS_ROOT                           decide=FENCED       armed=False span=True  latch=0
b3 instrument_validation capture                             decide=FENCED       armed=False span=True  latch=0
b4 instrument_validation is empty dir                        decide=LAUNCHING    armed=False span=False latch=1   (control: empty dir = no capture)
b5 instrument_validation broken symlink                      decide=FENCED       armed=False span=True  latch=0
b6 instrument_validation symlink to empty dir                decide=FENCED       armed=False span=True  latch=0
b7 instrument_validation is a file                           decide=FENCED       armed=False span=True  latch=0
b8 capture file is a symlink inside a dir                    decide=FENCED       armed=False span=True  latch=0
b9 evidence envelope file                                    decide=FENCED       armed=False span=True  latch=0
b10 evidence index non-empty                                 decide=FENCED       armed=False span=True  latch=0
b11 evidence index broken symlink                            decide=FENCED       armed=False span=True  latch=0
b12 evidence index empty file (control: release)             decide=LAUNCHING    armed=False span=False latch=1
b13 chain.started present                                    decide=FENCED       armed=True  span=True  latch=0
b14 RUNS_ROOT unreadable dir (perm 000)                      decide=FENCED       armed=False span=True  latch=0
b15 result chain_sha256 set                                  decide=FENCED       armed=False span=True  latch=0
b16 receipt row claims capture_writer_ran                    decide=FENCED       armed=False span=True  latch=0
b17 chain has no NIGHT_PAYLOAD_KIND and no RUNS_ROOT         decide=FENCED       armed=False span=True  latch=0
b18 RUNS_ROOT relative                                       decide=FENCED       armed=False span=True  latch=0
b19 ended_epoch_s in future                                  decide=FENCED       armed=False span=True  latch=0
b20 result plan_id mismatch                                  decide=FENCED       armed=False span=True  latch=0
c night_refused_registration delivered                       decide=FENCED       armed=False span=True  latch=0
c night_refused_class delivered                              decide=FENCED       armed=False span=True  latch=0
c night_refused_bind_mismatch delivered                      decide=FENCED       armed=False span=True  latch=0
c PASSED delivered                                           decide=FENCED       armed=False span=True  latch=0
c receipt reason disagrees with result                       decide=FENCED       armed=False span=True  latch=0
c eligible but undelivered                                   decide=FENCED       armed=True  span=True  latch=0
after completion delivered (base path, no probe)             decide=LAUNCHING    armed=False span=False latch=0 census_calls=0 driver_calls=0
```
Findings: no path returns LAUNCHING or disarms before nominal completion while (a) a courier or driver is observed alive, (b) any capture or reservation evidence exists on disk (including every symlink and non-directory shape, an unreadable RUNS_ROOT, a non-empty or symlinked envelope index), or (c) the refusal is not a zero-capture machine-state refusal (registration/class/bind-mismatch codes, PASSED verdict, receipt/result disagreement, undelivered). The only pre-completion LAUNCHING is the intended one: delivered eligible refusal, all disk facts clean, census and driver probe both empty on one tick. The one-way latch (a6b) is ruling 16's design, not a defect. The "armed=False, span=True" rows in (b)/(c) are the base disarm on `courier.sent` while the span hold continues, identical to main.

Note for (a): the census pattern covers the courier only through its `claude` path. The night plist template renders `--courier-bin @@COURIER_BIN@@`; an orphaned courier whose binary path lacks `claude`/`codex`/`t3` after the driver died would be invisible to both probes. In production that path is the session binary under `.../claude/versions/…` (record 10 executed it). Residual, recorded, not a cure.

## 3. Behaviour versus main for non-eligible refusals and normal GO nights

Enumerated from the diff and probes (record 23 V4's 72-case enumeration found the same three pre-completion differences):

Identical to main:
- Non-eligible delivered refusals (registration, class, bind mismatch, any code outside the five; receipt/result disagreement; chain fields set): `_delivered_zero_capture_refusal` is False → `plan_is_armed` falls to the base `courier.sent` disarm; `plan_span_active` holds to completion; no census beyond the base one; no driver probe (rows c above, `driver_calls=0`).
- GO/PASSED nights: `_terminal_refusal_result` is None → base logic throughout. Undelivered nights keep the dead-man tail (row "c eligible but undelivered" mirrors base).
- Eligible refusal outside the interval (before t0−8 min or after completion): not a candidate; base path, no probes (last row).

Different, intended by ruling 16 / lead:
- Eligible delivered refusal inside the interval: armed and span held until an observed empty tick, then released one-way (S1 of A234, ruling 16 Q1).
- Owner present on a hold tick with a pending release: `HOLD_CENSUS(adopt)` label instead of `STANDDOWN_<phase>(adopt)`; the resident supervisor still stands down via `relevant_standdown_plan` (record 10 N2). Only the eligible class reaches this.

Different, not named by ruling 16 (conservative, acceptable):
- Chain-started + exited + REFUSED + delivered: `plan_is_armed` stays True until completion (main: False at `courier.sent`). The checkout fence lasts longer; nothing launches earlier. Ruling 16 S1 discussed only the undelivered tail; this delivered case is the "more conservative" P1 of record 10 and record 23 V4's third difference.
- `decide()` now returns `HOLD_UNSAFE` on `snapshot.errors` before recomputing `state["fenced_checkouts"]` (main recomputed first). Stale-not-empty value on a no-launch tick (record 10 N3). Nit.
- Every tick now hashes each loaded plan's `result.json` for the key set and always writes `released_zero_capture_refusals` (possibly `[]`) into state. I/O and schema-additive only.
- Resident supervisor path (`ResidentSupervisor` step, line 2147) passes no state; `_release_observed` then reads `state.json` from disk and fails closed if unreadable (record 10 P4 executed). Consistent with `decide()`.

## 4. The two doc paragraphs

True against the code: every mechanism sentence checked — five codes (= `ZERO_CAPTURE_MACHINE_REFUSALS`), result/receipt agreement and null chain fields, `*.consumed.json` under custody or a calibration chain's absolute RUNS_ROOT, `instrument_validation` / `night/evidence` / empty index, interval bounds (8 min, `window_max_s`, 5 min), both probes empty on one tick, latch in `state.json`, no driver probe outside the interval or after the latch, one-way release, registration/class/chain-started keep the full hold. 300 s matches the magistrate template's `StartInterval`.

First-use test: passes for every term ruling 16 S3 named (machine state, tick, notice, owner veto, interval, harvest, successor). Both paragraphs are new relative to main (0 hits for their terms on main's handback). Four terms of art enter unglossed at first use in both files: **calibration chain**, **evidence night** (the two payload classes; the reader is not told how the watchdog tells them apart, namely the payload-kind literal in the plan's pinned chain file), **cold-gate review**, and **next-start planner**. "Agent census" leans on the preceding paragraph's "arm-time census is the process inventory", which is adequate. A reader can replicate the release mechanism from the text but not the class dispatch. Deferrable nit, exact wording in §5.

## 5. Should-fix before merge

None. The candidate carries no should-fix.

Deferred nits (docs-only, may ride the next bookkeeping push):
1. In both paragraphs, after "The watchdog also checks", add one clause: "The plan's pinned chain file names its payload class: a **calibration chain** exports `RUNS_ROOT` and captures under `<RUNS_ROOT>/instrument_validation`; an **evidence night** exports `NIGHT_PAYLOAD_KIND='quiet_predicate_evidence'` and captures under `night/evidence`." Gloss "cold-gate review" (a fresh-context Fable judge's written ruling before merge) and "next-start planner" (the code that chooses the successor's `t0`) at first use.
2. Restore `state["fenced_checkouts"]` recomputation before the `snapshot.errors` return in `decide()` (record 10 N3), or document that the value is stale on that tick.

NOT EXECUTED: live `pgrep`/launchd; the long CLI and installer modules (`test_magistrate_watchdog_cli.py`, `test_install_magistrate_watchdog.py`; record 12 V1 reports them green at 4c76ab69, not at 45889885); ruling 16's single-fact mutants (seat/record 23 report them killed); the earlier cold verdict 04; a real custody root.

## VERDICT

**MERGE.** Ruling 16 Q1 (F1, F2, F3, S1, S3, required tests 1–6), lead ruling 19 and the record 23 F1/F2 cures are each present in the code with a failing-input test, the three requested modules pass at 45889885 (269 tests), and 34 adversarial inputs through the production `decide()` produced no early LAUNCHING or disarm while a courier or driver was observed, any capture or reservation evidence existed on disk, or the refusal was outside the five machine-state codes. Behaviour for non-eligible refusals and GO nights is that of main; the only unnamed divergence holds longer, never shorter. The doc first-use gaps are four pointer terms and a class-dispatch clause, deferrable.

Judge: Fable 5.1, cold; scratch worktree removed after this file was written.
