# Ruling 40b — D-165 close-out core delta re-audit (luna max, report 40: REFUTE)

Magistrate ruling, 2026-09-01, on `feat/d165-dominance-closeout-core` @ `88e96f60`. Delta seat:
luna (report `40-luna-delta-closeout.md`); fixers were Sol (round 1, report 31) and terra
(round 2, report 35) under ruling 31c. Every ruled item (T-F1, T-F2, L-F1 as re-ruled, L-F2…L-F6)
is implemented with its named refusal spelled exactly and selecting neither branch; the
registration hash is unchanged (`1c0a4a11…`); `analysis_manifest_v3.py` and
`floor_extraction.py` untouched. The delta seat could not run the suite (no temp dir); the
bench reran it — see below. This is a THIRD round on L-F1's lineage cure → cold-gate trigger;
the cold seat's verdict is appended below.

## Dispositions

| Finding | Severity claimed | Ruling |
|---|---|---|
| F1 — validator hashes `replay_sidecar_bytes` but validates a separately supplied `replay_sidecar` mapping; a forged mapping paired with the authenticated bytes licenses Branch A | blocker | **ACCEPTED as blocker — but as an EVIDENCE fence, not an adversary fence.** Under D-161 the question is whether an honest caller can trip it: yes — any builder that decodes the bytes once, post-processes the dict (rounding, key reordering, a future "normalise" helper) and passes both channels would validate a mapping that is not the authenticated artifact. Cure: **single channel.** The consumer takes bytes only (`finalized_manifest_bytes`, `replay_sidecar_bytes`) and decodes them itself; the mapping parameters are removed from the public API (the builder in `scripts/build_d165_dominance_closeout.py:184` reads the files and passes bytes). If a decoded-object parameter must remain for test ergonomics, it is keyword-only, private-prefixed, and the validator refuses `replay_sidecar_object_bytes_mismatch` (neither branch) when its canonical JSON differs from the decoded bytes — but the single-channel form is preferred and the report must say which was chosen and why. |
| F2 — unhashable census / block-id inputs raise `TypeError` instead of a named refusal | should-fix | **ACCEPTED.** Type-guard every set/map element before hashing; named refusal `closeout_input_malformed: <path>` selecting neither branch; one regression per site (`:333`, `:1046`, `:1216`). |
| F3 — top-level `closeout.replay_sidecar_sha256` guard has no isolated test; partial-attachment and schema-mismatch cases not asserted by exact reason | should-fix | **ACCEPTED.** Three tests: mutate only `closeout.replay_sidecar_sha256` (exact source-byte-hash reason); partial attachment (each missing key → `manifest_lacks_replay_sidecar`); `schema_version` mismatch → `replay_sidecar_identity_mismatch`. |
| F4 — contract first-use failures (`sidecar`, `close-out builder`, `lineage`, `census`, neither-branch) and no runnable CLI invocation | should-fix | **ACCEPTED.** Contract gains a glossary-at-first-use pass and the exact invocation `python3 scripts/build_d165_dominance_closeout.py --finalized-manifest … --floor-artifact … --replay-sidecar … [--output …]` with the `output_already_exists` refusal stated. Ed's writing standard applies verbatim. |

## Round-3 shape

Fixer: Sol xhigh (round-1 author; terra wrote round 2; luna audited — the fourth family is not
available as a Codex seat, so Sol returns with the narrowest brief). WRITE_SCOPE
`joulewise/dominance_closeout.py`, `scripts/build_d165_dominance_closeout.py`,
`tests/test_d165_dominance_closeout.py`, `docs/contracts/d165_dominance_closeout.md`. Delta by
Opus 5 (contract lens) — a family that has not yet touched this branch.

## Bench verification of the refuted head

Magistrate, 2026-09-01, `wt-closeout` @ `88e96f60`, clean tree:
`python3 -m unittest tests.test_d165_dominance_closeout` → `Ran 18 tests in 9.798s / OK`;
registration hash (canonical JSON of `dominance_criterion_registration()`) =
`1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b` (unchanged). The suite being
green is consistent with the delta seat's REFUTE: F1 is a missing check, not a failing one.

## Cold-gate verdict

Cold Fable seat (fresh session): **RESHAPE** — full text in `48d-COLD-GATE-2-verdict-40b-45b.md`.
The seat REPRODUCED F1 with a probe (self-consistent forged mapping + authentic bytes → Branch A
licensed, validator errors `[]`); the CLI (`scripts/build_d165_dominance_closeout.py:197-237`)
is single-source, so the exposure is API-only. Magistrate disposition (2026-09-01, adopted):

- **F1 label AMENDED**: a C-mistake under D-161's mistake-vs-deliberate test ("tool's own bugs"
  stay fail-closed), not an "evidence fence"; severity = must-fix API soundness, no claim
  exposure at `88e96f60`. **Cure = bytes-only for ALL THREE sources** (`finalized_manifest_bytes`,
  `replay_sidecar_bytes`, and `floor_artifact_bytes` — the floor is currently mapping-only and its
  digest is already sealed at `analysis_manifest_v3.py:3649-3654`; check it, three lines). The
  keyword-only-object alternative and report 40's "compare decoded objects" alternative are
  **STRUCK** (deliberate-only guards). Tests mutate the dict and re-encode via a named
  `mutate_then_encode` helper.
- **F2 cure AMENDED**: one `try/except TypeError` per entry path → one named refusal
  `closeout_input_malformed: <path>` (neither branch); one regression per entry path, not per site.
- F3, F4, fixer Sol xhigh, delta Opus: agreed. Delta brief adds an API-surface assertion (no
  mapping parameter remains public) and the forged-pair probe re-expressed as "built from bytes X,
  validated against bytes Y".
- Missed 2 acted on at the bench: `main` merged into the branch (`057660e1`, suite OK) before
  round 3 launches. Missed 3 (producer→finalizer custody unproven until `D165-SIDECAR-EMIT-01`;
  paper cannot cite a close-out before it) → kernel-row check queued.
- Structural: no shared defect signature across rounds (round 1 NEEDS_RULING, round 2 faithful,
  delta caught the cure's defect); the repeated META-pattern is briefs leaving interface SHAPE to
  the fixer → round 3 carries the shape as a decision.
