ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: high
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# PRE-MERGE FRESH PASS — round-7 artifact fence, magistrate bench commit c8ea9e95 (detached worktree)

READ-ONLY refuter. DETACHED WORKTREE `/Users/edr/code/JouleWise-wt-dx2` @
c8ea9e95. Write NOTHING inside the worktree except transient mutation probes
that you restore; confirm `git status --porcelain` is EMPTY before writing the
report — non-empty is a protocol failure, say so and stop. Never `git
checkout`, `stash`, `commit`, or canonical `unittest discover`. `runs*/` are
immutable corpora; `docs/paper/draft-v1.md` is byte-frozen; never open either
for writing. Do NOT run the full replay without `--literals-only`.

This is the operation-loop §5 fresh pass over a POST-REVIEW bench commit by the
magistrate (terra 228 delta re-audit on 8efbb200 was CLEAN; read-only at
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/out/228-terra-dx-delta2b.md`).
The delta is `git diff 8efbb200 c8ea9e95` (ONE file,
`tests/test_paper_round7_artifacts.py`, +4/−1): in
`InvocationTests.test_absent_corpus_exits_three_and_names_path` the scratch
directory is now `Path(directory).resolve()`, because the fence prints the
RESOLVED corpus root (`scripts/check_paper_round7_artifacts.py:977-978`) and
the exact last-line assertion failed under macOS's default symlinked TMPDIR
(`/var/folders/...` → `/private/var/folders/...`). The seats never saw it
because every seat exports a scratchpad `TMPDIR` that is already resolved.

## Lenses

A. CONTRACT — is resolving in the TEST the right side of the fix, or should
   the fence print the path as given (`args.corpus_root`) and the test stay
   unresolved? Argue from the fence's contract: the `R7F CORPUS UNAVAILABLE:
   <path>` line names the file the fence tried; the ruling's P3 regression
   (`.../docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md`,
   read-only, on main) — quote what it requires of that line, and say whether
   either side of the fix could violate it. Then census the OTHER tests in
   the module that build paths under `SCRATCH_PARENT` and compare them
   against fence output: list each and state whether the same symlink
   hazard exists (a `str(path)` compared to fence stdout/stderr) and is
   latent.
B. EXECUTION — paste: the four-class test command
   `python3 -m unittest tests.test_paper_round7_artifacts.RegistryAndDigestTests tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests`
   run TWICE — once with the exported scratchpad TMPDIR, once with
   `env -u TMPDIR` (macOS default) — both must be OK; the literals-only fence
   (`R7F PLACED 0/16`, `R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`, EXIT=0);
   the counterfactual (drop `.resolve()` → the test must FAIL under
   `env -u TMPDIR` and PASS under the scratchpad TMPDIR; restore).
C. SAME-SIGNATURE — is "environment-dependent test passes only under the
   seats' TMPDIR" a defect class seen elsewhere in this module or in
   `tests/test_check_gate_ledger.py` (read the latter at
   `/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py`,
   a sibling branch, read-only)? Name any latent instance.

## Report

Severity-tiered findings (BLOCKER / SHOULD-FIX / NIT) with file:line,
counterfactual, observed output. `## Executed evidence` with every command and
exit line. One-line VERDICT: `CLEAN` / `SHOULD-FIX n` / `BLOCKER n`. End with
`git status --porcelain` (must be empty).
