```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: an empty --render-only argument permits installation; signal restoration gaps and documentation drift remain.",
  "workspace": {
    "base_requested": "ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a",
    "base_mode": "exact",
    "head_start": "ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a",
    "head_end": "ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "NOT LANDABLE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Empty render-only argument silently selects a mutating mode",
        "locations": ["scripts/install_night_agent.sh:20", "scripts/install_night_agent.sh:79", "joulewise/night_agent_install.py:660"],
        "evidence": "Scratch probes: --render-only \"\" returned 0 and loaded both fixture labels; --uninstall --render-only \"\" returned 0 after two bootouts and two prints.",
        "remedy": "Reject an empty render directory before reconstructing argv, preserve option presence, and test both cases for zero launchctl calls."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "F3 cure does not guarantee restoration across signal-entry boundaries",
        "locations": ["joulewise/night_agent_install.py:334", "joulewise/night_agent_install.py:353", "joulewise/night_agent_install.py:412", "joulewise/night_agent_install.py:494"],
        "evidence": "Real SIGTERM injected immediately before uninstall's mask or _unwind's mask escaped as Signalled and left INT/TERM/HUP blocked. An early refusal also restored a stale construction-time mask.",
        "remedy": "Make signal setup, teardown entry and restoration exception-safe; capture the invocation's mask before validation; add boundary and early-refusal regressions."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Shipped documentation still misstates timing and successful cleanup",
        "locations": ["docs/process/NIGHT_HANDBACK.md:204", "docs/phase_2/derivation_night_runbook.md:1438", "joulewise/night_agent_install.py:379", "joulewise/night_agent_install.py:464"],
        "evidence": "Handback promises immediate pre-bootstrap close checks that no longer exist. The committed outcome promises sidecar removal, although cleanup failure warns and still returns 0.",
        "remedy": "Describe the single post-verification commit gate and document best-effort sidecar cleanup with its exact warning."
      }
    ],
    "clause_map": {
      "D1": "Implemented in substance: stdlib engine; lazy install imports at night_agent_install.py:585,625; interpreter check precedes module exec at install_night_agent.sh:52,91. Shell additionally selects the interpreter and normalizes paths.",
      "D2": "Implemented: night_agent_install.py:227-237 requires rc 113 plus the exact whole stderr line for ABSENT; rc 0 is LOADED; other results are UNKNOWN.",
      "D3": "Implemented with the previously recorded publication refinement: proof validation at :148-162 protects removal/restoration; atomic publication at :243-260 is separate. Proofs bind target, label and mutation generation.",
      "D4": "Implemented as the recorded channel refinement, not literally 'nothing else touches launch_dir': adapter mutators are at :243,262,268; Target owns staging, restoration and sidecars at :136-186.",
      "D5": "State, snapshot, atomic publication, pre-invocation recording and commit ordering hold at :306-319,136-175,434-464. Both plists precede bootstrap; successful installation has no bootout. Sidecars support in-process rollback and manual recovery, not automatic post-exit journal replay.",
      "D6": "State dispatch, retention and restore-error handling hold at :374-409, but whole-unwind signal protection/restoration is incomplete: F2.",
      "D7": "Module uninstall and NullAdapter protections hold at :273-300,488-515,655-667. Shell entry violates render-only isolation and mutual exclusion for an empty argument: F1.",
      "D8": "Implemented: schedule constants remain owned by run_night.py:68-69,967-970; engine consumes schedule at :625-630. Label parameterization is at :93-109; one-label recovery is tested at test_night_agent_install.py:1249. No duration ceiling added.",
      "D9": "Retention messages, conditional recovery, sidecar explanation and courier stop rule are present. Migration remains incomplete because of F3.",
      "D10": "Three-valued fake, Cartesian census, shared tuple/fence assertion and FIX mapping exist at test_night_agent_install.py:24,329,357,635. Retained-prior regression is present at :931. Focused modules pass, but omit F1/F2 cases; full replay and mutation closure were not independently rerun."
    },
    "zero_exit_derivation": "Exactly two CLI success routes. Transaction.result starts at 1 (:332); internal refusals/errors assign nonzero codes (:473-481); only COMMITTED teardown assigns 0 (:377-382), after the sole commit predicate (:422-427). Uninstall returns 0 only after both absence proofs and file cleanup (:497-506). main merely forwards these results (:671-675); argparse errors exit 2 (:641-645). Render-only shares COMMITTED. Adapter Outcome(rc=0) is not a process exit.",
    "signal_path_answer": "Normal early refusal, post-handler refusal, COMMITTED, ROLLED_BACK, RETAINED, restore failure, committed cleanup failure, signal rollback, and uninstall 0/4/1 all restored masks and dispositions in the scratch probe. Nevertheless F2 establishes reachable leaks for in-process callers. A shell exec terminates that Python process on the uncaught exception; it receives a failure rather than the documented outcome.",
    "last_two_commits": "0ba6ce54 changes guards and test oracles without a found clock/deletion regression. ccce8a61 correctly fixes the ordinary handler-to-unwind case, but its handler-side blocking makes the remaining escape windows leak blocked masks. I1/I2/I3/I5 remain supported by source inspection; I4 fails through F1, an inherited shell defect retained by this redesign.",
    "docs_audit": "Grep-checked all documented installer diagnostic fragments against the engine, shell and delegated schedule/plan validators. Listed refusal codes, retained lines, bootstrap/verification messages and ordinary outcome codes match. Obsolete installer 'rolled back' messages are gone. Exceptions are F3; the runbook's recovery commands correctly require uninstall exit 0.",
    "readability": "No material dead or overbuilt mechanism found: typed outcomes, proof binding and target marker types enforce useful boundaries. For reproduction from docs alone, also state the exact rc-113/stderr-line ABSENT predicate at runbook:1385 rather than only saying the query establishes absence.",
    "next_step": "Lead fixes F1, adjudicates F2/F3, then obtains focused regressions and final-head replay/review. No repository files were modified; experiments reside only in the designated scratch copy."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/row10-copy",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 37 tests in 617.276s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_install_night_agent",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/row10-copy",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 47 tests in 59.783s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/row10-copy",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 101 tests in 20.963s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest row10_probe",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/row10-copy",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 6 tests in 2.691s", "OK", "shell --uninstall --render-only \"\": returned 0; two bootouts and two prints"]},
      "expected": {"exit_code": 0, "tail_regex": "two bootouts and two prints"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check 073a9763..ccce8a61",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Full suite, mutation campaign, lt-21 reproduction and live OS signature probe were not rerun. User prohibited full-suite and real launchctl execution. Canonical baseline digest, exact HEAD, index and clean worktree matched.",
      "needs": "Lead retains final replay and live-validation ownership."
    }
  ]
}
```

## Findings

- **F1 — blocker:** A supplied but empty render directory disappears during shell argv reconstruction. The resulting invocation performs a real installation or uninstall through the selected adapter. Both cases were reproduced with fake launchctl.
- **F2 — should-fix:** The ordinary mask restoration works. However, a signal immediately before either entry mask escapes the protected region; the new handler leaves signals blocked. Early refusal can also restore the constructor’s outdated mask.
- **F3 — should-fix:** Replace the handback’s pre-bootstrap-check description and qualify the runbook’s sidecar-cleanup guarantee.

## Residual risk

The 185 supplied tests passed. The six scratch tests deliberately characterize the reported defects; their passing result does not establish contract compliance.