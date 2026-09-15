```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Three findings: premature work selection, omitted directive propositions, and an inaccurate refusal history; focused checks pass.",
  "workspace": {
    "base_requested": "6d2d62d8",
    "base_mode": "exact",
    "head_start": "8afd6adecc1f13cc8afd51605c8eb4a491fbf47e",
    "head_end": "8afd6adecc1f13cc8afd51605c8eb4a491fbf47e",
    "upstream_end": "6d2d62d8d1820fb9d71bb7550705aab5eeac1a05",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [".venv"],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "docs/process/state_kernel.json",
        "line": 2990,
        "summary": "The first promoted task is selectable before the owner's start condition is satisfied.",
        "evidence": "Record 55:13 orders promotion immediately after the night's harvest and §2.5 outcome action. RUN_STATE.md:15 still records the night as armed. INSTALL-WINDOWS-MULTI-01 has dependencies=[], status=queued and rank=0; its status_note at line 3001 defers work in prose. scripts/gen_state.py:496-523 ignores status_note and actually selects this task; the queue renders READY. The changed tests pin that premature selection.",
        "proposed_closure_shape": "Retain rank 0 but add a pending hard dependency of kind event and scope start covering BOTH the 09-15 harvest and its §2.5 outcome action; set status=blocked. Release it with completion evidence and restore queued status during bookkeeping. AUD-WO-033 demonstrates event syntax, but its scope=close would not enforce this start condition. Update head assertions to distinguish pending and satisfied states, then regenerate. An in-memory validation confirmed this shape blocks selection until satisfaction."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "docs/decision_log.md",
        "line": 11809,
        "summary": "The entry drops substantive implementation and housekeeping instructions from record 55.",
        "evidence": "Record 55:13 explicitly specifies install spans as a list and a dead-man per span, recording through the normal PR gate, and no self-amendment of rule text outside that PR. D-181 names the lanes and says 'through this PR' but does not carry those explicit qualifications. Record 55:25 also states PR #330 had 170 kernel rows and passing tests; lines 11833-11835 omit that historical evidence. Record 55:27 requires commenting each ruling's outcome on the issue and closing it when all three are recorded; this is absent.",
        "proposed_closure_shape": "Restore these propositions using the owner's wording. Identify 170 rows/tests OK as historical PR #330 evidence, not the current kernel count. Preserve the issue-comment and closure instructions as obligations, without claiming they have been performed."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "file": "docs/decision_log.md",
        "line": 11794,
        "summary": "The forcing-problem paragraph conflates a t0 refusal with an arm-time refusal.",
        "evidence": "Lines 11794-11796 attribute both the September 13 refusal and September 14 morning non-arm to the arm-time census. RUN_STATE.md:25 (T38p) records the September 13 night firing and refusing at its t0 census. Line 23 (T38q third addendum) records the September 14 arm-time census never clearing. Line 15 (T38r) additionally records the owner-authorized evening installation, qualifying the assertion that the next calendar night was the only recovery mechanism.",
        "proposed_closure_shape": "Distinguish the September 13 t0 refusal from the September 14 morning arm-time non-arm. Describe next-night recovery as the ordinary documented path before directive #336's one-night exception. Keep this factual context free of new rules."
      }
    ],
    "proposition_map": {
      "notation": "Entry line references are in docs/decision_log.md. Source references are lines in record 55.",
      "preamble": [
        "Source 7: standing ruling after #336 and for subsequent windows — CARRIED at 11791-11793 and the general window rule at 11798-11806."
      ],
      "ruling_1": [
        "Source 11: machine serves science; windows run as quickly as scientifically sound — CARRIED in substance by 11798-11806: immediate clean-census windows subject to all soundness gates.",
        "Source 11: clean census, day or night, several windows daily if gates pass — CARRIED at 11798-11799.",
        "Source 11: no artificial spacing, one-in-three cadence, 02:56 restriction, or minimum gap — CARRIED at 11800-11801.",
        "Source 11: Ed keeps the machine quiet when unused; closes interactive sessions and agent desktop apps on request; notice email suffices — CARRIED at 11801-11803.",
        "Source 11: physics/evidence refusals, preregistration before data, arm and t0 census, twelve-row gate, email-then-arm, and Ed's overriding NO remain unchanged — CARRIED at 11803-11805.",
        "Source 11: no other timing rule — CARRIED at 11805-11806.",
        "Source 13: current single-plan daily launchd minute, 02:45–03:30 belt, single 07:00 dead-man and calendar-day install span are mechanism limits, not scientific requirements — CARRIED at 11806-11808.",
        "Source 13: promote INSTALL-WINDOWS-MULTI-01, then ARM-RETRY-CLASS-01, then ARM-CENSUS-IDLE-INTERACTIVE-01 after harvest and §2.5 action — CARRIED at 11809-11811; kernel timing defect is F1.",
        "Source 13: install spans as a list and dead-man per span — DROPPED from the entry; F2. These remain in the kernel acceptance.",
        "Source 13: arbitrary-clock t0 and second window immediately after previous harvest — CARRIED at 11811-11813.",
        "Source 13: dated decision-log record through a PR as #316 became D-180 — CARRIED at 11783-11789.",
        "Source 13: normal gate and no rule-text self-amendment outside that PR — DROPPED as explicit restrictions; F2."
      ],
      "ruling_2": [
        "Source 17: every merged PR has Fable 5.1 terminal review as its last review; magistrate at pinned model reads final head directly, not delegate summary — CARRIED at 11818-11820.",
        "Source 17: existing row 7 apex Fable code-reading diff gate and row 12 nondelegable final-head terminal review — CARRIED at 11821-11822.",
        "Source 17: retain both rows exactly, never downgrade/delegate, cite final head sha in row 12 for every PR — CARRIED at 11823-11824."
      ],
      "ruling_3": [
        "Source 21: named browser-probe lane needs Ed's desk proof using author_arm_evidence_t0 against a TRANSACTION_PACK root with no browser, agents or caffeinate — CARRIED at 11825-11828.",
        "Source 21: prepare pack root and window-custody root; email exact command and when — CARRIED at 11828-11829.",
        "Source 21: Ed runs at next otherwise-idle moment; this must not delay first G2-a pack window — CARRIED at 11829-11831."
      ],
      "housekeeping": [
        "Source 25: PR #330 conflicts resolved at d80e5e37 and body lacks gate ledger — CARRIED at 11833-11834.",
        "Source 25: historical kernel 170 rows and tests OK — DROPPED; F2.",
        "Source 25: take PR #330 through gate and merge under Fable terminal review — CARRIED at 11834-11835.",
        "Source 27: comment each ruling's outcome on issue; close when all three recorded — DROPPED; F2."
      ],
      "additional_text": [
        "11785-11796: status, recorder and decided-versus-installed boilerplate match D-180's permitted shape. Forcing context adds no rule, but contains F3's factual error.",
        "11813-11814: superseding the three rows' 'after G2-a instrument validation' sequencing is supported by the owner's explicit replacement timing after harvest and §2.5; no independent policy invention.",
        "11814-11817: rank-0 handoff and predecessor dependencies are the permitted queue-mechanism explanation. Future rank transfers still require bookkeeping; dependency edges alone do not promote ranks.",
        "11824: 'No lane: this clause changes no text' restates the instruction to preserve existing review rows; it grants no exemption.",
        "Other lane identifiers, pointers and clause headings add no substantive rule."
      ]
    },
    "placement_and_shape": "PASS: D-179 at 11678, D-180 at 11738, D-181 at 11783, followed by the preserved D-124 dated addendum at 11837. New numbered decisions precede the trailing addendum, preserving existing order. D-181 matches D-180's heading, Status, recorder, forcing context and numbered-clause shape. Clauses 1 and 3 name lanes; clause 2 correctly identifies no implementation lane. No clause claims installation.",
    "kernel_changed_fields": {
      "INSTALL-WINDOWS-MULTI-01": ["acceptance.summary", "authority.label", "authority.path", "goal", "priority", "rank", "status_note"],
      "ARM-RETRY-CLASS-01": ["authority.label", "authority.path", "dependencies", "priority", "status", "status_note"],
      "ARM-CENSUS-IDLE-INTERACTIVE-01": ["authority.label", "authority.path", "dependencies", "priority", "status", "status_note"],
      "ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01": ["status_note"],
      "top_level": ["updated"]
    },
    "kernel_assessment": "No other JSON fields or task IDs changed. All three promoted tasks use p1_phase_gate and D-181 authority pointing to record 55. INSTALL has the unique minimum agent rank 0. RETRY and IDLE retain ranks 172/173, become blocked, and have pending hard start task dependencies targeting INSTALL and RETRY respectively. Status notes preserve existing fences and describe the directive or queue bookkeeping; no new substantive rule was found. The prose-only first-task start condition is a defect, not an accepted encoding.",
    "count_and_tests": "Both kernels contain exactly 174 tasks with identical ID sets. tests/test_gen_state.py changes only the three head-pin sites at 1301, 1353 and 1514, each with a 2026-09-14 comment. EXPECTED_IDS and fixture files are unchanged. RUN_STATE.md and TASK_QUEUE.md edits are confined to generated regions.",
    "coverage": "Read-only contract review; no network or measurement processes. Full suite not run for this documentation/state change; the complete focused state module passed. Record 55's claimed byte identity with GitHub was not independently verified offline."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python3 -m unittest tests.test_gen_state",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 44 tests in 5.873s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 44 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check 6d2d62d8..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```