```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Replace forgeable caller identity with an honest private required-context API backed by atomic single-use, and defer AXI nested-root support behind a registered Phase-2 freeze gate.",
  "workspace": {
    "base_requested": "impl/wo-launch-binding",
    "base_mode": "exact",
    "head_start": "72cd69842434962d95176c9a625d256bc55f4fe5",
    "head_end": "72cd69842434962d95176c9a625d256bc55f4fe5",
    "upstream_end": "0f886d38cc1d87f5168e0775942d239bc0036c33",
    "branch": "impl/wo-launch-binding"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "q1": {
      "recommendation": "ADOPT_PRIVATE_REQUIRED_CONTEXT_API",
      "disposition": "Delete the public-named wrapper and both frame-identity guards; retain a module-private consumer with mandatory complete launch inputs, callee-side reauthentication, and the existing atomic no-clobber primary as the only real enforcement.",
      "os_separation": "disproportionate_for_this_work_order",
      "caller_guard": "remove_not_represent_as_security"
    },
    "q2": {
      "recommendation": "DEFER_WITH_PHASE_2_RELEASE_GATE",
      "disposition": "Register marker-bearing AXI as forbidden until a deterministic nested-root projection is implemented and tested; do not use nearest-ancestor search or locator replication.",
      "preferred_phase_2_mechanism": "exact AXI layout projection plus an authenticated successor-schema derivation descriptor"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Mutable frame metadata cannot enforce the sole-launcher claim",
        "disposition": "Remove consume_launch_capability and _require_launcher_consumption_context; retain only a private, mandatory-input consumer and narrow the contract to the sole supported production route."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Marker-bearing AXI children cannot find the top-level locator",
        "disposition": "Defer under the already-adopted Phase-2 boundary, but register a freeze/release prohibition and narrow any current claim that campaign-side enforcement covers AXI."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "rg -n \"def _require_launcher_consumption_context|caller_path = Path|def _consume_launch_capability|def consume_launch_capability\" joulewise/arm_readiness.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "4778:def _consume_launch_capability(",
          "4884:def consume_launch_capability(",
          "4896:        caller_path = Path(str(sys._getframe(1).f_globals[\"__file__\"])).resolve()",
          "4898:        caller_path = Path()"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "4898:.*caller_path = Path\\(\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n \"authenticate_campaign_writer_preflight\\(|attempt_runs_dir = \\(|run_authenticated_campaign_child\\(|authenticate_campaign_launch_lineage\\(\" scripts/run_campaign.py joulewise/bundle.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/run_campaign.py:6671:            attempt_runs_dir = (",
          "scripts/run_campaign.py:6760:                completed = run_authenticated_campaign_child(",
          "scripts/run_campaign.py:7272:        launch_authentication = authenticate_campaign_writer_preflight("
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "7272:.*authenticate_campaign_writer_preflight"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git grep -n 'launch_lineage_required' -- configs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": []
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1",
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
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A hostile same-UID or same-interpreter actor can invoke private Python machinery or the reviewed launcher; caller identity and Unix parentage are not authenticated.",
      "needs": "Preserve the existing registered-limitation family and escalate only if Ed brings that adversary into scope."
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This was a read-only design inspection; no runtime or mutation suite was executed.",
      "needs": "Run the focused launcher and marker-bearing AXI subprocess regressions after implementation."
    }
  ]
}
```

## Findings

### F1 — Blocker: replace caller identity with an honest API boundary

Recommendation: adopt option (i), but do not call it security “keying.” The assembled values are readable and reproducible; they are validated launch inputs, not an unforgeable capability.

The minimal cure is:

1. Delete the public-named `consume_launch_capability` wrapper. Its omission from `__all__` does not retire exact imports.
2. Delete `_require_launcher_consumption_context` and both `__file__`/frame checks.
3. Let `scripts/launch_window.py` call only `_consume_launch_capability`, with every input mandatory and without compatibility defaults:
   - pack root;
   - arm receipt and custody root;
   - launch manifest;
   - exact exec argv;
   - handoff-token digest.
4. Continue deriving and reopening `window.env`, the chain, manifest bytes, arm context, HEAD, pack digest, and related identities inside the consumer immediately before publication. Caller-supplied digests must not become authority.
5. Keep the atomic exclusive consumption primary as the actual single-use enforcement and linearization point. After it exists, every second consumer loses regardless of caller identity.
6. Change contract language from “only the reviewed launcher can claim” to “the reviewed launcher is the sole supported production route.” State explicitly that Python does not authenticate its caller.

A frozen context object may be used for API cohesion, but it adds no security over mandatory keyword-only inputs. An “opaque” Python token, private constructor, closure, sentinel, or code-object check remains recoverable or invocable by hostile in-process code.

Regression obligations:

- Prove the standalone CLI is absent.
- Prove `joulewise.arm_readiness.consume_launch_capability` is absent, not merely omitted from `__all__`.
- Prove the legacy three-argument/all-`None` shape cannot reach filesystem mutation.
- Prove missing, changed, or mismatched manifest/environment/chain/arm inputs refuse before the primary.
- Preserve the concurrent race regression: exactly one primary succeeds and every competing claim receives `readiness_record_consumed`.
- Preserve consume → replay → exact `execve`.
- Pin the limitation explicitly: a deliberate direct call to the private function with a fully valid context is indistinguishable from the supported caller.

Those tests cannot prove caller identity, Ed’s personal ceremony, Unix parentage, or that the first valid consumer was benign. The forged-`__file__` regression should therefore not be replaced with a different Python caller-identity test.

D-078 mapping:

| Condition | Disposition |
|---|---|
| Missing manifest, arm, environment, chain, primary, or sidecar | `launch_consumption_missing` where the lineage registry applies |
| Noncanonical/schema-invalid custody or bad sidecar/digest/predecessor | `launch_consumption_invalid` |
| Validly parsed inputs disagree on pack, HEAD, boot, arm context, recipe, roots, or argv | `launch_binding_mismatch` |
| Repeated atomic claim | Existing `readiness_record_consumed`; do not invent a D-078 synonym |
| Missing or replayed FD at chain start | `launch_handoff_invalid` |
| Deliberate first invocation with a completely valid context | Undetectable; covered by the registered limitation, not a fabricated refusal |

Honest limitation text:

> The private consumption API and mandatory validated launch inputs are an ordinary-misuse boundary, not caller authentication. Python code running in the same interpreter or under the same trusted UID can import private functions, construct equivalent inputs, alter module globals, or invoke the supported launcher. The mechanism does not prove caller identity or Unix parentage. Its enforceable property is single use: the atomic no-clobber consumption primary is the linearization point, so no later caller can create a second valid consumption. Stronger hostile-same-UID protection requires a separately ruled OS trust boundary.

Rejected alternatives:

| Alternative | Disposition | Reason |
|---|---|---|
| Distinct helper/UID | Reject for this WO | A subprocess under the same UID changes nothing. A genuinely separate principal, protected custody namespace, and authenticated IPC could work, but adds privileged deployment and recovery machinery disproportionate to an accidental-misuse requirement. |
| Retain the frame guard as an anti-footgun | Reject | It is redundant once the public symbol/default signature are removed, brittle under refactoring, and already induced a false security claim. If retained despite this recommendation, it must be named and documented as non-authoritative call-shape diagnostics and may not count toward acceptance. |
| Opaque Python context token or private constructor | Reject as enforcement | Same-interpreter code can obtain, construct, monkey-patch, or bypass it. It may improve type cohesion only. |
| Move all code into `launch_window.py` | Reject as a security cure | Python source/module placement does not create a trust boundary and would duplicate arm-readiness validation logic. |

### F2 — Should-fix: defer AXI, with a real Phase-2 gate

Recommendation: option (d) for this branch. This is not a recorder-race-style threat-model carve-out. The adopted contract explicitly places `launch_lineage_required` in the successor-family Phase-2 transaction, and inspection finds no current config carrying it.

The limitation must nevertheless be registered before merge:

> Marker-bearing AXI v2 campaigns are unsupported until the Phase-2 nested-root resolver lands. No successor pack may freeze or issue `launch_lineage_required` on an AXI config family before that gate passes. Existing campaign-side launch-lineage support covers flat/root-local writers only. This is a scheduling boundary, not an exclusion of AXI from the lineage contract.

If current documentation says stage 2 covers all campaigns, narrow it to flat/root-local campaigns.

For Phase 2, prefer a deterministic hybrid of (a) and (c), not ancestor search:

1. Freeze a successor-schema derivation descriptor such as `axi_attempt_v1`; do not freeze the absolute root, which is session-bound in `arm_context`.
2. For ordinary writers, compute exactly `runs_root/.joulewise-launch-lineage.json`.
3. For AXI writers, accept only the exact layout  
   `TOP/axi_attempt_bundles/<manifest-id>/<entry-id>/a<ordinal>`.
4. Compute `TOP` mechanically as `runs_root.parents[3]`; never search for the nearest existing locator.
5. Open exactly `TOP/.joulewise-launch-lineage.json`.
6. After authenticating it, authenticate the AXI manifest/config relationship from the pack inventory: manifest content ID, entry ID, selected config path and digest, and the attempt-directory grammar must all match.
7. Reject intermediate competing locators rather than selecting or falling back.
8. Preserve the existing parent-versus-child canonical lineage and locator-digest equality check.

No existing AXI manifest field carries the top-level run root. Its exact-key entry schema carries config paths and digests, while the absolute top root is created later in the arm receipt. Consequently option (c) cannot be implemented by merely reading a current field.

Phase-2 regression obligations:

- Run a real subprocess marker-bearing AXI campaign with the locator only at `TOP`; every nested child must authenticate before bundle creation and stamp the same canonical lineage as the outer preflight.
- Missing top locator → `launch_consumption_missing`.
- Malformed locator or sidecar → `launch_consumption_invalid`.
- Wrong layout, root, manifest ID, entry ID, config digest, or arm-context root → `launch_binding_mismatch`.
- Parent/child lineage divergence → `launch_lineage_conflict`.
- A nearer fake locator must refuse; it must never cause fallback to another candidate.
- Mutation tests must show that reverting to child-root lookup bricks the positive subprocess case.

These tests cannot establish hostile same-UID exclusion or support for unregistered future AXI directory layouts.

Rejected alternatives:

| Alternative | Disposition | Reason |
|---|---|---|
| Nearest authenticated ancestor search | Reject | Candidate selection depends on filesystem contents, recreating the scanning/ambiguity problem the fixed basename avoided. “Skip invalid and continue upward” is especially unsafe. |
| Republish or link into every attempt root | Reject | Adds one primary, sidecar, crash boundary, and no-clobber obligation per attempt. Symlinks conflict with current custody checks; copied payloads conflict with exact root-path binding unless the schema is weakened. |
| Existing pack-authenticated top-root field | Unavailable | No such field exists, and an absolute session-specific root cannot truthfully be frozen into a content-bound pack. A successor field may authenticate the derivation mode and manifest reference, not the root value. |
| Quietly rely on present child failure | Reject | It is fail-closed but leaves the feature knowingly bricked and may create parent-side AXI evidence before the child refusal. The explicit Phase-2 issuance prohibition is required. |

## Residual risk

The proposed F3 cure intentionally guarantees API retirement and single use, not caller identity. Closing hostile same-UID invocation would require a separate OS-principal or attestation design under Ed’s existing risk-appetite ruling.

The AXI disposition remains inspection-only until Phase 2; its release gate requires an actual subprocess integration test, not only a resolver unit test.