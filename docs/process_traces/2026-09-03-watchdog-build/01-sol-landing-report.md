# Magistrate watchdog build — Sol landing report

Date: 2026-09-03 PDT  
Base: `46eaf18c279edc76d0f1036abcbccc687ec85636`  
Branch: `feat/2026-09-03-magistrate-watchdog`  
Install/session/commit actions: none.

## Files

| File | Lines | Purpose |
|---|---:|---|
| `scripts/magistrate_watchdog.py` | 1328 | Short launchd tick, pure decision seams, guarded custody writer, resident supervisor, process-tree enforcement, classification/backoff, and dry-run CLI. |
| `scripts/install_magistrate_watchdog.sh` | 214 | Install/uninstall/render interface, template validation, and one-time current-tree adoption claim. |
| `configs/launchd/com.joulewise.magistrate.plist.template` | 33 | Five-minute, RunAtLoad, non-KeepAlive LaunchAgent with census-safe watchdog argv. |
| `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` | 20 | Headless magistrate resumption, email, handback, and stand-down contract. |
| `docs/process/MAGISTRATE_WATCHDOG.md` | 99 | Operator/state/fence/write/install/rehearsal documentation. |
| `tests/test_magistrate_watchdog.py` | 487 | 27 injected unit and contract cases. |
| `docs/process_traces/2026-09-03-watchdog-build/01-sol-landing-report.md` | 135 | This executed-evidence and clause-map record. |

## Executed evidence

### Focused test module

Command (the module was named explicitly; discovery was not run):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog -v
```

Tail, exit 0:

```text
test_stale_pid_reused_by_another_process_is_not_owned (tests.test_magistrate_watchdog.StopAndDecisionTests.test_stale_pid_reused_by_another_process_is_not_owned) ... ok
test_stop_branch_present_absent_and_positive_control_failure (tests.test_magistrate_watchdog.StopAndDecisionTests.test_stop_branch_present_absent_and_positive_control_failure) ... ok
test_unowned_census_hit_inside_span_holds_without_kill (tests.test_magistrate_watchdog.StopAndDecisionTests.test_unowned_census_hit_inside_span_holds_without_kill) ... ok
test_cooperative_exit_after_request_never_signals (tests.test_magistrate_watchdog.SupervisorTests.test_cooperative_exit_after_request_never_signals) ... ok
test_ignored_request_gets_term_then_kill_and_census (tests.test_magistrate_watchdog.SupervisorTests.test_ignored_request_gets_term_then_kill_and_census) ... ok
test_process_tree_walk_kills_descendant_that_escaped_pgid (tests.test_magistrate_watchdog.SupervisorTests.test_process_tree_walk_kills_descendant_that_escaped_pgid) ... ok

----------------------------------------------------------------------
Ran 27 tests in 0.064s

OK
```

### Python and shell syntax

Commands:

```sh
tmp_cache="$(mktemp -d "${TMPDIR:-/tmp}/wd-pycache-final.XXXXXX")"
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX="$tmp_cache" python3 -m py_compile scripts/magistrate_watchdog.py
bash -n scripts/install_magistrate_watchdog.sh
```

Both exited 0. `py_compile` emitted no diagnostic; its bytecode root was `/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/wd-pycache-final.tBg3UN`, outside the worktree.

### Render-only and plist lint

Commands:

```sh
tmp_render="$(mktemp -d "${TMPDIR:-/tmp}/wd-render-final.XXXXXX")"
scripts/install_magistrate_watchdog.sh --render-only "$tmp_render"
/usr/bin/plutil -lint "$tmp_render/com.joulewise.magistrate.plist"
```

Output, exit 0:

```text
/private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/wd-render-final.DgyU3y/com.joulewise.magistrate.plist: OK
rendered /private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/wd-render-final.DgyU3y/com.joulewise.magistrate.plist
/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T//wd-render-final.DgyU3y/com.joulewise.magistrate.plist: OK
```

Inspection of the rendered plist confirmed PATH begins `/Users/edr/.local/bin`, `StartInterval=300`, `RunAtLoad=true`, no KeepAlive key, and ProgramArguments only `/usr/bin/env`, `python3`, and the watchdog script path. The session binary is supplied only as `MAGISTRATE_SESSION_BIN` in the environment.

### Dry run with fake plan at now + 10 minutes

The fake `REHEARSAL_STUB` plan was placed at `/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/wd-dry.39J7f8/fake-night/night_plan.json` with `t0_epoch_s=1788491234`, computed as observed `date +%s + 600`. Its sibling watchdog root did not exist before or after the run.

Command:

```sh
MAGISTRATE_WATCHDOG_CUSTODY_ROOT=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/wd-dry.39J7f8/magistrate PYTHONDONTWRITEBYTECODE=1 scripts/magistrate_watchdog.py --dry-run
test ! -e /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/wd-dry.39J7f8/magistrate
```

Transcript, exit 0:

```text
decision=HOLD_CENSUS reason=production census non-empty inside plan span
WOULD_WRITE mkdir /private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/wd-dry.39J7f8/magistrate
WOULD_WRITE open_and_flock /private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/wd-dry.39J7f8/magistrate/watchdog.lock
WOULD_WRITE append /private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/wd-dry.39J7f8/magistrate/events.jsonl (259 bytes)
WOULD_WRITE append /private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/wd-dry.39J7f8/magistrate/events.jsonl (206 bytes)
WOULD_WRITE atomic_write /private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/wd-dry.39J7f8/magistrate/state.json (714 bytes)
WOULD_SPAWN none
dry-run custody root absent: PASS
```

`HOLD_CENSUS` is the expected live observation while this Codex implementation session is running. It is evidence that a plan-span dry run uses the production predicate and that dry-run suppresses both custody writes and spawning; it is not hardware or installed-Agent evidence.

## Clause map

File-15 text is shortened only to fit the table; the row number binds the complete adopted proposition.

| Row / adopted proposition | Production site | Biting assertion | One-site counterfactual |
|---|---|---|---|
| 1 — supervisor owns deadline/force; cooperative exit preferred | `scripts/magistrate_watchdog.py:877`, `:1003` | `tests/test_magistrate_watchdog.py:278`, `:294` | Delete the request-before-signal branch at `:1003`: the cooperative test no longer sees a request, and the ignored-request test loses the ordered path. |
| 2 — `-p`, stream-json, one turn; interval is cadence | `scripts/magistrate_watchdog.py:76`, `:818`; `configs/launchd/com.joulewise.magistrate.plist.template:24` | `tests/test_magistrate_watchdog.py:441` | Replace `"-p"` with `"--bg"` at `:821`: the spawn-shape assertion fails. |
| 3 — exact in-span census; span/courier/dead-man/chain extension; PID+start lock; belt and 07:00 | `scripts/magistrate_watchdog.py:483`, `:502`, `:557`, `:755` | `tests/test_magistrate_watchdog.py:146`, `:162`, `:176`, `:186`, `:193`, `:235`, `:243`, `:251` | Change the closed `<=` dead-man boundary at `:517` to `<`: the exact-boundary assertion at `:162` fails. |
| 4 — request −25, TERM −16, KILL −15, census, resident ≤10 s | `scripts/magistrate_watchdog.py:63`, `:1090`, `:1003` | `tests/test_magistrate_watchdog.py:146`, `:278`, `:294` | Change `TERM_LEAD_S` at `:65`: both the phase-boundary assertion and TERM/KILL sequence fail. |
| 5 — stable PPID-tree TERM/KILL; never killpg; unowned hit is HOLD | `scripts/magistrate_watchdog.py:829`, `:853`, `:765`, `:1027` | `tests/test_magistrate_watchdog.py:315`, `:251` | Replace the PPID closure at `:840` with root-only signaling: escaped descendant PID 300 remains absent from the signaled set. |
| 6 — positive control + stop glob + local STOP; rc128 uncertain | `scripts/magistrate_watchdog.py:343`, `:369`, `:378` | `tests/test_magistrate_watchdog.py:202`, `:216`, `:227` | Treat nonzero positive-control rc as clear at `:372`: the rc128 assertion fails. |
| 7 — canonical cwd; plan-pin change before first real arm | `scripts/magistrate_watchdog.py:53`, `:1137`; `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:9` | `tests/test_magistrate_watchdog.py:441` | Change the spawn cwd at `:1137` from `CANONICAL_REPO`: the exact-cwd assertion fails. |
| 8 — heartbeat before email; cooperative last email; forced/usage pending; once per transition | `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:2`, `:5`, `:6`; `scripts/magistrate_watchdog.py:594`, `:653` | `tests/test_magistrate_watchdog.py:371`, `:379`, `:476` | Remove the same-state guard at `scripts/magistrate_watchdog.py:604`: `test_one_event_per_transition` observes two events. |
| 9 — usage 15/30/60/120/120 + activation jitter; never in span; new plan preempts | `scripts/magistrate_watchdog.py:72`, `:695`, `:755` | `tests/test_magistrate_watchdog.py:344`, `:364` | Change the fourth ladder element at `:72` from 7200: the exact observed ladder fails. |
| 10 — email/install/no reply; first resident adopts and stands down the ruled interactive tree | `scripts/install_magistrate_watchdog.sh:60`, `:185`, `:188`; `scripts/magistrate_watchdog.py:1199` | `tests/test_magistrate_watchdog.py:466` | Remove `O_EXCL` from the adoption claim at installer `:188`: the exclusive-claim assertion fails. |
| 11 — arming outside charter; email-then-arm; Ed's NO overrides | `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:10` | `tests/test_magistrate_watchdog.py:466` | Delete “Ed's NO always overrides” at prompt `:10`: the prompt contract assertion fails. |

## Deviations and flags

- No adopted file-15 proposition was intentionally changed.
- `lead_ruling` (nonblocking): file 15 defines the usage ladder but is silent on generic-error delay. Per the task's tie-break rule, implementation uses file 09's 2/5/15/30/60-minute generic ladder rather than file 03's 15/30/60-minute cap or file 04's alternate table.
- `environment` (nonblocking): the launch argv defaults to `--permission-mode auto` and deliberately omits `--permission-prompts none`. Claude 2.1.260 help establishes both flags, but only a no-TTY launch bench can determine whether the latter is required.
- `environment` (nonblocking): this sandbox cannot provide installed launchd evidence. Render/lint and injected resident tests are the strongest permitted evidence here.
- `environment` (nonblocking): the real dry-run census found this active implementation session and therefore held. No session process was started by the rehearsal.

## Owed to the magistrate

1. Before install, execute the documented temporary-LaunchAgent, no-TTY `-p` bench. Pin heartbeat-before-email, stream-json completion, `auto` prompt behavior, post-exit empty production census, and whether `--permission-prompts none` is needed. If that flag is needed, edit only `SESSION_ARGV_AFTER_PROMPT`.
2. Bench the installer's ancestor selection from the actual Terminal-hosted magistrate and prove the seeded PID/start token names the ruled owning root and that the resident adopts it without a second launch.
3. Run the built-artifact gauntlet/cold gate, send Ed the install notice with exact local/remote switch instructions, then follow file-15 row 10. This implementation session performed none of those external/install actions.
4. Before the first real window is armed, land and verify the measurement-checkout plan pin and install the night agents from that checkout. Re-arm after any relevant HEAD move.

---

## Magistrate bench rulings and edits (2026-09-03 21:05 PDT)

- F1: generic-error backoff `GENERIC_BACKOFF_S = (120, 300, 900, 1800, 3600)` ACCEPTED (file 15 was silent; file 09's ladder adopted).
- Lead note 1: the two `git ls-remote` probe timeouts raised from 2 s to 10 s (`scripts/magistrate_watchdog.py` remote-stop probe and positive control); fail-closed direction unchanged.
- F2 / lead note 3: spawn argv gains `--permission-prompts none` (under launchd nobody can answer a prompt; anything that would prompt is denied rather than hung) and the allowed-tool list gains `Agent` (the current name of the subagent tool; `Task` retained for older builds), `SendMessage`, `ListAgents`, `TaskCreate`, `TaskUpdate`, `TaskList`. The bench rehearsal (first `-p` launch from launchd) is the proof of this argv; it is the single line the magistrate changes if the rehearsal shows otherwise.
- Lead note 2: outside a plan span the census is not consulted — this is file 15 row 3 as ruled; an unowned interactive session does not block a daytime relaunch. No change.
- Tests after edits: `tests.test_magistrate_watchdog` 27 OK; `py_compile` OK.

---

## Fix round 1 clause-map addendum (2026-09-03 PDT)

This addendum does not rewrite the implementation seat's map. It replaces the biting-assertion and counterfactual evidence for the touched propositions below; untouched rows retain their original evidence.

| Row / proposition delta | Production site | Biting assertion | One-site counterfactual |
|---|---|---|---|
| 1a — cooperative request precedes signals | `scripts/magistrate_watchdog.py:1024` | `tests/test_magistrate_watchdog.py:295` | Delete the plan `_write_request` call: `test_cooperative_exit_after_request_never_signals` fails. |
| 1b — ignored child still gets request first | `scripts/magistrate_watchdog.py:1024` | `tests/test_magistrate_watchdog.py:311` | Delete the same request call: `test_ignored_request_gets_term_then_kill_and_census` independently fails on the missing request artifact. |
| 3a — PID/start liveness excludes zombies | `scripts/magistrate_watchdog.py:558` | `tests/test_magistrate_watchdog.py:253` | Count a `<defunct>` row as live: `test_defunct_lock_owner_is_not_live` fails. |
| 3b — forced hold reaps the child | `scripts/magistrate_watchdog.py:988` | `tests/test_magistrate_watchdog.py:336` | Remove the in-loop `child.poll()`: `test_forced_hold_polls_child_to_reap_defunct_owner` fails on the poll count. |
| 4 — request −25, TERM −16, KILL −15 | `scripts/magistrate_watchdog.py:63` | `tests/test_magistrate_watchdog.py:147` | Change `TERM_LEAD_S` to `17 * 60`: the literal `960` assertion fails. The same test pins request `1500` and KILL `900`. |
| 5 — only a currently validated lock owner may be signaled | `scripts/magistrate_watchdog.py:1035`, `:1049` | `tests/test_magistrate_watchdog.py:360` | Signal `child.pid` without rechecking PID+start token: `test_plan_signal_revalidates_lock_token` observes a signal to the reused PID. |
| 6a — positive control gates stop-ref interpretation | `scripts/magistrate_watchdog.py:371` | `tests/test_magistrate_watchdog.py:207` | Ignore a nonzero positive-control result: `test_stop_branch_present_absent_and_positive_control_failure` fails on the extra stop probe. |
| 6b — emergency stop glob catches shortened names | `scripts/magistrate_watchdog.py:59` | `tests/test_magistrate_watchdog.py:221` | Narrow the glob to `refs/heads/ops/stop-magistrate*`: the shortened `ops/stop-magistrat` assertion fails. |
| 9a — real CLI usage exhaustion is classified as usage | `scripts/magistrate_watchdog.py:93` | `tests/test_magistrate_watchdog.py:404` | Remove the new spend/reset/`rate_limit`/HTTP-429 signatures: the verbatim production error is classified `generic_error`. |
| 9b — usage ladder is exactly 15/30/60/120/120 | `scripts/magistrate_watchdog.py:72` | `tests/test_magistrate_watchdog.py:417` | Change the fourth element to `7199`: `test_usage_backoff_ladder_and_activation_jitter` fails against the literal tuple. |

The fixed-fence operational consequence for row 3 is now explicit in `docs/process/MAGISTRATE_WATCHDOG.md`: an orphaned resident supervisor is not adopted during the belt or 07:00 minute (`FENCED`, `adopt=False`), so adoption can wait at most 45 minutes.

---

## Fix round 2 clause-map addendum (2026-09-03 PDT)

File 15 row 6 is amended by the magistrate's ruling on execution-refuter N2: the authoritative emergency-stop glob is the wider `refs/heads/ops/stop*`, not `refs/heads/ops/stop-magistrate*`. The wider glob makes shortened as well as suffixed emergency names fail-safe. This addendum supersedes only the row-6 glob literal; the positive-control, anonymous probe, and local-STOP clauses remain unchanged.

The resident row-4 enforcement path now resolves plans before consulting the cached remote-stop observation. Remote refresh runs on a single daemon thread at no more than five-minute cadence, so an unreachable GitHub probe cannot consume any part of the resident's 10-second deadline-resolution budget. Row 8 now consumes a matching `notice.ack` before the child-exit return, and the resident applies the same clock-uncertainty detector as the launchd tick, irreversibly draining an owned child on monotonic time once uncertainty is observed.

---

## Fix round 4 clause-map addendum (2026-09-04 PDT)

This addendum maps only the round-4 cures on the integrated plan-pin base. Untouched rows retain the earlier map and addenda.

| Cure / proposition delta | Production site | Biting assertion | One-site counterfactual |
|---|---|---|---|
| B-1 — a retired-v1 plan is recorded once per custody root and ignored; a valid v2 sibling alone supplies the span | `scripts/magistrate_watchdog.py:480-555` | `tests/test_magistrate_watchdog.py:151` | Append the retired-v1 parse failure to `errors` at `scripts/magistrate_watchdog.py:540`; `decide` returns `HOLD_UNSAFE` instead of `FENCED`. The executed mutation failed on that exact state difference. |
| B-1 — any other unparsable plan is recorded once as `plan_unparsable` and never holds | `scripts/magistrate_watchdog.py:480-555` | `tests/test_magistrate_watchdog.py:189` | Append every parse failure to `errors`; the test observes `HOLD_UNSAFE` instead of `LAUNCHING`. |
| B-1 — watchdog fixtures and both runnable example plans use the exact v2 shape with `measurement_root` and `measurement_head` | `tests/test_magistrate_watchdog.py:99-118`; `docs/process/MAGISTRATE_WATCHDOG.md:202-215`, `:290-303` | `tests/test_magistrate_watchdog.py:769` | Change either example schema back to v1 or remove either measurement key; the exact count/schema assertions fail. |
| M-2/M-3 — the read-only handoff inventory includes the invoking interactive twin tree and named PID-1 bg-host/shell-snapshot orphan trees, while excluding unrelated processes and its transient caller chain | `scripts/magistrate_watchdog.py:654-733`, `:1569-1597` | `tests/test_magistrate_watchdog.py:662` | Delete the PID-1 orphan-root union; the expected orphan host, spare, snapshot, and snapshot-child PIDs disappear from the inventory. |
| M-2/M-3 + Q4 — install handoff order is stop tasks → preserve retired custody → inventory → install → kill only recorded list and prove empty census → next launchd tick creates `-p` | `docs/process/MAGISTRATE_WATCHDOG.md:82-179` | `tests/test_magistrate_watchdog.py:779` | Move install before the retired-root move or inventory, or delete the recorded-only signaling rule; the ordered-position or ownership assertion fails. |
| Q4 — every v2 night installs both night agents FROM its pinned measurement checkout | `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:13`; `docs/process/NIGHT_HANDBACK.md:72-76`; `docs/process/MAGISTRATE_WATCHDOG.md:179` | `tests/test_magistrate_watchdog.py:763-767`, `:779-801` | Replace “installed from that plan's `measurement_root`” with the old generic “pinned” wording; the prompt and handback contract assertions fail. |

---

## Fix round 5 clause-map addendum (2026-09-04 PDT)

This addendum supersedes the round-4 assertions that non-v1 parse failures are ignored, that PID-1 command lookalikes are signal targets, and that documented plan examples may hand-author schema mappings. The authoritative detailed R-2…R-7 and AD-1…AD-13 map, RED/GREEN transcript, and mutation proof are in `14-sol-fix-round-5-report.md`.

| Round-5 proposition | Production site | Biting assertion / counterfactual |
|---|---|---|
| Production composition is gated end-to-end | `joulewise/night_plan_writer.py:15-63`; `scripts/magistrate_watchdog.py:335`; `scripts/run_night.py:267-290` | `tests/test_magistrate_watchdog_cli.py:142` fails when the writer is absent and, after landing, fails again if the sole constructor loses `measurement_head`. |
| Only positive retired-v1 identification is ignored | `scripts/magistrate_watchdog.py:552-603,1068-1076` | `tests/test_magistrate_watchdog.py:167-287`; truncation, missing current fields, and future authorship hold with named reasons while the frozen v1 fixture emits one event. |
| Handoff signal authority is explicit | `scripts/magistrate_watchdog.py:775-899,1801-1837`; `docs/process/MAGISTRATE_WATCHDOG.md:99-203` | `tests/test_magistrate_watchdog.py:806-871`; moving command-shape candidates into `owned` without exact PID/start adoption fails the set/provenance assertions. |
| Every armed checkout is rendered and conflicts hold | `scripts/magistrate_watchdog.py:642-707,1068-1076,1160`; `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:9-10` | `tests/test_magistrate_watchdog.py:289-351`; omit either root or accept overlapping roots/two heads and the prompt/conflict assertions fail. |
| Fixture and documentation drift are structurally blocked | `joulewise/night_plan_writer.py:15-63`; `docs/process/MAGISTRATE_WATCHDOG.md:218-251,312-341` | All v2 tests consume writer output; `tests/test_magistrate_watchdog.py:951-964` compiles documented heredocs and round-trips the writer mapping through `NightPlan`. |

Final authorized modules: watchdog 49 OK, CLI 1 OK, night gate 47 OK, run-night 55 OK, installer 11 OK. No install, agent launch, handoff signal, default-custody write, or quiet-machine run occurred.

---

## Fix round 6 clause-map addendum (2026-09-04 PDT)

This addendum supersedes round 5 only for retired-v1 identification, resident unsafe-plan handling, activation identity, and the documentation-example assertion. The complete RED/GREEN transcripts, S-4 mutation, final module tails, and detailed map are in `17-sol-fix-round-6-report.md`.

| Round-6 specification | Production site | Biting assertion / counterfactual |
|---|---|---|
| S-1 — v1 is the exact import-time golden shape; v2 carries integer `schema_version: 2` | `scripts/magistrate_watchdog.py:109-142,650`; `joulewise/night_gate.py:22,104-118,220-229`; `joulewise/night_plan_writer.py:15-28` | `tests/test_magistrate_watchdog.py:214-249`; restoring label-only identification, omitting the writer version, accepting a missing version, or accepting version 1 fails the golden-plus-v2-key and three-malformed-cases assertions. |
| S-2 — resident `HOLD_UNSAFE` starts and durably completes the cooperative drain | `scripts/magistrate_watchdog.py:1530-1574,1598-1640` | `tests/test_magistrate_watchdog.py:650-688`; `tests/test_magistrate_watchdog_cli.py:210-282`; restoring the transition-only branch removes `resident_drain_started` and the ordered request/TERM/KILL evidence. |
| S-3 — diagnostic identity is a fresh `(activation_id, spawn epoch)` per spawn | `scripts/magistrate_watchdog.py:526-621,1686-1766` | `tests/test_magistrate_watchdog.py:874-938`; reusing the prior id or deleting the epoch from the dedupe key suppresses the second identical diagnostic or fails the two-key equality. |
| S-4 — documented writer blocks produce bytes accepted by `NightPlan.from_mapping` | `docs/process/MAGISTRATE_WATCHDOG.md:224-251,315-341` | `tests/test_magistrate_watchdog.py:1102-1138`; deleting `measurement_head` from the first block fails with the pasted missing-argument mutation in trace 17. |

Final authorized modules: watchdog 52 OK, CLI 2 OK, night gate 47 OK, run-night 55 OK, installer 11 OK (167 total). The prompt remains 23 lines. No install, agent launch, launchd mutation, default-custody write, live signal, or quiet-machine run occurred.

---

## Fix round 7 clause-map addendum (2026-09-04 PDT)

This addendum narrows round 6 only for S-2b: recovery after a resident supervisor dies while its child remains live and the next short tick decides `HOLD_UNSAFE`. The complete RED/GREEN transcript, per-module tails, and detailed map are in `19-sol-fix-round-7-report.md`.

| Round-7 specification | Production site | Biting assertion / counterfactual |
|---|---|---|
| S-2b — every unsafe replacement tick validates and adopts the state-recorded PID/start/activation, records `resident_adopted`, and advances the durable request → TERM → KILL stage without restarting its timestamps | `scripts/magistrate_watchdog.py:472-490,1533-1595,1766-1783,1818-1937,1956-1987` | `tests/test_magistrate_watchdog.py:690-768`; deleting the early unsafe-tick adoption leaves `resident_hold_drain` null and no request, while dropping stage persistence repeats the allowance instead of producing TERM/KILL on the threshold ticks. |
| S-2b — a mismatched start token is `already_gone`, never a signal target | `scripts/magistrate_watchdog.py:1870-1899` | `tests/test_magistrate_watchdog.py:770-795`; treating PID equality alone as ownership signals the reused-token row and fails both the unchanged-signal and event assertions. |
| S-2b — the real CLI replacement path records adoption and the first ladder event | `scripts/magistrate_watchdog.py:1956-1987` | `tests/test_magistrate_watchdog_cli.py:292-387`; the trace-18 counterfactual leaves `standdown.request` absent and records no `resident_adopted`/`resident_drain_started`. |

Final authorized modules: watchdog 53 OK, CLI 3 OK, night gate 47 OK, run-night 55 OK, installer 11 OK. No install, agent launch, launchd mutation, default-custody write, production-agent signal, or quiet-machine run occurred.

---

## Fix round 8 clause-map addendum (2026-09-04 PDT)

This final pre-cold-gate addendum supersedes round 7 only where trace 22 C-1 through C-8 amend drain timing, installer identity/transaction coverage, persisted backoff, and the rehearsal/LaunchAgent documentation. The complete test-first RED/GREEN transcript and six required module tails are in `23-sol-fix-round-8-report.md`.

| Round-8 clause | Production/documentation | Biting assertion |
|---|---|---|
| C-1/C-5 — every latched drain is plan-clamped; replacement ticks apply the wall-time stage immediately | `scripts/magistrate_watchdog.py:1596-1770` | `tests/test_magistrate_watchdog.py:690-783` |
| C-2 — install and rendered plist are pinned to the canonical checkout | `scripts/install_magistrate_watchdog.sh:35-75,190-209`; `docs/process/MAGISTRATE_WATCHDOG.md:105-123` | `tests/test_install_magistrate_watchdog.py:132-186` |
| C-3 — backoff persists a wall deadline plus boot identity and resets after reboot | `scripts/magistrate_watchdog.py:472-492,504-508,1139-1186,1198,1258` | `tests/test_magistrate_watchdog.py:1041-1086` |
| C-4 — behavioral installer transaction coverage, including failed-seed plist cleanup | `scripts/install_magistrate_watchdog.sh:85-263` | `tests/test_install_magistrate_watchdog.py:188-218` |
| C-6 — GUI-login limitation and 15-minute liveness rule | `docs/process/MAGISTRATE_WATCHDOG.md:61,76-77` | `tests/test_magistrate_watchdog.py:1395-1406` |
| C-7 — fake rehearsal roots cannot conflict with a real measurement root | `docs/process/MAGISTRATE_WATCHDOG.md:222,253,343` | `tests/test_magistrate_watchdog.py:1352-1393` |
| C-8 — rendered plist pins install-time `sys.executable` and refuses `/usr/bin/python3` | `scripts/install_magistrate_watchdog.sh:49-64,190-209` | `tests/test_install_magistrate_watchdog.py:147-176` |

Final authorized modules: watchdog 60 OK, CLI 3 OK, watchdog installer 6 OK, night gate 47 OK, run-night 55 OK, night installer 11 OK. The prompt remains 23 lines. No install, real launchctl, agent/session launch, LaunchAgent mutation, default-custody access, production signal, or quiet-machine run occurred.

---

## Fix round 9 clause-map addendum (2026-09-04 PDT)

This addendum closes trace 24 findings F1 and F2. It supersedes round 8 only for installer rollback semantics and the round-8 report's Git-head metadata. The complete RED/GREEN transcript and detailed clause map are in `25-sol-fix-round-9-report.md`.

| Round-9 clause | Production/report site | Biting assertion / counterfactual |
|---|---|---|
| F1 — a failed exclusive lock seed restores the exact pre-install plist and preserves the colliding lock byte-for-byte | `scripts/install_magistrate_watchdog.sh:155-205,238-284` | `tests/test_install_magistrate_watchdog.py:207-221`; the pre-fix trap deleted the plist, producing the pasted `FileNotFoundError`. |
| F1 — failed bootstrap restores the exact pre-install plist and removes only this attempt's unchanged lock seed | `scripts/install_magistrate_watchdog.sh:161-178,294-298` | `tests/test_install_magistrate_watchdog.py:223-238`; the pre-fix trap deleted the plist and left the new lock. |
| F1 — failed post-load verification restores the exact pre-install plist and removes only this attempt's unchanged lock seed | `scripts/install_magistrate_watchdog.sh:161-178,299-302` | `tests/test_install_magistrate_watchdog.py:240-255`; the pre-fix trap deleted the plist and left the new lock after `bootout`. |
| F2 — trace 23 names its real final head | `23-sol-fix-round-8-report.md:3` | Direct `git log` comparison: baseline `1b51fecf...`, final round-8 implementation head `a15cc15e...`. |

Final authorized modules: watchdog installer 8 OK; watchdog 60 OK. No broader discovery ran. No install, real `launchctl`, agent/session launch, LaunchAgent mutation, default-custody access, production signal, or quiet-machine run occurred.

---

## Fix round 10 clause-map addendum (2026-09-04 PDT)

This addendum installs the packet-21 cold-gate cure table's round-10 rows. The full RED/mutation transcripts, exact clause-to-line map, and required six-module tail are in `27-sol-fix-round-10-report.md`.

| Round-10 clause | Production/documentation | Biting assertion |
|---|---|---|
| M-A — both retired-v1 classifier limbs hold under the real CLI | Unchanged `scripts/magistrate_watchdog.py:133-141`; `tests/test_magistrate_watchdog_cli.py:174-205` | Independent M1/M9 mutations each fail the sibling-path assertion. |
| M-C — M8 absent-prior-plist rollback pin | `tests/test_magistrate_watchdog.py:1208-1235` | Named test fails if a failed exclusive seed leaves the newly written plist. |
| M-B — reaper detaches before the kill ladder | `docs/process/MAGISTRATE_WATCHDOG.md:133-218`; `tests/test_magistrate_watchdog.py:1424-1471` | Exact snippet bytes execute and prove `reaper_pid == reaper_session_id`. |
| H-2 — courier reports independent watchdog liveness | `scripts/run_night.py:619-664`; `tests/test_run_night.py:636-657`; `docs/process/NIGHT_HANDBACK.md:15-22` | Prompt carries direct state-file age and last decision; >900 s/unavailable is dead. |
| B-A / S-A — ordered landing and explicit round-9 licence | `docs/process/MAGISTRATE_WATCHDOG.md:92`; `24a-magistrate-ruling-delta-8-signature.md:3` | Step 0 precedes handoff; the one-paragraph ruling binds trace 24 YES to traces 16/22. |

Final authorized six-module gate: 187 tests OK in 32.484 s. No install, canonical-checkout mutation, default-custody access, agent/session launch, production signal, email, or quiet-machine work occurred.
