```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "No blocker found. F1/F2 prose defects are closed; 79 tests and literal extraction pass; this diff does not repeat the same-signature class.",
  "workspace": {
    "base_requested": "76a2f2a73be3f5337155730fb88ce5ff555d19d0",
    "base_mode": "exact",
    "head_start": "ff3b59b91d68d4bb504ca1f1b42141efeb8dc081",
    "head_end": "ff3b59b91d68d4bb504ca1f1b42141efeb8dc081",
    "upstream_end": "76a2f2a73be3f5337155730fb88ce5ff555d19d0",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "closures": {
      "F1": "Closed at the affected prose and ledger sites: binary64 is glossed at first main-text use; both rows use a header-defined status supported by the text.",
      "F2": "Closed: README Next no longer directs merging the completed paper pass."
    },
    "same_signature": {
      "answer": "no",
      "reason": "This diff restores the missing first-use gloss and aligns ledger dispositions with actual definitions. It creates no orphaned term, false gloss certification, or changed figure/pin dependency."
    },
    "numerals": {
      "existing_numerals_changed": false,
      "added_tokens": {"64": 1},
      "removed_tokens": {},
      "qualification": "The sole draft-line replacement adds '(the usual 64-bit floating-point format)'. Removing that insertion reproduces the base draft exactly; no measured value or existing numeral changes."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint tests.test_docs_freshness tests.test_paper_replay_fence tests.test_d165_rationale_census",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 79 tests in 33.478s",
          "",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 79 tests in [0-9.]+s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 -B scripts/check_paper_replay_fence.py --literals-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "LITERALS 22 extracted from /Users/edr/code/JouleWise-wt-postmerge-331/docs/paper/draft-v2-skeleton.md",
          "INTERNAL MISMATCHES 0"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "INTERNAL MISMATCHES 0"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "sed -n '1,921p' docs/paper/draft-v2-skeleton.md | grep -n binary64",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "740:The event-duration statistic subtracts binary64 (the usual 64-bit floating-point format) epoch values before rounding;",
          "742:strings. Their last digits need not equal the binary64 duration statistic."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "740:.*\\n742:.*"}
    }
  ],
  "flags": []
}
```

## Findings

**No blocker found.** Blocker: none. Should-fix: none. Nit: none in this diff.

**F1 closure.** Draft line 740 reads:

> The event-duration statistic subtracts binary64 (the usual 64-bit floating-point format) epoch values before rounding;

The complete search over lines 1–921 returns only lines 740 and 742, reproduced in V3. Thus binary64 is glossed at its first main-text use; no earlier main-text use exists.

The ledger header defines:

> `built-before` means the body constructs the referent from physical inputs before its first named use.  
> `glossed-at-first-use` means the first named use supplies a plain-word definition or an equivalent calculation in the same sentence or paragraph.  
> `audience-vocabulary` means a textbook-statistics or plain-English expression the intended metrology/CS professor uses without definition; that class here is exactly: repeatability, repetition, random scatter, complete, completeness, sampler cadence, refused, refuses, missing, malformed, corpus range, degrees of freedom, threshold, exact equality, null hypothesis, tail area, quarantine, append-only, run bundle, full-history checkout, third-party dependencies, cumulative counter, linear programme, infeasible, argmin, and detected.  
> `forward-pointer-next-paragraph` means the first use carries an explicit cross-reference to a definition in the immediately following paragraph.  
> `FAILS` means the term is neither built before nor glossed at first use and therefore requires a prose cure or deletion.

Both changed rows, quoted verbatim:

```text
| binary64 / member-envelope integral sum | Record support in two historical model stacks | glossed-at-first-use | Binary64 is glossed at its first main-text use as the usual 64-bit floating-point format; the member-envelope integral sum is built in Appendix A.3.10 before its only use there. |
| resolution bound | Adding publication safeguards after the ratio | glossed-at-first-use | Registered operational resolution guard for assigned-energy differences in one cell; its first use in the protocol supplies that definition. |
```

Both use a defined status with a gloss supported by the prose. Protocol lines 240–242 say:

> The ratio is calculated before the safeguards used to publish the final  
> resolution bound, the registered operational guard for assigned-energy  
> differences in this cell.

**The member-envelope integral sum is built before operational use.** A.3.10 introduces it at lines 1370–1372:

> The **member-envelope  
> integral sum** is  
> \(\sum_{m\in\{A_1,B_1,B_2,A_2\}}|c_m|\int_{\mathrm{start}_m-b}^{\mathrm{end}_m+b}P_m(t)\,dt\),

The following lines define the weights and power trace and explain the nonnegative joule scale before its use in \(M=\max(\ldots)\) at line 1378. Later numerical illustrations remain in A.3.10. The ledger’s “only use there” is accurate as a location statement; the phrase occurs multiple times within that subsection.

**F2 closure.** README line 12 now says:

> **Next:** harvest the night on 2026-09-13 and apply the pre-registered equivalence rule.

**Pin check.** The draft diff contains exactly one replaced line. No existing numeral changed or disappeared. Strictly, the insertion adds one numeral token, `64`, in “64-bit”; therefore “no numeral added” would be inaccurate. Removing the new parenthetical reproduces the base draft exactly.

**Same signature: NO in this diff.** Records 16/21 identify uses orphaned by moved or deleted definitions; records 21/28/31 also discuss certification exceeding its evidence. Here the actual first-use site is repaired and the ledger agrees with the prose. No figure, numerical calculation, or replay consumer changes. This does not revise those earlier records’ historical verdicts.

## Residual risk

The tests still validate status names without enforcing membership in the header’s exact audience-vocabulary list. That existing general coverage limitation remains; direct inspection establishes these two rows’ correctness.

No paper build, full canonical suite, site build, or hardware validation was performed. The requested checks passed with tails recorded above. HEAD and the clean workspace remained unchanged.

No runner output path was supplied; this response is the report for runner capture. Next exact step: lead adjudication of this review.