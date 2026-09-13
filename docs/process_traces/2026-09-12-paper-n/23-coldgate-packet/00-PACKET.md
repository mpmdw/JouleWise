# Cold-gate packet 23 — Paper-N: escalation trigger after two fix rounds (2026-09-12 ~14:35 PDT)

Assembled mechanically by the interactive magistrate: the files in this directory are verbatim copies of
the lane's trace records (numbers = their record ids). The article under work is
`docs/paper/draft-v2-skeleton.md` at commit e3285e67 (round-2 head) in the checkout you run in; the
round-1 head was 482a0cc4 and the base origin/main dbe6c675 (`git diff dbe6c675..e3285e67 -- docs/paper/draft-v2-skeleton.md`).

## What happened

1. Three read-only reviews of the merged article (04 pedagogy lens; 06 blind advisor read; a fact lens,
   not included, found no blocker) → the lead wrote fix contract 12 → seat report 13 (round 1, 482a0cc4).
2. Delta re-audits of round 1: 16 (pedagogy: 2 NEW blockers of the term-used-before-built class; "same
   signature: yes") and 17 (fact: no blocker).
3. The lead wrote fix contract 18 with a structural rule (seat must list the USE sites of moved text and
   run its own mechanical first-use pass) → seat report 19 (round 2, e3285e67).
4. Delta re-audit of round 2: 21 (pedagogy: 1 NEW blocker — a deletion removed the only build of "false
   difference" and the floor's purpose clause; 5 should-fix; 6 nits; LATE 0 / NEVER 2 on a whole-main-text
   first-use pass; "same signature over both rounds: yes — a fix applied against the finding list rather
   than against the sites that use the changed text"; the reviewer records the standing escalation trigger
   as met and recommends a lead bench edit of the eleven cures, then land).

## Rule under which you are convened

Standing escalation trigger: two consecutive rounds failing with the same signature is evidence of a
structural problem, and the next spend is a consult, not round three. Mandatory cold-gate trigger: any
second fix round on the same defect; any proposed process rule.

## Questions (rule on each; exact text where you prescribe text)

Q1. Disposition of the eleven open cures in record 21 §4 (1 blocker, 5 should-fix, 6 nits — wait: 5
    nits are listed as six; take the record as written): (a) the lead applies them at the bench (each is
    one sentence or clause at a site already open, no new numeral, no move, no SVG edit), re-runs the paper
    checks, and lands; (b) a third delegated round under a new contract; (c) neither — something
    structural must change first. Choose and say why; if (a), verify each of the eleven cures yourself
    against the draft at e3285e67 and return the exact replacement text for each, corrected where record
    21's wording is wrong or incomplete.
Q2. Is the "false difference" regression (record 21 NB2-1) a real replication-bar failure or a
    reviewer's over-reading? Quote the draft.
Q3. Proposed process clause for future prose fix contracts (the magistrate proposes; you rule ratify /
    amend / reject with text): "Every delete, move or rename item in a prose fix contract must name and
    quote every site that USES the deleted build or the renamed object — in the draft, in pinned figure
    text, and in the ledger/lexicon gloss columns — and the seat's report must show each site defined at
    or before use after the edit." Where should it live (the codex-delegation skill's prompt contract, or
    the paper's first-use ledger doc)?
Q4. Anything in the two rounds that must be REVERTED rather than patched? Say "none" or name it with the
    line.

## Constraints on you

Read only this packet, the draft and its appendix at e3285e67, `docs/paper/protocol/first-use-audit-ledger.md`,
`docs/paper/round7/built-terms-lexicon.md`, and the figure SVG text under `docs/paper/figures/` when a
question needs it. Do not read process docs, decision logs, RUN_STATE, TASK_QUEUE, memory, or git history
beyond the three commits named. Contamination disclosure first: list every file you opened.
