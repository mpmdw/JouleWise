# Off-host verification

Source checks finished **2026-11-16 18:17:57 PST** (`date` in runner).
Source worktree `/tmp/jw-r1-ready-1116-source`, detached at
`b2e01464d6d4fbf2901ff4d4154df9455104a12a`; Python 3.13. Synthetic only.
No measurement Mac connection, native capture, measurement-data read,
notice, installation or READY declaration.

Reproduce on a separate off-host source worktree containing P:

```sh
zsh run_source_checks.sh /absolute/source/worktree /absolute/new/log-directory
R1_SOURCE_ROOT=/absolute/source/worktree python3.13 -B tests/test_preparation.py
zsh -n stage_mbp_r1.sh
zsh -n run_source_checks.sh
```

Run the commands above from this package. The wrapper sets private TMPDIR,
`PYTHONPATH=SOURCE:SOURCE/tests`, `JW_B5_SYNTHETIC_ONLY=1`, no bytecode.
The explicit source worktree prevents the audit branch's older/missing R1
files from being mistaken for P. It verifies source hashes before tests.

| Module / check | Result | Retained evidence |
|---|---|---|
| `test_rl145_gate_hashes` | 1 OK | `tests/logs/tests.align.test_rl145_gate_hashes.log` |
| `test_w1_rl122_kit` | 14 OK | pair on ok confirmation; planning 3(a); log of same name |
| `test_rl149_typical_case` | 13 OK | own-stop/set, typical-case and G1-wait negative cases; log |
| `test_rl149_blackout` | 4 OK | registered driver window, no campaign override; log |
| `test_rl145_night_confirmation` | 6 OK | named alias pair / confirmation; log |
| `test_rl145_part_c` | 31 OK | evaluator/own-stop/negative cases; log |
| `test_v4_kit` | 116 OK | pair/N_chunk/budget/readiness bindings; log |
| `test_r1_arm` | 10 OK | sizing, notice floor, mutated-chain refusal before work, multi-day fence, synthetic complete/interrupt restore routes; log |
| New `tests/test_preparation.py` | 17 OK | source mismatch / retired receipt; stage success/repeat/dry-run; missing close/fence root, live fence/process, observation failure, loaded job, dirty/attached/wrong HEAD, conflicting output and path-symlink refusals; `tests/logs/preparation.log` |
| Both shell scripts | syntax OK (`zsh -n`) | rerunnable above |
| Size at Thu 19 00:00 PST | 102168 driver, 119880 outer, 2 crossings | `tests/size-thu0000.json` |
| Fixture orphan census | **UNVERIFIED, exit 2** | `PermissionError: [Errno 1] Operation not permitted: 'ps'`; no empty-census claim |

**212 tests passed (195 pinned-source +17 preparation), no skips.**
Some test logs intentionally print `fail`/`refused` from negative fixtures;
their unittest outcomes are OK. None is a live instrument/restore result.

Source census:

- All 17 current condition-13/Part C hashes equal the existing F0 item's
  published table. SOURCES adds eight route/input hashes (25 total).
- `git diff c3f4bacd8 P -- <ten condition-13 paths>` is empty.
  The 17-path diff has exactly one file, `v4_registration.py`, and exactly
  one added `v4_desk_seal.py` EXECUTED_CLOSURE line. Imported-module
  carry reasons are separately transcribed in CARRY-RECORD-DRAFT.
- Both gate files equal `a6a09e6d7` by their fixed SHA-256 test.
- #777's `f30a97d00`, #783's `c3f4bacd8`, #798's `e5b4f4f7f` and
  #790 reviewed head `ca02c76e3` are ancestors of P. `ca02c76e3` and P
  have equal trees. See CI-AND-MERGES for fresh read-only API metadata.
- `pyproject.toml`, `env/mac-measurement-lock.txt`,
  `env/analysis-lock.txt` equal `9c40e4e5d` byte for byte.
- No receipt file at P's retired `registration/ruling_1f_receipt.json`;
  no `g0_cap_receipt` key in the pending thermal policy. A null policy is
  expected before R1 fills it and is not treated as native readiness.
- CI run [43712204542](https://github.com/mpmdw/JouleWise/actions/runs/43712204542)
  at P is completed/success, checked via GitHub plugin.

Caught and corrected during preparation: null pending policy handling;
zsh's reserved `modules` variable; an initial `.venv` symlink dirtied the
checkout because `.venv/` ignores a directory. The staging regression
exposed the last case; staging now links the existing environment's
contents inside an ignored directory, and repeat preserves a clean tree.
No source or dependency pin changed. A changed output is refused intact.

The canonical full suite was not run: this is docs and isolated preparation
tooling, with no production code/kit/registration change. Its focused
source and safety tests above are the relevant checks; P's full CI is green.
No new hardware admission or final lead verification is claimed. The
orphan census remains a lead-visible environment limitation, not a pass.
