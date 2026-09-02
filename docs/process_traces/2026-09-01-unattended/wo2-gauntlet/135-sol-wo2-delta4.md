```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIX-ROUND: C1-C3 pass their regressions and all seven mutants die, but C3 misses dangling-symlink record paths.",
  "workspace": {
    "base_requested": "66e496a534baa4d523164647023587d978ca663e",
    "base_mode": "descendant",
    "head_start": "7c80ba2d22f2317b9c6dc40c13827a4d6e86e1d4",
    "head_end": "7c80ba2d22f2317b9c6dc40c13827a4d6e86e1d4",
    "upstream_end": "7c80ba2d22f2317b9c6dc40c13827a4d6e86e1d4",
    "branch": "feat/2026-09-01-night-driver"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FIX-ROUND",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "C3 stale-record guard misses dangling symlink paths",
        "file": "scripts/install_night_agent.sh:125",
        "detail": "Under /bin/zsh, [[ -e ]] is false for a dangling symlink. An executed copied-suite variant using a dangling courier.sent therefore returned 0 instead of the required 3."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/fix4-audit-sol/tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 95 tests in 1.837s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 95 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/fix4-audit-sol/base && TMPDIR=tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 95 tests in 2.172s", "FAILED (failures=5)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=5\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/fix4-audit-sol/linkcase && TMPDIR=tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: 0 != 3", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "AssertionError: 0 != 3"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/fix4-audit-sol/freshcase && TMPDIR=tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 95 tests in 1.627s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 95 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check 66e496a534baa4d523164647023587d978ca663e 2f9ad50a84f88bf36730724de4e1ce94e97d0d18",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": []
}
```

## Findings

F1 — should-fix — [scripts/install_night_agent.sh:125](/Users/edr/code/JouleWise-wt-night-driver/scripts/install_night_agent.sh:125): `[[ -e path ]]` is false for a dangling symlink. The executed `courier.sent` symlink variant returned 0 rather than 3. C3’s fresh-root guarantee should also test `-L`, for example `[[ -e "$path" || -L "$path" ]]`.

Verdict: **FIX-ROUND**.

## Cure re-audit

| Item | Executed pre-fix failure | Post-fix |
|---|---|---|
| C1 | Lines 375/400: entry set gained `censuses.jsonl` and `courier.json`; line 436: `chain.exited` unexpectedly existed | Guard is after `courier.sent` and before resolution/lock at [run_night.py:1265](/Users/edr/code/JouleWise-wt-night-driver/scripts/run_night.py:1265). Both stand-down boundaries return GO, preserve entries, append one line, and call no `Popen`/`run`/`killpg`. Equality runs census, two durable publishes, and courier. |
| C1 arithmetic | N/A, inspection discriminator | `_completion_epoch_s` at [run_night.py:871](/Users/edr/code/JouleWise-wt-night-driver/scripts/run_night.py:871) is the only `t0 + window_max_s + COURIER_DEADLINE_S` sum and is used by run and dead-man. No inline duplicate remains. |
| C1 run boundary | Pre-existing tests | `test_overrun_refuses_before_the_gate_or_chain`, `test_deadman_boundary_refuses_equality_and_allows_one_second_before`, and `test_courier_backoffs_do_not_enter_the_overrun_predicate` are untouched and pass. |
| C2 | Line 1146: expected 2, got 0 | [installer:58](/Users/edr/code/JouleWise-wt-night-driver/scripts/install_night_agent.sh:58) returns 2 with the required message before rendering. `--uninstall` at hour 7 remains exempt and reaches both bootouts; `--render-only` is not exempt and is refused before its directory/render path. |
| C3 | Line 1190: expected 3, got 0 | Seven regular-file names are covered by reasoning from the single loop at [installer:124](/Users/edr/code/JouleWise-wt-night-driver/scripts/install_night_agent.sh:124); each appends its name and exits 3. Dirty uninstall passes; the executed fresh-root stub install reaches both bootstrap/print paths and passes. F1 remains. |

## Delta interactions

| Check | Result |
|---|---|
| REHEARSAL/malformed plan | **NOT FOUND** — every accepted `NightPlan`, including `REHEARSAL_STUB`, has a positive `window_max_s` ([night_gate.py:177](/Users/edr/code/JouleWise-wt-night-driver/joulewise/night_gate.py:177)). Missing fields route directly to `_malformed_plan_exit`; its fallback supplies `window_max_s=1` and never calls the helper ([run_night.py:966](/Users/edr/code/JouleWise-wt-night-driver/scripts/run_night.py:966)). |
| Missing custody root | **NOT FOUND** — `night_dir.mkdir(parents=True)` precedes the sent check and stand-down log ([run_night.py:1262](/Users/edr/code/JouleWise-wt-night-driver/scripts/run_night.py:1262)), so `_append_log` can open `custody_root/night.log`. |
| Stand-down `EXIT_GO` | **NOT FOUND** — launchd is calendar-triggered with no `KeepAlive`/`SuccessfulExit` policy ([plist:25](/Users/edr/code/JouleWise-wt-night-driver/configs/launchd/com.joulewise.night.plist.template:25)); installer does not consume job exits. Handback authority is `result.json`, not process status ([NIGHT_HANDBACK.md:10](/Users/edr/code/JouleWise-wt-night-driver/docs/process/NIGHT_HANDBACK.md:10)). |
| zsh/stale loop | **FOUND F1** — installer has a zsh shebang and tests invoke `/bin/zsh`. The plist does not invoke the installer; its `ProgramArguments` invoke Python/run_night ([plist:7](/Users/edr/code/JouleWise-wt-night-driver/configs/launchd/com.joulewise.night.plist.template:7)). Executed zsh probe: `zsh_e=absent`, `zsh_L=symlink`. |

## Mutants

| Mutant | Result |
|---|---|
| Delete guard | KILLED — three stand-down tests; `FAILED (failures=3)` |
| `<` → `<=` | KILLED — `test_dead_man_absent_marker_at_completion_epoch_couriers`; `failures=1, errors=6` |
| Guard on `plan.t0_epoch_s` | KILLED — three stand-down tests |
| Helper drops deadline | KILLED — pre-epoch stand-down and existing run boundary; `failures=3` |
| Remove C2 | KILLED — `test_installer_refuses_the_dead_man_hour_before_rendering` |
| C3 checks only `chain.started` | KILLED — `test_installer_refuses_a_stale_courier_sent_before_bootstrap` |
| C2 also fires under uninstall | KILLED — `test_installer_uninstalls_with_stale_courier_sent` |

## Signature

No finding concerns what an incomplete `chain.started` means to the dead-man. F1 concerns installer pathname detection, so this is **not** the D1/F3 marker-semantics signature and does not constitute that structural signal.

## Exact commands

```sh
audit_root=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/fix4-audit-sol
TMPDIR="$audit_root/tmp" python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate
cp -R /Users/edr/code/JouleWise-wt-night-driver "$audit_root/base"
git archive 66e496a534baa4d523164647023587d978ca663e | tar -x -C "$audit_root/base"
cp tests/test_run_night.py "$audit_root/base/tests/test_run_night.py"
(cd "$audit_root/base" && TMPDIR=tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate)
/usr/bin/perl -ni -e 'print unless $. >= 1270 && $. <= 1277' "$audit_root/a/scripts/run_night.py"
/usr/bin/perl -pi -e 'if ($. == 1271) { s/</<=/ }' "$audit_root/b/scripts/run_night.py"
/usr/bin/perl -pi -e 'if ($. == 1271) { s/completion_epoch_s/plan.t0_epoch_s/ }' "$audit_root/c/scripts/run_night.py"
/usr/bin/perl -pi -e 'if ($. == 872) { s/ \+ COURIER_DEADLINE_S// }' "$audit_root/d/scripts/run_night.py"
/usr/bin/perl -ni -e 'print unless $. >= 58 && $. <= 61' "$audit_root/e/scripts/install_night_agent.sh"
/usr/bin/perl -pi -e 'if ($. == 124) { s/receipt\.json result\.json refusal\.json chain\.started chain\.exited courier\.json courier\.sent/chain.started/ }' "$audit_root/f/scripts/install_night_agent.sh"
/usr/bin/perl -pi -e 'if ($. == 58) { s/! uninstall && // }' "$audit_root/g/scripts/install_night_agent.sh"
for copy in a b c d e f g; do (cd "$audit_root/$copy" && TMPDIR=tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate); done
```

## Residual risk

No live launchd execution was performed, as required; exit handling was inspected and installer behavior used stub launchers. Only `courier.sent` was individually executed for C3’s seven regular names; equivalence of the other six follows directly from the same loop.