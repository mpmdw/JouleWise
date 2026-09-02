ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: implementation
WRITE_SCOPE: ["scripts/run_night.py", "tests/test_run_night.py", "configs/launchd/com.joulewise.night.plist.template", "scripts/install_night_agent.sh", "docs/process/NIGHT_COURIER_PROMPT.md", "scripts/gen_g2_phase_d.py", "tests/test_gen_g2_phase_d.py", "joulewise/night_gate.py", "tests/test_night_gate.py"]

# WO-2 fix round 2 — night driver (D-169 stage 1)

Checkout: `/Users/edr/code/JouleWise-wt-night-driver` (branch
`feat/2026-09-01-night-driver`, head `8510e6dc`, which is `8f3d4adf` + a merge of main). Linked worktree: do NOT
commit. `TMPDIR` = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Run only `python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d
tests.test_night_gate`. NEVER spawn a real chain, a real `claude`,
`launchctl`, or `git push`. Avoid the substring `t3` in anything you create.
`joulewise/night_gate.py` is in scope ONLY for adding names to
`NIGHT_DRIVER_REASON_CODES` (+ its ORDER/coverage test in
`tests/test_night_gate.py`); the gate's evaluation logic is merged on main
and is not yours to touch.

Two refuters reviewed `8f3d4adf` — Opus (contract lens) and luna xhigh
(execution lens). Authority for every cure below is
`/Users/edr/code/JouleWise/docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
(R-2..R-8, §8). Every item gets a defect-shaped regression test that FAILS
on `8f3d4adf` (show how: run the new test against a TMPDIR copy of the old
driver via the `_load_driver` shim, or reason from the pre-fix lines).

## Blockers

B-A — **The installed LaunchAgent cannot reach the driver, and the courier
cannot be found or reported.** (Opus B1, luna B1, luna B2, Opus S3.)
- `run_night.py` must insert `REPO_ROOT` at `sys.path[0]` BEFORE
  `from joulewise import …` (luna B1: a launchd-style env with an absolute
  script path dies `ModuleNotFoundError`). Test: run the script via
  `subprocess` with `env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin"}`,
  `cwd="/"`, argv `--help`; exit 0.
- The plist template sets `WorkingDirectory` = the repo root and
  `EnvironmentVariables.PATH` = `@@PATH@@`, and the installer stamps
  `@@PATH@@` with `"$(dirname "$(command -v claude)"):/usr/bin:/bin:/usr/sbin:/sbin"`,
  refusing (`exit 2`, message) when `command -v claude` is empty. Test the
  rendered plist for both keys (installer has a `--render-only` / dry path
  or the test renders via the same `sed`; read the installer).
- The driver resolves the courier binary ONCE at start: `--courier-bin`
  (absolute path, stamped by the installer into `ProgramArguments`) or
  `shutil.which("claude")`; a missing/non-executable binary is refusal
  `night_courier_unavailable` (NEW driver code) written through the
  ordinary refusal + durable-record path — never a silent `False`.
- Courier `Popen` gets `cwd=REPO_ROOT`; `NIGHT_COURIER_PROMPT.md:7` names
  the handback by ABSOLUTE path (`@@REPO_ROOT@@/docs/process/NIGHT_HANDBACK.md`
  rendered by the driver at spawn) and states that the file is WO-4's (may
  not yet exist: the courier must say so in the email rather than stop).
- `run_courier`'s outcome is RECORDED, not discarded: after the courier
  step every terminal path writes `courier.json`
  (`{"attempted": n, "sent": bool, "heartbeat_seen": bool, "last_error": str|null}`),
  `_artifact_list` includes `courier.json`, `courier.attempts.jsonl`,
  `courier.heartbeat`, `courier.sent` when present, and the branch is pushed
  AGAIN (best effort, same clone helper) so the phone-readable record says
  whether Ed was emailed. Process exit code: a distinct non-zero rc when the
  courier never sent (`EXIT_COURIER_FAILED`), on every path including GO.
  Test: patched `Popen` raising `FileNotFoundError` → `courier.json.sent ==
  False`, rc == `EXIT_COURIER_FAILED`, second push argv observed.

B-B — **A second invocation must never clobber a night's evidence.** (Opus
B2.) Records are write-once: `receipt.json`, `result.json`, `refusal.json`,
`chain.started`, `chain.exited`, `courier.json` are opened with
`O_CREAT|O_EXCL|O_WRONLY`. On the FIRST existing record the driver writes a
single `rerun-<epoch_s>.refusal.json` (new file, itself O_EXCL) with
`night_record_exists` (NEW driver code) and exits non-zero; it touches
nothing else and spawns nothing (no gate probes, no courier). Test = Opus's
probe: same plan twice; assert byte-identical `result.json`/`receipt.json`
after run 2 and the rerun file's reason.

B-C — **Driver refusals get their own schema.** (Opus B3.) Driver-side
documents are `"schema": "joulewise.night_refusal.v1"` (a constant
`REFUSAL_SCHEMA` in the driver, next to `RESULT_SCHEMA`), never the gate's
`SCHEMA`. Add `validate_refusal(doc) -> list[str]` in the driver (exact
key set; `reason` ∈ `NIGHT_DRIVER_REASON_CODES | NIGHT_GATE_REASON_CODES`).
Test: every driver refusal path's document validates under
`validate_refusal` and FAILS `night_gate.validate_receipt` (they are
different shapes by design).

B-D — **No courier while the chain may be alive — on BOTH paths.** (Opus
B4, luna B3.) `_terminate_process_group` returns whether termination was
PROVEN (`wait()` returned). Unproven → write `chain.unkilled` (pgid, epoch),
refusal `night_chain_alive` through the ordinary refusal path, NO courier,
rc non-zero. The dead-man then owns recovery: it reads the pgid from
`chain.started`, probes `os.killpg(pgid, 0)`; `ProcessLookupError` → group
gone → it writes `chain.exited` (`{"reaped_by": "dead-man", …}`) and
proceeds to census → courier; group alive → `night_chain_alive` as today.
`chain.started` therefore records `{"pid", "pgid", "epoch_s"}` (it may be
empty today — read it). Tests: unproven termination spawns no courier;
dead-man with a dead pgid reaps and couriers; with a live pgid refuses.

B-E — **Malformed plan is a refusal, not a traceback.** (luna B4.) `{}`,
non-JSON, missing file → `night_plan_malformed` (gate code, already
registered) through the refusal + durable-record path, exit non-zero, and
the courier IS attempted (Ed must hear that the night did not run). Tests
for `{}` and for non-JSON.

B-F — **Rehearsal is observe-only for the census.** RULED: `REHEARSAL_STUB`
is "dry run, STUB chain" (ruling table :96, :236) whose purpose is
rehearsal "while agents are present" (:100-102). So: the stub process DOES
run (luna B5 is refuted — the stub is not a chain); the census still runs
every 30 s and every hit is RECORDED in `result.json`
(`census_hits: [...]`) but never aborts the stub; verdict `REHEARSAL_ONLY`;
the courier still runs (the rehearsal's acceptance IS the delivered email,
ruling §3 stage 2). Under `run` (not `rehearse`) a REHEARSAL_STUB plan's
gate document is written as `receipt.json`, not `refusal.json` (Opus nit).
Test = Opus's probe: rehearsal + census hit `12345 claude` → `REHEARSAL_ONLY`,
`census_hits` non-empty, stub NOT killed, courier attempted. A DIAGNOSTIC
run with the same hit still aborts (existing test stays).

## Should-fix

S-a — `COURIER_DEADLINE_S` is DERIVED, not asserted (Opus S1): R-7 formula
`min(600, max(3 × measured, 300))` with `measured` = `median_ms / 1000`
from `docs/process_traces/2026-09-01-unattended/cold_start.json`
(5303 ms → **300**). Set the constant to 300 with a comment citing the
artifact and formula; a test loads the JSON and asserts the constant equals
the formula.

S-b — **One courier at a time; the ruled overrun predicate stays literal.**
(Opus S2, luna S1.) The overrun predicate is exactly R-7's
`t0 + window_max_s + COURIER_DEADLINE_S < dead-man epoch` — remove the
backoff sum (luna S1). Collision cure: the run-path courier loop stops
attempting once the dead-man epoch is reached (hands off), and BOTH paths
take a `courier.lock` (O_EXCL, pid, removed on exit) — the dead-man refuses
`night_courier_running` (NEW driver code) while a fresh heartbeat/lock
belongs to a live pid. Retry shape per R-7: one launch + up to 3 retries
with backoffs `(60, 180, 600)` — all three elements USED (Opus nit); tests
assert four `Popen` calls and the three sleeps.

S-c — Emitter byte-identity (Opus S6): `tests/test_gen_g2_phase_d.py`
asserts the chain equals the FULL reconstruction (header + every reviewed
block, in order), not `in`. A mutant that appends one line must fail.

S-d — Coverage on ruled behaviour (Opus S7, luna N1): tests that (1)
`Popen` for the chain is called with `start_new_session=True` (drop it →
fail); (2) `chain.exited` is written BEFORE the durable push (reorder →
fail; assert on call order via a recording mock); (3) `census_count > 0`
and `CENSUS_INTERVAL_S == 30` on a run whose fake chain lives ≥ 1 census;
(4) the clone argv is `git clone --depth 1 … <custody tmp>` and the push
argv names `night-results/<date>` — replace the wholesale
`subprocess.run` patch in `test_clone_failure_does_not_change_a_go_exit_code`
with an argv-recording fake; (5) `killpg` asserted WITH `(pgid, SIGTERM)`.

S-e — Installer (Opus S9): refuse to (re)install while `chain.started`
exists without `chain.exited` under the custody root (`exit 3`); bootstrap
both plists or roll back the first on failure (no `set -e` exit between
them). Tests: shell the installer with a stub `launchctl` on `PATH` in
TMPDIR (read how the existing installer tests stub it; if none exist, add a
`--launchctl-bin` override rather than PATH games).

S-f — Nits, all small: `_night_date` uses LOCAL time like the dead-man
(one time base; say so in a comment); `_CODES` refuses (raises at import)
any registry member not prefixed `night_`; `dead_man` calls
`_durable_record` before its courier so `night_chain_alive` is pushed;
`chain.started`/`chain.exited`/`courier.sent` are `fsync`ed; the two plists
get distinct `launchd.{out,err}` names.

## Not in this round (magistrate dispositions — do not implement)

- Opus S4 (courier tool grant): R-7 orders the courier to "resume the loop"
  — narrowing the grant would reinterpret a ruling; recorded as dissent for
  the cold gate. B-D already guarantees no courier during capture.
- Opus S8 (measurement-checkout HEAD pin): stage-2 item, recorded.
- Opus B1's PATH claim is confirmed only by installing; stage-2 acceptance
  (NIGHT-REHEARSAL-01) is the live confirmation.

## Report

Envelope first (`claude-codex-report/v1`, genre `implementation`). Table:
item → file:line of the cure → NAME of the regression test → how you
showed it fails pre-fix. New registry codes listed. Test counts before/after
and exact commands. Under 100 lines after the envelope.
