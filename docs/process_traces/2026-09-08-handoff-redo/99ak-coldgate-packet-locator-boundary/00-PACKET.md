# Cold-gate packet: ICLOUD-CUSTODY-LOCATOR-01 — where is the issuing boundary, and by what mechanism?

Assembled mechanically by the interactive magistrate at 2026-09-08 ~10:15 PDT. Rule-11 trigger: THIRD round on the
same signature ("another missed issuing call site") on one lane; the standing escalation rule says the next spend is
a ruling, not round four. This checkout is the lane head ae09cad7 (branch fix/2026-09-08-icloud-custody-locator).

## History
- Parts 1–3: `probe_custody` bounds pure path probes (2 s budget) and honours `JOULEWISE_BACKUP_ROOTS` (a lexical
  override mapping the default iCloud backup root to replacement roots) so paper replays stop hanging on a dead
  iCloud mount. Fix round 1 (20cd559f) added `_refuse_custody_override_mint()`: a NON-EMPTY override refuses
  minting at the seven ledger entry points in exhibit E.
- Opus SF-4 (twice) and the Astra consult (exhibit B): the override could still let a MISSING original plus VALID
  replacement bytes satisfy custody validation on issuing paths; the consult proposed a per-site guard across ~31
  files. The magistrate overrode that (exhibit C, part-4 brief): a `mode` on the shared probe — default `issuing`
  probes only the original locator; only callers passing `mode="read_replay"` map the override.
- Part 4 (exhibit D): implemented; routing regressions pin readiness, head-pin advancement and the fiducial slot
  validator; four module suites pass (164 tests).
- Delta re-audit (exhibit A, Astra): BLOCKER F1 — five issuing-relevant `load_calibration_ledger_snapshot` calls
  still take the default `read_replay` snapshot mode (floor mint, generalized mint, bracket-binding publication ×2,
  analysis-manifest finalization); "shared mint/replay validators need caller-sensitive propagation; globally
  flipping them would damage replay". SHOULD-FIX F2 — the contract census covers two modules only.

## Candidate dispositions
1. FLIP: pass `mode="issuing"` at the five sites (and any others the judge finds), keep everything else. Risk: the
   same signature a fourth time — the set of "issuing-relevant" sites is discovered by review, not by construction.
2. GUARD-AT-ENTRY: call `_refuse_custody_override_mint()` at the ENTRY of every issuing script/finalizer (floor
   mint, generalized mint, binding builder, analysis finalization, plus the fiducial writer) BEFORE any snapshot
   load, so a non-empty override cannot reach an issuing path at all; snapshot modes stay as in part 4. Risk: entry
   points are also discovered by review; an empty override (`""`) is permitted by the guard and returns absent
   without probing, which can only REFUSE, never PASS.
3. INVERT THE DEFAULT AT THE SNAPSHOT: `load_calibration_ledger_snapshot` defaults to `mode="issuing"` (original
   only) and the replay callers (receipt oracle, analysis-engine inputs, whole_window, run_campaign evaluation,
   provenance checks, recover/audit commands, paper producers) opt IN to `read_replay` explicitly. The property
   becomes fail-closed by construction: a forgotten site can only lose the override (a replay hang or refusal),
   never gain replacement bytes on an issuing path. Cost: the replay sites must be enumerated once and pinned.
4. Any combination or a third design.

## Charge
Rule which disposition (or combination) makes the following failure-mode test pass BY CONSTRUCTION rather than by
review: "a missing original custody locator plus valid replacement bytes under a non-empty JOULEWISE_BACKUP_ROOTS
can never satisfy custody validation on a path that mints, publishes a binding, finalizes an analysis manifest, or
appends to the ledger." State, for the ruled disposition: the exact call sites to change at this checkout (verify
each by reading it; NOT EXECUTED if you cannot), which regression pins it, and whether the empty-override
spurious-REFUSE behaviour (exhibit A §3) is acceptable. Also answer: is F1 correctly a blocker given exhibit E
(does each of the five paths reach a guarded ledger function before it can issue anything)? Write the ruling to
./coldgate-packet-3/10-coldgate-fable-ruling.md (under 800 words, numbered findings, one-line verdict last).
