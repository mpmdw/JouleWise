# Qualification drafts use public freeze-2 authorization

**2026-11-18 · Tier 2 [AGENT] · DRAFT / HOLD_FOR_FIT_FREEZE**

Built on `align/2026-11-18-qual-public-freeze-gate` at audit tip
`6c1076f25f22b4b1a0a3038244e4498b62292746`. Audit advanced one commit
from spec base `09c77ae4fc9ae66526dbf752fbd283d8030469a5`.
Both revisions have draft tree `200bd9f4489cfe95cba6bae8883e341c6c5e44d4`
and identical governing rulings. GitHub had no builder branch or PR at
intake. Scope was the ordinary public-`yes` item adapter and synthetic
verification on the Air.

## Red first

Tests-only commit `b9af98ad5ca2447306ec719d370752b3df1f0ab9` ran the
standalone regression against the unmodified generated items through the
test runner. The runner and its standalone test exited 1 as expected.

```sh
D=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-1118
S=$(mktemp -d "$SEAT_DIR/item-freeze-frozen.XXXXXX")
TMPDIR="$S" JW_DRAFT_EVIDENCE_DIR="$S/log" bash "$D/tests/run_all_gates.sh"
# The runner invokes the standalone regression.
# python3 -B tests/test_freeze2_public_arm.py --scratch "$SCRATCH_DIR/arm"
```

Both bash and zsh exited 0 from the old gate and printed
`FREEZE2 COMMITTED b99b880d640ae64d11e10c4c44a825648f11b220 ordinary-public-note.txt sha256 edb3ae1a6f63ef067f570167fe9aaab4d4e661a0764ae3e3e5f3da6017c29a2a`.
The synthetic main commit `6fab50d7819df1b468882a35af3ca1cd85a0f685`
had no public decision. The later note existed only on synthetic audit at
`b99b880d640ae64d11e10c4c44a825648f11b220`.
The observer logged zero forbidden lookups in both shells. The assertion was
“an audit-only ordinary text blob with no public decision on main must refuse.”
The separate specification packet used synthetic red commit
`109ef0a3a91cd5237ffea41790fc9ad77471abc5`.

## Build and verification

Adapter commit `0d1b5c9f11fc9d2a39fa15668500e169ee51d1ab` replaces
the caller-selected commit and file with the issued public commitment for
`lm-interim-01`. Start and Run each refresh explicit `origin/main` and
audit tracking refs. The common gate calls the public CLI with the issued
hash, stages regular Python blobs at the reviewed revision when available,
and uses the pinned interpreter in isolated mode. The emitted adapter
holds while the owner-supplied revision and import closure are pending.
Synthetic provider code lives in the test fixture.

The generator's `--output-dir` mode writes qualification artifacts into
a new scratch directory. The default path retains the standing renewal,
queue expiry and planner behavior. The test repeated generation with the
base dates, source and expiry. The three kits and three queues match their
complete base blobs. Each of the three exact 38-path maps matches the
PR #812 pin, including every member's SHA-256 and Git blob OID. All six
renders match on repetition. The remaining item text and shell are
byte-identical after accounting for the freeze and ref-refresh edits.
This preserves the separate q0 hand-read and soak admission and the
existing date, t0, predecessor, close and launcher rules.

| Finding | Commit | Regression and result |
|---|---|---|
| An audit-only ordinary blob authorized the old item. | `b9af98ad5` | The standalone audit-only assertion failed as expected in both shells, with zero forbidden reads. |
| Both entry points need fresh public authority, an isolated code pin and the issued hash. | `0d1b5c9f1` | PASS in bash and zsh against the synthetic CLI. Cases cover ordinary `yes`, registered and malformed siblings on both ledgers, closed report and digest bindings, public routes, dirty checkout sources, incomplete code closure, and revised, withdrawn or missing main evidence at Run after a successful Start. A fresh-fetch failure prevents the gate from running. |
| The read observer must catch direct opens, metadata probes and Git-blob lookups. | `0d1b5c9f1` | PASS for the injected open, stat and Git mutations. The observer blocked them before access and reported zero forbidden lookups on ordinary paths. Its test assertions distinguish interpreter imports from evidence access and keep traceback bookkeeping out of the denial count. |
| The common gate must reach all six drafts without changing the kit or arm law. | `0d1b5c9f1` | PASS for `--compare-regen`, all three kit and queue comparisons and the base-to-head whitespace check. |
| The naming exception needs authenticated committed evidence. | Pending owner delivery | The adapter contract test passed for the in-memory verified response and refused the wrong hash. The in-memory decision check also refused wrong ID, look and purpose. The committed case remains **HELD — Fable representation**. |

The handoff commit also adds the source-root check to the regeneration
comparison. It checks both the committed range and tracked working-tree
changes under `joulewise`, `scripts` and `configs`. Regeneration passed
with that check enabled.

The focused suite passed 74 shell syntax checks, 57 Python compilations,
91 pinned kit and mock checks, 1,480 exact rendered-gate assertions,
21 standing checks, nine Round 10 tests and 13 generator checks. The
rendered-gate test ran in 12 scratch jobs, one per item and shell, with
the existing assertion bodies and only their dispatch restricted by
job. The duplicate serial aggregate had reached the gate matrix at
handoff. Its completed pinned and standalone results are included below.

## Evidence in the assigned seat

| Artifact | Location within the seat |
|---|---|
| Frozen red log at the tests-only commit | `item-freeze-frozen.WqWeof/runner.log` |
| Bash/zsh synthetic decision matrix and aggregate verification logs | `item-freeze-suite.xjWzQ2/log/` |
| Twelve rendered-gate jobs and standing, Round 10 and re-dating results | `item-freeze-parallel.B6GG6B/` |
| Two real builder generations and exact base comparison | `item-freeze-regen.COeG9n/regen.log` |
| Generated six-item diff, SHA-256 `50c03806660c8b5d7c0b73d991afdfbbf3f7f35236e8e653d931b670bbf9e52f` | `item-freeze-build.KiXnNb/generated-items.diff` |

## NEEDS_SPEC and next handoff

The designated lead routes this question from the specification to Fable.

> What committed public bytes, at what canonical path and revision, prove that the `ruling` ID on the `lm-interim-01` mainline ledger row is Fable's explicit decision to name this exact 64-hex `coefficients_sha256` as freeze 2? How does the public verifier authenticate the ID, look, digest and act of naming from those bytes?

Option A is a structured public record referenced by the row's ruling ID.
Fable specifies its authoritative path, format and provenance rule.
Option B is a canonical stanza in Fable's ruling text. Fable specifies its
exact syntax, authoritative revision and the commitment on main that binds
the stanza. Both choices bind ID, look, digest and the freeze-2 act. The
specification recommends A.

The PR #795 interim owner and PR #828 integration owner deliver the
reviewed public CLI revision, exact dependency closure and mixed-ledger
compatibility evidence. The lead records the red in the lead issue and
routes the reviewed interface to the rehearsal seat. The item builder then
binds the delivered revision, regenerates the six drafts and repeats both
phases against that exact CLI. Final admission also requires the committed
synthetic naming vector and its wrong hash, ID, look and purpose cases.

The current branch is local. No hosted checks exist for this head. The
quick and canonical shard suites and the independent Astra candidate audit
belong to the integrated head. This run verifies draft generation and
synthetic gates on the Air. Qualification remains at `HOLD_FOR_FIT_FREEZE`.
