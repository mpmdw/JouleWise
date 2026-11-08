# Opus delta check: four speed-engineering fix rounds (2026-11-08)

- **Reviewer:** Opus 5.5, cross-family delta check. Sol 6.1 applied all four fix rounds.
- **Date:** 2026-11-08.
- **Scope:** engineering only. For each Opus cold-review finding, is it really fixed, and did anything new break? No estimand, threshold, refusal meaning, registration or measured value is proposed or changed here.
- **Method:**
  - Read each fix diff against the head the cold review saw.
  - Ran the witnesses and touched test modules, one module per process, with `python3.13 -B -m unittest` on Python 3.13.18. All data was synthetic.
  - Ran a trial merge of each fix into its target.
  - No restricted, night-custody or night-archive path was read.

## Where the fixes actually live

Sol committed the code fixes to one branch name and its run reports to another. **All four pairs diverge**; neither branch in a pair contains the other.

| Item | Branch named in brief | What it holds | Fix branch (reviewed) | What it holds |
|---|---|---|---|---|
| Desk | `perf/2026-11-08-eng-desk` @ `7137e76bf` | pre-fix code + Sol report doc only | `perf/2026-11-08-fix-desk` @ `4214bacf7` | **the fix** (1 commit) |
| Kit cache | `perf/2026-11-08-eng-kitcache` @ `ad14c05f6` | pre-fix code + Sol report doc only | `fix-kitcache` @ `76be382aa` | **the fix** (`d0cc5b7c2` code, `76be382aa` docs) |
| Timing | `perf/2026-11-08-r0-timing` @ `27647f636` | pre-fix code + Sol report doc only | `fix-timing` @ `dc684b308` | **the fix** (`58f98632f` code, `dc684b308` docs) |
| Wake | `perf/2026-11-08-eng-prearm` @ `d51555b68` | pre-fix code + Sol report doc only | `perf/2026-11-08-fix-wake` @ `5f851edb9` | **the fix** (`2944e1fbd` code, `5f851edb9` docs) |

The wake fix existed **only locally** in `jw-wt/sol-fix-wake`; its report says "nothing pushed". I pushed it unchanged to `origin/perf/2026-11-08-fix-wake` (`5f851edb9`) so it can be cited and opened as a PR. Each eng-* "Sol run report" commit adds a single 8-25 line file under `docs/run_reports/interp-energy-desk/`. Cherry-pick it onto the fix branch if wanted; it contains no code.

## Verdicts

| Item | Target | Verdict | Ready to open the PR now? |
|---|---|---|---|
| Desk | `align/2026-11-08-v4-r11` | **ADMIT_WITH_FIXES** | **No.** It must be rebased onto the target head (`2cce80ede`), with 5 conflicting files (D-1). |
| Kit cache | `align/2026-11-08-v4-r11` | **ADMIT_WITH_FIXES** | **No.** It must be rebased, with 3 conflicting files; one has a resolution trap (K-1). |
| Timing | `align/2026-11-08-v4-r11` | **ADMIT** | **Yes**, from `fix-timing`. It merges cleanly and every file is new to the target. |
| Wake | `main` | **ADMIT_WITH_FIXES** | **No.** The parked pre-arm packet must be split out first (W-1). The code itself merges cleanly into `main`. |

**Nothing measured changes in any of the four.**
- The desk and kit changes are byte-equal on the synthetic witnesses, and the kit benchmark reports `exact_bytes_equal` and `filled_sizing_bytes_equal` against `05b6d04cb`.
- The timing reader is a record-only diagnostic.
- The wake change runs only after the driver's terminal reporting.

---

## 1. Desk: `perf/2026-11-08-fix-desk` @ `4214bacf7`

### Findings from the cold review

| Finding | Status | Evidence |
|---|---|---|
| **H1:** target binding | **Fixed** | `desk_record.py:190-229` derives targets with `harvest.build_roster` over the exported pack, using the same comprehension as `align_pilot_session.py:335-338`. Config locators are checked for containment first. If no pack is exported, or no target file, replay refuses. A supplied map must match the derived one. `test_desk_record_binding.test_targets_are_recomputed_with_build_roster_and_mismatch_refuses` covers it. The witness passes, but see D-2. |
| **H2:** harvest outcome | **Fixed as a binding** (the lead chose this) | The finalize manifest requires the MBP `desk.json` to carry `harvest_status: ok` and an exit code of 0 or 6, and it binds every archive digest plus harvest stdout and stderr (`desk_record.py:243-259`). Replay recomputes that manifest and refuses on a mismatch (`:362-364`). The CLI passes only on `instrument_ok` **and** harvest `ok` (`align_v4_record_desk.py:56`). See D-3 for what this does to the speed case. |
| **M1.1:** triage basis tied to an artifact | **Fixed** | `full_desk_gate: pass` now runs `validate_gate` (fix branch `v4_cadence.py:148-157`). It re-hashes PILOT and REPLAY, rechecks the pushed record commit and finalize manifest, and requires harvest `ok` and the previous window's identity. A non-empty `basis` alone fails. |
| **M1.2:** a lighter thermal/eligibility source | **Open** | This is a lead policy decision. The code does not relax it. |
| **M1.3:** landing counts as a code change | Acknowledged | A full desk pass is needed before the next arm after this lands. |
| **M2:** provenance tied to the MBP finalize | **Fixed** | v2 descriptors must bind an MBP `finalize_manifest` at the same commit. That commit must be an ancestor of a `refs/remotes/...records...` ref (`desk_record.py:262-296`). Session and plan IDs are cross-checked against `custody/night/result.json` (`:136-145`). |
| **M3:** export completeness | **Fixed** | `_required_files` (`desk_record.py:157-187`) names the run_clock and thermal journals (plain or `.zst`), the terminal and hazard results, the enumerated meter streams, the registration inputs and the harvest receipt and logs. |
| **M4:** parallel desk during a live window | **Fixed** | `host_desk_guard` (`desk_execution.py:25-52`) holds the host night lock through the desk and requires the launchd night job to be absent. It fails closed on an unknown state, and only `workers > 1` takes this path. `HostLock.release` only closes its own descriptor (`powermode.py:235-242`), so a failed acquire never drops the window's lock. |
| L1, L2, L3 | **Fixed** | Explicit output is created only after the analysis. The profile is written before publication, and a profile failure no longer masks the original error. Publication claims the directory with an exclusive mkdir. |
| L4, L5, L6, L8 | Documented, or covered by the imported witness | |
| L7 | Open | Per-task timeout and RSS remain open. Keep the 2-worker cap on the 24 GB Air until a real-record RSS measurement exists. |

Witness-file changes are limited to two things:
- a host-guard mock confined to the current tree (the base tree has no guard module);
- the L1 assertion `self.assertFalse(output.exists())`.

The byte, order and H1 assertions are unchanged.

### New or remaining findings

**D-1 (MED, blocks the PR): stale against the target.**
- The fix-desk branch forks from `50c99e4f8`. It carries the R12 `v4_cadence.py` and the arm-triage plumbing **copied from `05b6d04cb`**.
- The target has since advanced to `2cce80ede`. `f993b784f` rewrote `next_arm_triage` (new `identity` parameter, artifact-set digest).
- `git merge-tree` reports conflicts in `joulewise/align/apple/v4_cadence.py` (add/add, 12 hunks), `scripts/align_v4_session.py` (5), `tests/align/test_v4_cadence.py` (add/add, 11), `tests/align/test_v4_kit.py` (2) and `tests/align/test_v4_registration.py` (2).
- **Fix:**
  1. Rebase onto the target head.
  2. Take the target's `v4_cadence.py` and `align_v4_session.py` as they are.
  3. Re-apply only the fix's own deltas:
     - the `validate_gate` hook inside the target's `next_arm_triage`;
     - the eng-desk `_thermal_desk_member`/`DeskExecution` split in `powermode_desk_check`;
     - `host_desk_guard` in `desk()`.
  4. Re-run `test_v4_cadence`, `test_v4_registration`, `test_v4_kit`, `test_desk_record_binding`, `test_desk_equivalence_review`, `test_r11_delta_sol1/2` and `test_v4_opus_cold_witnesses`, one module per process.

**D-2 (LOW): the imported H1 witness now passes vacuously.**
- `test_desk_equivalence_review.py:361-364` returns on *any* `ValueError`.
- Under v2 its self-written descriptor has no `records_ref`, so replay refuses at `desk_record.py:265-267` before targets are ever compared.
- The real H1 coverage is `test_desk_record_binding.py:136-157`, and it is sound.
- **Fix:** make the witness assert that the refusal names the target or pack mismatch, or drive it through a v2 finalize so equal eligibility is compared.

**D-3 (INFO, lead decision): the laptop replay now saves no MBP time.**
- H2 was resolved by binding, not by relocating the harvest.
- Finalization requires `session/desk.json` from a `harvest=True` MBP desk (`desk_record.py:249-252`; written at `align_pilot_session.py:430-436`). That desk also runs every member read, the analysis and the thermal desk.
- So the replay is an independent re-verification. The only MBP saving on this branch is `--workers N` on the MBP desk: per the cold review, 10-15 min of non-harvest work becomes about 4-6 min at 4 workers.
- Moving that remainder off the MBP needs a harvest-only MBP mode. Sol's report says the same.

**D-4 (LOW):**
- The records-ref trust anchor is a local remote-tracking ref (`desk_record.py:264-270`), which `git update-ref` can forge. Sol documents this.
- The launchd absence check matches exact `launchctl print` stderr text (`desk_execution.py:46-48`). A macOS wording change fails closed, refusing `workers > 1` only.

### Tests (fix head, one module per process)

| Module | Result |
|---|---|
| `tests.align.test_desk_equivalence_review` (whole-tree witness, including H1) | 8 OK |
| `tests.align.test_desk_record_binding` | 19 OK |
| `tests.align.test_desk_parallel` | 13 OK |
| `tests.align.test_v4_cadence` | 15 OK |
| `tests.align.test_v4_registration` | 20 OK |
| `tests.align.test_thermal_desk` | 25 OK |
| `tests.align.test_pilot3.DeskTests` | 3 OK |
| `tests.align.test_pilot4.AnalysisTests` | 8 OK |
| `tests.align.test_v4_powermode_record` | 9 OK |
| `tests.align.test_v4_kit` | 116 OK |

---

## 2. Kit cache: `fix-kitcache` @ `76be382aa`

### Ruling compliance: delete both caches, keep the batched Git reads

| Item | Status | Evidence |
|---|---|---|
| **HIGH-1:** receipt cache | **Deleted** | `_has_git_replacements`, `_committed_oids`, `_cache_*` and the `cache` parameter are gone. `validate_receipt` compares all committed bytes on every call. |
| **MED-1:** generation cache | **Deleted** | `generation_input_digests`, `_generation_files`, `--no-cache` and `ThreadPoolExecutor` are gone. `_generate` always runs `build_files`. |
| **Batched reads kept** | Yes | `_git_batch` and `_git_blobs` (stricter parse: truncation, non-blob and trailing output refuse). `_frozen_sources` is an invocation-local snapshot of 10 immutable commit objects, used by `build_files` and `--check`. Working-bytes-first ordering is kept. |
| **MED-2:** worktree alternates | **Fixed** | `test_v4_kitcache.py:50` uses `--git-common-dir`. `test_v4_kitcache` passes in a `jw-wt` worktree, and so does the benchmark (below). |
| LOW-1 | Gone with MED-1 | |
| LOW-2 | **Reverted** | Back to `Path(output_root) / path`. |
| LOW-3 | Remains, disclosed | A tree, ambiguous or non-blob spec now reports "commit unreadable" rather than "missing committed artifact". This changes a message only, never the refusal itself. |
| LOW-4 | Gone with MED-1 | |

Witnesses: `tests/align/test_v4_kitcache_opus_witnesses.py`, 3 OK. Byte equality: `scripts/benchmark_align_v4_kitcache.py --baseline-ref 05b6d04cb --rounds 3` in a worktree gives `exact_bytes_equal: true` and `filled_sizing_bytes_equal: true`, and the pending refusal and receipt are equal. Medians on the Air were:

| Path | Legacy (s) | Batched (s) |
|---|---:|---:|
| Pending generate | 0.94 | 0.046 |
| Filled generate | 1.00 | 0.049 |
| Pending check | 0.97 | 0.051 |
| Synthetic static arm | 1.05 | 0.16 |
| Receipt | 0.102 | 0.099 |

`scripts/align_v4_kit.py --check` reaches the expected R0/R1 placeholder refusal with no generated drift.

### New or remaining findings

**K-1 (MED, blocks the PR): stale against the target, with a resolution trap.**
- The target's `f993b784f` added `artifact_set_digest` and two-tier amendment admission to `validate_receipt`, and regenerated `plan_tree.json` and `identity_pins.json`.
- A merge conflicts in those 3 files.
- In my trial merge, Git's auto-merged body combined the fix's strict working-first loop (`digest(raw) != expected` → refuse) with the target's tier check. That tier check then reads a **stale `raw` from the previous loop**. The result refuses every legitimate amendment-tier change.
- The target's own tests catch it: `test_v4_receipt_tiers` 6 errors, `test_r11_delta_sol1` 2, `test_v4_registration` 1. The kitcache witnesses still pass, so they would not catch it.
- **Correct resolution (tested):**
  1. Keep the target's `artifact_set_digest`, `_amendment_chains` and tier messages, and add the fix's `_git_batch`/`_git_blobs`.
  2. Make the working-first check amendment-aware, and run it before any Git I/O: `if digest(raw) != expected and digest(raw) != amended.get(path): raise ... (tier)`.
  3. Then run one batched committed-bytes loop.
  4. Regenerate the kit with `python3.13 -B scripts/align_v4_kit.py`.
- On that trial merge these all pass: `test_v4_kitcache_opus_witnesses` 3, `test_v4_kitcache` 16, `test_v4_receipt_tiers` 7, `test_r11_delta_sol1` 8, `test_r11_delta_sol2` 6, `test_v4_opus_cold_witnesses` OK, `test_v4_registration` 21, `test_v4_executed_closure` 4, `test_v4_kit` 116 and `test_w1_kit_r10` 30. `--check` reaches the same placeholder refusal.
- The target's receipt bindings are still `null` (unfilled), so no rebind is due now.

**K-2 (LOW):** the benchmark's default `--baseline-ref origin/align/2026-11-08-v4-r11` (`benchmark_align_v4_kitcache.py:59`) is a moving branch. Run as is, it now fails its own equality assertion, because the target's `align_v4_kit.py` has moved. Pin the default to the merge base, or require the argument.

### Tests (fix head, one module per process)

| Module | Result |
|---|---|
| `tests.align.test_v4_kitcache_opus_witnesses` | 3 OK |
| `tests.align.test_v4_kitcache` | 16 OK |
| `tests.align.test_v4_registration` | 20 OK |
| `tests.align.test_w1_kit_r10` | 30 OK |
| `tests.align.test_v4_executed_closure` | 2 OK |
| `tests.align.test_v4_kit` | 116 OK |

---

## 3. Timing reader: `fix-timing` @ `dc684b308`

### Findings from the cold review (Branch 2)

| Finding | Status | Evidence |
|---|---|---|
| **HIGH-B1:** clock drift | **Fixed** | With a mapping, drift becomes a warning and is added to the uncertainty (`window_timing.py:483-487`); it never vetoes placement. With only paired stamps, placement refuses only when drift exceeds the bracket uncertainty plus a 20 ppm allowance with a 1 ms floor (`:45-46`, `:500-502`). Both are labelled reader diagnostics, not capture rules. The witness covers 120 s, 1 h and 16 h at 9.2 ppm in both clock paths. |
| **MED-B1:** member without `run_finalized` | **Fixed** | Bounds fall back to the member's event envelope, labelled `event_envelope_incomplete_run` (`:441-448`). An episode outside it is unplaced. With no bounds at all, placement refuses (`:520-523`). The witness confirms the 1,000 s shift no longer inflates the window. |
| **MED-B2:** R1 gaps | **Fixed** | Each attempt now reports `gap_before_ns` (`:345`), the requested `os_batch_wait` marked "requested, unmeasured", and the recorded `g0_release` wait. Only measured epoch boundaries enter the disjoint ledger; bare `g0.start_ns` (episode monotonic) is never placed. A requested-wait position is an annotation that is kept out of the ledger. Today's R1 rows carry `g0_wait_s` plus a monotonic `g0` row, so those waits show as labelled-but-unplaced. That answers "where do R1's hours go" without guessing. |
| LOW-B2 | Fixed | The envelope warnings use the ppm allowance. |
| LOW-B3 | Fixed | A lone `chain.started` or `chain.exited` enters the bounds (`:625-627`). |
| LOW-B4 | Fixed | The worksheet column is `decode_excluding_tools`, with a note that native `phases_s.decode` includes tools. |
| LOW-B1 | Unchanged by design | Custodian export control remains the guard. |

- The original two review witnesses are unchanged in `tests/align/test_window_timing_opus_witness.py`; Sol only added assertions and cases.
- One existing test, `test_window_timing.py`, now sets `clock_mappings = []` so that it exercises the paired-stamp refusal. That matches the review's prescription that a mapped step is diagnostic, not a veto.
- **No capture code changed.**

**`docs/perf/TIMING-RECEIPTS.md`** is checked. It is a proposal-only design note: no capture change, no registration, no permission to instrument a window. I spot-checked about 40 of its source anchors at the pinned base `dfde96979` (R1 rehearsal, r1_runtime, magistrate_watchdog, run_night, r0_host, thermal_gates, launch_window, chain.py, backup_runs.sh). All of them point to the named operation; the push anchor `run_night.py:1594-1600` is `git push` inside `observed_run`. It keeps requested delays separate from measured ones, treats a missing end as open rather than zero, and requires registration before capture. This is accurate.

### Remaining notes (INFO, none blocking)

- **Open the PR from `fix-timing`, not `r0-timing`.** The two diverge: `r0-timing` holds only the Sol report commit, and `fix-timing` lacks that report.
- **The PR includes un-reviewed R0 code.** It carries the R0 timing extension (`43a3e21eb`: `window_timing_r0.py`, plus the `read_window` R0 hook; `39ea05ab4`: R0 rerun ledger docs). That was outside the Opus cold review, which covered `44fb124cc`. A skim found it stdlib-only, reading named blobs through the same `blob()` path, with no outcome or energy keys. Have the PR reviewer give it a short read.
- **Python 3.11 was not available here.** CI should cover it.

### Tests (fix head, one module per process)

| Module | Result |
|---|---|
| `tests.align.test_window_timing_opus_witness` | 17 OK |
| `tests.align.test_window_timing` | 25 OK |
| `tests.align.test_window_timing_r0` | 14 OK |
| `tests.align.test_records` | 4 OK |

Every file on this branch is new relative to the target, so the merge is independent of R12 code.

---

## 4. Terminal wake: `perf/2026-11-08-fix-wake` @ `5f851edb9`

### Findings from the cold review

| Finding | Status | Evidence |
|---|---|---|
| **W-M1:** spurious `hold_census` | **Fixed** | `run_night._finish_reporting` now starts `terminal_wake.notify_after_exit`, a detached observer. It publishes only after `os.kill(pid, 0)` raises ESRCH, so the driver's close and finally tail is over (`terminal_wake.py:18-55`). On timeout, permission error or PID reuse, the 300 s tick is kept. The observer runs in its own session (outside the job's process group) with `close_fds=True`, so it holds no night lock. Its argv cannot match the driver census `pgrep -lf [r]un_night\.py` (`magistrate_watchdog.py:81`). The review witness, copied verbatim, passes. |
| **W-L1:** census-event burst | **Fixed** | `tick_on_terminal_event` makes at most 31 driver-only probes, with no transition, census row or notice, then one ordinary tick (`magistrate_watchdog.py:3191-3196`). A persistent driver still gets its genuine hold and notice. |
| **W-L2:** wake-root mismatch | **Fixed** | `validate_terminal_wake_destination` (`night_agent_install.py:49-77`) compares the installed magistrate plist's `WatchPaths` and `MAGISTRATE_WATCHDOG_CUSTODY_ROOT` with the night destination. A mismatch refuses with exit 2. Render and probe stay off-host. |
| **W-L3:** no-marker exit paths | **Documented and tested** | The no-courier and dead-man paths keep the 300 s fallback. A test pins `_notify_terminal` as not called on dead-man completion. |
| **T-L1:** symlinked TMPDIR | **Fixed for wake scope** | The test roots and internally created probe temp dirs are resolved; production destinations stay strict. I ran the wake modules with `TMPDIR` routed through the `/tmp` symlink. |

**The packet half is unchanged.** `joulewise/prearm_packet.py`, `scripts/prearm_packet.py`, `scripts/bench_prearm_packet.py` and `tests/test_prearm_packet.py` are byte-identical to `348c4a70b`. `docs/contracts/prearm_packet.md` changed only in its `## Terminal wake` section (line 115 onward). P-H1 stays open and parked.

### New or remaining findings

**W-1 (MED, blocks the PR): the branch still carries the parked packet.** The review's disposition was "split the branch". `perf/2026-11-08-fix-wake` is based on `2f4cb41bd`, which adds the packet and the wake together.
- **Fix:** open the `main` PR from a branch that contains only the wake.
  - Keep the plist templates, `terminal_wake.py`, the `run_night`, watchdog, installer and install-script hunks, and the wake tests.
  - Drop the packet modules, the packet CLI, the packet benchmark and `tests/test_prearm_packet.py`.
  - Move the `## Terminal wake` section of `docs/contracts/prearm_packet.md` into its own contract doc.

**W-2 (INFO, rollout order):** after this lands, every *actual* night install refuses until the watchdog is reinstalled from this code. The installed magistrate plist on the MBP has no `WatchPaths` yet, so `night_agent_install.py:71` fails closed. The fix is to reinstall the watchdog first, then refresh the plist pins, in an authorized gap. Sol's handoff lists the reinstall but not the order.

**W-3 (LOW):** the observer inherits the driver's stderr (`terminal_wake.py:25-31` redirects stdin and stdout only). Its failure line ("terminal wake unavailable…") can be appended to the night launchd stderr log after the driver has exited, and so after the durable record. That is harmless today. Consider `stderr=DEVNULL` with a log line written by the driver before it spawns the observer, or a dedicated log in the magistrate root.

**W-4 (INFO):** native launchd validation is still owed, in a gap with stub jobs. Check that the observer survives the job exit and that WatchPaths fires on `os.replace`. Then run the three `NightProbeTests` that Sol's sandbox could not run (see the table below) and the orphan census.

### Tests (fix head, one module per process; `TMPDIR` through the `/tmp` symlink unless noted)

WAKE_TESTS_TABLE

The packet half was run separately with an unsymlinked `TMPDIR`, because its T-L1 fix is parked with P-H1.

---

## Reproduction

```sh
# fix heads: perf/2026-11-08-fix-desk 4214bacf7, fix-kitcache 76be382aa,
#            fix-timing dc684b308, perf/2026-11-08-fix-wake 5f851edb9
python3.13 -B -m unittest tests.align.test_desk_equivalence_review       # desk, H1 witness module
python3.13 -B -m unittest tests.align.test_v4_kitcache_opus_witnesses    # kit cache
python3.13 -B scripts/benchmark_align_v4_kitcache.py --baseline-ref 05b6d04cb --rounds 3
python3.13 -B -m unittest tests.align.test_window_timing_opus_witness    # timing
python3.13 -B -m unittest tests.test_terminal_wake_witness               # wake
git merge-tree --write-tree origin/align/2026-11-08-v4-r11 <fix head>    # D-1, K-1 conflicts
```

No model, study data, restricted directory or measurement host was touched. The trial merges were scratch worktrees and were not pushed.
