# r6 fix round — the `110-tamper-freeze-json` expected pair, AMENDED

Magistrate ruling over the PR #194 refutation round. One contradicted pair; both
seats' replays agree on the correction.

## The contradiction

`01-sol-consult.md` predicts, for the `freeze-json` tamper class:

> `[readiness_freeze_receipt_mismatch]`, detail `"plan freeze reference is not exact"`

derived from the exactness comparison at `arm_readiness.py:6503-6506`. The
refuter REFUTED that pair, and the derivation is not in dispute once stated:

**`generate_freeze_receipt()` filters scanned receipts by the plan's pin before
`_load_freeze_reference()` ever runs.** At `arm_readiness.py:6848-6862` (BASE
`5a034f84`), immediately after the namespace scan authenticates every sidecar,
each scanned receipt's `{path, sha256}` pair is compared against the plan's
recorded freeze pin, and any receipt that disagrees is refused there. The
`freeze-json` tamper bumps `issued_at_utc` AND recomputes the receipt's own GNU
sidecar — that recomputation is what lets it past namespace authentication, and
it is also precisely what changes the receipt's `sha256` away from the plan's
pin. So the tampered receipt is exactly the receipt the plan-pin filter
rejects. The exactness check at `:6503-6506` is reached only by a receipt that
has already SURVIVED plan-pinning, which this one cannot.

**Corrected expected pair, ruled:**

| field | value |
|---|---|
| `rc` | `2` |
| `reason_codes` | `["readiness_freeze_receipt_mismatch"]` |
| `detail` | `existing freeze receipt is not plan-pinned` |

The refusal CODE is unchanged; only the DETAIL moves, from the exactness raise
to the plan-pin raise. Because r6 asserts `detail` by equality rather than by
substring, that distinction is load-bearing: under the consult's pair the cured
probe would have failed estate 10 on a correct mechanism.

## Standing of the two records

**`01-sol-consult.md` stays VERBATIM. It is not edited, annotated, or
corrected.** `02-MAGISTRATE-ADJUDICATION.md` accepted the consult with the
explicit clause that its expected `reason_codes` and details "are code-derived
predictions whose confirmation is estate 10's job — a mismatch there is a
finding, not an improvisation license." This is that clause operating exactly as
written, one estate earlier than anticipated: the mismatch was found by a
refuter's re-derivation rather than by an execution, it was adjudicated rather
than patched at the bench, and the consult record stands unaltered as what the
seat actually said. **The amendment is ruled by the magistrate on the two
concurring derivations** — the refuter's and the replaying seat's, reached
independently and agreeing on both the ordering and the corrected detail
string — and the corrected pair, like the seven it sits beside, remains a
code-derived prediction that estate 10 confirms by execution.

## Where the cure lands

`docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md`, one coherent edit across
three sites plus the revision-history entry:

1. the `110-*` block's expected dict (`freeze-json` row);
2. the §4(e) class table's freeze-JSON row and its narrative bullet, which now
   names the plan-pin filter and says why the exactness check is unreachable
   here;
3. the §5 V-1.vi pre-fixation bullet.

## Flag dispositions recorded, not cured

- **R1 — `tamper_class.py` is written then `chmod 0555`, so a same-estate re-run
  of the `110-*` block cannot rewrite it.** No cure: the fresh-estate-only rule
  stands, and a same-estate re-run is already out of contract under §6, so the
  `0555` mode is the rule being enforced rather than a defect to route around.
- **R3 — what `123-c-to-s-later-rewrite` evidences is now narrower than its
  ordinal suggests.** Recorded as a limitation: it evidences the C→S edge
  reached through the `arm` ENTRY POINT, and nothing about marker replay. The
  marker lane's own C→S enforcement is evidenced separately (§3.10's `151-*`
  publication-lane replay); `122-*` and `110-tamper-pinset-json` remain the
  primary C→S vehicles, as `02-MAGISTRATE-ADJUDICATION.md` ruled.

## Also in this fix round

§0.2's PROSE anchor table rows 7-9 still carried the pre-D-154 coordinates
`6410`/`6680`/`6721`; they are corrected to `6475`/`6749`/`6790` per the
D-154 `+65`/`+69` piecewise remap. The remap had already been applied to the
embedded AST checker's `ANCHORS` tuple in §1.1 — which is why the map still
returns 15/15 — and the visible table was missed because its cells are bare
numbers that no mechanical check reads. The two now agree.

— Fable 5, magistrate, 2026-08-25.
