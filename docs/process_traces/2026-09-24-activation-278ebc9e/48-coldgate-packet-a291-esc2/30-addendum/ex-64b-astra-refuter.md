```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Closed INV-11 passes the named witnesses and 1,868 legal rosters; four blocking contradictions prevent issuing A291-R3 verbatim.",
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
    "recommendation": "REVISE_BEFORE_IMPLEMENTATION",
    "checks": {
      "R1": "Predicate accepted: four named forgeries refused, legal contrast accepted, 1,868 legal rosters accepted.",
      "R2": "Blocked: whole-row ownership cannot represent mixed structural, derived, replay and source obligations.",
      "R3": "Blocked: AST coverage contradicts retained digest and observation checks; confinement also needs revision.",
      "R4": "Scopes are disjoint; witness dependencies and exact-fixture requirements need clarification.",
      "R5": "Blocked: required third-clause deletion kill is impossible on the well-formed domain; forger outcomes need definition.",
      "R6": "Additional predicate omissions and generator exception ambiguity reproduced."
    },
    "findings": [
      {"id":"F1","severity":"blocker","summary":"AUD-1 must fail formation first, contradicting its required inv_11 regression."},
      {"id":"F2","severity":"blocker","summary":"A single owner per inv_id cannot distinguish structural INV-37 from replay INV-37 or represent other mixed rows."},
      {"id":"F3","severity":"blocker","summary":"The AST coverage pin forbids retained seal checks and cannot see required registration checks."},
      {"id":"F4","severity":"blocker","summary":"Deleting the third closed-form clause is an equivalent mutation on well-formed ownership inputs."},
      {"id":"F5","severity":"should_fix","summary":"Confinement matches ownership-view keys as raw roster keys and leaves ownership data flow unspecified."},
      {"id":"F6","severity":"should_fix","summary":"R3-1's abbreviated formation and terminal provenance predicates omit checks required by their oracle rows."},
      {"id":"F7","severity":"should_fix","summary":"Exact witness construction references an absent script, includes a known type-invalid probe, and depends on K-owned helpers."},
      {"id":"F8","severity":"should_fix","summary":"Composed fuzz lacks an explicit exception, skip and sampling policy; required refresh can fail before submission."},
      {"id":"F9","severity":"should_fix","summary":"Forger adjudication, inconclusive outcomes and closed-ownership-only stop conditions are not fully specified."}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"test",
      "cmd":"PYTHONPATH=. python3 -B /tmp/278ebc9e/r3ref/probe_r3.py named",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["NAMED predicate expectations PASS; AUD-1 ordered-code conflict REPRODUCED"]},
      "expected":{"exit_code":0,"tail_regex":"NAMED predicate expectations PASS; AUD-1 ordered-code conflict REPRODUCED"}
    },
    {
      "id":"V2","kind":"test",
      "cmd":"PYTHONPATH=. python3 -B /tmp/278ebc9e/r3ref/probe_r3.py corpus > /tmp/278ebc9e/r3ref/corpus.log 2>&1",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["CORPUS seed=291013 cases=12 rosters=420","CORPUS seed=291014 cases=12 rosters=398","CORPUS seed=291015 cases=12 rosters=508","CORPUS seed=291016 cases=12 rosters=542","CORPUS total_cases=48 rosters=1868 violations=0 removal_third_same=True"]},
      "expected":{"exit_code":0,"tail_regex":"CORPUS total_cases=48 rosters=1868 violations=0 removal_third_same=True"}
    },
    {
      "id":"V3","kind":"test",
      "cmd":"PYTHONPATH=.:/tmp/278ebc9e/r3ref python3 -B /tmp/278ebc9e/r3ref/probe_contract.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["MUTATION third-clause deletion states=5184 distinguishing=0","MAP legal-contrast seal ACCEPT","MAP legal-contrast INV-37 details ['terminal refusal effects differ from replay']","CONTRACT probes complete"]},
      "expected":{"exit_code":0,"tail_regex":"CONTRACT probes complete"}
    },
    {
      "id":"V4","kind":"test",
      "cmd":"PYTHONPATH=.:/tmp/278ebc9e/r3ref python3 -B /tmp/278ebc9e/r3ref/probe_extra.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["FORMATION renamed-parent literal= True closed= True seal= ACCEPT","FORMATION renamed-parent checker INV-10= ['parent order, id, model, level or slice']","FUZZ remove-single refresh= KeyError","EXTRA probes complete"]},
      "expected":{"exit_code":0,"tail_regex":"EXTRA probes complete"}
    },
    {
      "id":"V5","kind":"inspection",
      "cmd":"PYTHONPATH=.:/tmp/278ebc9e/r3ref python3 -B /tmp/278ebc9e/r3ref/probe_dependencies.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["WRITE scope overlap= []","FORGER checker-input-granted= False","FORGER scratch-path-declared= False","FORGER inconclusive-outcome-declared= False","STOP closed-ownership-only-trigger-declared= False","DEPENDENCY and gate probes complete"]},
      "expected":{"exit_code":0,"tail_regex":"DEPENDENCY and gate probes complete"}
    },
    {
      "id":"V6","kind":"suite",
      "cmd":"PYTHONPATH=. python3 -B -m unittest tests.test_scored_packer",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 37 tests in 10.143s","OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V7","kind":"inspection",
      "cmd":"git status --short --branch && git rev-parse HEAD && tail -5 /tmp/278ebc9e/r3ref/corpus.log",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","0fa4e6e3bdb55e1cf4129cd4b027a4c00b54f97e","CORPUS total_cases=48 rosters=1868 violations=0 removal_third_same=True"]},
      "expected":{"exit_code":0,"tail_regex":"CORPUS total_cases=48 rosters=1868 violations=0 removal_third_same=True"}
    }
  ],
  "flags": [
    {
      "id":"RULING",
      "kind":"lead_ruling",
      "level":"blocking",
      "text":"The implementation brief contains incompatible requirements; no repository changes were made.",
      "needs":"Resolve F1-F4 and issue corrected boundary, AST and gate text before dispatching K and P."
    },
    {
      "id":"LIMIT",
      "kind":"verification_gap",
      "level":"nonblocking",
      "text":"judge_probe.py is absent from the supplied packet. Its described witnesses were reconstructed; the type-clean probe-D was explicitly distinguished from the ruling's malformed version.",
      "needs":"Exhibit the canonical witness constructors."
    }
  ]
}
```

## Findings

**Do not issue A291-R3 verbatim.** The closed ownership predicate survives R1; the surrounding implementation and acceptance requirements do not.

| ID | Severity | Check / text | Executed evidence and defect |
|---|---|---|---|
| F1 | **BLOCKER** | R1/R4 — R3-1 versus R3-2 | V1: AUD-1’s cloned parent makes the parent slices unequal. Required ordering therefore yields `inv_10: formation`, while R3-2 demands `inv_11: item conservation`. Both expectations cannot hold. |
| F2 | **BLOCKER** | R2 — R3-0, R3-4, K2/K6(ii) | V3: the legal contrast passes both seal modes, while its sole `INV-37` complaint is **“terminal refusal effects differ from replay.”** Including `INV-37` in `SEAL_ROWS` makes property (g) reject this explicitly required seal acceptance. Excluding it loses structural terminal provenance. |
| F3 | **BLOCKER** | R3 — K2 AST pin | V3 finds retained `_seal` calls with `inv_38`, and `_structure` calls mapping to `INV-35`, `INV-47`, and `INV-48`. K2 assigns these rows to replay but requires the collected seal set to be disjoint from replay. Conversely, mandatory `INV-06`/`INV-09` validation lives in `Registration.from_mapping`, outside the AST scan. |
| F4 | **BLOCKER** | R5 — K5 mutation kills | V3 exhausts 5,184 bounded ownership states: deleting the third clause has **zero distinguishing cases**. On well-formed blocks, the global count clause already implies that a live holder contains no terminal item. K5 nevertheless requires this deletion to be killed. Its old `all→any` terminal-block target also need not exist in the new implementation. |
| F5 | **MATERIAL** | R3 — K3 confinement/data flow | V3: the syntax rule bans `owner["blocks"]` inside `_parent_facts` just as it bans `roster["blocks"]`. It also excludes existing `_eligible`, `_observations`, `verify_executed_roster`, and post-builder `_structure` reads. The preserved signatures and exact `_derived` body provide no specified path for passing the once-built local view from `_structure` to `_parent_facts`. |
| F6 | **MATERIAL** | R2/R6 — R3-1 predicates | V4: consistently renaming a parent passes the stated item-slice comparison and closed ownership but violates checker `INV-10`. V3: changing a terminal’s level to another valid level passes the stated provenance predicate and closed ownership but violates structural checker `INV-37`. |
| F7 | **MATERIAL** | R4 — exact witnesses and independence | V3/V5: `judge_probe.py` is absent. The ruling says its probe-D is type-invalid; V4 confirms that a malformed terminal stops the amended checker at `INV-52`, before `INV-11`. P’s requested `refresh_derived` comes from a K-owned test file; existing P tests also import K’s checker. |
| F8 | **MATERIAL** | R6 — R3-4 generator | V4: required `remove_single` followed by `refresh_derived` raises `KeyError`, before either seal call. The referenced probe silently discards such exceptions. R3 does not specify whether to discard, fail, or submit these mutants, nor the precise population/seed for 2,000 triples. |
| F9 | **MATERIAL** | R5 — K5 forger/stop rule | V5 confirms no explicit scratch allowance, checker adjudication interface, or inconclusive outcome. “Passes iff the forger fails” can include execution failure unless constrained. The stop rule also omits an independent closed-ownership breach when the checker emits no `SEAL_ROWS` violation. |

**Replacement text**

**F1 — preserve formation-first ordering:**

> AUD-1 must be refused by `_structure` and both seal modes with `inv_10`, detail `"formation"`. Independently evaluate its ownership relation and require INV-11 failure. B1/B2/probe-D retain their specified `inv_11` expectations. An earlier formation refusal does not establish INV-11 coverage.

Alternatively, put INV-11 before full formation—but explicitly supersede R3-1’s ordering.

**F2 — replace whole-row ownership with clause ownership:**

> §5.4 assigns each invariant clause an evaluation boundary and stable clause identifier. Split structural terminal provenance from terminal replay effects; split local digest relations from reconstructed digest history. Property (g) filters checker violations by clause identifier, never by `inv_id` alone.

The map also needs these explicit dispositions:

- `INV-27` and `INV-49` concern **planned derived values**; `INV-49` cannot be wholly executed-owned.
- Root `INV-28` and derived-field staleness require arithmetic; distinguish pre-derived checks from post-derived seal checks.
- `INV-40`/`INV-44` are source obligations, not roster predicates.
- Explicitly assign `INV-19`, `INV-34`, and the mixed clauses of `INV-18/21/22/29/35/38/46/50`.

Thus the current three-way, one-owner-per-row table cannot express the required contract.

**F3 — replace the AST coverage assertion:**

> Pin clause-specific implementation sites and their boundary. Permit local digest checks in `_seal` and local observation/physics checks in `_structure`. Registration clauses are discharged by pinned validation in `Registration.from_mapping` plus the seal’s validated-registration precondition. Do not infer predicate coverage solely from refusal-code string presence.

Otherwise `_need(True, "inv_06")` could satisfy the proposed scan without validating anything.

**F4 — make the mutation gate satisfiable:**

> Require kills for non-equivalent mutations of the final implementation. Report proven equivalent mutants separately, with the implication proof; they are neither killed nor failures. Deleting the no-terminal-item clause is equivalent under valid item membership and the global ownership count rule. Replace obsolete terminal-block mutation targets with concrete mutations of the implemented guards.

Proof: if a live block contains terminal item `y`, then `LIVE(model,y) ≥ 1` and `TERM(model,y) ≥ 1`; the count clause already rejects it.

**F5 — specify view access and lifetime:**

> Confinement distinguishes reads of the ownership view from reads of the raw roster. View access is permitted in `_parent_facts`. Enumerate permitted raw reads by purpose, including observation validation, scheduling and terminal provenance. Before implementation, specify whether the view is threaded through private derivation calls or rebuilt by the same builder for each consumer; explicitly supersede conflicting v4 signature/body pins. No key aliasing or inlining solely to evade the AST rule counts as compliance.

**F6 — restore the omitted relations:**

> Formation compares each parent’s `(block_id, model, level, items)` against the ordered §3.1 derivation, including exact IDs and order. Terminal provenance additionally requires the entry’s `model`, `level`, and `parent_block_id` to equal the referenced block’s corresponding fields.

Both omissions have concrete accepting counterexamples in the scratch probes.

**F7 — provide reproducible, independent fixtures:**

> Exhibit canonical constructors for all named witnesses. Probe-D uses a complete, type-valid TerminalRefusal; assert the type precondition before testing INV-11. Distinguish the ownership-legal contrast from a history-valid roster. P constructs its new witnesses using P-local helpers or explicitly pinned baseline helper bytes; it does not consume K’s evolving helper implementation during blind development.

K/P write scopes are disjoint. The inherited stress-test requirement is already implemented at this base, so it does **not** require scope expansion.

**F8 — specify generator outcomes:**

> Enumerate ordered operator pairs for every intermediate and final roster of the four CASES. Pin the triple sampling population, seed and count. Record operator inapplicability explicitly. Unexpected operator or refresh exceptions fail with reproduction context; they are never silently discarded. When derived refresh is undefined for a malformed roster, submit it to the pre-derived structural boundary and require typed refusal. Preserve the original unrefreshed single-operator corpus separately.

**F9 — define the forger protocol and complete stop trigger:**

> The magistrate supplies a runnable environment and designated scratch directory, while withholding witness history and checker source from the forger. The forger returns candidate construction code and seal results; the magistrate evaluates candidates with the amended clause-level checker and independent ownership predicate. Outcomes are ESCAPE, COMPLETED_NO_ESCAPE, or INCONCLUSIVE. Round 3 passes only when steps 1–6 pass and step 7 is COMPLETED_NO_ESCAPE. Infrastructure failure or incomplete execution is INCONCLUSIVE. Any accepted structural-clause violation **or independent closed-ownership breach** stops the round and triggers consultation; seats do not patch it.

**Accepted text, one line each**

- **K1 closed predicate — ACCEPT:** AUD-1/B1/B2/type-clean probe-D rejected; legal contrast accepted; **0 violations across 1,868 legal rosters**, seeds 291013–291016 × cases 0–11.
- **R3-1 lossless multiplicities/no cache — ACCEPT:** retain every live occurrence and terminal entry.
- **R3-2 R2b expectation — ACCEPT:** closed ownership passes; baseline refuses `inv_12`.
- **R3-3 checker amendment — ACCEPT with a type-clean fixture:** in-memory replacement reports INV-11 for all four forgeries and none for the contrast/R2b.
- **R3-4 independent ownership oracle and AUD-2 dedicated error field — ACCEPT.**
- **K4 disjoint scopes and parallel blind implementation — ACCEPT**, with the baseline-helper boundary made explicit.
- **K5 no seat-authored patch after an escape — ACCEPT**, with F9’s complete trigger and outcome definitions.

Probe commands and observed tails are in V1–V7 above. Scripts remain under [/tmp/278ebc9e/r3ref](/tmp/278ebc9e/r3ref); repository status remains clean.

## Residual risk

This reviewed the proposed contract, not an implemented R3. The full canonical suite, future composed generator, similarity screen and forger gate were not run. The existing 37 packer tests passed. No agents or Claude were called; no repository files were modified.