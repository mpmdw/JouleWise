# 03b — A172 ARM-RETRY-CLASS-01 design rulings (magistrate b0ae8462, 2026-09-15 20:55 PDT)

Inputs: Astra design brief (03), fresh Opus contract-lens refuter (03a). The refuter's blockers B1 and B2 and its
should-fixes S1/S2 are ADOPTED; its live-state verifications (every anchor true at `84e577ac`) are accepted.

**R1 — pacing, budget, hash: adopt (b) AS AMENDED by 03a.** Raw-plan SHA-256 fingerprint; no count cap (a hard count
re-inserts the human decision point D-180 cl.2 removes); ≥ 60 s spacing. The operative bound is NOT "same or next span"
(under the live `INSTALL_SPANS = (("00:00","24:00"),)` that is a ~48 h non-bound): retries are allowed until
`install_close_epoch(plan)` and while the plan is within `PLAN_MAX_AGE_S`; "same or next span" stays as D-180's ceiling,
pinned in a test against the live constant, never a synthetic one. Notice: EVERY attempt re-sends the notice and
re-runs the existing NIGHT_HANDBACK notice→publish lead for that attempt; a notice is "stale" when its fingerprint or
reviewed head differs from the candidate, when a newer abort or NO exists, OR when it was sent for an earlier attempt —
so no separate maximum notice age is needed, and the veto window is per attempt. No persistent `arm-retry.json`; the
per-attempt directory `$STAGE/arm-attempts/NNNNNN/` is kept (it cures the second-abort-overwrites-evidence catch).

**R2 — cross-activation ownership: REJECT (b) and (c); adopt (a) plus one sentence.** D-180 cl.2 grants relief from the
cold gate attached to the CAUSE and the plan CLASS, not custody of specific bytes. A successor activation that finds a
recorded retry-class abort authors a fresh same-class plan, sends a fresh notice, and arms — no relaunch-prompt clause
(c), no cross-activation state, no prior-owner proofs. NIGHT_HANDBACK gains exactly: "A retry-class abort recorded by a
prior activation authorises a successor's ordinary fresh-plan arm of the same class without a new cold gate; the
predecessor's published plan directory, if any, stays untouched under the existing human-resolution path."

**R3 — scope: adopt (a) AS AMENDED.** No `arm_retry_policy.json` (a third copy that the tests bypass — S1), no
`MAGISTRATE_RELAUNCH_PROMPT.md` edit (R2), and NO executable Python extracted from Markdown at arm time (B1 — a
production call site with no import-time review and no chain-digest coverage). Because Ed's goal needs the headless
magistrate to EXECUTE the rule rather than read it, the ONE home for the enumeration is a small real module,
`joulewise/arm_retry.py`, with two pure functions: `classify_abort(cause) -> "retry" | "cold_gate"` over the four D-180
causes plus the installer's §1.3 refusal table and the 22 gate/driver codes (every code named, `HOLD_CENSUS` and
`slot_refused` included — S2), and `retry_allowed(now_epoch_s, plan, attempts, notice) -> Decision` implementing R1.
NIGHT_HANDBACK and the runbook carry marked blocks rendered from that enumeration, and a test asserts the blocks are
byte-identical to the module's rendering (single home, two documents, one oracle). WRITE_SCOPE for the implementation
seat: `joulewise/arm_retry.py`, `tests/test_arm_retry.py`, `docs/process/NIGHT_HANDBACK.md`,
`docs/phase_2/derivation_night_runbook.md`. Sequencing: implementation starts from the post-merge head of
INSTALL-WINDOWS-MULTI-01 (both docs are edited there), per D-181 cl.1 order.

Three-seat note: Astra design + Opus refuter at this stage; the blind Fable seat is deferred to the lane's cold gate.
