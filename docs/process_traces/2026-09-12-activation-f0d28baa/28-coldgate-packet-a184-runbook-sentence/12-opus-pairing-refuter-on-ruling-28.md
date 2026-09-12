# Opus pairing refuter on cold-gate ruling 28 (contract lens)

Read-only @ `ca7346e4` in `wt-coldgate-a184`; no tracked-file write, no fenced path touched. RB = `docs/phase_2/derivation_night_runbook.md`, SC = `scripts/recover_calibration_ledger.py`.

**VERDICT: AMEND** — every fact in the ruling verifies, but its discriminator command is cwd-dependent (re-entering the B1/B2 signature it certifies it cannot fail), and building `refusal code` with no §8 row falsifies §8's preamble at RB:2300.

## 1. Fact audit — 0 false claims

`grep -c window_exhausted SC` → **f90cb8c0: 0** (absent anywhere, exit 1); **ca7346e4: 1** at `SC:66  "window_exhausted": RefusalCode.WINDOW_EXHAUSTED,`, the whole inter-head diff. Fallback `f90cb8c0:SC:376-378` (`.get(abort_reason)` → `!= "aborted" or code is None` → `raise …(RefusalCode.SESSION_NOT_OPEN)`), unchanged at ca7346e4 377-379. `calibration_exits.py:66 SESSION_NOT_OPEN = "calibration_session_not_open"` both heads; `:106 WINDOW_EXHAUSTED = "calibration_window_exhausted"` ca7346e4 only — same enum, so "same kind of name as §5's column" holds. `RB:1646 cd "$MEASUREMENT_ROOT"`, `RB:1647 "$PY" scripts/recover_calibration_ledger.py \`, `RB:2139 | Refusal code | Meaning | Operator action |`, parser `SC:186-191`. `f90cb8c0` is an ancestor of `ca7346e4` and is the 09-13 handback H.

## 2. Grep as discriminator

- **BLOCKER (cwd).** The ruled command uses a RELATIVE path with no `cd`, so its answer depends on the reader's working directory — the very "which checkout am I in" dependence B1/B2 escalated on. From a dev checkout it returns `1` and predicts `calibration_window_exhausted` for a clone that prints `calibration_session_not_open`. Free cure: `$MEASUREMENT_ROOT` exists at RB:288 and is rebuilt from the frozen triple at RB:1492 (§2.0), upstream of line 1665 (§2.4 = 1607-1690) — name the full path.
- **SHOULD-FIX.** The rule covers ANY copy but tests only the string: the string in a comment or argparse `choices` with no mapping → count ≥1 yet prints `calibration_session_not_open`; a changed `RefusalCode` value → count 1, another name. True today at both heads, so durability not falsity; cure by requiring the match to BE the mapping entry.
- **NIT.** "fallback for an abort reason it does not know" is incomplete: SC:377 raises the same code when the session was never aborted.

## 3. First-use spot-check — ruling's table accurate

`recovery tool` RB:1641 (script 1647, §8 row 2358); `refusal code` — `grep -in` → 1666, 2139, 2245 only, nothing before 1666, so S2 right and the inline build cures it; `$MEASUREMENT_ROOT` 288/1492/1646; `H` first 98, defined 249-253, §8 rows 2327/2355. All PASS.

## 4. Contradictions

Dropping "never main" clears B2 against §2.5 RB:1835-1836 ("Run it twice — once from the clone, once from a second checkout at the same head"); §5 RB:2133 and §2.4 RB:1653-1654 consistent. **FOUND — §8 RB:2300-2301: "Every term of art in this file… A term is listed only if it does technical work."** The ruled text builds `refusal code` and introduces `session-refusal`; §8 has a row for neither, so the scope "1661-1664 and 1673 stay as they are" leaves RB:2300 false — the ruling applies this test to delete "frozen clone" but not to the term it keeps. Cure: add `| refusal code / `session-refusal` | §2.4 | The machine-readable name (`RefusalCode` in `joulewise/calibration_exits.py`) a tool prints in place of a prose reason; `session-refusal` is the recovery tool's subcommand that prints an aborted session's stored reason as one. |`

## 5. Q2 — defensible; record both framings

Correct on the object contradicted (B1 code-vs-prose, f90cb8c0 verified to lack the mapping; B2 prose-vs-prose at RB:1835-1836), and escalation is independently right: round 1 cured one blocker while adding another plus two first-use defects to seven lines. But it classifies the contradicted object, not the generator — both defects issue from identifying a checkout by NAME or role rather than by content, so on a root-cause reading of "same defect class" delta 22 was correct, not over-inclusive, and my §2 blocker is that generator surviving a third time into the ruled text.

## 6. Replacement for RB:1665-1671 (plus the §8 row above)

```
`session-refusal` is the recovery tool's subcommand that reads a session the
chain aborted and prints the abort as a **refusal code** — the machine-readable
name the tool prints in place of a prose reason (the same kind of name the §5
tables' "Refusal code" column carries). Which name it prints for a
`window_exhausted` abort depends on the copy of
`scripts/recover_calibration_ledger.py` you run, and §2.4's `cd
"$MEASUREMENT_ROOT"` runs the measurement clone's copy at `H`, so ask that copy
by its full path:
`grep -c window_exhausted "$MEASUREMENT_ROOT/scripts/recover_calibration_ledger.py"`.
A count of `0` — every head before the mapping landed, including the
equivalence night armed at `f90cb8c0` — prints `calibration_session_not_open`,
which that copy also prints for a session that was never aborted; read the
reason from the `slot_unused … reason=window_exhausted` line above instead. A
count of `1` or more, where the matched line is the mapping entry
`"window_exhausted": RefusalCode.…`, prints `calibration_window_exhausted`.
Neither name changes what follows: the session is terminal either way.
```

## What I ran

1. `git rev-parse HEAD` → `ca7346e423d4fdc490190d5411c600c84b0aa729`
2. `git show f90cb8c0:SC | grep -c window_exhausted` → `0` (exit 1); ca7346e4 → `1` (line 66)
3. `git show f90cb8c0:SC | nl -ba | sed -n '58,72p;365,388p'` → 62-66 three-entry map; 376-378 fallback
4. `git diff f90cb8c0 ca7346e4 -- SC` → one `+` line
5. `git show <head>:joulewise/calibration_exits.py | grep -nE 'SESSION_NOT_OPEN =|WINDOW_EXHAUSTED ='` → 66 both, 106 ca7346e4 only
6. `git show ca7346e4:RB | nl -ba | sed -n '1636,1680p;1826,1844p;2125,2150p'` → 1646/1647; 1665-1671 = Exhibits C/D; 1835-1836 = Exhibit E; 2133; 2139
7. `grep -in 'refusal code'` → 1666, 2139, 2245; `grep -n 'recovery tool'` → 1641, 1665; `grep -n MEASUREMENT_ROOT` → 288, 1492, 1646
8. `… sed -n '94,100p;245,256p;1488,1504p;2296,2316p;2350,2368p'` → `H` 98/249-253; 1492 export from triple; 2300-2301 §8 preamble; rows 2327/2355/2358/2359 — **no `refusal code` / `session-refusal` row**
9. `grep -nE '^#{2,3} '` → §2.0 1481, §2.4 1607, §2.5 1691, §5 2073, §8 2298; `wc -l` → 2368
10. `git log -1 f90cb8c0` → handback H for d079-…-20260913; `git merge-base --is-ancestor f90cb8c0 ca7346e4` → exit 0
11. `git show ca7346e4:SC | nl -ba | sed -n '184,193p'` → parser 186-191

NOT RUN: the recovery tool, any test, anything in a fenced path, any tracked-file write.
