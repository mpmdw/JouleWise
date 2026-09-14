```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Only the pure rename landed; the claimed README, live-pointer, whitespace, and dated-note fixes are absent.",
  "workspace": {
    "base_requested": "a4bb8838",
    "base_mode": "descendant",
    "head_start": "8727a84cfcbc09f01ee5fdfa371d6ddc8eb08586",
    "head_end": "8727a84cfcbc09f01ee5fdfa371d6ddc8eb08586",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"should_fix","title":"Live references remain broken, including references newly broken by the sibling move"},
      {"id":"F2","severity":"should_fix","title":"Archive README omits the new sibling and understates totals","location":"docs/legacy/README.md:20"},
      {"id":"F3","severity":"nit","title":"All six branch-added whitespace defects remain"},
      {"id":"F4","severity":"nit","title":"Required dated fix-round note is absent","location":"docs/process_traces/2026-09-10-side-threads/docs-thin-01-RESUME.md:291"},
      {"id":"F5","severity":"nit","title":"Historical old-path citations remain; accepted by README:16 policy"}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"lint",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    },
    {
      "id":"V2","kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness tests.test_gen_state","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 75 tests in 4.228s","OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V3","kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint tests.test_paper_comparison_placements tests.test_paper_reported_energy tests.test_paper_custody","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 103 tests in 59.391s","OK","KILLED 130 owner-source mutations and 5 grant-policy mutations: stale receipts refused","PENDING production Git-blob role: fixture coverage is not production coverage","PENDING production Git-blob role: fixture coverage is not production coverage","KILLED 4 refusal AST mutations: dead literal, undeclared call, variable argument, declared-only code"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V4","kind":"lint",
      "cmd":"git diff --check a4bb8838..HEAD","cwd":".",
      "observed":{"result":"fail","exit_code":2,"tail":["docs/process_traces/2026-09-10-side-threads/docs-thin-01-test-pinned-paths.txt:86: trailing whitespace.","+docs/process_traces/2026-08-30-prefill-margin-coldgate/ and the "]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    },
    {
      "id":"V5","kind":"inspection",
      "cmd":"git diff --stat a4bb8838..HEAD -- . ':!docs' ':!*.md'","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[" tests/test_docs_freshness.py | 2 ++"," 1 file changed, 2 insertions(+)"]},
      "expected":{"exit_code":0,"tail_regex":"1 file changed, 2 insertions"}
    },
    {
      "id":"V6","kind":"inspection",
      "cmd":"git status --short","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    }
  ],
  "flags": []
}
```

## Findings

No runtime blocker found. The reviewed commit’s message claims FIX-1 through FIX-4, but its entire delta is one rename:

```text
$ git diff -M100% --diff-filter=R --name-status ae5b09e7..HEAD
R100	docs/process_traces/RESUME-2026-07-26.md	docs/legacy/process_traces/RESUME-2026-07-26.md

$ git diff -M ae5b09e7..HEAD --stat
 docs/{ => legacy}/process_traces/RESUME-2026-07-26.md | 0
 1 file changed, 0 insertions(+), 0 deletions(-)

$ git show HEAD:docs/legacy/process_traces/RESUME-2026-07-26.md | wc -c
   13223
```

Both `git show HEAD:docs/legacy/process_traces/RESUME-2026-07-26.md | shasum -a 256` and `git show ae5b09e7:docs/process_traces/RESUME-2026-07-26.md | shasum -a 256` returned:

```text
6fd4c507ee42f723514de6a9622488dbb0a6580afc7f49678a1a0f71f8dc27f1  -
```

**F1 — should-fix: live pointers remain broken.**

The four explicitly targeted reading surfaces remain unchanged:

- `RUN_STATE.md:7–8`: still names the old three sibling paths. The delta now breaks the 26 reference too.
- `docs/paper/results-fill-registry.md:132`: still points to `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`.
- `docs/project_critique_review.html:880`: still has `href="test_audit_2026-07-07.md"`.
- `docs/specs/axi/sb_static_batch_verdict.md:200`: still points to `docs/process_traces/2026-07-16-axi-sb-live-probes/axi-sb-b2.jsonl`.

Existence probes passed for the intended destinations, not the pointers currently written:

```text
test -e docs/legacy/process_traces/RESUME-2026-07-26.md => rc 0
test -e docs/legacy/process_traces/RESUME-2026-07-27.md => rc 0
test -e docs/legacy/process_traces/RESUME-2026-07-28.md => rc 0
test -e docs/legacy/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md => rc 0
test -e docs/legacy/process_traces/2026-07-16-axi-sb-live-probes/axi-sb-b2.jsonl => rc 0
(cd docs && test -e legacy/test_audit_2026-07-07.md) => rc 0
```

All six corresponding old-target probes returned **rc 1**.

The census also identifies these living reading surfaces:

- `docs/process/model_allocation_ledger.md:96,220`: the standing-assignment explanation and current assignment table cite the newly moved 26 sibling.
- `docs/site/run_state.html:1`: rendered orientation still names the old sibling paths.
- `docs/site/record.html:1`: navigation links include `href="../process_traces/RESUME-2026-07-26.md"`, newly broken by this delta; 27/28 links were already stale.
- `docs/site/readme.html:1`: retained reading page links to the moved exploratory-block results. This is a surviving whole-PR issue, not introduced by this fix delta.

The sibling search found **no reference in state_kernel.json, gen_state, tests, scripts, configs, or joulewise**. Its remaining matches are the reading surfaces above and historical records listed below.

**F2 — should-fix: README arithmetic is internally consistent but incomplete.**

`docs/legacy/README.md:20` still says **309 files, 83,121,775 bytes, 79.27 MiB**; `:24` still attributes the table solely to `f6aed467`. There is no row for the 26 sibling.

Mechanical computation, replayable with `python3 -B /tmp/ref329-r1-audit.py`:

```text
TABLE: 16 rows; sum(Files)=309; sum(Size)=83121775; MiB=79.27
RENAMES: count=310; bytes=83134998; MiB=79.28; missing table delta=1 file, 13223 bytes
```

The script sums the numeric Files and Size columns and independently sums destination Git-blob lengths for all renames. The required corrected totals are **310**, **83,134,998**, and **83,134,998 / 1,048,576 = 79.28 MiB** rounded to two decimals.

**F3 — nit: FIX-3 did not land.**

`git diff --check a4bb8838..HEAD` returns **2**, identifying:

- `docs/process_traces/2026-09-10-side-threads/docs-thin-01-RESUME.md:208,225,231`
- `docs/process_traces/2026-09-10-side-threads/docs-thin-01-test-pinned-paths.txt:63,80,86`

**F4 — nit: FIX-4 did not land.**

The resume note ends at `:291`, without the required dated fix-round entry. Searching it for `2026-09-13|FIX-[1-4]|fix round` returns **rc 1**, no output.

**F5 — nit, accepted historical references: complete census.**

Literal search used all **310 moved source paths** across **3,291 surfaces**, excluding `docs/legacy/` and **3,311 dated trace files**. It produced **296 matching lines**: **191 filename-substring false positives**, **9 living-surface lines** listed in F1, and **96 historical lines** below. Runtime matches were only false positives such as `STATUS.md` inside `PROJECT_STATUS.md`.

[Every literal hit with file, line, and classification](/tmp/ref329-r1-classified.tsv), [unabridged matching text](/tmp/ref329-r1-literal.txt), and [sibling-search output](/tmp/ref329-r1-sibling-pins.txt) are retained in temp storage.

All following locations are classified **dated/historical record — nit, accepted under `docs/legacy/README.md:16`**:

```text
RUN_STATE.md:2192,2614,2829,2841,2919,3019,3045,3134,3171,3832,3922,3983,4002,5505,5507,5591,5595,5597,5600
TASK_QUEUE.md:184
docs/advisor_briefs/2026-07-17-window-a-brief.html:962,1020,1038,1100
docs/council_log.md:2740,3041,3050,3206,3355,3367,3397
docs/decision_log.md:170,3651,3974,3992,4013,8186,8694,8987,9177
docs/paper/draft-v1-review-round2-lensA.md:30,41,52,62,125
docs/process/model_allocation_ledger.md:395
docs/reviews/2026-07-13-comprehensive-audit/manifests/EXCLUDED.txt:12,13,14,15,16,17,18,19,20,166
docs/reviews/2026-07-13-comprehensive-audit/receipts/WO-021-pre-demotion-freeze-cross-check.json:179
docs/run_reports/2026-07-13-bridge-v11.md:122
docs/run_reports/2026-07-16-resumption-nohw-batch.md:89
docs/run_reports/2026-07-17-window-a-floors.md:261,318
docs/run_reports/2026-08-07-paper-first-session.md:63
docs/run_reports/2026-08-08-t1-window-session.md:28
docs/run_reports/2026-08-10-t4-window-session.md:3,7,26,39,71,73,123,124,135,207
docs/run_reports/2026-08-12-t4-late-addendum.md:46,120,161,166
docs/run_reports/2026-08-12-t5-window-session.md:20,286,417
docs/run_reports/2026-08-13-t6-session.md:463,545,609,885
docs/run_reports/2026-08-23-t21-t22-session.md:814
docs/site/advisor_brief.html:963,1021,1039,1101
docs/site/council_log.html:1
docs/site/decision_log_archive_1.html:1
docs/site/decision_log_archive_4.html:1
docs/site/project_status.html:1
docs/site/task_queue.html:1
docs/stream_logs/2026-07-17-advisor-brief.md:68
docs/stream_logs/2026-07-17-axes-foldin.md:4
```

## Residual risk

The requested focused suites passed; the full canonical suite was not run for this documentation delta. Literal scanning does not prove absence of dynamically assembled paths. Fixture results do not establish live hardware validation. No tracked files were edited; final status is empty and HEAD unchanged.

**What the lead should double-check:** inspect the committed tree against the seat’s working-tree changes. The reviewed commit contains only the rename despite claiming all fixes. Land the missing authorized changes, address the sibling’s newly broken reading references, and rerun the exact-head checks before the final gate.

Same signature as a round-0 finding? **YES** — the same live reading surfaces still point at moved paths, and the sibling rename introduces additional instances.