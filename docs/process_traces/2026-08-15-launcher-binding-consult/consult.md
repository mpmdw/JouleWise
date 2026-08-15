```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Current D-134 consumption is not launch-binding; adopt one human-invoked consume→revalidate→exec launcher plus authenticated lineage gates through collection, reduce, verdict, extraction, and mint.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "head_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "ADOPT_WITH_CONTRACT_DELTAS",
    "launch_gate": "NO_GO_UNTIL_IMPLEMENTED",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Consumption and physical launch are separate, unauthenticated operations",
        "disposition": "Block D-117 launches until the reviewed launcher and downstream lineage gates land."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Make the consumption write the linearization point and bind it to one inherited launch handoff",
        "disposition": "Use a human-invoked consume→revalidate→exec launcher with burned-on-crash semantics."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Every claim-bearing consumer must authenticate the same pack/boot launch lineage",
        "disposition": "Gate collection, reduce, bound derivation, verdict, extraction, and mint with one shared verifier."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "D-134, runbook, pack, reason-code, and regression contracts need coordinated amendment",
        "disposition": "Issue successor frozen packs; do not grandfather or edit the existing frozen bytes."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "rg -l 'arm_readiness\\.consumptions|launch_consumption|CONSUMPTION_RECEIPT_SCHEMA' joulewise scripts | sort",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise/arm_readiness.py",
          "joulewise/arm_readiness_evidence_t0.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "joulewise/arm_readiness_evidence_t0\\.py$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n 'caffeinate -is /bin/zsh|def consume_launch_capability|never execute a command|launch-consumption receipt path' docs/phase_2/window_runbook.md joulewise/arm_readiness.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise/arm_readiness.py:4025:def consume_launch_capability(",
          "joulewise/arm_readiness.py:4030:    \"\"\"Atomically consume one unsuperseded GO receipt; never execute a command.\"\"\""
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "never execute a command"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "8937dec9bd7be8f6d87694a739089ac8434b8bc9"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^8937dec9bd7be8f6d87694a739089ac8434b8bc9$"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The named council-verdict and refuter-output files are absent from this detached checkout; the review used their facts as quoted in the prompt and independently inspected the current implementation and runbook.",
      "needs": "Consult the original traces while implementing exact wording."
    },
    {
      "id": "R2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Anonymous-FD handoff through /usr/bin/caffeinate requires target-macOS verification.",
      "needs": "Run a lead-owned live process-handoff smoke test before accepting the launcher."
    }
  ]
}
```

## Findings

### F1 — Blocker: the present capability is not launch-binding

The confirmed failure is structural. `consume_launch_capability` durably emits a receipt but explicitly never executes anything. The operator then starts `window-chain.zsh` through a separate ordinary shell command, and neither the chain nor any claim-bearing consumer authenticates that the launch descended from the consumption.

Decision: every D-117 physical launch remains NO-GO until this is machine-enforced. A close-out checkbox or later receipt recording does not close the gap.

### F2 — Atomic launcher contract

Replace the operator-visible `consume` followed by direct `caffeinate` with one reviewed command, invoked personally by Ed after he has inspected the ARM verification result:

```sh
.venv/bin/python scripts/launch_window.py \
  --pack-root "$PACK_ROOT" \
  --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST"
```

This preserves the ruling: Ed’s deliberate invocation performs the physical launch. No automated verdict invokes it.

The launcher contract is:

1. Generate a random one-use handoff token and retain only its SHA-256 in the prospective consumption record.

2. Atomically claim the capability by creating the consumption primary with no-clobber semantics. That successful creation is the single-use linearization point. Fsync the primary and containing directory before proceeding, then publish and fsync its sidecar.

3. Revalidate from the newly written consumption—not through `verify_arm_receipt`, which correctly rejects consumed arms. A new `verify_consumed_launch` operation must replay:

   - arm receipt, sidecar, namespace, PASS/GO, and supersession;
   - current boot and monotonic validity;
   - reviewed HEAD and committed pack digest;
   - arm context, roots, backups, ledger reservation, and absent locks;
   - launch-manifest, `window.env`, and `window-chain.zsh` bytes;
   - exact final exec argv.

4. Make the handoff token available only through an inheritable anonymous FD, never argv, environment text, or a persistent file. Store only its hash in the consumption receipt.

5. Call `execve` on the exact frozen foreground argv. Do not spawn and return, and do not contain an automatic retry loop.

The exact-key consumption v2 record should add:

- `consumption_id`;
- `consumed_at_monotonic_ns`;
- `boot_session_id`;
- pack ID, pack digest, plan ID, and window ID;
- the arm receipt reference;
- reviewed HEAD and arm-context digest;
- launch-manifest, environment, and chain path/digest references;
- exact exec argv;
- `handoff_token_sha256`;
- the existing volatile-check and assurance fields.

Standalone production `consume` must cease to be an operator route. The library primitive may remain for the launcher and focused tests, but the public production command is `launch`.

Crash semantics are intentionally asymmetric:

- Before the no-clobber claim: nothing was consumed; rerun is permissible only if the arm still verifies.
- After the claim but before `execve`: the capability is permanently burned. Missing sidecar or an incomplete record is still consumed, not repairable.
- `execve` failure: burned attempt; no retry.
- Chain entry followed by death before settle: the start receipt exists, the settle receipt does not, and the attempt is `launch_lifecycle_incomplete`. Reuse is forbidden.
- Death after settle: collected bytes remain immutable diagnostic evidence, but no whole-window claim can proceed without the terminal completion receipt.
- Recovery always uses a newly frozen bracket session and new attempt IDs, followed by a new ARM receipt. There is no rollback to “available.”

The chain’s first executable action must validate the inherited token against the consumption record and atomically emit an immutable start receipt. After the full monotonic settle, it emits a linked settle receipt; after finalized post-calibration it emits a linked completion receipt. Each receipt pins its predecessor digest, pack, boot, session, chain bytes, and consumption digest.

### F3 — Downstream provenance refusal

Every D-117 configuration must carry a frozen `launch_lineage_required` marker. That makes direct invocation of an individual campaign stage fail before bundle creation when the launcher lineage is absent.

The authenticated lineage is:

```text
ARM receipt
  → consumption receipt
  → inherited-FD start receipt
  → settle receipt
  → bundle/calibration lineage reference
  → completion receipt
  → verdict
  → extraction
  → mint
```

Required consumers:

- The collection writer authenticates consumption, start, and settle before capture and records their digests in immutable bundle metadata. Calibration and bound-corpus writers do the same.
- Post-hoc `reduce` independently opens and authenticates those receipts before producing an admissible reduction.
- NEG-8 bound derivation authenticates every bound member and carries the one lineage into the bound artifact.
- Whole-window verdict requires one identical lineage across every member, both calibrations, and the bound; it also requires the completion receipt.
- Extraction reauthenticates the source receipts and records the lineage in its report and evaluation basis.
- Floor/contrast mint reauthenticates the receipts directly. Merely trusting lineage strings copied into an extraction report is insufficient.
- Backup and quarantine remain available regardless of lineage validity; evidence preservation must never be blocked by a claim gate.

Postcollection processing must compare the receipt’s recorded boot to the boot captured in each bundle and lifecycle receipt—not to the machine’s current boot. The launcher and chain entry check the current boot; a later reboot must not destroy otherwise valid historical evidence.

Use one closed vocabulary at every downstream boundary:

- `launch_consumption_missing` — required reference, primary, or sidecar absent.
- `launch_consumption_invalid` — noncanonical/schema-invalid receipt, bad sidecar/digest, bad namespace, or invalid predecessor chain.
- `launch_binding_mismatch` — valid receipt disagrees on pack, plan, HEAD, arm context, collection boot, session IDs, roots, recipe bytes, or argv.
- `launch_lineage_conflict` — members or artifacts name more than one consumption/pack/boot lineage.
- `launch_lifecycle_incomplete` — start/settle is absent; for verdict, extraction, or mint, completion is absent.
- `launch_handoff_invalid` — chain entry lacks the one-use inherited token, its hash disagrees, or the handoff was replayed.

A failure may produce a structured diagnostic refusal, but never an admissible summary, passing verdict, extractable cell, or mint artifact.

### F4 — Contract, runbook, and regression deltas

Amend D-134 clause 8: exactly one reviewed launcher may claim the capability, and the consumption receipt alone does not prove launch. Authorization attaches only to the chain start descended from that launcher’s one-use handoff.

Add clauses:

11. The sole production entrypoint performs consume → revalidate → exec; the human invokes it, and no automated verdict does.

12. Consumption is irrevocable. Start, settle, and completion are append-only successor receipts; absence never reopens the capability.

13. Collection, reduction, verdict, extraction, and mint independently authenticate launch lineage using the closed refusal vocabulary.

14. Crash injection, race, ceremony-bypass, mutation, and every-downstream-stage tests are release gates.

D-137 should clarify that current-boot comparison applies through launcher/chain entry, while historical consumers authenticate equality among recorded boot identities.

Runbook changes:

- E-9a remains the governed bracket reservation.
- E-9b is T-0 evidence authoring; its 20-minute volatile horizon starts there.
- E-9c performs ARM and verify, then stops so Ed can inspect PASS/GO.
- New E-10 is Ed’s single reviewed-launcher invocation.
- Remove standalone consume and the direct `caffeinate … window-chain.zsh` operator command.
- §6 marks `window-chain.zsh` as private to the launcher and makes its first action the inherited-handoff verifier.
- §10 gains the six refusal codes and burned-attempt recovery rule.
- §12 records consumption, start, settle, and completion receipt paths and digests.

Because the frozen doctrine evidence pins the old runbook and launch recipe, this cannot be grandfathered as a docs-only change. Preserve the current frozen packs and issue semantic successor packs/receipts; do not edit frozen bytes in place.

The required regression matrix is:

- Eight concurrent launchers: exactly one claim and one mocked `execve`; seven `readiness_record_consumed` refusals.
- Crash injection after every durable boundary from claim creation through immediately before exec: capability stays burned and no second exec occurs.
- Direct chain invocation without inherited handoff: `launch_handoff_invalid` before settle or collection.
- Chain death before settle: start exists, settle absent, replay refuses, downstream reports `launch_lifecycle_incomplete`.
- Ceremony-skipped bundle fixture with no lineage: reduce, bound derivation, verdict, extraction, and mint each refuse `launch_consumption_missing`.
- Malformed receipt/sidecar fixture: each stage refuses `launch_consumption_invalid`.
- Valid receipt from a different pack or collection boot: each stage refuses `launch_binding_mismatch`.
- Mixed valid receipts in one window: aggregate stages refuse `launch_lineage_conflict`.
- Happy path: one consumption digest survives byte-for-byte through bundle, reduction, bound, verdict, extraction, and mint.

Rejected alternatives:

- Chain-side check only is bypassable through direct stage commands and provides no durable consume-to-exec proof.
- Launcher-only enforcement leaves previously/directly collected bytes acceptable to downstream consumers.
- Downstream-only enforcement wastes the quiet window before refusing and does not make the launch path fail closed.
- Passing a receipt path or token through argv/environment is replayable and does not prove same-launcher handoff.
- Reopening a consumed capability after a crash destroys D-134’s single-use guarantee.
- Launching automatically on machine GO violates the ruled human-launch boundary.

## Residual risk

The inherited anonymous FD must be verified through the real `/usr/bin/caffeinate` process topology on the target macOS. If it closes unknown descriptors, use a reviewed exec trampoline that preserves the FD; do not downgrade to an argv/environment token.

The named council and refuter trace files were not present in this detached checkout, so exact implementation wording should be reconciled against those originals before landing.