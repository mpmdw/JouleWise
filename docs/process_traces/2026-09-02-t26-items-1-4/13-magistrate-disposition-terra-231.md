# terra 231 (t26-a fresh pass over bench commit f84be217) — magistrate disposition 2026-09-02

VERDICT `SHOULD-FIX 1`. F1 cure mutation-killed three ways (revert hunk / drop `..` clause / drop absolute clause → the named assertions fail); F2 clean; `TASK_QUEUE.md` moved only the two generated A17 renderings; same-signature vs luna 226: no.

| Finding | Class | Disposition |
|---|---|---|
| F3 SHOULD-FIX — `_has_executed_evidence` validates `(root / path).is_file()` (worktree), while ruling §B1 says "exists at HEAD"; an untracked in-repo file satisfies it (probe: accepted `True`, `git cat-file -e HEAD:<probe>` → 128). | test-gap, operator-only shape | **ACCEPTED AS LIMITATION — not fixed.** (1) The test is load-bearing on CI, which runs on a clean checkout where worktree ≡ HEAD; a citation of an untracked file is already refused there, so the gap exists only for a local run by the operator (D-161: operator-only-adversary refusals are over-engineering). (2) A HEAD-tree check adds a `git` subprocess per citation to a docs test and breaks the temp-root selector tests, which mock `ROOT` to a non-git directory. (3) A second fix on the B1 existence predicate (after F1 in f84be217) would be a rule-11 "second fix round on the same defect" cold-gate trigger; the materiality above does not justify convening one. Recorded here and in the PR body (item 3: triaged and dispositioned, not silently applied); listed in the next Ed batch for visibility. |

Executed at the bench this session: none beyond terra's pasted evidence (the finding is accepted as stated, not contested).
