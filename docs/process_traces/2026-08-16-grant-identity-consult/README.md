# WO-RECORDER-GRANT-IDENTITY design consult (2026-08-16)

Rule-2 pre-implementation consult (Sol xhigh, read-only, anchors resolved at
`0418bfc`). **Magistrate disposition: adopted as the GATE-PACKET DESIGN
INPUT** — the WO's own rule-11 cold gate (mandated by the recorder-race
composed verdict) makes the final mechanism call; nothing is implemented from
this consult directly.

Recommendation: `allow_governed_extraction_spec(*, verified_identity: str)` —
a caller-verified canonical path identity accepted VERBATIM; callee performs
lexical validation only (never resolve/realpath/samefile/stat/reopen). The
naive fd-stat and `(st_dev, st_ino)` formulations are REJECTED on the
executed REPLAY E hardlink-restoration defeat (coldgate refuter findings
:22-23); a true owned-fd/same-open-file-description design is recorded as
stronger but DEFERRED (larger reader/lifetime blast radius). Honest limits
language binds: this closes the executed check-to-grant race only — it does
not authenticate callers or defend in-process adversaries (the launch-binding
precedent's family).

**SEQUENCING:** the cold gate + implementation WAIT for Ed's batched
risk-appetite session (the composed verdict allows the WO to drop to the
registered limitation alone if the concurrent local writer is ruled out of
model). This consult exists so that session decides with a concrete design
and costed blast radius in hand.
