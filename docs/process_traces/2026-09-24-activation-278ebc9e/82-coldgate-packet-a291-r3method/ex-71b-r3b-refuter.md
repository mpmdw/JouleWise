```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "R3b retains three blockers and four material defects; the closed ownership predicate passes all 1,868 legal rosters.",
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
    "recommendation": "REVISE_BEFORE_DISPATCH",
    "findings": [
      {"id":"D1","severity":"blocker","summary":"The fixed boundary assignments give inv_51 two owners."},
      {"id":"D2","severity":"blocker","summary":"B1 cannot kill deletion of the superseded-holder clause; the m1 replacement is underspecified."},
      {"id":"D3","severity":"blocker","summary":"Per-model formation accepts cross-model parent reordering rejected by seal-owned checker inv_10."},
      {"id":"D4","severity":"should_fix","summary":"The AST coverage requirement demands inv_27 despite the preserved stale_derived implementation and expectation."},
      {"id":"D5","severity":"should_fix","summary":"The prescribed witness copy omits term() and the independent sealing preconditions needed by checker and verification tests."},
      {"id":"D6","severity":"should_fix","summary":"The refresh-error branch calls _structure directly, which still raises raw KeyError on a required composed mutant."},
      {"id":"D7","severity":"should_fix","summary":"The pasteable forger text omits outcome definitions supplied elsewhere in the ruling."}
    ],
    "prior_findings": {
      "F1":"cured",
      "F2":"not cured",
      "F3":"not cured",
      "F4":"not cured",
      "F5":"cured",
      "F6":"not cured",
      "F7":"not cured",
      "F8":"not cured",
      "F9":"not cured"
    },
    "scope_collision":"No K/P write-path overlap.",
    "red_requirements":"B1, B2 and type-clean probe-D discriminate baseline from amended checker after independent resealing."
  },
  "verification": [
    {
      "id":"V1","kind":"test",
      "cmd":"PYTHONPATH=.:/tmp/278ebc9e/r3bref python3 -B /tmp/278ebc9e/r3bref/probe_delta.py semantics > /tmp/278ebc9e/r3bref/semantics.log 2>&1",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["PROVENANCE wrong-level= PackingRefusal: inv_37: terminal provenance","FORMATION renamed-parent=PackingRefusal: inv_10: formation","FORMATION reordered-models=both-seals-ACCEPT checker-inv_10=True","SEMANTICS completed"]},
      "expected":{"exit_code":0,"tail_regex":"SEMANTICS completed"}
    },
    {
      "id":"V2","kind":"test",
      "cmd":"PYTHONPATH=.:/tmp/278ebc9e/r3bref python3 -B /tmp/278ebc9e/r3bref/probe_delta.py contracts > /tmp/278ebc9e/r3bref/contracts.log 2>&1",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["RED B1/B2/type-clean-D=discriminating-after-independent-reseal","SCOPE K/P-write-overlap=[]","CONFINEMENT helper-raw-roster-reads=0; view rebuilt per consumer","FORGER INCONCLUSIVE-definition-in-pasted-text=False; in-L5-ruling=True","CONTRACTS completed"]},
      "expected":{"exit_code":0,"tail_regex":"CONTRACTS completed"}
    },
    {
      "id":"V3","kind":"test",
      "cmd":"PYTHONPATH=.:/tmp/278ebc9e/r3bref python3 -B /tmp/278ebc9e/r3bref/probe_delta.py mutations > /tmp/278ebc9e/r3bref/mutations.log 2>&1",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["M2 B1 original=REFUSE remove-superseded-clause=REFUSE witness-kills=False","M2 B2 original=REFUSE remove-superseded-clause=REFUSE witness-kills=False","M2 corrected-parent-live-singles-voided=distinguishes non-equivalent=True","M1 componentwise-upper-bounds B1=REFUSE; exact <= mutation unspecified","M8 duplicate-terminal=inv_11 before provenance; equivalence exemption applicable","MUTATIONS completed"]},
      "expected":{"exit_code":0,"tail_regex":"MUTATIONS completed"}
    },
    {
      "id":"V4","kind":"test",
      "cmd":"PYTHONPATH=.:/tmp/278ebc9e/r3bref python3 -B /tmp/278ebc9e/r3bref/probe_delta.py malformed > /tmp/278ebc9e/r3bref/malformed.log 2>&1",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["REFRESH prescribed-structure-only= KeyError: 'large:decode:1:0:single:1'","REFRESH existing-seal-wrapper= PackingRefusal: inv_52: malformed roster","COMPOSE existing-operator-exceptions= 0 first= None","COMPOSE remove_single+flip_late refresh-error-then-raw-KeyError= 1 first= (291013, 3, 14, \"KeyError: 'small:decode:2:2:single:0'\")","MALFORMED completed"]},
      "expected":{"exit_code":0,"tail_regex":"MALFORMED completed"}
    },
    {
      "id":"V5","kind":"test",
      "cmd":"PYTHONPATH=. python3 -B /tmp/278ebc9e/r3bref/probe_r3.py corpus > /tmp/278ebc9e/r3bref/corpus.log 2>&1",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["CORPUS seed=291013 cases=12 rosters=420","CORPUS seed=291014 cases=12 rosters=398","CORPUS seed=291015 cases=12 rosters=508","CORPUS seed=291016 cases=12 rosters=542","CORPUS total_cases=48 rosters=1868 violations=0 removal_third_same=True"]},
      "expected":{"exit_code":0,"tail_regex":"CORPUS total_cases=48 rosters=1868 violations=0 removal_third_same=True"}
    },
    {
      "id":"V6","kind":"test",
      "cmd":"PYTHONPATH=.:/tmp/278ebc9e/r3bref python3 -B /tmp/278ebc9e/r3bref/probe_contract.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["FIXTURE judge_probe.py present= False","CONTRACT probes complete"]},
      "expected":{"exit_code":0,"tail_regex":"CONTRACT probes complete"}
    },
    {
      "id":"V7","kind":"test",
      "cmd":"PYTHONPATH=.:/tmp/278ebc9e/r3bref python3 -B /tmp/278ebc9e/r3bref/probe_extra.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["SCOPES disjoint=True preserved_stress_requirement_already_present= True","EXTRA probes complete"]},
      "expected":{"exit_code":0,"tail_regex":"EXTRA probes complete"}
    },
    {
      "id":"V8","kind":"suite",
      "cmd":"PYTHONPATH=. python3 -B -m unittest tests.test_scored_packer",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 37 tests in 10.063s","OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V9","kind":"inspection",
      "cmd":"tail -6 /tmp/278ebc9e/r3bref/malformed.log && git status --short --branch && git rev-parse HEAD",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","0fa4e6e3bdb55e1cf4129cd4b027a4c00b54f97e"]},
      "expected":{"exit_code":0,"tail_regex":"0fa4e6e3bdb55e1cf4129cd4b027a4c00b54f97e"}
    }
  ],
  "flags": [
    {
      "id":"RULING",
      "kind":"lead_ruling",
      "level":"blocking",
      "text":"R3b cannot be issued verbatim without resolving contradictory ownership, mutation witnesses and formation semantics.",
      "needs":"Rule the replacements below and finish the Gate 0 boundary table before dispatching K and P."
    },
    {
      "id":"LIMIT",
      "kind":"verification_gap",
      "level":"nonblocking",
      "text":"Executed scratch models and baseline checks, not an integrated R3b implementation or its complete merge gate.",
      "needs":""
    }
  ]
}
```

## Findings

**Do not dispatch R3b verbatim.** References below are to [the extracted final texts](/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/70-a291-final-texts-r3b.md). Probe passes mean the assertions—including defect reproductions—passed.

| ID | Severity | Location | Finding and evidence |
|---|---|---|---|
| D1 | **BLOCKER** | R3b-0, line 19 | “Every other code raised in `scored_registration.py`” assigns `inv_51` to **registration**, while the explicit seal list also includes it. Exactly-one-owner cannot hold. V2 reproduces this overlap. |
| D2 | **BLOCKER** | R3b-5(4), line 29 | B1 still violates the count clause after removing the superseded-holder clause. It cannot kill m2. This mutant is **not equivalent**: reviving the parent while voiding its live singles distinguishes it. The ruling’s L4 mentions that corrected witness, but the pasteable text drops it. Also, m1’s `→ ≤` is not an exact mutation; componentwise upper bounds still reject B1. V3. |
| D3 | **BLOCKER** | R3b-1, line 21 | “Per model” formation loses cross-model order. Sorting the legal contrast’s blocks by model preserves every per-model sequence. The scratch implementation accepts it through both seals; the amended checker reports seal-owned `inv_10`. This is an escape under R3b-5’s own stop rule. V1. |
| D4 | **MATERIAL** | R3b-4 AST pin, line 27 | `SEAL_CODES` must contain `inv_27`, but none of the prescribed implementation sites emits it. Planned-drift staleness remains covered by `_seal`’s `stale_derived`, with an existing test requiring that code. The literal-code scan therefore requires an additional policy choice or a vacuous extra call. V2 and source inspection. |
| D5 | **MATERIAL** | R3b-2/3, lines 23–25 | Copying `witnesses()` alone raises `NameError: term`. After supplying that dependency, its raw B1 returns checker `INV-52` because digest fields remain unsealed; raw AUD-1 reaches verification refusal `inv_02`, not formation. Independent resealing makes all three requested checker RED tests discriminate correctly. V2. |
| D6 | **MATERIAL** | R3b-4 refresh-error branch, line 27 | The prescribed edits leave `_structure` without `_seal`’s exception translation. On an actual required base—seed `291013`, case `3`, final roster `14`—`remove_single + flip_late` makes refresh fail, then direct `_structure` raises raw `KeyError`. V4. |
| D7 | **MATERIAL** | R3b-5(7), line 29 | The pasted text names three outcomes but omits their definitions. L5/F9 elsewhere in the ruling expressly classifies infrastructure failure, timeout without a candidate and unadjudicable output as `INCONCLUSIVE`. Those conditions need to accompany the acceptance gate, rather than requiring a seat to reconstruct them. V2. |

**F1–F9 disposition**

| Prior finding | Disposition |
|---|---|
| F1 | **Cured:** formation-first AUD-1 refusal and direct conservation evidence agree; verification inputs need D5’s sealing precondition. |
| F2 | **Not cured:** the INV-37/38 split works, but the fixed code map assigns `inv_51` twice; D1. |
| F3 | **Not cured:** original registration/replay conflicts improve, but literal coverage still conflicts with the retained drift check; D4. |
| F4 | **Not cured:** redundant third-clause deletion is removed and equivalence is allowed, but m2 now requires an impossible B1 kill; D2. |
| F5 | **Cured:** view accesses are distinguished from raw accesses, permitted readers are enumerated, and each consumer rebuilds the view. |
| F6 | **Not cured:** renamed-parent and wrong-level defects are fixed, but the required formation relation still omits global parent order; D3. |
| F7 | **Not cured:** canonical constructors and blind-development baseline are identified, but fixture dependencies and sealing preparation remain incomplete; D5. |
| F8 | **Not cured:** skips, exceptions and population are addressed, but the prescribed refresh-error submission still crashes; D6. |
| F9 | **Not cured:** adjudication, conjunction and ownership-only stop triggers are repaired; outcome definitions were dropped from the pasteable text; D7. |

**Exact replacement text**

**D1 — amend R3b-0’s fixed assignments:**

> Registration-owned codes are `inv_06`, `inv_09`, `inv_51`, `unselected_arm_entry`, `item_ids_by_level_keys`, and `unequal_level_sizes`. Remove `inv_51` from the seal-owned list. Its first `_seal` check remains a required registration precondition, not a second ownership assignment. Remove `inv_49` from the executed list: INV-49 uses the seal-owned codes `stale_derived` and `spread_minima`; no new `inv_49` code is introduced. The magistrate supplies the completed, disjoint code table before either seat begins.

**D2 — replace m1/m2 and clarify the mutation boundary:**

> For m1, replace only the allowed-count predicate with `len(LIVE) <= 1 and len(TERM) <= 1`, retaining the superseded-holder clause. Kill it at `_conserve` with `probe-D-type-clean`, whose affected item has counts `(1,1)`. For m2, remove only the superseded-holder clause. Starting from B1, move every live listing of that superseded parent’s singles to the same envelope’s `voided_block_ids`, leaving the parent live. Assert counts `(1,0)` for every affected item. Original `_conserve` refuses; m2 accepts. B1 alone is not an m2 kill witness. Report predicate-level kills separately from integration-level kills; retain the equivalence exemption for mutants masked by other mandatory predicates.

The m8 duplicate-terminal target is masked by conservation at the integrated boundary; the new equivalence exemption handles that case.

**D3 — replace `_formation`’s predicate:**

> `_formation(registration, view)` compares the single global ordered list of all parents’ `(block_id, model, level, items)` against the complete §3.1 derivation: levels in `LEVELS` order, within each level models in `8B` then `1.7B` role order, and within each model slices in increasing slice index. Exact IDs and list order must match; otherwise raise `inv_10`, detail `"formation"`. Include a regression that changes only cross-model parent order.

**D4 — replace the literal-code coverage assertion:**

> Pin a coverage table mapping every seal-owned checker code to its implementation predicate site, emitted refusal code and behavioral witness. A checker code need not occur as the implementation’s literal refusal code when the table explicitly records the correspondence. In particular, `inv_27` is covered by `_seal`’s planned-drift equality check emitting `stale_derived`; preserve that refusal expectation. Retain the replay-code exclusion, registration-site scan and first `_seal` registration-precondition assertion. An unconditional or unreachable `_need` does not establish coverage.

**D5 — replace the witness-copy/preparation instructions:**

> Copy both `term()` and `witnesses()` from the exhibited probe, supplying `deepcopy`, `_split_route` and `refresh_derived`. In K’s test module, resolve `_split_route` after test-module initialization to avoid a circular top-level import. Preserve P’s pinned-baseline imports during blind development. Use separate deep copies for each boundary: raw constructor output for `_structure`, `_conserve` and `_seal(finalize=True)`; independently resealed output for `_seal(finalize=False)` and checker calls. Resealing computes `d = digest(m)`, sets `m["sha256"] = d`, and sets the last event’s digest to `d`, or `registered_sha256` to `d` for a root. Do not use the production seal to prepare invalid checker witnesses.

**D6 — replace the refresh-error submission and add its P-side boundary:**

> P supplies `_prederived_structure(registration, roster)`, which calls only `_structure` and applies `_seal`’s existing exception-to-`PackingRefusal` translation. It does not derive fields, validate digests or finalize the roster. On `refresh_derived` exception, K records `refresh_error` and submits the unchanged mutant to this boundary. Require typed refusal; normal return or an untranslated exception fails. Pin `remove_single + flip_late` on seed `291013`, case `3`, final roster as a regression.

**D7 — replace the outcome sentence:**

> `ESCAPE` means a reproduced candidate passes both seal modes and violates a seal-owned checker clause or the independent ownership predicate. `COMPLETED_NO_ESCAPE` requires completed execution of the bounded search and magistrate adjudication of every submitted candidate, with no escape. Infrastructure failure, incomplete execution, timeout without a submitted candidate, or unadjudicable output is `INCONCLUSIVE`, never `COMPLETED_NO_ESCAPE`. One inconclusive run is retried with a fresh seat; a second escalates.

There is **no K/P write-scope collision**. Completing the remaining boundary assignments is explicitly magistrate-owned Gate 0 work. The seats should receive that completed table and the corrected text, rather than choose these semantics themselves.

Probe commands and exact tails appear in V1–V9. The executable scratch model is [probe_delta.py](/tmp/278ebc9e/r3bref/probe_delta.py). Repository files remain unchanged.

## Residual risk

This reviews proposed text through scratch models, not completed K/P changes. The full composed corpus, canonical discovery suite, similarity screen, timing gate and forger gate were not run. The baseline’s 37 packer tests passed; the ownership corpus passed all 1,868 rosters.

The bounded composition probe observed **zero operator exceptions**; D6 concerns the separately reproduced refresh/structural exception path. No Claude, other agents, hardware measurements or prohibited system actions were invoked.