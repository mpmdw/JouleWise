```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "F1/F2/F4 fixed; active census RED to GREEN and producer-label kill proven; separate legacy allowlist needs scope and F3 era binding needs ruling.",
  "workspace": {
    "base_requested": "64547f31",
    "base_mode": "exact",
    "head_start": "64547f3185388f150b04934a6fb809c79511eea3",
    "head_end": "64547f3185388f150b04934a6fb809c79511eea3",
    "upstream_end": "64547f3185388f150b04934a6fb809c79511eea3",
    "branch": "feat/2026-09-05-d165-relabel"
  },
  "pathspec": [
    "joulewise/dominance_closeout.py",
    "docs/paper/round7/fill-checklist.md",
    "docs/campaign_packs/d117_contrast_v5.md",
    "tests/test_d165_dominance_closeout.py",
    "tests/test_d165_rationale_census.py",
    "docs/process_traces/2026-09-05-d165-relabel/08-fix-round-4-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 50 tests in 10.998s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_rationale_census",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "docs/campaign_packs/d117_contrast_v5.md:138: uniform shared fiducial shift cancels",
          "docs/campaign_packs/d117_contrast_v5.md:139: cancels exactly",
          "docs/campaign_packs/d117_contrast_v5.md:139: shared fiducial shift",
          "docs/paper/round7/fill-checklist.md:61: deviations-from-mean cancellation",
          "joulewise/dominance_closeout.py:57: cancels exactly",
          "joulewise/dominance_closeout.py:57: shared fiducial shift",
          "joulewise/dominance_closeout.py:57: uniform shared fiducial shift cancels",
          "Ran 4 tests in 17.998s",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 51 tests in 11.172s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport unittest\nfrom unittest import mock\nfrom joulewise import dominance_closeout as core\nname = 'tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_production_builder_emits_v2_rule_and_ratified_absolute_reason'\nsuite = unittest.defaultTestLoader.loadTestsFromName(name)\nwith mock.patch.object(core, 'COMMON_MODE_REPLAY_RULE_ID', core.LEGACY_COMMON_MODE_REPLAY_RULE_ID):\n    result = unittest.TextTestRunner().run(suite)\nraise SystemExit(not result.wasSuccessful())\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 'd165_shared_sign_local_corner_replay.v1' != 'd165_shared_sign_local_corner_replay.v2'",
          "Ran 1 test in 1.670s",
          "FAILED (failures=4)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=4\\)"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_rationale_census -v",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "test_no_active_retired_rationale_in_tracked_consumers (tests.test_d165_rationale_census.D165RationaleCensusTests.test_no_active_retired_rationale_in_tracked_consumers) ... ok",
          "AssertionError: False is not true : Required legacy allowlist missing: tests/fixtures/d165_rationale_legacy_allowlist.json",
          "Ran 4 tests in 3.261s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_rationale_census.D165RationaleCensusTests.test_no_active_retired_rationale_in_tracked_consumers",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 3.263s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check",
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
  "flags": [
    {
      "id": "S1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: requested separate legacy allowlist has no authorized path. It was not created. Census deliberately fails its missing-ledger check; no out-of-scope writes occurred.",
      "needs": "Authorize tests/fixtures/d165_rationale_legacy_allowlist.json; proposed four exact entries are below."
    },
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: F3 cannot bind production era under the existing closed three-field schema. Both current v2 output and historical v1 use joulewise.d165_dominance_replay.v1; no independent era declaration exists. Validator was preserved.",
      "needs": "Specify authoritative era declaration, absent-declaration policy and historical-read route; authorize the sidecar contract amendment. Producer regression and its kill are complete."
    },
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The active-text assertion is GREEN, but the complete census module is not GREEN and F3 validation is not fixed.",
      "needs": "Resume after scope/ruling, complete the ledger and validator regression/kill, then run the two named modules sequentially."
    },
    {
      "id": "M1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Paper-K owns draft-v2-skeleton.md and results-fill-registry.md; both preserved. Binding review reports a registry merge conflict against 3d1ab23b.",
      "needs": "Merge author must reconcile the eight R_cm rows and rationale paragraph manually as described below; run paper-K checks in its own authorized lane."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/fixtures/d165_rationale_legacy_allowlist.json",
      "docs/contracts/d165_dominance_closeout.md"
    ],
    "reason": "The requested separate occurrence allowlist and a binding sidecar-era declaration are absent from the exhaustive WRITE_SCOPE.",
    "blocked_work": "Complete census GREEN; F3 validator-era binding and its rejection regression/kill.",
    "minimal_change": "Add the four reasoned JSON occurrences below. Amend only the replay sidecar era/compatibility rows after the lead rules; implementation and tests can then resume in the already authorized Python files."
  }
}
```

## Change

F1: the checklist instruction and all four absolute R_cm rows now reproduce the registered rationale. F2: the campaign pack uses the registered absolute rationale and describes one shared additive energy sign, independent local corners, and no proven common-time conservatism. Thresholds and withdrawal remain unchanged. F4: the replay docstring again says what the function does; the test checks only the shared-energy-sign label.

The new census enumerates all 2,254 tracked files in the five required roots with `git ls-files -z`. It excludes the frozen draft-v1 and process traces, skips binary contents, folds prose whitespace, and decodes Python literals through AST so split strings cannot hide phrases. Its module docstring documents bounded line, paragraph and explicit block markers. Parser regressions check wrapped phrases and marker boundaries. The historical constant now has an explicit LEGACY v1 block without changing its value.

F3 is partial: a new test exercises the production sidecar builder and requires literal v2 output and the ratified reason for every cell. A process-local mutation of COMMON_MODE_REPLAY_RULE_ID to v1 kills that test in all four cells. This is producer evidence, not a validator cure. Direct inspection still produced `F3_v2_sidecar_with_one_v1_result_errors: []` after replacing just the first comparative result rule with v1.

## Verification notes

Only the two authorized test modules were used, sequentially, with bytecode writing disabled. No discovery suite, agent launcher, hardware collection, commit, or out-of-scope write was performed. V2 is the before-fix failure; it also includes the deliberate missing-ledger failure. V4 is an expected mutation kill. V5 remains a real incomplete-acceptance failure. V6 proves only the active-text component GREEN.

Before F1/F2, exact RED tail excerpt:

```text
docs/campaign_packs/d117_contrast_v5.md:138: uniform shared fiducial shift cancels
docs/campaign_packs/d117_contrast_v5.md:139: cancels exactly
docs/campaign_packs/d117_contrast_v5.md:139: shared fiducial shift
docs/paper/round7/fill-checklist.md:61: deviations-from-mean cancellation
joulewise/dominance_closeout.py:57: cancels exactly
joulewise/dominance_closeout.py:57: shared fiducial shift
joulewise/dominance_closeout.py:57: uniform shared fiducial shift cancels

----------------------------------------------------------------------
Ran 4 tests in 17.998s

FAILED (failures=2)
```

After F1/F2 and the explicit legacy marker, exact GREEN tail for the active-text test (V6):

```text
.
----------------------------------------------------------------------
Ran 1 test in 3.263s

OK
```

The final complete census module still ends:

```text
AssertionError: False is not true : Required legacy allowlist missing: tests/fixtures/d165_rationale_legacy_allowlist.json

----------------------------------------------------------------------
Ran 4 tests in 3.261s

FAILED (failures=1)
```

NEEDS_SCOPE: the separate allowlist cannot be written under the supplied allowlist. The following is the concrete proposed content for `tests/fixtures/d165_rationale_legacy_allowlist.json`, not an applied file:

```text
[
  {
    "path": "docs/paper/round7/structural-edits.md",
    "line": 84,
    "phrase": "cancels exactly",
    "reason": "Historical insertion paragraph explicitly SUPERSEDED by the preceding 2026-09-05 banner; retained for custody, not active paper text."
  },
  {
    "path": "joulewise/dominance_closeout.py",
    "line": 59,
    "phrase": "cancels exactly",
    "reason": "Exact LEGACY v1 reason bytes retained only for reading pre-relabel artifacts, inside an explicit LEGACY v1 block."
  },
  {
    "path": "joulewise/dominance_closeout.py",
    "line": 59,
    "phrase": "shared fiducial shift",
    "reason": "Exact LEGACY v1 reason bytes retained only for reading pre-relabel artifacts, inside an explicit LEGACY v1 block."
  },
  {
    "path": "joulewise/dominance_closeout.py",
    "line": 59,
    "phrase": "uniform shared fiducial shift cancels",
    "reason": "Exact LEGACY v1 reason bytes retained only for reading pre-relabel artifacts, inside an explicit LEGACY v1 block."
  }
]
```

NEEDS_RULING question: what independent artifact declaration establishes the v1 era, and how must undeclared historical bytes be read? The current contract at lines 108-116 permits exactly schema_version, sidecar_id and cells. The schema version is identical for current and historical output. Options considered: (1) prospectively version the sidecar schema and bind each era to its rule/reason pair; (2) add a separately specified production-era field and rule for its absence; (3) obtain era from authenticated enclosing artifact context. Recommendation: explicitly register the era declaration and historical-read policy in the sidecar contract before changing validation; a prospective schema discriminator gives new output a direct artifact declaration, but the already-created v2-labelled/v1-schema fixtures also need a disposition. Inferring era from the supplied result rule would repeat F3. The validator fix and corresponding refusal kill are blocked on this decision.

## Residual risk

Paper-K merge author: the binding review reports a content conflict in `docs/paper/results-fill-registry.md` against paper-K 3d1ab23b. Preserve the relabel branch's active v2 rationale paragraph and eight R_cm rows, remove paper-K's now-false `SUPPLIER_PENDING: the producer emits .v1 until the D-165 relabel lands` clauses, and retain paper-K's nonoverlapping edits. Do not resolve by choosing an entire side. The frozen registration reason must remain verbatim for the applicable absolute rows. `docs/paper/draft-v2-skeleton.md` is also paper-K-owned; this session found no banned-phrase census conflict there and changed neither file. This is the binding review's merge guidance, not a newly executed merge-tree result. The merge author owns its requested paper-term and first-use-ledger checks; this seat did not run them.

Next exact step: lead returns expanded scope for the JSON ledger and contract, plus the F3 era ruling. Resume this uncommitted tree, complete the validator and ledger, and rerun the two named modules one at a time. No full-census GREEN or F3 acceptance is claimed.
