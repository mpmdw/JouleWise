# Magistrate relaunch watchdog + night plan pin — magistrate terminal review (apex read)

Date: 2026-09-04. Merge candidate: `feat/2026-09-03-magistrate-watchdog` (night plan pin merged in) at the head named in the PR ledger row 12.

## What I read (primary artifacts)
- Rounds 1–7 as recorded in the apex read of 2026-09-04 (trace 16 addendum): classification, `decide`, `tick`/`main`, `handoff_inventory`, adoption-for-drain, the plan writer, the CLI gate test.
- Rounds 8–11 diff (456df164..HEAD, 942 insertions across nine files): the boot-id-scoped backoff (`current_boot_id` from `kern.boottime` with a monotonic-origin fallback; epoch deadline; `backoff_reset_after_reboot` event), the drain ladder clamped to the plan's stand-down phase on every poll (`_enforce_drain`: TERM due at cooperative timeout OR phase TERM/KILL; KILL due at cooperative+grace OR phase KILL), the installer's canonical-checkout refusal (`show-toplevel` must equal `/Users/edr/code/JouleWise`), the interpreter pin (refuses `/usr/bin/python3`, records `sys.executable`), the behavioural installer test with a stubbed `launchctl` and rollback matrix, the reaper detachment guard, the courier's watchdog-liveness line, and the step-0 snippet that I patched and executed both ways myself (trace 31).
- The three cold rulings (14, 19, 22), the Opus refutations (12, 18, 23) and counter-review (21), the consults (11, 12), and every delta re-audit (10, 15, 18, 20, 24, 26, 28, 30).

## Design-level answers (row 7)
1. **Fail-closed where it matters.** Plans are pre-registration evidence: only the golden retired-v1 shape is ignored; every doubtful shape holds; a hold with a live resident drains it, clamped so the KILL never lands later than t0−15 min; a plan conflict holds. This is the D-161 line drawn correctly (physics/evidence fences fail closed; operator-only guards were not added).
2. **The production path is now tested as production.** The real CLI subprocess gate, the real installer subprocess test, and D-172 make the unit-green/production-broken class detectable — the class that consumed rounds 3–5 and was named by consult, cold gate and counter-review alike.
3. **What remains deliberately open** (cold ruling 22): the first UNATTENDED night is not authorised until a launchd-spawned activation with `notice.ack` exists and a REHEARSAL_STUB night has sent its courier through the night driver's own headless path. Install is authorised after this merge and the canonical pull with step 0's digest check. LaunchAgents do not load before login: an unattended reboot is an accepted limitation this week (Ed's machine stays logged in), with the courier's liveness line as the detector.

## Overbuild / merge-ability (row 8)
The ratchet of eleven rounds left no dead mechanism: the retired opt-in dedupe, the duplicated `Probes` constructor, and the string-count doc tests were removed in rounds 5–6. Nothing further to prune.

## Integration replay (row 9)
Full unpiped suite on `int/2026-09-04-watchdog` = main d7d74225 + the final head; log `~/.claude/jobs/3c46c831/tmp/int-watchdog-replay-final.log`; exact tail appended below when it completes.
