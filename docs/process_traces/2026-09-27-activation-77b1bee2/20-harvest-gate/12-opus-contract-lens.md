# Harvest PR #434 (722f7bd1): contract lens (gate-ledger row 2) and Opus counter-review (row 6)

Reviewer: Opus 5.5, read-only, one session, 2026-09-27 about 11:45–12:15 PDT.
Candidate: `722f7bd161f1a1d0ae2ef624f7f29aac3e347d82` (parent `a71a5e79`), the only commit on PR #434 (open, base `main`, head matches; `git ls-remote` shows `main` at `670756f3`).
Integration tree: `2a4416c4` = merge of 722f7bd1 into `670756f3`; `git diff --stat 670756f3 2a4416c4` shows the same two files and nothing else.

**What I opened and what I did not.** I read no B value, meaning the per-capture timing result this campaign measures. From the ledger I printed only key names, sequence numbers, receipt digests, session ids, event names and dispositions. One command printed W1's last three chain-log lines, which includes `slot_end slot=d12 disposition=valid`. W1 is terminal and already harvested, and that line carries a disposition, not a measured value. Scratch files are only under `/tmp/opus-lens-77b1bee2/`.

**No-modification check.** Before running anything in the W2 measurement root, I recorded the sizes and modification times of the ledger, its lock file, the pin and the verdict file, plus the ledger's sha256. I repeated this after my two `check` runs. The two snapshots are identical (`diff` reported no difference). `git status --porcelain` is empty, and HEAD is still 722f7bd1.

## Executed evidence (this session)

| Check | Command | Result |
|---|---|---|
| Registration digest | `shasum -a 256 configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (tree and `git show a71a5e79:`) | `81b65f08…ddf1` both; placeholder count `grep -c -E '<PR-L-MERGE[-]SHA>\|<TEMPLATE[-]SHA256:'` = 0 |
| Commit content | `git show --stat 722f7bd1` | exactly 2 files: pin (sequence and head_digest only) and the new verdict file |
| Verdict file sha | `shasum -a 256 …w2-20260927.json` | `51f49618…46ec` = harvest line |
| Verdict identity | file fields | `tool_commit` a71a5e79 = W2's H (night_plan `measurement_head`); `battery_float_module_sha256` `4b4d7bb2…e7e5` = `git show a71a5e79:joulewise/battery_float.py \| shasum`; `ledger_head` 276/`476e2ae8…9737` = pin |
| Ledger | `head -n 226 ledger \| shasum` and a JSON read | rows 1–226 hash to `b03be938…c63f`, which is W1's harvested ledger byte for byte. 276 rows in total. Row 226 = `bd7aee7a…6693`, the old pin. Row 276 = `476e2ae8…9737`, the new pin. All 50 rows from 227 to 276 name the W2 session. |
| Dispositions (no values) | ledger `event`/`disposition` | W1: 6 valid, 6 ordinary-invalid; W2: 6 valid, 6 ordinary-invalid |
| Single adding commit | `git log --full-history --no-merges [--diff-filter=A] -- <verdict path>` in candidate and integration trees | W2 → 722f7bd1 only; W1 → c5088b87 only |
| Dry run W1+W2 (runbook §2.2a (vii)) | `check --session-ids …w1… --session-ids …w2… --preregistration … --preregistration-sha256 81b6…` | rc=0, byte-identical (`diff`) to operator `10-w2-harvest/check-w1w2.out`: both `battery=pass recorded=pass`, `finalized terminal=yes declared=12 filled=12 valid=6 excluded=none`, prefix pending 0, **admissible: yes** |
| Dry run W2 only | same, W2 alone | rc=5, byte-identical to `check.out`: only the addendum A-7 blocker "6 rows owned by …w1…", as runbook §2.2 predicts |
| Wrapper sidecar (§2.0) | `shasum -a 256 -c chain.zsh.sha256` in the night root | OK; `SESSION_ID`, `RUNS_ROOT` exports match |
| Night outcome | `night/result.json` | verdict GO, chain_exit_code 0, DIAGNOSTIC_NO_PACK; `chain.exited` 11:03:45, `courier.sent` 11:05:03 |
| Preservation (§2.1) | `diff -rq <night root> <archive>/custody-root`; `diff -rq <root>/runs <archive>/measurement-runs` | both identical; inventory 11,266 rows = 11,266 paths |
| Uninstall | `launchctl list \| grep joulewise` | only `com.joulewise.magistrate` |
| Measurement root full clone | `git rev-parse --is-shallow-repository` | false |
| Step order | nanosecond-free `stat` mtimes of the archived outputs + commit time | inventory 11:38:25 → uninstall 11:38:36 → terminal-pin 11:39:00 → advance dry/exec 11:39:10/14 → battery-verdict 11:39:19 (verdict file mtime 11:39:19) → commit 11:39:30 (= harvest-line mtime) → cadence 11:39:45–11:40:22 → check 11:40:23 → check W1+W2 11:40:51 → manual cross-check 11:41:05 |
| Chain digest in force (Revision 3) | `chain.zsh.chain-source.sha256` and `git show a71a5e79:scripts/night_chains/calibration_derivation_only.zsh \| shasum` | both `b5beea46…d6fb` = Revision 3's digest |
| Launch-context templates | `git show a71a5e79:<template> \| shasum` | `e62a461b…e5c8` and `1570b745…d1fd` = the Revision 5 sealed digests |
| Interactive at install | `night_probe_receipt.json` `launch_context` | all three labels `ProcessType: Interactive` in W2 and W1 |
| MLX / powermetrics per row | ledger `t1_bindings` over all W1+W2 rows | `mlx_version` {0.31.2}, `powermetrics_sha256` {b762e5bf…30c5}, `estimator_revision` {…_v2} |
| Estimator code across the campaign | `git diff --quiet 97082508 670756f3 -- <the four ESTIMATOR_CODE_PATHS>` | unchanged (W1's H through current main) |
| Spacing | W1 `WINDOW_END_EPOCH_S` 1790503200 = 03:00 PDT; W1 chain complete 02:33:41 PDT; W2 t0 09:00:00, session_open 09:00:05 PDT | 6 h 00 m from W1 window end; 6 h 26 m chain to chain; 8.5 h start to start. Every reading is ≥ 6 h. |
| Repo merge settings | `gh api repos/{owner}/{repo}` | merge, squash, rebase all allowed |

NOT EXECUTED: the full test suite (row 9); an independent re-parse of the 24 ioreg files (that is the execution lens's item 7; I relied on the passing `authenticate_committed_verdict` inside `check`, which re-parses the raw bytes); whether anyone opened `derivation-chain.log` before 11:39:19. File times can show the order in which tools ran; they cannot show that nothing else was read.

## 1. Does the harvest follow runbook §2.0–§2.2a?

**Yes, step by step.**
- §2 entry conditions hold. The harvest began at 11:38, after the 11:35 completion boundary. The courier marker exists. The chain had exited, and the night agents were uninstalled before the pin moved.
- §2.0: the frozen triple was rebuilt, the sidecar verified, and the plan's `custody_root` equals the night root (per the record; I checked the sidecar and exports myself).
- §2.1: a byte-exact preservation copy and an lstat inventory were made before any removal. I re-verified both identical just now.
- (i)/(ii): the session is finalized, so no desk recovery was needed. The pin was advanced by the guarded tool (dry run, then `--execute`) to W2's terminal head. As at W1, this desk step is §3 item 4 rather than a line in the §2.2a block (see NIT N4).
- (iii): `battery-verdict` rc 0 printed exactly one line, `…: battery=pass`.
- (iv): one commit holds exactly the pin and the verdict. The code's step-5 binding (`battery_float.py:634–646`, adding commit also changes the pin to the verdict's `ledger_head`) holds, as the passing dry run proves.
- (v): the harvest line format matches runbook:2592 and NIGHT_HANDBACK.md:186–188 exactly. Its sha256 and commit are correct.
- (vi): cadence report rc 0 (a diagnostic for W2; Revision 5's 150 ms stop applies at W1 harvest only).
- (vii): dry run as above.
- (viii): disposition counts were read from the dry run only after (vii).

**Read order (record item 2).** The owner's 10:42 instruction made the read-after-commit order optional. The file-time sequence above is consistent with W2 having followed the documented order anyway, and no earlier read is recorded. As §2.2a says (runbook:2612), the guarantee is the custody rule, not the reading order, so this is disclosure, not science.

**Merge-commit-only.** It is not written in the runbook (`grep -n -i 'merge commit\|squash' docs/phase_2/derivation_night_runbook.md` finds nothing). It comes from the W1 gate (lens S1, Fable S2). The PR #434 body states it correctly. The reason: `load_committed_verdict` walks all non-merge history (`battery_float.py:599–606`), so a squash or rebase would still pass the code check, but under a new commit id. The published `verdict_commit=722f7bd1` would then name a commit that is not in `main`'s history.

## 2. Registration contract: n = 12, W3, and what the dry run does not check

**n = 12 is sufficient under Revision 5 as written.** The rule text (prereg:612):

> "W3 is permitted only if the count-only dry run after W2 shows fewer than 12 valid, and is another 12-slot window. Every valid resolved member is retained. Retained n ≥ 12 is the issuance floor; 12/13 order-statistic coverage, the floored S and t(0.995,11) support it. … No B-based exclusion or outcome-driven top-up is permitted."

- The issuer's floor is `REVISION_FIVE_MINIMUM_CORPUS_SIZE = 12` (issue_…py:508), and it refuses at `if n < minimum` (:1856).
- Membership (Revision 1 "Membership.", prereg:156–162) is "ledger disposition is valid and whose STORED anchor-v3 outcome … resolves".
- The dry run already applies that anchor replay to every valid row (`registration_dry_run`, issue_…py:303–320). Its `excluded=none` for both windows therefore means all 12 valid rows resolve. The retained n is 12 on the dry run's own evidence, not only the valid count.
- The margin is zero: any member refusal at `prepare-candidate` means nothing issues.

**W3 is NOT PERMITTED. "Unnecessary" is the wrong word.**
- The dry run after W2 shows 6 + 6 = 12 valid, which is not "fewer than 12".
- The issuer enforces this: it refuses "W3 was opened despite at least 12 valid observations after W2" (issue_…py:1830–1838).
- A third window now would be exactly the "outcome-driven top-up" the text forbids.
- The A-R5b replacement window stays unused. It fires only on a non-pass battery verdict (prereg:662), and both windows passed.
- W2 is therefore the last window of the epoch.

**What the dry run does not check before `prepare-candidate`.** These are split into what the issuer enforces anyway and what no tool checks.

(a) Enforced by `prepare-candidate` alone. The docstring calls this "list B" (issue_…py:214–219):
- the r7 predecessor;
- the Revision 5 launch-context pins sealed;
- `os_build` and powermetrics per row;
- two or three sessions, named in W1/W2 ledger order (:1791);
- 12 declared slots;
- W1 futility;
- the W3 rule;
- member evidence custody: it reads each member's evidence by absolute path, so **both** custody roots must stay in place. W1's root holds all 12 capture directories (checked);
- the plateau inset. Revision 5 says "Any member B > 0.25 s refuses issuance with the `PLATEAU_INSET_S` mechanism named" (prereg:632; issuer :1853–1855);
- the `--d125-ruling` reference, without which it refuses (:1668);
- `--minimum-corpus-size` must be omitted or equal 12.

These need no pre-check, but the operator must supply the arguments correctly: sessions W1 then W2, no `--battery-confounded-session-id`, and a d125 reference.

(b) Checked by no tool. I verified each one now (table above). The candidate's derivation notes or prepare record should restate each with evidence:
1. **Spacing**, "at least 6 h apart" (prereg:612): holds on every reading.
2. **"verified Interactive launch context"**, one of Revision 5's named physical barriers (prereg:634). The issuer only checks that the pins exist in the text. Both probe receipts record `ProcessType: Interactive` for all three labels, and the templates at H equal the sealed digests.
3. **MLX 0.31.2.** Revision 1 says "A change to either voids this registration" (prereg:136). The issuer checks powermetrics per row but not MLX. All rows read 0.31.2.
4. **"an estimator-code rotation mid-campaign"** voids the registration (prereg:137). The issuer records the estimator-code hashes of whatever checkout it runs in (:2196–2199) and does not compare them with capture time. The four `ESTIMATOR_CODE_PATHS` are unchanged from 97082508 to 670756f3. `prepare-candidate` must run at a head where that still holds.
5. **Chain digest in force** (Revision 3, prereg:545): W2's (and W1's, from its probe receipt) is `b5beea46…`.

(c) **Directive #416** (the blind three-model audit before claim-bearing runs) is a directive, not a registration rule. The record places it before the next science step, and that ordering is the magistrate's to set.

**What if `prepare-candidate` refuses?** For example: a member B above 0.25 s, a member evidence custody failure, or a quantile-proof failure. Then W3 is foreclosed and no top-up is permitted. Revision 5 is silent on what happens next. Revision 1's "any further capture is Ed's written ruling" sits in the "Stopping." text that Revision 5 amends. So the lane REV5-POST-W3-SHORTFALL-01 is not moot: it becomes "refusal after W2". Its answer should be settled, or at least stated, before `prepare-candidate` runs, so that it is fixed before the values are seen.

## 3. Merge blockers, and what the harvest notice must say

**Merge: nothing in this commit blocks it.** Merge it as a merge commit. The rows still owed are the ledger's rows 1, 7, 9, 10, 11 and 12.

**Harvest notice.** Record 00 does not show one sent yet. It must carry the following:
- **Both lines**, because NIGHT_HANDBACK.md:194–196 says: "The last window of an epoch is followed by issuance rather than an arm, so its harvest notice is the copy held outside the machine that matters". W2 is now that last window:
  - `d079-epoch-25g83-derivation-w1-20260927: battery=pass verdict_sha256=07bcc13b6f476c72280a74e21bfc2499b9085f5bf380cf891afa7f341fa535a2 verdict_commit=c5088b871dac4a3e75773f645c6293ffde1568b9` (verified: file sha and single adding commit)
  - `d079-epoch-25g83-derivation-w2-20260927: battery=pass verdict_sha256=51f4961828a440cbab5c7cf504d7e4536b25243414441dab5fedfb6f28f946ec verdict_commit=722f7bd161f1a1d0ae2ef624f7f29aac3e347d82`
- **Count and consequence:**
  - 12 valid of 24. That meets the floor of 12 exactly, with no margin.
  - The third window is **not permitted** by the registration. It is not merely "not needed".
  - If issuance later refuses, no further capture follows without a council or owner ruling.
  - The realized valid yield is 50 %, against the 30/38 (≈ 79 %) the design assumed (prereg:92, Revision 1 context). That is disclosure, not a rule.
- The read order was followed on W2 (Ed's ruling noted), plus the manual battery cross-check result and W2's cadence diagnostic (128.47 ms median).
- The next step and its order: the #416 audit and `prepare-candidate`. Name the possible issuance outcomes the registration already fixes, so they are on record before any value is read:
  - issued;
  - issued and marked `excursion_limited` (two or more members B > 0.075 s);
  - issued with `zero_headroom`;
  - refused on `PLATEAU_INSET_S`.
- Plain register for the owner, with no internal shorthand. Send to the one standing address. The W2 arm notice went to the other alias (`notice-body.txt:1`).

## W1 precedent items (PR #432 gate) and whether W2 honored them

| W1 item | Applies later? | W2 status |
|---|---|---|
| Lens S1 / Fable S2: merge commit only, full clone | yes | PR body says `--merge`; measurement root not shallow. **Pending until merged.** |
| Lens S2: harvest notice carries line + NIT-1/NIT-6 | yes | NIT-1/NIT-6/NIT-3 were carried in W2's arm notice. The W2 harvest notice is not yet shown as sent (S2 below). |
| Lens S3: W2 ledger source = W1 ledger `b03be938…` 226 rows; W1 custody root in place | yes | Honored. Ledger rows 1–226 are byte-identical; the probe receipt input digest is `b03be938…`; W1's root is present. |
| Fable S3: manual `probe_error`/`passed` cross-check at every remaining harvest; keep the script in the trace | yes | Cross-check done, 24/24 OK. Only its output was kept, not the script (N1). |
| Fable S4: W1 line, ordering departure and d11 note in W2 arm notice | yes | Honored (notice-body.txt). |
| Lens N2 / Fable N2: spacing from W1 window end 03:00 | yes | Honored: W2 t0 09:00. |
| Lens N1 / Fable N3: §2.1 table note on chain-log timing | runbook | Not changed. It is now covered by HARVEST-ORDER-SIMPLIFY-01. |

## Findings

**BLOCKER:** none.

**SHOULD-FIX**

- **S1. Merge PR #434 with `gh pr merge 434 --merge` only**, with no rebase-update first. The repository allows squash and rebase (`gh api`: all three true), so the button does not protect against a wrong choice. See §1.
- **S2. The harvest notice** must carry both battery lines, the "W3 not permitted / no top-up" statement, the zero-margin n = 12, the realized 50 % yield, and the fixed outcome set (§3). It must also correct the record item 8 wording "W3 is not needed" to "W3 is not permitted" (prereg:612; issuer :1838).
- **S3. Before `prepare-candidate`:**
  - record the five checks that no tool performs (§2(b));
  - run it at a head whose four estimator-code files equal 97082508's;
  - supply the arguments correctly (§2(a));
  - keep both custody roots in place;
  - state what happens if it refuses after W2 (REV5-POST-W3-SHORTFALL-01 is reframed, not moot).

  None of this blocks the merge.

**NIT**

- **N1.** Copy the manual cross-check script, not only its output, into `10-w2-harvest/`, as Fable's W1 S3 asked, so the check can be replayed.
- **N2.** The probe plist's digest at render time differs from its digest at install, in both windows: W2 `da82415f…` vs `418bbf2a…`, W1 `562e4341…` vs `4dea8cce…`. The night and dead-man digests are identical at both points. The pattern is systemic and the installed `ProcessType` is Interactive for all three labels. Explain it once in the derivation notes, because "verified Interactive launch context" is a named barrier that no tool checks.
- **N3.** The runbook's §2.2a does not carry the merge-commit-only rule. Put it there, in whatever lane next edits the runbook.
- **N4.** Record item 7 labels the pin advance "(i)". In the runbook, (i) is "§2.0 done", and the advance is §3 item 4 (W1 lens N3). Readability only.

CONTRACT LENS: PASS
