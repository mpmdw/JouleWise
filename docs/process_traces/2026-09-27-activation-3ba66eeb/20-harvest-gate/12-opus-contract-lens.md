# Harvest PR #432 (c5088b87): contract lens (row 2) and Opus counter-review (row 6)

Reviewer: Opus 5.5, read-only. Candidate: `c5088b871dac4a3e75773f645c6293ffde1568b9` (parent 97082508 = origin/main), the only commit on PR #432.
I ran these checks myself this session:
- Registration sha256 is `81b65f08…ddf1`. Verdict file sha256 is `07bcc13b…35a2`, which equals the harvest line. The file is byte-identical to `render_verdict(json.loads(file))`.
- `tool_commit` 97082508 is H. `battery_float_module_sha256` `4b4d7bb2…` equals `git show 97082508:joulewise/battery_float.py | shasum`.
- The W1 ledger has 226 rows with contiguous sequences. Row 226's `receipt_digest` is `bd7aee7a…6693`, which equals both the pin and the verdict's `ledger_head`. Its first 176 rows hash to `95d152f0…5302`, the n2 ledger (`d0b83820/01-harvest-evidence/ledger-176-sha256.txt`).
- The measurement root's HEAD is c5088b87 and its tree is clean.
- A merge-method simulation ran in a throwaway clone under /tmp (see A5).
- I opened no measured value. On the chain log I read only the key names (kind, session, settle_s, slot, disposition, …). None of them is a measured value.

## A. Contract lens (runbook §2.2a (i)–(v))

**A1. Pin via the guarded tool, set to the terminal head: conforms.**
- `advance-head-pin` ran as a dry run, then with `--execute` (`10-w1-harvest/advance-{dryrun,execute}.out`). It moved the pin 176/`0f7609ae…` → 226/`bd7aee7a…`, with operator identity and attestation recorded.
- This is the §3 item 4 desk step (runbook:2937–2942), the same route n2 took (`d0b83820/01-n2-…-harvest-record.md:51`).
- The diff touches only `sequence` and `head_digest`.

**A2. Verdict produced by `battery-verdict`: conforms.**
- The file carries every key `verdict_record` emits (battery_float.py:531–552): schema, policy_id, session_id/kind/state, identity_epoch, preregistration_sha256, ledger_head, computed_wall_time_s, tool_commit, module sha, status, and 12 slots with the 10 per-slot keys.
- The writer creates the file exclusively (`open(path,"xb")`, scripts/issue_calibration_acceptance_generation.py:1643) and has no operator-choice input (:1573–1646).

**A3. Pin and verdict in ONE commit: conforms.** `git show --stat` lists exactly these 2 files. `load_committed_verdict` step 5 requires the adding commit to change the pin, with that commit's pin equal to the verdict's `ledger_head` (battery_float.py:634–646). It holds: 226/`bd7aee7a…` on both sides.

**A4. Embedded row count and digest match the pin: yes.**
- `ledger_head` = {226, `bd7aee7a…6693`}, equal to the pin and to row 226.
- The operator's (vii) dry run in the measurement root at c5088b87 prints `battery=pass recorded=pass` (`10-w1-harvest/check.out`). That output means `authenticate_committed_verdict` succeeded end to end: slot binding to the `instrument_evidence` digests, the pin-commit check, and the raw-byte recomputation.

**A5. Merge method: MERGE COMMIT ONLY.** How the code decides "exactly one commit touches the path and it added it":
- battery_float.py:599–606 runs `git log --full-history --no-merges --no-renames [--diff-filter=A] -- <path>` over all of HEAD's history. It is not first-parent. Merge commits are skipped (:603 comment, BFG-D M-1). It then requires the adding commit's blob to equal HEAD's blob.
- **Merge commit** (simulated with `--no-ff` onto 97082508): touching = adding = `c5088b87`. It passes, and the authenticated `commit` stays c5088b87.
- **Squash** (simulated): the code also passes, but the single adding commit becomes a new SHA (`de08fe0c` in the simulation).
- **GitHub rebase-merge** always rewrites SHAs, so it has the same effect as squash.

So the operator's stated reason (record item 11; PR body) is slightly off: squash would not break the single-adding-commit rule. The real hazard is identity. The harvest line already published `verdict_commit=c5088b87`. The runbook requires every later arm notice to repeat that line (runbook:2407; NIGHT_HANDBACK.md:188–196). The issuer writes the authenticated commit into `derivation_notes.battery_verdict_records[].verdict_commit` (issue_…py:2097). Squash or rebase would make all of those disagree with main's history.

Repo settings allow merge, squash and rebase, and linear history is not required (`gh api`). The merge button is therefore not protected against the wrong choice.

**A6. TIER = FULL: correct.** TIER-01 (iii) applies (orchestration.md:170): the verdict is an admit/exclude decision over a night. Item (i) does not apply, and item (v) is marginal. The PR body's impact statement already rests the classification on (iii).

**A7. Missing from the commit: nothing. Recorded at harvest: gaps (S2).** The runbook requires only the pin and the verdict in the commit (runbook:2587–2590). The non-pass disclosures in A-R5b "Consequences" (prereg:660) do not apply to a pass.

## B. The disclosed ordering departure

**What the governing texts say.**
- A-R5b "Window verdict" (prereg:658) and A-R5b-1 (decision_log.md:12223) require the verdict "before the cadence report, before the count-only dry run and before any B value is read."
- The runbook allows only night.log, result.json, the receipt and the launchd files before (iii) (runbook:2564–2567).
- The operator read the 12 `disposition=` lines. Those carry the same count the count-only dry run reports (6 of 12 valid), but no B value. The chain log contains no measured field.
- A second pre-verdict touch is recorded in item 8: the first cadence-report call ran before the pin commit and refused with `calibration_ledger_head_mismatch`. It produced no frame statistic.

**Effect on the science: none.**
- The verdict is a deterministic function of the raw ioreg bytes, which were fingerprinted at capture (`validate_window` → `verdict_record`). `battery-verdict` takes no judgement input and refuses if a record already exists.
- The one-adding-commit rule blocks a re-roll.
- Every consumer recomputes the verdict from raw bytes and refuses on any disagreement (battery_float.py:712–745).
- The issuer computes the verdict itself for every derivation session, so a window cannot be silently omitted (prereg:660).
- The verdict came out `pass`, and the rule the ordering protects exists to prevent outcome-selected exclusion.
- §2.2a's own closing words already say this: "The reading order above is procedure; the guarantee is the custody rule" (runbook:2612–2614).

**Where else to record it.** It is already in the PR body and record item 4. It should also go into the harvest notice and repeat in W2's arm notice (S2). Structurally, the §2.1 table's `derivation-chain.log` row (runbook:2478) appears before §2.2a and does not say "only at step (viii)". That is a runbook ask (N1). No decision-log entry is needed for the science; I make no process ruling.

## C. Science consequence of 6/12 valid (counts only)

The governing text, prereg:612 (Revision 5, which amends Revision 1's "Stopping."):

> "At W1 harvest, the pin-free cadence report … if the median of the per-capture median native frame lengths is above 150 ms, stop: no W2 … If it reports fewer than 6 valid of 12, stop: no W2, return to council. W2 then runs. W3 is permitted only if the count-only dry run after W2 shows fewer than 12 valid, and is another 12-slot window. Every valid resolved member is retained. Retained n ≥ 12 is the issuance floor … No B-based exclusion or outcome-driven top-up is permitted."

What that means for W1:
- **Cadence stop:** not triggered. The median is 128.80 ms against a 150 ms limit.
- **Futility stop:** not triggered. 6 is not "fewer than 6", so the margin is zero. **W2 runs.**
- **W1 is a counted window.** It has 6 valid rows (excluded=none). Its members are the valid rows whose stored anchor resolves; that is settled at issuance (prereg:156–162). An unresolved anchor with `affine_clock_fit_empty` could still lower the count.
- **The floor is cumulative.** The simulation doc says "count-only W3 only when W1+W2 have fewer than 12 valid" (docs/calibration/acc_25g83_rev5_simulation.md:5).
  - W2 needs ≥ 6 valid for n ≥ 12 without W3.
  - At a count-only yield of 0.5, P(W2 ≤ 5 of 12) ≈ 39%, so W3 is a realistic branch.
  - The same doc's 50%-yield stress replay (:18) found zero shortfalls after W3.
  - The floor is reachable.
- **Low yield by itself triggers nothing.** The 30/38 projection (prereg:92) is Revision 1 design context, not a rule. A-R5b replacement (prereg:662) fires only on a non-pass battery verdict. W1 passed, so the epoch's one replacement window is still unused (arm-gate NIT-3: the limit is per epoch).
- Revision 5 does not say what happens if n < 12 after W3. Revision 1's corresponding sentence ("not issued … any further capture is Ed's written ruling", prereg:176) is in the Stopping text that Revision 5 amends. This is flagged for W2/W3 planning only.

## D. Counter-review for merge, and for main at pin 226 as W2's head

- No test pins the live head: `0f7609ae` appears only under docs/process_traces, and every test uses a temporary or fixture pin.
- No test globs `battery_float_verdicts/`.
- Required checks: the 12 contexts listed; strict=false.
- Gate-ledger rows 1–12 are still PENDING in the PR body. Row 9 (full suite on the integration tree) remains owed.

## Findings

**BLOCKER:** none.

**SHOULD-FIX**

**S1.** Merge with `gh pr merge 432 --merge`, never squash or rebase. Do not rebase-update the branch before merging.
- The PR body and record item 11 should correct the rationale to identity preservation of `verdict_commit` (A5).
- W2's clone must be a full clone (§0.2 already makes one), never `--depth`: `touching` walks the full history.

**S2.** The harvest notice (§2.2a (v); NIGHT_HANDBACK.md:180–196) is not shown as sent in record 00. When sent, it should carry:
- the harvest line;
- the ordering departure (both pre-verdict touches);
- arm-gate NIT-1: the 78-row 09-16 fork, "disclose at harvest" (22784e38 armgate :15);
- NIT-6: n1/n2's 24 finalized 25G83 rows (11 valid) are diagnostics and never members (:39).

Record 22784e38 item 17 (:108) ordered these carried. Neither record 00 nor PR #432 mentions NIT-1 or NIT-6. The (vii) dry run shows no A-7 blocker, which is consistent with the pinned disposition registry excluding those rows. The disclosure is still owed.

**S3.** W2 arm material must not inherit W1's literals.
- `LEDGER_SOURCE` must become `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/runs/calibration_observation_ledger.jsonl`. Copy the `.jsonl` only, not the `.lock`.
- The expected sha256 is `b03be93867ceffe69bbd277fc83829600414d9cc5d53b0a28ced2d5a56abc63f` (226 rows), replacing the n2 source and digest at 22784e38 `10-w1-arm/scripts/arm-env.zsh:27–31`.
- Also update or replace:
  - the stale README HARVEST CHECK (record item 8);
  - W1 wording in step0, step3 and step4;
  - W2 arm-record item 6, which must carry W1's harvest line (runbook:2407);
  - the §3 item 1 "equal to night 1" registration digest.
- The W1 night custody root must stay in place, because the ledger locators point into it (runbook:2572–2574). Keep it out of any iCloud offload.
- The canonical checkout's ledger is 76 rows, stale against pin 226. This is pre-existing (it was already stale against 176), but it must never be the source.

**NIT**

- **N1.** Runbook §2.1 `derivation-chain.log` row (runbook:2478): add "after §2.2a (viii) only". This is the structural cause of the departure.
- **N2.** Measure the 6 h spacing from W1's registered window end, 03:00 PDT (`WINDOW_END_EPOCH_S` 1790503200), not from the 02:33 chain completion. That puts W2 t0 at or after 09:00 PDT.
- **N3.** Pin advancement is named in §3 item 4 but not in the §2.2a block itself. The operator followed precedent, so this is only a readability gap.
- **N4.** Revision 5 is silent on a shortfall after W3 (see C). Settle it before W3 is ever needed.

CONTRACT LENS: PASS
