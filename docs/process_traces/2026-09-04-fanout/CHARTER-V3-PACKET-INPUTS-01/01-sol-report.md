```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Charter v3 is drafted and digest-bound with a tracked evidence brief, while activation remains blocked on Ed's re-ratification.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-CHARTER-V3-PACKET-INPUTS-01"
  },
  "pathspec": [
    "docs/process/coldgate_charter_registry.md",
    "docs/process/coldgate_charter_v3_candidate.md",
    "docs/process/coldgate_consult_brief_template.md",
    "docs/process_traces/2026-09-04-fanout/CHARTER-V3-PACKET-INPUTS-01/01-sol-report.md",
    "tests/test_coldgate_charter_v3.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_coldgate_charter_v3 tests.test_docs_freshness.DocsFreshnessTests.test_dated_magistrate_rulings_carry_executed_evidence tests.test_docs_freshness.DocsFreshnessTests.test_bridge_protocol_clause_map_pins_s1_and_s2",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "shasum -a 256 docs/process/coldgate_charter_v3_candidate.md docs/process/coldgate_charter.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "9275316e46c6c7bf084e35caa927dae9727dd544dae72656bed22ba82d22b977  docs/process/coldgate_charter_v3_candidate.md",
          "099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^9275316e46c6c7bf084e35caa927dae9727dd544dae72656bed22ba82d22b977  docs/process/coldgate_charter_v3_candidate[.]md\\n099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter[.]md$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
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
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --untracked-files=all",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/process/coldgate_charter_registry.md",
          "?? docs/process/coldgate_charter_v3_candidate.md",
          "?? docs/process/coldgate_consult_brief_template.md",
          "?? docs/process_traces/2026-09-04-fanout/CHARTER-V3-PACKET-INPUTS-01/01-sol-report.md",
          "?? tests/test_coldgate_charter_v3.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "coldgate_charter_registry[.]md[\\s\\S]*01-sol-report[.]md[\\s\\S]*test_coldgate_charter_v3[.]py$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: the charter candidate cannot become operative until Ed re-ratifies its exact SHA-256-bound bytes.",
      "needs": "Ed chooses: approve candidate 9275316e46c6c7bf084e35caa927dae9727dd544dae72656bed22ba82d22b977, or return exact wording changes for a new candidate and digest. Recommendation: approve the candidate if the REFUSE-with-merits-unruled wording correctly preserves the charter's closed verdict vocabulary."
    }
  ]
}
```

## Change

The desk-completable portion is implemented. The v3 candidate adds D-170's
packet-input requirement to the current v2 text without changing any other v2
bytes. The operative v2 charter remains available and ratified while the
registry records the candidate SHA-256, status, authority, tracked brief, and
promotion procedure. SHA-256 is the cryptographic digest used here to identify
exact file bytes.

The repository-owned consult brief now has an `Executed:` field. It requires
the execution record or refusal-site proof that D-170 names, and it also
provides the artifact-pair exhibit required by the later D-160 amendment. An
artifact-pair exhibit records two artifacts at one revision, the exact JSON
field address, and both observed values.

### Scoped design

**Forcing problem.** D-170 records two occasions when a ruling claimed what an
evidence-production path would do without an execution record. The current
charter tells a seat to read listed inputs but does not require the evidence
that would make such a premise decidable. The only consult-brief requirement
was in an untracked scratchpad.

| Decision | Options considered | Recommendation and landed desk state |
| --- | --- | --- |
| Charter lifecycle | Replace operative v2 immediately; keep the amendment only in a template; create a separate, digest-bound v3 candidate | Use the separate candidate. It makes the revision reviewable without presenting unratified bytes as operative. |
| Rule placement | Add a general evidence principle; add the requirement beside the packet input list in charter section 4 | Place it beside the list. The seat encounters the requirement at the point where it decides what it may read. |
| Missing-evidence result | Add a new verdict named `UNRULED`; use the existing `REFUSE` verdict and state that the merits remain unrulled | Preserve the closed AFFIRM, REJECT, and REFUSE vocabulary. The candidate says to REFUSE for a packet defect and leave the merits unrulled. Ed's ratification of the exact bytes is the final ruling on this wording. |
| Tracked brief home | Add more text to the bridge contract; rely on the charter alone; create a process template | Use a process template because it is the reusable input form for a cold gate and does not alter the bridge protocol. |

**Worked example.** Suppose a packet asks whether a generator produces a
named receipt. Its listed inputs must contain either an execution record with
the exact command and arguments, revision, exit code, and produced-or-absent
path, or a proof naming the source line where generation refuses. If the
packet contains neither, the seat returns REFUSE for that question without
deciding whether the receipt would have been produced.

### Finding and decision table

| ID | Finding or decision | Evidence | Disposition |
| --- | --- | --- | --- |
| D1 | The candidate contains one amendment and is otherwise byte-for-byte v2. | Candidate lines 49-64; `test_candidate_is_current_charter_plus_ruled_packet_input_amendment` | Implemented; deleting the amendment is an in-memory counterfactual that the test rejects. |
| D2 | Candidate identity is recorded without displacing operative v2. | Registry lines 21-37; digest command V2 | Implemented; replacing the candidate digest with a stale value is an in-memory counterfactual that the test rejects. |
| D3 | The consult brief has a tracked `Executed:` home for all ruled evidence forms. | Brief lines 24-52; `test_tracked_brief_requires_each_ruled_evidence_shape` | Implemented; deleting the produced-or-absent field is an in-memory counterfactual that the test rejects. |
| F1 | Activation requires authority this agent does not hold. | State-kernel acceptance and D-170 charter-v3 deferral | NEEDS_RULING from Ed on the exact candidate bytes. |

### Clause map

| Ruling quote | Production site | Biting assertion | Counterfactual |
| --- | --- | --- | --- |
| execution record or code-path proof as a listed packet input | `docs/process/coldgate_charter_v3_candidate.md:49` | `tests/test_coldgate_charter_v3.py:72` | Remove the packet-input amendment; the one-amendment assertion fails. |
| charter digest is computed and recorded | `docs/process/coldgate_charter_registry.md:21` | `tests/test_coldgate_charter_v3.py:80` | Replace the candidate digest with stale bytes; the registry-binding assertion fails. |
| consult-brief `Executed:` requirement has a tracked home | `docs/process/coldgate_consult_brief_template.md:24` | `tests/test_coldgate_charter_v3.py:88` | Remove a required execution-record field; the brief-shape assertion fails. |

## Verification notes

The repository-wide suite was not run, as required by the preflight rule.
Only the new module and the two directly related documentation guards were
run. The first focused run exposed line-wrapping assumptions in two new tests;
the assertions were corrected to compare normalized prose while retaining the
byte-for-byte v2 check, and the final focused run passed as V1 records.

## Residual risk

NEEDS_RULING: Ed must either approve the exact candidate digest recorded in F1
or request exact wording changes. On approval, the lead must record the
ratification, promote the candidate bytes to the operative charter path,
verify the digest did not change, update the registry's operative row, and
move v2 to registry history. Do not use the candidate in a cold gate before
that atomic promotion.

The magistrate-owned state kernel, queue, run state, decision log, and paper
skeleton were intentionally not edited. After ratification and promotion, the
magistrate can mark the kernel row complete using this report, the final
digest check, and Ed's recorded approval as evidence.
