SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Refuter (execution lens, read-only): CI-LEGACY-FIXTURE-LINUX-01 — commit d5f35ca1 on fix/2026-09-20-legacy-fixture-linux

Cwd is the linked worktree `/Users/edr/code/JouleWise-wt-fixture-linux` at `d5f35ca1` (one commit over main `f2427b24`). Read-only inside the repository (WRITE_SCOPE empty); scratch under /tmp only. Never touch `/Users/edr/code/JouleWise` or other worktrees. Interpreters: `/Users/edr/code/JouleWise/.venv/bin/python` (3.13) and `/opt/homebrew/bin/python3.11`. No network, no launchctl. Do not end your turn before the report.

## The change under refutation
`git show d5f35ca1` — 8 lines in `tests/test_install_night_agent.py`: the legacy plan fixture's `chain_path` moves from `/bin/true` (absent on macOS; an ELF binary on Ubuntu whose byte 24 = 0xf0 tripped the PR #369 UTF-8 wrapper refusal at `joulewise/night_agent_install.py:1163`, 12/65 failures on hosted `test (3.11, 3)` at `2f4fc128`) to `self.root / "legacy-missing-chain.zsh"`, never created, with an `assertFalse(exists)` guard naming the signature. Seat 02's report (`/tmp/magistrate-21752427/02-seat-legacy-fixture-linux-astra.md`) claims: pre-fix reproduction with `/usr/bin/true` on macOS → exactly 12 failures with the UTF-8 signature; post-fix 65/65 on 3.13 and 3.11; guard fires on an existing non-UTF-8 path. The lead re-ran the module on both interpreters (65 OK each).

## Refute (execution lens; every claim executed, not read)
1. Reproduce the counterfactual yourself: with the fixture pointed at a real non-UTF-8 binary (`/usr/bin/true`), how many failures and which signature? (Edit in a /tmp copy of the worktree or use `git stash`-free means: copy the test file to /tmp, patch, run with `-m unittest` from a /tmp checkout `git worktree`-free copy — e.g. `cp -R` the repo to /tmp and run there.) Then confirm 65/65 at `d5f35ca1`.
2. Does the guard actually protect? Create `legacy-missing-chain.zsh` inside a fixture root before `_write_plan` and show the assertion fires (paste the message). Does `self.root` differ per test (TemporaryDirectory in setUp)? Could any test create that exact path legitimately?
3. Is `legacy-missing-chain.zsh` reachable by the installer on Linux in a way that differs from macOS (path length, /tmp vs /private/tmp symlink, `Path.exists` on dangling symlinks)? Any platform where a never-created path under a fresh TemporaryDirectory could exist?
4. Are there OTHER platform-dependent fixture paths in the same module or its siblings (grep `/bin/`, `/usr/bin/` in tests/ for plan fixtures) that would trip the same refusal on Linux? Name them with line numbers (report only; out of scope).
5. Run the module's neighbours that share the fixture helpers, if any (`grep -l "_write_plan\|InstallNightAgentTests" tests/`), on 3.13.
6. Same-signature statement: is the defect class (fixture names a platform-existing file) fully closed by this change, or does another instance survive?

## Report
claude-codex-report/v1 envelope for --genre review; findings tiered blocker / should_fix / nit with executed evidence; JSON header under 800 bytes; total under 8 KB.
