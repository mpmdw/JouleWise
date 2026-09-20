# Record 08 — magistrate diff gate, replay, and terminal review: CI-LEGACY-FIXTURE-LINUX-01 (`fix/2026-09-20-legacy-fixture-linux`)

## §1 Diff gate (rows 7 and 8; the magistrate read every hunk, 03:58 PDT 09-20)

Head `d5f35ca1` = one commit over main `f2427b24`; `git diff --stat` = `tests/test_install_night_agent.py | 8 +++++++-`. No production module changes.

Design-level questions answered from the diff and `joulewise/night_agent_install.py:1150-1170`:
1. **Does the fixture still exercise the intended production branch?** Yes: the legacy branch keys on the chain file being unreadable (the `OSError` caught above line 1155 yields `chain_bytes = b""`), and a never-created path under the test's `TemporaryDirectory` is unreadable on every platform; the UTF-8 refusal at :1163 is reached only when the file exists and is not UTF-8, which is exactly what `/bin/true` did on Ubuntu.
2. **Is the guard correctly placed?** `assertFalse(legacy_chain.exists(), …)` sits in `_write_plan` before the plan is built, so every test that builds a legacy plan gets one loud message naming the 09-20 signature instead of twelve UTF-8 decode failures. `self.root` is a fresh temporary directory per test (`setUp`), so no test can pre-create the path unless it does so deliberately.
3. **Overbuild / prune:** nothing to prune — eight lines, one fixture literal and one guard. The seat's residual-risk suggestion (narrow the production fallback from `OSError` to `FileNotFoundError`) is a production change with its own blast radius; it is NOT taken here and is registered as a finding for a separate ruling (§4).
4. **Pre-existing smell noted, out of scope:** `chain_sha256_path="/tmp/install-night-agent-test.sha256"` is a fixed absolute path (unchanged by this PR); it could exist on a shared runner. Registered in §4 for the counter-review to weigh.

Verdict of the diff gate: MERGE-able pending refuter 06 (execution lens) and counter-review 07 (contract lens).

## §2 Replay (row 9; lead, unpiped tails, in the branch worktree at `d5f35ca1`)

```
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_install_night_agent -q
Ran 65 tests in 93.453s
OK
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.11 -B -m unittest tests.test_install_night_agent -q
Ran 65 tests in 66.349s
OK
```
The delta is confined to this one module, so the module alone on both interpreters is the replay; the seat's pre-fix counterfactual (fixture pointed at `/usr/bin/true`, a Mach-O binary: exit 1, exactly 12 failures with the UTF-8 signature, then restored byte-for-byte) is the executed proof that the change kills the defect rather than passing by platform accident. The hosted matrix (all Linux shards) is the final platform proof and runs on the PR head.

## §3 Fix contract and same-signature statement (rows 3 and 5)

Fix contract = brief 02 (`02-brief-seat-legacy-fixture-linux.md`): dictated closure shape = fixture path absent on every platform + loud guard; no production edits. Seat 02 implemented exactly that shape in one round; no fix round was needed, so there is no delta to re-audit beyond the refuters' pass on the same head. Same-signature statement: the defect class "fixture names a platform-existing file" has one instance in this module (`/bin/true`); refuter 06 is asked to sweep `tests/` for others.

## §4 Findings carried, not fixed here
- F-a (seat 02 residual risk): production legacy fallback catches all `OSError`; narrowing to `FileNotFoundError` needs a ruling — successor lane candidate.
- F-b (diff gate): fixed `/tmp/install-night-agent-test.sha256` in the same fixture — same class, latent; counter-review 07 R3 weighs it.

## §3a Bench decision on the second `/bin/true` fixture (Opus 07 nit 2; refuter 06 item 4)
`tests/test_magistrate_watchdog_cli.py:198` sets `chain_path="/bin/true"` but that module never reaches the installer's UTF-8 reader: refuter 06 substituted `/usr/bin/true` (a Mach-O binary) at runtime and all three affected tests still passed. It is a latent instance of the class, not a failing one; it is registered for the successor fixture lane (with Opus nit 1, the fixed `/tmp` sidecar path) rather than widened into this PR. The PR stays at one file.

## §5 Terminal review (row 12), 04:40 PDT 09-20
Refuter 06 (Astra high, execution lens, record 06): CLEAN — counterfactual reproduced (12 failures with the UTF-8 signature), fix 65/65 on 3.13 and 3.11, guard fires on an existing non-UTF-8 file / directory / symlink-to-binary, 256 fresh temporary roots without sentinel collision, dangling-symlink edge analysed; its neighbouring-module failures are the sandbox's `pgrep` refusal (`Cannot get process list`) and the 8 s supervision watchdog under sandbox load, both reproduced by it with the PRE-fix helper, i.e. not this change (the lead ran `BindSupervisionProcessTests` alone at the bench: 22 OK). Opus 07 (contract lens): MERGE, three nits dispositioned above. No fix round was needed, so the delta re-audit (row 4) is the two refuters' pass over the only head; rows 10 and 11 are satisfied by the same head plus the hosted checks on the PR (recorded in §6 before merge).
Verdict: MERGE the records-only candidate (merge of main onto `d5f35ca1`); the hosted matrix on the PR head is the Linux proof and gates the merge.

## §6 Hosted checks on the PR head (row 11)
(filled before merge)
