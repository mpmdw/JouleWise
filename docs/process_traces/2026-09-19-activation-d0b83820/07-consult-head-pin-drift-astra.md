```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a test-only fix: preserve the advancing committed pin and existing generator drift checks; test the baseline-prefix invariant already implemented by production (docs/decision_log.md:7511; joulewise/calibration_ledger.py:2614).",
  "workspace": {
    "base_requested": "2f79e633",
    "base_mode": "exact",
    "head_start": "2f79e633e205a81b01040e8c98d1e092f8d53a9e",
    "head_end": "2f79e633e205a81b01040e8c98d1e092f8d53a9e",
    "upstream_end": "2f79e633e205a81b01040e8c98d1e092f8d53a9e",
    "branch": "fix/2026-09-19-head-pin-test-drift"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "The acceptance test incorrectly equates an immutable issuance cutoff with the advancing current head.",
        "location": "tests/test_calibration_bracketing.py:635",
        "authority": "docs/decision_log.md:7511"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Shared-generator mechanics tests depend on a mutable operational input unrelated to their assertions.",
        "location": "tests/test_campaign_generator_core.py:103",
        "production_fence": "configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2504"
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "The same drift also breaks tests outside the quick tier, including the cited non-ledger drift regression before its intended mutation.",
        "locations": [
          "tests/test_arm_readiness_evidence_packauth.py:561",
          "tests/test_d117_floor_qwen3_v5_generate.py:774",
          "tests/test_d117_floor_qwen3_v5_generate.py:606"
        ]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_calibration_bracketing.CalibrationBracketingTests.test_live_issued_anchor_authenticates_and_matches_committed_head_pin tests.test_campaign_generator_core",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=1, errors=2)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_arm_readiness_evidence_packauth.ProjectedPackAuthenticationTests.test_external_pinned_input_drift_is_checked_in_derivation_mode tests.test_calibration_ledger.CalibrationLedgerTests.test_proper_prefix_of_pinned_head_refuses_as_rollback tests.test_calibration_ledger.CalibrationLedgerTests.test_unpinned_physical_extension_refuses_stale_head tests.test_calibration_ledger.CalibrationLedgerTests.test_baseline_must_be_exact_member_of_current_chain",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_floor_qwen3_v5_generate.D117FloorQwen3V5PackTests.test_contrast_references_resolve_to_matching_floor_plan_digests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python /tmp/pinfix-design-probe.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=2)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python /tmp/pinfix-focused-probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 10 tests in 8.440s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "rg -l 'LEDGER_HEAD_FILE_SHA256' configs/campaigns --glob generate_configs.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py",
          "configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py",
          "configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py",
          "configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py",
          "configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "generate_configs\\.py"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --short --branch && git log -1 --format='%H'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## fix/2026-09-19-head-pin-test-drift...origin/main",
          "2f79e633e205a81b01040e8c98d1e092f8d53a9e"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "2f79e633e205a81b01040e8c98d1e092f8d53a9e"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only consult completed. Proposed test changes were exercised through /tmp probes; no repository patch, full quick-tier run, canonical suite, hosted-CI query, or physical-ledger verification was performed.",
      "needs": "Lead implements and verifies the exact candidate; do not describe scratch results as main or hardware validation."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A two-file quick-tier repair does not repair the independently reproduced heavier-test failures at tests/test_arm_readiness_evidence_packauth.py:561 and tests/test_d117_floor_qwen3_v5_generate.py:606.",
      "needs": "Carry explicit dispositions for these failures; use physical fixture inputs for subprocess tests."
    }
  ]
}
```

## Findings

**Recommendation:** keep the committed pin advancing, preserve generator drift refusal, and repair the tests. Production already implements the required prefix relationship. I agree with Q1(b) and fixture isolation; I disagree with redefining the existing generator file hash as the acceptance cutoff in this fix. The governing distinction is explicit in `docs/decision_log.md:7511`, and the current generator checks exact file bytes at `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2504`.

**F1 — Q1: the invariant is an authenticated prefix, not equality.**

For cutoff **C**, committed pin **P**, and physical ledger **L**, require:

- Matching ledger schema.
- `C.sequence <= P.sequence`.
- The chain digest at exactly `C.sequence` equals `C.head_digest`.
- The authenticated physical terminal head equals **P**, with the remaining completeness and custody checks passing.

D-109 R1.4 explicitly requires a complete, non-forked extension from the acceptance baseline to the independent current head (`docs/decision_log.md:7511`). R2.1 defines the issuance cutoff as an exact sequence/digest pair (`docs/decision_log.md:7537`). D-116 records **76 as the issuance-time head**, not a permanent maximum (`docs/decision_log.md:7992`). The append contract expressly permits reviewed, committed advancement (`docs/contracts/calibration_ledger_append.md:286`), and the runbook distinguishes the frozen registration baseline from subsequent terminal pins (`docs/phase_2/derivation_night_runbook.md:2792`).

**This requires no production correction:** `load_calibration_ledger_snapshot` checks physical-head equality at `joulewise/calibration_ledger.py:2609`, exact baseline membership at `:2623`, and rejects a baseline beyond the pinned sequence at `:2630`. V5 exercised those conditions against actual synthetic ledger bytes and a committed pin.

**CI cannot prove the actual 76→176 ancestry from the pin file alone.** Its three fields contain no intermediate chain records (`configs/calibration/calibration_ledger_head.json:1`). A sequence comparison is a necessary consistency check, not authentication.

To prove actual ancestry in CI, supply the canonical extension receipts from cutoff+1 through the current pin—or the complete ledger—and verify their sequence, predecessor and receipt hashes against both trusted endpoints. Receipt hashing is defined at `docs/contracts/calibration_ledger_append.md:98`. That witness can be a separate evidence input; it need not—and cannot prospectively—be embedded in the immutable acceptance for future appends. The existing contract requires evaluation-time chain verification, but prescribes no hosted-CI witness format (`docs/decision_log.md:7511`).

For this repair, explicitly separate:

1. Checked-in artifact authentication and head/cutoff consistency.
2. Synthetic tests proving the production chain-verification algorithm.
3. Lead-owned verification of the real physical ledger.

Do not rename a bare `<=` assertion “prefix authentication.”

**F2 — Q2 and Q5: retain generation-input byte identity; separate it from acceptance authority.**

`LEDGER_HEAD_FILE_SHA256` currently means **the exact head-pin file bytes captured for that generator’s generation inputs**. `LEDGER_HEAD_SHA256` is a different value, and acceptance identity/digests are separately pinned (`configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:191`, `:211`, `:2878`). Making the file hash mean the acceptance cutoff would change both the accepted inputs and the meaning of serialized `issued_ledger_head.file_sha256`.

Two corrections to the supplied premises:

- The failing mechanics tests regenerate **three live v5 generators**, through `GENERATOR_CASES`; they do not regenerate all twelve (`scripts/check_campaign_generator_core_parity.py:19`, `tests/test_campaign_generator_core.py:75`).
- Twelve generators reference the ledger path, but only **five** declare `LEDGER_HEAD_FILE_SHA256` (V6). For example, the v5 contrast generator names the path in reservation argv at `configs/campaigns/d117_contrast_v5/generate_configs.py:2134`; that reference is not itself a frozen file-hash pin.

The existing custody classification is:

| Class | Generators/packs | Correct test behavior |
|---|---|---|
| Historical snapshots | `d117_floor_qwen25_1p5b_v{1,2,3}`, `d117_floor_qwen25_7b_v{1,2,3}`, `d117_contrast_qwen25_1p5b_vs_7b_v{1,2,3}` | Preserve committed bytes. Keep historical-custody and echo/authentication tests; do not require successful regeneration against today’s operational inputs. |
| Live generator sources | `d117_floor_qwen3-1p7b_v5`, `d117_floor_qwen3-8b_v5`, `d117_contrast_v5` | Exercise regeneration mechanics with explicit fixture inputs. Separately test real input-drift refusal. |

The census and historical self-containment assertions are at `tests/test_campaign_generator_core.py:25`, `:33`, and `:203`. Frozen state belongs to the receipt, not the README wording (`configs/campaigns/d117_floor_qwen25_1p5b_v2/README.md:5`).

**A later append does not universally mean “new family generation.”** It makes regeneration against a stale pinned input refuse. It does not require rewriting an existing frozen pack. Same-ordinal draft generation remains supported; frozen current identities require preserve mode (`configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:314`, `:328`). MIDCAMPAIGN-CURE-GENERATION-01 concerns **non-config cures during a running campaign**, not every legitimate ledger append (`docs/process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md:58`).

Also, echo success is not sufficient PACK_AUTHENTICATION evidence: the existing test explicitly rejects promoting an echo result to generator PASS (`tests/test_arm_readiness_evidence_packauth.py:509`).

A prospective design could bind scientific eligibility to an immutable acceptance cutoff while retaining independent current-head authentication. That is a coherent separate proposal. It is unnecessary for restoring these tests.

**Q3 — exact minimal fix shape.**

The quick-tier unblock touches two test files. Add the ledger regressions and repair the cited non-ledger regression in two further test files:

| File | Proposed change |
|---|---|
| `tests/test_calibration_bracketing.py:597` | Rename the test to describe artifact authentication and head consistency. Replace `:635–646` with schema equality, `pin.sequence >= cutoff.sequence`, and digest equality **when sequences are equal**. Move the fixed `76` and `08456d50…` expectations onto the r6 **cutoff**. Retain all artifact byte-pin, identity, derivation and eligibility assertions. Add a comment that this test lacks the physical chain. |
| `tests/test_campaign_generator_core.py:103` | Within `assert_generation_uses_shared_write_boundary`, provide the historical head-file fixture for ALPHA/BETA. Narrowly intercept only `sha256_file(REPO_ROOT / LEDGER_HEAD_REL)`; delegate every other path to the real function. Use fixed fixture bytes whose independently checked SHA is `6bbe2625…`, rather than returning an arbitrary expected value. Apply the same fixture to normal and mutated source paths. Leave GAMMA and the boundary observer unchanged. |
| `tests/test_calibration_ledger.py:637` | Add non-genesis, physical-chain tests using temporary ledger/custody files and a temporary Git repository with committed pins. Cover the cases below. Existing helpers are at `:169–217`. |
| `tests/test_arm_readiness_evidence_packauth.py:541` | Before emitting the temporary successor, install and commit the generation-time head fixture **only inside this test’s disposable clone**. Preserve the acceptance-file newline mutation. Strengthen the refusal assertion to name the acceptance path, ensuring ledger drift cannot satisfy the negative oracle accidentally. |

Required regression cases:

- **Advanced pin:** finalize baseline A, append/finalize B, commit B’s pin, load using A’s cutoff; authentication succeeds.
- **Wrong cutoff digest:** same valid extended ledger and committed head, wrong baseline digest; `calibration_ledger_baseline_missing`.
- **Pin below cutoff:** roll the committed fixture pin below A; refuse. Also test a self-consistent shortened ledger/pin, so refusal cannot rely only on physical-head mismatch.
- **Physical rollback:** retain the existing rollback test at `tests/test_calibration_ledger.py:563`.
- **Non-ledger drift:** retain and repair the acceptance mutation at `tests/test_arm_readiness_evidence_packauth.py:565`. Its regenerate branch must refuse while echo remains classified as echo.
- **Frozen identity:** retain the earlier preserve-mode refusal; a frozen identity can refuse before reaching input validation (`configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:270`). Test the input-drift reason on the permitted successor-generation path, as the existing regression does.

Only the live-pin-equals-cutoff assertions and their test name become obsolete. Neither core counterfactual test is obsolete; their intended assertions must remain at `tests/test_campaign_generator_core.py:120` and `:180`.

No changes are needed to production ledger code, acceptance artifacts, committed pin, generators, frozen packs or sidecars. V5 passed ten scratch tests covering the replacement assertion, all seven core tests, physical-prefix counterfactuals and repaired non-ledger regression.

**Next-pin-advance surface:** these repaired tests have no new failure solely because the pin advances again. The structural assertion tolerates advancement, and mechanics fixtures remain fixed. Real regeneration against stale generation inputs still refuses intentionally (`configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2504`).

**F3 — the quick-tier repair does not establish full-suite green.**

The cited packauth test currently fails at its initial successful-emission assertion, before mutating the acceptance (V2; `tests/test_arm_readiness_evidence_packauth.py:561`). A v5 floor-generation test also fails on the ledger pin (V3; `tests/test_d117_floor_qwen3_v5_generate.py:774`). Both modules exceed the quick-tier weight threshold (`scripts/test_timings.json:70`, `:137`; selection at `scripts/quick_suite.py:98`).

The broader scratch experiment exposed an additional isolation detail: an in-process hash fixture does not reach the subprocess invoked at `tests/test_d117_floor_qwen3_v5_generate.py:592`. That subprocess needs a disposable repository containing the historical input bytes and must execute its generator there. The standalone parity tool likewise regenerates from ambient inputs through `scripts/check_campaign_generator_core_parity.py:132`.

Those are separate, named test-fixture repairs; do not weaken production drift checks to conceal them.

**Q4 — authority boundary.**

The recommended test-only repair implements an existing rule and changes no production admission behavior. D-109 already mandates the baseline/current distinction, and production already enforces it (`docs/decision_log.md:7511`; `joulewise/calibration_ledger.py:2614`). It therefore needs ordinary lead review and verification, not a new process ruling merely because a mistaken test changes.

The boundary is crossed by:

- Redefining `LEDGER_HEAD_FILE_SHA256` or allowing previously refused regeneration under a moved input.
- Replacing actual chain authentication with sequence-only comparison.
- Making a new committed CI witness a mandatory issuance or pin-advancement gate.
- Altering frozen-pack, acceptance-issuance, epoch or measurement rules.

Those change the contract or process and need the applicable cold-gate/Ed route. The recorded amendment principle explicitly treats changed refusal semantics as an amendment (`docs/process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md:14`); rule-11 roles are at `docs/orchestration.md:64`.

D-161 retains physics, evidence, pre-registration and operator-mistake protections (`docs/decision_log.md:10691`). No numerical tolerance needs adjustment here.

**Alternatives rejected:** equality contradicts D-109; pin rollback contradicts required readiness; bulk repinning/regenerating historical packs violates their custody role; acceptance-cutoff reinterpretation changes production semantics unnecessarily; sequence-only “authentication” omits the required chain proof. Authorities are respectively `docs/decision_log.md:7511`, `docs/phase_2/derivation_night_runbook.md:532`, `tests/test_campaign_generator_core.py:203`, and `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2504`.

## Residual risk

Actual 76→176 ancestry was not verified: the physical ledger was outside this consult’s permitted inputs. The harvest record locates it in the retained clone/archive (`docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md:52`). The proposal removes the three reproduced quick-tier failures, but full quick-tier green remains for the lead to verify after implementation.

Green tests confer no G2-a authorization. r6 binds 25F84 (`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:20`); the retained 25G83 equivalence result is FAIL (`docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md:71`).

Repository unchanged. Scratch probes remain at [focused probe](/tmp/pinfix-focused-probe.py) and [broader probe](/tmp/pinfix-design-probe.py). Next exact step: implement the four-file test repair, review the negative oracles, then run the quick tier and affected modules with the heavier-test failures explicitly dispositioned.