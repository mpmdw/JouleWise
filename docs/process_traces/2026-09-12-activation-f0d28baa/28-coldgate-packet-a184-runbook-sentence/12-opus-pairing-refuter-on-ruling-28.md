# Opus pairing refuter on cold-gate ruling 28 (contract lens)

Read-only @ `ca7346e4` in `wt-coldgate-a184`. RB = `docs/phase_2/derivation_night_runbook.md`, SC = `scripts/recover_calibration_ledger.py`.

**VERDICT: AMEND** — every fact verifies, but the ruled discriminator is cwd-dependent (re-entering the B1/B2 signature it certifies it cannot fail) and `refusal code` is built with no §8 row, falsifying RB:2300.

**1. Facts (Q1): no false claim.** `grep -c window_exhausted SC`: f90cb8c0 **0** (absent, exit 1), ca7346e4 **1** at `SC:66 "window_exhausted": RefusalCode.WINDOW_EXHAUSTED,`, the only inter-head diff. Fallback `f90cb8c0:SC:376-378` (`.get(abort_reason)`; `!= "aborted" or code is None`; `raise …(SESSION_NOT_OPEN)`); same at ca7346e4 377-379. `calibration_exits.py:66 SESSION_NOT_OPEN = "calibration_session_not_open"` both heads; `:106 WINDOW_EXHAUSTED = "calibration_window_exhausted"` ca7346e4 only; one enum. `RB:1646 cd "$MEASUREMENT_ROOT"`, `RB:1647 "$PY" scripts/recover_calibration_ledger.py`, `RB:2139 | Refusal code | …`.

**2. The grep. BLOCKER (cwd):** the ruled command gives a RELATIVE path with no `cd`, so its answer depends on the reader's cwd — the "which checkout am I in" dependence B1/B2 escalated on: from a dev checkout it returns 1, predicting `calibration_window_exhausted` for a clone that prints `calibration_session_not_open`. Free cure: `$MEASUREMENT_ROOT` is at RB:288, rebuilt at RB:1492 (§2.0), both upstream of 1665. **SHOULD-FIX:** the rule covers ANY copy but tests only the string — in a comment or argparse `choices` with no mapping, count ≥1 yet `calibration_session_not_open`; with a changed `RefusalCode` value, count 1 and another name. True at both heads today (durability, not falsity); require the match to BE the mapping entry. **NIT:** SC:377 prints the same code for a session never aborted, so the "unknown reason" gloss is partial.

**3. First-use spot-check: the ruling's table is accurate.** `recovery tool` RB:1641 (§8 2358); `refusal code` hits only 1666/2139/2245, so S2 was right; `$MEASUREMENT_ROOT` 288/1492/1646; `H` first 98, defined 249-253. PASS.

**4. Contradictions.** Dropping "never main" clears B2 against §2.5 RB:1835-1836 ("Run it twice — once from the clone, once from a second checkout at the same head"); §5 RB:2133 and §2.4 RB:1653-1654 stay consistent. **FOUND — §8 RB:2300-2301, "Every term of art in this file… listed only if it does technical work."** The ruled text builds `refusal code` and introduces `session-refusal`; §8 rows neither, so its scope ("1661-1664 and 1673 stay") leaves RB:2300 false — and the ruling uses that very test to delete "frozen clone". Cure: add a §8 row — `| refusal code / `session-refusal` | §2.4 | The machine-readable name (`RefusalCode`) a tool prints instead of a prose reason; `session-refusal` prints an aborted session's stored one. |`

**5. Q2.** Defensible on the object contradicted (B1 code-vs-prose; B2 prose-vs-prose at RB:1835-1836), and escalation holds regardless, since round 1 cured one blocker while adding another plus two first-use defects to seven lines. But it classifies the contradicted object, not the generator — both issue from naming a checkout by role instead of reading its content — so on a root-cause reading delta 22's call stands, and my §2 blocker is that generator surviving a third time.

**6. Replacement for RB:1665-1671:**

```
`session-refusal` is the recovery tool's subcommand that reads an aborted
session and prints its abort as a **refusal code** — the machine-readable name
the tool prints in place of a prose reason, the kind §5's "Refusal code"
column carries. Which name it prints for a `window_exhausted` abort depends on
the copy of `scripts/recover_calibration_ledger.py` you run, and §2.4's
`cd "$MEASUREMENT_ROOT"` runs the measurement clone's copy at `H`, so ask that
copy by full path:
`grep -c window_exhausted "$MEASUREMENT_ROOT/scripts/recover_calibration_ledger.py"`.
A count of `0` — every head before the mapping landed, including the night
armed at `f90cb8c0` — prints `calibration_session_not_open`, which it
also prints for a session never aborted; read the reason from the
`slot_unused … reason=window_exhausted` line above instead. A count of `1` or
more whose matched line is the entry `"window_exhausted": RefusalCode.…`
prints `calibration_window_exhausted`. Either way the session is terminal.
```

**What I ran** (read-only; tool, tests, fenced paths NOT run; nothing written). `git rev-parse HEAD` → `ca7346e4…a729`. `git show <head>:SC | grep -c window_exhausted` → `0` (exit 1) / `1`. `git diff f90cb8c0 ca7346e4 -- SC` → one `+` line. `git show <head>:SC | nl -ba | sed -n '58,72p;365,388p;184,193p'` → map, fallback, parser. `grep -nE 'SESSION_NOT_OPEN =|WINDOW_EXHAUSTED ='` on `calibration_exits.py` → 66 both heads, 106 ca7346e4 only. `git show ca7346e4:RB | nl -ba | sed -n` over the eight ranges cited above, plus `grep -in`, `grep -nE '^#{2,3} '`, `wc -l` (2368) → every RB line as cited, Exhibits C/D/E verbatim. `git merge-base --is-ancestor f90cb8c0 ca7346e4` → 0.
