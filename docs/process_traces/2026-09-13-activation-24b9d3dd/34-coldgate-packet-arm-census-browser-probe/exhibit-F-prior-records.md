# Exhibit F — prior records of this row

## docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md lines 1050–1066 (the row's four probes as documented on 2026-08-23)
```

Every `_fresh_probe` subprocess in the intervening derivers is therefore:

| Deriver row | Exact argv | Governing timeout |
|---|---|---:|
| `clock.network_time_off` | `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` | 45 s |
| `t0.background_quiet` | `/usr/bin/pgrep -lf 'XProtect\|mds_stores\|mdworker\|mdbulkimport\|backupd\|photoanalysisd\|softwareupdated\|Spotlight\|mediaanalysisd'` | 45 s |
| `t0.display_thermal_idle` | `/usr/bin/pmset -g therm` | 45 s |
| `t0.no_stray_keepawake` | `/usr/bin/pgrep -x caffeinate` | 45 s |
| `t0.no_stray_keepawake` | `/usr/bin/pgrep -lf 'codex\|claude\|t3'` | 45 s |
| `t0.no_stray_keepawake` | `/usr/bin/pgrep -lf 'Safari\|Google Chrome\|Chromium\|Firefox\|browser automation'` | 45 s |
| `t0.no_stray_keepawake` | `/usr/bin/pgrep -lf 'powermetrics\|window-chain\|run_campaign\|tail -f\|watch'` | 45 s |
| `t0.passwordless_powermetrics` | `/usr/bin/sudo -n /usr/bin/powermetrics -i 200 -n 1` | 45 s |
| `t0.power_path` | `/usr/bin/pmset -g batt` | 45 s |
| `t0.power_path` | `/usr/bin/pmset -g custom` | 45 s |
| `t0.power_path` | `/usr/sbin/system_profiler SPPowerDataType -json` | 45 s |

```

## git log: when the browser and monitor patterns entered joulewise/arm_readiness_evidence_t0.py
```
ac3fe1d2 2026-08-14 Readiness tooling: registry reconciliation + arm-time evidence author + chain-fix batch (union of #146/#147/#148 + integration fixes) (#149)
```

## Mentions of a passing process census in the August clone-proof and dry-run records (rg 'eleven-kind census|process census' over 2026-08-2*)
```
```

## Does any test exercise the real pgrep for this row, or are probes mocked? (rg over tests for the browser pattern and for _execute_probe patching)
```
tests/test_arm_readiness_evidence_t0.py:799:        stack.enter_context(mock.patch.object(t0, "_execute_probe", side_effect=selected_probe))
tests/test_arm_readiness_evidence_t0.py:970:        """The ruled 600 s = (post-R1 ``_fresh_probe`` sites) × 45 s + 105 s.
tests/test_arm_readiness_evidence_t0.py:976:        census of direct ``_fresh_probe`` calls, the timeout from the
tests/test_arm_readiness_evidence_t0.py:983:        a deriver registered for a second row, a direct ``_execute_probe``
tests/test_arm_readiness_evidence_t0.py:985:        stamp, a retry inside ``_fresh_probe``, or a wait in another
tests/test_arm_readiness_evidence_t0.py:994:        module reaches ``_fresh_probe``. Rather than enumerating reference
tests/test_arm_readiness_evidence_t0.py:1023:            if isinstance(node, ast.FunctionDef) and node.name == "_fresh_probe"
tests/test_arm_readiness_evidence_t0.py:1031:            and call.func.id == "_fresh_probe"
tests/test_arm_readiness_evidence_t0.py:1040:            if item == "_fresh_probe"
tests/test_arm_readiness_evidence_t0.py:1042:        self.assertEqual(stray, [], "non-call mentions of _fresh_probe")
tests/test_arm_readiness_evidence_t0.py:1959:                mock.patch.object(t0, "_execute_probe", execute),
tests/test_arm_readiness_evidence_t0.py:1962:                t0._fresh_probe(context, kind, "synthetic census", ("probe",))
tests/test_arm_readiness_evidence_t0.py:2448:            probes = tuple(t0._execute_probe(command, cwd=ROOT) for command in commands)
tests/test_arm_readiness_evidence_t0.py:2513:                    "Safari|Google Chrome|Chromium|Firefox|browser automation",
```
