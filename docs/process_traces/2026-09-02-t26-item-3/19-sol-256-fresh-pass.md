# Sol 256 (gpt-5.6-sol, high, read-only workspace-write with empty scope) — operation-loop §5 fresh pass over `7488a3c0`

Custodied verbatim from the seat's report (scratchpad paths redacted). Brief: `fresh-t26b-256.md` (G1–G5). Disposition in file 20.

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The cures are test-green and the documentation corrections are coherent, but the census test is syntactic rather than semantic and the new empirical kernel route requires a receipt field no current producer or schema permits.",
  "workspace": {
    "base_requested": "c582120d3de14cb3e9694014a19117c60098cbcd",
    "base_mode": "exact",
    "head_start": "7488a3c085530feed240938e8a642a4210022bae",
    "head_end": "7488a3c085530feed240938e8a642a4210022bae",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 2,
      "nit": 0
    },
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "The census regression counts direct syntax, not the governed post-R1 probe call graph"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "The empirical kernel route requires a validity-origin field that current receipts cannot contain"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "build",
      "cmd": "mkdir -p <scratchpad>/tmp256/t26-review-gen && TMPDIR=<scratchpad>/tmp256/t26-review-gen python3 scripts/gen_state.py --check",
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
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "mkdir -p <scratchpad>/tmp256/t26-review-docs && TMPDIR=<scratchpad>/tmp256/t26-review-docs python3 -m unittest tests.test_gen_state tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".................................................................",
          "----------------------------------------------------------------------",
          "Ran 65 tests in 1.811s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 65 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "mkdir -p <scratchpad>/tmp256/t26-review-arm && TMPDIR=<scratchpad>/tmp256/t26-review-arm python3 -m unittest tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness tests.test_arm_readiness_schemas",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "......ss..............................................................................................",
          "----------------------------------------------------------------------",
          "Ran 149 tests in 192.964s",
          "",
          "OK (skipped=7)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 149 tests in .*s\\n\\nOK \\(skipped=7\\)"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch && git diff --no-ext-diff --exit-code",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical discovery suite was not run, as explicitly instructed.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — should_fix — The census regression counts direct syntax, not the governed post-R1 probe call graph

The current source really has eleven direct `_fresh_probe` call sites outside `_fresh_clock_reference_batch`, and the current production order makes them post-R1. However, [the test](/Users/edr/code/JouleWise-wt-t26-b2/tests/test_arm_readiness_evidence_t0.py:855) recognizes only calls whose callee is an `ast.Name` spelled exactly `_fresh_probe`. It neither follows aliases/wrappers nor proves reachability or ordering.

An in-memory mutant added this inside `_derive_power`:

```python
probe_alias = _fresh_probe
probe_alias(context, kind, "extra", ("/usr/bin/true",))
```

Executed result:

```text
base test census= (1, 11)
mutant test census= (1, 11)
mutant additional alias-mediated probe call lines= [1836]
all census assertions would still pass= True
```

The runtime would now have a twelfth governed probe call, making the ruled site arithmetic 12 × 45 + 105 = 645 seconds, while every census assertion and the 600-second constant remain green. Equivalent bypasses include a stored callback, `globals()["_fresh_probe"]`, or a method/lambda invoking an alias.

The test also counts every direct call outside the specially named R1 function, including an unreachable helper or a call moved before R1. A robust cure should pin the exact governed deriver/call-site inventory and prohibit or detect indirect `_fresh_probe` invocation.

### F2 — should_fix — The empirical kernel route requires a validity-origin field that current receipts cannot contain

The new acceptance text requires three real rehearsal receipts carrying both `r1_batch_finished_monotonic_ns` and `validity_origin_monotonic_ns` ([kernel line 4618](/Users/edr/code/JouleWise-wt-t26-b2/docs/process/state_kernel.json:4618)). No current producer emits the latter field:

- `_assemble_receipt` emits only `valid_until_monotonic_ns` ([author line 2016](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness_evidence_t0.py:2016)).
- `validity_origin` exists only transiently and is converted to `valid_until = validity_origin + horizon` ([author line 2338](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness_evidence_t0.py:2338)).
- The exact evidence-receipt key set omits `validity_origin_monotonic_ns`, and validation rejects extra keys ([schema line 487](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness.py:487)).
- Repository-wide search found the field name only in the new kernel row and generated queue.

Thus the `[QUIET-MAC]` row cannot satisfy empirical route A without an unregistered producer/schema change. The smallest correction is to accept the exactly recoverable origin, `valid_until_monotonic_ns − _validity_horizon_ns(kind)`, or register an agent-lane producer/schema prerequisite.

## G1 — Census test

(a) Literal clarification: `joulewise/arm_readiness.py` contains zero `_fresh_probe` calls; the test parses `t0.__file__`, meaning `joulewise/arm_readiness_evidence_t0.py`.

Independent AST census:

```text
1101: _fresh_clock_reference_batch
1216: _derive_clock_probe
1318: _maintenance_probe
1365: _thermal_probe
1723-1726: _derive_process_census
1801: _derive_powermetrics
1836-1838: _derive_power
total=12, R1=1, non-R1=11
```

Eleven is therefore the correct current direct-call-site count. The exclusion matches the current ruling semantics: `_EXPECTED_ROWS` puts `clock.correct_and_prior_state` first, its deriver performs `_fresh_clock_reference_batch`, and the remaining eleven sites belong to later derivers. F1 explains why the test itself does not enforce that semantic fact.

(b) Confirmed alias bypass above. Wrappers or dynamically obtained callables can likewise add governed invocations without changing the test census.

(c) The `105` in the assertion is a bare literal. The ruling describes it as an allowance for ungoverned filesystem/Git work, but there is no named constant or bounded calculation for the test to pin. Worse, §6.3.1 identifies 220 seconds of fixed Git ceilings alone and says no finite complete successful-path bound follows from the code. The test pins ruled arithmetic, not a justified runtime envelope.

## G2 — Ruling addendum and correction

The drift-envelope addendum changes only the metrology rationale. It does not change the 600-second number, inclusive `<=`, liveness/not-metrology label, or ordinary-monotonic clock typing.

The correction does contradict the original “cannot false-refuse a healthy night” sentence, but does so explicitly: it quotes that sentence, says it is contradicted, and withdraws that premise while retaining the verdict. I found no undisclosed contradiction with the still-standing item-3 text.

The GitHub slug for:

```text
Addendum 2026-09-02 — item 3 drift-envelope rationale
```

is:

```text
addendum-2026-09-02--item-3-drift-envelope-rationale
```

The link uses that exact slug, and `gen_state.py --check` passed. The path named in the question without `impl/` does not exist; the actual linking document is `docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md`.

## G3 — Kernel row and generated queue

Both requested checks passed:

```text
python3 scripts/gen_state.py --check
exit 0, no output

Ran 65 tests in 1.811s

OK
```

The refreshed fence correctly says that the 5-second bound was struck and replaced by the installed 600-second ordinary-monotonic liveness bound ([kernel line 4727](/Users/edr/code/JouleWise-wt-t26-b2/docs/process/state_kernel.json:4727)).

One literal “upper bound was deliberately NOT implemented” sentence remains in both the kernel status note and its generated `TASK_QUEUE.md` rendering. It is explicitly historical—“Before that ruling”—and immediately follows the bracketed 2026-09-02 replacement notice. Therefore it does not assert the current state. I found no unqualified current sentence retaining the 5-second bound or saying the replacement remains unimplemented.

The new row has the separate executability defect reported as F2.

## G4 — Code and fixture comments

The production comment is accurate as a classification and record of ruled provenance: the conjunct is an ordinary-monotonic liveness deadline, not a metrology bound, and the cited §6.3.1 discloses that it may false-refuse a healthy slow path. Its `11 × 45 + 105` statement is ruled arithmetic, not proof of a worst-case runtime envelope; G1(c) records that limitation.

The fixture comment is true:

```text
sample_arm.evidence = []
sample_arm.rows = []
```

I also patched `_clock_probe_predicate_passes` in memory to raise if invoked, then validated `sample_arm`:

```text
validate_result=<valid arm receipt>
clock_probe_calls=0
```

The call is reached only while evaluating a `clock.correct_and_prior_state.v1` fact whose source kind is `PROBE` ([dispatch line 6564](/Users/edr/code/JouleWise-wt-t26-b2/joulewise/arm_readiness.py:6564)). Since `sample_arm` has no evidence or rows ([fixture line 249](/Users/edr/code/JouleWise-wt-t26-b2/tests/test_arm_readiness_schemas.py:249)), its `10**30` deadline never reaches the liveness conjunct.

## G5 — Requested suite tail

```text
......ss..............................................................................................
----------------------------------------------------------------------
Ran 149 tests in 192.964s

OK (skipped=7)
```

## Residual risk

No real R1-finish-to-validity-origin interval has been measured. Static and fixture evidence cannot establish whether ordinary healthy rehearsals retain margin below 600 seconds.

## What this pass did NOT check

- It did not run `python3 -m unittest discover`.
- It performed no live T-0 rehearsal, hardware operation, or `[QUIET-MAC]` measurement.
- It did not read operation-loop briefs or transcripts.
- It did not re-audit settled prior rounds or review changes outside `c582120d..7488a3c0` except context needed for G1–G5.
- It made no checkout changes; start and end were detached at `7488a3c0` with a clean Git diff.