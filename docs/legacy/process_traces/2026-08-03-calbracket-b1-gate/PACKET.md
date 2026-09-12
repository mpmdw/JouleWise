# Rule-11 gate packet — CAL-BRACKET-D079-01 audit blocker B1, proposed fix round 2

Assembled: 2026-08-03 (late evening), by the lead session, MECHANICALLY:
every substantive statement below is a quotation or a checkable repo
fact; the lead's own views are confined to §7 and labeled as such.
Tracked per D-111 from birth.

## 1. Trigger (mandatory, not discretionary)

CLAUDE.local.md rule 11: "any second fix round on the same defect"
convenes the cold gate. Audit blocker B1 has had one fix round
(commit `2e61ff96ea80186efa71efb9c9f6f00a16a70019`); the delta
re-audit finds B1 persists in refined form. Round 2 on B1 is therefore
gate-first. The standing two-consecutive-rounds-same-signature
escalation trigger has NOT yet fired (one failed round on B1, not two);
if round 2 fails with the same signature it fires.

## 2. Question presented

1. Is fix round 2 on B1 licensed, and in what shape? The gate rules on
   the repair approach, not just yes/no.
2. What regression shape must round 2 carry so that the round-1 test
   gap (see §5, "the new tests miss this interaction") cannot recur?
3. Bench vs delegated: D-109 landed as a Sol-delegated stream;
   rule 9's bench-vs-session threshold applies if the ruled fix is
   small. The gate may rule on execution route.

## 3. Chain of custody (verbatim inputs, in `inputs/`)

| File | What it is | Head |
|---|---|---|
| `streamB-prompt.md` | Implementation prompt (D-109 combined round) | base `a14d1fe` |
| `streamB-report.md` | Sol implementation report | `8383113` (verified diff sha `eeccea3e…`) |
| `streamB-audit.md` | Independent audit (B1, B2 blockers; S1 should-fix) | audited `8383113` |
| `streamB-fix-prompt.md` | Fix round 1 prompt | |
| `streamB-fix1.md` | Fix round 1 report (suites 2453 OK at bench) | `2e61ff9` |
| `streamB-delta.md` | Delta re-audit: B2/S1 CLOSED, **B1 persists refined** | audited `2e61ff9` |

Branch `impl/cal-bracket-d079` @ `2e61ff9` (pushed). Worktree:
`/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/calbracket`.

## 4. Governing clauses (verbatim, `docs/decision_log.md` D-109)

R1.2: "RESERVATION-FIRST: every capture appends an authenticated
`pending` attempt entry BEFORE hardware capture begins, and must
finalize it as valid / systematic-invalid / ordinary-invalid /
abandoned. Any unresolved pending, unfinalized, malformed, or
conflicting entry causes claim evaluation to REFUSE."

R1.4 (excerpt): "…threads ONE immutable ledger snapshot through every
consumer path (session, direct runner path, secondary verifier) —
repeated independent loads are a refusal-grade defect."

## 5. The defect, both rounds (verbatim from the audits)

Original B1 (`streamB-audit.md`): "Minted-consumption sessions bypass
the mandatory ledger snapshot refusal. `AuthenticatedConsumptionSession`
deliberately avoids loading a snapshot for minted semantics at
`joulewise/whole_window.py:416`, then skips snapshot/refusal checks at
:490 and becomes ready from stored summaries at :508. The secondary
verifier also permits a missing session at :4584."

Round-1 change for B1 (`streamB-fix1.md`): "B1 now loads and enforces
the canonical ledger snapshot for minted sessions and refuses explicit
minted secondary verification without a ready session."

Delta re-audit B1-refined (`streamB-delta.md`, in full):

> "The repair's readiness check sits on the wrong side of session
> preparation. A newly constructed minted session has a valid ledger
> snapshot but is not `ready` until `_validate_row_uncached()` reaches
> `_current_core_rederivation_reasons()` and calls `_prepare()` at
> `joulewise/whole_window.py:3468`. The new early return at lines
> 4073–4083 runs first, so legitimate production consumers in floor
> extraction, floor minting, and analysis input loading reject valid
> minted rows without ever attempting preparation.
>
> The read-only probe showed:
> - Explicit minted row + valid but fresh/unprepared session →
>   provenance-invalid; uncached verifier called zero times.
> - Implicit minted row + missing session → accepted by the mocked
>   uncached verifier.
>
> The second result occurs because `_row_consumption_semantics_id()`
> defaults a missing declaration to `d078_minted_envelopes_v1`, while
> the new guard compares only the raw declaration. Consequently, the
> fix is simultaneously fail-closed for the legitimate explicit path
> and still fail-open for implicit/default minted rows.
>
> The new tests miss this interaction: the pending-snapshot test
> manually invokes `_prepare()` before asserting, and the
> secondary-verifier test covers only an explicitly declared minted
> row with no session."

Delta evidence lines: `joulewise/whole_window.py:3567, :3468, :4073`;
`joulewise/floor_extraction.py:1616, :1877`;
`scripts/mint_floor_artifact.py:520, :529`;
`joulewise/analysis_engine/inputs.py:2815, :2820`;
`tests/test_whole_window_selection.py:1055`.

What is NOT in dispute (delta): B2 closed (mutant-proven), S1's four
fences closed (mutant-proven), scope exactly the declared six files,
reservation-first ordering / chaining / head-pin / F1 / F2 / T1
authentication / Window-A refusal all spot-checked retained. Delta's
nonblocking flag: sandbox had no writable TMPDIR, so filesystem-backed
tests and the full suite need lead replay after B1 is repaired.

## 6. Downstream stakes (checkable facts)

D-110 re-mint condition (a): the D-109 CAL-BRACKET implementation must
land before mint #1 re-mint; MINT-GENERALIZE-01 is hard-blocked on this
row (RT-2 edge). This row gates everything mint-ward. Timeline pressure
is LOW (Ed context, recorded 2026-08-01: ~3 weeks early, December
horizon).

## 7. Lead's disposition (labeled; the gate is free to reject it)

The delta report names both mechanisms precisely: (i) the guard must
sit after (or inside) the preparation seam rather than before it, and
(ii) the guard must compare NORMALIZED semantics
(`_row_consumption_semantics_id()`), not the raw declaration. This
looks like a decidable, small, two-mechanism repair plus
interaction-shaped regressions (a test that constructs a fresh minted
session WITHOUT manual `_prepare()` and expects acceptance; a test
that presents an implicit/default minted row and expects refusal
without a session). The lead has NOT benched or prototyped this;
severity of being wrong: the row gates the mint chain, and a wrong
guard placement either blocks legitimate re-mint work (fail-closed) or
readmits the original bypass (fail-open).

## 8. What the gate must return

(a) LICENSE or REFUSE round 2; (b) the ruled repair shape (or a ruled
alternative, including structural options the rounds have not tried);
(c) the mandatory regression shape; (d) execution route
(bench / delegated); (e) any conditions on the delta re-audit that
follows round 2.
