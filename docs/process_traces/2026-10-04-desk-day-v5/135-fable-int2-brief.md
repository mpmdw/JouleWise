You are giving a cold final pass on a large change before merge. You have no prior context.

Your working directory is a detached checkout of `__HEAD__` (PR #483, branch feat/2026-10-05-v5-qualification-code). An earlier cold pass at `898c49a7` failed it. Its ruling is `/Users/edr/night-archive/desk-day-v5/fable-int.md`: read it first.
- Then read `git diff --stat 898c49a7 __HEAD__` and the code diff since then (focus on `joulewise/` and `scripts/`; the docs under `docs/process_traces/` are records).
- Check the whole change only where the delta touches it.
- You may run read-only commands, and unit tests with `/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider <files>` (TMPDIR=/tmp/dd5-fable-int2).

Rules:
- Scratch /tmp/dd5-fable-int2/ only. Do not edit the checkout or run writing git commands.
- Never run powermetrics, sudo, launchctl, systemsetup, sntp or a model.
- Do not read RUN_STATE.md, CLAUDE*.md, memory, skill files or PR bodies.
- One session, foreground only, no subagents. Budget: 75 minutes.
- Write your ruling to /Users/edr/night-archive/desk-day-v5/fable-int2.md: first line `FINAL PASS: PASS` or `FINAL PASS: FAIL`, then the findings with severity, file:line and evidence. Ending before the file exists is a protocol failure.

**What the change is for.** JouleWise measures LLM inference energy on a dedicated MacBook. Before any claim-bearing window, a qualification block runs:
- two arm-only controls, `a1` and `a2`, which arm once, never launch, and must expire;
- a privileged clock control (G10): turn network time on, prove the clock really moved, and prove the T-0 author then refuses;
- one real non-claim window, `s1`, which runs one A/B/B/A block of the real measurement pack unattended, through the full launch path.

**What changed since 898c49a7:**
1. The fixes for the earlier cold pass (B1 G9 two-root layout, B2 G1 absence-probe outcomes, M1-M3).
2. Gate-stream maximum bound to authenticated sizing; stage list authenticated before capability consumption; battery boundary records bound to lifecycle artifacts.
3. A mandatory attempt-history chain: each fresh `s1` or `s2` names its predecessor's harvest, and the harvester walks the chain and checks it against a census of the block's archive. Also: one guard-attested idle-admission abort may re-arm, an `s2` occurrence, and a NULL-attempt ledger restore that removes exactly the attempt's own reservation rows.
4. The sealed Revision-6 `scripts/prewindow_check.sh` restored byte-identical. T-0 runs a dwell of its own (CPU census, load average recorded, not vetoed).
5. G10 moved after `a2` and before `s1`'s T-0. Its helper first measures the clock offset against time servers, read-only, and proceeds only if the offset is between 20 ms and 0.4 s.
6. The T-0 stage cap (3300 s) sits outside the programmed span. The window is the span plus that cap. The cooldown is excluded from the sampler-stream maximum (it runs on its own sampler). Every anchored stream is at least 60 s.

**Judge, in order of importance:**
1. Can any of this admit a measurement window or a member that should be refused, or let a non-claim byte reach a claim path?
2. Can the attempt history be wrong (an attempt omitted, double-counted, or an allowance spent twice), or can the NULL restore remove a ledger row it should not?
3. Does G10 still prove the anchor check can fail, and can the preflight or placement let it pass without a real resync?
4. Is the frequency gate and stream sizing consistent across writer, author, ARM and G4, and could the cooldown exclusion hide a stream that is really longer?
5. Can any public output carry an energy, power or per-member duration?
6. Anything that would refuse a good window only after the launch has been consumed.
