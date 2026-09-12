# Resolution: reviewed interface amendment (CAL-BRACKET integration collision)

Ruled and executed 2026-08-04 by the successor magistrate. The finding
(`FINDING.md`, this directory) is preserved unchanged; this record is
the disposition. FINDING.md's "recommended shape" step 2 (historical
mint-1 replay byte-compare) was CORRECTED before execution — see the
oracle correction below — and its lines using "byte-frozen"/"frozen
expectation" framing are superseded by the rename adopted here.

## Ruling

Pre-decision Sol high consult (bounded, one round, explicit license to
disagree): `../2026-08-04-calbracket-collision-consult/consult-solhigh.md`.
Adopted shape:

1. **Signature amendment** — update
   `_CORE_SIGNATURES["mint_floor_artifact"]` in
   `scripts/mint_floor_artifact_generalized.py` to the D-109 signature
   (adds `calibration_ledger_snapshot: 'CalibrationLedgerSnapshot |
   None' = None`), as a deliberate reviewed interface revision. No
   adapter shim (would conceal a claim-relevant dependency), no
   multi-version pin (no second core revision exists), no core-file
   digest pin (too broad; rejects legitimate reviewed repairs).
2. **Oracle correction (consult F1, blocker):** byte identity is
   proven as INTEGRATION-TREE CORE-VS-WRAPPER PARITY — the reviewed
   core and the generalized wrapper minting from identical inputs on
   the same tree must produce byte-identical artifact/statement output.
   It is NOT a requirement that any future output match the historical
   mint-1 artifact digests: D-110's corrected re-mint may legitimately
   produce different bytes, and requiring historical identity would
   contradict D-110. D-110's three re-mint conditions are unchanged.
3. **Honest naming (consult F2):** the guard is a review-pinned
   mint-core INTERFACE pin, not a byte freeze — renamed throughout the
   module, its errors, and test names. "Byte-identical" is reserved for
   observed output comparisons.
4. **Snapshot-identity regression (consult F3):** a mint-path test
   asserts `load_calibration_ledger_snapshot` is called exactly once
   and that the SAME OBJECT (identity, `assertIs`) reaches absolute
   authentication, comparative authentication, and evidence rebinding —
   D-109 R1.4's invariant, now executable.

## Execution and evidence

- Merge of main into `impl/cal-bracket-d079` at `341055e` (clean; the
  delta re-audit's V2 proved the merge tree hash-identical to a fresh
  automatic remerge — no content beyond the union).
- Amendment commit `4c0897a` (Sol high implementation, enforced
  WRITE_SCOPE over exactly three files; report at the session trace).
- Lead gate at the bench: full diff read; core untouched; full suite on
  the integration tree `Ran 2487 tests OK (skipped=82)`, exit 0
  captured unpiped.
- Parity evidence: the mint-1 core-vs-wrapper byte-identical tests
  execute past the amended guard and PASS on the integration tree.
- Guard teeth: synthetic signature drift still refuses loudly.
- Delta re-audit (fresh Sol high instance, adversarial):
  `delta re-audit` record in the session trace. Verdict: two
  should-fixes, no blockers. F2 was SUBSTANTIVE and proven live: a
  default object whose `repr()` is `None` renders a signature string
  identical to the pin while defeating the core's `is None`
  load-on-absent behavior. Fixed at the bench per the auditor's
  specified shape in `4280ebd`: the guard now identity-checks the
  `None` sentinel defaults of `consumption_semantics_id` and
  `calibration_ledger_snapshot` structurally, with a regression proving
  the spoof is invisible to the string pin but refused. Focused modules
  `Ran 54 tests OK`, exit 0 unpiped. F1 (stale "byte-frozen" framing in
  RUN_STATE's active script) is fixed in the main-tree bookkeeping
  pass alongside this record.
- Merge-ref CI at the final head is the merge gate (result recorded in
  the PR and the session run report).

## Bindings

- Future changes to `_CORE_SIGNATURES` require explicit signature-pin
  review plus parity evidence (noted in-code adjacent to the pin).
- `MINT-GENERALIZE-01` acceptance evidence is reworded: the generalized
  path is byte-identical to the reviewed core on the same integration
  tree and inputs (kernel edit in the same bookkeeping pass).
- Process finding (candidate rule for the next cold-gate packet, per
  rule 11 — NOT ratified here): the lead's rule-1 verification replay
  runs on the INTEGRATION tree whenever the branch is behind main.
- Residual (from the consult and audit, honestly held): rendered-
  signature comparison retains a `__signature__`-spoofing residual
  property; the guard is a tripwire for reviewed drift, not a security
  boundary against an adversarial core file. The issued-ledger governed
  re-mint remains gated by D-110 and is NOT evidenced here.
