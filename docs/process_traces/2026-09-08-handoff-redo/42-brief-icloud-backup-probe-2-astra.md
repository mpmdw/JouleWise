WRITE_SCOPE: ["scripts/paper_anchor_correction_quantified.py","scripts/check_paper_replay_fence.py","scripts/paper_excursion_decomposition.py","tests/test_paper_round7_artifacts.py","tests/test_paper_excursion_decomposition.py","tests/test_paper_anchor_correction_quantified.py","tests/test_check_paper_replay_fence.py","docs/paper/results-fill-registry.md"]

# Seat brief — ICLOUD-BACKUP-PROBE-01 part 2: the SAME unbounded iCloud probe in the anchor producer (and the replay-fence checker) (gpt-6-astra, medium)

HEAD of this worktree = part 1 (committed): `scripts/paper_excursion_decomposition.py` now discovers backup roots
through a 2 s daemon-thread budget and honours `JOULEWISE_BACKUP_ROOTS` (os.pathsep list; empty = no roots);
seven regressions; the XS producer pin in `docs/paper/results-fill-registry.md` updated with a dated note. Part 1's
combined retained-corpus golden replay (in `tests/test_paper_round7_artifacts.py`) was interrupted because it also
runs `scripts/paper_anchor_correction_quantified.py`, whose backup probe ignores the override and can block forever
on the iCloud path `/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup` (zero-CPU hang seen
twice today). `scripts/check_paper_replay_fence.py` mirrors the same BACKUP_ROOTS.

Do: (1) factor ONE shared bounded-discovery helper (same 2 s budget, same override, same "unavailable = zero
candidates, exactly like an absent root" semantics) and use it from all three scripts — if the paper producers must
stay standalone single-file scripts (check the reviewed-producer conventions in results-fill-registry.md and the
round7 docs before deciding), duplicate the helper verbatim instead and say why; (2) update the AS (anchor producer)
source pin and any other affected producer pin in results-fill-registry.md with the same dated note style as part 1;
(3) every test that imports or runs any of the three scripts sets the override to a scratch dir; (4) run the
COMPLETE combined retained-corpus golden replay in tests/test_paper_round7_artifacts.py (never skip it) and report
byte-equality of every retained artifact (XD, F4, AQ, and whatever the anchor producer emits) against HEAD; (5)
acceptance = the touched test modules to a log with rc. Do NOT touch the iCloud path; do NOT run the
repository-wide suite; no `git commit`; header < 8192 bytes; genre implementation verdict keys; body = per-script
cure, counterfactuals, fail-before/pass-after tails, golden byte-equality result.
