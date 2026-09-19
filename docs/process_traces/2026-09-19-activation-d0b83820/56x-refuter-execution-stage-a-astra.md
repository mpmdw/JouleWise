```json
{
"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Two reproducible executor defects; all X items answered, with baseline failures and a blocked host census.",
"workspace":{"base_requested":"0c529f99","base_mode":"exact","head_start":"087bf3afc9f46e11edce9ab0376b0a8f7e2762df","head_end":"087bf3afc9f46e11edce9ab0376b0a8f7e2762df","upstream_end":"087bf3afc9f46e11edce9ab0376b0a8f7e2762df","branch":null},
"pathspec":[],"unowned_dirty":[],
"verdict":{"counts":{"blocker":1,"should_fix":1,"nit":0},"findings":[
{"id":"R1","severity":"blocker","title":"Normal evidence completion suppresses its courier","call_site":"scripts/run_night.py:1248; producer joulewise/quiet_predicate_campaign.py:449","counterfactual":"A completed executor already wrote evidence_cleanup.json. The courier guard calls the exclusive _write_json on that path, catches FileExistsError, and returns attempted=0, sent=false despite proven cleanup. With that destination absent, the same clean journal passes.","recommendation":"Preserve the executor receipt and write any driver recheck to a separate artifact; test successful executor-to-courier handoff."},
{"id":"R2","severity":"should_fix","title":"Pilot interior moves with accepted collector startup delay","call_site":"scripts/sample_quiet_predicate_evidence.py:846-847; scheduled deadline at :751-754","counterfactual":"Scheduled epoch 1000, collector start 1002, accepted drift 2 s: the 480 s interior becomes [1062,1542], instead of the frozen scheduled [1060,1540].","recommendation":"Anchor the interior to the scheduled envelope using the recorded clock mapping; cover nonzero drift below the five-second exclusion threshold."}
]},
"verification":[
{"id":"X1a","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_night_gate tests.test_gen_evidence_night tests.test_quiet_predicate_campaign tests.test_sample_quiet_predicate_evidence","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 142 tests in 11.417s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"X1b","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_run_night","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 192 tests in 180.494s","FAILED (failures=3, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"X1c","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_night_agent_install","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 61 tests in 1115.064s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"X1d","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier quick --workers 4","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["QUICK SUMMARY tier=quick modules=153 excluded=88 failures=1 seconds=150.576 result=FAIL"]},"expected":{"exit_code":0,"tail_regex":"result=PASS"}},
{"id":"X2-X4","kind":"smoke","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/qpe-execution-review/oracles.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["X2 REAL SUPERVISOR 2","X2 REAL STATUS refused probe_process_survived False","X2 REAL VALIDATOR REFUSED probe receipt outcome is not ok","X2 FIXTURE CLEANUP VALIDATOR PASS joulewise.night_evidence_probe_receipt.v1","X2 CAPTURE ARTIFACTS [] []","X2 CENSUS after PermissionError(1, 'Operation not permitted')","X3 i PASS night_refused_registration","X3 ii PASS night_refused_registration registration binds chain source 0000000000000000000000000000000000000000000000000000000000000000; measured source is 568a2771b28da9d805cd23ff4059bbbc27d6dfad1f8d9603331a412e3751b7ea","X3 iii PASS {'outcome': 'refused', 'refusal_code': 'probe payload kind ambiguous'}","X3 iv PASS gen_evidence_night.py: error: unrecognized arguments: --envelopes 13","X3 v PASS night_refused_registration","X3 MUTANT KILLED busy FAILED (failures=1)","X3 MUTANT KILLED overlap FAILED (failures=1)","X4 ADMISSION PASS additive keys ['registration_label', 'registration_ruling']","X4 PROBE BYTE IDENTICAL 2697 2530dced4aa217adcc46179f1e555ba541c9d500fbc2e05aaeb8cc48b3e9fe6c","ALL ORACLES FINISHED"]},"expected":{"exit_code":0,"tail_regex":"ALL ORACLES FINISHED"}},
{"id":"R1-repro","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/qpe-execution-review/courier_repro.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["REPRODUCED: successful executor cleanup file suppresses courier"]},"expected":{"exit_code":0,"tail_regex":"REPRODUCED"}},
{"id":"R2-repro","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/qpe-execution-review/interior_repro.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["REPRODUCED: 2-second accepted startup drift shifts interior from scheduled +60 to +62"]},"expected":{"exit_code":0,"tail_regex":"REPRODUCED"}},
{"id":"census","kind":"inspection","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans","cwd":".","observed":{"result":"fail","exit_code":2,"tail":["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]},"expected":{"exit_code":0,"tail_regex":"\"count\": 0"}}
],
"flags":[
{"id":"F1","kind":"environment","level":"blocking","text":"X2: /bin/ps denied before and after; pgrep cannot access sysmond. The real supervisor correctly refused probe_process_survived. Only the explicitly mocked cleanup replay validates; it is not host process-absence proof. No live power capture or real LaunchAgent installation was performed.","needs":"Lead repeats verify-only probe and before/after census on a host where process inspection works."},
{"id":"F2","kind":"verification_gap","level":"nonblocking","text":"All final driver failures, installer census failure and quick-tier failures reproduce in a /tmp archive of exact base 0c529f99. Watchdog timeouts remain unexplained; process-identity failures are environmental. The aborted initial combined run also showed a generator error without a retained traceback; subsequent complete generator runs passed.","needs":"Lead resolves baseline verification limits and performs final verification after fixes."},
{"id":"F3","kind":"scope_deviation","level":"blocking","text":"Initial tests used the macOS default temporary directory under /private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T, outside the user-authorized /tmp scratch location. The combined run was stopped; final focused modules were rerun with TMPDIR/TEMP/TMP=/tmp. No repository path changed. This records a past deviation, not retrospective authorization.","needs":"Lead adjudicates the transient test-write scope deviation."}
]
}
```

## Findings

1. **R1 — blocker:** [The courier guard](/Users/edr/code/JouleWise-wt-sarefx-d0b83820/scripts/run_night.py:1248) exclusively creates a cleanup file that the executor already wrote. A successful evidence night therefore suppresses its courier with `FileExistsError`. The reproduction returned `attempted=0, sent=false`; removing only that destination allowed the same clean journal to pass.

2. **R2 — should fix:** [Interior reduction](/Users/edr/code/JouleWise-wt-sarefx-d0b83820/scripts/sample_quiet_predicate_evidence.py:846) uses the collector’s actual start, while the envelope deadline uses its scheduled start. A permitted two-second delay moves the frozen interior from scheduled +60 to +62 seconds. The fake-clock reproduction requires no collection or power sampling.

**X5:** None of the three false assertions was found. Surviving D-166 documentation describes calibration plans. Busy cores remain diagnostic inputs; both requested reducer mutations fail their tests.

Next step: fix R1/R2, add the corresponding regressions, then repeat verification and the unmocked verify-only probe.

## Residual risk

All seven X3 oracles passed. The binding oracle temporarily admitted its altered registration digest in the in-memory fixture table to isolate the chain-source comparison.

X4 passed against exact base `0c529f99`: calibration probe bytes match; admission bytes match after removing only `registration_label` and `registration_ruling`.

The driver, installer, and quick-tier failures reproduce at the base: [baseline failures](/tmp/qpe-execution-review/base-failures.log), [additional timing failures](/tmp/qpe-execution-review/base-timing.log). The sandbox blocks process inspection; the watchdog timeout cause remains unresolved.

For **X2**, rendering produced the plan, wrapper, both sidecars, and manifest under `/tmp`. The real supervisor refused because cleanup could not be established. The receipt below validated **with the explicitly mocked cleanup seam only**. No capture artifacts appeared, but the denied before/after census prevents the requested host-level absence proof.

Validator output:

```text
X2 FIXTURE CLEANUP VALIDATOR PASS joulewise.night_evidence_probe_receipt.v1
```

Receipt:

```text
{
  "chain_pgid": 48087,
  "chain_python": {
    "path": "/opt/homebrew/opt/python@3.13/bin/python3.13",
    "sha256": "d483cfdc272ddd1bfd8f6f595b65cdc2f00b8e503f0deab65b20e8faeb986132",
    "version": "3.13.1"
  },
  "chain_sha256": "29ec6bb5a7c012288feb14b09aef6645a6cce165e3026364e21c74883372df7a",
  "chain_source_sha256": "568a2771b28da9d805cd23ff4059bbbc27d6dfad1f8d9603331a412e3751b7ea",
  "cleanup_proven": true,
  "collect_started": false,
  "driver_pid": 46840,
  "driver_python": {
    "path": "/Users/edr/code/JouleWise/.venv/bin/python",
    "sha256": "d483cfdc272ddd1bfd8f6f595b65cdc2f00b8e503f0deab65b20e8faeb986132",
    "version": "3.13.1"
  },
  "finished_epoch_s": 1789851167.4816482,
  "harness_digests": {
    "joulewise/quiet_admission.py": "79e12d2b6ce8fec739c23ded36ee7127fc1b22b4b7dcf7468253eaebb632db22",
    "scripts/sample_quiet_predicate_evidence.py": "8940c19d993ed50b3bb2d521a8cf83ed00abe1d01103ea9505ca533195e8ae99"
  },
  "input_digests": {
    "/tmp/qpe-fixture-hie6llcp/custody/evidence_manifest.json": "sha256:abbb90e2aaa99fe2f009f103b1c9b30f30435c2ae7a3d90569d6fc686aa48b83",
    "/tmp/qpe-fixture-hie6llcp/custody/plan.json": "sha256:5da86000b1b871321ad791e63d2628d6141bd449e6b16f31334af58573b2cab7"
  },
  "launchd_label": "com.joulewise.night-probe.qpe-fixture",
  "load_started": false,
  "manifest_digests": {
    "configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json": "8fd65255d2167e1817a04f0326002a33d03f4947c1fb2977913b2b099fd76f2f",
    "joulewise/night_agent_install.py": "76cc5927e10127e51039c60f0983295b47e049cfaee1872f70a2753ff6f5f2ac",
    "joulewise/night_gate.py": "d47e97deee1a1786a585535c49b34f624994c758fd815b434d8fda69300862ec",
    "joulewise/quiet_admission.py": "79e12d2b6ce8fec739c23ded36ee7127fc1b22b4b7dcf7468253eaebb632db22",
    "joulewise/quiet_predicate_campaign.py": "98d169d8580083ebb1c4f8b770e7ab58c471e593ecd0318d50de009d4a523aa1",
    "scripts/night_chains/quiet_predicate_evidence.zsh": "568a2771b28da9d805cd23ff4059bbbc27d6dfad1f8d9603331a412e3751b7ea",
    "scripts/run_night.py": "c7fe28d22225396a97e4d65b6656efecfdc512689864e5a3e18f647936e086cc",
    "scripts/sample_quiet_predicate_evidence.py": "8940c19d993ed50b3bb2d521a8cf83ed00abe1d01103ea9505ca533195e8ae99"
  },
  "manifest_sha256": "abbb90e2aaa99fe2f009f103b1c9b30f30435c2ae7a3d90569d6fc686aa48b83",
  "measurement_head": "e8fbdc041a7075dda24acf81e07ad633063fd563",
  "outcome": "ok",
  "phase": "evidence-chain",
  "plan_id": "qpe-fixture",
  "plan_sha256": "5da86000b1b871321ad791e63d2628d6141bd449e6b16f31334af58573b2cab7",
  "powermetrics_path": "/usr/bin/powermetrics",
  "refusal_code": null,
  "registration_label": "QPE-01 idle-variance pilot protocol v1",
  "registration_sha256": "8fd65255d2167e1817a04f0326002a33d03f4947c1fb2977913b2b099fd76f2f",
  "schema": "joulewise.night_evidence_probe_receipt.v1",
  "started_epoch_s": 1789851164.84154,
  "verify_only": true,
  "verify_stdout": [
    "VERIFY_ONLY_OK manifest=abbb90e2aaa99fe2f009f103b1c9b30f30435c2ae7a3d90569d6fc686aa48b83"
  ]
}
```