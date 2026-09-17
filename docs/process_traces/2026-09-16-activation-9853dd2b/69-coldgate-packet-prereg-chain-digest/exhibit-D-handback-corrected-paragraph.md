# Exhibit D — docs/process/NIGHT_HANDBACK.md corrected chain-digest paragraph at a4d530cdab07a0b72d70f1fea00d145b177895f2 (verbatim)

```
190-plan-pinned wrapper `<night root>/chain.zsh`, emitted by
191-`scripts/gen_derivation_night.py`, which carries the night's environment as
192-literals, verifies the tracked chain's bytes and `exec`s
193-`scripts/night_chains/calibration_derivation_only.zsh` (SHA-256
194:`b5beea464d392621631d9e5060e2c63c804676b28a5b2aea58b714c5cbead6fb` at this
195-head). The pre-registration revision 1 (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md`)
196-still carries the digest of the chain as sealed, `b8bf5b0a85bb…`; the chain
197-has since changed twice for operational reasons only (2026-09-17: bounded
198-custody reads and the strict pre-reserve flag; the bounded end-of-window
199-abort and the driver deadline), with no change to any timing, capture, slot
200-or settle constant. The pre-registration's chain-digest field must be
201-re-pinned by a dated addendum before the next arm (lane
202-PREREG-CHAIN-DIGEST-ADDENDUM-01); an arm against the sealed digest refuses
203-`night_chain_digest_mismatch`.
204-
```
