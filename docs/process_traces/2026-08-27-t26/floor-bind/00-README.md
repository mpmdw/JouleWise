# FLOOR-BIND-01 scope check and design consult (T26, 2026-08-27)

Two read-only Sol xhigh sessions plus lead-side verification, run to answer one
question: is queue row FLOOR-BIND-01 — minted 2026-07-22 from D-078 clause 8,
blocker CR9-1, registered limitation L1 — still live after thirteen months of
instrument change, or has the mint-side hardening since superseded it?

**Answer: partially superseded. The producer half is closed; the consumer half
is open exactly as CR9-1 described it.** Magistrate ruling on the sequencing is
Option 1 — implement after `_v4` mint closure, no pre-mint coupling.

## The two artifacts here

| File | What it is |
|---|---|
| `p0-scopecheck.md` | Sol xhigh read-only scope adjudication: per-acceptance-item classification (E1/E2/E3), the traced claim-consumption edge, the S/O attack walkthroughs, the existing-regression census, and the (b) PARTIALLY SUPERSEDED verdict. |
| `design-consult.md` | Sol xhigh read-only design consult, one bounded round with explicit license to disagree. **Section D6 is a ready-to-execute implementation contract** — exact files, projection dataclasses, refusal-reason strings, nine named regressions, and the four existing tests that break. |

## Terms used below

- **Claim consumption** — the code path a claim-bearing analysis run takes when
  it is handed a floor-artifact JSON: `cli.py _cmd_analyze_claims` →
  `analyze_claims` → `load_analysis_inputs` → `authenticate_floor_artifact_bytes`
  → `validate_floor_artifact`, then `bind_floor_artifact_evidence`. This is
  distinct from **mint time**, the path `scripts/mint_floor_artifact_generalized.py`
  takes when it *creates* an artifact.
- **Self-attesting** — an artifact whose claimed quantities are checked only
  against other fields of the same artifact, so an internally consistent forgery
  passes. CR9-1's charge against the floor artifact.
- **Admissible half-width** — the per-member half-width, in joules, that widens
  a floor to its conservative corner. Understating one understates the floor,
  which licenses a smaller energy difference as a real claim.
- **Repository pinset** — a repo-committed, human-reviewed JSON file under
  `scripts/floor_mint_pinsets/` that records, outside the artifact, what the
  artifact's numbers are supposed to be.

## Finding 1 — what is superseded, and what is not

Superseded (mint time): S5 contract Q4 (element-for-element report-width
closure), W6 (mint rebinds members to source bytes and verifies report widths and
membership before any builder call), W3 (component-scoped provenance pins), and
the D-117 / D-120 postcollection trust closure. Together these protect every
artifact the mint *produces*.

Not superseded (claim consumption). A claim run handed a pre-existing JSON
invokes none of that:

- the extraction report's bytes are never read — its SHA in component provenance
  is only syntax-checked as 64 hex characters (`joulewise/detection_floor.py:3472`);
- admissible half-widths are taken from the artifact's own
  `admissible_half_widths_j`, and `_validate_estimate_math` recomputes the
  widened corner *from that same array* (`joulewise/detection_floor.py:3106`);
- complete governed campaign membership is not enforced —
  `_campaign_order_binding_problems` proves each *artifact-listed* member occurs
  once and in order, never the converse, that every governed member appears
  (`joulewise/analysis_engine/inputs.py:1522`).

## Finding 2 — the reviewed pinset is read, authenticated, and then discarded

`validate_floor_artifact` already resolves and authenticates a reviewed
repository pinset for the artifact's family, and a family with no matching pinset
is a hard refusal (`_resolve_evidence_root_ids`,
`joulewise/detection_floor.py:2699`). `scripts/floor_mint_pinsets/mint1.json`
pins, per component, `evaluation_basis_sha256`, `evaluation_basis_members`
(37 / 47), `extraction_spec_members` (30 / 40), `expected_n` (10),
`drift_allowance_j`, `order_manifest_id`, and per cell
`operative_floor_six_decimal` (`"7.377086"`).

Every one of those is validated for *pinset-internal* consistency by
`_project_floor_mint_pinset_v2` and then thrown away: the projection returned to
the artifact validator carries only `family_identities` and `evidence_root_ids`
(`joulewise/detection_floor.py:2059`, `:2601`). Nothing is ever compared against
the artifact.

**Lead-executed proof (inert-pinset proof).** Against the real frozen pack
`df-ph-decode-floor-mint1.json`, which validates clean at baseline, six single-
field mutations were made to a copy of `mint1.json` and supplied through the
explicit pinset route (`validate_floor_artifact(artifact, pinset_path=...,
expected_pinset_sha256=...)`). All six returned an **empty finding list**:

| Mutated pin | Pinned value → mutated value | Result |
|---|---|---|
| control: unmodified, reserialized | — | CLEAN |
| `cell.operative_floor_six_decimal` | `7.377086` → `9.999999` | CLEAN |
| `absolute.expected_n` | `10` → `999` | CLEAN |
| `absolute.extraction_spec_members` | `30` → `999` | CLEAN |
| `absolute.evaluation_basis_members` | `37` → `999` | CLEAN |
| `comparative.drift_allowance_j` | `0.5812720449734456` → `42.0` | CLEAN |

A reviewed pin asserting the operative floor is 9.999999 J does not disturb an
artifact whose floor is 7.377086 J. The pins are inert against the artifact
today.

## Finding 3 — pinned floor literals alone cannot close the width attack

The cheap cure suggested by Finding 2 — compare the artifact's operative floor
to the pinned six-decimal literal — was proposed by the lead and **refuted by the
consult with a repro**, which is why it is recorded here rather than built.

**The ×0.99999999 six-decimal collision.** Scaling one component's admissible
half-widths by 0.99999999, then recomputing every derived field so the artifact
stays internally consistent, moves the exact operative floor

    7.377085735735073  →  7.377085672752914

Both render as `7.377086` under `.6f`. `validate_floor_artifact` returns no
findings, and a six-decimal comparison against the pin would not either. A second
survivor needs no rounding luck at all: a width that is not the maximizing corner
can change while the component and operative floors stay bit-identical, because
the floor is a maximum over corners.

Acceptance item E2 requires refusal on *any* stored width or corner mismatch, so
comparison against rendered floor literals can never discharge it. Closing the
width attack needs the v2 pinset's exact component-artifact digest (the component
serialization includes the width arrays, so any width edit moves the digest) —
and closing membership deviation of the omit-one-and-substitute-another shape
needs the v2 pinset's exact `(bundle_id, config_sha256)` member dispositions.

## Finding 4 — why this is sequenced after the `_v4` mint

Neither half of the sound cure can land now:

1. **The precondition does not exist.** `scripts/floor_mint_pinsets/` contains
   only `mint1.json` (schema `joulewise.floor_mint_pinset.v1`) and
   `schema_v2.json`, which is a JSON Schema, not a pinset instance. The final v2
   pinset instances carrying component digests and member dispositions are a
   **U10 postcollection obligation of the `_v4` mint itself**
   (`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:465-467`).
   Building the consumer against a shape U10 freezes *during* the mint either
   breaks the mint or ships a dead gate.
2. **Both halves touch the open transaction.** The validator half tightens
   `validate_floor_artifact`, which the mint itself calls
   (`scripts/mint_floor_artifact_generalized.py:3339`). The replay half adds a
   `--floor-extraction-spec ROOT_ID=PATH` input that is hard-required for
   claim-bearing runs, which would gate the imminent `_v4` claim run.

Registered limitation L1 continues to mitigate in the meantime, and it already
governs the mint: a claim-bearing analysis may consume a floor artifact only when
the governed extraction ran in the same custody session.

## Two residuals for a post-`_v4` named decision

1. **E1 is not discharged by the pinset route.** E1 requires binding to the
   extraction report and source-member disposition, or rederivation of extraction
   gates and widths. A reviewed pin is a third anchor, neither of those. Consult's
   sentence, verbatim: *"Claim consumption proves that the artifact matches
   reviewer-frozen assertions, but still cannot independently prove that those
   assertions match the governed extraction report and source bytes."* Closing the
   row on the pinset half alone would need an explicit amendment to E1.
2. **The replay half breaks four claim fixtures.** Making
   `--floor-extraction-spec` hard-required for claim-bearing runs breaks
   `tests/test_analysis_integration.py:541`, `:1944`, `:3580`, and `:3585`, which
   currently succeed at claim consumption with a floor and evidence roots but no
   extraction-spec mapping. They must be re-fixtured with governed synthetic
   extraction specs and matching final-pinset pins in the same change.

## Reading state at the time of this record

Both Sol sessions read the tree at `51ed8817`; `origin/main` advanced to
`95432807` while they ran. Nothing in the findings is head-sensitive — the cited
functions are unchanged — but the implementation must be rechecked against the
then-current head when it is scheduled.
