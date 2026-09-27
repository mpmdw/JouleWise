```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Close a bounded regression guard, not a universal Python safety proof; fix ordinary scope/reference gaps, reader retargeting, truthful classifications, and the failing inventory.",
  "workspace":{"base_requested":"315364b2","base_mode":"exact","head_start":"315364b2087ce413cc6c36347970838398796157","head_end":"315364b2087ce413cc6c36347970838398796157","upstream_end":null,"branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[
    {"id":"F1","severity":"should_fix","summary":"The sweep's universal promise exceeds its mechanism; ordinary scope and callable-reference gaps warrant bounded repair."},
    {"id":"F2","severity":"should_fix","summary":"Retargeting a reader preserves authentication cached for another bundle; prefer a runtime single-bundle invariant."},
    {"id":"F3","severity":"should_fix","summary":"Envelope rows require a truthful gated classification; neither historical nor non_claim(ii) describes them."},
    {"id":"F4","severity":"should_fix","summary":"The existing sweep fails at the requested head on two run_campaign inventory discrepancies."}
  ]},
  "verification":[
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/samesig-3ba66eeb-astra python3 -B -m unittest tests.test_bfgs_consumer_sweep tests.test_bfgs_window_consumers tests.test_envelope_gate","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 61 tests in 33.717s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/samesig-3ba66eeb-astra PYTHONPATH=. python3 -B /tmp/samesig-3ba66eeb-astra/probe.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["envelope removed-callee-gate mutation: 5 energy records returned","envelope custody failure: propagated","probe assertions: PASS"]},"expected":{"exit_code":0,"tail_regex":"probe assertions: PASS"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/samesig-3ba66eeb-astra python3 -B -m unittest tests.test_bundle_read.StrictAccessorTests.test_historical_set_bytes_and_protected_base_paths_are_pinned","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 0.136s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}}
  ],
  "flags":[
    {"id":"R1","kind":"lead_ruling","level":"nonblocking","text":"Recommendations amend the sweep's acceptance boundary and envelope classification; this consult installs no ruling.","needs":"Cold judge adjudicates before the implementation brief."},
    {"id":"R2","kind":"verification_gap","level":"nonblocking","text":"Full suite and exhaustive current-tree claim-flow audit were not run; no live hardware validation was attempted.","needs":"Lead verifies the final implementation and current claim routes."}
  ]
}
```

## Findings

**Q1. Structure — The universal promise is not closable; a bounded static regression guard is. This is the same rule-11 signature.**

F1 — **SHOULD-FIX.** Each round expands syntactic recognition while retaining the claim that a green sweep prevents every future ungated read. Arbitrary Python does not support that promise through a finite catalogue of recognized forms. Conservative rejection of unsupported constructs can be sound, but that is a restricted programming model requiring explicit adoption.

The repeated signature is **unmodelled execution or binding invalidates syntactic gate recognition**, not merely “five findings again.” B-4 is a separate classification error; grouping every finding as an evasion obscures it.

Evidence: both refuter reports; first ruling’s amendments 57–59; erratum §4 and amendments 57–60; `tests/test_bfgs_consumer_sweep.py`. My V2 reproduced silent lambda, conditional-definition and module-level reads, with a reported direct-call control.

**Q2. Threat model — Keep protections against ordinary programming mistakes; do not classify intent solely from syntax.**

D-161 explicitly retains fail-closed protection for physics/evidence **and operator mistakes**, while retiring deliberate-only guards. An agent implementing a future refactor can make the relevant mistakes.

- **B-1: plausible accident, high priority.** Nested definitions, callbacks and `__main__` blocks are ordinary code. Cover their reads without inheriting a gate from a scope that may execute at another time.
- **B-2: predominantly deliberate replacement in the presented probes.** Patching authentication to return acceptance or manufacturing a subclass that disables it is outside ordinary reader use. Accidental deployment of test patches is possible, but these probes do not establish that production route. Do not expand S1 into a monkey-patching security boundary.
- **B-3: plausible misuse, lower frequency but real.** Reusing a reader by changing its path can be an attempted optimization, without intent to evade science policy. V2 reproduced a charging trace returned under the first bundle’s cached authentication.
- **B-4: an actual classification defect.** It concerns neither hypothetical intent nor a current energy leak.
- **B-5: plausible accident, high priority.** `map`, callbacks, aliases and `partial` are normal refactors. Taking a reference must invalidate an incomplete caller proof; a gate before reference creation does not prove a gate before eventual invocation.

**Q3. Recommended design — Choose (d): bounded (b), plus a small runtime single-bundle invariant.**

F2 — **SHOULD-FIX.** Make `BundleReader`’s construction root immutable through its ordinary interface: for example, constructor-owned backing storage with a read-only `_path` property. A different bundle requires a fresh reader and fresh cache. This rejects B-3 at assignment, including before tolerant reads, without expanding a repository-wide blacklist of attributes named `_path`.

The change belongs in `joulewise/bundle_read.py`, with a focused regression in `tests/test_bundle_read.py`. It requires no `battery_float.py` change, no FT §E excluded-file change, and no consumer import of `battery_float`.

Keep the sweep as a bounded inventory and regression guard, including ordinary gate-order, receiver, path and reference checks. State explicitly that it neither proves arbitrary Python safe nor establishes complete data provenance.

Do **not** add token parameters throughout tolerant APIs or rehash whole bundles on every accessor for S1. Readers also operate during reduction before finalization; whole-bundle digest changes need lifecycle semantics, not an improvised cache check.

A future claim-boundary check could validate the complete contributing roster against authenticated bundle identities and verdicts. That would be useful only if the roster is complete and bound to the actual numerical inputs. Checking supplied `"pass"` values alone is insufficient, and a universal writer retrofit crosses frozen paths such as `scripts/render_results_fills.py`. It is not the smallest S1 fix.

Evidence: `BundleReader.__init__`, `metadata`, tolerant accessors and `trace_rows`; `authenticate_window_members`; FT §E; V2. The protected-file pin passed, and an AST inspection found no battery imports in the eight consumers.

**Q4. B-4 — Reclassify truthfully before closure; do not add production calls merely to satisfy the detector.**

F3 — **SHOULD-FIX.** AP-5’s inclusion and disqualification rules make the envelope verdict licensing evidence. Absence of a tracked code reader does not make it `non_claim(ii)`. The present `historical` rows are also false.

Have the judge authorize a **closed, explicitly evidenced callee form of `behind_gate`** for these two rows. Record the actual route: all admitted readers pass `_manifest_record → metadata` before the summary reads, and failures leave before energy is emitted. Pin that route with positive controls, refusal/custody tests, and the gate-removal mutation.

V2 reproduced refusal without energy, custody propagation, and **five energy records after removing the callee gate in memory**. This supports a concrete classification without building a general interprocedural analyzer.

The redundant `metadata()` calls may be considered with the separate envelope reason-code lane if they improve maintainability. They need not precede S1. Their claimed behavior identity depends on the present call graph and caching; it is not an unconditional property of the helper API.

**Q5. Fix round 3 — Implement a finite package in this order.**

1. Replace amendment 51’s universal promise with the supported forms, trusted-code assumptions, explicit limitations and closure criterion.
2. Complete amendment 51’s already owed ordinary path/order/receiver coverage, then B-1 scope coverage and B-5 reference detection. Unsupported callable escapes require review, not automatic inherited gating.
3. Add the reader’s immutable-root invariant and a regression reproducing B-3’s passing-A/charging-B sequence.
4. Correct every allowlist condition, including the envelope rows and caller chains. Include B-6’s ordinary post-idle capture filename omission; it is a useful **NIT**, not adversarial hardening.
5. Recompute the actual-head inventory and repair F4 — **SHOULD-FIX**: V1 found an unlisted `evaluate_member/direct:read_text` and a stale `run_axi_spec_campaign/direct:read_bytes`. Apply the ruled consumers-form reasoning; do not merely accept both keys.
6. Run the finite mutation matrix, focused checks, protected-file/import fences and canonical suite; lead reviews actual claim routes.

B-2’s additional patch spellings, reflective mutation catalogues, B-9’s enlarged marker blacklist, the envelope reason-code lane and a universal capability/writer redesign **do not block S1 merge**. The current failed inventory and false classifications do require resolution.

**Q6. Stop rule — Close when the exact candidate satisfies one finite, judge-approved acceptance predicate.**

That predicate is: **the current claim routes have no ungated prospective energy contribution, every inventoried exception has a true evidenced condition, and the agreed supported-form/runtime regression matrix plus required checks passes.**

Do not use “no imaginable accidental edit” as the criterion: that is another unbounded search. A new spelling outside the declared model does not restart this lane without a demonstrated current leak, failure of an agreed supported case, or an explicit scope revision.

## Residual risk

No current claim leak was established by this consult; the earlier reports’ broader conclusions were not independently reproduced exhaustively. V1 passed 60 of 61 tests. Envelope probes used a mock suite with injected verdicts, not live charging measurements.

Root immutability does not prevent same-path byte replacement or reflective alteration of private backing state. The existing immutable-evidence/custody assumptions remain necessary. Existing historical/mock dispositions also mean `metadata()` success must not be described as universally equivalent to literal `pass`.

Recommendation: adopt bounded coverage plus an immutable reader root; stop extending the deliberate-evasion catalogue.  
Reclassify the envelope rows with tested callee-gate evidence and repair the actual-head inventory failure.  
Close after the finite acceptance predicate passes; leave broad runtime provenance redesign to its own lane.