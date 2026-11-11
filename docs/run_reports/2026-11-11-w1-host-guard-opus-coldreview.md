# Cold review: `ops/2026-11-11-w1-host-guard` @ `7d2a1bfe7` (suite-wide host-command guard)

Opus 5.5, interim lane lead, 2026-11-11, on the Air. Reviewed cold against the orchestrator-approved design:
`tests/host_command_guard.py`, `tests/_host_guard_site/sitecustomize.py`, `tests/__init__.py`, the two
`import tests` launch lines in `scripts/shard_tests.py` (unbound; checked), the static site scan and allowlist,
the guard's own tests, and the one leak fix in `tests/test_post_window_unstrand.py`.

**Verdict: ADMIT-WITH-FIXES; the fixes are made in this commit (F-1, F-3).** No production or bound file changes.

## Mutation pass (each run against `tests.test_host_command_guard`)

| Mutant | Result |
|---|---|
| per-test failure removed (`addFailure` -> pass) | killed |
| `os.system` wrapper removed | killed |
| `posix_spawn(p)` wrappers removed | killed |
| `exec*` wrappers removed | killed |
| `Popen.__init__` wrapper removed | killed (32 failures) |
| `executable=` not classified | killed |
| `env` prefix not unwrapped | killed |
| shell string not split into simple commands | killed |
| `sh/zsh/bash -c` body not classified | killed |
| realpath (symlink) not compared | killed |
| `caffeinate`, `nvram`, `shutdown` each dropped from the refused set | killed (each) |
| `networksetup`/`scutil` `-set`/`--set` check removed | killed |
| `expect_refusals` usable from any module | killed |
| PYTHONPATH propagation to children removed | killed |
| sitecustomize's `install()` call removed | equivalent: importing `tests.host_command_guard` runs `tests/__init__`, which installs |
| **launchctl write verbs emptied** | **survived** -> F-1 |

Classifier probes (pure classification, nothing executed): every approved refused form refuses, bare, absolute,
symlinked, `env`-prefixed, `VAR=1`-prefixed, `sh -c`, and split on `;`, `&&`, `||`, `|`, newline and `&`;
`launchctl print/list/blame`, `networksetup -list...`, `git`, `defaults write`, `kill` are allowed at run time.

## Findings

| # | Severity | Finding | Disposition |
|---|---|---|---|
| F-1 | Medium | The launchctl tests iterate the guard's own `_LAUNCH_WRITES`, so emptying it passes vacuously. | Fixed: a literal list of the eight verbs in a new test. Mutant now killed. |
| F-2 | Info | The sitecustomize mutant is equivalent (see table). Propagation is proven by the PYTHONPATH mutant. | None. |
| F-3 | Medium | Transparent wrappers and shell grouping escaped: `nohup sudo`, `timeout 5 pmset`, `nice caffeinate`, `xargs sudo`, `time systemsetup`, `launchctl asuser 501 launchctl bootstrap`, `command sudo`, `exec pmset`, `(sudo x)`, `$(pmset -g)`, backticks, `{ ...; }`. | Fixed: wrappers classify every trailing suffix; `asuser`/`bsexec` recurse; `$(`, backtick, parentheses and braces open a new simple command before lexing (quoted text stays one token, so `git commit -m "(pmset)"` is allowed). New test; wrapper, opener and asuser mutants killed. Residual: substitution inside double quotes, `eval`, functions, runtime-assembled names. |
| F-4 | Low | The caffeinate leak fix turns a native witness (real `caffeinate` + native `ps`) into a synthetic one; native coverage of the caffeinate-wrapped unstrand is gone from the suite. | Accepted: a real `caffeinate` is on the approved refused list. The native case moves to the post-install native checks (remote), with the other W-3 natives. |
| F-5 | Info | The seat's guarded scan reached ~14 modules; 9 hit its caps and 144 keyword candidates were not reached (seat report). | The lane lead runs the guard over the batch/arm module set on the Air, and CI on the combined PR runs it suite-wide on Linux. |
| F-6 | Info | NEEDS_RULING (grep for `PYTHONPATH` in production): production already uses `PYTHONPATH` legitimately. | Lead decision: accept the implemented contract (the guard's own variable and site directory are absent from `scripts/` and `joulewise/`). |

## Leak list (before fixes), as established so far

| Module | Test | Command | Where seen |
|---|---|---|---|
| `tests.test_post_window_unstrand` | `PostWindowUnstrandTests.test_native_ps_clean_completed_window_under_caffeinate` | `/usr/bin/caffeinate -i /bin/bash ...` | seat scan; fixed in `4217aa0ae` |

## Tests run (Air)

- `tests.test_host_command_guard`: 12 OK after the fixes. `tests.test_host_command_sites`: OK.
