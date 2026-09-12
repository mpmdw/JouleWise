# Cold-gate ruling 28 — the A184 runbook paragraph about `session-refusal`

Judge: Claude Fable 5.1, cold seat convened under rule 11 (a fresh session with no loop context, ruling on a
mechanically assembled packet). Written 2026-09-12 from the detached worktree `/Users/edr/code/JouleWise-wt-coldgate-a184`
at `ca7346e4` (the PR #325 head). Packet digest recomputed over `00-PACKET.md` + Exhibit A + Exhibit B:
`02300e930ef9552633bb9da990ab302d4e093e20fd2ca1ed03b0b54690f1ac07` (matches the convening prompt's `02300e930ef95526`).

## Contamination disclosure

Before opening the packet I already held three things about this lane, all delivered by the launch context rather than
by anything I read. First, the git-status snapshot in my launch prompt listed the recent commit subjects, including
`ca7346e4` ("fix round 1 (contract refuter 14 B1): the runbook sentence names the frozen clone's older behaviour so the
harvest operator is not misled") and `7014dd0e` ("session-refusal reports a window_exhausted derivation abort as
calibration_window_exhausted"), so I knew the lane's name, that a B1 finding existed, and the gist of round 1 before
reading Exhibit A. Second, the auto-loaded memory index named "A184 resume+verify (wt-a184)" and "A184 (contract change
→ paired refuters)" as a running desk seat, and named the armed night `d079-epoch-25g83-derivation-n1-20260913` at
`f90cb8c0` with t0 02:56 on 09-13; I knew nothing of the paragraph's wording, of B2, S1 or S2, or of delta 22's
same-signature call. Third, my global instructions carry Ed's writing standard (the first-use test), which is doctrine I
applied deliberately, not lane knowledge. I did not read `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/`,
`docs/decision_log.md`, any process trace outside this packet directory, `.claude/`, or `CLAUDE.local.md`; the repo's
`CLAUDE.md` (Codex bridge notes, nothing about this lane) loaded automatically. I touched none of the three fenced
paths. The run was a single foreground session with no subagents, background tasks, edits to tracked files, or git writes.

## Q1 — the text the runbook section may say

**Ruling: none of the three packet options as written. I rule a rewritten paragraph (closest to option (ii)), which
replaces lines 1665–1671 of `docs/phase_2/derivation_night_runbook.md` at `ca7346e4` in full.** Lines 1661–1664 above it
and line 1673 below it stay as they are. It is a citation of the subcommand, as the kernel acceptance asks, and not a
harvest procedure.

Why not the options as offered: option (i) keeps a paragraph whose truth is keyed to checkout NAMES ("the frozen
clone", "main") and would still have the operator identify their checkout by its label rather than by what is in it;
option (ii) as drafted still names the frozen clone as the thing that "predates" the code, which is a date claim in
disguise; option (iii) leaves the acceptance open for no gain, since a paragraph that cannot be false for any checkout
is writable. The ruled text:

```
`session-refusal` is the recovery tool's subcommand that reads a session the
chain aborted and prints the abort as a **refusal code** — the machine-readable
name the tool prints in place of a prose reason (the same kind of name the §5
tables' "Refusal code" column carries). Which name it prints for a
`window_exhausted` abort depends on the copy of
`scripts/recover_calibration_ledger.py` you run; §2.4's `cd "$MEASUREMENT_ROOT"`
runs the measurement clone's copy at `H`, so ask that copy:
`grep -c window_exhausted scripts/recover_calibration_ledger.py`. A count of
`0` — every head before the mapping landed, including the equivalence night
armed at `f90cb8c0` — prints `calibration_session_not_open`, the tool's fallback
for an abort reason it does not know; read the reason from the `slot_unused …
reason=window_exhausted` line above instead. A count of `1` or more prints
`calibration_window_exhausted`. Neither name changes what follows: the session
is terminal either way.
```

Every factual claim in the paragraph was checked this session (Executed probes below): the `f90cb8c0` copy of the
script contains the string `window_exhausted` zero times and falls through to `SESSION_NOT_OPEN` at its lines 376–378;
the `ca7346e4` copy contains it once (line 66) and `RefusalCode.WINDOW_EXHAUSTED` is `calibration_window_exhausted`
(`joulewise/calibration_exits.py:106`); `SESSION_NOT_OPEN` is `calibration_session_not_open` at both heads
(`calibration_exits.py:66`); the subcommand is registered as `session-refusal` and dispatched at script lines 186–191
and 368–385.

**First-use table.** Line numbers are from `git show ca7346e4:docs/phase_2/derivation_night_runbook.md` (2368 lines).
"Ruled paragraph" means the term is built inside the text above, at the point where lines 1665–1671 now sit.

| Term in the ruled text | Where it is built, before or at first use | Line(s) |
|---|---|---|
| `session-refusal` | Only occurrence in the file; defined inline in the ruled paragraph ("the recovery tool's subcommand that reads a session the chain aborted and prints the abort as a refusal code"). | 1665 (ruled paragraph) |
| recovery tool | §2.4 "Desk recovery means the recovery tool run by the operator…", with the script named in the code block that follows; §8 row "desk recovery". | 1641, 1647, 2358 |
| session / aborted session / terminal | §Terms builds "session (ledger)" (§8 row 2313); "An aborted session IS terminal" is the sentence directly above the ruled paragraph; "terminal (session)" is built in §2.2 (§8 row 2356). | 1663, 2313, 2356 |
| refusal code | Was UNDEFINED before use at 1666 (delta 22's S2 is correct: the §5 table only carries it as a column header). Now defined inline in the ruled paragraph, with the §5 column named as the same kind of name. | ruled paragraph; §5 column 2139 |
| `window_exhausted` | First appears at 1226 as the chain-log evidence of a lost slot; built as an abort reason in this section's heading and first sentence; §8 row. | 1226, 1654, 1659–1663, 2359 |
| `scripts/recover_calibration_ledger.py` | Named in §2.4's desk-recovery code block. | 1647 |
| `cd "$MEASUREMENT_ROOT"` / `$MEASUREMENT_ROOT` | Exported in §0.2, rebuilt from the frozen triple in §2.0, and the first line of §2.4's code block. | 288, 1492, 1646 |
| measurement clone | The object is built in §0.2 as the "measurement root" (a fresh clone detached at H); the phrase "measurement clone" first appears at 553 and is used in this section's own definition of desk recovery; §8 row. | 276–278, 553, 1642, 2327 |
| `H` | First mention at 98; defined in §0.1 as the full SHA of the reviewed head; §8 rows for measurement head and frozen checkout triple. | 98, 249–253, 2327, 2355 |
| `f90cb8c0` | A literal SHA, not a term; it is the value of `H` for the night armed for 2026-09-13 and is verified below. First and only occurrence in the file. | ruled paragraph |
| `calibration_session_not_open` | Defined inline in the ruled paragraph as "the tool's fallback for an abort reason it does not know". Only occurrence. | ruled paragraph |
| `slot_unused … reason=window_exhausted` line | The chain log is built at 1226 and its file named in §2.1's artifact table; the literal antecedent line is the first sentence of this section. | 1226, 1535, 1661–1662 |
| `calibration_window_exhausted` | The code A184 adds; only occurrence in the file; named in the ruled paragraph as the output of a copy that carries the mapping. | ruled paragraph |
| equivalence night | Built in the front matter and "What night one is for"; §8 row "epoch-equivalence check". | 29, 105, 2306 |

**The one-sentence reason the ruled text cannot fail the B1/B2 signature:** every claim in it is conditioned on a
property the operator reads out of the copy they actually run (the grep count in that copy), never on a checkout's
name, role, or date, and it asserts nothing about which checkout any other harvest step uses, so there is no checkout
for which the paragraph is false and no other section it can contradict.

Two notes for the magistrate, outside the ruling: (a) delta 22's S1 and S2 are both correct and are absorbed by the
ruled text (no date; "refusal code" defined at first use); (b) the phrase "frozen clone" was new at 1668 and is gone —
the section's own term is "measurement clone" (1642), and §8 has no row for "frozen clone".

## Q2 — the classification

**Delta 22's same-signature call was over-inclusive: B2 is a different defect class from B1, but the escalation was
still the right outcome.** B1 was a factual claim about the recovery tool's OUTPUT that was true for the PR's checkout
and false for the checkout §2.4 tells the operator to run (verified: `f90cb8c0` lacks the mapping). B2 is a
scope over-reach: a correct instruction about one tool ("run the recovery tool from the clone") was widened into a
universal rule for all of harvest ("Harvest always uses the night's frozen clone, never main"), which contradicts §2.5's
mandatory second run of the equivalence tool from another checkout at the same head (verified at 1835–1836). B1 is a
code-versus-prose mismatch; B2 is a prose-versus-prose contradiction, and the refuter itself said the corrected output
claim "does not repeat B1". What the two share is only the surface form, a sentence whose truth depends on which
checkout the reader holds. Escalation was nonetheless correct under the round count: the round-1 fix cured B1 while
adding a blocker and two first-use defects to the same paragraph, which is exactly the "the fix is generating new
defects" condition rule 11 exists to stop, whatever label the second blocker carries. Recommend recording it as
"escalated on two consecutive blockers in one paragraph; classes differ".

## Executed probes

All run in the foreground from `/Users/edr/code/JouleWise-wt-coldgate-a184` (detached at
`ca7346e423d4fdc490190d5411c600c84b0aa729`, confirmed by `git rev-parse HEAD`). Read-only throughout.

1. `cat 00-PACKET.md exhibit-A-refuter-14-contract.md exhibit-B-delta-22.md | shasum -a 256` →
   `02300e930ef9552633bb9da990ab302d4e093e20fd2ca1ed03b0b54690f1ac07`. Exhibits C, D, E read in full.
2. `git show ca7346e4:docs/phase_2/derivation_night_runbook.md | nl -ba | sed -n '1636,1680p;1828,1842p'` → lines
   1640–1643 define desk recovery against the measurement clone; 1646 `cd "$MEASUREMENT_ROOT"`; 1659 heading
   "The other early end: `window_exhausted`"; 1665–1671 the round-1 paragraph exactly as in Exhibits C and D;
   1835–1836 "Run it twice — once from the clone, once from a second checkout at the same head". Exhibits D and E are
   verbatim.
3. `grep -n` over the same file for `refusal code` (1666, 2245 only), `frozen clone` (1668, 1671 only),
   `recovery tool` (1641, 1665), `session-refusal` (1665 only), `measurement clone` (553, 635, 946…), `chain log`
   (1181, 1226, 1670), `second checkout` (1830, 1836), `f90cb8c0` (1668 only), `calibration_session_not_open` (1669
   only), `calibration_window_exhausted` (1667 only), `slot_unused` (1226, 1535, 1661), `MEASUREMENT_ROOT` (288…),
   `derivation-chain.log` (1228, 1518, 1535), `chain.stderr.log` (874, 1536, 1653), `desk tool` (40, 1790, 1808),
   `subcommand` (1665 only), `origin/main` (249, 261, 1324), `never main` (1671 only); `H` as a bare token first at 247–253.
4. `sed -n '90,100p;245,282p;1220,1230p;1436,1446p;1490,1504p;1530,1540p;2130,2146p'` on the same file → `H` defined
   249–253; measurement root 276–278; frozen triple 1436–1440; §2.0 exports 1491–1498 with `test "$(git -C
   "$MEASUREMENT_ROOT" rev-parse HEAD)" = "$H"` at 1502; §2.1 chain-log row 1535; §5 rows 2131–2133 and the "Refusal
   code" column header at 2139. `grep -n -E '^#{2,3} '` → section map (§2 Morning harvest 1474, §2.4 1607, §2.5 1691,
   §5 2073, §8 First-use table 2298); `sed -n '2298,2368p'` → §8 rows quoted in the table above; `wc -l` → 2368.
5. `git show f90cb8c0:scripts/recover_calibration_ledger.py | nl -ba | sed -n '60,70p;370,385p'` → lines 62–66
   `_AUTOMATIC_ABORT_REFUSALS` with three entries, no `window_exhausted`; 376–378 `.get(abort_reason)` then
   `raise CalibrationLedgerError(RefusalCode.SESSION_NOT_OPEN)` when the code is `None`.
6. `git show ca7346e4:scripts/recover_calibration_ledger.py | nl -ba | sed -n '60,70p;370,385p'` → line 66
   `"window_exhausted": RefusalCode.WINDOW_EXHAUSTED,` added; fallback unchanged at 377–379.
   `git diff f90cb8c0 ca7346e4 -- scripts/recover_calibration_ledger.py` → that one added line is the whole diff.
7. `git show <head>:scripts/recover_calibration_ledger.py | grep -c window_exhausted` → `f90cb8c0: 0`, `ca7346e4: 1`.
   This is the check the ruled paragraph relies on.
8. `git show <head>:joulewise/calibration_exits.py | grep -n -E 'SESSION_NOT_OPEN =|WINDOW_EXHAUSTED ='` →
   `f90cb8c0`: line 66 `SESSION_NOT_OPEN = "calibration_session_not_open"` only; `ca7346e4`: line 66 the same plus line
   106 `WINDOW_EXHAUSTED = "calibration_window_exhausted"`.
9. `git show ca7346e4:scripts/recover_calibration_ledger.py | grep -n -E 'session-refusal|session_refusal'` → parser
   at 186–191, dispatch at 368; `sed -n '355,370p'` → `session-refusal` calls `calibration_session_status` (same
   reader as `session-status`) before mapping the abort reason.
10. `git diff --stat ace4cc3c ca7346e4` → five files, 59 insertions, 1 deletion (matches Exhibit A's flag F1 plus the
    round-1 runbook change).

NOT EXECUTED: the recovery tool itself, any test, `gen_state.py --check`, and any command inside the fenced paths; the
Exhibit A/B verification blocks are taken as the refuters' own reports. Wall time from convening to this file: under
the 12-minute budget.
