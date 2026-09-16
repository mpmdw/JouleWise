# Delta re-audit brief — fix round 4 of the transactional installer (`0ba6ce54`), fresh seat

SESSION_MODE: delegated
WRITE_SCOPE: []
BASE_HEAD: 0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa
BASELINE_MANIFEST: .codex-bridge/baselines/mag-delta4b-20260915-2015.json
BASELINE_DIGEST: sha256:1d057a3f5c5d48a9e41e063cfd94fe1ef98793d875e126f30342a375137dc718
LEASE_ID: lease-9632711df15d493fa0a327f4eba59337

Worktree `/Users/edr/code/JouleWise-wt-delta4-txn` (detached at `0ba6ce54`, the final head of `feat/2026-09-15-install-windows-transactional`). You may NOT edit this worktree (WRITE_SCOPE is empty; the lease exists only so the sandbox admits you); do every mutation in `cp -R /Users/edr/code/JouleWise-wt-delta4-txn /private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta4-copy`. Never touch `/Users/edr/code/JouleWise`, other worktrees, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`; never run a real `launchctl bootstrap`/`bootout`. Single modules: `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install` etc.

## Under review
`git diff d626bf64..0ba6ce54` (fix round 4: two oracle defects found by the Opus execution lens — S2: six cells asserted nothing when SIGINT was inherited as SIG_IGN from a background shell; S1: an uncovered cell "commit gate refuses from VERIFIED × teardown query LOADED/UNKNOWN" where a mutant at `joulewise/night_agent_install.py:394` turning exit 4 into exit 1 survived; N3: a dangling option value must exit 2 not 1 — `scripts/install_night_agent.sh` argv guards). Context: `docs/process_traces/2026-09-15-activation-d6888966/lt-28-opus-execution-lens.md` and `lt-29-*` on the lieutenant's branch are NOT in this checkout; the facts above are the brief.

## Execute
1. Isolated reversions in the /tmp copy: (a) revert the S2 oracle change → the six cells must FAIL under `SIGINT` ignored (run the module with `( … ) &`-style inheritance: `python3 -c 'import signal,subprocess; signal.signal(signal.SIGINT, signal.SIG_IGN); subprocess.run([...])'`) and PASS in the foreground; (b) revert the S1 cell → the `:394` mutant (exit 4 → exit 1 in the RETAINED branch of `_teardown`) must SURVIVE; with the cell present it must be RED; (c) revert the shell guards → `--plan` with no value must exit 1 instead of 2. Paste tails.
2. Same-signature question, answered ONLY by executing the two predicates at `0ba6ce54`: class 1 = installer exits 0 with a label loaded while a clock read taken after the LAST LAUNCHD MUTATION is at or past `min(selected_span_close, install_close_epoch)`; class 2 = any path ends with a label loaded and its plist absent, or exits 0 while a label it attempted to bootout is still loaded. Use the three-valued fake launchctl in `tests/test_night_agent_install.py`. Report `class_1: YES/NO`, `class_2: YES/NO` with the executed cases.
3. Run `tests.test_night_agent_install`, `tests.test_install_night_agent`, `tests.test_run_night` in the foreground AND under inherited SIG_IGN; paste both tails.
4. Census: any leaked process or `/tmp` entry from the module runs.

## Report
claude-codex-report/v1 envelope (genre `review`, under 8192 bytes): verdict CLEAN / FINDINGS with severity; reversion tails; the two predicate answers; anything not verifiable.
