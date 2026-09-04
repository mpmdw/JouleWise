# Night plan pin — Sol fix round 2 report

Date: 2026-09-03 PDT  
Branch: `feat/2026-09-03-night-plan-pin`  
Base and checkout HEAD: `bb5441e3205d77f5d1d86d2941bbca839f582431`  
Authority: Fable fix-round-2 brief; exhaustive `WRITE_SCOPE` observed.

## Outcome

Finding B2 is cured. The install path now loads the raw plan mapping and calls
`NightPlan.from_mapping` before crossing the Python-to-zsh output boundary.
Consequently, the shared `_HEAD_RE.fullmatch` validation sees an embedded or
trailing LF in `measurement_head` and refuses it instead of allowing command
substitution to erase the evidence. The installer additionally refuses
surrounding whitespace on `measurement_root`, as required by the fix brief.

Only successfully validated field values cross into zsh, base64-encoded. This
keeps spaces and other significant bytes out of shell field splitting while
retaining the existing install-time Git pin comparisons. Refusals exit 3 with
the shared validator's named-field detail. The uninstall bypass remains
unchanged.

The test plan factory now emits the exact v2 mapping accepted by
`NightPlan.from_mapping`. The pre-existing positive render-only install remains
green, and new regressions pin a trailing LF on `measurement_head` and a
trailing space on `measurement_root`.

## Clause map — fix-round-2 delta

| Proposition | Production site | Biting assertion | One-site counterfactual |
|---|---|---|---|
| Raw `measurement_head` must match exactly 40 lowercase hex characters, without normalization | `scripts/install_night_agent.sh:52-65` calling `NightPlan.from_mapping` before base64 transport | `tests/test_install_night_agent.py:163` `test_install_refuses_measurement_head_with_trailing_lf` | Insert `data["measurement_head"] = data["measurement_head"].strip()` before validation; the test observes exit 0 instead of 3. |
| `measurement_root` must be absolute and have no surrounding whitespace | `scripts/install_night_agent.sh:55-60` | `tests/test_install_night_agent.py:145` `test_install_refuses_measurement_root_with_trailing_space`; existing `:139` relative-root test | Delete the `parsed.measurement_root != parsed.measurement_root.strip()` refusal; the trailing-space case proceeds to the Git probe instead of the named-field validation refusal. |
| A valid exact-v2 plan still installs in render-only mode | `scripts/install_night_agent.sh:44-86` | `tests/test_install_night_agent.py:121` `test_install_with_both_pins_matching_renders_both_plists` | Corrupt the shared-validation import or field transport; the installer exits nonzero or fails to render both plists. |

## Verification

Exact requested final command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent tests.test_run_night tests.test_night_gate
```

Verbatim final tail:

```text
...............................................................................................................
----------------------------------------------------------------------
Ran 111 tests in 13.781s

OK
```

`zsh -n scripts/install_night_agent.sh` and `git diff --check` both exited 0
with empty output.

## Mutation proof

Before mutation, the installer SHA-256 was
`ccd596baa78ae1123a04516c3aa2e5850c83804fb1aadd190d3129d3f91605e2`.
The executed mutation inserted this line immediately before shared validation:

```python
data["measurement_head"] = data["measurement_head"].strip()
```

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent.InstallNightAgentTests.test_install_refuses_measurement_head_with_trailing_lf
```

Observed failure tail:

```text
FAIL: test_install_refuses_measurement_head_with_trailing_lf (tests.test_install_night_agent.InstallNightAgentTests.test_install_refuses_measurement_head_with_trailing_lf)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-planpin/tests/test_install_night_agent.py", line 167, in test_install_refuses_measurement_head_with_trailing_lf
    self.assertEqual(3, completed.returncode)
AssertionError: 3 != 0

----------------------------------------------------------------------
Ran 1 test in 0.840s

FAILED (failures=1)
```

The mutation was removed with `apply_patch`. The restored installer SHA-256 is
again `ccd596baa78ae1123a04516c3aa2e5850c83804fb1aadd190d3129d3f91605e2`,
after which the exact requested three-module command passed as recorded above.

## Scope and workspace

No commit, staging operation, LaunchAgent write, custody write, quiet-machine
measurement, or cross-model hop was performed. Only the two implementation
paths and this authorized report are dirty.
