VERDICT: MERGE

# Cold Fable 5.1 final pass (gate-ledger row 7): PR #432, candidate c5088b87

Judge: Fable 5.1, one non-interactive session, 03:21–03:31 PDT on 2026-09-27.
Candidate: `c5088b871dac4a3e75773f645c6293ffde1568b9`, parent `97082508f3648ff8575c94b0cdfcf657ba440142`.
`git ls-remote` at 03:28 showed `main` still at `97082508` and the PR branch at `c5088b87`.

## 0. Contamination disclosure

I opened none of the forbidden files (RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory files, skill files).
The session launcher, however, placed three texts in my context before my first turn, and I could not prevent it:

1. the owner's global instruction file (its writing standard and a list of playbook names);
2. this repository's tracked `CLAUDE.md` (the description of the Codex bridge);
3. the one-line index of the owner's memory directory, about 110 lines. It includes lines stating that W1 was armed, that harvest was the next step, and several standing directives.

None of the three contains a W1 measurement, a battery reading, or a claim about this commit's bytes.
Every factual statement below rests on a command I ran or a file I read in this session.
Where I rely on someone else's statement I say so and mark it NOT EXECUTED.

I also read the three evidence files the charge named (the operator record, the Sol audit, the Opus contract lens) before doing my own checks. My checks were written independently of their scripts: I did not open Sol's `audit.py`.

**Values I kept closed.** The per-capture file `instrument_evidence.json` holds both the battery readings and the timing results this campaign exists to measure (the registration calls those results "B values"). My script reads only the `battery_float` object from that file. I opened no B value, and I printed ledger rows by key name, digest and count only.

## 1. What this commit is, in plain terms

During the W1 night the machine ran twelve captures ("slots", named d01 to d12), ten minutes apart.
Each capture wrote its outcome as rows appended to a ledger file, one JSON object per line. Each row carries a SHA-256 fingerprint of its own content and the fingerprint of the row before it, so the rows form a chain in which no earlier row can be altered without breaking every later fingerprint.

The repository keeps a small file, the "pin", that names the ledger's last accepted row by its number and fingerprint. The commit moves the pin from row 176 to row 226, the last row W1 wrote.

Immediately before and immediately after each capture, the machine also ran `ioreg -r -c AppleSmartBattery` and kept the raw output. The registration (amendment A-R5b) admits a window only if all of those readings show the battery idle: charger connected, not charging, current within ±200 mA, and the battery controller's own timestamp no more than 180 s old. The commit adds one file recording that result for W1: `pass`.

## 2. Rulings on the five questions

### Q1. Merge?

**MERGE**, as a merge commit. No blocker found. The conditions attached are in the findings (S1–S4).

### Q2. Is the battery verdict right?

**Yes.** All 24 readings (12 slots, before and after) satisfy the registered rule on my own reading of the raw bytes, and the committed file records exactly what those bytes say.

What I ran:

**(a) The runbook §2.2a (vii) command, from the measurement root.** Exit code 0. Output byte-identical (`diff`) to the operator's `10-w1-harvest/check.out`:

```
d079-epoch-25g83-derivation-w1-20260927: battery=pass recorded=pass
d079-epoch-25g83-derivation-w1-20260927: kind=derivation state=finalized terminal=yes declared=12 filled=12 valid=6 excluded=none
prefix pending or unresolved rows: 0
registration admissible for prepare-candidate: yes
```

`recorded=pass` is the committed file's status; `battery=pass` is the tool's fresh recomputation from the raw bytes. The expected `os_build` MISMATCH line (25F84 against 25G83) is present and is the intended result for this epoch.

**(b) An independent audit script** (`/tmp/fp-harvest-3ba66eeb/audit.py`, Python standard library only, importing no project code). Result: `FAILED CHECKS: none`. It established:

| Check | Result |
|---|---|
| Ledger file SHA-256 | `b03be93867ceffe69bbd277fc83829600414d9cc5d53b0a28ced2d5a56abc63f`, 226 rows, numbered 1–226 without gaps |
| Every row's fingerprint recomputed from its content | all 226 match |
| Every row's "previous row" fingerprint | all 225 links match |
| Old pin | equals row 176, `0f7609ae…2512` |
| New pin | equals row 226, `bd7aee7a…6693`, the physical last row |
| Rows 177–226 | 50 rows, all belonging to W1: 1 session-open, 12 slot claims, 12 slot finalizations, 25 write-intent rows |
| Rows 1–176 | the W1 session name appears nowhere |
| Verdict file SHA-256 | `07bcc13b…35a2`, equal to the published harvest line |
| Verdict file bytes | identical in the candidate tree and the measurement root; identical to a canonical re-rendering of its own content |
| Per slot: evidence-file fingerprint | file on disk = ledger row = verdict file, 12 of 12 |
| Per reading: raw-file fingerprint | file on disk = evidence file = verdict file, 24 of 24 |
| Per reading: registered rule on my own parse | passes, 24 of 24 |
| Per reading: recorded `exit_code` 0, `timed_out` false, `probe_error` false, `passed` true, `reasons` empty, `stderr` empty | 24 of 24 |
| Per reading: recorded parsed values equal my parse of the raw bytes | 24 of 24 |
| Verdict file's ages and capacity differences | equal my arithmetic, 12 of 12 slots |

**(c) Raw files read directly** for d01, d10 and d11, before and after (six files, top-level property lines printed). One `AppleSmartBattery` object in each. Representative lines:

| Reading | ExternalConnected | IsCharging | InstantAmperage (printed) | as signed mA | Voltage mV | Raw capacity / max mAh |
|---|---|---|---|---:|---:|---|
| d01 before | Yes | No | 0 | 0 | 12896 | 7575 / 7575 |
| d01 after | Yes | No | 0 | 0 | 12896 | 7575 / 7575 |
| d10 before | Yes | No | 0 | 0 | 12892 | 7575 / 7575 |
| d10 after | Yes | No | 18446744073709551605 | −11 | 12890 | 7575 / 7575 |
| d11 before | Yes | No | 0 | 0 | 12891 | 7575 / 7575 |
| d11 after | Yes | No | 0 | 0 | 12891 | 7584 / 7584 |

The d10 value is the registration's two's-complement case: a printed integer at or above 2^63 is read as that value minus 2^64, so 18446744073709551605 − 18446744073709551616 = −11 mA, a small discharge, inside ±200 mA.

**Whole-window figures from my parse.** Current: 0 mA in 23 readings, −11 mA in one. Timestamp age: 22.85–25.30 s before each capture and 41.04–44.00 s after, against the 180 s limit. `FullyCharged = Yes` and state of charge 100 % in all 24. Voltage drifts down from 12896 mV to 12890 mV across the night and never rises.

**The one non-zero capacity difference (d11, +9 mAh) is not charging.** In d11 the gauge's current-capacity figure and its *maximum*-capacity figure both stepped from 7575 to 7584 mAh together, with current 0 mA, `IsCharging = No` and voltage unchanged at 12891 mV. A battery that took on 9 mAh would show current flowing and voltage rising, and its maximum capacity would not move. This is the gauge revising its own estimate of a full battery. The registration already records this quantity as a diagnostic that "does not bound the net charge" (A-R5b, Disclosure), so it has no role in the verdict either way.

**Limits of what the verdict can show**, as the registration itself discloses: two readings bound a capture's endpoints only. A charging episode that began and ended inside one capture's roughly 199 s span would not be seen. The flat-to-falling voltage across all 24 readings is weak independent evidence against one, not proof.

### Q3. Does Sol's F1 block this merge?

**No.** It does not block this merge, and it should not be patched into the verdict code between W1 and W2.

What F1 says: the function that recomputes the verdict (`validate_window`, `joulewise/battery_float.py:390–486`) consults two recorded fields, `exit_code` and `timed_out` (line 457), then re-parses the raw bytes. It never looks at the recorded `probe_error` or `passed` fields.

Why it does not touch W1: all 24 recorded `probe_error` values are false and all 24 `passed` values are true (Q2 table), and they agree with the raw bytes.

Why it is narrower than it sounds. I read the capture-side function `observe` (lines 306–371) to list every way it can record `probe_error = true`:

| Cause at capture | What the recomputation does with it |
|---|---|
| `ioreg` exits non-zero | caught: recorded `exit_code` ≠ 0 |
| `ioreg` times out | caught: recorded `timed_out` |
| output is not bytes | caught: `exit_code` is still unset (not 0), and the retained bytes are empty and fail to parse |
| output fails the grammar or is stale | caught: the same bytes and the same recorded wall time are re-parsed by the same code and fail the same way |
| argument list differs | unreachable in a real capture: the writer passes no substitute runner outside test mode (`scripts/validate_powermetrics_fiducial.py:2155–2180`) |

So a recorded failure that recomputes as a pass needs one of two things: parsing code that differs between capture and harvest, or an evidence file built by hand whose fingerprint was then written into a ledger row. For W1 the first is excluded: the capture ran at `97082508`, the verdict's `tool_commit` is `97082508`, and the module fingerprint `4b4d7bb2…e7e5` equals the file in the candidate tree (I hashed it).

Why a quick code fix is the wrong cure. The registration defines the window verdict as checked "from its raw bytes alone". Making the recorded flags able to change a verdict would change the registered rule while the epoch is open. The right shape is a *consistency refusal*: if a recorded flag disagrees with the recomputation, the tool refuses and names the disagreement, and no verdict changes.

**Disposition.**
- Before each remaining harvest of this epoch (W2, and W3 if it runs): a manual cross-check that every reading's recorded `probe_error` is false and `passed` is true, and that the recorded parsed values equal the raw bytes. A disagreement is reported as a finding and sent to the owner; it is never used to alter a verdict. My script does this in under a second. `/tmp` does not survive a reboot, so the operator should copy `audit.py` and `audit.out` into this trace directory.
- The code change is its own reviewed lane, landing with a replay of every committed Revision 5 verdict showing zero differences, as the module's header already requires for parser changes.

F2 (the comparison function checks status and four per-slot fields, not the ages, reasons, attempt id or capacity difference) belongs to the same lane. For W1 the unchecked fields are correct: my script recomputed them and they match.

I did **not** re-run Sol's synthetic replays of F1 and F2 (NOT EXECUTED). My ruling on them rests on reading the code.

### Q4. Does the ordering departure affect the science?

**No.** It is a procedural departure that must be disclosed, and it changes no number.

The rule that was departed from exists to stop a window being excluded *because of* its results. Two facts make that impossible here:

1. **The verdict has no input a person can choose.** `battery-verdict` (`scripts/issue_calibration_acceptance_generation.py:1573–1647`) takes the ledger, the registration digest and the raw battery bytes. It creates the file in exclusive mode and refuses if one exists. My independent recomputation gives the same answer from the same bytes.
2. **The verdict came out `pass`.** Nothing was excluded, so there is no exclusion that could have been result-driven.

What the operator saw early: the twelve `disposition=` words in `derivation-chain.log`. I printed that log with every value masked. It has 28 lines of four shapes (`slot_start slot=`, `slot_end slot= disposition=`, a completion line, and session lines) and contains no decimal measurement at all. The information seen was the count "6 valid of 12", the same count the dry run prints at step (vii).

The early cadence call: the cadence tool loads the ledger and checks it against the committed pin first (`scripts/calibration_cadence_report.py:67–72`) and reads the first capture file only at line 101. A call refused on pin mismatch therefore read no capture file and computed no frame statistic. I verified the code order; I did not witness the refused call itself (NOT EXECUTED; the operator's record item 8 is the only source).

### Q5. Anything blocking `main` at pin 226 as W2's measurement head?

**Nothing in the commit's bytes.** I rehearsed it:

- In a scratch clone under `/tmp`, I merged `c5088b87` into `97082508` with `--no-ff`. The merge commit's tree is `a0d9cedf…b515`, identical to the candidate's tree.
- On that merged head, the two history queries the authentication code runs (`git log --full-history --no-merges --no-renames [--diff-filter=A]`) each return exactly `c5088b87`.
- With W1's ledger copied into the scratch clone, the step (vii) dry run on the merged head exits 0 with `battery=pass recorded=pass` and `admissible: yes`. The tool resolves its repository root from its own location, so this run authenticated against the scratch clone, not the measurement root.
- 143 tests pass on the merged head (`tests.test_battery_float`, `tests.test_battery_float_consumers`, `tests.test_acc_25g83_rev5`; 126 s).
- I re-ran the cadence report: exit 0, byte-identical to the operator's. Median of per-capture medians 128.80 ms against the 150 ms stop; verdict CONTINUE.

Conditions W2's arm must meet are in S2 and S4.

## 3. Findings

### BLOCKER

None.

### SHOULD-FIX

**S1. The gate is not yet complete on GitHub.** At 03:25 PDT `gh pr checks 432` showed the `gate-ledger` check failing and six `test` shards plus `calibration-exits-exclusive` pending; `mergeStateStatus` was `BLOCKED`. The full test suite on the integration tree (ledger row 9) is owed by others. I ran 143 tests, not the suite. This ruling covers row 7 only.

**S2. Merge with a merge commit, and build W2 from a full clone.** Use `gh pr merge 432 --merge`. Do not squash, rebase, or rebase-update the branch first.
- I agree with the Opus lens on the reason. A squash would still leave a single adding commit, but under a new commit id. The harvest line already published `verdict_commit=c5088b87…`, and later notices must repeat it. The hazard is that the published id would no longer exist in `main`'s history.
- W2's measurement root must be a full clone, never a shallow one: the history queries walk all of history.

**S3. F1 and F2: manual cross-check at every remaining harvest of this epoch; code change as its own lane.** Details under Q3.

**S4. Disclosures and W2 inputs.**
- The harvest notice and W2's arm notice carry the harvest line, the ordering departure (both early touches), and one sentence on d11's +9 mAh (gauge re-estimate, maximum capacity moved with it, current 0 mA).
- W2's ledger source is W1's measurement-root ledger, SHA-256 `b03be938…c63f`, 226 rows.
- W1's custody root stays where it is. All 12 ledger rows locate their evidence by absolute path inside `/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/` (verified), and every later tool re-reads those bytes.
- The Opus lens's S2 items NIT-1 and NIT-6 (disclosures carried from the arm gate) and its S3 list of stale W1 literals: I did not verify these (NOT EXECUTED). Nothing I saw contradicts them.

### NIT

- **N1.** Valid count is 6 of 12, from the ledger's disposition field (6 `valid`, 6 `ordinary-invalid`). The registration stops the campaign at "fewer than 6", so W1 clears that stop with no margin. This is a planning fact for W2 and W3, not a gate.
- **N2.** Spacing. The registration requires windows "at least 6 h apart" without naming the endpoints. W1's last battery reading was at 02:33:29 PDT and the chain ended at 02:33:42. The Opus lens gives the registered window end as 03:00 PDT, which I did not verify. The conservative reading is W2's start at or after 09:00 PDT.
- **N3.** Runbook §2.1 lists `derivation-chain.log` in its reading table before §2.2a says when it may be read. Adding "after §2.2a step (viii) only" to that row removes the cause of the departure.
- **N4.** The registration calls the cadence report "pin-free"; the tool requires the committed pin. Wording drift only.
- **N5.** Operator record item 8 notes the arm README's harvest commands are stale. Use the runbook block for W2.

## 4. Not executed

| Item | Status |
|---|---|
| Full test suite on the integration tree | NOT EXECUTED (143 tests run) |
| Sol's synthetic replays of F1 and F2 | NOT EXECUTED (code read instead) |
| The early refused cadence call | NOT EXECUTED (code order verified; the call is attested by the operator only) |
| Byte-exact archive copy of the custody root, and its inventory | NOT EXECUTED |
| Uninstall result and launchd state at harvest time | NOT EXECUTED for the harvest moment; at 03:25 only `com.joulewise.magistrate` was loaded |
| Repository merge settings and branch protection | NOT EXECUTED |
| Opus NIT-1 / NIT-6 disclosures and the W2 literal list | NOT EXECUTED |
| W1's registered window end (03:00 PDT) | NOT EXECUTED |

## 5. No-modification statement

I snapshotted the measurement root (HEAD, `git status`, sizes and nanosecond modification times of the ledger, its lock file, the pin and the verdict file) and every file under the custody root's `runs/` directory before my first command there. I compared after the dry run and again after the cadence report. Both comparisons were identical.
My working tree stayed clean at `c5088b87`. The only file I wrote outside `/tmp/fp-harvest-3ba66eeb/` is this ruling.

## Summary

The battery verdict is right: all 24 raw readings show an idle battery, and the pin names the ledger's true last row.
Merge PR #432 as a merge commit once the remaining gate rows and required checks are complete; nothing in the commit blocks W2.
Sol's F1 is a real but narrow gap that did not occur here: cover it with a manual cross-check at each remaining harvest and fix it in its own reviewed lane.
