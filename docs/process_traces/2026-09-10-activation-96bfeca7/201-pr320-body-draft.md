## What this does

Ed's ruling of 2026-09-10 (directive issue 316) says that if the equivalence night lands inside the envelope already in force, the calibration acceptance is *continued* onto the new operating-system build rather than derived again, and that any code the continuation needs lands as the smallest change through the normal gate. This PR is that change. Nothing in it issues or continues anything by itself: the registry it adds is empty, and the artifact it can prepare is a marked candidate that a later governed transaction would have to pin.

- **A separate, byte-pinned continuation artifact.** A continuation is a small JSON record that names the acceptance it extends (by id, file digest and derivation digest), the new identity epoch, the rule with its constants, and the night's evidence: every declared slot with its ledger attempt id, content id, the two artifact digests, disposition, anchor-resolution outcome and bound. It carries its own derivation digest and is authenticated only through a registry pin, exactly as the acceptance artifacts are. The acceptance in force stays byte-identical, so nothing that pins its digests moves.
- **One loader notion: the epochs an acceptance judges.** The acceptance's own epoch plus every authenticated continuation's. The bracket evaluator uses it at four places: freshness (a machine on a continued epoch is fresh, and the record says which continuation made it so); corpus doubling counted per judged epoch, never pooled; range expansion, where only the adjudicated night's rows are exempt (they were judged against the envelope already); systematic failure, where every row keeps its trigger. A night that contained a systematic failure cannot be prepared as a continuation at all.
- **The envelope must hold over every disclosed valid bound, resolved or not.** The loader cannot replay anchor resolution from bytes, so it does not let an asserted "unresolved" label remove a failing bound from the comparison: anchor resolution can lower the retained count, possibly to INCONCLUSIVE, but never turn a FAIL into a PASS. The ledger cross-check also asserts the converse of what the file claims: the file's finalized rows must equal the session's, so no row can be hidden.
- **Capture writer routed through the same notion.** An ordinary capture on a continued epoch passes preflight and records which epochs the acceptance judges and on what basis; derivation-only capture refuses a judged epoch with the existing refusal code; the desk-inputs writer treats a continued epoch as an ordinary night.
- **The preparation tool** re-derives the verdict from primary bytes through the issuer's own helpers and treats the desk check's record only as a witness to disagree with. It refuses to write anything for a FAIL, an INCONCLUSIVE, a night with a systematic failure, or a night whose unresolved rows fall outside the envelope.
- **Contracts** for the continuation artifact and the capture artifacts' new preflight block, with drift tests that read the documents.

## What it cannot do

No continuation exists after this PR: the registry has no entries, and preparing a candidate requires a terminal derivation night on the new epoch. Issuing one is a separate governed transaction with its own D-102 addendum. The acceptance artifacts and their digests are unchanged.

## Gate ledger (D-118 / D-121)

| # | Gate item | Evidence |
| --- | --- | --- |
| 1 | Independent audit by a fresh non-author reviewer | RUN e2d28c311e197d9a10de162e109d15fa26af61b0 |
| 2 | Paired distinct lenses: contract + execution (physics if measurement-adjacent) | RUN 1d6775f38794784316e084730b9410e5abf39e12 |
| 3 | Lead-written FIX contract with dictated closure shapes; findings triaged and dispositioned, never silently applied | RUN 57a94c187d8bf1a4952f410d7b8f716acf0397d0 |
| 4 | Delta re-audit of every fix round | RUN 47d7761c914eef1099d35eb7af5b2d7db048bad3 |
| 5 | Same-signature statement from every delta; a surviving class escalates to a consult, not round three | RUN 57a94c187d8bf1a4952f410d7b8f716acf0397d0 |
| 6 | Opus counter-review on the near-final head | RUN 46f54a57ca184af61dd5e6331ff486cdb84198d4 |
| 7 | Apex Fable code-reading diff gate answering design-level questions; never skipped or downgraded | RUN a7c9993d4befc7ba1a355c699577976d536ad380 |
| 8 | Overbuild / merge-ability prune | RUN a7c9993d4befc7ba1a355c699577976d536ad380 |
| 9 | Lead unpiped full-suite replay on the integration tree (not the stale branch), exact tail recorded | RUN PENDING |
| 10 | Final-head fresh-eyes review after every post-review commit | RUN PENDING |
| 11 | CI green on final head + post-merge cross-unit integration review | RUN 4c04f53e7f476d8fa60a2306940c2311875fd98f |
| 12 | Magistrate terminal review, full session context, of the exact merge candidate (final head sha); not delegable | RUN 4c04f53e7f476d8fa60a2306940c2311875fd98f |

Rows 1 and 2: refuter 170 (Opus, contract + execution, round 1) and refuter 174 (Opus, round 2) with counter-review 193; rows 3 to 5: the lead's fix contracts and triage in records 171, 182, 185, 188, 197 and the deltas 179, 187, 191, 192 (same-signature statements in each; the doc-asserted-contract class escalated to a mechanism lane rather than a further round); row 6: counter-review 193 on cfeba22f and its fix round 8; row 7: the magistrate's reading in record 194; row 8: no overbuild taken (record 194). Row 9: replay 18 at this exact head (record pending). Row 10: fresh-eyes 196 on 2e798f87 and 199 on this exact head. Row 12: terminal review on this exact head.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
