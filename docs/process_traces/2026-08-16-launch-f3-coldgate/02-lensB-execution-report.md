```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REJECT: the outer and inner campaign checks can accept different valid launch lineages, and two author-written regressions overclaim adversarial coverage.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "e7fa8fd37b2de27e6600cd74b91dbffc9871dec3",
    "head_end": "e7fa8fd37b2de27e6600cd74b91dbffc9871dec3",
    "upstream_end": "e7fa8fd37b2de27e6600cd74b91dbffc9871dec3",
    "branch": "impl/wo-launch-binding (detached checkout)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "REJECT",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "title": "Outer and inner checks do not bind to the same lineage",
        "paths": ["scripts/run_campaign.py:7193", "joulewise/bundle.py:95"],
        "evidence": "run_campaign discards the outer authenticated object; the inner writer authenticates current disk state without an expected outer identity. A→B replacement between checks is accepted without launch_lineage_conflict."
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "title": "Ceremony-bypass regression replaces the gate instead of bypassing ceremony",
        "paths": ["tests/test_run_campaign.py:140"],
        "evidence": "The test patches authenticate_campaign_writer_preflight to raise. It proves call ordering, but would still pass if the real authenticator were a broken no-op."
      },
      {
        "id": "S2",
        "severity": "should_fix",
        "title": "Locator corruption and mixed-lineage subcases use weaker mutations than claimed",
        "paths": ["tests/test_arm_readiness.py:342"],
        "evidence": "The corruption subcase edits only the sidecar. The mixed subcase changes pack_id without constructing a second authenticated receipt chain. The root-swap subcase does correctly swap actual produced locator and sidecar bytes."
      },
      {
        "id": "N1",
        "severity": "nit",
        "title": "Precreated-locator test does not establish its named burn property",
        "paths": ["tests/test_arm_readiness.py:314"],
        "evidence": "It checks refusal and sibling absence but never removes the collision and retries, or directly checks that the durable settle receipt prevents repair."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness 2>&1 | tail -n 8",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["----------------------------------------------------------------------", "Ran 17 tests in 0.008s", "", "FAILED (errors=16)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_launch_window 2>&1 | tail -n 8",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["----------------------------------------------------------------------", "Ran 10 tests in 0.004s", "", "FAILED (errors=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_lifecycle 2>&1 | tail -n 8",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["----------------------------------------------------------------------", "Ran 12 tests in 1.687s", "", "FAILED (errors=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_schemas 2>&1 | tail -n 8",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["..............", "----------------------------------------------------------------------", "Ran 14 tests in 0.056s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_campaign 2>&1 | tail -n 8",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["    raise FileNotFoundError(_errno.ENOENT,", "                            \"No usable temporary directory found in %s\" %", "                            dirlist)", "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensEXE']"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_bundle 2>&1 | tail -n 8",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["----------------------------------------------------------------------", "Ran 73 tests in 0.028s", "", "FAILED (errors=61)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_engine 2>&1 | tail -n 8",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["----------------------------------------------------------------------", "Ran 12 tests in 0.126s", "", "FAILED (errors=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_whole_window 2>&1 | tail -n 8",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["----------------------------------------------------------------------", "Ran 15 tests in 0.007s", "", "FAILED (errors=14)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V9",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_floor_extraction 2>&1 | tail -n 8",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["    raise FileNotFoundError(_errno.ENOENT,", "                            \"No usable temporary directory found in %s\" %", "                            dirlist)", "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensEXE']"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V10",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_arm_readiness.LaunchPackConfigInventoryTests.test_real_pack_inventory_authenticates_exact_member_bytes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.001s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V11",
      "kind": "inspection",
      "cmd": "Python AST/source comparison of run_campaign, bundle writer, and origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["outer_preflight_parent=Expr; line=7193; result_stored=False", "inner_auth_args=1; inner_auth_keywords=[]; line=95", "origin_has_campaign_auth=False", "origin_has_writer_gate=False", "origin_has_outer_preflight=False", "origin_consume_retired=False"]
      },
      "expected": {"exit_code": 0, "tail_regex": "origin_consume_retired=False$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox provides no usable writable TMPDIR. Eight suites failed at tempfile setup/import; all five adversarial probes and the origin/main comparison therefore used explicit static source-trace fallback.",
      "needs": "Lead should replay V1-V9 in a writable clean worktree before landing."
    }
  ]
}
```

## Findings

B1 — blocker: The outer authentication result is discarded at [run_campaign.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensEXE/scripts/run_campaign.py:7193). The inner writer independently reads current disk state at [bundle.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensEXE/joulewise/bundle.py:95), but receives no expected outer lineage or digest. Thus outer=A, replace both locators consistently with valid B, inner=B is accepted. No registered `launch_lineage_conflict` is emitted.

S1 — should-fix: The ceremony-bypass test patches the preflight itself to raise at [test_run_campaign.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensEXE/tests/test_run_campaign.py:154). It proves the call occurs before lock/provenance/child work, but does not construct a marker-bearing campaign with missing launch custody. It would pass if the real authenticator always returned `None`.

S2 — should-fix: In [test_arm_readiness.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtB-lensEXE/tests/test_arm_readiness.py:367), “corruption” changes only the sidecar, not the authenticated locator primary. The root-swap case is sound: it swaps actual settle-produced primaries and their actual sidecars. The mixed case changes only `pack_id` and re-signs the locator, so it is not a second authenticated lineage.

N1 — nit: The precreated-locator regression verifies refusal and sibling absence, but not the named irreparable burn. The separate partial-publication regression is sound: it faults at the bound-locator primary after the settle receipt and complete claim locator are durable, then proves retry dies on the already-existing settle primary.

### Fifteen-test audit

| Regression | Classification | Reviewer result |
|---|---|---|
| `test_settle_publishes_both_canonical_no_clobber_locators` | genuine | Exercises produced bytes, sidecars, roles, paths, and fsync counts. |
| `test_lineage_replay_derives_pack_root_and_rejects_caller_mismatch` | genuine | Covers pack-root derivation and caller mismatch. |
| `test_partial_locator_publication_burns_and_cannot_be_repaired` | genuine | Fault is injected at the correct second-root boundary; retry is refused. |
| `test_precreated_locator_burns_settle_without_publishing_sibling` | genuine | Collision/no-sibling behavior is real; named burn assertion is incomplete (N1). |
| `test_locator_missing_corrupt_root_swap_and_mixed_are_discriminated` | genuine | Useful multi-case coverage, but corruption/mixed mutations are weaker than claimed (S2). |
| `test_campaign_config_membership_and_completion_absence_are_enforced` | genuine | Covers outside-pack copy and completion-before-collection refusal. |
| `test_writer_auth_does_not_reapply_short_arm_expiration` | genuine | Correctly preserves consumed-within-horizon semantics for long windows. |
| `test_real_pack_inventory_authenticates_exact_member_bytes` | genuine | Executed independently and passed. |
| `test_marker_writer_authenticates_before_bundle_creation` | genuine | Valid ordering/wiring regression. |
| `test_marker_writer_stamps_byte_identical_authenticated_lineage` | genuine | Valid carrier-byte regression. |
| `test_marker_writer_refuses_caller_supplied_lineage` | genuine | Valid writer-ownership regression. |
| `test_standalone_consume_cli_is_retired_with_launcher_guidance` | genuine | Exercises the real subprocess CLI route. |
| `test_outer_preflight_derives_from_runs_root_and_exact_configs` | genuine | Valid forwarding/wiring regression. |
| `test_outer_preflight_refuses_mixed_marker_selection` | genuine | Constructs and checks the real marker-selection refusal. |
| `test_ceremony_bypass_refuses_before_lock_provenance_or_child` | vacuous | Ordering is tested, but actual ceremony bypass is not; see S1. |

Silent-weakening audit: **none of the 15 would pass on `origin/main` unchanged** under static transplant analysis. Origin lacks the campaign locator authenticator, writer gate, and outer preflight, while its standalone consume route is not retired. This comparison was static because TMPDIR writes were denied.

### Adversarial probes

Every probe below used **STATIC FALLBACK — TMPDIR denied**.

| Probe | Source-traced outcome |
|---|---|
| Valid locator carrying the other authenticated root’s role | Refuses `launch_binding_mismatch` when the selected root’s derived role is compared with `locator.root_role`. |
| Byte-identical locator and sidecar copied into a different runs root | Refuses `launch_binding_mismatch` because recorded `root_path` and locator parent differ from the selected root. |
| Earlier-boot lineage | Refuses `launch_binding_mismatch` through `require_current_boot=True`. |
| Completion-present locator before new collection | Refuses `launch_binding_mismatch` when either the completion reference, primary, or sidecar exists. |
| Lineage A at outer check and valid lineage B at inner check | **Does not refuse.** Outer A is discarded and inner B is independently accepted; expected `launch_lineage_conflict` is absent (B1). |

## Residual risk

Eight focused suites were not meaningfully executable in this read-only environment. Only `arm_readiness_schemas` and the no-temp real-pack inventory regression executed successfully; the remaining conclusions are source-traced and should be replayed in a writable clean worktree. No files were modified, and HEAD remained `e7fa8fd`.