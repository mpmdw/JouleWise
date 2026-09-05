# Magistrate synthesis of the structural consult, and the round-5 contract

Date: 2026-09-04. Trigger: the standing escalation trigger (CLAUDE.local rule 11) fired — rounds 3 and 4 failed with the same signature (unit suite green, production path broken: B-1 at the cold gate, then F1–F5 in trace 10). Per the rule, the spend was a CONSULT, not round five: Sol xhigh design lens (trace 11) and Opus contract lens (trace 12). The blind cold Fable seat convenes on packet 21 after this round, as already mandated.

## Rulings (magistrate; both seats agreed unless noted)

R-1 **Root cause** (both seats, evidence in 11 §Q1 / 12 §Q1): an untested composition boundary. Tests inject doubles for census/git/process/spawn and hand-author plans; no test reaches `main → real_dependencies → production_census`; the watchdog re-declares a `Probes` constructor that `scripts/run_night.py:make_probes` already owns; code, fixture, and oracle were authored in the same seat and commit; tests 189-205 ratify F2. The gauntlet could not fail.

R-2 **Production-shaped CLI test is the gate** (12 §Q2 shape adopted; 11 §Q2 fail-closed cases folded in): `tests/test_magistrate_watchdog_cli.py` runs the real `scripts/magistrate_watchdog.py tick` as a subprocess against a temp custody parent with four sibling roots — valid active v2 (real temp git checkout), golden retired-v1 file, the valid plan truncated to 40 %, the valid plan minus `measurement_head` — no `--dry-run` for hold cases; assertions: rc 0, no traceback, `state.json` written; exactly one `plan_retired_v1` event and no v1-reason hold; `HOLD_UNSAFE` naming both bad plan paths; no `attempts/`; positive control admitting `{FENCED, HOLD_CENSUS}`. The seat must show this test RED on the current head, then GREEN.

R-3 **Fixture contract**: a production `write_night_plan()` at the arming boundary (the repo today has only readers and four hand-maintained schema copies); no v2 dict literal in any test; invalid cases are named mutations of a written valid plan. One `Probes` constructor (reuse `make_probes`); `agent_census` narrowed to what it uses.

R-4 **Fail-closed classification** (both seats; D-161 applied to pre-registration evidence): IGNORE-and-record only a plan POSITIVELY identified as retired v1; HOLD `night_plan_unreadable` for unparsable JSON (re-read every tick, never latch); HOLD `night_plan_malformed` for v2 missing required fields and for future authorship. `load_plans` errors must populate the `HOLD_UNSAFE` limb (AD-2); tests asserting LAUNCHING on a corrupt plan are replaced (AD-12).

R-5 **Handoff kill list** — Opus's split adopted over Sol's "ancestry sufficient": inventory emits `owned` (ancestry-closed from the recorded interactive twin) and `unclassified_candidates` separately; the reaper signals `owned` only; promotion only by explicit `--adopt-pid P --start T` recorded in the handoff file. Identity = (pid, start_time); re-validate before EACH signal; absent = success, start-changed = reuse-skip; root last; re-snapshot after TERM and after KILL; any recorded pair alive after KILL = failure regardless of census. `_is_interactive_claude` must not classify a headless `claude -p` as interactive (AD-7). KILL ladder follows `STOP_COOPERATIVE_S` (9 min), not 15 s (AD-9); the reaper imports by absolute checkout path (AD-10).

R-6 **Prompt fence** (both seats): render `@@FENCED_CHECKOUTS@@` at spawn as canonical repo ∪ every ARMED (authored, not completed) valid-v2 plan's `measurement_root`, as a deterministic JSON list of (plan_id, root, head); overlapping spans with different roots, or one root at two heads → `HOLD_UNSAFE plan_conflict`; non-overlapping spans are not a conflict.

R-7 Fold AD-1…AD-13 from trace 12; AD-3/4/5/6 are should-fix in this round.

Process proposal (NOT adopted here; for packet 21 / the cold gate): "a production-shaped subprocess test of the real entry point is a mandatory gate row for any watchdog/launcher/installer change".

## Round-5 brief (Sol xhigh; WRITE_SCOPE in the launch)

Implement R-2…R-7 on the current branch head; no other behaviour changes; demonstrate the CLI test red then green (paste both tails); run the three night modules + the new CLI module; mutation: re-introduce the missing `measurement_head` kwarg → CLI test fails (paste). Report as trace 14 with a clause map R-2…R-7, AD-1…AD-13 → file:line.
