# COLD-GATE RULING — R1 FREEZE-EVIDENCE LIFECYCLE (rule-11 cold Fable adjudicator, 2026-08-15; verbatim custody)

Provenance: cold Fable instance, fresh session, no loop context; packet = the R1 consult +
consult prompt, the A-cluster refuter record, council-verdict.md, decision-log primaries
D-131/D-134/D-137/D-117-attachment/D-078, and code inspection of all eleven generic receipt
derivers + the ARM-side authenticator. Relayed verbatim; the magistrate did not edit content.
The paired Opus contract refuter's findings are custodied separately; the magistrate records
the composed adoption ruling only after both seats.

---

**Gate question:** adopt, amend, or reject the Sol consult's option C (content-bound durable freeze evidence + freshness-class taxonomy + family-level successor tool + contract deltas to D-131/D-134/D-137/D-078/D-117), replacing the 24h-monotonic-horizon implementation policy that expired all 33 frozen generic receipts.

## A. Central claim — SOUND, with one honest caveat the consult itself carries

All eleven derivers inspected (packet required four). Every one derives exclusively from committed or deterministic content:

- `_committed_artifact` (evidence module line 158) reads the working file AND `_git_blob_at_head`, refusing unless byte-identical to HEAD — every "primary artifact" is provably committed content, not live state.
- DOCTRINE_PIN: committed runbook/decision-log/plan-tree bytes, section hashes, D-134 text extraction. Content-bound.
- ACCEPTANCE_OWNER: pinned committed acceptance artifact + deterministic in-process authenticator probes. Content-bound.
- PACK_AUTHENTICATION: pinned generator, generator --check run, manifest validation, extraction-spec validation, attempt-policy shape — all over committed bytes. Content-bound.
- ESTIMATOR_IDENTITY: frozen-plan estimator IDs vs registry constants in committed modules; --estimator CLI absence probe on committed mint source. Content-bound.
- PACK_FAMILY: three committed plan trees cross-checked for identity-unit consistency. Content-bound.
- RECEIPT_ORACLE: fresh deterministic derivation from the committed ledger implementation vs pack bytes. Content-bound.
- REASON_CODE_COVERAGE: refusal census over committed source + focused test. Content-bound.
- MINT_TRUST / MULTICELL_MINT / RECOVERY_LEDGER_TEST / THREE_WINDOW_REGRESSION: focused suite executions + committed sources.

None reads a clock attestation, process census, power state, root freshness, or any live machine condition. The 24h `valid_until` is stamped uniformly at authoring (`now + _EVIDENCE_VALIDITY_NS`, ~line 1646) with no per-kind reasoning — blanket implementation policy, exactly as both refuter lenses found.

Caveat (real, and correctly reserved to Ed): the four suite-running kinds plus the two probe-running kinds attest "these committed bytes pass these checks as executed in the authoring environment." The interpreter and platform are implicit unrecorded dependencies. Amendment 5 makes the reservation operational instead of silent.

## B. Does content-bound validation close the staleness threat? YES — conditionally — and it opens exactly one new surface that must be governed

What the 24h horizon actually protected: nothing content-shaped. It cannot detect a dependency changed five minutes after authoring (under-protective) and expires unchanged-dependency evidence at hour 25 (over-inclusive). Its only real functions were (a) bounding the exposure window of any undetected invalidation to one day, and (b) making the D-137 monotonic-across-reboot question moot.

The consult's admission is verified in code and is the load-bearing condition of adoption. At the freeze-verify call site (arm_readiness.py:2852-2865), `_authenticate_generic_evidence_item` is invoked with only `expected_boot_session_id` — no head comparison. Inside it, the fact-source loop (2411-2428) compares recorded digests against the recorded namespace files: it detects post-freeze tampering of the recorded source documents, not divergence of the underlying repo dependencies from current reviewed bytes. So today, content staleness is caught by NOTHING — the 24h horizon merely capped how long that blindness could persist. The design's fresh dependency-manifest comparison at ARM is not an optimization; it is the entire replacement guarantee. Adoption is conditional on that validator landing and being test-obligated before any content receipt is consumed at ARM. Deleting the horizon without it would be strictly worse than the status quo.

New attack surface — manifest under-enumeration = unbounded silent staleness. If a deriver reads a dependency it does not record, the fresh comparison misses it forever. Under the 24h policy that gap was capped at one day; under content-binding it is capped at nothing. This is the one place the old policy was genuinely stronger — amendment 2. Secondary surfaces: (i) the normalized plan_tree.json binding — any normalization broader than the exact freeze-receipt slot subtraction becomes a hole — amendment 3; (ii) the dependency manifest as forgery target — adequately covered by existing mechanics; (iii) execution-environment drift — amendment 5.

## C. Contract deltas — minimal and correctly targeted; no clause weakened; two gaps to close

- D-131 cl.4: current text mandates successor mechanics for reissue; it nowhere says time forces reissue. The delta is a clarification, not a weakening; immutable-successor mechanics retained verbatim. SOUND.
- D-134 cl.1/3/5/6/9/10: all extensions, not relaxations. Cl.5's NEW exact-key schema rather than mutation of the issued v1 schema is the correct move now that production receipts exist: issued bytes stay historical, never reinterpreted. Cl.8 retains ARM's same-boot short-horizon atomically-consumable semantics unchanged. SOUND.
- D-137: the operative sentence is conditional — boot binding is required of receipts "that carr[y] valid_until_monotonic_ns." A content receipt carrying neither key satisfies it vacuously; the delta makes the conditional explicit. SOUND.
- D-078: `readiness_temporal_budget_insufficient` is additive, refuse-only. SOUND but incomplete — amendment 1.
- D-117 attachment: frozen bytes still declare slots, never future hashes; no cycle. SOUND.
- No D-120 change — correct.

Gaps: (1) the fresh dependency-comparison mismatch at ARM has no ruled refusal spelling; D-078's closed-vocabulary discipline does not permit silently overloading an existing code. (2) The D-078 delta does not name the new code's type label. Both folded into amendment 1.

## D. Boot-session binding for content-bound receipts — REJECTION UPHELD

Three grounds. (1) No threat coverage: a boot session identifies a boot epoch, not a machine; content receipts attest machine-independent properties of committed bytes. (2) The claimed residual value ("tie evidence to the machine that will arm") is already delivered in the right place: the ARM receipt and every TIME_BOUND/T-0 receipt retain same-boot binding, and ARM is where machine identity matters. (3) Coherence with D-137: boot binding exists BECAUSE monotonic deadlines are meaningless across reboots; remove the deadline and the binding's reason evaporates. Condition: the content schema carries NEITHER key, enforced by exact-key unknown-key refusal (amendment 4).

## E. Phase-2 unblocking path — LEGITIMATE; the design does NOT commit the self-serving failure mode, and this ruling adds a lock so it never can

Sought explicitly: "redefine validity so the expired receipts become valid again." Not present — the consult forecloses it three ways: F3 states the existing v1 packs cannot be repaired in place (their exact-key receipts really are expired under their issued schema; D-131 forbids rewriting those bytes); the D-137 delta keeps existing v1 bytes historical, never reinterpreted; and the new policy applies only through a new exact-key schema the old bytes structurally cannot satisfy. The unblocking path goes THROUGH D-131 clause 4's successor mechanism — new pack IDs, new custody roots, freeze-0002 receipts binding predecessor hashes, predecessor directories preserved byte-for-byte — not around it. It is not a disguised revalidation in effect: Phase 1 changes pack bytes anyway, so successor packs were already mandatory on independent grounds, and the evidence must be FRESHLY RE-AUTHORED at the new reviewed head under the new schema — re-derivation, not re-blessing.

RULED: the current 33 receipts may NOT be revalidated, reinterpreted, or grandfathered under the new policy. They must be re-authored as content-bound receipts inside the Phase-2 successor family, at the exact reviewed head, in one atomic family transaction (the family completion manifest/marker requirement is ratified — PACK_FAMILY cross-authentication makes partial publication a real mixed-generation hazard). Amendment 6 writes this prohibition into contract text.

Flag: cross-root receipt numbering (freeze-0001 → freeze-0002 under a new pack root) is a numbering-semantics change that must be specified in the freeze-receipt v2 schema, not left to tool behavior; on Ed's reserved list.

## F. VERDICT: ADOPT-WITH-AMENDMENTS

1. **Refusal-vocabulary completeness (D-078).** The fresh dependency-comparison mismatch at ARM receives a ruled spelling — either a new closed code (recommend `readiness_evidence_dependency_divergent`, type LIFECYCLE or CUSTODY as Ed prefers) or an explicit ruling that it reuses `readiness_evidence_digest_mismatch`; silence is not permitted. `readiness_temporal_budget_insufficient` must name its type label. Both refuse-only.
2. **Dependency-manifest completeness obligation (D-134 cl.10).** An authoring-side mechanical guarantee that every filesystem/git read in a deriver routes through the recording helpers (or a registered equivalent), enforced by a test obligation that fails on any unrecorded read path, plus a standing review obligation that new derivers declare their read set.
3. **Normalized plan_tree.json binding is enumerated subtraction only.** The normalization removes exactly the arm_attachments.arm_readiness freeze-receipt slot fields, enumerated by key in contract text; any other field difference refuses. A regression pins that a one-byte change anywhere else refuses. General canonicalization forbidden.
4. **Content schema key hygiene.** The content receipt schema carries neither boot_session_id nor valid_until_monotonic_ns, enforced as exact-key unknown-key refusal.
5. **Execution-environment facts recorded now, comparison semantics ruled by Ed.** The six probe/suite-running kinds record a derived (never entered) interpreter/platform fingerprint as receipt facts immediately; ARM's treatment of divergence is Ed's reserved ruling.
6. **Grandfathering prohibition written into contract (D-131 cl.4 delta).** "No receipt issued under joulewise.arm_readiness_evidence_receipt.v1 may be revalidated, reinterpreted, or consumed under the content-bound policy; migration is exclusively by fresh re-authoring within a successor pack."
7. **Validator-before-consumption ordering.** The horizon may not be removed in any commit that does not also land the fresh dependency-comparison validator and its cl.10 test obligations.

**Open questions only Ed can rule:** the three freshness semantics and exact per-row policy mapping; short horizons, arm-to-consume budget, and which volatile predicates re-probe at consumption; amendment 5's comparison semantics; amendment 1's code-vs-reuse choice and type labels; successor pack IDs and cross-chain freeze-000N numbering; freeze-receipt v2's predecessor binding set and the family publication marker; the irreversible one-time successor-family publication plus Phase-3 baseline-manifest identity (rule-11 irreversible-action trigger — Ed approval mandatory regardless of this ruling).

The magistrate may act on this ruling as-is or overrule with written dissent that Ed sees, per rule 11.
