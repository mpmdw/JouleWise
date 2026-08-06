# Synthesis — COLDGATE-VALIDATOR-01 F3 design consult (2026-08-05, Fable magistrate)

## Why this consult existed

Rule 11 standing escalation trigger: three consecutive fix rounds failed
with the same F3 signature (absolute-path bypass of the attestation
privacy denylist; final bypass `cwd='/ secret'` → PASS receipt leaking
the path). The mandated next spend was a consult on the closure shape,
not fix round 4. Consult ran read-only Sol against
`impl/coldgate-validator` @ 38b6570 with the concurrent oversight audit
(cgv-audit-B) as reframing input.

**Effort-tier deviation record:** rule-10 tier for a design-bearing
consult is xhigh; Ed's standing Sol-HIGH-only directive controls; `high`
applied. Recorded at launch, in the manifest, and here.

## Magistrate's pre-consult analysis (upheld)

The `input / output` acceptance requirement and the privacy invariant
are mutually unsatisfiable: POSIX filenames may contain any byte except
NUL and `/`, so every `/` — including a space-surrounded one — prefixes
a legal absolute path (`input / output` itself contains the legal path
`/ output`). No denylist regex closes the class while that acceptance
test stands. Sol concurred formally (confidence 0.98) and sharpened the
conclusion: the correct cure is not a better filter but deleting the
channel, because self-asserted free text discriminates no registry
invariant.

## Adjudicated decisions (adopted; no dissent recorded on either side)

1. **F3 closure = Option D, deletion.** Both attestation CLI options,
   the `convening_attestations` receipt member, `ABSOLUTE_PATH_RE`, and
   the string-privacy preflight are removed. Receipt privacy stays
   structural (no raw CLI paths serialized; relative/basename-or-ordinal
   representations; RECEIPT-PRIVACY regression). No replacement global
   path regex. If a future registry ruling wants receipt-level convening
   state, the fallback is closed ASCII enum tokens, never prose.
2. **B1 (PASS does not bind the judge to validated bytes) splits:**
   - In-branch: receipt schema v2 with `binding_scope:
     validation_time_observation_only` + `judge_handoff_bound: false`;
     PASS redefined as a validation-time observation, explicitly not
     launch authorization; `--receipt-out` removed (persistence is
     runner-owned).
   - Follow-on: **COLDGATE-HANDOFF-01** (runner-owned, BLOCKING for
     operational use) — immutable snapshot-to-judge byte binding, with
     Sol's warning preserved: open descriptors do NOT seal bytes
     (same-inode mutation), and path-based revalidation leaves a
     revalidate-to-read race. Kept separate from CGV-HARDEN-01 by
     design (different contracts, tests, failure consequences) — though
     CGV-HARDEN-01's receipt-write scope migrates runner-ward with
     `--receipt-out`'s removal; both rows to be registered together.
   - **Operational constraint, standing until COLDGATE-HANDOFF-01
     lands: no validator PASS may be used to convene a cold judge.**
3. **S1 (fence-unaware parsing) and S2 (--help receipt violation) fix
   in-branch now**; --help becomes a conventional exit-0 informational
   path exempted from the receipt contract; every other nonzero exit
   emits exactly one JSON refusal receipt.
4. **Test prune** per oversight audit + consult: internal call-shape
   assertions removed; independent packet digest and
   dirfd/symlink/hard-link custody tests retained.

## Magistrate scope ruling (deviation from the consult's letter)

The consult asked for registry (`docs/process/coldgate_charter_registry.md`)
and state-kernel acceptance amendments in the fix scope. That document
is Ed-ratified; amending it is a rule-11 cold-gate trigger. Ruling: the
fix round touches only the validator and its tests; the registry
amendment text (separating validator observation from runner custody)
is registered WITH the COLDGATE-HANDOFF-01 row and routes through
ratification. Until then the branch's honesty lives in the receipt
fields, the module documentation, and the queue row — which satisfies
Sol's rank-3 refusal of "documentation-only limitation with no blocking
operational row" because the blocking row is registered.

## Disposition

Fix round launched same session (workspace-write, high, WRITE_SCOPE =
validator + tests only). Landing gate: lead unpiped test replay → delta
re-audit (C-028) → PR under the operation-loop §5 shape.
