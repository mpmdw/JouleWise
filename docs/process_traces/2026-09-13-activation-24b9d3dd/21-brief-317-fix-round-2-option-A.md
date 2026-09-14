# FIX contract — PR #317 CI-TRIM-01, fix round 2: install cold-gate ruling 17/10 option A (Astra high, enforced scope)

SESSION_MODE: delegated
WRITE_SCOPE: [".github/workflows/ci.yml", "scripts/test_timings.json"]

You are in the linked worktree of branch `chore/2026-09-10-ci-trim` (HEAD `8819cb5f`). Do NOT commit (the lead commits by pathspec). Do not touch `/Users/edr/code/JouleWise` (read-only use of its `.venv/bin/python3` for PyYAML is allowed), any `/Users/edr/JouleWise-measurement-*` directory, or `/Users/edr/night-custody`. No network. Precedence: this contract over the PR body over any other doc; flag conflicts.

Authority: cold-gate ruling `/Users/edr/code/JouleWise-wt-bk-24b9d3dd/docs/process_traces/2026-09-13-activation-24b9d3dd/17-coldgate-packet-ci-trim-t2/10-coldgate-fable-ruling.md` (read-only), Q1 and Q2(c). Option A: NO path-based skipping of the test matrix. Apply EXACTLY the ruling's edits to `.github/workflows/ci.yml` (line numbers refer to the file at HEAD `8819cb5f`; verify each before deleting):

FIX-A1. Delete lines 15–91: the four-line comment starting "Docs-only paths are selected by classify_path" plus the whole `changes:` job (19–90) and its trailing blank line.
FIX-A2. Delete lines 125–194: the three-line "FENCE for documentation-asserting tests" comment plus the whole `docs-readers:` job (128–193) and its trailing blank line.
FIX-A3. Delete lines 196–197 (`needs: changes` / `if: ${{ !cancelled() && needs.changes.outputs.code != 'false' }}`) under `test:`; lines 286–287 under `calibration-exits-exclusive:`; lines 322–323 under `calibration-writer-crash-matrix-exclusive:`.
FIX-A4. Replace comment lines 8–9 with exactly one line: `# Pushes get a per-run group so nothing can evict a queued run; PRs share a ref group and cancel superseded runs.`
KEEP unchanged: lines 10–12 (`concurrency` block); the `fences` job and its comment (92–123); the bodies of `test`, both exclusive jobs, `build`, `installed-wheel`; the zsh guard steps; `pr-fast` remains absent. Do not touch `scripts/shard_tests.py`.
FIX-A5. `scripts/test_timings.json`: delete the top-level `pr_fast_tier` key (lines 6–13 at HEAD) and nothing else; the file must remain valid JSON with its other keys byte-identical (show `git diff` and a `python3 -c "import json; json.load(open('scripts/test_timings.json'))"` rc 0). Confirm with `rg -n pr_fast_tier` that only trace records under `docs/process_traces/` still name it.

Verification to run and paste: (1) YAML parse with the venv interpreter listing every job id, `needs` and `if` (expected: `fences`, `test`, `calibration-exits-exclusive`, `calibration-writer-crash-matrix-exclusive`, `build`, `installed-wheel`; no `changes`, no `docs-readers`; `needs` only on `installed-wheel`; no `if:` on any job); (2) `bash -n` on every `run:` block; (3) `git diff --stat` and `git status --short` (only the two scoped files modified); (4) `git diff a4bb8838..HEAD --stat -- .github/workflows/ci.yml` plus your working-tree diff, so the lead can see the PR's net change against its base; (5) `python3 -m unittest tests.test_check_gate_ledger` tail (the one test module that mentions pr-fast in a comment).

Report (claude-codex-report/v1, genre implementation) as your FINAL MESSAGE: what changed per FIX id with line evidence, pasted verification, deviations, and "what the lead should double-check". Under 8000 bytes.
