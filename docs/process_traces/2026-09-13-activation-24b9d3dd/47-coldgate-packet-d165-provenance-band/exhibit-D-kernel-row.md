# Exhibit D — kernel row GATE-SENSIBILITY-SWEEP-01 at main 1421242633769e5a2ffa25eaf51d8da9a49273fe

```json
{
 "acceptance": {
  "evidence": [
   "docs/process_traces/2026-09-09-rehearsal-harvest/121-ed-rulings-2026-09-10-recoverability-steerability.md"
  ],
  "pointer": {
   "json_pointer": "/tasks/GATE-SENSIBILITY-SWEEP-01/acceptance",
   "label": "GATE-SENSIBILITY-SWEEP-01 acceptance",
   "path": "docs/process/state_kernel.json"
  },
  "summary": "A table of every numeric gate, tolerance, threshold and refusal between capture and a reported number (admission, floors, clock skew/drift, timing anchors, custody freshness, sample counts), each with its current value, the physical quantity it protects, and its ratio to the ~1 J attribution limit and ~5 J claim bar; every gate is either justified by physics or evidence (kept, D-161 fail-closed classes) or re-set to a physically motivated tolerance with a defect-shaped test; no microscopic tolerance survives without a written physical reason. Reviewed by an execution refuter and a physics-lens refuter; lands before any G2-a number is consumed."
 },
 "authority": {
  "label": "Ed 2026-09-10 ~04:20 PDT: no silly gates on accepting numbers",
  "path": "docs/process_traces/2026-09-09-rehearsal-harvest/121-ed-rulings-2026-09-10-recoverability-steerability.md"
 },
 "dependencies": [],
 "fallback": null,
 "fences": [],
 "flags": [],
 "goal": "Before consuming the first real G2-a numbers, audit every numeric acceptance gate on the claim path for physical sensibility and remove microscopic tolerances that have no physical justification (Ed: 'make sure all barriers are sensible').",
 "id": "GATE-SENSIBILITY-SWEEP-01",
 "lane": "agent",
 "priority": "p1_phase_gate",
 "rank": 175,
 "status": "active",
 "status_note": "2026-09-10: Ed, verbatim: 'make sure there are no silly gates on accepting numbers, like make sure all barriers are sensible, recall that time where you wanted a tolerance of like 1e-15 sensitivity or something ridiculously microscopic compared to the measurement, be sensible about instrument rigor requirements.' Physics/evidence refusals stay (D-161); everything else gets a tolerance sized to the instrument. 2026-09-10 (activation 96bfeca7): inventory complete (02a 156 rows / 02b 143 rows; the 1e-15 is a decimal presentation quantum in an identity check and stays); repairs R1/R3/R4 + G2-a idle_seconds 75 on PR #314 (`feat/2026-09-10-gate-sensibility-sweep`, final head beb808bc) through the full gauntlet incl. cold gate 24 on the contract prose; R2 staged (GATE-R2-COVERAGE-ULP-01); B1 (D-165 provenance band, seat B) needs a decision-log correction \u2192 cold gate, not G2-a-blocking at G2-a energies; the lane closes when PR #314 merges and the B1 disposition is recorded.",
 "stop_card": null
}
```

## Terminal review 36 of PR #314 (activation 96bfeca7), lines 70–80
```

## Verdict

MERGE PR #314 at head `beb808bc` exactly (35 W1), after the Opus pairing refuter on ruling 35 returns without a blocker and the
`gate-ledger` check passes on the posted twelve-row ledger. Post-merge: CI on main at the merge commit; then the 09-11 activation
cuts the G2-a clone at H, which descends from this merge (checklist 13 §5–6). GATE-SENSIBILITY-SWEEP-01 closes when the B1 (D-165
provenance band) disposition is recorded by a cold gate; R2 rides D-138 (GATE-R2-COVERAGE-ULP-01).
```
