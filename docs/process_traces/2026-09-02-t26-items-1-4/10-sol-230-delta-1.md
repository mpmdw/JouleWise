```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "B1-B4 mechanisms pass all dictated mutations, but the evidence citation permits paths outside HEAD and kernel acceptance text contradicts the singular ruled B2 dependency.",
  "workspace": {
    "base_requested": "2d24ef70..1d254bb1; d243445d..d8451daa",
    "base_mode": "exact",
    "head_start": "d8451daacad2ec685a1b88e4bfe28d1f6d90d82f",
    "head_end": "d8451daacad2ec685a1b88e4bfe28d1f6d90d82f",
    "upstream_end": "d8451daacad2ec685a1b88e4bfe28d1f6d90d82f",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "classification": "test-gap",
        "file_line": "tests/test_docs_freshness.py:146-149",
        "summary": "An absolute citation to a file outside the repository satisfies the B1 code-path branch even though that path cannot exist at HEAD.",
        "counterfactual": "A TMPDIR outside.py file cited by absolute path returned True from _has_executed_evidence."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "classification": "kernel-state",
        "file_line": "docs/process/state_kernel.json:4477,4490-4499",
        "summary": "The installer has the one B2 dependency dictated by the ruling, while its acceptance text still requires four D-170 dependencies on that row.",
        "counterfactual": "Satisfying the singular ruled dependency would still leave acceptance[4] literally requiring three nonexistent dependencies."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_gen_state tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 65 tests in 1.962s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 65 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 scripts/gen_state.py --check; echo EXIT=$?",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^EXIT=0$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_docs_freshness.DocsFreshnessTests.test_executed_evidence_mutations_are_rejected tests.test_docs_freshness.DocsFreshnessTests.test_dated_ruling_selector_scans_all_depths_and_excludes_needs_ruling tests.test_docs_freshness.DocsFreshnessTests.test_open_decision_counterfactuals_bind_all_installation_limbs tests.test_docs_freshness.DocsFreshnessTests.test_malformed_decision_index_status_is_not_skipped tests.test_docs_freshness.DocsFreshnessTests.test_terminal_decision_counterfactuals tests.test_docs_freshness.DocsFreshnessTests.test_dangling_decision_reference_mutation_is_rejected tests.test_gen_state.TestKernelValidity.test_satisfied_decision_dependency_requires_named_test_regression tests.test_docs_freshness.DocsFreshnessTests.test_bridge_protocol_clause_map_s2_rewrap_passes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 8 tests in 0.033s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'import re; p=re.compile(r\"(?<![0-9A-Za-z])D-\\d{3}[a-z]?(?![0-9A-Za-z])\"); [print(repr(s), \"->\", p.findall(s)) for s in (\"D-170\",\"D-170a\",\"(D-170)\",\"D-170.\",\"D-170/D-171\",\"D-170:\",\"B09C8BDD-187C-4740\")]'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "'D-170' -> ['D-170']",
          "'D-170a' -> ['D-170a']",
          "'(D-170)' -> ['D-170']",
          "'D-170.' -> ['D-170']",
          "'D-170/D-171' -> ['D-170', 'D-171']",
          "'D-170:' -> ['D-170']",
          "'B09C8BDD-187C-4740' -> []"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "B09C8BDD-187C-4740.*\\[\\]"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --porcelain",
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

### F1 — SHOULD-FIX — B1 citation path can escape the repository

[tests/test_docs_freshness.py](/Users/edr/code/JouleWise-wt-t26-a2/tests/test_docs_freshness.py:146) extracts a syntactically matching path and tests `(root / path).is_file()` without rejecting absolute paths or `..`. For an absolute path, `Path` discards `root`.

Counterfactual:

```text
absolute non-HEAD citation accepted: True
absolute path: $TMPDIR/t26-absolute.../outside.py
```

Thus `See /outside/repository/outside.py:1` satisfies branch 2 despite not existing at repository HEAD. Require a repo-relative POSIX path with no escape components before checking existence.

### F2 — SHOULD-FIX — B2 acceptance count contradicts the ruled object

[state_kernel.json](/Users/edr/code/JouleWise-wt-t26-a2/docs/process/state_kernel.json:4477) says “each of the four D-170 dependencies on this row” must become satisfied. The live row contains exactly one dependency at [state_kernel.json](/Users/edr/code/JouleWise-wt-t26-a2/docs/process/state_kernel.json:4490), matching the singular object dictated by B2.

Observed:

```text
D-170 dependencies on installer: 1
acceptance[4]: each of the four D-170 dependencies on this row moved to satisfied...
dependency required: the four T26 verdict mechanisms are installed...
```

Change the acceptance sentence to refer to the singular D-170 dependency covering all four mechanisms.

## Clause audit

| Clause | Status | Production and biting test | Counterfactual |
|---|---|---|---|
| B1 | PARTIAL — F1 | Selectors/evidence predicate `tests/test_docs_freshness.py:43-47,107-166`; real-set test `:615-637`; mutations `:695-787` | M7, M8, `$ echo exit`, `.md:48`, nonexistent path, and both-depth empty rulings rejected; `gen_state.py:63` accepted; `NEEDS-RULING-*` excluded. Absolute-path escape survives. |
| B2 | INSTALLED | Floor `:31`; four limbs `:339-392`; installer object `state_kernel.json:4490-4499`; counterfactuals `:552-613` | M4 → limb 2; only-V5 → limb 2; missing-start → limb 3; M13 → limb 4. Live kernel passes. |
| B3 | INSTALLED | Status union `:32-41`; terminal enforcement `:394-425`; controls `:518-550` | M6c and unknown `decided` killed. |
| B4 | INSTALLED | Exhaustive document set and boundary regex `:195-235`; live/dangling tests `:789-805` | D-999 killed; live dangling set empty; UUID rejected without an allowlist. |

Ruled values did not move: `DECISION_RULE_FLOOR = 170`; selector cutoffs remain `2026-08-29` and `2026-09-03`; the B2 object is canonical-JSON byte-equal to the dictated shape.

The real B1 set is exactly:

```text
docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md True
docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md True
```

Evidence is supplied by command/status pairs at coldgate lines `45`/`52` and process-rules lines `134`/`148`.

B2/B3 details:

```text
live B2 limbs: PASS
B2 object byte-equal: True
only-V5 D-170 carriers: ['V5-TRANSACTION-01']
only-V5: KILLED ... limb 2
M6c all pending D-170 carriers:
['T26-RULING-INSTALL-01', 'V5-TRANSACTION-01']
M6c method report: ... task T26-RULING-INSTALL-01
```

`_assert_terminal_decisions` reports only the first carrier because it fails immediately. B3 requires the message to name the status and a task; it does not require an exhaustive carrier list.

`D110-MINT-DEP-RECONCILE-01` has the only global rank `20`; its acceptance pointer, decision-log authority, and coldgate fence authority all exist. Its fence preserves the explicit below-floor inconsistency and does not contradict B3.

## Mutation outcomes

- M7, M8, `$ echo exit`, `.md:48`, nonexistent citation: KILLED by `test_executed_evidence_mutations_are_rejected`.
- `scripts/gen_state.py:63`: positive control PASSED.
- Both selector depths: selected and KILLED; `NEEDS-RULING-*`: excluded.
- M4: KILLED at limb 2.
- Only V5: KILLED at limb 2 on exactly the input with the installer dependency stripped.
- Missing start: KILLED at limb 3.
- M13: KILLED at limb 4 (`171 != 172`).
- M6c and unknown `decided`: KILLED by terminal-decision enforcement.
- D-999: KILLED by the dangling-reference scan.
- M6b: KILLED by the satisfied-decision rule.
- Own probes: nonexistent test label, path outside `tests/`, and anchor-without-path all KILLED. A valid named regression PASSED.
- S2 rewrap: PASSED after normalization.

Regex probe:

```text
'D-170' -> ['D-170']
'D-170a' -> ['D-170a']
'(D-170)' -> ['D-170']
'D-170.' -> ['D-170']
'D-170/D-171' -> ['D-170', 'D-171']
'D-170:' -> ['D-170']
'B09C8BDD-187C-4740' -> []
```

The exact UUID remains in the live scanned corpus at `docs/strategy/2026-08-07-paper-portfolio/proposals/prop-tokenizer-honesty.md:4438`, so its exclusion is regression-pinned by `test_decision_references_resolve`.

## Same-signature

First delta re-audit on this landing.

- F1: test-gap.
- F2: kernel-state.
- No documentation-consistency-only finding.
- No ruled floor, dependency shape, or selector date moved.

## Executed evidence

```text
$ python3 -m unittest tests.test_gen_state tests.test_docs_freshness
Ran 65 tests in 1.962s
OK
EXIT=0

$ python3 scripts/gen_state.py --check; echo EXIT=$?
EXIT=0

$ python3 -m unittest -v <eight named mutation tests>
Ran 8 tests in 0.033s
OK
EXIT=0

$ python3 - <<'PY'  # initial B1/B4 probe, over-escaped regex
AttributeError: 'NoneType' object has no attribute 'group'
EXIT=1

$ python3 - <<'PY'  # corrected B1/B4 selector/evidence/regex probe
M7 real ruling heading deleted: False
M8 real ruling exit + .md citation deleted: False
selector positives: [root-depth, archive-depth]
NEEDS excluded: True
EXIT=0

$ python3 - <<'PY'  # B2/B3/D-999 probe
live B2 limbs: PASS
B2 object byte-equal: True
live dangling refs: []
EXIT=0

$ python3 - <<'PY'  # gen_state own probes, D110, absolute-citation probe
M6b/OWN-A/OWN-B/OWN-C: KILLED
valid named regression: PASS
absolute non-HEAD citation accepted: True
EXIT=0

$ git diff --check
(no output)
EXIT=0
```

## Residual risk

B1 remains a deliberately shape-only check: even after F1 is cured, it does not prove that an execution transcript is truthful. No canonical discovery suite was run, per the explicit audit prohibition.

VERDICT: SHOULD-FIX 2

```text
$ git status --porcelain
(no output)
EXIT=0
```