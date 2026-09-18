# Exhibit C — what is green, and what is not, at `73cdbbc4`

Every block is byte-exact output of the stated command against the stated file
or revision. Prose between blocks names the source and adds no argument.

## C1. The round-3 seat's own six-module suite result

Source: `02d-seat-Q-round-3-report.md:12` — the `verification` array of the
seat's report envelope (V1 suite, V2 compileall, V3 generator `--check`, V4
mutants, V5 diffstat, V6 new-test profile), reproduced whole so no verification
is quoted apart from its siblings.

```
    12	  "verification": [{"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate tests.test_quiet_admission tests.test_night_plan_writer tests.test_arm_retry tests.test_run_night tests.test_gen_derivation_night 2>&1 | tail -4","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 341 tests in 69.093s","","OK (skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"(?s)Ran 341 tests.*OK \\(skipped=9\\)"}},{"id":"V2","kind":"build","cmd":"PYTHONPYCACHEPREFIX=/tmp/jw-compile python3 -m compileall -q scripts joulewise; echo rc=$?","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["rc=0"]},"expected":{"exit_code":0,"tail_regex":"rc=0"}},{"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check; echo rc=$?","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS generated derivation-night wrapper region matches","rc=0"]},"expected":{"exit_code":0,"tail_regex":"(?s)PASS.*rc=0"}},{"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/jw-r3-mutants.py > /tmp/jw-r3-mutants-final.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},{"id":"V5","kind":"inspection","cmd":"git diff --stat\ngit status --short","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[" docs/contracts/night_quiet_admission.md |  75 ++-"," joulewise/night_gate.py                 |  10 +"," joulewise/quiet_admission.py            |  71 ++-"," scripts/run_night.py                    | 867 +++++++++++++++++++++++---------"," tests/test_quiet_admission.py           |  34 +-"," tests/test_run_night.py                 | 327 ++++++++----"," 6 files changed, 1044 insertions(+), 340 deletions(-)"," M docs/contracts/night_quiet_admission.md"," M joulewise/night_gate.py"," M joulewise/quiet_admission.py"," M scripts/run_night.py"," M tests/test_quiet_admission.py"," M tests/test_run_night.py","?? tests/night_gate_fixtures/bind_supervision.py"]},"expected":{"exit_code":0,"tail_regex":"(?s)6 files changed.*bind_supervision.py"}},{"id":"V6","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/jw-r3-profile.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 18 tests in 15.782s","","OK","maximum_new_test_s=2.698 tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go"]},"expected":{"exit_code":0,"tail_regex":"(?s)Ran 18 tests.*OK.*maximum_new_test_s=2\\."}}],
```

The delta re-audit re-ran the same six modules on its own interpreter and did
NOT reproduce that green result; its `V1` and its environment flag are in
exhibit A §A5 (`Ran 341 tests in 171.428s`, `FAILED (failures=2, skipped=9)`,
flag `G1`: "Both heads share Python-path failures; canonical interpreter passes
2/2"). Both records are before the judge; neither is endorsed here.

## C2. The full repository replay — on the PRIOR head `5c5a3323`, not on `73cdbbc4`

Source: `17-full-replay-5c5a3323.log`, the shard and worker summary lines,
extracted with `grep -n "SHARD SUMMARY\|WORKERS SUMMARY"`:

```
2568:SHARD SUMMARY index=1/4 modules=59 tests=1694 failures=0 errors=0 skipped=6 result=PASS
4689:SHARD SUMMARY index=2/4 modules=59 tests=1525 failures=0 errors=0 skipped=16 result=PASS
7540:SHARD SUMMARY index=3/4 modules=61 tests=1972 failures=0 errors=0 skipped=6 result=PASS
9334:SHARD SUMMARY index=4/4 modules=59 tests=1211 failures=0 errors=0 skipped=81 result=PASS
9335:WORKERS SUMMARY shards=4 modules=238 tests=6402 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
```

There is no equivalent replay record for `73cdbbc4`. The file that would hold
one exists and is EMPTY:

```
$ wc -c 21-full-replay-73cdbbc4.log
       0 21-full-replay-73cdbbc4.log
```

## C3. The generator self-check and the native live sampler

Generator `--check` at `73cdbbc4` is V3 of the seat envelope quoted in C1
(`PASS generated derivation-night wrapper region matches`, `rc=0`).

The sandboxes deny `top`/`sysctl`, so the sampler was run natively by the lead.
Source: `09-live-sampler-smoke-and-bench-fixes.md:21-29`, run 3 at head
`536fd4db` (a fix-round-1 head, NOT `73cdbbc4`):

```
    21	## Run 3 — head `536fd4db`, 20:39:36 PDT — PASS
    22	
    23	```
    24	{"busy_cores": 0.608, "host_busy_cores": 0.608, "load_avg_diagnostic": {"raw": "{ 2.09 1.94 1.92 }"},
    25	 "observer_cpu_s": 0.2475,
    26	 "top_consumers": [{"busy_cores": 0.0864, "command": ".../WindowServer", "observer": false, "pid": 417},
    27	                   {"busy_cores": 0.0794, "command": "claude", "observer": false, "pid": 2490},
    28	                   {"busy_cores": 0.0781, "command": ".../Terminal", "observer": false, "pid": 2461}]}
    29	```
```

The only record of a native sampler run at `73cdbbc4` itself is a clause inside
the delta-re-audit brief. Source: `22-brief-delta-reaudit-round-3.md:3`, final
sentence, quoted with the sentence that carries it:

```
skip the live sampler (denied in the sandbox; the lead ran it natively on this head: PASS, busy 0.55 core, whole-round `observer_cpu_s` 1.145).
```

That is the lead's own report inside a brief it wrote; it is not an artefact of
a reviewing session, and the delta re-audit recorded it as "Lead smoke PASS
supplied, not reproduced" (exhibit A §A5, `same_signature`).

## C4. The gate-side mechanism: what the two round-2 reviews traced clean

Source: `12-refuter-contract-astra.md:56-101` — the contract refuter's
`clause_trace` in full, all eleven items, at head `a2671902`. Items 3, 4 and 10
carry findings and are included with the rest so the trace is not cherry-picked:
item 4 carries F2 (boot-probe classification), item 10 carries F1 (first-use
definitions), item 11 carries F3 (the v2 rerun guard) and item 3 is clean.

```
    56	    "clause_trace": [
    57	      {
    58	        "item": 1,
    59	        "result": "traced, no finding in plan validation: exact seven policy keys; nonempty authority; known policy only; finite positive durations/count, nonnegative cutoff sentinel, integer-valued positive interval, integer count >=1, bind >= interval*count and window >= bind+runway. Generator derives the 7980 s minimum from constants. No environment override. Legacy parser branches remain equivalent; driver compatibility finding F3 is separate."
    60	      },
    61	      {
    62	        "item": 2,
    63	        "result": "traced, no finding: writer emits v4 only with explicit NightPlan.quiet_admission; otherwise removes the added dataclass field. Explicit generator authoring exclusively creates a new id/output. V2 fixture bytes and one-shot semantics tests pass; generator --check passes."
    64	      },
    65	      {
    66	        "item": 3,
    67	        "result": "traced, no finding: min(t0+B,E-R) converts once using driver-entry clocks; late starts consume B. Completion, dead-man, install-close and chain-environment functions are AST-identical. Existing E-based expressions remain unchanged. The added v4 shutdown argument anchors the same E+300 trigger to entry monotonic time, independent of GO."
    68	      },
    69	      {
    70	        "item": 4,
    71	        "result": "traced, finding F2. Static plan/window/age/head/chain/registration failures are terminal. Dynamic census hits, nonzero screensaver configuration, AC loss, thermal restriction, boot changes and clock rollback are terminal; malformed required observations are terminal. Display configuration is parsed without a new threshold; absent thermal-limit lines still pass. CPU excess alone yields WAIT. Census is fresh before/after intervals and before GO, with concurrent 30 s supervision; initial-census replay remains legacy-only."
    72	      },
    73	      {
    74	        "item": 5,
    75	        "result": "traced, no finding: busy=max(process,host), identity=(pid,lstart), union accounting and unaccounted exits, observer included/labeled without subtraction, second top sample only. Whole-diff grep found no added production daemon references or name exemptions. Load values/errors are diagnostic only."
    76	      },
    77	      {
    78	        "item": 6,
    79	        "result": "traced, no finding: v3 requires policy, deadlines/GO fields, sample counts, journal digest/count, attribution or unavailable reason, load diagnostic and literal admission_is_capture_evidence=false. Versioned validation preserves legacy reason membership and receipt shape. Base/head receipt-byte regression passes. Pack receipt contract contains exactly the two verbatim ruled insertions, with no removals or other additions."
    80	      },
    81	      {
    82	        "item": 7,
    83	        "result": "traced, no finding: bind_expired is registered in gate/driver registries, arm_retry, generated policy copies and handback table. Legacy receipt validation excludes it. Valid v2 load and non-CPU power/thermal failures retain not_quiet; bind expiry uses the distinct code."
    84	      },
    85	      {
    86	        "item": 8,
    87	        "result": "traced, no finding: D-182 route checks matching terminal machine-state refusal, explicit no-start/no-reservation/no-session/no-writer/empty-inventory evidence, courier.sent, unused successor count, new id/digest, fresh notice, >=60 s after terminal write, successor install close and inherited NO veto. retry_allowed/classify_abort are AST-identical. Changed digest is rejected in same-candidate history. Both generated copies equal render_policy; D-182/R1 and ten-minute corrections are present."
    88	      },
    89	      {
    90	        "item": 9,
    91	        "result": "traced, no finding: whole-diff grep with AST test-body exclusion found only numeric busy_core_max=0.0 outside test bodies, in the contract example and shared test policy; both carry TEST-ONLY-NOT-A-RULING. Nonzero GO thresholds are injected inside tests. Document arithmetic examples are explicitly rejected calculations, as fix item 1 requires."
    92	      },
    93	      {
    94	        "item": 10,
    95	        "result": "traced, finding F1. Otherwise the document builds accounting, supervision, journal/receipt and successor mechanisms. It uses 480 s, approximately 1 J/5 J bars, identifies provisional parameters and ruling ownership, and computes timing correctly: 9600-187=9413 s; E=18:10, completion=18:15, dead-man=19:15."
    96	      },
    97	      {
    98	        "item": 11,
    99	        "result": "traced, findings F3 and F2. No measurement/instrument/claim constant changed: existing module-constant changes are confined to reason registries, retry descriptions and the journal record guard. Pre-registration and chain files have no diff. Pinned receipt-contract changes are exactly the ruled exception."
   100	      }
   101	    ]
```

That refuter's own suite run was not green either; its blocking flag `G1`,
`12-refuter-contract-astra.md:117-121`:

```
   113	      },
   114	      "expected": {"exit_code": 0, "tail_regex": "OK"}
   115	    },
   116	    {
   117	      "id": "V2",
   118	      "kind": "test",
   119	      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_quiet_admission tests.test_night_gate.QuietGatePhaseTests tests.test_arm_retry.ZeroCaptureSuccessorTests tests.test_arm_retry.ArmRetryTests.test_both_document_blocks_are_exact tests.test_arm_retry.ArmRetryTests.test_every_cold_assignment_is_explicit",
   120	      "cwd": ".",
   121	      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 18 tests in 0.084s", "", "OK"]},
   122	      "expected": {"exit_code": 0, "tail_regex": "OK"}
   123	    },
```

Source: `16-delta-reaudit-astra.md:40-58` — the delta re-audit's disposition
table, which is where each of those findings was checked as landed at
`5c5a3323`. Reproduced whole, including the E-F6 row that was NOT clean.

```
    40	    "disposition_table": {
    41	      "columns": ["ID", "landed", "mutant killed", "notes"],
    42	      "rows": [
    43	        ["C-F1", "observed", "N/A: line inspection", "nl -ba definition<first-use: t0 13<15; GO 14<159; bind 15<70; interval 16<71; consecutive 17<72; busy-core 18<46; observer 19<27; terminal/WAIT 20<143; attribution 21<49; cutoff authority 22<31. All ten pass."],
    44	        ["C-F2", "observed", "yes", "Disabled strict v4 checking: four failures, night_refused_boot_clock instead of night_probe_error. Cases include failed/empty, failed/UUID, successful/empty and whitespace. Leaking strict mode into v2 also fails the legacy comparison."],
    45	        ["C-F3", "observed", "yes", "Tuple regression plus v2 journal counterexample kill restored legacy contamination: FAILED (failures=2). Separate always-quiet guard and missing v4 guard mutants also killed."],
    46	        ["E-F1", "observed", "yes, 11/11", "Named regression kills individual exemptions for all ten daemons and arbitrary-program. Observed assertions include process_busy_cores 0 != 0.9."],
    47	        ["E-F2", "observed", "yes", "Named regression fails both stale-percent cases: high percent/zero delta and zero percent/27 CPU-second delta. FAILED (failures=2)."],
    48	        ["E-F3", "observed", "yes", "parse_ps pid-only identity mutant fails the named regression: 42 differs from (42, 'Thu Sep 17 19:00:00 2026')."],
    49	        ["E-F4", "observed", "yes", "Named regression exercises downstream GO +0 and real bind GO +540; E=t0+9600, completion/courier/shutdown=t0+9900, dead-man=t0+13500. Three samples retain deadline 1600. GO-t0 rewrite fails 10440 != 9900; deadline-reset and rollback-extension mutants fail expected expiry classification."],
    50	        ["E-F5", "observed", "yes, both", "Inside regression 9, removing predecessor-digest checking yields allowed instead of predecessor_rearm; removing history-digest checking yields allowed instead of candidate_changed."],
    51	        ["E-F6", "partial; F1", "yes for named ready/join mutant", "Real pre-send hung worker regression passes: ready under 50 ms, census during hang, expiry and no zombie. Blocking join mutant fails the 50 ms assertion. Partial-message hang remains uncovered and blocks the supervisor."],
    52	        ["E-F7", "observed", "yes", "Complete build_spec fixtures kill window and computed-runway bypasses. Authoring tests kill silent window extension and short-runway acceptance. Failures are GenerationRefusal not raised, not incomplete-fixture exceptions."]
    53	      ]
    54	    },
    55	    "compatibility": {
    56	      "six_module_counts_before_after": {
    57	        "night_gate": [63, 64],
    58	        "quiet_admission": [9, 10],
```

## C5. The files the lane touches, by area

From exhibit D's `git diff --stat a90ab4e8 73cdbbc4`, the same list split by the
area the packet's Q3 proposes to split on. This grouping is the assembler's,
the file names and line counts are not:

- Gate-side mechanism: `joulewise/night_gate.py`, `joulewise/quiet_admission.py`,
  `joulewise/night_plan_writer.py`, `joulewise/arm_retry.py`,
  `scripts/gen_derivation_night.py`, `docs/contracts/night_quiet_admission.md`,
  `docs/contracts/pack_night_go_receipt.md`,
  `docs/phase_2/derivation_night_runbook.md`, `docs/process/NIGHT_HANDBACK.md`,
  `docs/process/state_kernel.json`, and their tests
  (`tests/test_night_gate.py`, `tests/test_quiet_admission.py`,
  `tests/test_night_plan_writer.py`, `tests/test_arm_retry.py`,
  `tests/test_gen_derivation_night.py`, `tests/test_gen_state.py`,
  `tests/night_gate_fixtures/legacy_plan_v2.json`).
- The contested seam: `scripts/run_night.py` (+727 over the lane, of which the
  round-3 delta is one 669-line hunk), `tests/test_run_night.py`,
  `tests/night_gate_fixtures/bind_supervision.py`.

## C6. The sampling CLI Q5 names, as it exists at `73cdbbc4`

Source: `git show 73cdbbc4:joulewise/quiet_admission.py | nl -ba | sed -n
'296,343p'`, run in `/Users/edr/code/JouleWise-wt-gate-quiet`. Q5 asks about
`python -m joulewise.quiet_admission --observation`; this is what that flag
does, and what the flagless mode does:

```
   296	
   297	
   298	def publish_observation(descriptor, job_id, call):
   299	    """Worker-only blocking publication, with a capped JSON envelope."""
   300	    prepare_result_descriptor(descriptor)
   301	    limit = 256 * 1024
   302	    try:
   303	        value = dict(job_id=job_id, ok=True, result=call())
   304	        payload = json.dumps(value, allow_nan=False, separators=(',', ':')).encode()
   305	        if len(payload) > limit:
   306	            raise ValueError('serialized binding payload exceeds 256 KiB cap')
   307	    except BaseException as error:
   308	        payload = json.dumps(dict(job_id=job_id, ok=False,
   309	            error=f'{type(error).__name__}: {error}'[:4096]), separators=(',', ':')).encode()
   310	    frame = len(payload).to_bytes(4, 'big') + payload
   311	    try:
   312	        offset = 0
   313	        while offset < len(frame):
   314	            offset += os.write(descriptor, frame[offset:])
   315	    finally:
   316	        os.close(descriptor)
   317	
   318	
   319	def main(argv=None):
   320	    import argparse
   321	    parser = argparse.ArgumentParser(description=__doc__)
   322	    parser.add_argument('--sample-interval-s', type=float, required=True)
   323	    parser.add_argument('--observation', action='store_true')
   324	    parser.add_argument('--observer-pid', type=int)
   325	    parser.add_argument('--job-id')
   326	    parser.add_argument('--result-fd', type=int)
   327	    args = parser.parse_args(argv)
   328	    top_argv(args.sample_interval_s)
   329	    if args.observation:
   330	        if args.job_id is None or args.result_fd is None:
   331	            parser.error('--observation requires --job-id and --result-fd')
   332	        prepare_result_descriptor(args.result_fd)
   333	        publish_observation(args.result_fd, args.job_id, lambda: sample_interval(
   334	            args.sample_interval_s, observer_pid=args.observer_pid))
   335	    else:
   336	        from scripts.run_night import smoke_observation_round
   337	        observation, cost = smoke_observation_round(args.sample_interval_s)
   338	        print(json.dumps(smoke_metrics(observation, cost), sort_keys=True, allow_nan=False))
   339	    return 0
   340	
   341	
   342	if __name__ == '__main__':
   343	    raise SystemExit(main())
```

Two facts on these lines bear on Q5 and the judge should verify them: line
330-331 makes `--observation` require `--job-id` and `--result-fd` and write a
framed envelope to a descriptor rather than print, and line 336 makes the
flagless printing mode import `smoke_observation_round` from
`scripts.run_night` — the module Q3 proposes to exclude from PR 1.
