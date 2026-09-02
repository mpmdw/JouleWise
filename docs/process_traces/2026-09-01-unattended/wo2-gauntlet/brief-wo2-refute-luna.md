ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
WRITE_SCOPE: []

# Refuter, EXECUTION lens — night driver (D-169 stage 1, WO-2)

Checkout: `/Users/edr/code/JouleWise-wt-night-driver` (branch
`feat/2026-09-01-night-driver`, head `89d58e80`). Files under review:
`scripts/run_night.py`, `scripts/gen_g2_phase_d.py` (`--emit-chain`),
`scripts/install_night_agent.sh`, `configs/launchd/com.joulewise.night.plist.template`,
`docs/process/NIGHT_COURIER_PROMPT.md`, `tests/test_run_night.py`,
`tests/test_gen_g2_phase_d.py`. `git log --oneline cd9b2216..HEAD -- scripts/run_night.py`
shows the landing + fix round 1 + the sidecar seam commit. Write NOTHING
in the tree; `TMPDIR` = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`;
probe scripts go there. Run only `python3 -m unittest tests.test_run_night
tests.test_gen_g2_phase_d tests.test_night_gate` — never canonical
discover; NEVER spawn a real chain, a real `claude`, `launchctl`, or
`git push`. Avoid the substring `t3` in anything you create.

Authority: `/Users/edr/code/JouleWise/docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
(main; read §2 R-1..R-12 and §8 — the cold gate's dispositions). Known and
already ruled: the gate (`joulewise/night_gate.py`) is under its own fix
round; the chain sidecar is GNU shasum form `"<hex>  <basename>\n"`; the
gate will accept it after its fix — the driver's `tests/test_run_night.py`
fixture still writes bare hex (accepted by both) and will switch to shasum
form once the gate lands. Do not report that as a finding.

## What this driver must do (the contract you refute against)

R-2/R-7 lifecycle: `run` → refuse-overrun → gate → (GO) claim
`chain.started` O_EXCL → `Popen(start_new_session=True)` the chain →
census every 30 s with the EXACT production argv
(`night_gate.AGENT_CENSUS_ARGV`); any hit → `killpg` the chain group,
`night_aborted_agent_present` → `chain.exited` written the instant `wait()`
returns → result record → push from a FRESH SHALLOW CLONE to
`night-results/<date>` (never from the working checkout) → courier
`claude -p` with heartbeat proof, `COURIER_DEADLINE_S = 600`, three
attempts with `COURIER_BACKOFF_S` → `courier.sent`. `dead-man` (07:00):
`courier.sent` → exit 0; `chain.started` without `chain.exited` →
`night_chain_alive`, spawn nothing; else courier. Zero-agent fence: no
agent process may exist while the chain runs (the courier IS an agent
process). Reason codes only from `night_gate.NIGHT_DRIVER_REASON_CODES |
NIGHT_GATE_REASON_CODES`. REHEARSAL_STUB never runs a chain. A
DIAGNOSTIC_NO_PACK night never reads a pack root or calls
`launch_window.py` (ruling R-10: the E-10 test is pack/launcher consumption).

## What to try (EXECUTION: what the code DOES, with a recording Popen shim and real files)
1. Drive `run` end to end under a fake `subprocess.Popen`/`run` that records
   argv and returns scripted exit codes: GO path; chain exit 0/17; a census
   hit at tick 2 (assert `killpg` on the chain's pgid, the reason string,
   `chain.exited` written BEFORE result.json/push/courier); second `run`
   after each outcome spawns nothing.
2. Time: the 30 s census loop — does it busy-wait, drift, or block `wait()`?
   Feed a monotonic clock shim; count census calls for a 95-s chain.
3. Overrun predicate: t0 at 23:00 with window_max_s that lands after 07:00
   local; t0 at 06:30; DST boundary date; t0 exactly 07:00:00.
4. Clone-and-push: what argv is run, from which cwd; what happens when
   `git clone` fails (exit code unchanged?); does any push touch the
   working checkout (`grep -n "cwd=" scripts/run_night.py`)?
5. Courier: argv shape, deadline enforcement (does a hung `claude -p`
   actually get killed at 600 s?), backoff arithmetic, `courier.sent`
   content; heartbeat proof — what exactly is written and by whom?
6. Dead-man both branches with real files; a `chain.started` that is
   malformed JSON.
7. `--emit-chain`: byte-determinism across two runs; the sidecar form;
   `chmod 0o755`; the chain text contains no `$PACK_ROOT` read and no
   `launch_window.py` call (grep the rendered text).
8. Every place the driver reads the environment, HOME, cwd, or the clock
   outside an injected seam (`grep -n "environ\|expanduser\|getcwd\|time\."`).
9. Mutants (in a TMPDIR copy, never in the tree): drop `start_new_session`;
   drop the O_EXCL flag; swap the census argv to `pgrep -x codex`; write
   `chain.exited` AFTER the push; skip `killpg`. Which survive the suite?

## Report

Envelope first (fenced ```json, `claude-codex-report/v1`, genre `review`).
Verdict MERGE-READY / FIX-ROUND. Findings severity-tiered (blocker /
should-fix / nit), each with file:line, the INPUT that exposes it, observed
vs expected. Then the exact commands you ran. Under 120 lines after the
envelope.
