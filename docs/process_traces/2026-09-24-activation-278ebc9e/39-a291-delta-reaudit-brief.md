ROLE: DELTA RE-AUDITOR (Astra 6, cross-family) for JouleWise lane A291 fix round 2. Read-only review with executed probes. Do not call Claude or any other agent.

WRITE_SCOPE: []

OBJECT: integration head `0fa4e6e3` = seat P's packer commit `58e2a0bf` plus seat K's checker, generator, fuzz and stress commits (cherry-picked), on top of `20cd29de`. Your worktree /Users/edr/code/wt-278ebc9e-a291audit is a detached checkout of `0fa4e6e3`. Scratch only under /tmp/278ebc9e/a291audit/. Fences: never launchctl, sudo, networksetup, powermetrics; never touch /Users/edr/night-custody, /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents, /Users/edr/code/JouleWise.
The binding spec is Final texts v4: /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/14-a291-final-texts-v4.md (items refer to "ex-10" = /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-7370d0fb/07-coldgate-packet-a291-fix2/10-coldgate-fable-ruling.md; contract 02d in the same directory as ex-02d-contract-v4.md). The seat reports are /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/15b-a291-seatP-report.md and 16b-a291-seatK-report.md. The bench already ran the five scored modules at `0fa4e6e3`: 71 tests OK; fuzz census {inv_02 808, inv_03 99, inv_11 447, inv_12 41, inv_38 372, inv_39 8, inv_52 23}.

CHECK (execute; paste tails):
 A1. Every Final text v4 item addressed to P or K: implemented as written? One line each: file:line and verdict.
 A2. R1, R2, R2b, R3, R4a–R4d, R4d-facts, R5a, R5b: each GREEN at `0fa4e6e3` and RED at `20cd29de` (run the test file against a `git archive 20cd29de` copy with only the test file swapped in).
 A3. The similarity screen of text 8, EXACTLY as specified (canonicalise with ast.parse + ast.unparse, normalisation, pairwise pairs, the P1/P2 positive controls pinned to 20cd29de, the helper extension H with its reachability set, control bound 0.28, threshold 0.30). Paste the script you ran and every number. PASS/FAIL.
 A4. The COUNCIL-407-01 scope predicate: confirm no change touches FT-6, FT-7, FT-9, FT-10, the registration-key set, role identities or the cell structure of contract v4 (compare the registration/roster schemas and keys at 20cd29de vs 0fa4e6e3).
 A5. Same-signature statement: do any of the three defect classes this round exists to cure (a forged roster with two live placements accepted by the seal; a trusted-output cache letting a re-finalized roster skip replay; a derived value built from two different parent populations) survive, in any form, anywhere in the packer or checker? Hunt one more call site for each class. Also: are the fuzz's 23 inv_52 refusals "malformed roster" or "internal:*" (the latter must be zero; property (f))?
 A6. P's flag F2 (quadratic requeue replay, 2.8 s at 131 events): confirm the numbers and state the largest registration the current contract permits.
Severity BLOCKER / should_fix / nit, with the executed witness and a cure.
OUTPUT: final message = findings table; A1–A6 verdicts; probe commands with tails.
