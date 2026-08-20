# Gate-1 fix gauntlet — two-refuter synthesis (magistrate ruling, 2026-08-20)

## Subject

Commit `60ddb03` — the post-mint successor-emission residue fix
(test-only: mint-custody overlay in `tests/test_d117_v3_family.py`).
Implemented by Sol (high) under WRITE_SCOPE
`["tests/test_d117_v3_family.py","joulewise/**"]`; report
`sol-fix-report.md` (this directory). Lead reviewed the full diff before
commit.

## Refuter round (severity-tiered, distinct lenses)

1. **Terra (high), execution lens** — `terra-refuter-report.md`.
   Verdict REFUTED with a claimed blocker: after custody seeding,
   generator `--check` exits 0 even when the seeded
   `arm_readiness.evidence/evidence-multicell-mint.json` has its
   `pack_sha256` replaced with 64 zeroes (executed, all three
   families). Its other attacks failed: generator-owned byte
   corruption and custody-file deletion both still fail closed, and
   the new `missing=order_manifest.json` assertion is discriminating.
2. **Sol (high), contract lens** — `sol-refuter2-report.md`.
   Verdict: not a blocker against `60ddb03`. Dispositive evidence:
   the ruled S3 `--check` passed BEFORE any evidence or freeze
   receipts existed (`S3-emission-report.md:91-104` vs `:154-162`),
   so receipt semantics were never check-mode's contract; the frozen
   checker only builds an inventory from custody JSON
   (`d117_floor_qwen25_1p5b_v2/generate_configs.py:2560-2629`). No
   authority assigns receipt-integrity validation to generator check
   mode. The fix weakened nothing (at `afb7d57` the property was red,
   not proven) and added the non-emission proof + fail-closed
   regression.

## Magistrate synthesis

- The execution-lens observation is TRUE but MISATTRIBUTED: it is
  pre-existing frozen-checker behavior, untouched by `60ddb03`
  (`git blame` places the relevant `arm_readiness.py` regions in the
  §5C D-134 and R1-lifecycle commits, both before `7d4454e`), and
  receipt integrity is owned by the arm/consume authentication chain
  (`_authenticate_generic_evidence_item`,
  `joulewise/arm_readiness.py:4163`, refusals at `:4189-4215` and
  `:4248-4262`) plus D-134 disk-vs-git digesting (`:2553-2564`).
  **Finding reclassified: non-defect of the fix.**
- **`60ddb03` STANDS.** Gate-1 fix accepted; full canonical at the fix
  head is the remaining gate-1 input.
- The contract-lens pass surfaced a REAL pre-existing should-fix,
  **C1**: legacy frozen PACK evidence replay authenticates exact
  nested bytes but never validates the receipt's historical
  `pack_sha256`/`head_commit` (expected values supplied only for
  WINDOW_CUSTODY LAUNCH_RECIPE at `:6863-6879`; freeze minting passes
  `None`/`None` at `:5507-5528`). A coherent multi-file rewrite could
  keep the byte chain internally consistent while carrying false
  historical semantics. Mitigations already in force: D-134
  disk/git comparison, published S5 confirmation digests, and every
  claim-bearing route traversing arm/consume lineage authentication.
  **Registered as queue row A64 (RECEIPT-HISTSEM-01), not a merge
  blocker.** Closure shape (from the report): an external governed
  verifier/pinset that recomputes each legacy receipt's historical
  pack digest from its recorded `head_commit` and validates the full
  receipt → sidecar → freeze → plan binding, in CI and pre-arm.

Both refuter reports and the implementation report are in this
directory; the D-144 seat-pass terra report (`terra-seat-report.md`)
is co-located pending the seat-pass ruling record.
