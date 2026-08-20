# D-149 T-0 GO receipt — template and evidence runbook

Every auto-issued T-0 GO under D-149 writes ONE copy of this receipt,
filled at T-0, into the window's custody root before the first capture.
A GO without a receipt is not a GO; a condition without its evidence
line is a NO-GO. The five conditions are the D-149 index row's, verbatim
in order.

```
D-149 T-0 GO RECEIPT
window: <window id / pack id>            issued_at_utc: <ISO8601>
custody_root: <path>
issuer: <session id>                      loop_turn: <n if under /loop>

C1 READY-candidate council verdict stands
    verdict path: docs/process_traces/<...>/council-verdict.md
    form check: no NOT-READY: [ ]  no UNVERIFIED: [ ]  ED-QUAL rows closed: [ ]
    verdict sha256: <...>

C2 Arm ceremony green, freshness honored
    arm receipt path + sha256: <...>
    volatile horizon (20 min) at T-0: <mm:ss remaining>
    procedural horizon (6 h) at T-0: <h:mm remaining>

C3 Machine quiet
    census output sha256: <...>  (attach file in custody root)
    fleet quiesced (no codex/agent writers): pgrep evidence attached [ ]
    interactive use: none observed since <time>; display asleep [ ]
    single writer attestation: <session id> only [ ]

C4 Boot session + clock discipline
    kern.bootsessionuuid at T-0: <uuid>  == arm-time uuid: [ ]
    network time: OFF (evidence: <command output attached>) [ ]

C5 No-retry binding acknowledged
    statement: any refused capture ends this window's lane; diagnosis
    before any re-arm; the refusal is recorded, not discarded. [ ]

VERDICT: GO / NO-GO (one word; NO-GO lists the failing condition(s))
```

## Evidence runbook (how each line is produced, no improvisation)

- C1: the verdict file is the reconvened council's; the three form checks
  are read off its verdict form (charter amendments 11–12). Never infer
  from a draft or a packet — only a custodied verdict counts.
- C2: the arm ceremony's own receipt; horizons recomputed from its
  monotonic stamps (joulewise/arm_readiness_evidence_t0.py constants).
- C3: census per the T11 driver pattern
  (docs/process_traces/2026-08-18-t10-t11-working-notes/shakedown-driver.sh
  is the model: process census + pristine-ledger check); the census
  output file lands in the custody root and its sha is quoted here.
- C4: `sysctl -n kern.bootsessionuuid` compared to the arm-time record;
  network-time state via the qualification-installed check.
- C5: no evidence — it is the issuer's binding acknowledgment, and the
  window's refusal log is where it is later proven or broken.

## Notes

- The receipt is append-only custody: never edited after issuance; a
  corrected receipt is a NEW receipt superseding by timestamp with the
  old one retained.
- Tooling: a mechanical evaluator script MAY be built to fill C2–C4, but
  it goes through the ordinary gauntlet first; until then the issuer
  fills the receipt by running the runbook commands and attaching
  outputs. The template is authoritative either way (D-149).
