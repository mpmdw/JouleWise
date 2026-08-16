```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Adopt a fixed, arm-bound root-local locator that writers derive without new argv/env transport and authenticate back to the one-use-FD start receipt.",
  "workspace": {
    "base_requested": "impl/wo-launch-binding",
    "base_mode": "informational",
    "head_start": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "head_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "upstream_end": "345bfbb4428cc6c1e74723976b949777ec62b366",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "ADOPT_FIXED_ROOT_LOCAL_LOCATOR",
    "chosen_option": "c implemented as a fixed-custody index into a",
    "token_transport": "launcher-to-chain inherited FD only",
    "writer_transport": "none; deterministic discovery plus direct reauthentication",
    "successor_config_staging": "phase_2_only",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The branch lacks a writer-discoverable lineage locator",
        "disposition": "Publish a no-clobber locator at a constant basename in both arm-bound execution roots immediately after settle."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Every writer and downstream consumer must independently reauthenticate rather than trust copied strings",
        "disposition": "Use metadata.extra.launch_lineage as the durable carrier and reopen the authoritative receipts at every claim-bearing boundary."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Launch authorization remains session-bound despite content-addressed receipt bytes",
        "disposition": "Classify actual launch custody as SESSION_STATE_BOUND/TEMPORAL_CAPABILITY, with historical content authentication after completion."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The required config marker cannot be added to existing frozen packs",
        "disposition": "Land dormant enforcement code on impl/wo-launch-binding and issue semantic successor packs during Phase 2."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git show impl/wo-launch-binding:joulewise/arm_readiness.py | rg -n 'LAUNCH_LINEAGE_SCHEMA|def authenticate_launch_lineage|def launch_lineage_required|def authenticate_bundle_launch_lineage'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "56:LAUNCH_LINEAGE_SCHEMA = \"joulewise.launch_lineage.v1\"",
          "4929:def authenticate_launch_lineage(",
          "5126:def launch_lineage_required(config: object) -> bool:",
          "5136:def authenticate_bundle_launch_lineage("
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5136:def authenticate_bundle_launch_lineage\\($"
      }
    },
    {
      "id": "V2",
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
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git grep -n 'launch_lineage_required' impl/wo-launch-binding -- 'configs/campaigns/**' ':!tests/**'",
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
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A public authenticated locator proves descent of the launch session, not Unix parentage of each later writer process once that session is active.",
      "needs": "If a hostile same-UID process racing the frozen chain is in scope, separately rule and add per-stage one-use dispatch receipts; do not make the locator secret."
    }
  ]
}
```

## Findings

### F1 — Blocker: fixed root-local locator

Choose option (c), backed by option (a)’s durable receipts. Do not propagate FD 198 through zsh or multiple Python children. The token’s job ends when chain entry atomically creates the start receipt; writers need only discover and authenticate that proof.

After the settle receipt is durable, `record_launch_lifecycle_event("settle")` should publish:

- `<claim_runs_root>/.joulewise-launch-lineage.json`
- `<bound_runs_root>/.joulewise-launch-lineage.json`
- GNU SHA-256 sidecars for both

Both roots come from the consumed arm receipt’s authenticated `arm_context`; the chain already creates them before settle. Publication is canonical, no-clobber, file-fsynced, directory-fsynced, and never repaired. Partial publication burns the attempt and stops before calibration or collection.

Use exact-key schema `joulewise.launch_lineage_locator.v1`:

```json
{
  "schema_version": "joulewise.launch_lineage_locator.v1",
  "root_role": "claim_runs_root|bound_runs_root",
  "root_path": "/authenticated/absolute/path",
  "launch_lineage": {}
}
```

`launch_lineage` is the existing `joulewise.launch_lineage.v1` object returned at settle, with `completion: null`.

I recommend a constant basename rather than putting boot/pack values in the filename. The arm-bound execution root is already fresh and unique. Boot, pack, and bracket identities belong in authenticated content; using them as path selectors invites scanning and “latest” ambiguity.

Writer derivation requires no new transport:

- Campaign: `resolve(--runs-dir)/.joulewise-launch-lineage.json`.
- Calibration: require `output_root.name == "instrument_validation"`, then use `resolve(--output-root).parent/.joulewise-launch-lineage.json`.
- No receipt path, token, or lineage JSON is added to child argv or environment.

Before any bundle directory, calibration custody directory, campaign provenance, or calibration slot claim, the writer authenticates:

1. Fixed path, canonical exact-key locator, sidecar, root role, and exact root path.
2. Consumption primary/sidecar/namespace and its arm predecessor.
3. Committed pack digest, reviewed HEAD, plan/window/bracket IDs, arm-context digest, launch manifest, `window.env`, chain bytes, and exact exec argv.
4. Start predecessor and `handoff_token_sha256`, without accessing the token.
5. Settle predecessor and monotonic ordering.
6. Current boot equals the recorded collection boot.
7. The selected source config is an authenticated member of that pack or a pack-pinned external manifest.
8. The current runs root matches the appropriate `arm_context` root; calibration also matches the bracket session and attempt slot.
9. Completion is not already present when beginning new collection.

Do not reapply the arm’s short T-0 expiration at every writer. Authentication must prove consumption occurred within the horizon; otherwise a legitimate multi-hour window would expire mid-chain.

### F2 — Should-fix: carrier and downstream authentication

Campaign bundles stamp the full object at:

```text
metadata.json → extra → launch_lineage
```

Calibration stamps it at:

```text
instrument_evidence.json → launch_lineage
```

`manifest.json` then hashes that calibration evidence. The calibration ledger’s artifact hashes preserve the same binding.

At collection time, completion remains null. Later consumers derive the deterministic completion path from the authenticated consumption identity and require it where applicable.

| Boundary | Required authentication | Propagation |
|---|---|---|
| Campaign/calibration writer | Consumption + start + settle; current boot | Full `launch_lineage` |
| Post-hoc reduce | Reopen bundle receipts; completion not required | Full lineage in admissible reduction |
| NEG-8 bound | Every member directly authenticated; one identical lineage | Full lineage in bound artifact |
| Whole-window verdict | Members, both calibrations, bound, and completion | Full lineage in verdict/evaluation basis |
| Extraction | Direct source reauthentication plus completion | Full lineage in report and basis |
| Mint | Reopen source receipts directly; never trust copied digest strings alone | Minted provenance |

D-078 mapping stays closed:

- Missing locator/reference/primary/sidecar → `launch_consumption_missing`
- Malformed locator, bad sidecar/digest/schema/predecessor → `launch_consumption_invalid`
- Wrong root, boot, pack, plan, session, recipe, config membership, or lifecycle phase → `launch_binding_mismatch`
- Mixed authenticated lineages → `launch_lineage_conflict`
- Missing start/settle, or missing completion at verdict/extraction/mint → `launch_lifecycle_incomplete`
- FD/token/start replay defects remain chain-entry-only → `launch_handoff_invalid`

Backup, quarantine, and diagnostic refusal output remain available.

The existing `authenticate_launch_lineage` should also stop replaying with `Path(".")`; derive the authenticated pack root from the consumed arm’s pack record and compare it with any caller-expected pack/config root.

### F3 — Should-fix: R1 lifecycle classification

The actual launch lineage is not content-bound merely because every receipt is hashed.

- The successor pack’s locator rule, schema, marker, and launch recipe are content-bound frozen policy.
- Arm authority and unconsumed launch capability are `TEMPORAL_CAPABILITY`.
- Consumption/start/settle/completion are `SESSION_STATE_BOUND` execution records: boot/session/root state is essential to their meaning.
- After completion, historical consumers authenticate their immutable bytes and compare recorded boot identities to one another, not to the machine’s current boot.
- These records are never re-derived, refreshed, grandfathered, or reissued from unchanged pack content.

The locator itself is an immutable index, not authority and not a secret.

### F4 — Should-fix: staged work order

Land on `impl/wo-launch-binding`:

1. Locator schema plus no-clobber publication/resolution in `joulewise/arm_readiness.py`; settle publishes both root locators.
2. `run_campaign.py` outer preflight, with the inner CLI/controller independently resolving again and stamping bundles—no lineage environment variable.
3. Calibration pre-capture gate and evidence stamp.
4. Standalone reduce, bound, verdict, extraction, and both mint paths wired to direct reauthentication.
5. Retire the public standalone consume route.
6. Regressions for missing/corrupt/root-swapped/precreated/mixed locators, writer ceremony bypass, completion absence, rebooted historical verification, publication crash boundaries, and byte-identical happy-path propagation.
7. Generic runbook/decision-contract wording for the fixed locator.

Phase 2 only:

1. Generate semantic successor pack directories and IDs.
2. Add `launch_lineage_required` to every successor collection config, including successor copies of shared bound/reference configs whose current hashes are frozen.
3. Freeze the locator schema/basename/root-role rules into the successor plan tree and launch bindings.
4. Regenerate order manifests, plan digests, freeze receipts, pack-family receipts, and R1 content-bound evidence as one successor-family transaction.
5. Produce fresh `window.env`, chain, launch manifest, T-0 evidence, ARM receipt, and live E-10 launch.

Confirmed: the flag is Phase 2. The branch contains enforcement support but no campaign config currently carries `launch_lineage_required`. Editing existing frozen packs would invalidate their config hashes, manifests, pack digest, and freeze receipts.

## Residual risk

A fixed authenticated locator is intentionally observable. It prevents absent-lineage and wrong-session bypass, but after a legitimate settle it does not cryptographically prove that every writer’s Unix parent is the frozen zsh chain. Existing fresh-root, campaign-lock, exact-membership, and calibration-slot single-use gates address ordinary/direct-invocation bypass.

If hostile same-user process injection during an active window is in scope, add a separate frozen per-stage dispatcher that mints one-use stage receipts and passes fresh tokens by anonymous FD directly to each writer. That is a larger contract; it should not be smuggled into this locator mechanism.