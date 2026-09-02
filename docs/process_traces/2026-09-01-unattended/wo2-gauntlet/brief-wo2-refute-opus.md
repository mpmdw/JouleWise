ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
WRITE_SCOPE: []

# Refuter, CONTRACT lens — night driver (D-169 stage 1, WO-2)

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

## What to check (CONTRACT: the ruling vs the code, line by line)
1. Map every R-2/R-7/§8 clause above to a file:line that implements it; any
   clause with no line is a finding, any line that does MORE than a clause
   allows is a finding.
2. The launchd plist template and installer against R-2 item 2, §8 item 3:
   no `KeepAlive`, `RunAtLoad` false, both labels rendered from the ONE
   template, the dead-man hour from the driver's constants only, no sudo,
   user-domain only. Does the installer `bootout`/`bootstrap` the right
   domain, and what happens on re-install?
3. `docs/process/NIGHT_COURIER_PROMPT.md` against R-7: the courier's prompt
   must instruct a Gmail send to Ed's address with the result record and
   heartbeat proof, nothing else — no tool that writes to the repo, no
   second agent, no interpretation of the night's data.
4. R-10 / E-10: trace every path by which a DIAGNOSTIC_NO_PACK night could
   consume a pack root or call `scripts/launch_window.py` / `generate_arm_readiness.py verify`.
   Cite the chain template text.
5. Reason-code hygiene: every `refusal.json`/`result.json` writer names a
   registry member; the `night_gate` codes vs driver codes split matches R-8.
6. D-078 once-only: is there ANY path (exception between claim and Popen,
   a crash after Popen before `chain.started` is durable, a launchd re-fire)
   that runs a chain twice or leaves the latch inconsistent with reality?
7. Test honesty: for each test in `tests/test_run_night.py`, does its name
   claim more than its assertions prove? List overclaims.

## Report

Envelope first (fenced ```json, `claude-codex-report/v1`, genre `review`).
Verdict MERGE-READY / FIX-ROUND. Findings severity-tiered (blocker /
should-fix / nit), each with file:line, the INPUT that exposes it, observed
vs expected. Then the exact commands you ran. Under 120 lines after the
envelope.
