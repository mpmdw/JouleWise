# Cold Fable ruling — A291-FINALPASS-01 (PR #409, S = c5cbfd9e)

Judge: Claude Fable 5.1 (claude-fable-5-1), cold, single non-interactive session.
Worktree: `/Users/edr/code/JouleWise-wt-coldgate-278ebc9e-final` at HEAD `2070efe2cc1d54b09dc2bda25c8076647130c9e1` (detached).
Session start (UTC): 2026-09-25 11:03:02. Wall used: about 8 minutes of the 45.
Packet directory: `docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/` (below, `P/`).

## 0. Disclosure of auto-loaded context

The harness injected three files before I acted: the global `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (truncated by the harness). None was requested. I did not open CLAUDE.local.md (absent from this worktree, as the convene script requires), RUN_STATE.md, TASK_QUEUE.md, any council log, run report, memory topic file, or any process-trace file outside `P/`. Nothing from the memory index is used below. No subagents, no background tasks, no sudo/launchctl/powermetrics/systemsetup, no discovery suite, no writes other than this file.

## 1. Trust-anchor verification (charter §9) — recorded before any merits reading

Method: `python3 scripts/validate_gate_packet.py --packet P/00-charge.md --charter docs/process/coldgate_charter.md --expected-charter-sha256 <X> --expected-packet-sha256 f7e6a218…4615e5`, run twice as the convening message instructs; then an independent `shasum -a 256` on both files.

| Run | Expected charter sha | Observed charter sha | Result | Reason |
|---|---|---|---|---|
| 1 (deliberate typo) | `…c95d82` | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | REFUSE (rc=2) | `charter_trusted_observed_mismatch` |
| 2 (correct anchor) | `…c95d81` | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | **REFUSE (rc=2)** | `exhibit_unreadable`, details `[{"path":"ex-03-regate-d2e751df.log"}]` |

Packet sha: expected `f7e6a2186d8d316bfa4c4194e8f851cebf5053a6c9f56efc3c1bd83f1b4615e5`, observed (validator and shasum) identical. Charter sha: observed identical to the correct anchor on both runs. Exhibit manifest digest observed `8dd8cc47376e1916eda53e51d7dfa7f6ab273eec625cf19104d1e3c12ac462a4`. Of the 30 manifest exhibits, 29 hash-match their pins; `ex-03-regate-d2e751df.log` (pinned `02d0224c89b9b3e6e962702ea1ba50e042fc31510d0de99df5f272ebf84bd559`) is absent from the packet directory, observed sha `null`. `judge_handoff_bound: false`.

The convening instruction is: "refuse to judge unless that PASSes." It did not PASS. The charge itself says (`P/00-charge.md`, "What is asked"): "a missing item is a REFUSE of this pass, not a NO-MERGE." Item 3's first exhibit is missing. Both rules point the same way.

## 2. Verdict

**REFUSE — all questions of A291-FINALPASS-01.** No MERGE and no NO-MERGE is issued. This REFUSE has no effect on the merits of PR #409 and authorizes nothing (charter §8). I did not read the merits exhibits and executed none of the items 1–3 probes, because the packet failed its own admission test before the merits were reached; ruling on a packet whose frozen exhibit set cannot be reproduced in the judge's checkout would be exactly the kind of "going looking" charter §4 forbids.

### 2.1 Exact defect (verified, file:line)

1. `P/00-charge.md` "Exhibit manifest" pins `ex-03-regate-d2e751df.log`. The file does not exist in the judge worktree: `git ls-tree HEAD P/` lists 31 entries (00-charge, 09-convene-script, 29 exhibits) and none matches `ex-03`; `git status --ignored --short P/` is empty; `git log --all -- P/ex-03-regate-d2e751df.log` is empty. It was never committed on any ref.
2. Root cause: `.gitignore:45` reads `docs/process_traces/**/*.log`; `git check-ignore -v` returns exactly that rule for the exhibit path. The rule landed in commit `1d4b4ba4` (2026-09-01, "Untrack codex-run-v3 sidecar logs committed by mistake; ignore them under process_traces"). The packer's ordinary `git add` therefore silently skipped the log. The "(validator PASS)" in the HEAD commit subject (`2070efe2`) was necessarily obtained in a checkout where the untracked, ignored file still sat on disk (the canonical root, which I may not touch). The packet as committed is therefore not the packet that was validated.
3. The convene script `P/09-convene-script.sh` runs the judge in this worktree and does not itself run the validator before launching, so the discrepancy between "validated where assembled" and "readable where judged" was not caught.

### 2.2 Minimum cure (exact text for the packer seat P and the checker seat K)

Seat P (packet assembler) does the following, in order, in the packets worktree, touching nothing else:

1. Rename the exhibit so it is not caught by the ignore rule: `git mv` is not possible (untracked), so copy the original bytes to `P/ex-03-regate-d2e751df.log.txt` and confirm `shasum -a 256` of the copy equals `02d0224c89b9b3e6e962702ea1ba50e042fc31510d0de99df5f272ebf84bd559`. If the bytes differ, STOP: the log has changed since the manifest was pinned and must be regenerated by re-running the named tests at d2e751df in a `git archive` copy, with the new digest recorded.
2. In `P/00-charge.md`, replace the manifest line `02d0224c…bd559  ex-03-regate-d2e751df.log` with `02d0224c…bd559  ex-03-regate-d2e751df.log.txt` (same digest, new name), and replace the two prose references to `ex-03-regate-d2e751df.log` (item 3 bullet one) with the new name.
3. Add item 10's missing exhibit: save the validator receipt JSON, produced in the JUDGE worktree after step 5, as `P/ex-10-validator-receipt.json` and pin it in the manifest. (See finding M-1.)
4. Recompute the packet sha (`shasum -a 256 P/00-charge.md`) and write it into `P/09-convene-script.sh` as `PACKET_SHA`, and into the convening message's "Trust anchors" clause.
5. Commit with `git add P/` (no `-f` needed once the suffix is `.txt`), then check out the new commit in the judge worktree and run the validator there with the correct charter sha. Do not launch a judge until that run prints `"result":"PASS"`. Paste the receipt into the commit message or into `ex-10`.

Seat K (checker) verifies, before any judge is convened: (a) `git ls-tree HEAD P/` contains every manifest path; (b) `git check-ignore -v` over every manifest path returns nothing; (c) the validator receipt in the judge worktree is PASS with `charter_sha256 = 099de884…c95d81` and `packet_sha256` equal to the value in `09-convene-script.sh`. Any (a)–(c) failure blocks convening.

Alternative accepted: `git add -f P/ex-03-regate-d2e751df.log` with no rename and no manifest change (packet sha unchanged). I recommend the rename, because every future `.log` exhibit will hit the same rule and a `.txt` suffix makes the failure impossible rather than merely caught.

## 3. Findings (tiered; severity independent of verdict)

**B-1 BLOCKER — Packet not reproducible in the judge's checkout.** Manifest exhibit `ex-03-regate-d2e751df.log` is ignored by `.gitignore:45` and was never committed; validator result REFUSE `exhibit_unreadable`. Effect: item 3 ("Re-gate outputs", the 49-test log) cannot be verified by anyone working from the tracked packet, and the convening message's own admission rule fails. Cure: §2.2.

**M-1 MATERIAL — Item 10 is incomplete in the manifest.** The charge's item 10 reads "This charter pin with the validator receipt, and the PR ledger draft." The manifest carries `ex-pr-ledger-draft.md` and the charter pin, but no validator-receipt exhibit at all. The only assertion of a PASS is the commit subject of `2070efe2`, which is narrative, unpinned, and (per B-1) was produced on a different file set than the one committed. Cure: §2.2 step 3.

**M-2 MATERIAL — Convening procedure validates where assembled, not where judged.** `P/09-convene-script.sh` checks for `CLAUDE.local.md` and launches the judge; it does not run `validate_gate_packet.py` in the judge worktree first. A pre-launch validation there would have caught B-1 before spending a cold seat. Cure: add to the convene script, after the `CLAUDE.local.md` test, the validator invocation with the correct charter sha and `|| exit 4`. (This is a proposed process-rule change; under charter §3.4 it needs its own convening or magistrate adoption. I am naming it, not ratifying it.)

**N-1 NIT — Convening message names code anchors that are not the merge candidate.** The convening message says "verify load-bearing claims against the exhibits, `git show 0fa4e6e3:<path>` or `git show 24ff94cb:<path>`", while the charge's merge candidate is S = `c5cbfd9e` and its code-evidence rule is "`git show <rev>:<path>` at S or at the named revisions." I verified that `0fa4e6e3` is "A291 fix round 2 (K)" (2026-09-24 05:43) and `24ff94cb` is the ownership-forgery harness commit (12:43), both ancestors of the lane but neither the candidate. The template text appears to be carried over from an earlier gate. Harmless here because the charge governs, but on re-convene the message should name `c5cbfd9e` (and the named revisions 3fb98469, d2e751df) so a judge never has to choose.

**N-2 NIT — Item 3, bullet two, cites a narrative source.** "the new test FAILS with the 3fb98469 packer (RecursionError) and PASSES at d2e751df (record 00 item 108)". Record 00 is outside `P/` and is a document the judge must not read. The charge does allow own-execution for items 1–3, so this is curable by the judge's probe, but the packet should either carry the FAIL/PASS transcript as an exhibit or drop the record citation. No effect on this REFUSE.

**N-3 NIT — `ex-01-sha.txt` pins `origin/main` at `e0934a59` while the judge worktree's canonical `main` is at `7c1c9caf`** (from `git worktree list`, read-only). Main has moved again since assembly. The charge already discloses that main moved (docs-only) and that the magistrate re-checked the merge; on re-convene, refresh the `origin/main` line and the "merges cleanly" check to the then-current main, or state the exact main sha the merge check used.

## 4. Items NOT EXECUTED (deliberately, because the trust anchor failed)

- Item 1 (sha and merge-base verification against S): NOT EXECUTED.
- Item 2 (diff verification of `ex-02a`–`ex-02d` against `git show`): NOT EXECUTED.
- Item 3 (re-running the 49 tests and the RecursionError regression in a `git archive c5cbfd9e` copy under /tmp; the `ex-115b` patch-target test): NOT EXECUTED. No `git archive` copy was created.
- Items 4–9 (evidence transfer, F-C/F-B replay, full suite, lenses and dispositions, entry-witness note, R4-2 text): NOT READ, NOT RULED.
- Every merits exhibit other than `00-charge.md`, `ex-01-sha.txt` (read only to identify S and the revisions for N-1/N-3), and `09-convene-script.sh` remains unread by this judge. On re-convene the packet reaches a judge with no memory of this session, which is the intended state.

Everything I did execute is listed in §1 and §2.1 and is read-only: two validator runs, `shasum`, `git ls-tree`, `git status --ignored`, `git log`, `git check-ignore`, `git ls-files`, `git worktree list`, and `git log -1` on nine revisions.

## 5. Gate-ledger row 7 — exact text to carry

```
Row 7 | Cold final pass A291-FINALPASS-01 (Fable 5.1) | REFUSE — packet inadmissible: manifest exhibit ex-03-regate-d2e751df.log ignored by .gitignore:45 and never committed; validator REFUSE exhibit_unreadable in judge worktree at 2070efe2 (charter 099de884…c95d81 and packet f7e6a218…4615e5 both matched). No MERGE/NO-MERGE issued. Re-convene after cure §2.2 of P/20-coldgate-fable-finalpass-ruling.md.
```

## 6. Standing notes for the re-convene

- This REFUSE is not a verdict on PR #409 and must not be recorded or summarized as NO-MERGE, nor as a partial MERGE.
- The refuter's sealed output, if any, was not seen by me; the synthesis must quote both verbatim (charter §5).
- On re-convene, use a fresh cold seat with the corrected packet sha; do not resume this session.

Verdict line: REFUSE — A291-FINALPASS-01 packet inadmissible (ex-03-regate-d2e751df.log gitignored, never committed; validator exhibit_unreadable); no MERGE/NO-MERGE issued; cure §2.2, then re-convene.
