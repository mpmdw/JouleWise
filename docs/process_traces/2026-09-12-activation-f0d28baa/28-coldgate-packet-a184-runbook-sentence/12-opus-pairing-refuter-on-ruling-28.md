# Opus pairing refuter on cold-gate ruling 28 (contract lens)

Read-only from `/Users/edr/code/JouleWise-wt-coldgate-a184` @ `ca7346e4`. No tracked-file writes, no fenced path touched. Runbook = `docs/phase_2/derivation_night_runbook.md`; script = `scripts/recover_calibration_ledger.py`.

**VERDICT: AMEND** — every fact in the ruling verifies, but the ruled paragraph's own discriminator is cwd-dependent (re-entering the B1/B2 signature it certifies it cannot fail) and building `refusal code` with no §8 row falsifies §8's preamble at `:2300`.

## 1. Fact audit — 0 false claims

- `grep -c window_exhausted script`: **f90cb8c0 → 0** (string absent anywhere, grep exit 1); **ca7346e4 → 1**, `script:66  "window_exhausted": RefusalCode.WINDOW_EXHAUSTED,`. That line is the entire inter-head diff.
- Fallback `f90cb8c0:script:376-378`: `code = _AUTOMATIC_ABORT_REFUSALS.get(str(output.get("abort_reason")))` / `if output.get("session_state") != "aborted" or code is None:` / `raise CalibrationLedgerError(RefusalCode.SESSION_NOT_OPEN)`; unchanged at ca7346e4 `377-379`.
- `calibration_exits.py:66 SESSION_NOT_OPEN = "calibration_session_not_open"` at both heads; `:106 WINDOW_EXHAUSTED = "calibration_window_exhausted"` at ca7346e4 only. Same `RefusalCode` enum → "same kind of name as §5's column" true.
- Runbook `:1646 cd "$MEASUREMENT_ROOT"`, `:1647 "$PY" scripts/recover_calibration_ledger.py \`, `:2139 | Refusal code | Meaning | Operator action |`. Parser `script:186-191`, dispatch `367-384`. `f90cb8c0` = ancestor of `ca7346e4`, subject "Handback H for the equivalence night d079-epoch-25g83-derivation-n1-20260913".

## 2. Grep as discriminator

**BLOCKER (cwd).** The ruled command uses a RELATIVE path with no `cd`; its answer depends on the reader's working directory — the same "which checkout am I in" dependence B1/B2 escalated on. Consulted from a dev checkout it returns `1` and predicts `calibration_window_exhausted` for a clone that prints `calibration_session_not_open`. Free cure: `$MEASUREMENT_ROOT` exists at `:288` (§0.2) and is rebuilt from the frozen triple at `:1492` (§2.0); line 1665 is inside §2.4 (1607-1690), downstream of both — use the full path.

**SHOULD-FIX.** The paragraph rules on ANY copy but tests only the string: (a) string in a comment/docstring/argparse `choices` with no mapping → count ≥1 yet prints `calibration_session_not_open`; (b) a differing `RefusalCode` value → count 1, another name. True today at both enumerated heads; durability, not falsity. Cure: require the match to BE the mapping entry.

**NIT.** "fallback for an abort reason it does not know" is incomplete — `:377` raises the same code when `session_state != "aborted"`, so it cannot distinguish that from an unknown reason.

## 3. First-use spot-check (ruling's table accurate)

`recovery tool` `:1641` (+ script `:1647`, §8 `:2358`); `refusal code` — `grep -in` → 1666, 2139, 2245 only, nothing before 1666, so S2 right and the inline build cures it; `$MEASUREMENT_ROOT` `:288`, `:1492`, `:1646`; `H` first `:98`, defined `:249-253`, §8 `:2327`, `:2355`. All PASS.

## 4. Contradictions

B2 cured: the ruled text drops "never main", so no conflict with §2.5 `:1835-1836` ("Run it twice — once from the clone, once from a second checkout at the same head"). §5 `:2133` and §2.4 `:1653-1654` consistent. **FOUND — §8 `:2300-2301`: "Every term of art in this file… A term is listed only if it does technical work."** The ruled text builds `refusal code` and introduces `session-refusal`; §8 has a row for neither. The ruling applies this very test to delete "frozen clone" but not to the term it keeps, and its scope ("1661-1664 and 1673 stay as they are") leaves `:2300` false. Cure — add: `| refusal code / `session-refusal` | §2.4 | The machine-readable name (`RefusalCode` in `joulewise/calibration_exits.py`) a tool prints in place of a prose reason; `session-refusal` is the recovery tool's subcommand that prints an aborted session's stored reason as one. |`

## 5. Q2 — defensible; record both framings

Sound on the object contradicted (B1 code-vs-prose, `f90cb8c0` verified to lack the mapping; B2 prose-vs-prose, verified at `:1835-1836`), and escalation is independently right because round 1 cured one blocker while adding another plus two first-use defects to seven lines. But it classifies the contradicted object, not the generator: both defects issue from one disposition — identifying a checkout by NAME or role ("frozen clone", "main", "harvest") instead of by content — so on a root-cause reading of "same defect class" delta 22 was correct rather than over-inclusive, and my §2 blocker is a third instance of that generator surviving into the ruled text. Record as "two consecutive blockers in one paragraph; contradicted-object classes differ, generator common".

## 6. Replacement for lines 1665-1671 (plus the §8 row above)

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
2. `git show f90cb8c0:script | grep -c window_exhausted` → `0` (exit 1); `grep -n` → empty. Same at `ca7346e4` → `1`, `66: "window_exhausted": RefusalCode.WINDOW_EXHAUSTED,`
3. `git show f90cb8c0:script | nl -ba | sed -n '58,72p;365,388p'` → `62-66` three-entry map; `376-378` fallback (quoted §1)
4. `git diff f90cb8c0 ca7346e4 -- script` → one `+` line
5. `git show {f90cb8c0,ca7346e4}:joulewise/calibration_exits.py | grep -n -E 'SESSION_NOT_OPEN =|WINDOW_EXHAUSTED ='` → `66:` both, `106:` ca7346e4 only
6. `git show ca7346e4:runbook | nl -ba | sed -n '1636,1680p'` → `1646`, `1647`, `1659` heading, `1665-1671` round-1 paragraph verbatim (= Exhibits C/D)
7. `… sed -n '1826,1844p'` → `1835-1836` run-it-twice sentence (= Exhibit E)
8. `… sed -n '2125,2150p'` → `2133` window_exhausted row, `2139` "Refusal code" header
9. `grep -in 'refusal code'` → `1666, 2139, 2245`; `grep -n 'recovery tool'` → `1641, 1665`; `grep -n MEASUREMENT_ROOT` → `288` first, `1492`, `1646`
10. `… sed -n '94,100p;245,256p;274,292p;1488,1504p;2296,2316p;2325,2330p;2350,2368p'` → `98`/`249-253` `H`; `276-278` measurement root; `1492` export from triple; `2300-2301` §8 preamble; rows `2327/2355/2358/2359` — **no `refusal code` or `session-refusal` row**
11. `grep -n -E '^#{2,3} '` → §2 `1474`, §2.0 `1481`, §2.4 `1607`, §2.5 `1691`, §5 `2073`, §8 `2298`; `wc -l` → 2368
12. `git log -1 f90cb8c0` → handback H, 09-13 equivalence night; `git merge-base --is-ancestor f90cb8c0 ca7346e4` → exit 0
13. `git show ca7346e4:script | nl -ba | sed -n '184,193p'` → parser `186-191`

NOT RUN: the recovery tool, any test, anything inside a fenced path, any write to a tracked file.
