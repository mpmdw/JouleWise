```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "S1 can close with a bounded accidental-edit sweep and truthful classifications; an exhaustive Python read-site guarantee cannot close.",
  "workspace": {
    "base_requested": "315364b2",
    "base_mode": "exact",
    "head_start": "315364b2087ce413cc6c36347970838398796157",
    "head_end": "315364b2087ce413cc6c36347970838398796157",
    "upstream_end": "97082508f3648ff8575c94b0cdfcf657ba440142",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "text": "The current sweep test fails at 315364b2 because its run_campaign.py allowlist differs from the detected reads; repair before merge."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "text": "The proposed exhaustive static guarantee has the same recurring incompleteness signature and must be narrowed."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "text": "B-1, B-3 and B-5 cover plausible accidental edits and merit bounded guards."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "text": "B-4's non_claim classification is false because the envelope verdict licenses AP-5."
      },
      {
        "id": "F5",
        "severity": "nit",
        "text": "B-6's raw-capture pattern misses the post-run idle capture name."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest discover -s tests -p 'test_bfgs_consumer_sweep.py'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "('scripts/run_campaign.py', 'evaluate_member', 'direct:read_text')",
          "('scripts/run_campaign.py', 'run_axi_spec_campaign', 'direct:read_bytes')",
          "Ran 3 tests in 2.391s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --stat cbfa9dc3..HEAD -- joulewise/bundle_read.py joulewise/envelope_gate.py tests/test_bfgs_consumer_sweep.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The cold judge must replace amendment 51's exhaustive guarantee with a stated accidental-edit boundary before implementation resumes.",
      "needs": "Rule on the narrowed S1 acceptance and the envelope change's production lane."
    },
    {
      "id": "FL2",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "The existing sweep test is red at the requested head.",
      "needs": "Reconcile its run_campaign.py rows and obtain a green merge-candidate suite."
    }
  ]
}
```

## Findings

### Q1 — Structure: **The exhaustive static guarantee is not closable; this is the same rule-11 signature.** F2, SHOULD-FIX.

Python can move a read through aliases, dynamic names, imports, descriptors or execution of generated code. Each syntactic rule can cover named forms, but cannot establish that *every* future execution path is gated. The two refuters found the same failure pattern twice: a green syntactic sweep despite a newly expressible ungated read. That warrants changing the promise, not another unrestricted erratum. I read both rulings and refuters; I also ran the current `sweep_source` on four small inputs: it reported a direct `raw_summary()` call and missed the same call in a lambda, a nested `def` under `if`, and module-level code, matching B-1.

### Q2 — Threat model: **B-1, B-3, B-4 and B-5 matter for mistakes; most of B-2 addresses deliberate patching.**

- **B-1:** Ordinary nested helpers, lambdas and `__main__` blocks are plausible additions. A missed read there can become a science error.
- **B-3:** Reusing a reader by assigning its private `_path` is less likely, but is a credible refactor mistake with an executed charging-bundle consequence. A narrow guard is justified.
- **B-4:** This is an existing false classification. The [AP-5 contract](/Users/edr/code/JouleWise-wt-samesig-sol-3ba66eeb/docs/contracts/analysis_plans.md:270) makes envelope validation a condition for scored claims; its verdict therefore cannot satisfy `non_claim` (ii).
- **B-5:** Passing a helper to `map` or storing it in a variable is normal Python refactoring. Caller checks must count references as well as direct calls.
- **B-2:** Replacing `battery_float.authenticate_bundle`, patching module attributes, or constructing a `type()` subclass requires an explicit intervention in gate machinery. The probes demonstrate real bypasses, but they principally defend against an in-process actor outside D-161’s threat model. They do not justify an expanding syntax blacklist.

### Q3 — Design: **Choose (b), with a narrow B-3 guard and B-4 correction.** F3, SHOULD-FIX.

Keep the static test as an inventory and a guard for ordinary, named edits. Cover every AST scope (B-1), helper references (B-5), and literal `_path` reassignment outside reader initialization (B-3). State its dynamic-Python limits in amendment 51(h); do not describe green as proof that no Python program can read energy without a gate.

The smallest possible runtime addition is a path binding in [BundleReader.metadata()](/Users/edr/code/JouleWise-wt-samesig-sol-3ba66eeb/joulewise/bundle_read.py:445): record the path associated with its cached verdict and reject a cache hit after `_path` changes. It closes B-3 more firmly, but it does not cover direct `Path` reads or a patched verdict source. I would use the simpler static B-3 guard for S1 and reserve that runtime change for evidence of actual reader reuse. Capability arguments would disrupt legitimate tolerant callers; a check at *every* claim writer needs a complete writer and contribution inventory, so it is not a small S1 replacement. None of the recommended S1 changes touches `battery_float.py` or the FT §E excluded files, or adds a `battery_float` import to an eight-consumer module.

### Q4 — B-4: **Add `reader.metadata()` immediately before both envelope `raw_summary()` sites, before closing S1’s allowlist.** F4, SHOULD-FIX.

The calls at [the summary check](/Users/edr/code/JouleWise-wt-samesig-sol-3ba66eeb/joulewise/envelope_gate.py:133) and [the energy-record loop](/Users/edr/code/JouleWise-wt-samesig-sol-3ba66eeb/joulewise/envelope_gate.py:654) already follow `_manifest_record(reader)`, which calls `metadata()` and refuses a failed reader. On the present path, an additional call returns cached metadata; it makes the dependency local and visible. Because this is a production edit outside the prior S1 test-only amendment, give the envelope lane explicit write authority and sequence it before final S1 allowlist classification. Do not retain `non_claim` (ii) with an acknowledged false condition. The separate incorrect envelope *reason code* may remain in its own lane: it refuses the bundle and releases no energy.

### Q5 — Fix round 3: **Implement a bounded completion, then stop adding evasion forms.**

1. Obtain the cold ruling that narrows amendment 51’s guarantee. Implement its existing tree inventory and honest classes, with B-1 scope coverage, B-5 reference coverage, the narrow B-3 `_path` rule, and B-6’s simple capture-name correction. Use defect-shaped mutations.
2. In the authorized envelope production lane, put `metadata()` before both reads; remove the false `non_claim` rows when S1’s allowlist closes.
3. Reconcile the current `run_campaign.py` allowlist mismatch, audit any raw-capture entry that actually supplies claim energy, run focused mutations and the required full suite, then review the exact merge candidate.

B-2’s patching and dynamic-subclass variants, further `exec`/dynamic-name variants, and B-7–B-9 do **not** block S1’s merge under the narrowed promise. An actual ungated claim contribution, a false allowlist class, or the currently failing sweep test **does**. The observed test failure is F1, BLOCKER for merge, not evidence that a bad energy value currently reaches a claim.

### Q6 — Stop rule: **Close when the exact merge candidate has no ungated prospective claim contribution, the named accidental-edit mutations fail the guard, and the suite is green.**

Apply that criterion once at the final head. A new exotic Python evasion without a plausible accidental edit or an observed claim path becomes a documented limitation, not another same-shape review round.

## Residual risk

The bounded sweep cannot detect a deliberately constructed accessor name, runtime monkeypatch, generated code, or every direct raw-file read. The round-two refuter reports no current ungated energy path into a claim artifact; I did not independently replay its charging-bundle probes or complete its 48-entry raw-capture classification. My local test found the existing allowlist failure noted above.

Recommend the cold judge narrow amendment 51 to accidental-edit coverage.  
Recommend B-1/B-3/B-5 guards and the envelope call-site fix before final classification.  
Recommend ending this lane at the stated final-head criterion, with dynamic Python limits recorded.