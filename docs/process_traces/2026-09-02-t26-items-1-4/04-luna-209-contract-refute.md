```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Read-only review found missing S9 decision dependencies, a non-binding same-task assertion, and a weak executed-evidence regex.",
  "workspace": {
    "base_requested": "6075389a",
    "base_mode": "exact",
    "head_start": "6075389a",
    "head_end": "2d24ef70",
    "upstream_end": "6075389a",
    "branch": "feat/2026-09-02-t26-install"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file:line": "docs/process/state_kernel.json:2215-2224, 4432-4452, 5338-5346; SHORTLIST.md:16-30",
        "ruled_text": "S9 SHORTLIST items marked gates the mint or gates windows are registered under item 1.",
        "landed_text": "Only kind: decision dependencies are D-110 on MINT-GENERALIZE-01 and D-170 on V5-TRANSACTION-01; T26-RULING-INSTALL-01 has dependencies: [].",
        "why_they_differ": "Required S9-01b, S9-02, S9-03, S9-04, S9-05, S9-06, and S9-12 registrations are absent."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file:line": "tests/test_docs_freshness.py:260-294; docs/process/state_kernel.json:4432-4452, 5338-5346",
        "ruled_text": "The installing task named by open (...) must exist and carry the kind: decision dependency targeting the row D-id.",
        "landed_text": "The test asserts task existence at lines 277-280, but computes dependent_tasks across every task at lines 282-289 and only asserts that list is nonempty at lines 291-294.",
        "why_they_differ": "T26 is named but has no dependency; V5-TRANSACTION-01 supplies the unrelated D-170 dependency. The test passes without proving the named task carries it. D-016's legacy open form is also skipped at lines 269-271."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "file:line": "tests/test_docs_freshness.py:114-134",
        "ruled_text": "A fenced block must hold a $ argv line plus an exit line, or the section must contain a file:line citation.",
        "landed_text": "The regex accepts any block matching both patterns, including `$ echo exit` on one line; citation extensions are limited to py, md, json, sh, toml, and yml.",
        "why_they_differ": "The implementation accepts a weaker same-line shape and rejects otherwise valid file:line citations using other file extensions."
      },
      {
        "id": "F4",
        "severity": "nit",
        "file:line": "docs/process_traces/2026-08-27-t26/process-proposals/README.md:13-16; docs/decision_log.md:10540-10543",
        "ruled_text": "The consult brief template gains an Executed: block, including or artifact-pair exhibit.",
        "landed_text": "No tracked template exists or changed; repository prose says the requirement is carried by a scratchpad template.",
        "why_they_differ": "The repository cannot mechanically verify this external template requirement."
      }
    ],
    "clause_table": [
      {"id":"C01","clause":"How-To documents open (installs via <TASK-ID>).","status":"CONFIRMED","file:line":"docs/decision_log.md:22-31","binding":"prose only"},
      {"id":"C02","clause":"Every index Status leading token is in the closed set.","status":"CONFIRMED","file:line":"tests/test_docs_freshness.py:247-258","binding":"test_decision_index_status_vocabulary_is_closed"},
      {"id":"C03","clause":"Open rows match the regex and the named task carries the D-id dependency.","status":"DIVERGES","file:line":"tests/test_docs_freshness.py:260-294; state_kernel.json:4432-4452,5338-5346","binding":"test_open_decisions_name_an_installing_kernel_task; weak, F2"},
      {"id":"C04","clause":"Decision IDs widen to D-\\d{3}[a-z]?.","status":"CONFIRMED","file:line":"tests/test_docs_freshness.py:237-245","binding":"test_decision_index_matches_decision_bodies"},
      {"id":"C05","clause":"Dependency shape is hard/start/pending with null evidence and required.","status":"CONFIRMED","file:line":"docs/process/state_kernel.json:5338-5346","binding":"TestKernelValidity.test_kernel_validates"},
      {"id":"C06","clause":"S9 mint/window-gating shortlist rows are registered as decision dependencies.","status":"DIVERGES","file:line":"docs/process/state_kernel.json:2215-2224,5338-5346; SHORTLIST.md:16-30","binding":"prose only; F1"},
      {"id":"C07","clause":"D-170 carries all four T26 verdicts by pointer.","status":"CONFIRMED","file:line":"docs/decision_log.md:10472-10529","binding":"prose only"},
      {"id":"C08","clause":"M0 says pending decision dependencies are uninstalled and not selectable.","status":"CONFIRMED","file:line":"docs/agent_playbook.md:56-60","binding":"prose only"},
      {"id":"C09","clause":"Item 1 does not change orchestration.md or the council skill.","status":"CONFIRMED","file:line":"git diff 6075389a..HEAD --name-only","binding":"inspection only"},
      {"id":"C10","clause":"Item 4 uses dated-directory cutoff >= 2026-08-29.","status":"CONFIRMED","file:line":"tests/test_docs_freshness.py:99-111","binding":"test_dated_magistrate_rulings_carry_executed_evidence"},
      {"id":"C11","clause":"Item 4 triggers on Rulings, RULED, and Addendum.","status":"CONFIRMED","file:line":"tests/test_docs_freshness.py:296-301","binding":"test_dated_magistrate_rulings_carry_executed_evidence"},
      {"id":"C12","clause":"Triggered files require Executed evidence with the ruled fence/citation shape.","status":"DIVERGES","file:line":"tests/test_docs_freshness.py:114-134","binding":"test_dated_magistrate_rulings_carry_executed_evidence; weak, F3"},
      {"id":"C13","clause":"D-160 R-5 is amended additively by D-170, not rewritten in place.","status":"CONFIRMED","file:line":"docs/decision_log.md:10344-10351,10472-10529","binding":"prose only"},
      {"id":"C14","clause":"Charter §4 remains unchanged with the required digest.","status":"CONFIRMED","file:line":"docs/process/coldgate_charter.md:1","binding":"shasum and diff inspection"},
      {"id":"C15","clause":"Consult brief has the Executed: block and artifact-pair wording.","status":"MISSING","file:line":"README.md:13-16; docs/decision_log.md:10540-10543","binding":"prose only; external scratchpad"},
      {"id":"C16","clause":"Q1 lives in bridge §1 after ACCEPTANCE/VERIFICATION.","status":"CONFIRMED","file:line":"docs/contracts/bridge_protocol.md:48-73","binding":"test_bridge_protocol_clause_map_pins_s1_and_s2; placement inspection"},
      {"id":"C17","clause":"Bridge §10 has the Q1 inventory row.","status":"CONFIRMED","file:line":"docs/contracts/bridge_protocol.md:818-823","binding":"prose only"},
      {"id":"C18","clause":"Q1 has an M0 pointer.","status":"CONFIRMED","file:line":"docs/agent_playbook.md:60","binding":"prose only"},
      {"id":"C19","clause":"S1 mandates Clause map for dated custodied *-impl.md reports.","status":"CONFIRMED","file:line":"tests/test_docs_freshness.py:313-341","binding":"test_custodied_impl_reports_carry_clause_map"},
      {"id":"C20","clause":"S2 text requires independent contract-lens enumeration.","status":"CONFIRMED","file:line":"docs/contracts/bridge_protocol.md:67-73","binding":"test_bridge_protocol_clause_map_pins_s1_and_s2; partial"},
      {"id":"C21","clause":"Q2 is an additive D-160 amendment with full JSON pointer and observed values.","status":"CONFIRMED","file:line":"docs/decision_log.md:10351; MAGISTRATE-RULING-process-rules.md:101-115,127-149","binding":"prose only"},
      {"id":"C22","clause":"T26 and process-rules custody READMEs are present.","status":"CONFIRMED","file:line":"process-proposals/README.md:1-16; 2026-09-02-process-rules/README.md:1-10","binding":"inspection only"}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"suite",
      "cmd":"python3 -m unittest tests.test_docs_freshness tests.test_gen_state",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 52 tests in 1.401s","","OK"]},
      "expected":{"exit_code":0,"tail_regex":"Ran 52 tests .*\\n\\nOK"}
    },
    {
      "id":"V2",
      "kind":"inspection",
      "cmd":"python3 scripts/gen_state.py --check",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    },
    {
      "id":"V3",
      "kind":"inspection",
      "cmd":"shasum -a 256 docs/process/coldgate_charter.md",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md"]},
      "expected":{"exit_code":0,"tail_regex":"^099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81"}
    }
  ],
  "flags": [
    {"id":"G1","kind":"verification_gap","level":"nonblocking","text":"The consult-brief template is external scratchpad state, not a tracked repository artifact.","needs":"Verify the external template before the next applicable seat."}
  ]
}
```

## Independent clause list

The JSON `verdict.clause_table` records the independent C01–C22 propositions first established before diff/report inspection.

## Findings

- F1 blocker: required S9 mint/window registrations are absent from `state_kernel.json`.

- F2 should-fix: the open-status test checks for a dependency somewhere in the kernel, not on the named installing task; it also exempts D-016.

- F3 should-fix: the executed-evidence regex accepts `$ echo exit` as both required lines.

- F4 nit: the consult-brief template requirement is only recorded as external scratchpad prose.

## Residual risk

The S1 clause-map test currently has no eligible `*-impl.md` report dated 2026-09-03 or later, so its prospective path has not yet executed against a real report.