```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The refreshed mission delta is LANDABLE; all required scope and counterfactual checks pass, with one should-fix in the byte-equivalence regression.",
  "workspace": {
    "base_requested": "b15132d91a0018933300c102728a5542754bb201",
    "base_mode": "exact",
    "head_start": "b15132d91a0018933300c102728a5542754bb201",
    "head_end": "b15132d91a0018933300c102728a5542754bb201",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-CHARTER-V3-PACKET-INPUTS-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/CHARTER-V3-PACKET-INPUTS-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "location": "tests/test_coldgate_charter_v3.py:33",
        "text": "The helper claims byte-for-byte equality but compares strings loaded with Path.read_text(), which normalizes line endings. A CRLF-converted v3 candidate with its registry digest updated still passes all three new tests. Compare bytes (or open with newline='') so the asserted invariant is mechanically true.",
        "counterfactual": "Convert the candidate's 161 LF line endings to CRLF and update the registry to the resulting SHA-256 06fcd1452ca4930844905a5befff99dd87c9e776c337e0cf278f14842ee0dcaa; the three-test module reports OK although the candidate is no longer byte-for-byte v2 outside the amendment."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_coldgate_charter_v3 tests.test_docs_freshness.DocsFreshnessTests.test_dated_magistrate_rulings_carry_executed_evidence tests.test_docs_freshness.DocsFreshnessTests.test_bridge_protocol_clause_map_pins_s1_and_s2",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 5 tests in 0.064s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 5 tests.*\\n\\nOK$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --name-only \"$base\"..HEAD; git diff --name-only \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["docs/process/coldgate_charter_registry.md", "docs/process/coldgate_charter_v3_candidate.md", "docs/process/coldgate_consult_brief_template.md", "docs/process_traces/2026-09-04-fanout/CHARTER-V3-PACKET-INPUTS-01/01-sol-report.md", "tests/test_coldgate_charter_v3.py"]},
      "expected": {"exit_code": 0, "tail_regex": "tests/test_coldgate_charter_v3[.]py\\n?$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "cd /private/tmp/jw-charter-v3-refuter.2RO7ju/mut_candidate && python3 -m unittest -v tests.test_coldgate_charter_v3.ColdgateCharterV3Tests.test_candidate_is_current_charter_plus_ruled_packet_input_amendment",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED [(]failures=1[)]$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "cd /private/tmp/jw-charter-v3-refuter.2RO7ju/mut_registry && python3 -m unittest -v tests.test_coldgate_charter_v3.ColdgateCharterV3Tests.test_registry_binds_candidate_digest_without_displacing_v2",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED [(]failures=1[)]$"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "cd /private/tmp/jw-charter-v3-refuter.2RO7ju/mut_brief && python3 -m unittest -v tests.test_coldgate_charter_v3.ColdgateCharterV3Tests.test_tracked_brief_requires_each_ruled_evidence_shape",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED [(]failures=1[)]$"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "cd /private/tmp/jw-charter-v3-refuter.2RO7ju/mut_crlf && python3 -m unittest -v tests.test_coldgate_charter_v3",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["Ran 3 tests in 0.002s", "OK"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "shasum -a 256 docs/process/coldgate_charter_v3_candidate.md docs/process/coldgate_charter.md && git diff --check $(git merge-base origin/main HEAD)..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["9275316e46c6c7bf084e35caa927dae9727dd544dae72656bed22ba82d22b977  docs/process/coldgate_charter_v3_candidate.md", "099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md"]},
      "expected": {"exit_code": 0, "tail_regex": "099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter[.]md$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The candidate remains explicitly non-operative after landing until Ed re-ratifies the exact recorded bytes and the lead performs the registry promotion procedure.",
      "needs": "Send digest 9275316e46c6c7bf084e35caa927dae9727dd544dae72656bed22ba82d22b977 to Ed for the already-ruled re-ratification step."
    }
  ]
}
```

## Findings

F1 — should_fix — `tests/test_coldgate_charter_v3.py:33`: the claimed
byte-for-byte invariant is implemented with universal-newline text reads. In
an isolated copy, converting all 161 candidate newlines to CRLF and updating
the registry digest left the whole new test module green. The current LF bytes
and recorded digest are correct, so this is regression hardening rather than a
landing blocker.

## Evidence

The mission-only range was `b0ed6991c11f3a515ad293760c6dfc031adda8e1..b15132d9`.
Its five paths exactly match the implementer's declared pathspec. `RUN_STATE.md`,
`TASK_QUEUE.md`, `docs/process/state_kernel.json`, and
`docs/decision_log.md` have no delta. The exact five claimed tests passed.

Production-file counterfactuals were exercised in isolated copies:

| Behaviour | Counterfactual input | Result |
|---|---|---|
| v3 is v2 plus the ruled amendment | Remove the complete packet-input amendment | Candidate test failed: amendment count 0 |
| registry binds the candidate bytes | Replace the candidate digest with 64 zeroes | Registry test failed |
| tracked brief requires the execution-record shape | Rename `Produced-or-absent artifact path` to generic `Artifact path` | Brief test failed |

No previous refuter report exists in the mission directory or reachable or
unreachable commit history, so there is no prior non-staleness blocker of
record. The plausible false-counterfactual concern was nevertheless re-tested
with real temp-copy mutations above. No CLI identity or occupied-root behaviour
exists in this delta. Candidate identity is not trusted as mutable prose: V7
recomputed its digest from the actual bytes, and V4 proved a stale digest bites.

## Residual risk

Landing does not activate v3. Ed's exact-byte re-ratification and the lead-owned
atomic promotion remain required by the magistrate ruling and registry fence.
