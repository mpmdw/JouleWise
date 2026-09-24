```json
{
  "schema": "claude-codex-report/v1",
  "genre": "triage",
  "status": "findings",
  "completion": "complete",
  "summary": "The population and trust-boundary defects reproduce; remove the trusted-output cache, validate ownership before derivation, and keep the oracle independent.",
  "workspace": {
    "base_requested": "20cd29de",
    "base_mode": "exact",
    "head_start": "20cd29de4cd8c177ab4f9c12c998cbbb32babac2",
    "head_end": "20cd29de4cd8c177ab4f9c12c998cbbb32babac2",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "regions": [
      {"region": "C1 invariant table", "disposition": "compose"},
      {"region": "C2 derived populations", "disposition": "compose"},
      {"region": "C3 trusted-output cache", "disposition": "apply"},
      {"region": "C4 seeded stress", "disposition": "compose"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/a291_design_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SEED_EQUAL_EDGE_COUNTS 10 of 11",
          "DUP_SEAL accepted checker= ['INV-11', 'INV-36']",
          "DUP_REQUEUE accepted checker= ['INV-11', 'INV-36']",
          "EMPTY_POS ZeroDivisionError None division by zero"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "EMPTY_POS ZeroDivisionError None division by zero"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_scored_registration tests.test_scored_roster_checker tests.test_scored_packer",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 51 tests in 6.538s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 51 tests.*OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Records 37, 44, 45, 46, and 50 were absent from this checkout; their reported current-code failures were independently probed.",
      "needs": "Include those records in the magistrate's synthesis packet."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The executed-lever population should be stated explicitly before any semantic change: the current test includes a partly counted parent's position while the zero-parent guard counts fully counted parents.",
      "needs": "Preserve current behavior in fix round 2; obtain a ruling before changing that population."
    }
  ]
}
```

## Decision matrix

**Q1 — Root cause.** This is a structural failure across the roster boundary, with the weak stress generator as an amplifier. Live placement, item ownership, terminal state, and parent position are reconstructed separately by `_live`, `_derived`, `_structure`, and the checker. `_live` collapses duplicate block IDs into a dictionary; `_derived` builds `pos` but guards division using a separately counted population; `_structure` validates placements within each envelope without proving global live ownership; `_seal(finalize=True)` grants cache trust after those incomplete checks. The checker has independent logic, but its earlier population mistakes show that independence alone does not settle the contract semantics. The seed issue is a separate test design defect that leaves these paths underexplored. [scored_packer.py:72](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:72), [scored_packer.py:77](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:77), [scored_packer.py:143](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:143), [scored_packer.py:194](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:194), [scored_packer.py:331](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:331), [test_scored_packer_stress.py:69](/Users/edr/code/wt-7370d0fb-consult-sol/tests/test_scored_packer_stress.py:69).

| Candidate | Decision | Evidence | Exact action |
|---|---|---|---|
| C1: one invariant table | **ADOPT WITH CHANGES** | The contract distinguishes roster checks, root-only checks, recorded values, replay, executed values, and implementation-source checks; a universal `_seal` predicate table would blur those consequences. [contract:398](/Users/edr/code/wt-7370d0fb-consult-sol/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:398), [contract:620](/Users/edr/code/wt-7370d0fb-consult-sol/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:620). | Use one **coverage inventory** of row ID, applicable path, consequence, production validator, checker validator, and witness. `_seal` enforces every applicable roster invariant; replay enforces history; `executed_status` owns executed values. Share contract row IDs and texts only. The checker keeps separately written predicates, canonicalization, and fixtures, with no production imports as §6 requires. [contract:635](/Users/edr/code/wt-7370d0fb-consult-sol/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:635). |
| C2: one population per quantity | **ADOPT WITH CHANGES** | A single population for planned lever conflicts with RD-4: partly terminal parents can have positions, while the null rule tests whether *any fully nonterminal parent* remains. The present code uses both populations but fails when the guard is positive and `pos` is empty. [contract:351](/Users/edr/code/wt-7370d0fb-consult-sol/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:351), [scored_packer.py:91](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:91), [scored_packer.py:108](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:108). | Build one ordered set of per-parent facts, then explicitly project **positioned**, **fully nonterminal**, **fully live**, and **fully counted** parents as needed. Document each quantity’s position and guard populations. Validate the relationship between them before division; retain the ruled item and parent summation order. [31 rulings:6](/Users/edr/code/wt-7370d0fb-consult-sol/docs/process_traces/2026-09-24-activation-a65fb4fa/31-a291-v4-residual-rulings.md:6). |
| C3: remove trusted-output cache | **ADOPT** | `_seal(finalize=True)` inserts any accepted roster into `_TRUSTED_OUTPUTS`, then `requeue_overrun` skips replay on a matching digest. The duplicate-live probe crossed that entry. [scored_packer.py:215](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:215), [scored_packer.py:331](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:331). | Remove `_TRUSTED_OUTPUTS`; run seal and full replay at every external requeue entry. `_REPLAYING` may remain solely as the recursion guard for replay’s own calls. Defer a provenance-bound optimization until a measured need. |
| C4: seed-driven stress | **ADOPT WITH CHANGES** | `i` fixes block size, item count, capacity boundary, and mode; the seed mostly affects prediction magnitude and one completed-only branch. [test_scored_packer_stress.py:69](/Users/edr/code/wt-7370d0fb-consult-sol/tests/test_scored_packer_stress.py:69), [test_scored_packer_stress.py:82](/Users/edr/code/wt-7370d0fb-consult-sol/tests/test_scored_packer_stress.py:82). | Retain deterministic coverage templates for all eleven edges, but let each seed choose legal dimensions, stage/report shapes, boundary durations, and placement geometry. Assert distinct shape signatures and meaningful edge-count variation across fixed seeds, as well as zero checker violations. |

**Q3 — Replay cost.** The `/tmp` probe used the stress fixture’s `n=11`, block size `2`, and capacity `8`; it timed `_seal` and full `_replay_roster` separately at saved depths. The 15-call sequence comparison cleared the cache before every external requeue in its second run. The seed tally still exercised production `pack` and `requeue_overrun`, with only unrelated end verification replaced for that tally. [test_scored_packer_stress.py:69](/Users/edr/code/wt-7370d0fb-consult-sol/tests/test_scored_packer_stress.py:69), [scored_packer.py:391](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:391).

```text
STRESS_SHAPE n=11 block_size=2 cap=8 events_final= 15 envelopes_final= 15 placements_final= 69
REPLAY_MS events= 0 envelopes= 12 placements= 60 seal= 0.99 replay= 2.45
REPLAY_MS events= 3 envelopes= 14 placements= 65 seal= 1.01 replay= 10.18
REPLAY_MS events= 6 envelopes= 14 placements= 65 seal= 1.09 replay= 18.33
REPLAY_MS events= 10 envelopes= 14 placements= 65 seal= 1.2 replay= 30.18
REPLAY_MS events= 15 envelopes= 15 placements= 69 seal= 1.4 replay= 47.13
SEQUENCE_MS cache_on= (15, 48.29) cache_cleared= (15, 376.75)
SEED_EDGES 291013 {'E1': 262, 'E10': 76, 'E11': 37, 'E2': 1027, 'E3': 186, 'E4': 224, 'E5': 38, 'E6': 260, 'E7': 74, 'E8': 223, 'E9': 37}
SEED_EDGES 291014 {'E1': 262, 'E10': 76, 'E11': 37, 'E2': 1028, 'E3': 186, 'E4': 224, 'E5': 38, 'E6': 260, 'E7': 74, 'E8': 223, 'E9': 37}
SEED_EQUAL_EDGE_COUNTS 10 of 11
DUP_SEAL accepted checker= ['INV-11', 'INV-36']
DUP_REQUEUE accepted checker= ['INV-11', 'INV-36']
EMPTY_POS ZeroDivisionError None division by zero
```

Dropping the cache is affordable for a scored-night roster of this measured size: roughly **377 ms total** across fifteen requeues, versus 48 ms cached. It will materially lengthen a 600-sequence stress gate, so keep that cost visible in the round report. The safety gain justifies the measured cost; the probe does not establish performance for larger rosters.

**Q4 — Additional cures.** Treat `_seal(finalize=True)` as an internal emission operation, never as a caller-granted provenance certificate. Python module privacy is not a safety boundary; full entry replay must reject a caller’s re-sealed history. Make `_live` raise `PackingRefusal("inv_11", …)` on a second live placement for a block instead of overwriting the first, and add the global ownership check to `_seal`. Put malformed-derived conversion at one helper used by **both** exit recomputation and seal verification: `_derived` is called before `_seal` at both public exits, while `_seal` currently omits `ZeroDivisionError` from its conversion set. Catch expected malformed-data exceptions, including division and overflow, without a blanket `Exception` catch. [scored_packer.py:72](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:72), [scored_packer.py:202](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:202), [scored_packer.py:307](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:307), [scored_packer.py:385](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:385).

## Composition recipe

**Q5 — Fix-round-2 plan, in order.**

1. **`joulewise/scored_packer.py`: close the entry bypass.** Remove `_TRUSTED_OUTPUTS` and its insertion in `_seal`; always call `_replay_roster` after input `_seal` at external `requeue_overrun` entry. Preserve replay’s recursion guard and `verify_executed_roster` behavior. Regression in `tests/test_scored_packer.py`: take a `pack` root, append a second live placement of one block in a fresh same-model envelope, recompute derived fields, clear the digest and re-seal, then call production `requeue_overrun`. Require typed refusal; the independent checker must report INV-11/INV-36 on the counterfactual. Also mutate a valid event history while preserving a locally valid digest and require replay refusal. [scored_packer.py:331](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:331), [contract:465](/Users/edr/code/wt-7370d0fb-consult-sol/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:465).
2. **`joulewise/scored_packer.py`: establish ownership before arithmetic.** Validate one live placement per block and one live-or-terminal owner per registered model/item in `_seal`; make `_live` reject duplicates. Keep root-only minima and replay-only history in their applicable phases. Regression: duplicate-live and missing-live variants drive production `requeue_overrun`, `pack` output checking where reachable, and `verify_executed_roster`; assert their typed invariant codes. [scored_packer.py:143](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:143), [contract:465](/Users/edr/code/wt-7370d0fb-consult-sol/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:465).
3. **`joulewise/scored_packer.py`: refactor derived facts and refusal boundary.** Compute ordered per-parent facts once; derive planned positions, nonterminal count, and occupied envelopes from those facts. Use one checked-derived wrapper at `_seal`, `pack` exit, and `requeue_overrun` exit. Regression: move every live placement of one level/model to its envelope’s voided list while leaving its parents nonterminal, then call production `requeue_overrun`; require typed refusal, never `ZeroDivisionError`. A separate valid partial-terminal split sequence must drive production `requeue_overrun` and retain the RD-4 planned position by hand-calculated item indices. Preserve the existing executed partial-position expectation until F2 is ruled. [scored_packer.py:77](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:77), [test_scored_packer.py:254](/Users/edr/code/wt-7370d0fb-consult-sol/tests/test_scored_packer.py:254), [test_scored_packer.py:268](/Users/edr/code/wt-7370d0fb-consult-sol/tests/test_scored_packer.py:268).
4. **`tests/test_scored_packer_stress.py`: diversify the generator.** Make seed-selected legal shapes and report choices reach production `pack` and `requeue_overrun`, then `check_roster` and `check_transition` at each step and `check_executed` at completion. Add a regression whose counterfactual is a generator driven only by case index: fixed seeds must produce distinct shape signatures and several different edge tallies while each still covers E1–E11. The current seed probe differs on only E2. [test_scored_packer_stress.py:69](/Users/edr/code/wt-7370d0fb-consult-sol/tests/test_scored_packer_stress.py:69), [contract:664](/Users/edr/code/wt-7370d0fb-consult-sol/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:664).
5. **Run the invariant coverage inventory and focused tests, then the canonical suite.** The packer seat owns production checks, typed refusals, replay, and production-call regressions. Preserve `tests/scored_roster_checker.py` as the independently implemented oracle; it owns contract interpretation and violation reporting, without importing packer predicates. Its current code already detects duplicate live ownership and catches malformed checker arithmetic. Any proposed oracle semantic change needs separate review rather than being made merely to match the packer. [scored_roster_checker.py:537](/Users/edr/code/wt-7370d0fb-consult-sol/tests/scored_roster_checker.py:537), [scored_roster_checker.py:748](/Users/edr/code/wt-7370d0fb-consult-sol/tests/scored_roster_checker.py:748), [contract:635](/Users/edr/code/wt-7370d0fb-consult-sol/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:635).

**Q6 — Reintroduction risks.** A shared executable invariant table would make the oracle agree with the same mistake; separate predicates plus counterfactual fixtures prevent that. Collapsing the planned position and nonterminal populations would drop partly terminal parents; the valid split regression catches it. Checking duplicates only after `_live` constructs a dictionary would lose the evidence; the duplicate-live entry regression catches it. Catching malformed arithmetic only inside `_seal` would miss direct exit recomputation; the empty-position `requeue_overrun` regression catches it. Replacing the cache with another caller-resealable trust marker would recreate the bypass; the mutate, re-seal, requeue regression catches it. [contract:354](/Users/edr/code/wt-7370d0fb-consult-sol/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:354), [scored_packer.py:72](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:72), [scored_packer.py:385](/Users/edr/code/wt-7370d0fb-consult-sol/joulewise/scored_packer.py:385).

## Rulings

- **F1:** Provide records 37/44/45/46/50 to the cold gate. They were unavailable at this exact head; the probe above independently reproduced the current-code claims relevant to this consult.
- **F2:** Clarify the executed lever’s partly counted parent population before changing semantics. The current production regression explicitly includes a partly counted position, while §4.1 defines “counted parent” using every item. Preserve that behavior during this structural fix. [test_scored_packer.py:268](/Users/edr/code/wt-7370d0fb-consult-sol/tests/test_scored_packer.py:268), [contract:379](/Users/edr/code/wt-7370d0fb-consult-sol/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:379).

No repository paths were changed; the checkout remains clean at `20cd29de`.