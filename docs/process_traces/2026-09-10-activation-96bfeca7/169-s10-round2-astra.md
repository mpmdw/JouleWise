```json
{
  "schema":"claude-codex-report/v1",
  "genre":"implementation",
  "status":"findings",
  "completion":"complete",
  "summary":"Round-two writer routing, judged-epoch records, G2-a proof and diagnostic registration are complete; the identity-probe failure reproduces on the baseline checkout.",
  "workspace":{"base_requested":"c75da300","base_mode":"exact","head_start":"c75da300f72e1ccc28473d856c9abce8e61f9882","head_end":"c75da300f72e1ccc28473d856c9abce8e61f9882","upstream_end":"c75da300f72e1ccc28473d856c9abce8e61f9882","branch":"feat/2026-09-10-epoch-continuation"},
  "pathspec":["docs/contracts/d078_reason_registry_amendment.md","docs/contracts/epoch_continuation.md","scripts/validate_powermetrics_fiducial.py","tests/fixtures/epoch_continuation/README.md","tests/fixtures/epoch_continuation/build.py","tests/fixtures/epoch_continuation/writer_mutation_cuts.py","tests/test_d078_reason_registry.py","tests/test_validate_powermetrics_fiducial.py","tests/test_validate_powermetrics_fiducial_derivation_only.py"],
  "unowned_dirty":[],
  "verdict":{"implementation":"implemented","acceptance":"ready"},
  "verification":[
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_epoch_continuation","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 39 tests in 27.578s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 92 tests in 0.369s","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 13 tests in 69.326s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_validate_powermetrics_fiducial","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 6 tests in 3.857s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_generate_g2a_probe_inputs","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 24 tests in 0.637s","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},
    {"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d078_reason_registry","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 14 tests in 0.077s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V7","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 31 tests in 1.085s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V8","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_mint_policy_resolver_guard","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 0.014s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V9","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_custody_mode_inventory","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 7 tests in 34.782s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V10","kind":"build","cmd":"PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/s10-round2-compile-cache python3 -m compileall -q joulewise scripts","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V11","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/writer_mutation_cuts.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["cuts=10 killed=10 survivors=0 source_sha256_restored=true"]},"expected":{"exit_code":0,"tail_regex":"cuts=10 killed=10 survivors=0 source_sha256_restored=true$"}},
    {"id":"V12","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V13","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_calibration_acceptance_generation.DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["AssertionError: None is not an instance of <class 'str'>","Ran 1 test in 0.019s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V14","kind":"test","cmd":"cd /Users/edr/code/JouleWise-wt-epoch-integration && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_calibration_acceptance_generation.DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["AssertionError: None is not an instance of <class 'str'>","Ran 1 test in 0.019s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V15","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_powermetrics_fiducial.FrozenProtocolTests","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 12 tests in 11.195s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}}
  ],
  "flags":[{"id":"F1","kind":"environment","level":"nonblocking","text":"The live epoch-watch test gets os_build=None in both this worktree and the clean baseline checkout at 7107657d8b1000c03be13060ca9a2caa821468a5, using the same interpreter. This reproduces the failure independently of round-one changes.","needs":"Lead verifies machine identity on the permitted runner."}]
}
```

## Change

- [Ordinary preflight](/Users/edr/code/JouleWise-wt-s10-continuation/scripts/validate_powermetrics_fiducial.py:367) accepts any authenticated judged epoch. Both capture artifacts retain `acceptance_preflight`, including `judged_epochs`, continuation diagnostics and `judged_epochs_basis: "registry_pins_only"`.
- [Derivation-only guard](/Users/edr/code/JouleWise-wt-s10-continuation/scripts/validate_powermetrics_fiducial.py:1945) refuses continued epochs with the existing `calibration_derivation_only_epoch_unchanged` code. Its screen basis carries judged epochs.
- [Diagnostic registration](/Users/edr/code/JouleWise-wt-s10-continuation/docs/contracts/d078_reason_registry_amendment.md:24) and [degradation documentation](/Users/edr/code/JouleWise-wt-s10-continuation/docs/contracts/epoch_continuation.md:150) are installed.
- The [writer CLI regression](/Users/edr/code/JouleWise-wt-s10-continuation/tests/test_validate_powermetrics_fiducial_derivation_only.py:491) proves refusal without continuation and rc 0 with continuation. The [G2-a regression](/Users/edr/code/JouleWise-wt-s10-continuation/tests/test_validate_powermetrics_fiducial.py:86) exercises its real delegation to writer preflight.

Decision: preserve the Decimal-returning helper API and add an optional record output. The existing continuation accessor sufficed; neither the continuation core nor G2-a needed a lasting code change. No design disagreement.

Footprint: **6 modified files, 3 additions**, all allowlisted; no unowned changes, commits or Git-state changes. Acceptance bytes and production registries remain unchanged.

The [mutation runner](/Users/edr/code/JouleWise-wt-s10-continuation/tests/fixtures/epoch_continuation/writer_mutation_cuts.py:21) records exact test identifiers. Every cut was killed by one test, with source hashes restored:

| Cut | Mutation | Killing test |
|---|---|---|
| W01 | Restore original-epoch-only comparison | Ordinary continued-epoch CLI capture |
| W02 | Disable epoch refusal | Unregistered/rotated continuation refusal |
| W03 | Drop preflight record population | Continued preflight record |
| W04 | Mislabel registry-only authentication | Continued preflight record |
| W05 | Omit continued epochs from screen basis | Derivation basis |
| W06 | Guard derivation-only against original epoch only | Continued-epoch derivation refusal |
| W07 | Empty evidence preflight record | Ordinary continued-epoch CLI capture |
| W08 | Empty manifest preflight record | Ordinary continued-epoch CLI capture |
| W09 | Skip G2-a writer preflight | G2-a continuation delegation |
| W10 | Remove diagnostic registration | D-078 continuation registration |

## Verification notes

V13 and V14 fail identically at the `os_build` string assertion; their complete failure tails are above. This supports the environmental diagnosis specified by the brief.

The GitHub directive re-fetch failed to connect; implementation followed the supplied briefs and local magistrate synthesis. Full-suite discovery was omitted as instructed. Compilation wrote bytecode under `/tmp`.

## Residual risk

Continuation evidence remains synthetic, and no production continuation was issued. The next step is lead diff review and canonical-suite replay, followed by the governed issuance and live verification gates.