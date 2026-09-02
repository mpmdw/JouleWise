ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: implementation
WRITE_SCOPE: ["scripts/run_night.py", "configs/launchd/com.joulewise.night.plist.template", "scripts/install_night_agent.sh", "tests/test_run_night.py"]

# WO-2 fix round 1 — cold-gate amendments to the night driver (D-169 stage 1)

Checkout: `/Users/edr/code/JouleWise-wt-night-driver` (branch
`feat/2026-09-01-night-driver`, head `3da07d8b`). The real gate
`joulewise/night_gate.py` is now merged into this branch — delete the
fake-gate fallback path in `tests/test_run_night.py` if it still exists and
test against the real module (keep a recording `subprocess` shim; never
spawn real processes). Linked worktree: do NOT commit. `TMPDIR` = a
subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Run only `python3 -m unittest tests.test_run_night tests.test_night_gate`.
Avoid the substring `t3` in anything you create.

Authority: `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
(on main, not in your worktree; read it at
`/Users/edr/code/JouleWise/docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`)
§2 R-6/R-7 (as amended) and §8 (cold gate). The registry of the codes you
emit is `joulewise/night_gate.py::NIGHT_DRIVER_REASON_CODES` — import and
use it; a test asserts every code the driver writes into `refusal.json` /
`result.json` is a member of `NIGHT_DRIVER_REASON_CODES | NIGHT_GATE_REASON_CODES`.

## Cures (each with a defect-shaped regression test that FAILS on head `3da07d8b`)

C1 — **Once-only latch (D-078; Opus refuter d.3).** Before the chain is
started in `run`, claim `$custody_root/night/chain.started` with
`os.open(path, O_CREAT | O_EXCL | O_WRONLY)` and write `{plan_id, epoch,
monotonic_ns, driver_pid}`. If the claim fails (`FileExistsError`) write
`refusal.json` with reason `night_chain_already_started`, exit 3, and
NEVER start the chain — even if `result.json` is absent and the window is
open. Test: a second `run` on the same custody root after a first `run`
(whatever its outcome) spawns zero chains. Write `chain.exited` (JSON:
exit code, epoch, monotonic) the moment the chain's `wait()` returns, before
anything else.

C2 — **Dead-man refuses while the chain is alive (cold gate d.3).**
`dead-man` must check, in order: `courier.sent` exists → exit 0 (already
reported); `chain.started` exists and `chain.exited` does NOT → write
`refusal.json` reason `night_chain_alive`, exit 3, spawn nothing (a courier
is an agent process; starting it during capture breaches the zero-agent
fence); otherwise proceed to the courier step. Test both branches.

C3 — **Overrun predicate (cold gate d.3).** In `run`, before the gate is
consulted, compute the next dead-man instant after `t0_epoch_s` from
module constants `DEADMAN_HOUR = 7`, `DEADMAN_MINUTE = 0` in local time
(`datetime.fromtimestamp(t0).replace(hour=…, minute=…, second=0,
microsecond=0)`, +1 day if not after t0). Refuse with
`night_plan_overruns_deadman` (detail names the three numbers) unless
`t0 + window_max_s + COURIER_DEADLINE_S + sum(COURIER_BACKOFF_S) <
deadman_epoch`. Test with a plan whose window ends after 07:00.

C4 — **No launchd restart.** The plist template must contain no
`KeepAlive` key at all and `RunAtLoad` false; the installer must refuse to
render a template containing `KeepAlive` (grep) — test both. The
dead-man entry uses `DEADMAN_HOUR`/`DEADMAN_MINUTE` (the installer passes
them; do not duplicate the literal 07:00 anywhere except those two
constants — a test greps the installer and template for `<integer>7</integer>`
appearing only via the placeholder substitution).

C5 — **`night_aborted_agent_present` is a registry member** (it already is,
in `NIGHT_DRIVER_REASON_CODES`); the census-abort path must write exactly
that string. Replace any literal reason strings in the driver with names
taken from the registry (a test greps `run_night.py` for `"night_` literals
outside a single `_CODES` mapping).

## Report

Envelope first (`claude-codex-report/v1`, genre `implementation`). Then: for
each cure C1-C5, the file:line of the change and the NAME of the test that
fails on head `3da07d8b` (state that you ran it against the pre-fix
driver: `git stash` is FORBIDDEN — instead copy the pre-fix
`scripts/run_night.py` to your TMPDIR first and run the new test module
against it with `PYTHONPATH` tricks, or simply show the assertion that
would fail by reasoning from the pre-fix code and say so honestly). Test
counts before/after and the exact commands. Under 100 lines after the
envelope.
