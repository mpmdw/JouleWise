# OPUS CONTRACT-LENS REFUTATION — R1 FREEZE-EVIDENCE LIFECYCLE (rule-11 pairing, refuter seat; verbatim custody)

Provenance: Opus contract-lens refuter, fresh session, no loop context; read the consult, the
actual clause text of D-131/D-134/D-137/D-078/D-120/D-117-attachment, and personally re-read
every load-bearing code site. Relayed verbatim except this header; the magistrate did not edit
findings. MAGISTRATE VERIFICATION NOTE on B2's premise is appended at the end.

---
## BLOCKERS

**B1 — The CONTENT_BOUND bucket is factually false for at least 8 of the 11 generic kinds. They are execution-derived, and the inputs that determine their verdicts are neither committed bytes nor recorded anywhere.**
- PACK_AUTHENTICATION — _run_generator_check (arm_readiness_evidence.py:745-757) calls subprocess.run([sys.executable, <generator>, "--check"], ...) with NO env= argument: inherits the entire ambient environment (PATH, PYTHONPATH, VIRTUAL_ENV, HOME). Receipt records only exit_code + stdout/stderr digests. Not content-bound under any reading.
- MINT_TRUST, MULTICELL_MINT, RECOVERY_LEDGER_TEST, THREE_WINDOW_REGRESSION, REASON_CODE_COVERAGE — suite runs in a child interpreter; env scrubbed (:335-347) but the child rebuilds sys.path as [repository, *stdlib_paths] where stdlib_paths retains every non-repo entry verbatim (:262-271) — full site-packages. Result depends on interpreter version, installed packages, TMPDIR. None recorded.
- ACCEPTANCE_OWNER, ESTIMATOR_IDENTITY, REASON_CODE_COVERAGE, RECEIPT_ORACLE — PASS/REFUSE computed by the IMPORTED live joulewise of the running interpreter while the recorded digest is of the committed file (e.g. REASON_CODE_COVERAGE compares committed literals against live _readiness.READINESS_REASON_CODES at :1140). The generic author, unlike the T-0 author, never asserts the executing repository is the pack repository.
Only DOCTRINE_PIN (:504-593) and PACK_FAMILY (:1066-1111) are pure committed-byte derivations.
The consult reserves the execution-environment ruling to Ed while removing the time bound NOW — fail-open sequencing.
Required amendment: split the bucket. RE_DERIVABLE (pure byte reads — DOCTRINE_PIN, PACK_FAMILY) is re-derived at ARM (milliseconds, no manifest, staleness structurally impossible; doctrinal support D-134 cl.6 derive-never-enter, D-120 cl.2 cache-requiring-reauthentication). EXECUTION_BOUND (anything spawning a process or importing production code) retains boot binding + horizon, or records an execution-environment fingerprint (interpreter path+version, resolved non-repo sys.path entries with digests, and for PACK_AUTHENTICATION the inherited env) that ARM re-checks.

**B2 — The design trades a claimed-complete staleness bound for a demonstrably incomplete one, with no closure argument.**
[Claimed basis: arm_readiness.py:2500-2506 pack_sha/head_commit refusal conjoined with reviewed_main() at ARM = complete repo-byte closure. SEE MAGISTRATE VERIFICATION NOTE BELOW — the premise is corrected; the constructive remedy survives.]
The replacement manifest is NOT closed; in-repo counterexample: _derive_receipt_oracle (arm_readiness_evidence.py:1184-1215) records primary artifacts (joulewise/receipt_oracle.py, plan_tree.json) but the value is produced by the RUNNING joulewise.calibration_ledger — the module that actually determines the oracle is absent from the manifest. executed_files (:288-307) drops every non-repo module via except-continue: stdlib and site-packages structurally invisible. Every manifest is a hardcoded per-deriver list. ARM reads none of them today (grep: no primary_artifacts/executed_files consumption in arm_readiness.py) — the replay is entirely new code.
Required amendment (constructive): enumerate the CHANGED set, not the depended-on set — refuse unless every path in `git diff --name-only <derivation_commit>..HEAD` appears in a governed, registry-pinned irrelevant-path allowlist (finite, mechanically derivable, complete by construction; serves the Phase-3 supersession motivation). Keep the dependency manifest as an additional conjunct, never the sole gate.

**B3 — TERMINAL_REVIEW classified content-bound is a fail-open contradicting the council's ruled remedy.**
_derive_terminal_review (arm_readiness_evidence_t0.py:913-943) requires exact PASS / head_tree_oid / pack_sha256. Under head relaxation, a terminal review attesting tree X would authorize an arm at tree Y — contradicting the council addendum ("the measurement checkout and T-0 author operating at the attested commit"). Required: TERMINAL_REVIEW binds head_tree_oid equality unconditionally; head relaxation is per-policy-ID, never a class property.

## SHOULD-FIX
S1 — DRY_RUN_REHEARSAL: D-134 cl.7's same-head condition is ruled text, outside the freshness registry's authority; state it survives verbatim. The receipt is execution-derived (in-process scripts.* imports, disk mutation).
S2 — Freshness class is operator-entered in the row registry; misclassification becomes permanent under durable evidence. Amendment: each deriver declares its class as a code constant; the author refuses on registry/code mismatch.
S3 — D-078 delta under-enumerated: register spellings for dependency-manifest mismatch, unknown freshness-policy ID, declared-vs-code class mismatch, successor-chain break, incomplete family-publication marker — all before issuance.

## NOTES
N1 — The consult's F1 rationale overstates ("cannot detect a change five minutes after authoring"): against ENVIRONMENT changes true (and that class becomes unbounded); the repo-change half of the rationale must be corrected in the amendment record. [Modified by the magistrate verification note: the repo-change half is in fact ALSO uncaught on the evidence path today.]
N2 — D-137 delta is textually clean but is an AMENDMENT, not a clarification: at adoption the antecedent was universally satisfied (EVIDENCE_RECEIPT_KEYS exact-key includes both fields); the new class narrows D-137's effective freeze-lane reach to zero. Label it and state the consequence. "Existing v1 bytes remain historical" is correct.
N3 — D-131 cl.4 delta is a genuine clarification; no conflict.
N4 — Attack line 4 resolves in the consult's favour: NOT self-serving (explicit no-in-place-repair; fresh authoring in successor family). The residual self-serving risk is the EXTENSION (all eleven kinds durable), addressed by B1.
N5 — "No D-120 change needed" VERIFIED CORRECT.
N6 — D-117 attachment claim VERIFIED CORRECT provided the freshness-policy table lives inside d117_row_registry_v1.json; a split file would need a new slot field.
N7 — Pack↔evidence containment should be stated explicitly (cl.5's "pre-freeze pack binding" is adequate BECAUSE evidence lives in the committed pack tree; reads as a relaxation otherwise). evidence_expirations gating means an all-content freeze set falls back to the 300s ARM default — safe, but readiness_temporal_budget_insufficient must evaluate the T-0 set explicitly.

## ADOPTION JUDGMENT
Adoption is safe only with B1, B2, B3 cured; as written it is not. The core insight is correct and should survive. Adopt under exactly: (1) RE_DERIVABLE/EXECUTION_BOUND split — nothing relaxed ahead of its governing decision; (2) changed-set enumeration against a registry-pinned allowlist as primary gate, manifest as conjunct; (3) TERMINAL_REVIEW unconditional head binding + DRY_RUN same-head per cl.7, head relaxation per-policy-ID; (4) class asserted against code-side constant; (5) full refusal-spelling set registered before issuance; (6) D-137 delta labelled an amendment with its zero-reach consequence stated, F1 rationale corrected.

---

## MAGISTRATE VERIFICATION NOTE (rule 1 — lead-verified before synthesis, 2026-08-15)

B2's premise ("head-equality + exact_match is a complete repo-byte closure TODAY") is INCORRECT
as to freeze evidence: both call sites of _authenticate_generic_evidence_item (arm_readiness.py
:2859 freeze-verify and :2956 _freeze_evidence_for_arm — the ARM path) pass ONLY
expected_boot_session_id; the pack_sha256/head_commit parameters are never supplied, so the
:2501-2506 comparisons are skipped (is-not-None guards). reviewed_main() at ARM pins the CURRENT
tree to a clean origin/main head but never compares against the evidence's recorded authoring
head. The cold adjudicator's reading stands: content staleness is caught by NOTHING today; the
24h horizon was the only (crude) bound. Consequence for the record: B2's constructive remedy
(changed-set enumeration) is ADOPTED on its own merits — it is complete by construction and the
counterexamples (RECEIPT_ORACLE manifest omission; executed_files site-packages blindness) are
real — but the urgency claim inverts: the design + amendments STRENGTHEN a currently-unbounded
surface rather than weakening a complete one. N1's repo-change half is modified accordingly.
