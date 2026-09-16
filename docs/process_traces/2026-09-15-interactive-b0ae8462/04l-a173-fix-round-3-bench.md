# 04l — A173 fix round 3 at the bench (magistrate b0ae8462, 2026-09-15 22:35 PDT)

Fresh-eyes 04k: LANDABLE with two bench amendments. S1: the round-2 `_own_root` branch "unreadable AND a discovery
hit" is unreachable in production (Darwin `pgrep` never lists the caller's own ancestors), and two tests pinned that
impossible shape. Amendment applied: an unreadable own-chain ancestor anchors descendant scanning WITHOUT requiring a
hit (readable agent root preferred, outermost of either kind wins; an over-broad root is safe because only
non-workload descendants are ever exempted and every workload family still blocks). Both tests retargeted to
realistic hit sets (no own-ancestor hits). N1: the tautological `assertLess(events.index(events[0]), …)` deleted.
Executed: `tests.test_arm_census` 20 OK, `tests.test_run_night` 104 OK; reverting the fallback in a copy →
`FAILED (failures=3)` (the retargeted cells bite). Commit on the branch: see `git log feat/2026-09-15-arm-census-idle`.
Live run by the reviewer (04k §5): this interactive session classified idle and exempt; the block came from the foreign
seats only — Ed's use case works.
