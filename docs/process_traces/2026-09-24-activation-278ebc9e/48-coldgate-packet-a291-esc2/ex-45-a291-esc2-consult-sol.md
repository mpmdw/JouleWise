```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "AUD-1 is an implementation error enabled by repeated ownership interpretations in the seal; Final text 3 states INV-11 correctly.",
  "workspace": {
    "base_requested": "0fa4e6e3",
    "base_mode": "exact",
    "head_start": "0fa4e6e3bdb55e1cf4129cd4b027a4c00b54f97e",
    "head_end": "0fa4e6e3bdb55e1cf4129cd4b027a4c00b54f97e",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "AUD-1",
        "severity": "blocker",
        "summary": "The seal uses an item and block-ID-specific terminal test where INV-11 requires an all-items-terminal block test."
      },
      {
        "id": "AUD-2",
        "severity": "should_fix",
        "summary": "The fuzz harness fails to recognize checker exceptions because it stringifies the crash tuple before comparing it with a bare marker."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_scored_packer",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 37 tests in 10.017s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 37 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The reproduced forgery is rejected by later event replay, but the required seal boundary accepts it.",
      "needs": "Keep merge blocked until the seal itself refuses the composed witness with inv_11."
    }
  ]
}
```

# Sol 6.0

## Findings

### AUD-1 — Root cause and fix-round-3 recommendation

**Final text 3 states INV-11 correctly.** It says a block is terminal as a block, and requires exactly one qualifying live holder or one terminal refusal with no live holder. The contract defines a terminal block as one whose *every* item is terminal; its INV-11 predicate repeats the block-wide condition. The independent checker implements that reading. [Final texts v4:8](/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/14-a291-final-texts-v4.md:8), [contract v4:62](/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-7370d0fb/07-coldgate-packet-a291-fix2/ex-02d-contract-v4.md:62), [contract v4:465](/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-7370d0fb/07-coldgate-packet-a291-fix2/ex-02d-contract-v4.md:465), [checker:577](/Users/edr/code/wt-278ebc9e-esc2-sol/tests/scored_roster_checker.py:577).

The immediate error is in the implementation: `_structure` discounts a live block for an item only when a refusal names **that item and that block ID**. A refusal naming the original block therefore hides it from the packer’s count while a differently named copy remains counted. The checker asks whether *all items* of each block have terminal entries, independent of the refusal’s block ID. [scored_packer.py:225](/Users/edr/code/wt-278ebc9e-esc2-sol/joulewise/scored_packer.py:225), [scored_packer.py:234](/Users/edr/code/wt-278ebc9e-esc2-sol/joulewise/scored_packer.py:234), [checker:581](/Users/edr/code/wt-278ebc9e-esc2-sol/tests/scored_roster_checker.py:581).

I reproduced the reported failure in memory from a packed roster with one real event: copy the two-item `large` parent under a distinct block ID, place the copy in a new loaded envelope, add terminal entries for both items naming the original block, refresh the recorded derived values, and finalize. Results: `_structure` **ACCEPT**, `_seal(finalize=True)` **ACCEPT**, verification-mode `_seal` **ACCEPT**; L1I0 has two live `large` block IDs; the checker reports `INV-11`; `requeue_overrun` later raises `inv_38: event replay`. The later replay is valuable, but it does not satisfy the required seal check. The re-audit reports the same witness and a scratch-only literal-predicate cure. [re-audit:461](/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/39b-a291-delta-reaudit-report.md:461), [scored_packer.py:251](/Users/edr/code/wt-278ebc9e-esc2-sol/joulewise/scored_packer.py:251), [scored_packer.py:390](/Users/edr/code/wt-278ebc9e-esc2-sol/joulewise/scored_packer.py:390).

The **structural cause** is that ownership is reconstructed several times with different coordinates. `_structure` counts live block IDs and interprets terminality; `_parent_facts` separately builds an item terminal set and a live-placement index for derived positions; replay reconstructs history later. The round-1 same-ID duplicate was closed by `_live_index`; this distinct-ID forgery crosses a different interpretation in `_structure`. The texts did not introduce that interpretation. [scored_packer.py:70](/Users/edr/code/wt-278ebc9e-esc2-sol/joulewise/scored_packer.py:70), [scored_packer.py:80](/Users/edr/code/wt-278ebc9e-esc2-sol/joulewise/scored_packer.py:80), [scored_packer.py:225](/Users/edr/code/wt-278ebc9e-esc2-sol/joulewise/scored_packer.py:225), [scored_packer.py:449](/Users/edr/code/wt-278ebc9e-esc2-sol/joulewise/scored_packer.py:449).

| Cure | Cost | Guarantee and limit |
|---|---|---|
| **(a) Literal contract predicate** | Small patch and two focused regressions. | Closes AUD-1 directly; the re-audit’s scratch probe got `inv_11` and kept 37 packer tests green. Separate ownership interpretations remain, so this is a necessary immediate correction, not a structural cure. [re-audit:502](/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/39b-a291-delta-reaudit-report.md:502) |
| **(b) One validated ownership table** | Medium refactor across structure and derived facts; review type and ordering behavior carefully. | Build one record for each registered `(model, item)` with its parent, containing blocks, live placements, and terminal entries. Validate raw types and envelope indices while constructing it; evaluate INV-10/11/12/17/52 from that normalized view before arithmetic, and derive parent positions from the same view. This removes the current packer-internal disagreement. It still needs an independent contract oracle and adversarial tests. |
| **(c) Call the checker in production** | Large dependency and packaging change; likely extra work at every seal and replay. | Makes the checker’s present INV-11 ruling enforceable by the seal. Once the checker becomes production logic, agreement between it and the packer ceases to be independent evidence. A new oracle would be required; I do not recommend this. The checker is currently a stdlib-only module outside production imports. [contract v4:635](/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-7370d0fb/07-coldgate-packet-a291-fix2/ex-02d-contract-v4.md:635) |
| **(d) Production differential guard** | A second item-centric implementation, two computations per seal, and continuing dual maintenance; replay compounds its cost. | Fail closed when fact vectors disagree, including terminal-block status and live-owner counts. It detects divergence of this kind when the paths are genuinely separate. Shared mistakes and omitted facts can still agree. Keep the test checker separate if this is adopted. |
| **(e) Canonical event reconstruction** | High redesign cost and replay cost. | Accept public rosters only when registration plus events reconstruct the same roster. That already catches this witness at requeue; it is a strong history boundary. It cannot replace INV-11 at `_seal(finalize=True)`, whose own contract requires refusal before derived arithmetic. [scored_packer.py:267](/Users/edr/code/wt-278ebc9e-esc2-sol/joulewise/scored_packer.py:267), [scored_packer.py:449](/Users/edr/code/wt-278ebc9e-esc2-sol/joulewise/scored_packer.py:449) |

**Recommendation:** adopt (b), using (a) as the literal acceptance condition inside it. Preserve the independently written checker as a test oracle. Require the ownership table to expose counts and terminal-block status so reviewers can compare facts, not only final refusal codes.

### AUD-2 — Regression and fuzz gap

The ten operators each mutate a base once. Operator 2 duplicates a placement using the **same** block ID; operator 4 adds **one** terminal entry. Neither creates the distinct-ID copy plus terminal entries for *all* original items, and the harness does not compose operators on the same mutant. Its resealed submissions therefore did not exercise the masking interaction. [test_scored_packer_fuzz.py:3](/Users/edr/code/wt-278ebc9e-esc2-sol/tests/test_scored_packer_fuzz.py:3), [test_scored_packer_fuzz.py:53](/Users/edr/code/wt-278ebc9e-esc2-sol/tests/test_scored_packer_fuzz.py:53), [test_scored_packer_fuzz.py:73](/Users/edr/code/wt-278ebc9e-esc2-sol/tests/test_scored_packer_fuzz.py:73), [test_scored_packer_fuzz.py:175](/Users/edr/code/wt-278ebc9e-esc2-sol/tests/test_scored_packer_fuzz.py:175).

Add a deterministic **composed ownership operator**: select a live parent with at least two items; clone it under a fresh ID; add its envelope and placement; then add one refusal per item naming the original block while leaving both blocks live. Refresh derived values and reseal test-side. Require checker `INV-11` and `inv_11` from `_structure`, both `_seal` modes, and the public entry **before** replay can return `inv_38`. Add the partial-terminal contrast, where only one item has a refusal, to pin the all-items predicate. Generate variants over block sizes 1–3, original/clone refusal IDs, zero/some/all terminal items, same/distinct live IDs, and root/one-event histories. Shrink failing cases to the smallest two-item, two-block witness. A property is: **every resealed roster for which the independent checker reports INV-11 is refused at the seal boundary**.

Repair the harness diagnostic at the same time. It converts a checker exception tuple into a string, then compares that string with the bare `checker-crash` marker; the re-audit injected 30 checker exceptions and the assertion stayed green. Store a dedicated error field or fail immediately with operator, seed, and roster index. [test_scored_packer_fuzz.py:181](/Users/edr/code/wt-278ebc9e-esc2-sol/tests/test_scored_packer_fuzz.py:181), [test_scored_packer_fuzz.py:204](/Users/edr/code/wt-278ebc9e-esc2-sol/tests/test_scored_packer_fuzz.py:204), [re-audit:176](/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/39b-a291-delta-reaudit-report.md:176).

## Fix round 3: executable ordering

1. **Lead, ruling and brief:** retain contract v4 and Final text 3’s block-wide terminal definition. Specify that a seal-level INV-11 refusal must precede replay refusal on the composed witness. The lead owns brief, contract, state, report, and merge edits; no delegated write scope is implied.
2. **K, independent test seat — `WRITE_SCOPE: ["tests/test_scored_packer_fuzz.py", "tests/test_scored_ownership_forgery.py"]`:** commit the composed witness, partial-terminal contrast, generated variants, and checker-crash diagnostic test first. Preserve `tests/scored_roster_checker.py` as an unchanged independent oracle. Show the new seal-boundary tests **RED** at `0fa4e6e3`.
3. **P, production seat — `WRITE_SCOPE: ["joulewise/scored_packer.py", "tests/test_scored_packer.py"]`:** on the test-integrated head, build the validated ownership table, use its block-wide terminal status for INV-11, and consume its facts for parent positions. Preserve refusal ordering, both seal modes, and replay. Show the K tests **GREEN** without changing their expectations.
4. **A, cold delta re-audit — `WRITE_SCOPE: []`:** independently reconstruct at least one new distinct-ID forgery; inspect the table’s INV-10/11/12/17/52 mappings; check root, event, finalization, verification, and public entry paths. Exercise a guard-deletion mutant of terminal-block status and the checker-crash injection.
5. **Lead’s pre-merge gate:** review the exact integrated diff and K’s red/green evidence; run the focused scored tests and `python3 -m unittest discover -s tests`; require zero checker violations on legal generated histories, seal-level `inv_11` on every composed ownership witness, no raw exceptions or `internal:` refusals, and a clean cold re-audit. A repeated ownership signature returns to a consult before another patch or merge.

## Residual risk

The one-event forgery also violates other checker rows, including formation and event-history rows; those later defenses do not establish that the seal enforces INV-11. The proposed ownership-table design has not been implemented or benchmarked in this read-only seat.