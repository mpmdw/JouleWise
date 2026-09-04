```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Runtime closures are sound, but the landing retains a blocker-level stale kernel fence and several documentation/bench handoff inconsistencies.","workspace":{"base_requested":"e40e7502","base_mode":"exact","head_start":"fea89b7254bd3491df327d29469d8a0eb4026dd2","head_end":"fea89b7254bd3491df327d29469d8a0eb4026dd2","upstream_end":null,"branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"KERNEL-STALE-01","severity":"blocker","file":"docs/process/state_kernel.json:4286","classification":"documentation-consistency","counterfactual":"Kernel-directed work can still forbid or seek to undo the installed 600 s conjunct because it declares the 5 s upper bound pending and unimplemented.","observed":"Lines 4286-4289 retain the COLD-GATE-PENDING 5 s fence; line 4345 says the upper bound is deliberately not implemented."},{"id":"DOC-ADDITIVITY-01","severity":"should_fix","file":"docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md:79","classification":"documentation-consistency","counterfactual":"The required amendment-only audit cannot establish that the historic ruling text was preserved verbatim.","observed":"The docs-only diff reports eight removed lines not re-emitted verbatim, including two ruling lines and unrelated RF-04/RF-08 rewrites."},{"id":"D170-UNRESOLVED-01","severity":"should_fix","file":"joulewise/arm_readiness.py:6478","classification":"documentation-consistency","counterfactual":"D-170 citations cannot resolve to an authoritative decision-log entry.","observed":"Production and §6.3 cite D-170; docs/decision_log.md ends at D-169 (line 10448)."},{"id":"F7-BENCH-UNAPPLIED-01","severity":"should_fix","file":"docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md:1163","classification":"registered-limitation","counterfactual":"Following the arithmetic-addendum link at this head reaches no target anchor.","observed":"The correct addendum exists only as the lead-owned bench text; COLD-GATE-RULING.md has no matching addendum/anchor yet."}]},"verification":[{"id":"V1","kind":"suite","cmd":"python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas tests.test_arm_readiness_integration","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 180 tests in 223.050s","OK (skipped=12)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=12\\)"}},{"id":"V2","kind":"test","cmd":"python3 -m unittest tests.test_docs_freshness","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 6 tests in 0.053s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V3","kind":"test","cmd":"M2: 600_000_000_000 -> 599_999_999_999; python3 -m unittest [the three exactly-600 tests]","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 3 tests in 2.145s","FAILED (failures=2, errors=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},{"id":"V4","kind":"test","cmd":"M9: <= -> <; python3 -m unittest [the three exactly-600 tests]","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 3 tests in 2.163s","FAILED (failures=2, errors=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},{"id":"V5","kind":"test","cmd":"M8: evidence_author_t0_predicate_refused -> evidence_author_t0_predicate_refused_mutant; python3 -m unittest [integration census, direct issuance]","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 2 tests in 2.062s","FAILED (failures=2)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},{"id":"V6","kind":"test","cmd":"M10: _MIN_IDLE_NS + 1; python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_t0_liveness_constant_matches_minimum_idle_interval","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 1 test in 0.000s","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},{"id":"V7","kind":"test","cmd":"Paired +1 mutation of _MIN_IDLE_NS and _T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS; python3 -m unittest [the three +1-ns refusal tests]","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 3 tests in 2.599s","FAILED (failures=3)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},{"id":"V8","kind":"test","cmd":"Remove arm exactly-600 assertion and apply M2; python3 -m unittest [the three exactly-600 tests]","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 3 tests in 2.024s","FAILED (failures=1, errors=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},{"id":"V9","kind":"test","cmd":"Omit arm_readiness_evidence_t0.py from census and inject M8; python3 -m unittest tests.test_arm_readiness_integration.ArmReadinessIntegrationTests.test_t0_evidence_author_refusal_vocabulary_is_closed","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 1 test in 0.001s","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},{"id":"V10","kind":"inspection","cmd":"grep -n '5 s\\|≤5\\|<=5\\|35 s' docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["1055-1065: eleven 45 s rows","1074: historical 11 * 45 s arithmetic","1159: resolved 495 seconds + 105 seconds"]},"expected":{"exit_code":0,"tail_regex":"1159:timeout \\(495 seconds\\), plus 105 seconds"}},{"id":"V11","kind":"inspection","cmd":"git status --porcelain","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[{"id":"B1","kind":"baseline_drift","level":"nonblocking","text":"The requested suite reports skipped=12, not 7: 7 active skips are in test_arm_readiness_evidence_t0 and 5 in test_arm_readiness_integration; source comparison shows neither count is new in this delta.","needs":""},{"id":"R1","kind":"residual_risk","level":"nonblocking","text":"No quiet-machine, arm, custody, nap, or live-rehearsal action was run. The 600 s rule remains a ruled liveness limit, not a proven successful-path maximum.","needs":"Lead should apply the two bench-owned proposals before claiming aggregate closure."}]}
```

## Findings

- **BLOCKER KERNEL-STALE-01** — [state_kernel.json](/Users/edr/code/JouleWise-wt-t26-b2/docs/process/state_kernel.json:4286) still calls the 5 s rule `COLD-GATE-PENDING` and says it must not be implemented; its status note still says the upper bound is deliberately absent ([line 4345](/Users/edr/code/JouleWise-wt-t26-b2/docs/process/state_kernel.json:4345)). Production now enforces the ruled inclusive 600 s relation. This is pre-existing/outside the seven-file delta, but it blocks aggregate closure.

- **SHOULD-FIX DOC-ADDITIVITY-01** — F-4/F-5 are semantically marked as superseded, but not amended additively as required. The docs diff found eight removed lines not re-emitted verbatim: the prior ruling’s two split lines, RF-04/RF-08 rewrites, RF-17, the numeric old relation, the §6.3 heading, and the final resolved-paragraph line. The unrelated RF-04/RF-08 rewrites are at [lines 477 and 481](/Users/edr/code/JouleWise-wt-t26-b2/docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md:477).

- **SHOULD-FIX D170-UNRESOLVED-01** — [production](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness.py:6478) and [§6.3](/Users/edr/code/JouleWise-wt-t26-b2/docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md:1152) cite D-170, but the decision log ends with D-169 at [line 10437](/Users/edr/code/JouleWise-wt-t26-b2/docs/decision_log.md:10437).

- **SHOULD-FIX F7-BENCH-UNAPPLIED-01** — The bench addendum is arithmetically correct, but the landing’s link at [line 1163](/Users/edr/code/JouleWise-wt-t26-b2/docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md:1163) has no target anchor until the lead appends the bench text to `COLD-GATE-RULING.md`.

## Contract reconciliation

| Closure | Verdict | Evidence |
|---|---|---|
| F-1 | INSTALLED | Comparator is production [arm_readiness.py:6478](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness.py:6478)-[6482](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness.py:6482). Arm test [line 65](/Users/edr/code/JouleWise-wt-t26-b2/tests/test_arm_readiness.py:65) calls `_predicate_passes` directly; issuance [line 849](/Users/edr/code/JouleWise-wt-t26-b2/tests/test_arm_readiness_evidence_t0.py:849) calls public authoring → production predicate; rehearsal [line 574](/Users/edr/code/JouleWise-wt-t26-b2/tests/test_t0_rehearsal.py:574) calls `_run_real_arm_boundary` → `_evaluate_rows` → predicate. M2/M9 kill all three. |
| F-2 | INSTALLED | Vocabulary-B registry is test-side [integration:63](/Users/edr/code/JouleWise-wt-t26-b2/tests/test_arm_readiness_integration.py:63); census scans both author files [lines 694-714](/Users/edr/code/JouleWise-wt-t26-b2/tests/test_arm_readiness_integration.py:694). Equality catches both unregistered produced codes and registered-but-unproduced codes; the brief required only the former. |
| F-3 | INSTALLED | Equality test [evidence-t0:855](/Users/edr/code/JouleWise-wt-t26-b2/tests/test_arm_readiness_evidence_t0.py:855) binds the distinct constants. The T-0 author imports arm readiness [line 35](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness_evidence_t0.py:35), not vice versa. |
| F-4 | PARTIAL | Marker/addendum are present at [ruling:80](/Users/edr/code/JouleWise-wt-t26-b2/docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md:80) and [153](/Users/edr/code/JouleWise-wt-t26-b2/docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md:153), but the original lines were edited rather than preserved verbatim. |
| F-5 | PARTIAL | Resolved banner and markers work; the required grep has no live 5 s/35 s policy. Strict additive-history verification fails as above. |
| F-6 | INSTALLED | Limitation at [§6.3.1](/Users/edr/code/JouleWise-wt-t26-b2/docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md:1167) correctly states no finite successful-path maximum. Bench kernel row rejects fixture/mock/synthetic receipts. |
| F-7 | PARTIAL | Bench arithmetic is correct, but its lead-owned target addendum is not yet applied. |
| F-8 | INSTALLED | The only `joulewise/` delta is `arm_readiness.py` (1 added/4 removed): its old four-line comment became the one-line ruled-provenance comment at [line 6478](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness.py:6478). |

The F-5 grep classifications: lines 1055–1065 and 1074 are inside the superseded historical block; line 1159 is a quote in the resolved paragraph. No live hit remains.

## Physics

Independent re-derivation agrees with Sol: 11 post-R1 probes reach `process.wait(timeout=45)` at [evidence-t0:449](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness_evidence_t0.py:449), for 495 s. Eleven fixed Git calls use 20 s timeouts through [arm_readiness.py:4373](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness.py:4373) and [5203](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness.py:5203), adding 220 s: 715 s before untimed startup/I/O, scans, hashing, and runtime preparation/projection ([identity_pins.py:1287](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/identity_pins.py:1287), [1439](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/identity_pins.py:1439)). Thus no finite successful-path maximum follows.

The limitation says this accurately and does not claim empirical proof. The bench arithmetic is correct: `0.499 + 3.68e-6 × 1830 = 0.5057344`; at 22,230 s it is `0.5808064`. Its kernel acceptance expressly makes fixture receipts non-satisfying.

Same-signature statement: first delta audit of `fea89b72`. All runtime test-gap closures are installed; remaining findings are documentation-consistency or registered-limitation items. The ruled 600 s number and inclusive `<=` did not move.

## Executed evidence

    python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas tests.test_arm_readiness_integration
    Ran 180 tests in 223.050s
    OK (skipped=12)
    exit 0

    python3 -m unittest tests.test_docs_freshness
    Ran 6 tests in 0.053s
    OK
    exit 0

    M2 / M9: three exactly-600 tests
    Ran 3 tests; FAILED (failures=2, errors=1)
    exit 1

    M8: integration census + direct issuance test
    Ran 2 tests; FAILED (failures=2)
    exit 1

    M10: constant-equality test
    Ran 1 test; FAILED (failures=1)
    exit 1

    Paired +1 constants: three +1-ns refusal tests
    Ran 3 tests; FAILED (failures=3)
    exit 1

    Remove arm exact-600 assertion + M2: three exact-boundary tests
    Ran 3 tests; FAILED (failures=1, errors=1)
    exit 1

    Omit T-0 author from census + inject M8
    Ran 1 test; FAILED (failures=1)
    scanner: mutant_seen=False; literal_count=0
    exit 1 / 0

    git status --porcelain
    <empty>
    exit 0

VERDICT: BLOCKER 1