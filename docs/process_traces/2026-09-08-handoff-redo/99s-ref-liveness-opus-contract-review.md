# 99s — Opus contract-lens refuter: WINDOW-STATUS-GUARD-CENSUS-01

Worktree `/Users/edr/code/JouleWise-wt-ref-liveness-opus` at `a2cfb644`
(detached, one commit on `main` `e9318fdf`). Read-only; no tracked-file edits;
no touch of the real `~/night-custody`.

Acceptance run (the only suite run):
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_window_status_guard
tests.test_measurement_liveness tests.test_run_night tests.test_run_campaign`
→ **Ran 368 tests in 277.9 s — OK, rc=0**.

## Findings

| id | sev | file:line | defect | demonstrating command |
|---|---|---|---|---|
| R1 | should-fix | `joulewise/measurement_liveness.py:53,60` | Fail-**open** via environment. `JOULEWISE_IDENTITY_PROBE` selects the probe binary in production, and rc `0` with empty stdout/stderr is classified `DEAD` (→ WARN + permit). Real `/bin/ps` never does that (dead PID = rc 1, empty). A probe leaked into the shell that exits 0 silently disables the whole guard. | `cd <wt> && python3 -c "import os,sys; sys.path.insert(0,'.'); os.environ['JOULEWISE_IDENTITY_PROBE']='/usr/bin/true'; from joulewise.measurement_liveness import observe_identity; print(observe_identity(os.getpid()))"` → `Identity(state='DEAD', ...)` for a live PID. Fix: require `returncode == 1` for `DEAD`. |
| R2 | should-fix | `scripts/run_night.py:375` + `:1387-1394` | The new `observe_identity()` runs a `subprocess.run(..., timeout=2)` **while the `O_EXCL` `chain.started` descriptor is held and the child is already running**, widening the empty-marker window from ~µs to ≤2 s. If the driver dies in that window, the dead-man reads the empty marker, `_read_started_pgid` → `None`, and writes `chain.exited launch_failed=True` — which **closes** Rule A while the orphaned chain child is alive. Fail-open, one dead-man tick later. | `sed -n '371,382p;1336,1344p;1384,1395p' scripts/run_night.py` and `sed -n '52,57p' joulewise/measurement_liveness.py` (the `timeout=2`). |
| R3 | should-fix | `tests/test_run_campaign.py` (diff hunk `-586,35 +703,16`) | Out-of-scope coverage loss: the commit deletes `test_r7_real_campaign_log_writer_rows_are_complete`, which torn-prefix-tested **real** campaign-log corpora (`runs_window_contrast_20260730`, `runs/p2_015_floors_window_a`) under a `skipUnless` guard, replacing it with two synthetic rows. Nothing in consult 94 asks for this; deliverable 5's hermeticity clause is about *custody*, *host processes*, and *home-directory registry writes*, not repo run dirs. | `git show HEAD -- tests/test_run_campaign.py \| sed -n '/REAL_CAMPAIGN_LOGS/,+8p'` |
| R4 | should-fix (docs, lead) | n/a — absence | The registry is an undocumented operational surface: `grep -rn "active-campaigns" docs/ scripts/` returns **nothing** outside `joulewise/measurement_liveness.py` and tests. No doc names its path, its stale semantics, or **who may remove a stale entry** — unlike `campaign.lock`, whose manual repair workflow is documented. SIGKILL/SIGTERM leaves entries forever (no signal handler exists in `run_campaign.py`). | `grep -rn "active-campaigns" docs scripts; grep -n "SIGTERM\|signal\." scripts/run_campaign.py` (second grep: no hits) |
| R5 | nit | `joulewise/measurement_liveness.py:110`, `scripts/run_campaign.py:8248` | `publish_campaign` raises a bare `RuntimeError` *after* the campaign lock is acquired; `run_campaign` only converts `RuntimeError` to exit 2 around `acquire_campaign_lock`. A transient `ps` failure therefore aborts a campaign with a traceback rather than a clean refusal. Lock and entry are still released. | `sed -n '8240,8252p' scripts/run_campaign.py` |
| R6 | nit | `joulewise/measurement_liveness.py:241-245` | Registry re-reconciliation reruns `inspect_registry` from the top, re-appending refusals/warnings for entries already inspected. Cosmetic duplication only; verdict unaffected. | inspection |
| R7 | nit (fail-closed) | `joulewise/measurement_liveness.py:60-64` | Out-of-range PIDs give `ps: process id too large` on stderr → `UNKNOWN` → refuse, not `DEAD`. Correct direction; noted so it is not mistaken for a bug later. | `python3 -c "import sys;sys.path.insert(0,'.');from joulewise.measurement_liveness import observe_identity;print(observe_identity(999999))"` |

## Per-question evidence

**Q1 — night-driver contract (D-169 / stage-1 R-3).** The driver diff is two
hunks and six lines: the module import (`run_night.py:28`) and `start_time` in
`_complete_chain_start` (`:371-381`). **No ordering change**: `agent_census`
call sites are untouched (`:456`, `:1422`); the `O_EXCL` once-only claim
(`_claim_chain_start`, `:360-368`) and its `night_chain_already_started`
refusal (`:1251`) are unchanged; `_record_chain_exit` semantics (`:312-328`)
and the launch-failure path (`:384-398`) are unchanged; dead-man
(`:1384-1400`) is untouched. Stage-1 **R-3** (ruling `:72`) keeps the driver's
own argv-based agent census (`pgrep -lf "codex|claude|t3"`) — correctly *not*
retired, since it detects agents, not measurement. Stage-1 `:318` (O_EXCL
`chain.started` before the chain starts) still holds. The one real ordering
consequence is **R2**: a subprocess now executes inside the descriptor-held
window.

**Q2 — campaign registry/lock.** Entries live at
`<custody parent>/active-campaigns/<pid>-<24 hex>.json`, i.e. `~/night-custody/
active-campaigns/` by default (`measurement_liveness.py:111,117`) — **not**
under the runs dir, and not inside any night plan's `custody_root`
(`run_night.py:910`, plan roots are `~/night-custody/<plan>/`). Nothing hashes
or seals that sibling directory: `_artifact_list`/`_durable_record`
(`run_night.py:500-583`) walk only `custody_root`, and no script enumerates the
custody parent (`grep -rn 'night-custody"' scripts/*.py`). So **no
custody-bound or claim-bearing path is touched.** Creation is `open(...,"xb")`
= `O_EXCL` (`:118`). Removal is inode+payload-exact (`remove_campaign:83-97`)
and runs in `finally` **before** lock release on both production paths
(`run_campaign.py:8027-8031`, `:8945-8949`) — normal and exception exits
covered; SIGKILL/SIGTERM is not (no handler), by design per consult. A stale
entry cannot block a later campaign: dead PID → WARN, reused PID with a
different token → WARN (`_inspect_identity:172-181`). `--dry-run` does **not**
register (`run_campaign.py:8247-8250`, guarded by `if not args.dry_run`), nor
does the maintenance/verdict-only acquisition — both proved by
`test_dry_run_and_maintenance_lock_publish_no_registry`. The campaign lock
gains only an additive `start_time=` field (`:3163-3172`); nonce/inode
ownership and the manual stale-repair workflow are untouched, as the consult
required. Open gap: **R4** (no documented repair rule or owner).

**Q3 — identity.** Same convention as the watchdog: whitespace-normalized
five-field `lstart` (`measurement_liveness.py:34-38` vs
`magistrate_watchdog.py:201-225` `" ".join(parts[2:7])`), same
PID+start_time equality test (`_inspect_identity:179` vs `owned_process:854-864`),
same zombie exclusion (`stat` starting `Z` vs `<defunct>`). New code additionally
pins `LC_ALL=C` (`:56`); the watchdog does not, but the two marker families
never compare tokens across writers, so this is self-consistent. PID reuse with a
different token → **WARN + permit**, never live
(`test_pid_reuse_warns_and_permits`, `test_reused_pid_warns_and_permits`).
**The census never signals a process** — no `os.kill`/`killpg` anywhere in the
module (`grep -n "kill" joulewise/measurement_liveness.py` → no hits); it reads
`ps -p <pid> -o lstart= -o stat=` only, never command text.

**Q4 — decision table.** All rows are evaluated at `window_status.sh:44`,
**before** the status heredoc (`:60-94`) and before any git call (`:101-108`),
so every refusal precedes both the status write and Git mutation.

| observation | outcome | site |
|---|---|---|
| live chain (`started`, no `exited`, PID+token match) | REFUSE | `:185-199`, `:182` |
| exited chain (valid exit marker) | permit, no probe | `:189-192` |
| dead PID | WARN + permit | `:172-173` |
| reused PID (token mismatch) | WARN + permit | `:179-180` |
| malformed marker (empty/`[]`/no pid/bad token/legacy live PID/invalid exit) | REFUSE indeterminate | `:144-148`, `:159-163`, `:169-178` |
| unreadable registry / bad `ADDITIONAL_PARENTS` JSON | REFUSE indeterminate | `:229-231`, `:256-257` |
| missing custody parent | clear (empty census) | `:236-238` |
| multiple parents | deduped, each inspected | `:232-233` |
| freeze sentinel | status written locally, **no git** | `window_status.sh:96-99` |

The freeze branch is reachable **only after a clear census**, so it never
writes during a live measurement (`test_open_chain_refuses_before_status_or_
git_even_with_sent_and_freeze` sets the sentinel *and* an open chain and still
refuses). Under D-127 the contaminant is the network/CPU of `git commit/push`,
not a local file write; skipping Git while writing locally is therefore
consistent, and strictly quieter than the previous behaviour.

**Q5 — spec vs test.** Every row above has a biting test, in both the Python
module (`tests/test_measurement_liveness.py:40,47,54,61,70,80,129,146,157`) and
end-to-end through the shell (`tests/test_window_status_guard.py:79,85,91,96,
101,107,124,132`). The shell tests are **not** self-declared fixtures: the fake
probe (`:31`) emits raw `ps`-shaped text and the *production* parser
(`observe_identity` → `_start_token`) consumes it; a `ps` stub that logs and
exits 99 plus `assertFalse(self.ps_log.exists())` (`:34,60`) proves no host argv
census. Writer tests assert registration *before* child dispatch by asserting
inside the mocked child (`test_run_campaign.py`
`check_launch_and_cleanup`), and `test_run_night.py:388-397` asserts the
recorded PID is the child, not the driver. The one genuine gap: **no test
executes the real `/bin/ps`** — `test_probe_is_specific_pid_fixed_locale_no_
commands` mocks `subprocess.run`. I closed that manually: real `/bin/ps` on
this machine returns `LIVE` for self and PID 1, `DEAD` for a reaped child
(rc 1, empty), which is how R1 surfaced.

**Q6 — overbuild / miss analysis.** 271 lines for the module is proportionate;
each mechanism (`_reconciled`, inode+payload-exact cleanup, `_valid_exit`) maps
to a named consult clause and a test. The miss analysis **is** documented, in
the module docstring (`measurement_liveness.py:1-8`): hand-run chains are
covered only during registered campaigns (so settle and inter-campaign gaps are
uncovered), direct collectors and old checkouts are uninstrumented, a dead owner
can leave surviving children, and the measurement checkout must be updated and
share `JOULEWISE_CUSTODY_PARENT`. That last point is the live deployment risk:
the production clone (`/Users/edr/JouleWise-measurement-20260818`) has no
`publish_campaign`, so Rule B covers nothing until deployed. The residual misses
are acceptable under **D-161** — a hand-launched chain outside the driver is a
deliberate operator route, not a mistake the guard must fail closed against —
whereas R1 and R2 are *accidents* (a leaked env var; a driver killed mid-write),
which is exactly the class D-161 keeps fail-closed.

## Verdict

**LAND-WITH-FIXES** — required before merge: **R1** (restrict `DEAD` to
`returncode == 1`; one line). Lead ruling required on **R2** (dead-man converts
the widened empty-marker window into a false chain closure) and **R3** (restore
the deleted real-corpus regression test). **R4** is a doc follow-up outside this
commit's WRITE_SCOPE. R5–R7 are nits. No blocker; the design faithfully
implements consult 94 and the driver's D-169 / stage-1 ordering is intact.
