# ALIGN v4 pre-W1 smoke kit (merged Sol/Opus build)

Authority: RUN_STATE 219 and 220, and the lead rulings on the smoke kit (2026-11-08).

Ed's goal is "good quick smokes that test all the likely flag/dangerous points before we commit to long
blocks". A fault that a 30-45 min check can catch must never cost a 12 h W1/D window.

**Provenance.** This kit merges two independent builds, compared in `W1-SMOKE-AGREEMENT.md`:
- Opus: `align/2026-11-08-w1-smoke-opus` @ `0a4b5a73c`, the base;
- Sol: `align/2026-11-08-w1-smoke` @ `035a8c7fe`, from which these pieces are ported:
  - executed-module coverage of the receipt;
  - the edited-packet-bytes test;
  - the segment-based deadline check;
  - the series-manifest binding;
  - transcript and process-group discipline.

It lives on `align/2026-11-08-w1-smoke-merged`. That branch merges `align/2026-11-08-v4-r11` @ `f03a7ee38`,
which carries the packet rebuild (`scripts/align_v4_next_arm_packet.py`), the W1 blockers, and the
delta2 fixes (G2, G3).

**Sol reviews (HOLD at `f6251227a`), fixed here.** Both witness modules are on the branch, and they pass
with every `expectedFailure` removed: `tests/align/test_smoke_review_sol1.py` (21 tests) and
`test_smoke_review_sol2.py` (14 tests). Section 7 of `W1-SMOKE-AGREEMENT.md` maps each finding to its
fix and lists three named witness adaptations to the landed schema.

**Lead rulings applied:**
1. Opus owns the single merged kit, and the command folds into `scripts/align_v4_prequal.py`.
2. A reduced 2-member window labelled `smoke` is approved. It is never pooled or analysed.
3. **HARD:** the native smoke runs only in an isolated clone with a copied calibration ledger and its own
   `runs/` and custody roots. A test fails if any smoke path resolves inside production.
4. Sol's dry-arm contention expectation is dropped. Contention is tested by an in-window contender that
   must produce the flag.
5. G1, G2 and G3 go to the v4 fixer. Their PREQUAL checks go green when the fixes land. G2 and G3 are
   green on `8d0dabc73`.
7. **Packet as pointer (lead ruling, 2026-11-08).**
   - The arm rebuilds the next-arm packet deterministically from the identities it names: record path and
     commit, series ledger, kit, receipt and lead rulings.
   - The arm requires canonical equality, ignoring only `pushed_tip` and `packet_preflight`.
   - Expiry is mandatory.
   - Window records are hash-chained to their predecessor, and zero-capture retries take ids such as
     `C3#2`.
   - G1 and G1b are rewritten as behaviour checks for this design. They do not assume that packets are
     committed files. They run on the fixer's real schema and are green on `48a4d1d76`.
8. **The next measurement is W1.** R1 is armed (RUN_STATE 225/227: `lane/2026-11-08-r1-arm-fixes` @
   `20e9edbc4`, plan `align-r1-20261108T0917Z`). Its route is pinned in `arm_routes.json`.
   `--w1-next w1` is the gate that matters now.
6. PREQUAL's base launcher check compares `runner.json` semantically, and a WARN row lists the required
   tests that only run behind an opt-in (opt-in audit 2026-11-08).

## Part A: next-arm PREQUAL (Air)

```sh
# at the exact commit the MBP will run (clean checkout)
nice -n 15 python3.13 -B scripts/align_v4_prequal.py --w1-next r1 --output /private/tmp/jw-w1pq/<commit>-r1 \
    --deadline-projection <repo-relative installed-plan projection>
nice -n 15 python3.13 -B scripts/align_v4_prequal.py --w1-next w1 --output /private/tmp/jw-w1pq/<commit>-w1 \
    --series-projection <repo-relative frozen series projection> --deadline-projection <...>
```

**Output and exit codes:**
- One PASS/FAIL/PENDING/WARN table, plus `prequal-w1.json` and `prequal-w1.md`.
- Exit 0 only when no *blocking* check FAILs; 1 is a fail, 3 is incomplete (`--only`), 2 is a usage error.

**Rules:**
- **Isolation of checks.** Each check is a probe in its own process (`--w1-probe`), and probes run in
  parallel (`--jobs`). An exception counts as a FAIL. Every host command goes to a fake host; nothing
  touches hardware.
- **Gating.** Each check gates `r1` or `w1`. It blocks the current arm when it gates this measurement or
  an earlier one. A FAIL in a later-gate check is printed but does not block. PENDING (cannot be
  satisfied yet) becomes FAIL at the check's own gate. WARN never blocks.
- **Waivers.** `--waive CHECK=RULING` records a lead waiver in the report.
- **Wall time.** About 90-125 s on the Air with 6 jobs. The full WP22 run dominates.

**The base PREQUAL** (`--stage …`: R0, model and launcher checks) is unchanged and still required.
Its `launcher` check now compares `runner.json` semantically, not as an exact argv list:
- the runner must run under the *unresolved* venv `--python-bin`;
- the runner script must be `scripts/align_r0_checks.py`;
- `--config` and `--output` must carry their exact values;
- only the optional flags `--keep-going` and `--checks` are allowed;
- no flag may start with `--skip`, `--allow`, `--force`, `--synthetic`, `--fake`, `--dry-run`, `--no-quiet`,
  `--python` or `--unsafe`;
- other flags are listed in the report, not failed.

`origin/main` 274e1e7a7's default `--keep-going` therefore no longer false-fails it.

For a launcher with the RUN_STATE 206 display dwell (`origin/main` 9f56fe78d), the `run --help` probe uses
the launcher's own dwell test seam (`JOULEWISE_R0_TEST_DISPLAY_DWELL_S=0.1`) and `--pmset-bin
/usr/bin/true`, so it never sleeps the Air's display.

`tests/align/test_v4_prequal.LauncherDryRun.test_real_launcher_keeps_the_venv` passes against the current
`origin/main` launcher. `RunnerArgvSemantics` covers the comparator.

| Check | Gates | What it runs | Goes green when |
|---|---|---|---|
| `arm-cli` | w1 | `align_v4_session.py install --help`, then `install` without evidence (argparse must name every required flag: `--w1-disk-config`, `--obc-off-attested-by`, `--battery-log`, `--next-arm-triage`). Then the production `main(['install', …])` through `h.install` against a fake host, in 12 cases. The measurement root is a git repo with a committed R1 record. The battery log is synthetic. The cases: control; triage missing, edited or pre-R12; `record_commit` unknown; top-up with no charge, stale or future-dated; OBC unattested; a disk image mounted; battery charging; powermode mismatch. | The control admits and calls the installer exactly once. The 11 faults each refuse with their documented reason before the installer. |
| `packet-rebuild` | w1 | **G1, packet as pointer.** The fixture is the fixer's real record schema (`Scenario`): W1, C1, C2, a zero-capture C3 and its retry `C3#2`. The packet comes from the real producer `build_packet`. The production `arm_checks` runs with a fake host and a fake meter probe, and the rebuild is read from `next_arm_triage.rebuilt_packet`. Four probes, all judged on `next_arm_triage:` reasons only: the rebuild must admit; the rebuild with only `pushed_tip`/`packet_preflight` changed must admit; one second **before** `valid_until_epoch_s` it must admit; one second **after**, it must be refused *for expiry* (`expired` / `valid_until`), never for an unrelated reason (S3). A missing `valid_until_epoch_s` FAILs. | Green. |
| `packet-tamper` | w1 | **G1b.** Every leaf at any depth of every check entry and every `window_chain`/`calibration_windows` element is changed and removed, and a key is added to each (D6/D2-5: chain `path`/`sha256`/`previous_sha256`/`status` leaves included). Beyond that: An admitted control comes first: the arm's own rebuild. If that control is refused, the check FAILs, because no refusal can then be attributed to tampering (S3). Then every single change must be refused as a mismatch (`does not match its committed sources` / `could not be rebuilt`); any other refusal reason counts as not refused. The changes: every top-level key changed or removed; an added key; in **every** check entry the status flipped, the basis edited, the status removed and a key added (S2-3: nested leaves); every `window_chain`/`calibration_windows` element's first leaf changed; and the chain with the zero-capture attempt removed. About 100 arm runs, 6 in parallel. | Green. |
| `calibration-stop` | w1 | `calibration_stop` over the planned C1-C8 (7/7 per pair, 22 members): the 8 prefixes, zero-capture, escalation, provisional, insufficient, a ninth window, loss of two whole windows (completes) and of three (insufficient). Then 5 triage-integrated arms, with the arm-derived identity. | It is green now. |
| `cal-escalation-exit` | w1 | MED-2(a): two final zero-capture refusals escalate. Then a signed `lead_rulings` row (`resets: zero_capture_escalation`) resets the count, and the triage admits the next calibration arm. | It is green now. |
| `kit-ready` | w1 | `align_v4_kit.py --check` on a clean clone of the candidate | The kit is W1-ready (R0 and R1 values filled). |
| `receipt` | w1 | Three parts. **(Sol)** The static import closure of `endpoint.py`, `run_night.py` and `align_v4_session.py`, **every** first-party path including `scripts/` (S10), must be covered by `ARTIFACTS`. A validator self-test: an exact receipt is admitted; a digest mismatch and a working-bytes drift are refused. Then the committed receipt via `require_registration`, whose bound commit must be an ancestor of the candidate, with a clean checkout. | The receipt is registered. A receipt cannot contain its own commit, so the merged kit requires the bound commit to be an *ancestor* of the candidate rather than Sol's literal `receipt.commit == candidate`. |
| `series-manifest` | w1 | `--series-projection`: one W1, then C1-C8 in order, then tests, with 7/7 benign. It names its source manifest by sha256, and the projected roster must **equal the source's `windows` roster** (order, roles, windows, per-pair counts). A digest binds bytes; the roster has to describe them (S2). Fixed-8 is checked on that roster. | The lead freezes and projects the series. |
| `deadline` | r1 | `--deadline-projection` is a repo-relative **evidence bundle** directory copied from the arm (D5/D2-4): `night_plan.json`, its session's `session.json`, and the published `~/Library/LaunchAgents/com.joulewise.night.plist`. Three things are checked. **Binding:** all three must name one plan. The plist runs `--plan P`; the session's `plan_path` is P; its `plan_sha256` equals the copied bytes; its installer argv names P and exited 0; P is `<custody_root>/night_plan.json`. **Validity:** the plan must parse as a production `NightPlan`, and its `plan_id` kind (`align-r1-`, `align-v4-`; never `align-v4-smoke-`) must be the next measurement. **Sizing:** the authoritative `hazard_window.programmed_span_s`, through the plan writer's formula, must fit `window_max_s`; for R1 the corrected floors (67,371 / 96,427 s) also apply. A lone plan or a schedule declaration is refused. | The magistrate copies the bundle in. |
| `r1-w1-chain` | w1 | `R1-TO-W1-CHAIN.md` as written, on a lane-shaped synthetic R1 record in a clean clone: exporter, `backfill-x-g`, `backfill-turn-counts`, `derive-contrast` (equal to the kit's re-derivation), `decide`, `kit.require_ready`, then the kit steps the runbook's shell block documents. | **G2.** It is green on `8d0dabc73`: the runbook now regenerates the kit (step 7) before `--check`. |
| `km003c-launch` | r1 | The real HAZARD_PACK driver with a live sample-writing stand-in meter, run clean and with the reader SIGKILLed mid-chain. Custody hashes and the SIGTERM stop are checked; the reader must restart into `stream-002`; the straddling member must read DC `missing` with `meter.*` flags; the other members must read `available` with rails unchanged. Also the production argv and `require_enabled`. | It is green now. |
| `km003c-crash-radius` | w1 | **G3.** A member that ended *before* the reader was killed | It is green on `8d0dabc73` (unclosed-stream salvage). |
| `w1-window-max` | w1 | The W1 template filled at the planning worst case. Validator = `plan_inputs.window_max_s` = b5 formula. Caps and L1 fit. An AST scan for a `wait_outside_os_batch` call in the W1 entry points' import closure. Then the committed `w1_plan.json`. | The R1-filled `w1_plan.json` is committed. |
| `wp22-dry-run` | w1 | `JW_WP22_FULL=1 python -m unittest tests.align.test_v4_w1_synthetic` plus the minimal witness | It is green now: HIGH-1 is fixed on `v4-r11`, and the run reports 20 tests OK with 1 expected failure. |
| `smoke-kit` | w1 | Part B pre-qualified. `isolate()` runs on a stand-in production checkout with a synthetic ledger. Then the production `measurement_view` of the isolated clone, `reduce_view`, `isolation_violations` (must be empty), a planted symlink into production `runs/` (must be caught), the production ledger unchanged, and 6 of 7 arm-fault expectations against the production arm. | It is green now. |
| `optin-required` | WARN | The opt-in audit ledger (`docs/perf/2026-11-08-optin-audit-results.json`). Every test whose recommendation names PREQUAL and that exists at the candidate runs only behind an opt-in: 134 today. The row names which ones this kit runs (14: WP22, via `wp22-dry-run`). The other 120 need the native MBP, the base PREQUAL or a provisioned fixture. | It never blocks; it keeps that debt visible. |
| `arm-route` | r1 | `configs/align/v4/arm_routes.json` for `--w1-next`: every step's files exist, its entry point answers, and the receipt class is known. A route with a `commit` is *pinned*: its files are verified at that commit and its probes run in a scratch clone of it. R1 is pinned at `20e9edbc4` (armed as `align-r1-20261108T0917Z`). | It is green for both R1 and W1. |

## Part B: native MBP smoke

**When to run it.** Run it after R1 closes and registration is signed, and before the W1 arm, in a gap.
Repeat it before the first long window after any code change. It is never run during a window: the
guards refuse if the night job is loaded, the host night lock is held, `run_night.py` is running, the
checkout is dirty, or no `--w1-next w1` PREQUAL PASS exists at this exact HEAD.

**Label.** The smoke is non-registrable and labelled `smoke`. Its session and plan ids start with
`align-v4-smoke-`, and the reduced tree carries `smoke_label.registrable: false`. It is never pooled,
analysed, pushed or cited.

**Isolation (HARD, lead ruling 3).** `w1_smoke.isolate`:
- makes `git clone --shared` of HEAD into `<smoke-dir>/measurement`;
- copies the calibration ledger and head pin with `b6.smoke.copy_ledger` (distinct inodes, destination
  inside the smoke dir, source bytes checked unchanged), and commits the pin copy in the clone;
- leaves `runs/` holding only the copied ledger;
- creates a venv from the base interpreter, which reads the checkout's site-packages read-only.

Prepare, every arm attempt and the native chain then run from the clone's scripts and venv. Custody and
runs roots live under the smoke session.

Before any arm, `isolation_violations` must return empty. It resolves through symlinks:
- the smoke dir;
- every absolute path in the session state and the plan;
- every write key (custody, runs parent, backups, ledger, measurement and pack roots);
- every symlink under the smoke dir.

These are checked against the production roots:
- the checkout;
- wherever its `runs/` resolves;
- `production_roots` in `w1_smoke.json` (`~/night-align`, `~/night-custody`, `~/night-archive`). These
  are compared as strings only, never opened.

**When isolation is checked, and how hits are handled** (Sol S4/S5, S2-1):
- Before ANY write, `destination_violations` checks the smoke directory: it must be new, and neither it
  nor its nearest existing ancestor may lie inside a production root. A refusal writes nothing at all,
  not even the log.
- Isolation is checked again after `isolate`, after prepare (state and plan), before every fault
  (that fault session's state and its plan copy) and before the main arm.
- Every **write locator** (custody, runs parent and runs roots, backups, ledger, measurement/view/pack
  roots, chain, `disk_volumes`) must be absolute and inside the smoke directory in both its lexical and
  its resolved form. A relative locator is a violation.
- A read-only exemption (the base site-packages) never excuses a write locator, and it is
  component-bounded.
- `TMPDIR` for every command is `<smoke-dir>/tmp`.
- Configured roots are protected in both their lexical and their resolved form. Only link metadata is
  read; no root is opened or listed.
- The reducer refuses to write through a symlink or outside its session.
- Any hit raises `IsolationAbort`. The whole smoke stops (exit 2) before any further arm, and `parse`
  shows `isolated-clone` FAIL.

**Write-time safety (delta D2/D2-1).** Every write the runner makes after creating the smoke directory goes
through `safe_write`, which opens the target from a directory handle with `O_NOFOLLOW` at every component
and requires a regular, single-link file before truncating. A link or directory swapped in after the last
check is refused at use time. This covers the log, transcripts, fault sessions and plan copies, the packet,
and the reducer's manifests and tree. The smoke directory is created `0700`. The command `TMPDIR` is a
directory this smoke created; its device and inode are re-verified before and after every command, and a
replacement aborts. Every path-typed HAZARD_PACK launch binding (`b5.plan._BINDING_TYPES`, including
`operator_log_root` and `pre/post_calibration_dir`) is a write locator (D7). The detached CLI validates the
destination and its log before creating anything (D1).

**Residual trust boundary, for a lead ruling.** Two things are outside this protection. The production
`align_v4_session.prepare` and the installer write files inside the session by pathname, and a child
resolves `TMPDIR` by path after the inode check. So a concurrent same-user writer that renames smoke
directories in those windows is outside the guarantee. The owner-only directory mode excludes other users.

**Hard limits** (Sol S5/S7, S2-2), not reports:
- **Teardown.** A fault's teardown that cannot be proven stops the smoke before the main arm: the disk
  image still mounted, the receipt clone not removed, or a teardown error. So does a fault that reached
  the installer.
- **Budget.** One **monotonic** deadline (`budget_s` = 2,700 s) clips every command timeout and every
  sleep (D3/D2-2), including isolation's git/venv commands, run with the remaining budget and the smoke
  `TMPDIR`, and the production prepare's commands, run through the bounded runner. Prepare itself starts
  only with budget left and runs with the smoke `TMPDIR`. Teardown commands are the exception. Plan t0
  stays on wall time. Nothing is armed unless `arm_reserve_s` (1,800 s) of budget is left.
- **Installer ownership.** The main install is recorded as pending before the installer runs (D4/D2-3).
  On any abnormal return (timeout, surviving group, error), the session is reconciled, and an install of
  this smoke's own plan is adopted and torn down. A published plist that runs another plan is never
  touched.
- **Owned teardown.** On a budget expiry, a failed terminal or any error after the main install, `finally`
  uninstalls only the job this smoke installed (`install_night_agent.sh --plan <its plan> --uninstall`),
  stops and reaps the contender, and proves the job unloaded and no process naming its plan. If that
  proof fails, it leaves `teardown-unproven.json`.
- **Process groups.** A command timeout kills the whole process group (TERM, then KILL regardless of the
  leader), reaps the leader and proves the group gone. A surviving group is a `TeardownFailure` (S8).
- **Meter kill.** The meter kill targets only this window's reader, by the pgid in its
  `meter_supervision.jsonl`; there is never a global `pkill`.

**Gap guards** also refuse a **published but unloaded** production plan (Sol S6):
`~/Library/LaunchAgents/com.joulewise.night{,.deadman}.plist`.

**Receipt locators** (S9): the seam replaces the view's symlinked kit directory with a regular copy, and
the session's `measurement_root` is the isolated clone itself. The production install's
`kit.generate(check=True)` / `require_registration` therefore resolves receipt locators without
symlinks.

`tests/align/test_w1_smoke.IsolationTests` runs the real `isolate` and the real `measurement_view` on a
stand-in production checkout. It fails if any smoke path resolves inside a production root, if the ledger
shares an inode or if the production ledger changes. It also proves that each planted escape is caught
(custody, runs parent, ledger, plan path, symlink, configured root), and that the runner aborts before
any arm. It passes, so the earlier do-not-run note is removed.

### Commands

```sh
# Air: python3.13 -B scripts/align_v4_prequal.py --w1-next w1 ... must PASS at the MBP's HEAD; copy prequal-w1.json over.
# MBP, magistrate, in a gap. The packet, disk config, OBC attestation and battery log are the ones planned for the W1 arm.
$M/.venv/bin/python -B scripts/align_v4_w1_smoke.py run --detach \
  --measurement-root $M --smoke-dir <smoke-root>/align-v4-smoke-<utc> \
  --prequal-report <prequal-w1.json> --next-arm-triage <w1 packet.json> \
  --w1-disk-config <R0 desk config with W1 offloads> --obc-off-attested-by <name> \
  --battery-log <the live scripts/align_v4_battery_log.py log>
# When smoke-log.jsonl shows guards, isolate, prepare and isolation passing, exit the agent session
# within about 4 min. The window's agent census at t0 must see no agent.
$M/.venv/bin/python -B scripts/align_v4_w1_smoke.py parse <smoke-dir> --json <smoke-dir>/report.json
$M/.venv/bin/python -B scripts/align_v4_w1_smoke.py faults
```

- `<smoke-root>` must not be under the checkout or any production root. The guard refuses those before
  writing anything. A dedicated smoke root outside the window run roots is recommended; a smoke root
  under `~` is no longer refused, and the earlier claim that it was is withdrawn.
- `--detach` re-runs the command in a new session.
- Every command is run in its own process group, with TERM then KILL on timeout. Its transcript is
  written create-once to `<smoke-dir>/transcripts/NNNN-*.json`.

### Sequence and expected outcomes

| # | Step | Expected |
|---|---|---|
| 1 | `guards` | The night job is absent, there is no `run_night.py`, the lock is free, the checkout is clean, and the PREQUAL report PASSes at HEAD. Otherwise abort (exit 2). |
| 2 | `isolate`, `prepare`, `isolation` | An isolated clone with a copied ledger. The production `align_v4_session.prepare` on the clone, with the view pack reduced to `neg8-window-start-r1` (a 1.5B reference) and `align-pilot-v3-episodes-a-e01` (W1 ordinal 1, 30B anchor). Zero isolation violations. |
| 3 | `arm-fault:*` (7) | Production `install` from the clone, on disposable sessions whose plan copy has a past t0, so the installer is unreachable. Each fault gives its documented refusal; see the table below. |
| 4 | `arm-main` | Production `install`: the night job is installed at t0. If the fault attempts used up the lead, the runner stages a fresh session first and checks its isolation again. |
| 5a | `meter-kill` | At the reference's bundle + 90 s, `pkill -KILL -f scripts/km003c_monitor.py`. The reference reads DC `missing` with `meter.*` flags, and the reader restarts. |
| 5b | `cpu-contender` | At the anchor's bundle + 390 s, `/usr/bin/yes` runs for 45 s, out of tree. The anchor must carry `contention.request_overlap`, read with the production `monitor.member_findings`, and its DC must be `available` (recorded in the restarted stream). |
| 6 | `terminal` | `night/result.json` appears, then the launchd job is gone (B1 latch). |
| 7 | `finalize` | A sha256 inventory of the smoke custody. It is never pushed. |
| 8 | `r1-w1-chain` | The PREQUAL probe, natively, in the clone's venv |

| Arm fault | Injection | Expected (needle) |
|---|---|---|
| `arm-control` | none | The arm admits, the W1 disk gate passes, then `plan t0 has passed` |
| `triage-edited` | `capture_faults` set to `fail` | `triage capture_faults failed` |
| `triage-stale` | A pre-R12 packet (no schema, no `full_desk_gate`) | `missing or wrong schema` |
| `receipt-digest-mismatch` | One byte appended to a receipt-bound `.md` in a disposable clone of the isolated clone | `digest drift`, before the arm |
| `disk-image-mounted` | `hdiutil attach -nobrowse -readonly` of a 2 MB image at `/Volumes/JWSMOKE`; it is detached and verified gone | `external_volume_mounted:` |
| `topup-missing` | A battery log with no completed charge | `completed top-up evidence missing` |
| `topup-omitted` | `--battery-log` left out | argparse usage error |

**Parser rows.** `parse` emits one row per check below. Overall PASS requires every row to PASS.

- `labelled-non-registrable`
- `isolated-clone`
- `gap-guards`
- `prepare-reduced`
- each `arm-fault:*`
- `arm-main`
- `terminal-marker`
- `finalize`
- `km003c-reader`
- `meter-kill-flags-member`
- `cpu-contender-flagged`
- `w1-member-dc-available`
- `r1-w1-chain-native`
- `wall-time` (at most 2,700 s)

**Wall time.** The estimate is about 37-42 min, including about 1 min for the isolated clone and venv.
Not yet measured natively.

**Native assumptions the first run checks** (each one has its own row):
- the plan writer accepts the reduced view pack and the committed pin copy in the clone;
- the chain honours the pack-local truncated manifests;
- the fault offsets land inside the intended requests;
- the calibration-capture durations fit the budget.
