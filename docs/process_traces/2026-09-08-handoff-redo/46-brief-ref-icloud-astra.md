WRITE_SCOPE: []

# Refuter brief — ICLOUD-BACKUP-PROBE-01 landing, EXECUTION lens (gpt-6-astra, read-only)

HEAD of this detached worktree = two commits on main a969e526. Packet: `git diff HEAD~2 HEAD` (scripts/
paper_excursion_decomposition.py, scripts/paper_anchor_correction_quantified.py, scripts/check_paper_replay_fence.py,
tests/test_paper_round7_artifacts.py, tests/test_paper_excursion_decomposition.py, tests/test_paper_replay_fence.py,
docs/paper/results-fill-registry.md). Claims: each of the three scripts discovers backup roots through a
verbatim-identical helper with a 2 s daemon-thread budget per root; `JOULEWISE_BACKUP_ROOTS` (os.pathsep list;
empty string = no roots) overrides the default iCloud path; an unavailable root contributes ZERO candidates exactly
like an absent root; every consuming test sets the override to a scratch dir; the XS and AS producer source pins in
results-fill-registry.md are updated with a dated note and nothing else in that file changed; the complete
retained-corpus golden replay reproduces XD (33,765 B), F4 (10,568 B) and AQ (54,280 B) byte-identically.

Break it: (1) BLOCKING probe: make `os.path.isdir`/`Path.is_dir`/`os.listdir`/`Path.glob` on the backup root block
(mock with a 10 s sleep, or point the override at a FIFO-backed path) and time each script's discovery: it must
return within ~2 s with the unavailable outcome; (2) helper identity: diff the three helper copies byte-for-byte;
any divergence is a finding; (3) semantics: with the override pointing at a scratch root containing a planted
candidate file, does each script FIND it (same globs as before, same ordering; AS sorted per capture ID)? With the
root absent vs. blocked, are outputs byte-identical? (4) daemon-thread residue: after a timeout does the process
exit promptly (no non-daemon thread keeps it alive)? (5) golden replay: run the complete
tests/test_paper_round7_artifacts.py with `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise` and confirm byte identity
yourself; (6) results-fill-registry.md: `git diff HEAD~2 HEAD -- docs/paper/results-fill-registry.md` must show
only the two pin lines changed; compute sha256 of the two scripts at HEAD and confirm they equal the new pins;
(7) mutation: revert the daemon budget in a $TMPDIR copy and confirm the blocking regression fails. Do NOT touch the
real iCloud path. Run only the touched test modules. Report (genre review): `verdict` = {counts, findings} ONLY;
header < 8192 bytes; findings with file:line, severity, exact demonstrating command.
