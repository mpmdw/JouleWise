DESIGN CONSULT — WO-T0-PRODUCER F4: capture provenance vs the trusted-operator model (this has
recurred across THREE review rounds — B-execution, singlelens F4, and now the T0-producer review;
per the standing escalation trigger the next spend is a CONSULT, not another patch; 1 round;
license to disagree).

WRITE_SCOPE: []

READ-ONLY; probes to $TMPDIR only.

THE RECURRING FINDING (F4): the T-0 capture tool derives boot-bound monotonic-ns fields, but the
evidence author authenticates the captures' BYTES and self-reported timestamps, NOT their
PROVENANCE — a hand-authored canonical JSON with fabricated monotonic_ns, or a call through
capture_step's injectable monotonic_ns/execute interface, is indistinguishable to the consumer
from a genuine capture. The council's WO-T0-PRODUCER scope explicitly wanted "boot-bound
monotonic-ns fields NO HUMAN CAN HAND-PRODUCE" — but nothing enforces that.

CONTEXT (read):
- docs/process_traces/2026-08-15-readiness-council/council-verdict.md (WO-T0-PRODUCER scope + addendum)
- refuter-outputs/sol-refuter-B-execution.md + sol-refuter-singlelens.md F4 (the prior two raisings)
- The PARALLEL ruling just made for the recorder race: docs/process_traces/2026-08-15-recorder-race-coldgate/composed-verdict.md — the concurrent-writer race was ruled a REGISTERED LIMITATION because receipt integrity was intact and the adversary is a trusted writer; is capture-provenance the SAME class (fabrication by the trusted operator is out-of-adversary-model), or DIFFERENT (the whole point of T-0 evidence is to bind the arm to a real quiet window, so a fabricated capture defeats the instrument's PURPOSE, not just a boundary)?
- joulewise/arm_readiness_evidence_t0.py (what the author actually authenticates), scripts/capture_t0_step.py (the injectable interface), docs/contracts/calibration_ledger.md (the trusted-writer threat statement)

QUESTION: is trusted capture provenance (a) ACHIEVABLE by a real mechanism the author can verify
(e.g. a boot-session-bound HMAC the capture tool holds but a hand-author cannot forge; a kernel/OS
attestation of the monotonic clock; a signing key in a place Ed-the-operator can't trivially
reach) — and if so, the exact mechanism and its trust root; OR (b) NOT achievable against a
fabricating operator on a single-operator machine, in which case the honest disposition is a
RULED trust assumption (capture provenance is trusted-operator, like the recorder race) + remove
the injectable monotonic_ns/execute PUBLIC interface (so accidental/casual fabrication is harder)
+ the terminal-review attestation + the human §5A tap as the real binding, all DOCUMENTED as the
limitation. Argue which, with the exact contract deltas and the residual each leaves. If (a),
does the mechanism's trust root actually exclude the operator, or does it just move the
fabrication point?
