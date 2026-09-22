```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Python matches all 14 fixtures; all six mutations are killed; 94 tests pass; the ruled zsh loop falsely reports retained for three cases.",
  "workspace": {
    "base_requested": "9e0a4995d800cbebda223fb67981664f5f74b207",
    "base_mode": "descendant",
    "head_start": "fc28d7822c5b5eac8f42a3b56634fe86b08465a8",
    "head_end": "fc28d7822c5b5eac8f42a3b56634fe86b08465a8",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 733,
        "summary": "The manual loop accepts directory markers, symlinked markers, and non-regular plan files that retained_roots rejects.",
        "cure": "Amend the ruled manual procedure to use retained_roots or equivalent path guards, and add parity coverage."
      }
    ],
    "python_cases": "14/14 conform",
    "mutations": "6/6 killed",
    "module": "94 tests passed",
    "zsh_disagreements": 3
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/retention-audit-3pdov0/fixtures.py > /tmp/retention-audit-3pdov0/fixtures.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "Q1: 14/14 match ruled classification and path guards",
          "Q4 disagreements: 08-directory-marker, 10-symlink-marker, 14-directory-plan"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Q4 disagreements: $"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/retention-audit-3pdov0/mutations_verified.py > /tmp/retention-audit-3pdov0/mutations_verified.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MUTATION SUMMARY: baseline PASS; 6/6 KILLED; every run selected 4 tests"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MUTATION SUMMARY: baseline PASS; 6/6 KILLED; every run selected 4 tests"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night > /tmp/retention-audit-3pdov0/module.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 94 tests in 272.515s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 94 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/retention-audit-3pdov0/authority.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Q1 exact replacement sentence: MATCH (whitespace normalized)",
          "Q2 ruled zsh loop: BYTE-IDENTICAL (quote prefixes removed)",
          "Q2 replacement paragraph: MATCH (whitespace normalized)",
          "Q3 operative commands and stop rule: MATCH (whitespace normalized)",
          "A263 reproduced: {\"now_minus_t0_s\": 600, \"plan_span_active\": true, \"retained_roots\": \"retained\", \"verdict\": \"pass\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Q2 ruled zsh loop: BYTE-IDENTICAL"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "F1 reproduces a defect in the exact Q2 ruled shell text; the implementation copied that text faithfully.",
      "needs": "Obtain an amendment to the manual procedure and add the parity regression."
    },
    {
      "id": "R2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The bookkeeping remote-tracking ref advanced from 85ddb9ec to 0cd42bd7 during review. The ruling was unchanged; the revised Opus refuter was reread. The reviewed worktree HEAD and clean state remained unchanged.",
      "needs": ""
    }
  ]
}
```

## Findings

**Blocker: none.**

**F1 — should-fix: the manual loop produces three false `retained` lines.** At [derivation_night_runbook.md:733](/Users/edr/code/JouleWise-wt-retention2-29ea94df/docs/phase_2/derivation_night_runbook.md:733), `(N)` permits directory and symlink matches, and the loop never validates the plan’s file type. Python enforces those guards at [evidence_night.py:670](/Users/edr/code/JouleWise-wt-retention2-29ea94df/joulewise/evidence_night.py:670), consistent with [contract item 4:203](/Users/edr/code/JouleWise-wt-retention2-29ea94df/docs/contracts/evidence_night_entry.md:203).

Executed command, with only the loop’s discovery root changed:

```sh
/bin/zsh /private/tmp/retention-audit-3pdov0/runbook.zsh
```

Relevant output, exit 0:

```text
08-directory-marker: retained refusal.json
10-symlink-marker: retained refusal.json
14-directory-plan: retained refusal.json
```

Python returns `UNKNOWN/fail`, raises `Refused: symlink/path collision`, and raises `Refused: retained plan is not a regular non-symlink file`, respectively.

**Cure:** amend Q2’s manual procedure to use the Python classifier or equivalent guards, and pin these cases with a parity test. The tracked Python check already refuses them.

**Nit: none.**

**Q1/Q4 — fourteen executed cases**

Fixtures and full output: [fixtures.py](/tmp/retention-audit-3pdov0/fixtures.py), [fixtures.log](/tmp/retention-audit-3pdov0/fixtures.log). `/tmp` paths were resolved to `/private/tmp` before calling `safe_path`.

| Fixture | Python classification | Verdict | zsh classification |
|---|---|---|---|
| Only `refusal.json` | retained | pass | retained |
| Only `chain.exited` | retained | pass | retained |
| Only `refusal-3.json` | retained | pass | retained |
| Only `calibration-refusal.json.2.json` | retained | pass | retained |
| `chain.started` alone | ACTIVE | fail | ACTIVE |
| Started + calibration refusal | ACTIVE | fail | ACTIVE |
| Started + exited | retained | pass | retained |
| `refusal.json` directory | UNKNOWN | fail | **retained** |
| Plan only, empty `night/` | UNKNOWN | fail | UNKNOWN |
| `refusal.json` symlink to regular file | No classification | Refused | **retained** |
| Only `refusal.json.bak` | UNKNOWN | fail | UNKNOWN |
| Empty `night/` | UNKNOWN | fail | UNKNOWN |
| No `night/` | UNKNOWN | fail | UNKNOWN |
| Plan directory, regular refusal marker | No classification | Refused | **retained** |

No Python result contradicts the ruling. ACTIVE roots retain any terminal-marker evidence found; `chain.started` itself is excluded.

**Q2 — mutation results**

Executed [mutations_verified.py](/tmp/retention-audit-3pdov0/mutations_verified.py) against independent package copies. Each invocation asserted the imported module’s scratch path before loading tests. The filters `-k retained -k discovery` select **four** tests. The unchanged baseline passed.

Every mutation was killed by an assertion in `LifecycleTests.test_retained_root_classification_ruled_cases` ([test_evidence_night.py:760](/Users/edr/code/JouleWise-wt-retention2-29ea94df/tests/test_evidence_night.py:760)):

| Mutation | Result | Failing assertion/case |
|---|---|---|
| m1 Retained before ACTIVE | **KILLED** | Started + calibration refusal |
| m2 Remove `chain.exited` marker | **KILLED** | Exited only; started + exited |
| m3 Literal `refusal.json` only | **KILLED** | Numbered and calibration refusal cases |
| m4 Marker `is_file()` → `exists()` | **KILLED** | Directory marker must be UNKNOWN |
| m5 ACTIVE on started alone | **KILLED** | Started + exited must be retained |
| m6 Original two-marker set | **KILLED** | Refusal, exited, and refusal-family cases |

All mutant test processes exited 1. Mutation-induced `Refused` exceptions also occurred for m2/m5/m6; each had explicit assertion failures independently establishing the kill. [Detailed results](/tmp/retention-audit-3pdov0/replay/mutations.json).

**Q3 — full module**

Executed once:

```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night
```

Verbatim tail, exit 0:

```text
----------------------------------------------------------------------
Ran 94 tests in 272.515s

OK
```

**Authority comparison**

Both governing texts were read from `origin/bookkeeping/2026-09-21-activation-29ea94df`, ultimately pinned at `0cd42bd755b8db86d3f4e3df2ac453abfbf1326a`, under `docs/process_traces/2026-09-21-activation-29ea94df/05-coldgate-packet-a230-retained-root-discovery/`.

- `10-coldgate-fable-ruling.md:21–29`: Python classification and contract replacement conform.
- `10-coldgate-fable-ruling.md:39–50`: runbook paragraph conforms; shell loop is byte-identical after removing quotation prefixes. F1 therefore originates in the ruled text.
- `10-coldgate-fable-ruling.md:60`: handbook operative commands and stop rule conform.
- `10-coldgate-fable-ruling.md:68–75`: regression behaviors executed; all six requested mutations killed.

The refusal globs match `scripts/run_night.py:281–284`. Installer admission checks at `joulewise/night_agent_install.py:1130–1141` are broader than retention classification. `_record_chain_exit` at `scripts/run_night.py:411–427` also records failed launches; the ruling does not require successful execution for retention. Contract items 0 and 5 remain unchanged.

## Residual risk

A263 remains reproducible: at `t0 + 600`, a started-and-exited fixture returns `retained/pass` while `plan_span_active` returns `True`. This is the already-registered gap at `TASK_QUEUE.md:881`, described by `11-opus-contract-refuter.md:80–85` and implemented by `scripts/magistrate_watchdog.py:775–790`.

Live helper termination, respawn behavior, and hardware operation were not exercised. All writes stayed in scratch fixtures; the reviewed worktree remained clean at `fc28d782`. The next step is lead disposition of F1 and amendment of Q2’s manual loop.