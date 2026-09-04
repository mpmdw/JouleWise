```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Corrected the authorized documentation and publication surfaces; README.md and PROJECT_STATUS.md still require expanded write scope.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-docs-vs-truth"
  },
  "pathspec": [
    "docs/agent_playbook.md",
    "docs/council_log.md",
    "docs/guides/instrument-guide.md",
    "docs/guides/tutorial-run-a-window.md",
    "docs/milestones.md",
    "docs/orchestration.md",
    "docs/process_traces/2026-09-02-paper-d-dg071/41-coldgate-opus-refutation-fixture-shape.md",
    "docs/process_traces/2026-09-02-paper-d-dg071/MAGISTRATE-NOTES.md",
    "docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md",
    "docs/process_traces/2026-09-02-t26-item-3/MAGISTRATE-NOTES.md",
    "docs/process_traces/2026-09-04-fanout/docs-vs-truth/01-sol-report.md",
    "docs/publication_release_checklist.md",
    "docs/risk_register.md",
    "docs/run_reports/README.md",
    "docs/site_src/index.html",
    "docs/site_src/research.html",
    "docs/site_src/results.html",
    "scripts/build_site.py",
    "tests/test_build_site_parsers.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 23 tests in 0.883s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 23 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "JOULEWISE_SITE_CONTENT_TESTS=1 python3 -m unittest tests.test_build_site_parsers",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["SiteBuildError: Completed Queue Items: TASK_QUEUE.md: expected 5 table cells per row", "Ran 27 tests in 5.264s", "FAILED (errors=1, skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 27 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "JOULEWISE_SITE_CONTENT_TESTS=1 python3 -m unittest tests.test_build_site_parsers.BuildSiteParserTests.test_claim_surfaces_do_not_render_d078_voided_values",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.001s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
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
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "sed -n '2,/^```$/p' docs/process_traces/2026-09-04-fanout/docs-vs-truth/01-sol-report.md | sed '$d' | python3 -m json.tool >/dev/null",
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
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "README.md and PROJECT_STATUS.md are named mission targets but are excluded by the exhaustive runner-owned write scope.",
      "needs": "Resume with README.md and PROJECT_STATUS.md added to WRITE_SCOPE, or accept the authorized partial implementation."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The touched site test module reaches a pre-existing parse failure in the prohibited TASK_QUEUE.md before the production renderer runs; the new D-078 claim-surface test passes in isolation.",
      "needs": "The magistrate may repair or adjudicate the TASK_QUEUE.md five-cell table and rerun the site module."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["README.md", "PROJECT_STATUS.md"],
    "reason": "Audit items B4 and A6 remain true on origin/main, and both files are explicitly requested by the mission but omitted from the authoritative allowlist.",
    "blocked_work": "Retense the README site-lane instruction to D-136 and replace the project-status next-machine-step paragraph with the current unattended-first sequence.",
    "minimal_change": "Edit only the stale paragraphs in those two root files; preserve README's existing D-078 fences."
  }
}
```

## Change

The audit was re-evaluated against `origin/main` at
`849915bc1393a6c1cb962a4dc12b25c33dad1f74`. The table quotes the stale text,
the authority used to judge it, and the replacement now installed.

| Finding and file | Stale sentence | Truth source | New sentence |
|---|---|---|---|
| B5 — publication checklist | “regenerate the capstone artifacts from all six retained strict-valid bundles” | D-078 permanently bars energy claims from the defective-anchor corpus; D-167 makes the `_v5` transaction prospective. | “Output from the `rpt001` profile demonstrates only that the report-building path runs; it must be labelled `plumbing evidence only` and must never supply a paper, abstract, figure, comparison, or detection-floor claim.” |
| B4 — publication checklist | “Ed alone handles generated-site regeneration and deployment.” | D-136 retires the site lane from automatic and agent processes. | “Manual-dispatch reference, not a session step. … If Ed chooses the manual workflow dispatch, Ed alone handles generated-site regeneration and deployment.” |
| B6/A10 — milestones and run-report guide | “Status: skeleton - real dates pending user input”; “Read the latest report in this directory.” | The state kernel owns readiness; `RUN_STATE.md` T31 owns the current sequence and uses dated blocks plus process traces as session records; `P1-008` still owns unknown external dates. | “Status: live sequence, with unresolved external dates named explicitly”; “Follow the latest session-record pointer in `RUN_STATE.md`.” The live sequence is supervisor and plan pin, G2-a diagnostic probe, desk day, shakedown, transaction, collection, issue, and write. |
| B7 — agent playbook | “ungated, any time: M1 (Slice 2N)”; handoff to absent `docs/phase_2/baseline_results.md` | Completed queue history, D-164 through D-167, and the current state-kernel rows supersede the old mission menu. | “Live work is selected only from `RUN_STATE.md` and the state kernel”; M1–M10 are marked historical, and the dead file is explicitly not a current destination. |
| B8 — orchestration | “Topology: how it evolved” was the only topology description. | D-080, D-087, D-088, D-119, and D-121 define the current separation of authority. | A current rule-11 section defines the magistrate, lieutenant, and cold gate; the old topology is labelled historical. |
| B4 — orchestration | “Sessions that change front-facing state refresh `docs/site/DRIFT.md`.” | D-136. | “D-136 retires the site lane from routine sessions: agents do not refresh, regenerate, or deploy it.” |
| B9 — risk R-001 | “all work since has been hardware-independent … Slice 2N is next” | Live Mac evidence exists; the state kernel and `P1-008` show that advisor scope is the unresolved external risk. | “The live uncertainty is no longer whether Slice 2N may start; it is whether the `_v5` campaign and planned paper answer the advisor's required scope.” |
| B9 — risk R-012 | The ladder began “Drop live split” and “Drop 10GbE and one model size.” | D-165 owns withdrawal of the timing-dominance sentence; D-166 owns refusal of an unsupported prefill arm. | The ladder now refuses an unsupported prefill arm, withdraws a failed dominance sentence, and defers extension work before weakening the admitted Mac evidence chain. |
| B9 — risks R-016/R-017 | One row sanctioned iCloud backup while the next said “never under iCloud.” | The existing restoration receipt concerns a backup copy; R-017 concerns the active checkout and corpus. | “This is a sanctioned backup copy outside the repository”; the live checkout and active corpus remain local and unsynchronized. |
| B9 — new risk rows | No row covered unattended failure or missing paper dates. | D-169 and D-171 govern the unattended lane; kernel task `P1-008` owns evaluator dates. | R-021 records unattended-night failure and refusal; R-022 records the open paper-calendar risk without inventing a date. |
| Guide — instrument status | “three changes in the current checkout”; “The three current successor packs each pin `freeze-0003.json`.” | D-164 through D-167 retire the Qwen2.5 packs and install a prospective Qwen3 `_v5` campaign; current readiness is in `RUN_STATE.md` and the state kernel. | The dated Qwen2.5 account is historical; predecessor receipts do not make `_v5` packs ready, and `_v5` must prove its own frozen lifecycle. |
| Guide — prefill floor | “The plan requires a 256-token prefill floor dependency.” | D-166 makes prompt length a G2-a output; no `_v5` transaction or issued floor exists. | “D-166 makes the live `_v5` prefill length an output of the G2-a diagnostic selection.” |
| Tutorial | “In this checkout, quiet-machine collection is blocked.” | That volatile assertion belongs to `RUN_STATE.md`, the state kernel, and the current operator card. | “This tutorial grants no permission to arm … or sample”; readers must consult the live authorities. |
| Site index | “6/6 bundles passed strict validation … the floors are usable for later adjudication.” | D-078 distinguishes structural validation from physical soundness and voids the energy values. | “Strict validation does not repair a defective physical time anchor”; no predecessor energy value is claim-bearing. |
| Site research page | “The verified Window-A extraction reports the following false-effect guard floors.” | D-078. | “No current numeric floor is displayed”; the old extraction is instrument evidence only and `_v5` must issue new floors. |
| Site results page | “The first live Mac observations” followed by energy values and “Verified Window-A floor extraction.” | D-078 and the uncollected D-167 transaction. | “The files remain evidence; their energy values do not”; the page reports no claim-bearing energy or floor value. |
| Site renderer and test | Learning and measurement pages parsed and substituted `FLOOR_*` tokens from the voided extraction. | D-078's fence must hold at the generated claim surface, not only in prose. | The three claim pages no longer accept floor substitutions or cite that extraction as current provenance; a focused regression test rejects the retired heading, tokens, and values. |
| C3 — T26 note | “NOT YET APPLIED to the bench texts.” | PR #273 landed the installation. | “APPLIED to the bench texts by the T26 install merged in PR #273.” |
| C3 — paper-D note | “after `feat/2026-09-02-dx-registry` merges” | The branch merged; registry rows DG-071/DG-075 remain `VALUE_UNISSUED` / `STOP_FILL`. | “Artifact issuance is due rather than deferred behind that merge.” |
| C3 — process ruling | “Both rules install via the in-flight T26 install branch.” | PR #273 merged and the former installing row is retired. | “Both rules are installed,” followed by the installed sites. |
| C5 — fixture trace | Bare `fb601e54…` appeared to be a project commit. | The audit's throwaway-repository experiment produced it; it is absent from JouleWise history. | The reference is labelled “a throwaway-repository experiment SHA rather than a JouleWise commit.” |
| C6 — council log | The last session block was T29. | The three T30 cold-gate trace directories contain the adjudications. | A T30 block records numeric rendering, unavailable-corpus wording, and process-rule outcomes, with each term defined. |

Audit items B1–B3 were already corrected on `origin/main`. B10 is not still
true: “A” is the grammatical article for the next line's “machine-readable
record,” not an orphan fragment. C4's acceptance-predicate addendum is already
present. Kernel, queue, run-state, decision-log, and paper-skeleton findings
were left for their named owners as instructed.

Two corrections remain blocked by the allowlist:

| File | Stale sentence | Truth source | Proposed new sentence |
|---|---|---|---|
| `README.md` (B4) | “sessions that change front-facing state refresh `docs/site/DRIFT.md`, and Ed deploys manually (D-068)” | D-136 | “The site lane is retired from routine sessions under D-136; regeneration and deployment occur only through Ed's manual workflow dispatch.” |
| `PROJECT_STATUS.md` (A6) | “Next machine step: one instrumented evening, waiting on Ed.” | `RUN_STATE.md` T31; D-169 and D-171 | “The unattended supervisor and pinned night plan precede G2-a; the diagnostic probe, desk-day freeze, shakedown, and transaction proceed only as their state-kernel gates open.” |

## Verification notes

The required freshness test first failed because orchestration said “Ed
regenerates and deploys,” while its established guard requires the literal
phrase “Ed deploys.” The sentence was corrected without weakening D-136, and
the rerun passed.

The site module's single error occurs while parsing the prohibited,
lead-owned `TASK_QUEUE.md`: its completed-items table contains a row that does
not have the expected five cells. The failure precedes the changed renderer.
The newly added D-078 regression test passes independently. The repository-wide
suite was not run, as required by preflight.

## Residual risk

Until the root-file scope is expanded, README still instructs routine sessions
to refresh a retired site lane, and project status still names an obsolete next
machine step. No generated site was built or deployed; only its source and
renderer were corrected.
