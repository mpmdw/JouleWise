# W2 arm gate — Opus 5.5 contract lens (paired with the cold Fable judge)

Charge `05-armgate-charge.md` @ fad4aabe. Read-only; every probe executed this session. The only clone command was the Q2 `check`; after it, tree clean and ledger sha unchanged.

## Q1 Bindings — PASS
- Staged `night_plan.json` = `0395a605…c0ce`. All 14 staged files match `09-staging-sha256.txt`.
- The plan binds `repo_head` = `measurement_head` = a71a5e79…7b27, plan id `…-w2-20260927`, t0 1790524800.0, window_max_s 9000, and the charge's custody and measurement roots.
- Clone: HEAD = H, porcelain empty, `is-shallow-repository` = false, 5598 commits.
- Recomputed from the clone, equal to the notice:
  - prereg `81b65f08…ddf1`
  - frozen plan `9ab4776f…a072`, cmp-equal to the custody copy
  - protocol_v3 `9eaf92f8…31b1`
  - D-166 `dfe55f8d…c265`
  - templates `e62a461b…e5c8` / `1570b745…1fd`
  - chain source `b5beea46…d6fb`

## Q2 Ledger — PASS
- The clone's ledger is 226 lines, sha `b03be938…c63f`, equal to the W1 clone's.
- Pin at H: 226 / `bd7aee7a…6693`. step1.out shows the authenticated head equals the pin.
- In the W2 clone, `issue_calibration_acceptance_generation.py check --session-ids …-w1-20260927` with the prereg and sha flags returned rc 0:
  - `battery=pass recorded=pass`;
  - `finalized terminal=yes declared=12 filled=12 valid=6 excluded=none`;
  - admissible yes.
- No later head exists on the machine. Every other ledger has 76, 78, 126 or 176 rows.
- Lineage:
  - rows 1–176 are byte-equal to the n2 ledger (`95d152f0…`);
  - rows 1–76 equal the 78-row 09-16 fork, but row 77 differs, so the fork is not in the chain (NIT-1 holds).

## Q3 Script changes — PASS, none weaker
A line-by-line `diff` of all 8 files, W1 set against W2:
- `arm-env.zsh`: H, T0, `w1`→`w2`, and LEDGER_SOURCE plus its sha pin.
- `step0`, `step1`, `step4`: label text, plus step1's basename literal `w1`→`w2`. The assertions themselves are unchanged.
- `step2`: one comment line.
- `step3`: the three intended notice lines.
- `step5` and `README-sequence.md`: byte-identical.

No check removed or loosened; no W1 time or head left in the `.zsh` scripts; step4/5 derive boundaries from `T0_EPOCH_S` and `install_close_epoch(plan)`.

## Q4 Wrapper and schedule — PASS
- `chain.zsh` recomputes to `e27978bd…1c01`, equal to its sidecar.
- Its diff against W1's chain changes only the plan id, roots, head, the per-slot ids and locators, and `WINDOW_END_EPOCH_S` = 1790533800, which is t0 + 9000.
- Identity-epoch and T1 JSON are byte-identical to W1's (os_build 25G83).
- Rendered plists, compared with `plutil -p` against W1's:
  - The night plist is Month 9, Day 27, 09:00.
  - Dead-man is 12:35 (1790537700). That is t0 + 12900, the same offset W1 used.
  - Paths point into the w2 `.venv`; probe label per-plan; all Interactive.
- Boundaries, converted with zoneinfo:
  - install close 08:50;
  - REQUEST 08:52;
  - TERM 08:54;
  - KILL 08:55;
  - t0 09:00;
  - end 11:30;
  - courier 11:35;
  - install span 09-27 00:00 to 09-28 00:00.

  All follow t0.
- The courier binary `…/claude/versions/2.1.283` exists.

## Q5 Notice — no false line
Every line of the notice checked out against the record:
- `verdict_sha256` `07bcc13b…35a2` recomputes from the file at H, and `c5088b87` is the commit that adds it.
- "6 valid of 12", "stop line is fewer than 6" and "W3 … on count" match the dry run and Revision 5 §Sample.
- The d11 line is verified from the verdict: `delta_q_mah` 9, and the final pass (lines 86–93) shows raw and max capacity both stepping 7575→7584 at 0 mA.
- Both early touches match record items 4 and 28.
- "at least 6 h after … 03:00" is true: 1790503200 + 21600 = t0.
- NIT-3 holds: all 12 W1 slots passed, so the replacement is unused.

## Q6 Science — PASS
- Battery gate, 04:27:22 PDT: connected, not charging, 0 mA, gauge age 37 s, 100 %.
  - A-R5b re-checks it before publication and at t0 (C3).
- Spacing is exactly 6 h from W1's window end and 6 h 26 m from its chain end. "At least 6 h" is met.
- Time of day: Revision 5 has no time-of-day rule. Revision 1's generator rule (end + 300 s before the next local 07:00) is met at 11:35. Its "03:00–06:30 install span" is a description, not a constraint. Ed's any-time ruling applies.
- The identity epoch and T1 are unchanged from W1. The sampler sha `b762e5bf` matches the registration.
- W1 was admitted:
  - battery pass;
  - cadence 128.80 ms < 150 ms, CONTINUE (record item 34);
  - 6 valid, not < 6.
- W2 is therefore the registered next step. W3 follows only on a post-W2 count below 12, and the replacement is unused.
- Census: all foreign PIDs descend from the magistrate (S1 Codex seat, `--timeout 14400`, hard stop ≈07:49 < 08:50; its MCP server). Step 4's final census must show them gone.

## Findings
**BLOCKER:** none. **MATERIAL:** none.

**NIT:**
- **N1.** `scripts/README-sequence.md` is still the unedited W1 text: the title "W1 … bench sequence", the W1 cadence command, and the stale HARVEST CHECK (no `--window` or `--preregistration-sha256`). That stale command caused W1's second early touch. It is not an arm input. Annotate it before the W2 harvest to point at runbook §2.2a, and note that after W2 the count-only dry run, not the cadence stop, is the trigger.
- **N2.** The notice says "a third window W3 follows on count". Revision 5 says W3 is "permitted only if" the count after W2 is below 12. The notice also omits the battery-replacement path. It is true in substance, so no change is needed.
- **N3.** The notice reports the refused early cadence call but not the passing cadence stop (128.80 ms, CONTINUE), which is the second W2 precondition. One optional clause would fix it.
- **N4.** The 6 h spacing has zero margin measured from the window end. That is compliant; record the margin.
- **N5.** The header `To:` is the copper531 alias. Send to `claude2.glaring610@passmail.net` only; copying both addresses doubles every notice.

VERDICT: ARM
