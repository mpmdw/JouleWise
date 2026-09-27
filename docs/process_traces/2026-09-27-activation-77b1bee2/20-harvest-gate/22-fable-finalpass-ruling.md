VERDICT: MERGE

# Cold Fable 5.1 final pass (gate-ledger row 7): PR #434, merge candidate 722f7bd1

Judge: Fable 5.1, one non-interactive session, 2026-09-27 about 12:00–12:25 PDT.
No subagents, no background tasks. Scratch files are only under `/tmp/fp-harvest-77b1bee2/`.

The verdict is MERGE **subject to the two merge conditions in S1** (merge-commit method; required checks green). There is no BLOCKER.

## 0. Contamination disclosure

- **Injected before my first turn, not by my choice:** the session harness placed three texts in my context: the owner's global instruction file, this repository's `CLAUDE.md`, and the one-line index of the memory store (`MEMORY.md`). The index carries short summaries of past rulings, including one line each on directive #416, the battery-float gate and the W1/W2 checkpoints. I did not open any memory file behind that index.
- **Not read:** `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, any `CLAUDE*.md` file on disk, any memory file, any skill file.
- **How I limited the effect:** every fact this ruling relies on was re-derived in this session from the repository, the ledger, the custody root, GitHub or Gmail, and is listed under "Executed evidence". Where the injected index and a primary source could disagree (directive #416), I read the primary source (the GitHub issue) and rule from that.
- **Read as charged evidence, not trusted:** the activation record, the Sol audit report, the Opus contract lens, the operator's raw outputs in `10-w2-harvest/`.
- **Not read:** the W1 precedent ruling (`…3ba66eeb/20-harvest-gate/22-fable-finalpass-ruling.md`). I ran out of reason to open it: it was offered for comparison only, and not reading it keeps this ruling independent of the earlier one.
- **Measured values:** I read no B value (B is the per-capture timing offset this campaign measures, stored as `b_fiducial_s`). My ledger script printed only sequence numbers, digests, session ids, event names and slot dispositions. My evidence script opened `instrument_evidence.json` and read only its `battery_float` key.

## 1. Executed evidence (this session)

| # | Check | How | Result |
|---|---|---|---|
| E1 | Candidate identity | `git rev-parse HEAD`, `git log -3`, `git show --stat HEAD` | HEAD = `722f7bd161f1a1d0ae2ef624f7f29aac3e347d82`, parent `a71a5e79`, tree clean. Exactly 2 files: the pin (2 lines changed) and the new verdict file (170 lines). |
| E2 | Integration tree | `git diff --stat origin/main 2a4416c4` | `origin/main` = `670756f3`; `2a4416c4` = merge of 722f7bd1 into it; the diff is the same two files and nothing else. `a71a5e79..670756f3` touches only `tests/test_arm_readiness_evidence_t0.py`. |
| E3 | File digests | `shasum -a 256` | verdict file `51f4961828a440cbab5c7cf504d7e4536b25243414441dab5fedfb6f28f946ec` (= harvest line); pre-registration `81b65f08…ddf1`; ledger `23f72c37…1c7d`. |
| E4 | Ledger, independently | my script `ledger.py` | 276 rows; sequence numbers 1…276 with no gap; every row's `predecessor_digest` equals the previous row's `receipt_digest`; row 226 = `bd7aee7a…6693` (old pin); row 276 = `476e2ae8…9737` (new pin), a W2 slot finalization; rows 1–226 hash to `b03be938…c63f`. |
| E5 | Who owns rows 227–276 | `ledger.py`, `ledger2.py` | 25 rows carry `session_id` = W2 (1 open, 12 slot claims, 12 slot finalizations). The other 25 are `append-intent` rows, which have no `session_id` field; all 25 name W2 inside `target_core`. No row in 227–276 names W1. |
| E6 | Dispositions (no values) | `ledger.py` | W1: 6 valid (d04 d05 d06 d07 d10 d12), 6 ordinary-invalid. W2: 6 valid (d01 d03 d04 d05 d09 d10), 6 ordinary-invalid. |
| E7 | **§2.2a (vii) dry run, W1 + W2** | from the measurement root: `check --session-ids <W1> --session-ids <W2> --preregistration … --preregistration-sha256 81b65f08…` | **rc = 0.** Output byte-identical (`diff`) to the operator's `check-w1w2.out`: both windows `battery=pass recorded=pass`, `finalized terminal=yes declared=12 filled=12 valid=6 excluded=none`, `prefix pending or unresolved rows: 0`, `registration admissible for prepare-candidate: yes`. |
| E8 | **Raw battery files, read directly** | `grep` over all 24 `raw/battery_float.{pre,post}.ioreg` (12 slots × 2) | every file: exactly one `AppleSmartBattery` object; `ExternalConnected = Yes`; `IsCharging = No`; `InstantAmperage = 0`; `Amperage = 0`; `FullyCharged = Yes`; `ChargingCurrent = 0`. |
| E9 | **`probe_error` / `passed` per slot** | my script `xcheck2.py`, all 12 slots | 24 of 24 readings: `probe_error` false, `passed` true, `exit_code` 0, `timed_out` false. 0 failures. |
| E10 | Digest chain, raw bytes → evidence → verdict → ledger | `xcheck2.py` | 24 of 24 raw files hash to the value recorded in `instrument_evidence.json` and to the value in the committed verdict file; 12 of 12 evidence files hash to the verdict file's value, and each digest appears in that slot's ledger rows. |
| E11 | Reading freshness | verdict file + raw `UpdateTime` vs file times | the battery gauge's last update was 25.9–27.6 s old at each pre reading and 44.0–46.1 s old at each post reading; the rule allows 180 s. |
| E12 | Verdict file identity | file fields, `git show … \| shasum` | `tool_commit` a71a5e79; `battery_float_module_sha256` `4b4d7bb2…e7e5` equals `joulewise/battery_float.py` at a71a5e79 and at the integration tree; `ledger_head` 276/`476e2ae8…9737` equals the pin. |
| E13 | One adding commit | `git log --full-history -- <verdict path>` | W2 verdict → 722f7bd1 only. In the integration tree: W1 → c5088b87 only, W2 → 722f7bd1 only. |
| E14 | Estimator code unchanged | sha256 of the four `ESTIMATOR_CODE_PATHS` at 97082508, a71a5e79, 722f7bd1, 670756f3, 2a4416c4 | identical at all five commits. |
| E15 | Issuer rules | read `scripts/issue_calibration_acceptance_generation.py` :183–332, :1203–1257, :1650–1999 | floor constant 12 (:508); W3 refusal (:1831–1838); plateau refusal (:1852–1855); floor refusal (:1856–1859). |
| E16 | Value-free pre-check | `build_quantile_proof(11)` imported from the candidate tree | builds without refusal. (11 = n − 1 for n = 12.) |
| E17 | Owner notices | Gmail messages `1a0e42d7ad74be5f` and `1a0e43cab8a8ea93`, read in full | see §5. |
| E18 | Directive #416 | `gh issue view 416` | see §5. |
| E19 | PR state | `gh pr view 434`, `gh pr checks 434`, failing job log | open, MERGEABLE, head 722f7bd1. 10 checks pass; `test` shards 2, 3, 4, 6 pending; `gate-ledger` **fails** because all twelve ledger rows in the PR body still read PENDING. |
| E20 | Nothing modified | sizes, modification times and sha256 of ledger, lock, pin, both verdict files, before and after my runs | identical (`diff` empty). Measurement root and my worktree: `git status` clean, HEAD unchanged. All Python ran with `PYTHONDONTWRITEBYTECODE=1`; no bytecode file newer than 12:00. |

**NOT EXECUTED**
- The full test suite (gate-ledger row 9).
- `battery-verdict`, `terminal-pin`, `advance-head-pin`, the cadence report: not re-run. For the verdict I relied on E7 (the tool's own recomputation from raw bytes) plus my independent parse (E8–E10).
- `prepare-candidate`: not run, and it must not be run by a reviewer.
- W1's 24 raw battery files: not re-read. W1's verdict was re-authenticated by the tool inside E7 only.
- The preservation copy in `~/night-archive`: not re-compared.
- A search of the operating system's power log for a charge event between 09:52 and 10:00 (bears on S4).
- The W1 precedent ruling: not read (see §0).
- Whether anyone opened a capture outcome before the verdict commit: file times cannot show this, and the owner's 10:42 instruction makes it a disclosure matter, not a science one.

## 2. Ruling 1 — merge

**MERGE** this exact candidate, `722f7bd161f1a1d0ae2ef624f7f29aac3e347d82`, into `main`, as a merge commit.

Reasons:
- The commit holds exactly what the runbook's §2.2a step (iv) requires and nothing else (E1).
- The pin is the true last row of a ledger whose chain I re-walked link by link (E4), and whose first 226 rows are W1's harvested ledger byte for byte.
- The verdict is right (§3).
- The merge adds no estimator or battery-gate code change (E2, E12, E14).

Why the merge method matters: the published harvest line names `verdict_commit=722f7bd1`. A squash or a rebase would re-create the change under a new commit id, and the line held by the owner would then name a commit that is not in `main`'s history. A merge commit keeps 722f7bd1 itself in history.

## 3. Ruling 2 — the battery verdict is right

**`battery=pass` is correct.**

The registered rule (pre-registration, amendment A-R5b, "Predicate") says one battery reading passes when all of the following hold: exactly one battery object is present; the machine is on external power; it is not charging; the instantaneous battery current is within ±200 mA; the gauge's last update is no more than 180 s old. A window passes when both readings of every finalized slot pass.

What I found, from the raw bytes and not from any summary:

| Quantity | Rule | Observed, all 24 readings |
|---|---|---|
| Battery objects | exactly 1 | 1 |
| `ExternalConnected` | Yes | Yes |
| `IsCharging` | No | No |
| `InstantAmperage` | within ±200 mA | 0 mA |
| Gauge update age | ≤ 180 s | 25.9 s to 46.1 s |
| `probe_error` / `passed` | false / true | false / true |
| Raw-file digest matches its record | required | 24 of 24 |

Three slots in full, as the charge asked (times PDT, from the files' own modification times):

| Slot | Reading | Taken at | sha256 (first 12) | External | Charging | Instant mA | Raw capacity mAh |
|---|---|---|---|---|---|---|---|
| d01 | pre | 09:10:10 | `6ff0e6bb91c4` | Yes | No | 0 | 7572 |
| d01 | post | 09:13:29 | `dee13b8cb994` | Yes | No | 0 | 7572 |
| d07 | pre | 10:10:11 | `c6a6b00c3749` | Yes | No | 0 | 7584 |
| d07 | post | 10:13:30 | `1a4abb381ecb` | Yes | No | 0 | 7584 |
| d12 | pre | 11:00:12 | `fd6afc2ca7f3` | Yes | No | 0 | 7584 |
| d12 | post | 11:03:31 | `2b644e9ad4fc` | Yes | No | 0 | 7584 |

The remaining nine slots read the same way (E8–E10).

**One observation that no earlier lens reported** (finding S4). Between slot d05's post reading and slot d06's pre reading, three capacity figures each rose by exactly 12 mAh:

| Figure | d05 post (gauge time 09:52:45) | d06 pre (gauge time 09:59:45) |
|---|---|---|
| `AppleRawCurrentCapacity` (charge the gauge believes is stored) | 7572 | 7584 |
| `AppleRawMaxCapacity` (the gauge's estimate of a full battery) | 7572 | 7584 |
| `NominalChargeCapacity` | 7816 | 7828 |
| `Voltage` | 12890 mV | 12890 mV |
| `InstantAmperage`, `ChargingCurrent` | 0, 0 | 0, 0 |

- **What it most likely is:** the gauge revising its estimate of how much a full battery holds. The stored-charge figure equals the full-battery figure before and after, all three figures moved by the same amount, and the battery voltage did not move by even 1 mV. Charge flowing in would normally lift the voltage.
- **What I cannot rule out:** a short top-up charge inside the seven minutes between those two readings. The pre-registration's own disclosure describes this gauge stepping its capacity figure when a charge ends.
- **Why the verdict stands either way:** the rule is defined on the two readings that bracket each slot, and every one of them passes. Inside every slot the capacity figure is unchanged (`delta_q_mah` = 0 in all 12). The step falls between slots, outside both captures. The rule's blind spot (a charge that starts and ends between two readings) is already disclosed in the registration.
- **Residual:** d05's post reading was taken at 09:53:30 but reflects the gauge's state at 09:52:45. A charge beginning in those last 45 s would not show. This is the same disclosed limit, stated with W2's numbers. d05 is a valid slot; d06 is ordinary-invalid.

## 4. Ruling 3 — the registration consequence

### 4.1 Is "W3 is not permitted" the right reading? Yes.

The text (Revision 5, "Sample, stops and blindness"): "W3 is permitted only if the count-only dry run after W2 shows fewer than 12 valid". The dry run after W2 shows 6 + 6 = 12 valid (E7). Twelve is not fewer than twelve. So a third window is not permitted. The same paragraph adds: "No B-based exclusion or outcome-driven top-up is permitted."

The issuing tool enforces the same reading: if three sessions are named and the first two hold 12 or more valid rows, it refuses with "W3 was opened despite at least 12 valid observations after W2" (:1831–1838).

The one other route to an extra window, the battery replacement window of A-R5b, opens only when a window's battery verdict is not `pass`. Both passed. It stays closed.

**W2 is the last window of this epoch.**

### 4.2 Is n = 12 enough? Yes, with zero margin, and two terms must be kept apart.

- **Valid** is a slot's disposition in the ledger. The W3 trigger counts valid rows.
- **Retained** (a "member") is a valid row whose stored clock-anchor outcome also resolves when the issuer reads it back. The issuance floor counts retained rows: "Retained n ≥ 12 is the issuance floor".

These can differ. Here they do not: the dry run performs the same read-back on every valid row and reports `excluded=none` for both windows, so all 12 valid rows are expected to be retained. Retained n = 12 = the floor.

Zero margin means: if `prepare-candidate` drops or refuses even one member, nothing issues.

### 4.3 What can still make `prepare-candidate` refuse

| Cause | Depends on a measured value? | Curable without a capture? |
|---|---|---|
| Any member B above 0.25 s (the pulse protocol's plateau inset, `PLATEAU_INSET_S`) | **yes** | **no** |
| A member's evidence missing or not matching its digest | no | yes: restore the bytes from the preservation copy |
| A member's stored B text differing from the ledger row's | no | no tool cure; owner ruling |
| Sessions named out of order, missing `--d125-ruling`, a confounded-session flag given, a wrong `--minimum-corpus-size` | no | yes: re-run with correct arguments |
| Predecessor acceptance not the r7 generation, or registration pins malformed | no | yes: supply the right file |
| Quantile proof for 11 degrees of freedom fails | no | pre-checked here: it builds (E16) |

Only the first row is both value-dependent and incurable. That row is why §4.4 matters.

### 4.4 Is REV5-POST-W3-SHORTFALL-01 a precondition for `prepare-candidate`? Yes, in a light form.

**The forcing problem.** `prepare-candidate` is the first step that turns measured values into a decision. If it refuses because a member exceeds 0.25 s, whoever decides what happens next already knows something about the values. Any choice made after that point can be shaped, even innocently, by the outcome. The cure is to write the answer down before the step runs.

**What the registration already fixes.** Revision 5 forbids any top-up and closes W3. So the registration's own default is determinate: on refusal, nothing issues under Revision 5, and no further capture happens under it. Revision 1's sentence "any further capture is Ed's written ruling, not this registration's" sits in the "Stopping." text that Revision 5 amends without restating, so it is unclear whether it survives. That gap is what needs a ruling.

**What must be written, and ratified by the owner (Ed) or a cold gate, before `prepare-candidate` runs.** One short statement answering three questions:
1. On refusal, does the epoch's derivation under Revision 5 end? (The text supports only "yes".)
2. What becomes of the 24 W1/W2 captures? The outcome-independent answer is the one already used for the eleven 2026-09-19 captures: they become disclosed diagnostics and are never members of a later registration. Re-using them alongside new captures would be the forbidden top-up under another name.
3. Who authorizes a successor registration, and must its text be sealed before its first capture? (Owner or council; yes.)

**Why the magistrate alone should not settle it:** the answer interprets the registration where the registration is silent. That is a registration-level act, and the magistrate also runs the issuance step.

**Why this is light, not a new gate:** it is one paragraph and one approval. No code, no capture, no delay beyond the owner's reply. The magistrate has also already told the owner, in the correction email, that it will put this case to the owner or the cold gate before issuance. That promise now binds.

### 4.5 The full list to settle before `prepare-candidate`, and by whom

| Item | Who | Status |
|---|---|---|
| The refusal-branch statement of §4.4 | Ed or cold gate | **open; precondition** |
| The order of the #416 audit relative to issuance (§5, S2) | Ed confirms | **open** |
| Record, with evidence, the five conditions no tool checks: at least 6 h spacing; Interactive launch context; MLX 0.31.2 on every row; estimator code unchanged; Revision 3 chain digest | magistrate, in the prepare record and the derivation notes | contract lens verified them; I re-verified estimator code only (E14) |
| Run at a head whose four estimator-code files equal those at capture | magistrate | true at 2a4416c4 today (E14); re-check at the head actually used |
| Arguments: W1 then W2; no confounded-session flag; `--d125-ruling` given; `--minimum-corpus-size` omitted or 12 | magistrate | for the issuance brief |
| Both custody roots stay where they are | magistrate | W1 root present with 12 capture directories |
| The cold science gate and the issuance transaction that follow `prepare-candidate` | per record item 9 | not in scope here |

The contract lens's S3 list is correct. I add two items it did not carry: the #416 ordering, and the gauge-step disclosure (S4) in the derivation notes.

## 5. Ruling 4 — blockers, and what the owner notice got wrong

**Nothing blocks the merge.**

**The owner notices.**

*Correct:*
- Both harvest lines, character for character (E3, E13).
- The correction's two points: a third window is not permitted; n = 12 has zero margin.
- "There is no top-up of any kind."
- One recipient address.

*Wrong or missing:*
1. **The audit order is wrong in the first notice and the correction did not fix it.** The first notice says the three-family audit comes next and "Issuing the calibration comes after it." The directive's binding text says the opposite order: the audit's trigger message is "CLAIM-RUN WORK COMPLETE", defined as "W1/W2 issued plus the headline pipeline frozen". The activation record corrected itself (item 9). The owner was never told. (S2)
2. **The directive and the registration now pull against each other on one point, and neither notice says so.** Directive #416, clause 3: if the audit finds a defect in the derivation path, "W1/W2 are re-run before any headline run." Revision 5 permits no further window. A re-run would therefore need a new sealed registration. The owner should hear this before the audit, not after it. (S2)
3. **The gauge step is not mentioned.** "Every one reads plugged in, not charging, 0 mA" is true and complete for the rule. The +12 mAh step between d05 and d06 is a diagnostic the registration asks to be recorded, and it belongs in the record. (S4)
4. **The fixed outcome set is not named.** The contract lens asked that the notice list the outcomes the registration already fixes: issued; issued and marked `excursion_limited` (two or more members above 0.075 s); issued with `zero_headroom`; refused on the plateau inset. The registration is pinned by digest, so this is a convenience, not a repair. (N2)

## 6. Findings

### BLOCKER
None.

### SHOULD-FIX

- **S1. Merge conditions.** (a) Use `gh pr merge 434 --merge`. No squash, no rebase, no rebase-update of the branch first. (b) Merge only when the required checks on head 722f7bd1 are green. At 12:05 PDT the `gate-ledger` check fails, because the PR body's twelve rows all read PENDING, and test shards 2, 3, 4 and 6 are still pending (E19). This ruling is row 7's evidence.
- **S2. Send one more correction to the owner** covering: the audit follows issuance and the pipeline freeze, per the directive's own trigger; and the directive's "re-run W1/W2" clause would require a new registration because Revision 5 has no window left. Ask the owner to confirm the order.
- **S3. Before `prepare-candidate`:** the refusal-branch statement of §4.4, ratified by the owner or a cold gate; then the remaining rows of the §4.5 table. This does not block the merge.
- **S4. Disclose the gauge step** in the harvest record and in the candidate's derivation notes, with the numbers in §3, and say plainly that the verdict does not depend on it. Optional but cheap: search the operating system's power log for 09:52–10:00 PDT to settle whether any charge flowed.

### NIT

- **N1.** The contract lens says all 50 rows from 227 to 276 "name the W2 session". Precisely: 25 name it in `session_id`; 25 are `append-intent` rows that name it inside `target_core` (E5). The conclusion holds.
- **N2.** Add the fixed outcome set to the S2 correction.
- **N3.** Spacing is exactly 6 h 00 m on the strictest reading (W1's window end 03:00 to W2's start 09:00) and 6 h 40 m from W1's last capture to W2's first (ledger capture times). "At least 6 h" is met with no margin on the strict reading. State which reading is used in the derivation notes.
- **N4.** The "roughly 79 % assumed" yield is Revision 1's design arithmetic (valid rate 30/38). Revision 5 states no yield assumption. Attribute the figure to Revision 1 when it is next quoted.
- **N5.** My first evidence script printed `raw=rec=verdict: False` on every line. That was a fault in my print expression (a chained comparison), not in the data; the pass/fail logic was unaffected. The corrected script `xcheck2.py` prints True 24 of 24. Both outputs are kept in scratch.
- **N6.** `/tmp/fp-harvest-77b1bee2/judge.out` exists and was not created by any command of mine; I take it to be the launcher's capture of this session and left it alone.

## 7. Plain summary

1. Merge PR #434 as a merge commit once its checks are green: the pin and the battery verdict are correct, re-verified from the raw files, and nothing was modified.
2. W2 is the last window: 12 valid captures meet the floor of 12 exactly, a third window is not permitted, and the rule for "what if issuance refuses" must be written and approved by Ed or a cold gate before `prepare-candidate` runs.
3. Tell Ed two things the notices missed: the audit comes after issuance, not before; and the battery gauge's capacity figure stepped +12 mAh between slots d05 and d06, most likely a gauge re-estimate, with no effect on the verdict.
