# COLD-GATE RULING — WO-LAUNCH-BINDING F3, third-failure adjudication

**Adjudicator:** cold Fable instance, no loop context, convened 2026-08-16 on the rule-11 mandatory trigger (second fix round on the same defect; delta-2 G1 explicitly demanded the gate).
**Packet:** `/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/coldgate-f3-packet/` (SHA-256 manifest verified present; head `66884c6`).
**Evidence independently examined:** packet files 01–10; `joulewise/arm_readiness.py` at `66884c6` (consumer lines ~4770–4960, `verify_consumed_launch` ~4670–4760, `validate_launch_manifest` 1487–1503, `validate_arm_receipt` ~1350–1400, LAUNCH_RECIPE evidence rules 443–648, 2990–3000); `scripts/launch_window.py` at `66884c6` (assembly ~100–160, `launch()` ~230–260); `joulewise/arm_readiness_evidence_t0.py` at `66884c6` (window.env parser 576–598, `_launch_manifest` 600–723, LAUNCH_RECIPE evidence recording ~1541–1569); branch decision-log entry at `66884c6` (~9403–9450); `docs/process_traces/2026-08-15-launch-lineage-consult/consult.md` (residual-risk fence, lines 106–109, 238–242); `docs/process_traces/2026-08-15-launch-f3-consult/README.md`; `docs/process_traces/2026-08-15-recorder-race-coldgate/composed-verdict.md`; `docs/decision_log.md` 9097–9330 (WO contract + stages).

## Question 1 — DESIGN vs IMPLEMENTATION

**Finding 1.1 — The three failures are not three failures of one formulation. The defect class pivoted at the consult, and the pivot was correct.**
Failure 1 (public route left in `__all__`; packet 01, F3) and failure 2 (caller-frame `__file__` guard forged; packet 04, F3, `FORGED_CALLER_BYPASS CONSUMED`) are both failures of *caller-identity* enforcement — which the escalation consult correctly ruled structurally impossible in-process (packet 06, F1: "Mutable frame metadata cannot enforce the sole-launcher claim"). Failure 3 is the first implementation of a *different* class: **data authentication** — binding the supplied launch artifacts to the pack-anchored identity chain. The delta-2 attack (packet 10, V3/V4: `REAL_REAUTH_FOREIGN_PACK_SESSION CONSUMED True PASS`) succeeds not because in-process checking cannot work, but because the implemented anchor is wrong: the consumer compares caller-supplied artifacts against *themselves* (re-read from disk) instead of against the arm-attested identities.

**Finding 1.2 — The gap is completable, and the proof is that the exact reconciliation already exists in this codebase, one module away.**
At T-0 evidence-authoring time, `joulewise/arm_readiness_evidence_t0.py` already does everything the consumer omits:
- `_parse_shell_assignments` (lines 576–598) parses `window.env`;
- `_launch_manifest` (600–671) reconciles every `window.env` binding against the authenticated arm-context (`expected_env`: `PACK_ROOT`, `RUNS_ROOT`, `BOUND_RUNS_ROOT`, `CUSTODY_ROOT`, `QUARANTINE_ROOT`, both backup destinations, `BRACKET_SESSION_ID`, `PRE_ATTEMPT_ID`, `POST_ATTEMPT_ID`, `POWER_POLICY`), refusing "window.env differs from pack/arm-context bindings" (line 671), and checks `manifest.boot_session_id` against the boot session (line 621);
- the LAUNCH_RECIPE evidence receipt records the manifest, window.env, and window-chain digests as `input_artifacts` (line ~1569, via `artifacts = (manifest_identity, env_identity, chain_identity, arm_identity)` at 723).

The authenticated arm receipt the consumer already requires and verifies (`_verify_arm_receipt` at `arm_readiness.py:4838`) carries the row/evidence chain (`_validate_rows_and_refusals`, row `t0.single_launch_capability`) that reaches those attested identities. The consumer at `arm_readiness.py:4862–4890` checks only caller↔disk self-consistency (`dict(authenticated_manifest) != dict(manifest)`, digest equality with caller-supplied values) and never touches the attested identities; `verify_consumed_launch` (4670–4760) has the same gap — it binds consumption↔arm identity but validates the manifest only for schema, path shape, and argv agreement. This is a missing comparison, not a missing capability.

**Disposition 1: ADOPT_PRIVATE_REQUIRED_CONTEXT_API is structurally sound. Round 2's gap is a completable implementation defect. One more implementation round is licensed under the acceptance bar in §2. No re-scoped contract is required.** The honest contract after the fix: the mechanism proves (a) atomic single use, and (b) that any consumed context is byte-identical to the launch context the arm receipt's T-0 evidence chain attested for *this* pack/session — it does not and cannot prove caller identity, which remains the registered hostile-same-UID limitation exactly as the consult's limitation text states (packet 06). Note the fix also *strengthens* the mechanism against the failure delta-2 exposed: today a foreign-context consume irrevocably **burns** the single-use capability with garbage (denial of the real launch, plus a consumption record that survives replay); post-fix, foreign context refuses before the primary and the capability survives.

**Finding 1.3 — The defect's proximate cause is anchor underspecification in the adopted design text, shared between the consult and the fix-2 prompt.**
The consult's Q1 obligations say "missing, changed, or mismatched manifest/environment/chain/arm inputs refuse before the primary" (packet 06) — *mismatched against what* is never enumerated; its instruction "Continue deriving and reopening window.env, the chain, manifest bytes … inside the consumer" was satisfied to the letter by re-reading caller-chosen files. The fix-2 prompt (packet 07, item 2) says "CALLEE-SIDE REAUTHENTICATION of all of them" with the same missing anchor, and its regression list (5a–5d) contains no foreign-context attack. The implementer built what was written. This finding matters for §3: the correct response is a better-specified round, not a distrust verdict on the lineage.

## Question 2 — ACCEPTANCE BAR for the licensed round

The bar is defined so a fresh delta can verify it mechanically. Reference semantics for the reconciliation are `arm_readiness_evidence_t0.py:600–723` — the round-3 prompt must cite them.

**2.1 Identities that must reconcile**, in **both** `_consume_launch_capability` (before any filesystem effect, including the `mkdir` currently at ~4940) **and** `verify_consumed_launch` (before returning PASS), via one shared helper:

| # | Supplied value | Must equal | Anchor |
|---|---|---|---|
| I1 | launch-manifest sha256 | arm-attested LAUNCH_RECIPE manifest identity | arm receipt → `t0.single_launch_capability` row → evidence receipt `input_artifacts` |
| I2 | window.env sha256 | arm-attested env identity | same chain |
| I3 | window-chain sha256 | arm-attested chain identity | same chain |
| I4 | `manifest.boot_session_id` | `receipt["boot_session_id"]` | authenticated arm receipt (consume-time; today only checked at verify) |
| I5 | `manifest.window_plan_root` | resolves inside `window_custody_root`; equals caller's `window_plan_root` | existing check retained + custody containment added |
| I6 | `exec_argv` | `manifest["launch_command"]` AND `_launch_argv_matches(...)` against the chain | argv-chain match moved/duplicated pre-primary (a direct caller skips `verify_consumed_launch`) |

I1–I3 are the load-bearing checks: byte equality with the attested artifacts makes any self-authored or foreign artifact refuse regardless of internal consistency. Parsing `window.env` and re-checking its bindings against `arm_context` (the `expected_env` table) is licensed as defense-in-depth but is **not** a substitute for I1–I3 and not independently required by this bar. If the implementer finds the evidence-receipt chain is not digest-bound tightly enough to serve as the I1–I3 anchor, that is `NEEDS_RULING`, not improvisation.

**2.2 Refusal codes** (all registered; assert code strings in tests):
- Any I1–I6 disagreement → `launch_binding_mismatch` (the consult's own D-078 mapping row: "Validly parsed inputs disagree on pack, HEAD, boot, arm context, **recipe**, roots, or argv"), with **zero filesystem side effect** (no directory created, no primary, no sidecar) and the capability **not burned**. If exception-family plumbing (ArmReadinessError vs LaunchLineageError) forces a different registered code, `NEEDS_RULING`.
- Omitted required kwarg (cures delta-2 F2) → registered `readiness_usage_invalid`, never a raw `TypeError`. Implementation may use a validating required-context object or always-refusing sentinels — the consult's own alternative — provided incomplete context still cannot proceed.
- Second consume of a consumed arm → `readiness_record_consumed` (unchanged).
- Foreign-context consumption record at replay → `launch_binding_mismatch` from `verify_consumed_launch`.

**2.3 Discriminating regressions** — each must **fail at head 66884c6** and pass after the fix (the delta verifies both directions):
- **R1 (foreign pack/session):** real ALPHA arm + complete real BETA context, same boot → refuses `launch_binding_mismatch`, no side effect; a subsequent honest ALPHA consume then **succeeds** (no-burn assertion). This is delta-2 V4 inverted.
- **R2 (self-authored):** ALPHA arm + freshly authored self-consistent manifest/window.env/chain with correct boot id and honestly computed digests → refuses; no side effect; honest consume still succeeds after. Delta-2 V3 inverted.
- **R3 (omitted kwarg):** omit `launch_manifest_sha256`, and separately one Path input → `readiness_usage_invalid`, no side effect. Delta-2 V5 inverted.
- **R4 (replay):** a foreign-context consumption record placed by test seam → `verify_consumed_launch` refuses `launch_binding_mismatch`.
- **R5 (mutation kill):** with the attested-identity lookup mocked to return the caller-supplied digests, R1 and R2 must fail — proving the reconciliation is load-bearing, not decorative.
- **Held-property battery re-run:** public name absent, honest single-use + `readiness_record_consumed`, launcher end-to-end, the nine focused suites plus lifecycle, **and** the AXI execution pair and public-absence mutation check that delta-2's G2 interruption left unexecuted.

**2.4 Documentation cure in the same round:** the branch decision-log paragraph ("The callee independently reopens and reauthenticates the arm receipt, manifest, `window.env`, window chain, roots, argv, and digests" — `66884c6` decision_log ~9410) currently overclaims, exactly as delta-2 F1 states. Amend it to name the attested-identity anchor once the fix lands.

## Question 3 — PROCESS

**Disposition 3.1 — Fresh instance: YES.** Round 3 goes to a fresh Sol session (xhigh is justified under rule 10: third round, material cost of error). Not because the lineage is untrustworthy — Finding 1.3 shows it executed its instructions — but because the incumbent lineage's operative concept of "reauthentication" (re-read and self-compare) is exactly the anchoring the fresh delta broke, and a fresh session receiving §2's enumerated table has no such prior. The prompt must contain the identity table verbatim, cite `arm_readiness_evidence_t0.py:600–723` as reference semantics, and carry the standing `NEEDS_RULING`-over-improvisation clause.

**Disposition 3.2 — No quarantine; no stage re-scope.** What held in round 2 is substantial and independently verified by the hostile delta (public-name deletion with no alias, frame guards gone, honest single-use, replay-of-consumed refusal, null-context refusal — packet 10, "Deletion completeness itself passed"). The NDF1/AXI deferral and its Phase-2 release gate are sound and stand. Stages 2 (calibration side), 3, 4 proceed as staged after F3 closes. The branch remains unmerged until the delta-3 pass; that is the existing gauntlet, not a quarantine.

**Disposition 3.3 — Escalation handling: CORRECT, with one amendment to the record.** The consult after failure 2 was the standing trigger applied properly; the cold gate after failure 3 was mandatory and was convened without being eaten — this is the topology working as designed post-2026-07-27. The amendment: the trigger's framing "the same defect class failed three formulations" should be recorded as imprecise. Failures 1–2 were caller-identity failures; failure 3 is the first failure of the data-authentication design, caused materially by anchor underspecification in the adopted text (Finding 1.3). I strike nothing — every verdict in the packet stands, including both REJECT deltas — but the record must not read as "the design failed three times," because that reading would wrongly license abandoning a sound design. This mirrors the recorder-race composed verdict's discipline (composed-verdict.md §1–2): name the real root cause; don't purchase closure by misclassifying it.

**Disposition 3.4 — Consult and prompt hygiene rule for the skill record:** when a design consult mandates "reauthentication," the adopted text must enumerate the *anchor* (what the supplied values are compared against) and the fix prompt must enumerate the *adversarial* regressions, not only the honest-path and null-path ones. The fix-2 prompt's regression list (packet 07, 5a–5d) contained no attack with complete-but-foreign inputs; the delta found it in one probe. Rule 9's "defect-shaped regressions" should be read as attack-shaped. Recommended for the codex-delegation/adversarial-review field notes.

## Question 4 — What the loop cannot see from inside

**4.1** The decisive reconciliation machinery sat in `arm_readiness_evidence_t0.py` — outside every round's WRITE_SCOPE and never cited in any prompt or the consult. Reading outside WRITE_SCOPE was always permitted, but nothing directed attention there, and three rounds of specialists re-derived (incompletely) what the codebase already contained. When a fix concerns re-checking an invariant, the prompt should name where that invariant is first established.

**4.2** `verify_consumed_launch` shares the gap and is the more dangerous half: it is the pre-`execve` gate in `launch()` (`scripts/launch_window.py` ~245) and the downstream lineage anchor. Any cure landing only in the consumer would leave forged records replaying PASS. §2.1 binds both sites for this reason; the delta must probe both.

**4.3** The burn asymmetry (Finding 1.2, disposition 1) has not appeared in any report: pre-fix, the cheapest attack is not stealth but *denial* — one foreign-context call permanently consumes the arm capability for a window Ed armed. The no-burn-on-refusal assertions in R1/R2 are therefore claim-bearing, not decorative.

**4.4** Delta-2 executed its decisive probes but was interrupted before the suite matrix (packet 10, G2); fix-2b ran 406 tests green (packet 09) but predates the delta's findings. No one has yet run the full battery on a tree containing the round-3 fix — delta-3's checklist in §2.3 closes that, and its verdict should be the last gate before the branch's ordinary C-028 merge review.

**RULING SUMMARY: design AFFIRMED (ADOPT_PRIVATE_REQUIRED_CONTEXT_API stands); round-2 gap ruled a completable implementation defect with the anchor enumerated in §2; ONE further implementation round licensed, fresh Sol instance, against the §2 mechanical acceptance bar with delta re-audit; no quarantine, no stage re-scope; escalation path AFFIRMED as correctly operated; record amended per §3.3 and §3.4.**
