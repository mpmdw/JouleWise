ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: []
GENRE: review
EFFORT: high
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FINAL-HEAD FRESH PASS (operation-loop §5, post-cold-gate commit) — dx lane, detached worktree `/Users/edr/code/JouleWise-wt-dx2` @ 3efa807e

Read-only: WRITE_SCOPE is empty — no file edits, no git state changes, no
codex/claude launches, never canonical `unittest discover`.

The commit under review is `git diff 4c88b941..3efa807e`: ONE code file
touched (`scripts/check_paper_round7_artifacts.py`, module docstring only —
paragraphs 2–3) plus custody files under
`docs/process_traces/2026-09-02-coldgate-r7f-unavailable/` (two sealed seat
reports and `MAGISTRATE-RULING-r7f-unavailable.md`). Read the ruling first.

Questions, each with executed evidence:
1. Docstring truth, sentence by sentence, against the code at this head: for
   EACH sentence of paragraphs 2–3, name the code site that makes it true, or
   a concrete input that makes it false. The ruling claims the `<detail>`
   enumeration is derived from a closed census of `ArtifactsUnavailable` raise
   sites — replay `grep -n ArtifactsUnavailable scripts/check_paper_round7_artifacts.py`
   and confirm or refute closure (anything else that can reach the `:1011`
   handler?).
2. Is the diff docstring-only? `git diff 4c88b941..3efa807e -- scripts tests | grep -c '^[+-]' ` vs the docstring span; confirm no executable line changed (`python3 -c` compile both revisions and compare `co_code`-level or simply confirm no non-docstring hunk).
3. Full module: `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_round7_artifacts` (this linked worktree has no retained corpus; the env var points the replay class at main's; ~8 min). Paste the tail. Also `python3 scripts/check_paper_round7_artifacts.py --literals-only | tail -1` and `python3 scripts/check_paper_round7_artifacts.py --corpus-root /Users/edr/code/JouleWise | tail -2`.
4. Ruling hygiene: does every command under `## Executed evidence` in the ruling replay as written (run at least the grep, sed, and --help ones)? Do the two custodied seat files' sha256 match the "committed sha256" values the ruling states?
5. Any NEW defect in the diff (a sentence in the new docstring that is false; a claim in the ruling its evidence does not support).

Report: claude-codex-report/v1 envelope — the JSON header MUST be under 8192 bytes (the wrapper rejects larger envelopes as malformed; a previous seat failed exactly this way by placing its sentence-by-sentence audit inside the JSON). Keep `verdict` to `{"counts": {...}, "findings": [...]}` and put the sentence audit, census, custody hashes, and all evidence in the markdown BODY below the envelope, not in the JSON. Then `VERDICT: CLEAN` or `VERDICT:
SHOULD-FIX n` with `file:line` per finding and a concrete falsifying input for
any docstring finding, `## Executed evidence` (replayable, no shell variables
inside heredocs). Do not end the turn before every question is answered.
