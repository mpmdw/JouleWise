```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"REVIEW: HOLD — quiet-launch notice.ack can erase an undelivered required fault.",
  "workspace":{"base_requested":"32ff901374024defa97fc3d137c5a699423676e7","base_mode":"exact","head_start":"fca99d0432efd97abf124602d8089c8f7a60c65c","head_end":"fca99d0432efd97abf124602d8089c8f7a60c65c","upstream_end":"32ff901374024defa97fc3d137c5a699423676e7","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"decision":"HOLD","findings":[{"id":"F1","severity":"blocker","file":"docs/process/MAGISTRATE_RELAUNCH_PROMPT.md","line":6,"summary":"A quiet-launch acknowledgment clears notices queued after prompt rendering without delivering them.","verification":"V4"},{"id":"F2","severity":"should_fix","file":".github/pull_request_template.md","line":13,"summary":"The retained full|light instruction is parsed as a table row, so correctly filled templates fail.","verification":"V3"}]},
  "verification":[
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/procprunerev python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/procprunerev python3 -m unittest tests.test_magistrate_watchdog.SupervisorTests.test_notice_ack_is_consumed_before_child_exit tests.test_magistrate_watchdog.BackoffAndEventTests.test_notice_ack_clears_only_the_current_activation tests.test_magistrate_watchdog.ContractTests.test_prompt_has_at_most_twenty_five_lines_and_required_order tests.test_magistrate_watchdog.ContractTests.test_first_install_adopts_current_tree_and_arming_stays_outside_charter","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V3","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/procprunerev python3 /tmp/procprunerev/review_cases.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["CASE_MATRIX_OK: 26 cases matched expected exits"]},"expected":{"exit_code":0,"tail_regex":"CASE_MATRIX_OK"}},
    {"id":"V4","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/procprunerev python3 -c \"import runpy; runpy.run_path('/tmp/procprunerev/notice_race.py', run_name='__main__')\"","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["NOTICE_SUPPRESSION_REPRODUCED"]},"expected":{"exit_code":0,"tail_regex":"NOTICE_SUPPRESSION_REPRODUCED"}}
  ],
  "flags":[]
}
```

## Findings

**REVIEW: HOLD**

- **F1 — blocker — `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:6`.** Render a quiet prompt with `notice_pending=[]`; while launch reads/Gmail search run, the resident supervisor queues `network_uncertain`; the session writes the newly permitted no-email acknowledgment and exits. `scripts/magistrate_watchdog.py:1411–1412` clears the current queue by activation ID, including that undelivered fault. **Command: V4.** Remove acknowledgment from the no-email path; acknowledgments should cover only delivered notices.

- **F2 — should_fix — `.github/pull_request_template.md:13`, `scripts/check_gate_ledger.py:103`.** Both correctly filled full/light templates fail: the instruction’s `full|light` starts the parser’s table, and the following blank ends it before the real rows. This trap also exists at the base. Removing that instruction paragraph makes both pass. **Command: V3.**

The requested light/Yes, row-4 N/A/Yes, stale-head and missing-path cases all refuse. Each of the six Impact “Yes” answers refuses light tier and skipping the cold pass; number-changing bodies cannot omit review or suite evidence.

Old twelve-row bodies refuse at this head, even after renaming their heading. Already-open PRs become blocked once their heads incorporate the prune; the workflow checks out the PR head, so older heads retain their older checker.

The KEEP rules retain arm notice/NO, STOP, stand-down fences, raw calibration re-derivation, estimator write fences and merged-tree suite requirements. The triple audit remains, explicitly once per frozen code/protocol change. F1 weakens required fault delivery.

Requested tests: **73 passed**; focused watchdog tests: **4 passed**. Repository unchanged.

## Residual risk

`RUN README.md` satisfies evidence syntax even with Impact Yes. The checker validates attestations, not report contents or actual execution; fabricated evidence remains outside the documented D-161 threat model. No compliant number-changing exemption was found. Notice reproduction used fixture state; live Gmail and branch protection were not exercised.