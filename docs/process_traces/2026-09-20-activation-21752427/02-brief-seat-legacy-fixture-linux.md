SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["tests/test_install_night_agent.py"]

# Fix-forward: the legacy render fixture in tests/test_install_night_agent.py names /bin/true, which is an ELF binary on Linux

Cwd is the linked worktree `/Users/edr/code/JouleWise-wt-fixture-linux` on branch `fix/2026-09-20-legacy-fixture-linux` at main `f2427b24`. Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree. Interpreter for the suite: `/Users/edr/code/JouleWise/.venv/bin/python` (3.13). A second interpreter `/opt/homebrew/bin/python3.11` exists for a 3.11 reproduction (stdlib unittest only; if the project's imports need packages that 3.11 lacks, report that and skip the 3.11 run — do not install anything). No git commits or pushes (the lead commits by pathspec), no launchctl, no network, no sudo. Do not end your turn before the report.

## The defect (executed evidence from the hosted run at main `2f4fc128`, PR #369's merge)
Hosted CI job `test (3.11, 3)` on Ubuntu: 12 of 65 `tests.test_install_night_agent` tests fail with one signature: `night wrapper is not valid UTF-8 … 'utf-8' codec can't decode byte 0xf0 in position 24`, raised at `joulewise/night_agent_install.py:1163` (the UTF-8 wrapper refusal added by PR #369). The fixture at `tests/test_install_night_agent.py:103` builds the legacy plan with `chain_path="/bin/true"`. On macOS `/bin/true` does not exist, so the installer takes the legacy branch ("legacy fixtures name a missing stub", the comment above line 1163) and the suite is green locally. On Ubuntu `/bin/true` is an ELF executable; byte 24 is `e_entry` = 0xf0, so the decode fails and the refusal fires. The macOS matrix shards and every other Linux shard were green; ten shards were cancelled by fail-fast. This is a test-fixture defect, not a night-path defect (the real `chain.zsh` is UTF-8 and passed the live render-only step 09-19).

## What to change (tests only)
1. Make the legacy fixture platform-independent: point `chain_path` at a path that exists on NO platform, under the test's own temporary root (for example `str(self.root / "legacy-missing-chain.zsh")`, never created). If several fixtures or helpers share the `/bin/true` literal, fix each the same way (grep the file for `/bin/true`).
2. Add one guard so this cannot regress silently: in the fixture (or a `setUp` assertion) assert that the legacy chain path does not exist on the running platform, with a message naming the 09-20 CI signature. A fixture that accidentally names a real file must fail loudly, not decode-fail twelve tests.
3. Do NOT change `joulewise/night_agent_install.py` or any other production module. If you believe the legacy branch itself should key on `FileNotFoundError` only, say so in the report as a finding; do not implement it (out of scope, separate ruling).

## Verification (paste tails in the report)
- `/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_install_night_agent -q` → all pass (65 tests expected).
- Reproduce the Linux condition on macOS BEFORE your fix: temporarily run the module with the fixture pointed at a real non-UTF-8 binary that exists here (for example `/usr/bin/true`, which is a Mach-O binary) and confirm the same `night wrapper is not valid UTF-8` signature appears; then restore. Report the exact command and the failure count you saw. (This proves the fix kills the defect rather than passing by platform accident.)
- If the 3.11 interpreter can import the project: `/opt/homebrew/bin/python3.11 -m unittest tests.test_install_night_agent -q` tail as well.
- `git diff --stat`.

## Report
claude-codex-report/v1 envelope for --genre implementation; `pathspec` = ["tests/test_install_night_agent.py"]; findings for anything out of scope; JSON header under 800 bytes; total envelope under 8 KB.
