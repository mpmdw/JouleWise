# Sol implementation report — fix round 9

Date: 2026-09-04. Starting committed Git HEAD: `30adc5efba46d983e308279d93abbd30c60abf73` on `feat/2026-09-03-magistrate-watchdog`; the round-9 changes are intentionally uncommitted. Contract: trace 24 findings F1 and F2. All writes stayed in the runner-owned allowlist.

## RED — rollback regressions before implementation

The installer module was run after adding the three behavioral failure-path tests and before changing the installer. Each test used a temporary `HOME`, the real zsh installer through its canonical shadow, a stubbed process view, and a stubbed `launchctl`:

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_magistrate_watchdog
EEE.....
ERROR: test_failed_bootstrap_restores_exact_preexisting_plist_and_absent_lock
FileNotFoundError: .../home/Library/LaunchAgents/com.joulewise.magistrate.plist
ERROR: test_failed_lock_seed_restores_exact_preexisting_plist_and_lock
FileNotFoundError: .../home/Library/LaunchAgents/com.joulewise.magistrate.plist
ERROR: test_failed_post_load_verification_restores_exact_preexisting_plist_and_absent_lock
FileNotFoundError: .../home/Library/LaunchAgents/com.joulewise.magistrate.plist
Ran 8 tests in 5.015s
FAILED (errors=3)
```

All three failures had the same defect-shaped cause: the old EXIT trap deleted the plist written by this attempt without restoring the pre-existing bytes. The two downstream cases also left the newly seeded lock behind.

## Implementation and clause map

| Finding / failure path | Production site | Biting behavioral assertion | Result |
|---|---|---|---|
| F1 — exclusive lock seed fails | `scripts/install_magistrate_watchdog.sh:155-205,238-284` | `tests/test_install_magistrate_watchdog.py:207-221` | A byte-for-byte backup of the pre-existing plist is restored; the colliding pre-existing lock is untouched byte-for-byte; no `launchctl` call occurs. |
| F1 — `launchctl bootstrap` fails | `scripts/install_magistrate_watchdog.sh:161-178,294-298` | `tests/test_install_magistrate_watchdog.py:223-238` | The prior plist bytes are restored and the exact lock seed created by this attempt is removed, restoring prior absence. |
| F1 — post-load `launchctl print` fails | `scripts/install_magistrate_watchdog.sh:161-178,299-302` | `tests/test_install_magistrate_watchdog.py:240-255` | After the existing `bootout` rollback, the prior plist bytes are restored and the exact lock seed created by this attempt is removed, restoring prior absence. |
| F1 — ownership guard | `scripts/install_magistrate_watchdog.sh:238-284` | The two downstream tests compare the lock path with its absent pre-state | The seed is written completely with short-write handling; a partial seed is removed only when its inode is still the one opened by this attempt, and later cleanup removes a completed seed only while its bytes still match the retained snapshot. |
| F2 — truthful round-8 metadata | `docs/process_traces/2026-09-03-watchdog-build/23-sol-fix-round-8-report.md:3` | Direct comparison with `git log` | Trace 23 now names baseline `1b51fecf...` and final round-8 head `a15cc15e...`. |

Temporary rollback copies are removed on both success and failure. Successful install semantics are unchanged: the newly rendered plist and adoption lock remain in place after bootstrap and verification succeed.

## GREEN — installer rollback and success paths

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_magistrate_watchdog
........
----------------------------------------------------------------------
Ran 8 tests in 4.771s

OK
```

## Required authorized-module tails

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_magistrate_watchdog
........
----------------------------------------------------------------------
Ran 8 tests in 4.771s

OK

$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog
............................................................
----------------------------------------------------------------------
Ran 60 tests in 0.235s

OK
```

No broader test discovery was run because the runner's PREFLIGHT RULE allowed only these two modules. No install, real `launchctl`, agent/session launch, default-custody access, LaunchAgent mutation, production signal, or quiet-machine work occurred.
