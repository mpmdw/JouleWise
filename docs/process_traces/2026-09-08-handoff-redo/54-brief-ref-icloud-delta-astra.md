WRITE_SCOPE: []

# DELTA RE-AUDIT — fix round 1 on ICLOUD-BACKUP-PROBE-01 (gpt-6-astra, read-only)

HEAD = fix-round commit; HEAD~1 = c3488fb8 (reviewed landing); HEAD~3 = main a969e526. Packet: `git diff HEAD~1
HEAD` (8 files, +118/−17). Seat claims: C1 pins re-recorded with the immediately preceding digest and correct
commit/PR attribution plus older lineage (final XS fc8f1728…, AS 3844a8f1…); C2/C3 override + per-root cumulative
budget + slow-root skip documented in the three USAGE blocks and three docs by dated addenda; C4 any worker exception
→ zero candidates (`reason=worker_error`); C5 sha256 identity test across the three helper blocks; C7 import order;
golden replay XD/F4/AQ byte-identical; acceptance rc 0.

Break it: (1) recompute `shasum -a 256` of the two scripts at HEAD and compare to the pin lines; confirm the
"supersedes" digests equal the digests at HEAD~1 (`git show HEAD~1:docs/paper/results-fill-registry.md | sed -n
'778,781p'`) and that the named commits (173fe07e #285, b36d1e85 #272) actually contain those superseded bytes
(`git show <commit>:scripts/<file> | shasum -a 256`); (2) the registry parser: run whatever test parses the
registry (`tests/test_paper_round7_artifacts.py` registry tests) and confirm the new pin lines parse; (3) helper
identity: extract the three helper blocks yourself and compare; run the new identity test; mutate one copy in a
$TMPDIR clone and confirm it fails; (4) C4: inject a non-OSError exception into the worker and confirm zero
candidates + the stderr reason, and that a partial result (worker appended then raised) is rejected; (5) docs: the
three doc addenda must be APPENDED (git diff shows only additions in those files) and must state the default
path, the override syntax, the 2 s cumulative per-root budget, and the fail-closed pin check; (6) complete golden
replay with `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise` — byte-identity yourself; (7) anything HEAD~1 had right that
HEAD broke. Never touch the real iCloud path; run only the three modules (`tests.test_paper_excursion_decomposition
tests.test_paper_replay_fence tests.test_paper_round7_artifacts`). Report (genre review): `verdict` = {counts,
findings} ONLY; header < 8192 bytes; findings with file:line, severity, exact demonstrating command.
