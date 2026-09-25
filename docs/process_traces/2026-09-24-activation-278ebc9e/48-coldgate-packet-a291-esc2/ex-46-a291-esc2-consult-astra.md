```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Astra 6: text 3 does not misstate INV-11; production substitutes the wrong terminal predicate, while fuzz neither composes edits nor verifies the seal boundary.",
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
      {"id":"F1","severity":"blocker","summary":"Seal ownership validation uses an item-specific and block-id-specific terminal predicate instead of the contract's block predicate."},
      {"id":"F2","severity":"should_fix","summary":"Single-operator public-entry fuzz cannot establish pre-arithmetic ownership rejection."},
      {"id":"F3","severity":"should_fix","summary":"Checker exceptions are stringified into a form the diagnostic assertion never matches."}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"smoke",
      "cmd":"PYTHONPATH=. python3 -B /tmp/278ebc9e/esc2-astra/two_live.py","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["STRUCTURE ACCEPT","FINALIZE ACCEPT","VERIFY-SEAL ACCEPT","REQUEUE inv_38: event replay"]},
      "expected":{"exit_code":0,"tail_regex":"REQUEUE inv_38: event replay"}
    },
    {
      "id":"V2","kind":"test",
      "cmd":"PYTHONPATH=. python3 -B /tmp/278ebc9e/esc2-astra/cure_probe.py","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["CURE TWO_LIVE inv_11: item conservation","Ran 37 tests in 10.057s","OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V3","kind":"test",
      "cmd":"PYTHONPATH=. python3 -B /tmp/278ebc9e/esc2-astra/checker_crash_probe.py","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["checker crash submissions 30","test_a failures 0 errors 0 passed True","dedicated-marker cure: test_a failures 1 errors 0 passed False"]},
      "expected":{"exit_code":0,"tail_regex":"dedicated-marker cure: test_a failures 1 errors 0 passed False"}
    },
    {
      "id":"V4","kind":"other",
      "cmd":"python3 -B scripts/fixture_orphan_census.py --fail-on-orphans","cwd":".",
      "observed":{"result":"fail","exit_code":2,"tail":["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]},
      "expected":{"exit_code":0,"tail_regex":".*"}
    }
  ],
  "flags":[
    {
      "id":"ENV","kind":"environment","level":"nonblocking",
      "text":"The required fixture census could not invoke ps. No clean census is claimed.",
      "needs":"Lead runs the census in a permitted environment."
    }
  ]
}
```

# Astra 6

## Findings

**F1 — BLOCKER. Q1: an implementation error sustained by incomplete architectural consolidation. Text 3 itself does not misstate INV-11.**

The [contract v4](</Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-7370d0fb/07-coldgate-packet-a291-fix2/ex-02d-contract-v4.md:62>) defines a terminal block as one **all of whose items are terminal**. Its INV-11 predicate is at lines 467–469. [Final text 3](</Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/14-a291-final-texts-v4.md:8>) accurately repeats that predicate, including “are not terminal.” It neither substitutes an item-level test nor requires the refusal’s `block_id` to match. Its separately identified quantifier-placement ambiguity is not AUD-1’s cause.

Production substitutes:

`not any(refusal matches this model, this item, and this block_id)`

for:

`not all(items in this block have a terminal refusal for this model)`

That substitution is explicit at `joulewise/scored_packer.py:234`. The checker uses the latter definition at `tests/scored_roster_checker.py:585`.

A crucial detail: in AUD-1, **both blocks are terminal under the contract**, because they contain the same two terminal items. Thus contract branch (a) counts **zero** eligible blocks, while branch (b) fails because both blocks remain envelope-listed. Production wrongly excludes only the original block and counts its duplicate as the one eligible owner. This is not merely an erroneous count of two nonterminal owners.

V1 reproduced the reported acceptance and checker INV-11. Replay then refused `inv_38`. The present external requeue path runs seal followed by replay (`joulewise/scored_packer.py:390`); executed verification does likewise (`joulewise/scored_packer.py:469`). **This witness establishes a seal failure, not a demonstrated replay bypass.**

The architectural diagnosis from round 1 was substantially right, but round 2 consolidated **derived statistics**, not the ownership interpretation that makes those statistics meaningful:

- `_structure` computes item ownership with its own terminal predicate (`joulewise/scored_packer.py:225`).
- `_parent_facts` independently skips terminal items and selects a parent or first matching single (`joulewise/scored_packer.py:83`, `:91`, `:95`).
- `_live_index` detects duplicate listings of one block ID, which cannot detect two distinct IDs holding the same items (`joulewise/scored_packer.py:70`).

A checked arithmetic boundary cannot correct these differing meanings. Agreement on legal rosters is insufficient because the competing predicates coincide on many legal states.

**Q2 — Structural cures**

| Candidate | Cost | Guarantee and limitation |
|---|---|---|
| **(a) Literal contract predicate** | Small change plus focused regressions. | Corrects this quantifier error. V2’s in-memory substitution rejects AUD-1 with `inv_11` and passes all 37 packer tests. It leaves separate ownership reconstruction sites intact. |
| **(b) One production ownership table** | Moderate refactor and contract-to-field review. | Build lossless relations once; evaluate INV-10/11/12/17/52 against those relations and project derived facts from the validated result. Eliminates internal disagreement between ownership validation and consumers. A faulty builder remains a common failure point, so retain an independent oracle. |
| **(c) Promote the checker into production and call it from seal** | Moderate integration; potentially substantial runtime and dependency cost. | Seal rejects everything that checker detects. It still does not prove unchecked properties such as root re-pack. The checker ceases to be an independent oracle for seal acceptance: testing one against the other becomes largely circular. Requires a new independent oracle and a contract §6 amendment. |
| **(d) Production differential guard** | Two implementations, execution cost, comparison protocol and ongoing maintenance. | Reject if either validator rejects or their detailed ownership facts disagree. Comparing only lever values or aggregated parent facts is insufficient. Both implementations can share a mistake; agreement is not proof. |
| **(e) Validated immutable ownership view** | Moderate when combined with (b). | Parse raw roster → lossless relations → validate → immutable accepted view; derive positions only from that view. Makes the validation-to-consumption dependency explicit and prevents later consumers from selecting a different owner. It must be freshly constructed per call, never a caller-supplied trust token or cache. |

For (b), retain **all** block memberships, terminal entries, placement occurrences, envelope positions and parent-child edges, with source indices. Do not collapse duplicates through dictionary overwrite or choose an owner during construction. Preserve terminal-entry multiplicity separately from the set used for the all-items-terminal predicate. INV-52 requires validation of the original values, including fields not needed for ownership.

For (c), today `check_roster` invokes static and event checking (`tests/scored_roster_checker.py:785`); blindly calling the whole checker would introduce another history-validation path, not just an ownership check. Contract §6 expressly excludes INV-39 from its capabilities.

For (d), compare candidate-owner identities, multiplicities, block-terminal truth and live occurrences **before** lossy position aggregation. Current parent facts skip terminal items (`joulewise/scored_packer.py:92`), and the checker’s position helper does too (`tests/scored_roster_checker.py:267`); those summaries can agree while the ownership predicate is wrong.

**Recommendation: (b)+(e), containing (a), with the checker retained outside production.** This is a bounded structural correction. Do not require a wholesale rewrite of replay.

**F2 — SHOULD_FIX. Q3: the fuzz design misses both composition and the required rejection boundary.**

At `tests/test_scored_packer_fuzz.py:175`, each operator receives `deepcopy(base)`. No mutant becomes another operator’s input. Furthermore, operator 2 duplicates a placement of the **same** block ID (`:53`); none of the ten operators creates AUD-1’s distinct block with overlapping membership (`:125`). Merely composing existing operator 2 with operator 4 is therefore insufficient.

There is a second, independent hole: submissions exercise requeue or executed status (`tests/test_scored_packer_fuzz.py:146`), and property (b) accepts **any** refusal (`:208`). Even if AUD-1 entered this corpus, its `inv_38` replay refusal would satisfy that property. An invariant-code census somewhere else in the corpus does not prove this witness fails at seal.

Implement these tests:

1. **Exact regression:** preserve AUD-1’s completed first envelope, distinct duplicate block, matching placement/envelope, and terminal entries. Refresh derived fields independently. Require `_structure`, verification seal and finalizing seal to refuse `inv_11`. Assert rejection precedes derived arithmetic; a replay refusal is not success. Test public entry rejection separately.
2. **Terminal truth table:** vary zero, some and all terminal items, multi-item versus singleton blocks, and refusal provenance naming the original, duplicate or another ID. Test INV-11 separately from terminal-provenance validation. Do not declare a roster legal just because its isolated INV-11 predicate passes.
3. **Legal contrast:** preserve genuine split-parent histories with one terminal single and one live single. Existing hand-calculated partial-position assertions are valuable (`tests/test_scored_packer.py:459`, `:478`).
4. **Composed generator:** begin with a legal root/intermediate/final roster; choose a target model/item set once; apply a sequence of 2–4 coordinated edits to the **same** copy. Add distinct-ID overlapping blocks, resurrection of voided placements, terminal insertion/removal/retargeting, superseded flips and child partition changes. Include mandatory duplicate-holder × terminal-mask combinations rather than hoping random selection reaches them.
5. **Small exhaustive ownership model:** enumerate bounded memberships, terminal masks, superseded flags and 0/1/2 live occurrences, embedded in a valid surrounding roster. Compare production ownership validation against separately written literal contract predicates. Preserve multiplicities; distinguish invalid membership, ownership and history.
6. **Shrink and retain failures:** minimize edits and affected items while preserving the discrepancy; report seed, ordered operations, target identities and expected boundary. Run unrepaired, digest-resealed and independently derived-refreshed variants. Early digest or stale-derived refusals must not earn ownership coverage.

A stdlib deterministic generator suffices; introducing a property-testing dependency is optional.

**F3 — SHOULD_FIX. The checker-crash assertion is ineffective.**

The harness converts `('checker-crash', 'TypeError')` to a string at `tests/test_scored_packer_fuzz.py:184`, `:186`, then compares it with the bare string `"checker-crash"` at `:206`.

V3 reproduced **30 injected checker exceptions with a passing assertion**. Preserving the marker caused the assertion to fail correctly. Fail immediately with seed/operation context, or store a dedicated `checker_error` field and assert it is absent. Keep the fault-injection regression.

**Q4 — Executable fix-round-3 plan**

These are proposed **new lead-issued scopes**, not writes authorized to this consult.

1. **Lead + fresh contract seat, before implementation.** Contract seat `WRITE_SCOPE: []`. Freeze the literal terminal definition, lossless ownership-view schema, validation order and invariant-to-boundary matrix. Have the lead author `docs/contracts/scored_ownership.md`. Explicitly supersede affected Final-text AST/interface requirements. Preserve digest-first verification, basic identity/type/empty-block checks, then INV-11 before derivation. Place expanded formation checks so AUD-1’s intended INV-11 regression remains discriminating.
2. **Independent test seat K, first.** `WRITE_SCOPE: ["tests/test_scored_ownership.py", "tests/test_scored_packer_fuzz.py", "tests/scored_case_generator.py", "tests/test_scored_roster_checker.py"]`. Pin the existing checker; write the literal ownership oracle, truth tables, composed generator, exact AUD-1 regression and checker-crash test without reading the new production implementation. Demonstrate the ownership-boundary tests fail at `0fa4e6e3`. Existing checker semantics need no AUD-1 repair.
3. **Implementation seat P, after K’s tests are pinned.** `WRITE_SCOPE: ["joulewise/scored_ownership.py", "joulewise/scored_packer.py", "tests/test_scored_packer.py"]`. Implement (b)+(e), with literal (a). Keep checker imports out of production. Derive ownership-dependent positions from the accepted view; preserve ordering and existing planned/executed population semantics. No trusted-output cache.
4. **Fresh adversarial and test-audit seats.** Both `WRITE_SCOPE: []`; neither audits its own work. Audit the relation builder for discarded duplicates, incomplete domains, premature owner selection and raw-roster escape paths. Mutation tests must kill `all→any`, restoration of refusal-ID matching, duplicate overwrite, weakened multiplicity, and removal of each ownership guard.
5. **Gate before merge, owned by the lead.** At the exact integrated head: reproduce baseline-red/fix-green witnesses; pass both seal modes and public-entry tests, legal contrast corpus, composed/exhaustive ownership tests, all five scored modules, and `python3 -B -m unittest discover -s tests`. Review the invariant-binding matrix and executed mutation kills. Run delta re-audit, then a fresh cold gate paired with a distinct contract reviewer. Lead performs final diff review, records dissent and decides merge. Another recurrence returns to consultation.

## Residual risk

No repository files changed; scratch probes are under `/tmp/278ebc9e/esc2-astra/`. No other agent/model was called, and blindness restrictions were observed.

The cure probe changes production code only in memory. Its 37 passing tests establish a local correction, not completeness of the proposed architecture. I did not rerun the full fuzz, stress or canonical suite. Performance costs for the proposed designs remain unmeasured.