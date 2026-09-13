# Cold Fable ruling — recorded verbatim (received 2026-08-03, late evening)

Instrument: cold Fable instance (fresh session, packet-only, read-only
probes at head 2e61ff9). Recorded unedited by the lead; synthesis in
SYNTHESIS.md after the paired Sol contract-lens refuter returns.

---

All probes complete. I have personally verified every load-bearing claim and found one additional structural fact the packet's rounds missed: the codebase already contains the correct enforcement pattern for the other two semantics at whole_window.py:4343-4361, and round 1 built a parallel, defective guard instead of extending it. Sanity check done — every citation below is from my own reads of the audited head 2e61ff9 in the named worktree, which I confirmed clean at that commit; I modified nothing and ran no write-bearing commands.

The full ruling follows.

---

# COLD-GATE RULING — CAL-BRACKET-D079-01, blocker B1, fix round 2

Cold Fable instance, context-free per rule 11. Inputs: PACKET.md + six custody files + read-only probes of branch `impl/cal-bracket-d079` @ `2e61ff96ea80186efa71efb9c9f6f00a16a70019` (worktree verified clean at that head).

## 0. Evidence personally verified

1. **Guard placement (fail-closed mechanism).** The round-1 guard sits at `joulewise/whole_window.py:4073-4083`, at the top of `_validate_row()`, and returns `("whole_window_verdict_provenance_invalid",)` when the row's **raw** declared semantics equals `MINTED_CONSUMPTION_SEMANTICS_ID` and the session is `None` **or not `ready`** — before `_validate_row_uncached()` is invoked at :4110. `ready` requires `_prepared and not refusal_reasons` (:447-449); `_prepared` starts `False` at construction (:438); the only path that sets it is `_prepare()`, reached via `_validate_row_uncached` → `_current_core_rederivation_reasons` (:4332-4341) → `_prepare` at :3468. So a freshly constructed, snapshot-valid minted session is structurally incapable of passing the guard. Confirmed at all three production consumers, each of which constructs a fresh session and immediately consumes: `joulewise/floor_extraction.py:1616→1625/1877`, `scripts/mint_floor_artifact.py:520→529`, `joulewise/analysis_engine/inputs.py:2815→2820`. The delta's fail-closed finding is **correct**.
2. **Normalization mismatch (fail-open mechanism).** `_row_consumption_semantics_id()` (:3567-3580) defaults a missing/non-string declaration to `MINTED_CONSUMPTION_SEMANTICS_ID`. The guard (:4074-4080) reads the raw declaration and compares `==`; an undeclared row therefore bypasses the guard while being treated as minted everywhere downstream (`_validate_row_uncached` itself normalizes at :4144). The delta's fail-open finding is **correct**.
3. **Round-1 test gap.** Verified in the round-1 diff (`git diff 8383113..2e61ff9 -- tests/test_whole_window_selection.py`): the pending-snapshot test calls `session._prepare(...)` manually; the secondary-verifier test presents only an explicitly declared minted row with mocked `_validate_row_uncached` and asserts `assert_not_called()`. Both hand-hold internals; neither exercises a production entry point. The delta's test-gap finding is **correct**.
4. **What round 1 did fix.** Constructor snapshot loading for minted sessions (:416-430) and `_prepare()` snapshot refusal for minted (:487-494, ahead of the minted branch at :504) are real and correct. The defect is confined to the guard.
5. **Fact neither round surfaced (load-bearing for §b):** `_validate_row_uncached` **already contains the architecturally correct enforcement point**: at :4343-4361, rows whose **normalized** `row_semantics` is MAX_BRACKET or SALVAGE_DANGLER are refused post-rederivation-seam when `basis is None or consumption_session is None or not consumption_session.ready`. Round 1 did not extend this existing block to minted; it built a new pre-flight raw-declaration guard with both defects. The rederivation call (and hence `_prepare`) runs only `if isinstance(core, Mapping)` (:4332), and the cache write already requires `result[0] and consumption_session.ready` (:4116-4122), so relocation to this point is cache-consistent.

## Packet-hygiene check

The packet is substantially complete and faithful; every quoted finding matched the underlying custody file and the code. Two minor flags, neither material to the ruling: (i) §3's "suites 2453 OK at bench" attributes fix-1 suite counts that `streamB-fix1.md` V2 shows were run in **Sol's sandbox**; whether the lead itself replayed the full suite before committing `2e61ff9` is not stated in the packet — if it did not, that is an open rule-1 gap the round-2 conditions below close regardless. (ii) The packet does not surface the :4343-4361 existing-pattern fact above, but that is analysis, not withheld evidence. **Hygiene: PASS.**

## (a) License

**LICENSED.** Fix round 2 on B1 may proceed. The defect is precisely characterized, both mechanisms verified against the head, and the repair is decidable; refusal would strand the row that gates D-110 re-mint with no superior alternative. License is conditional on the shape in (b)-(e) — round 2 in any other shape is outside this license. The standing same-signature trigger is armed: if the round-2 delta re-audit again finds the minted guard wrong-sided or normalization-inconsistent, that is round two of the same signature — no round 3; consult per rule 11.

## (b) Ruled repair shape — AMENDED from the lead's §7

I **adopt** the delta's two mechanisms (post-preparation enforcement; normalized comparison) but **replace** the lead's "move the guard after (or inside) the preparation seam" with a more specific shape, because the codebase already has the correct pattern and a second bespoke guard would be a third parallel convention:

1. **Remove** the round-1 pre-flight guard at `_validate_row` :4073-4083 entirely. Do not amend it in place.
2. **Extend the existing post-seam enforcement block** in `_validate_row_uncached` (the :4343-4361 pattern) to minted semantics: when `row_semantics == MINTED_CONSUMPTION_SEMANTICS_ID` and (`consumption_session is None or not consumption_session.ready`), add `whole_window_verdict_provenance_invalid`. Key it on the already-computed **normalized** `row_semantics` (:4144). Note the necessary asymmetry: unlike the two bracketed semantics, minted rows may legitimately lack `evaluation_basis`, so the minted clause must **not** refuse on `basis is None` alone — session presence + readiness is the condition. This single change closes both defects at once: a `None` session (explicit **or** implicit row) refuses — preserving and widening the round-1 secondary-verifier fence — and a fresh valid session passes, because `_prepare` at :3468 has run by the time the block evaluates.
3. **Structural alternative considered and rejected:** hoisting preparation ahead of row validation (eager `_prepare` at construction or in `whole_window_refusal_reasons`) is not warranted — preparation inputs (`bundle_paths`, policy) are derived mid-validation from the row's members (:3455-3474), so hoisting means restructuring the derivation pipeline: larger blast radius on the mint-gating row, no enforcement value beyond mechanism 2. A second in-place patch is acceptable **because** it is now a convention-join, not a third invention.
4. **Legacy-row ruling (tension the lead's §7 does not address):** undeclared legacy rows normalize to minted, so mechanism 2 will refuse session-less legacy replay through the frozen pointwise seam (:3483-3497, comment "Frozen/pre-D-109 row-verifier tests retain their historical pointwise seam"). I rule **fail-closed wins**: D-109 R1.4's "every consumer path" admits no undeclared-row exemption — an exemption for missing declarations recreates the fail-open hole by construction. If frozen tests break, update them to supply prepared sessions or explicit non-minted declarations; if Sol believes a genuinely frozen contract forbids this, the required move is a `NEEDS_RULING` early return, never a weakened guard.

**Explicit disagreements with the lead's §7:** (i) "after (or inside) the preparation seam" is under-specified — placed literally inside `_current_core_rederivation_reasons` it would miss rows that never reach the seam (`core` not a Mapping, :4332) and duplicate an enforcement point that already exists at :4343; the ruled location is that existing block. (ii) The lead's proposed two-test regression pair reproduces the round-1 failure class (narrow, single-path tests); see (c). (iii) §7 is silent on the legacy/implicit-row consequence, which is the one place round 2 can silently re-open the hole under test pressure.

## (c) Mandatory regression shape

Hard structural constraint, stated verbatim in the prompt: **no B1 regression may call `_prepare()` directly, mock `_validate_row_uncached`, or otherwise enter below `whole_window_refusal_reasons`** (or a higher production consumer). This makes the round-1 gap class — tests that hand-hold internals past the defect — unwritable. The existing round-1 test pair must be rewritten to comply, not deleted.

Five regressions, all through production entry points, over fixture snapshots:

- **R1 (fail-closed, red pre-fix at 2e61ff9):** explicitly-declared minted row + freshly constructed session with a **valid** snapshot → accepted; assert the session became ready as a side effect (proves preparation was reached, unmocked).
- **R2:** same fresh-session shape, snapshot carrying `calibration_ledger_pending` → refused, with the refusal traceable to preparation (proves refusal is the snapshot's, not never-prepared).
- **R3 (fail-open, red pre-fix at 2e61ff9):** row with **no** `consumption_semantics_id` anywhere (normalizes to minted) + `None` session → refused.
- **R4 (normalization equivalence):** the R3 implicit row + fresh valid session → same acceptance outcome as R1.
- **R5 (round-1 fence retained):** explicitly-declared minted row + `None` session → refused.

Red-pre-fix demonstration for R1 and R3 against parent `2e61ff9` via the established overlay-on-git-archive method (per fix-1 V3). R1 red proves the fail-closed defect; R3 red proves the fail-open defect; together they pin both mechanisms.

## (d) Execution route: DELEGATED to Sol, effort xhigh

Against the packet's rule-9 quote ("if the fix is smaller than the contract needed to delegate it… the lead does it at the bench"): the production diff alone (~a dozen lines: delete one guard, extend one block) would be bench-sized, but the ruled deliverable is dominated by the five interaction-shaped regressions, two overlay red-pre-fix demonstrations, the rewrite of the two round-1 tests, and probable frozen-legacy-test updates — and the contract is already written (this ruling **is** the prompt's spec). The bench threshold does not hold; rule 8's economics do. **xhigh, not high:** a second round on a blocker whose failure fires the standing escalation trigger, with a known legacy-test interaction, is exactly rule 10's "cost of error is material" trigger. `WRITE_SCOPE: ["joulewise/whole_window.py", "tests/test_whole_window_selection.py"]`, exhaustive; frozen-test casualties in other files return `NEEDS_SCOPE` with the enumerated paths rather than pre-widened scope. `EARLY_RETURN: NEEDS_SCOPE, NEEDS_RULING` (the clause-4 tension above is the anticipated `NEEDS_RULING` shape). The lead retains final live verification per rule 1 — see (e)(4).

## (e) Conditions on the post-round-2 delta re-audit

1. Independent read-only re-audit at the round-2 commit, same lane as `streamB-delta.md`, distinct from the implementer.
2. **Probes must be unmocked end-to-end** through `whole_window_refusal_reasons` with fresh sessions. The delta's round-1 V2 probe shape (mocked `_validate_row_uncached`) is now structurally blind: the ruled enforcement lives inside the function it mocks. The re-audit must demonstrate, dynamically: explicit-valid-fresh → accepted; implicit + `None` session → refused; pending-snapshot fresh → refused.
3. Verify the structural test constraint (no `_prepare` calls, no `_validate_row_uncached` mocks in B1 fences), verify **no raw-declaration semantics comparison remains anywhere on the enforcement path**, and verify the guard at :4073-4083 was removed rather than shadowed. Confirm B2/S1 fences and the round-1 snapshot mechanisms (:416-430, :487-494) are untouched.
4. **The TMPDIR gap closes this round or the round is not closed:** both prior audits flagged that filesystem-backed tests and the full suite never ran audit-side. Before the round-2 commit is accepted, the **lead** must replay the focused minted-session/ledger tests and the full suite with a writable TMPDIR at the bench and record exact counts in the gate record (rule 1; also retires the §3 hygiene ambiguity).
5. If the re-audit finds B1 persisting in any placement- or normalization-shaped form, the same-signature trigger has fired: no fix round 3 — return to consult per rule 11.

result: Cold gate LICENSES CAL-BRACKET B1 fix round 2 — amended shape (delete round-1 guard, extend the existing whole_window.py:4343 normalized post-seam block to minted), five production-entry regressions with two red-pre-fix proofs, delegated Sol xhigh, unmocked delta re-audit plus lead TMPDIR replay; all delta claims independently verified, packet hygiene PASS.
