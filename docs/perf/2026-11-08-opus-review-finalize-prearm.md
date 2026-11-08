# Opus cold review: eng-finalize and eng-prearm

Cross-family review (Claude Opus 5.5) of two Sol 6.1 engineering branches. Brief: latency synthesis §4 ranks 3 and 5 (`perf/2026-11-08-latency-synthesis` @ `55029b860`) and RUN_STATE 213-217 on `main` @ `ae60ae22c`. Engineering only: I checked that nothing changes what is measured, custody semantics or the meaning of any arm rule.

| Branch | Head reviewed | Verdict |
|---|---|---|
| `perf/2026-11-08-eng-finalize` | `fdcc73d74` | **ADMIT_WITH_FIXES**: safe to merge, but it saves seconds, not minutes, on the v4 path (F-M1) |
| `perf/2026-11-08-eng-prearm` | `348c4a70b` | **HOLD as one unit. Split it:** terminal wake ADMIT_WITH_FIXES (W-M1, T-L1); pre-arm packet HOLD (P-H1) |

Method: I read both diffs and reports in full, plus the code they call (`magistrate_watchdog.decide/tick`, `arm_retry.terminal_window_release`, `run_night._durable_record/_finish_reporting/run_courier`). I traced the ALIGN v4 finalize and harvest path on `lane/2026-11-06-v4-r1-integrated` @ `e901eb2a4`. Tests ran one module per process with `python3.13 -B -m unittest`, on synthetic data only, and never as the full suite. No restricted path, night-custody or night-archive was opened.

## 1. eng-finalize: bounded parallel hashing and incremental manifests

### What holds

- **Byte-identical custody output in every non-race case.**
  - Harvest manifests keep sorted keys, rows, modes, sizes, `mtime_ns` and literal symlink text. `dict(hashes.map(...))` consumes the results in input order, so the manifest order equals `sorted(rglob)` for 1, 2, 4 and 8 workers.
  - The night artifact list keeps its order, its missing-file omission and its error entries. The `os.walk` failure path appends the same entries in the same order, followed by the diagnostic.
- **Same refusals on corruption, missing files and interruption.**
  - Destination and existing-archive inventories always use a fresh `FileHashes` (`scripts/harvest_window.py:510,528`), so copy corruption is still caught by a full byte re-read.
  - A failed read never caches a digest (`joulewise/file_hashes.py:56-68`).
- **The cache is sound on APFS.**
  - The identity is (dev, ino, mode, nlink, size, mtime_ns, ctime_ns) for both the link and its target.
  - A rewrite with restored mtime still moves ctime, a replacement moves the inode, and the cache never outlives one CLI invocation (`hash_scope`, `scripts/run_night.py:5212`).
  - Admission and gate hashes (`_sha256_path`, `run_night.py:189`) bypass the cache.
- **Memory is bounded, and lower than before.** Reads are 1 MiB chunks, at most `workers` futures are pending, and the old whole-file `read_bytes` is gone.
- **Concurrency.** Threads are joined on every exit: `with ThreadPoolExecutor` runs `shutdown(wait=True)` after the generator's `finally` cancels the queued work. Dict access under the GIL is safe. `--hash-workers` defaults to 1, and the installed launchd argv and plist digests are unchanged.
- **It never hashes a file mid-write without noticing.** Identity is checked before the open, at the open (fstat), after the read and after the path re-stat (`file_hashes.py:21-31,57-64`). A writer that stays idle for the whole read gives a consistent snapshot, exactly as the old `read_bytes` did.

### Findings

**F-M1 (MED): the change misses the v4 critical-path I/O.**
- **Failure scenario.** The magistrate adopts `--hash-workers 4` expecting the 10-30 min finalize saving in synthesis row #5 and sees about none.
  - The 18.71 / 26.45 GB per copy (L1 M24) flows through the ALIGN harvest: `align_pilot_session.desk` → `scripts/harvest_b6_session.py` → `joulewise/b5/harvest.py`, which already takes `Seams(workers=...)`.
  - `scripts/harvest_window.py` is not referenced anywhere on the v4 lane. `CANONICAL.md` lists it under the G2-a/B5 family.
  - The only v4-relevant change is `run_night`'s terminal inventories of `night/` and `night/evidence/`. These are the result inventory plus one to three durable-record inventories (`run_night.py:1510, 2070, 2300-2312, 1819`). The cache makes the second and later passes free.
- **Port needed.** Both branches target `main`, but v4 runs `run_night.py` from the R1 integration lane, where the file differs by +585/-30 lines. The patch applies cleanly to `lane/2026-11-06-v4-r1-integrated` and to `align/2026-11-08-v4-r11` (`git apply --check`), but it needs a port and a re-run of the lane's `tests.test_run_night`. RS 216 also forbids touching the R1 lane while R1 is armed.
- **Fix.**
  - Correct the report's framing.
  - If finalize really costs minutes, profile `joulewise/b5/harvest.py` and the offload/copy path. That is where the bytes are.

**F-L1 (LOW): race semantics change. A file that changes while it is being hashed is now omitted instead of given a snapshot digest.**
- **Scenario.** A courier group that outlives its kill (`prove_group_absent=False`, `run_night.py:1970, 1985`) rewrites `courier.heartbeat` during "durable record after courier".
  - **Before:** the file got a digest of whatever bytes were read and was copied to the results branch.
  - **Now:** `OSError` ("file changed while hashing") produces an `error` entry, so the file is omitted from the branch and named in the diagnostic (`run_night.py:1383, 1513-1515`).
- The same stricter behaviour reaches the admission callers of `_sha256_path` (for example `run_night.py:4125, 4215`). A concurrent writer there is not expected, but now raises instead of hashing.
- This fails closed and is arguably more honest, since the old digest rarely matched the copied bytes. It is still not "same refusals on races", which is what the brief asks for.
- **Fix.** Retry up to three times for a stable snapshot before declaring the error, and document the race semantics.

**F-L2 (LOW): cache reuse assumes fine-grained timestamps.**
- **Scenario.** On exFAT or HFS+ (an external SSD record copy, once the SSD qualifies), a same-size rewrite inside the timestamp granularity keeps the identity unchanged. A second inventory in the same invocation would then reuse a stale digest.
- Today's custody roots are internal APFS, and destination checks re-read the bytes regardless.
- **Fix.** Disable reuse when `statfs` does not report `apfs`.

**F-L3 (LOW): with workers > 1, a TERM/INT during hashing waits for the in-flight whole-file hashes.** `shutdown(wait=True)` runs after `future.cancel()` (`file_hashes.py:95-98`). The delay is bounded by the largest file divided by disk throughput. With the default of 1 worker, behaviour is unchanged.

**F-L4 (LOW): `current_hashes()` silently falls back to a fresh uncached instance off the main context** (`file_hashes.py:115-116`). ContextVars do not cross `threading.Thread`, so this only loses speed, never correctness. Noted so that nobody later "fixes" it by sharing the cache across threads.

**Tests (this review, native macOS, branch head):**

| Module | Result |
|---|---|
| `tests.test_finalize_hashes` | 13 OK, 0.18 s |
| `tests.test_harvest_window` | 39 OK, 31.0 s |
| `tests.test_run_night.CourierDeliveryBoundaryTests` | 19 OK, 9.9 s |
| `tests.test_run_night.NightDriverTests` | 132 OK, 41.8 s |

No HIGH finding, so no witness was required.

## 2. eng-prearm: immutable pre-arm packet and terminal-event wake

### 2a. Pre-arm packet (`joulewise/prearm_packet.py`): HOLD

**What holds:**
- Packet bytes are pinned by an externally supplied digest. Canonical JSON and the recipe digest are enforced.
- The full file and tree inventory is re-hashed, including executable bits and empty directories. Added tree members refuse.
- Symlinks, traversal and restricted path components refuse.
- Freshness is the minimum of `not_after_epoch_s`, plan authored time + `PLAN_MAX_AGE_S` (36 h) and the receipt expiries, and the window is `issued <= now < expires`. A build-host clock ahead of the MBP refuses (fails closed).
- Publication is exclusive (`os.link`) and never replaces an existing packet.
- Verify runs no validators.

**What does not hold:** the packet is not wired into anything. No ALIGN adapter or production recipe exists (the report's own NEEDS_RULING), so today it skips no check and saves nothing.

**P-H1 (HIGH, failing-first witnesses): the packet binds less than the validators read, so it can vouch for a check that would now refuse on the MBP.** That would weaken an arm rule the moment an adapter consumes it. Three ways in:

1. **The execution environment is not bound.**
   - `run_checks` passes the whole build-host environment through (`prearm_packet.py:188`) and runs `sys.executable`.
   - The interpreter version, site-packages and environment variables are not in the packet.
   - An Air-built PASS for a check that depends on an installed package version, or on an environment pin, verifies on an MBP whose environment would fail it.
2. **Dependency closure and a dirty tree are unchecked.**
   - The only code binding is `git rev-parse HEAD` (`prearm_packet.py:165`) plus the recipe's own inventory.
   - An uncommitted edit to a module the validator imports, but which the recipe left out of the inventory, keeps HEAD and the snapshot unchanged.
3. **Host observations can be cached.**
   - The four `CHECKS` names are labels (`prearm_packet.py:26, 112-128`). Any bound `{root}/*.py` may run under any of them, including a script that reads battery, thermal or volume state.
   - The packet then carries the build host's physical state to the arming host. Nothing in code, only "recipe review", stops this. The brief requires that the packet cannot vouch for a fresh physical check.

**Witnesses.** The file is `docs/perf/2026-11-08-opus-review-witnesses/test_prearm_packet_witness.py` (copy it to `tests/` on the branch and run it with a real `TMPDIR`).
- Each test first proves that `run_checks` now refuses, then asserts that `verify` refuses too.
- On `348c4a70b` all three tests fail at the second assertion with "PacketError not raised: packet vouched for a check that now refuses".

**Fix (all three before any adapter consumes results):**
- **(a) Bind the environment in the packet.** Record `sys.version`, a digest of `sys.executable`, a sorted `importlib.metadata` distribution list, and an allow-listed environment. At build, run the validators with exactly that environment. At verify, compare against the MBP interpreter.
- **(b) Bind the dependency closure.**
  - Run each validator under an audit hook or `sys.modules` dump, and refuse at build if any loaded file under `{root}` is outside the inventory.
  - Require `git status --porcelain --untracked-files=no` to be empty at build and at verify.
- **(c) Pin checks in code.** Map each `CHECKS` name to a fixed script path in code, reviewed like any gate. Refuse any validator that touches `pmset`, `powermetrics`, `ioreg` or `diskutil`, or reads outside `{root}`.

**P-L1 (LOW): `verify` is not single-use.** One packet verifies any number of times until it expires. That is harmless while the packet confers no authority. If an adapter ever treats a verify as a once-only token, record the packet digest in the arm record and refuse a reused digest.

### 2b. Terminal-event wake: ADMIT_WITH_FIXES

**What holds against the brief:**
- **Missed event.** `StartInterval=300` and `RunAtLoad` stay (test `test_watchpaths_keeps_watchdog_fallback`). A lost or suppressed WatchPaths edge degrades to today's behaviour.
- **Duplicated event.**
  - A digest of the raw marker (including its nonce) is deduped through `terminal-wake-seen.json` under `service_lock`. A repeat edge runs exactly one ordinary tick.
  - Concurrent instances return at `descriptor is None` before touching the marker.
- **Never arms early or twice.**
  - The watchdog never arms a window. It only launches the magistrate session.
  - The launch goes through the unchanged `decide()` gates: plan span, chain open, the PLAN2 X1 census-backed release (courier.sent, result, `chain.exited`, an empty agent census and an empty driver census), desk fence, STOP, clock and network, backoff and `_launch_fence`.
  - The resident supervisor holds `service_lock`, so a second launch cannot start.
  - The retry loop exits on the first launch or adopt (`magistrate_watchdog.py:3190-3196`). It retries only FENCED and HOLD_CENSUS, and only for a fresh marker (age 0-60 s, `:3189`).
  - The v4 W1 plan is `HAZARD_PACK` (`configs/campaigns/align_v4/night_plan.template.json:187` on the lane), so the early terminal release applies.
- **No arm rule weakened.** Quiet dwell, meter samples, battery, thermal and volume checks stay in the magistrate and arm path, which this change does not touch.
- **Publication.** The marker is written only after the durable courier outcome (`run_night.py:2318`, after `_durable_record`). A publication failure keeps the reporting exit code.

**W-M1 (MED, witness): every window now raises a spurious `hold_census` notice to the magistrate, and through it to Ed.**
- **Scenario.**
  - The marker is published before `run_night` exits. On the v4 lane the powermode close and lock retake also come after it.
  - The first event tick therefore sees the driver alive: `release_held` (`magistrate_watchdog.py:2110`) gives `Decision("HOLD_CENSUS", ...)` (`:2209`).
  - That is a FENCED → HOLD_CENSUS transition, and `tick` attaches `notice="hold_census"` (`:3079-3080`) to `notice_pending`, which is rendered into the magistrate prompt (`:2265`).
- With 300 s polling, a tick almost never lands inside the driver's exit tail.
- **Harm.** A routine alert every window trains people to ignore the real census-hold alert.
- **Witness.** `docs/perf/2026-11-08-opus-review-witnesses/test_terminal_wake_witness.py`.
  - The wake reaches LAUNCHING, but `notice_pending == ['hold_census']`. The control case (driver already gone) queues nothing.
  - It fails on `348c4a70b`.
- **Fix.** In `tick_on_terminal_event`, run the retry ticks so that a HOLD_CENSUS caused only by the driver probe does not transition or notice until the retry budget is spent. Simpler: publish the marker as the driver's very last act, after the close.

**W-L1 (LOW): the retry loop records up to 31 census events per window** (`append_census_event` on every tick), plus about 30 s of `ps`/`pgrep` activity. This only happens between windows, so it is log noise, not contention. The fix for W-M1 could also log only the first and last attempt.

**W-L2 (LOW): a mismatched wake root silently disables the wake.**
- The night installer binds `MAGISTRATE_WATCHDOG_CUSTODY_ROOT`, or else a default, at render time (`joulewise/night_agent_install.py:663`). The watchdog watches its own custody root.
- If they differ, `publish` refuses ("not installed") or writes to a stale directory, and only the 300 s fallback remains. The failure is swallowed by `optional()` after the last durable log.
- **Fix.** The night installer reads the installed magistrate plist's WatchPaths and refuses on a mismatch.

**W-L3 (LOW): some exit paths publish no marker.** The no-courier path and the dead-man path (`run_night.py:2296-2309` on the prearm head; the dead-man tail near `:4600-4640`) never reach `_finish_reporting`'s wake, so they rely on the fallback. That is acceptable; it should be documented.

**T-L1 (LOW): the tests are not portable to a stock macOS `TMPDIR`.**
- With the default `TMPDIR` (`/var/folders/...`, and `/var` is a symlink to `/private/var`), 9 of 12 in `tests.test_prearm_packet` and 4 of 10 in `tests.test_terminal_wake` fail on the symlink refusal. They pass with an unsymlinked `TMPDIR`.
- The magistrate will hit this on the MBP.
- **Fix.** Use `.resolve()` on the temporary roots in the tests, and keep production strict.

**Integration notes (INFO):**
- The night and magistrate plist template changes alter rendered digests, so the pins and probes need a refresh. Existing installs are untouched until reinstalled.
- The patch applies cleanly to both v4 lanes. The lane's `night_agent_install.py` differs by +24/-3, so re-run `tests.test_night_agent_install` there.

**Tests (this review, native macOS, branch head, `TMPDIR` unsymlinked):**

| Module | Result |
|---|---|
| `tests.test_prearm_packet` | 12 OK |
| `tests.test_terminal_wake` | 10 OK |
| `tests.test_magistrate_watchdog.TerminalWindowReleaseTests` | 19 OK |
| `tests.test_night_agent_install.RenderedProcessTypeTests` | 2 OK |
| `tests.test_install_magistrate_watchdog` | 10 OK |

## 3. Realistic saving per window on the MBP critical path

RS 213's four MBP steps run in sequence: finalize/hash/push, cool-down (15-25 min of physics), pre-arm checks, then dwell.

| Change | Saving per window | Basis |
|---|---|---|
| eng-finalize, as merged to `main` | **0** until ported to the v4 lane. After the port, **seconds**: (passes - 1) × the serial hash time of `night/` + `night/evidence/`, which the cache removes. Workers help only if the evidence is GB-scale | Unmeasured. The GB-scale custody path is not touched (F-M1) |
| Pre-arm packet | **0** today, because nothing consumes it | Upper bound after P-H1 and an adapter: the four static validators' native runtime minus verify (re-hash plus `git`). The fixture saved 43% of 0.24 s. Probably 1-5 min at most; unmeasured |
| Terminal wake | **About 2-2.5 min mean, 5 min max**. That is the poll phase (150 s mean under the uniform-phase assumption, 300 s max) minus the 1-30 s driver-exit tail | This counts only if the magistrate's activation is on the sequential path, as RS 213 orders it |

**Total: about 2-3 minutes of a 30-45 minute turnaround.** Cool-down and quiet dwell dominate. Neither branch changes what is measured.

## 4. What the magistrate must benchmark in a gap (after close, never during a window)

Use an unsymlinked `TMPDIR` for every test run on the MBP.

1. **Finalize: locate the minutes first.**
   - Timestamp the real RS 213 step 1 phases on one closed v4 record: `result.json` write, the durable-record commit/push, `harvest_b6_session` hashing and compression, the copy to the second location, and the destination re-read.
   - Record file count and bytes for `night/` + `night/evidence/` separately from the runs tree.
2. **Finalize hashing, only if step 1 shows hashing matters.**
   - Run `python3.13 -B scripts/benchmark_finalize_hashes.py --closed-root <closed night dir> --workers 1 2 4 8 --passes 3 --repeats 3`, and note page-cache state.
   - Also run `tests.test_run_night.HazardPackPrimitiveTests` natively (Sol could not).
3. **Terminal wake, after the W-M1 fix, with a synthetic plan and stub jobs.**
   - Measure marker → first tick and marker → LAUNCHING.
   - Confirm that launchd WatchPaths fires on an `os.replace` of `terminal-wake.json` on the MBP's macOS build.
   - Lost edge (job unloaded while the marker is written): recovery within ≤ 300 s.
   - Duplicate marker: exactly one ordinary tick.
   - Check that `notice_pending` stays empty and count the `events.jsonl` rows.
4. **Pre-arm packet: nothing to benchmark until P-H1 is fixed and an adapter exists.** First time the four real static validators natively, to see whether any saving is worth building.

## 5. Recommended disposition

- **eng-finalize.** Merge after F-L1 (bounded retry) or after documenting the race semantics. F-L2 can follow. Then open a separate port to the v4 lane once R1 has closed (RS 216).
- **eng-prearm.**
  - Split the branch. The terminal wake lands with the W-M1 and T-L1 fixes, then the plist pin refresh, then step 3 above.
  - The packet stays unmerged until P-H1 (a)-(c) are fixed, the three witnesses pass, and the lead rules on which lane owns the adapter.
