```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "A93/A94 are confirmed; authentication should ignore the stale constant and enforce the already-recorded pre-freeze regeneration anchor composed with existing historical-semantics custody checks.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "informational",
    "head_start": "2fd7c920314333535ea2631bec887a19b964f834",
    "head_end": "2fd7c920314333535ea2631bec887a19b964f834",
    "upstream_end": "3109c0dc960a21c4ec0881b8a9f725995224ebe1",
    "branch": "fix/packauth-soundness-rows"
  },
  "pathspec": [
    "docs/process_traces/2026-08-26-t26-s3/characterization.md",
    "docs/process_traces/2026-08-26-t26-s3/what-check-proves.md",
    "docs/process_traces/2026-08-26-t26-s3/consumption-sites.md",
    "docs/process_traces/2026-08-26-t26-s3/cure-options.md",
    "docs/process_traces/2026-08-26-t26-s3/recommendation.md",
    "docs/process_traces/2026-08-26-t26-s3/report.md",
    "docs/process_traces/2026-08-26-t26-s3/replay-characterization.sh",
    "docs/process_traces/2026-08-26-t26-s3/replay-mutations.sh",
    "docs/process_traces/2026-08-26-t26-s3/replay-historical-anchor.sh",
    "docs/process_traces/2026-08-26-t26-s3/replay-v4-transition.sh",
    "docs/process_traces/2026-08-26-t26-s3/raw/**"
  ],
  "unowned_dirty": [],
  "verdict": {
    "cause": "confirmed",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "sh docs/process_traces/2026-08-26-t26-s3/replay-characterization.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "sh docs/process_traces/2026-08-26-t26-s3/replay-mutations.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "sh docs/process_traces/2026-08-26-t26-s3/replay-historical-anchor.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "sh docs/process_traces/2026-08-26-t26-s3/replay-v4-transition.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_arm_readiness_evidence_packauth.ProjectedPackAuthenticationTests.test_projected_pack_authenticates_through_the_composed_check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 1.240s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "for f in docs/process_traces/2026-08-26-t26-s3/replay-*.sh; do sh -n \"$f\" || exit; done",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --porcelain -- . ':(exclude)docs/process_traces/2026-08-26-t26-s3/**'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The /tmp v4 state-transition probe deliberately omitted U11 and therefore minted a schema-valid REFUSE freeze-0004, not a real PASS transaction; it proves pre/post-receipt generator control flow only. The projected authentication path is separately covered by V5 and existing S0 estate evidence.",
      "needs": "Lead retains final verification of the real projected §3.2/§3.4/§3.6 operator transaction."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The local origin/main tracking ref advanced during the session from 954328078194b557af967505ef88edea6aa56d27 to 3109c0dc960a21c4ec0881b8a9f725995224ebe1 while HEAD stayed fixed; no fetch or network operation was run and no out-of-scope worktree path changed.",
      "needs": "Lead should review against the recorded fixed HEAD and rebase only in its own merge lane."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Recorded-anchor verification requires full local Git history; shallow or pruned operator checkouts must continue to refuse through the existing histsem vocabulary.",
      "needs": "Implementation must keep missing-history behavior fail-closed."
    }
  ]
}
```

## Causal chain

Successor emission rewrites the family suffix but inherits
`CURRENT_FROZEN_RECEIPT_SHA256`. Once the successor's own receipt is committed,
the constant names the predecessor, `freeze_aware_status` reports frozen, and
bare/no-preserve current-target checks refuse. Ordinal 1 has the opposite
problem: its constant matches, so bare mode defaults to preserve; preserve
copies declared current bytes and `check_current` compares those copies with
their source. Executed mutations show that science, calibration-plan,
plan-tree, and pinned-external-input drift survive that echo, while inventory
and plan-to-freeze binding changes are caught.

The important qualification is historical. All three ordinal-1 PACK_AUTH
sources record pre-freeze commits whose generators had no echo capability.
Replaying those exact commits returned 0 and reproduced each source's recorded
pack digest. The existing historical-semantics pinset already composes those
derivation coordinates with exact current-tree digests and a closed custody
delta. The current CLI is tautological; the frozen evidence's original
derivation was not.

Premise 6 was also overbroad: current ordinal-1 generator bytes do not match
their plan generator pins, no freeze receipt embeds its own final tree digest,
and S5 pins only the three v3 final trees. Exact derived values are in
`raw/pins/` and `characterization.md`.

## Remediation

For A93, stop authentication from depending on the receipt constant. Invoke
modern derivation anchors with explicit no-preserve, capability-check legacy
anchors, and AST-record the current constant relationship as a non-authoritative
diagnostic. A stale constant must be visible but must not invalidate a sound
anchor composition.

For A94, use the PACK_AUTH source/receipt's already-authenticated `head_commit`
as the regeneration anchor; do not search history. Re-run the pinned generator
at that no-freeze coordinate and compose its result with existing histsem K5,
K12, binding, and closed-delta checks. Classify any current preserve check as
`echo_integrity` and forbid it from independently setting the generator PASS
claim. This requires no frozen-byte, generator, receipt-schema, or runsheet
change and leaves the `_v4` mint sequence unchanged.

## Disproved alternatives

Refreshing the constant cannot be an atomic cure: the future receipt digest is
unknown when the successor generator is emitted, and editing after mint changes
frozen, pinned bytes. Hard-refusing a stale AST value also fails the transaction
timeline: there is nothing current to compare at §3.4, then every existing
successor would refuse after §3.6. Comparing echo output to the current pack is
the demonstrated tautology. Searching for a regeneration ancestor is sound but
unnecessary because the authenticated source already names it. A new
plan-tree/freeze schema could strengthen future binding but cannot retrofit the
nine packs and would unnecessarily invoke D-153 during the open `_v4`
transaction.

## Residual risk

The implementation must preserve legacy receipt compatibility and the exact
six-key predicate: adding a required `derivation_mode` fact would invalidate
frozen receipts. Put new mode/constant diagnostics in source checks or verifier
output. Historical replay also depends on full local Git objects and must refuse
cleanly when they are absent. The lead still owns live projected `_v4`
verification; the synthetic state-transition probe is not a mint substitute.
