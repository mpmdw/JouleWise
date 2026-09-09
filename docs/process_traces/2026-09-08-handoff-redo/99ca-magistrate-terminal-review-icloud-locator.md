# Magistrate terminal review — ICLOUD-CUSTODY-LOCATOR-01 (interactive magistrate, 2026-09-08 ~12:40 PDT)

Merge candidate: `fix/2026-09-08-icloud-custody-locator`, head named in the PR ledger row 12 (code head 07e6e4c1 +
trace commit). Makes calibration-custody path probes bounded (2 s budget, outside any authentication session) and
honours `JOULEWISE_BACKUP_ROOTS` for replay lanes, WITHOUT letting a relocated replacement satisfy custody on any
issuing path: `load_calibration_ledger_snapshot` and `_custody_reasons` default to `issuing` (original locator only);
every shared validator takes a caller-supplied mode defaulting to issuing; only classified replay consumers pass
`read_replay` (14-row allowlist, ordinal-keyed); `_refuse_custody_override_mint()` guards the four issuing entries; a
planted-replacement fixture proves zero opens under the replacement root on the bare snapshot load; the AST census
is a bounded governance aid with its limits named in the contract.

## Why
Paper replays were hanging on a dead iCloud mount (custody probes inside authentication sessions). The bounded probe
+ override fixed the hang, and the override created the hazard this lane spent five rounds closing.

## Gauntlet record
| Round | Seat | Report | Unique catches |
|---|---|---|---|
| Parts 1–3 (ec181aaa, 42b0d235) | Astra | seat reports | — |
| Fix round 1 (20cd559f) | Opus SF-1..SF-4 | 99ae consult after SF-4 ×2 | override could satisfy custody with replacement bytes (SF-4, twice → consult) |
| Part 4 (ae09cad7) | Astra medium | 99af/99ai | routing pins |
| Delta 4 | Astra | delta report | BLOCKER: five issuing snapshot loads still replay-mode — third "missed call site" → COLD GATE |
| Cold gate 99ak | cold Fable 10 + Opus 11 + synthesis 13 | — | invert the default (by construction); shared validators caller-parameterised (Opus); entry guards; three pins |
| Part 5 (96bfb448) | Astra high | 99an | — |
| Refuters 5 | Opus 99bi + Astra 99bj | — | census hatch (local `mode`), calibration_bracketing discovery reachable from mint, extraction CLI lost replay |
| Part 6 (b598113e) | Astra high | 99bk/99bs | — |
| Refuters 6 | Opus 99bu + Astra 99bv | — | live AXI idle-admission evaluated under replay (Opus); two more census escape shapes (Astra) → ruling 99bw: census is bounded, no round three |
| Part 7 (07e6e4c1) | Astra high | 99bx/99by | — |
| Delta 7 | Astra medium | 99cb | none; residual: the live-AXI counterfactual trips the call-edge keyword assertion before the replacement assertion |

Same-signature statement: the "missed issuing site" class was closed BY CONSTRUCTION at the cold gate (a forgotten site
can only lose the override); the "census escape shape" class was closed by RULING (99bw) after its second recurrence,
with the limits named in the contract. No class ran to a third fix round.

## Lead rulings
- Cold-gate synthesis 99ak/13 (disposition 3 + 2, pins) and ruling 99bw (census scope) govern.
- Residual accepted (99bu §4b, D-161 operator adversary): a snapshot pre-loaded in replay mode makes `mode` inert
  downstream; only the entry guards close a load-then-unset-then-mint sequence.
- Follow-ups registered: regroup the `_refuse_custody_override_mint` import in analysis_manifest_v3.py (nit);
  no dedicated relocated-root integration test for recovery/provenance/campaign lanes (fixture-level only).

## Live verification (lead-owned)
Bench, rc-gated per round: part 4 (164 OK), part 5 (858 OK), part 6 (864 OK), part 7 (378 OK). Bench read of the
production diff at part 4 and the guard census at the cold gate. Full-suite replay: ledger row 9.

## Verdict
LAND after CI is green on the final head and the replay tail is recorded.
