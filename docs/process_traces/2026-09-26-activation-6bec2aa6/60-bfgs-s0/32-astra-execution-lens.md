```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two blockers and four should-fix findings reproduced; all executed suites passed; repository unchanged.",
  "workspace": {
    "base_requested": "64e39bb9",
    "base_mode": "informational",
    "head_start": "26ab72342e7200ebf0494f6e627bbb56e14f266c",
    "head_end": "26ab72342e7200ebf0494f6e627bbb56e14f266c",
    "upstream_end": "6a463e87fb460e5f0d9ef0da50c48e3c5b48ff35",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "R1",
        "severity": "blocker",
        "title": "Malformed rounds journal suppresses custody failures",
        "location": "joulewise/battery_float.py:865"
      },
      {
        "id": "R2",
        "severity": "blocker",
        "title": "Invalid timing evidence passes; malformed span types can preempt custody",
        "location": "joulewise/battery_float.py:776"
      },
      {
        "id": "R3",
        "severity": "should_fix",
        "title": "Duplicate JSON keys silently replace contradictory authentication evidence",
        "location": "joulewise/battery_float.py:851"
      },
      {
        "id": "R4",
        "severity": "should_fix",
        "title": "Capture authentication accepts inconsistent slot and attempt identities",
        "location": "joulewise/battery_float.py:927"
      },
      {
        "id": "R5",
        "severity": "should_fix",
        "title": "Fixed raw paths can resolve through symlinks outside custody",
        "location": "joulewise/battery_float.py:806"
      },
      {
        "id": "R6",
        "severity": "should_fix",
        "title": "Missing NightKind battery flag raises without journaling refusal",
        "location": "joulewise/evidence_night.py:1392"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep > /tmp/bfgs-astra-v1.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 95 tests in 178.785s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_evidence_night tests.test_night_kinds > /tmp/bfgs-astra-v2.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 178 tests in 974.720s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float.PairAuthenticationTests tests.test_battery_float.BundleAuthenticationTests tests.test_battery_float.S0FreezeTests tests.test_battery_float_consumers tests.test_battery_float_sweep tests.test_night_kinds > /tmp/bfgs-astra-focused.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 52 tests in 226.830s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "BFGS_REPO=\"$PWD\" PYTHONPATH=\"$PWD\" PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_astra_attack.py > /tmp/bfgs-astra-attacks.jsonl 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ATTACK_MATRIX_COMPLETE 83"]
      },
      "expected": {"exit_code": 0, "tail_regex": "ATTACK_MATRIX_COMPLETE 83"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "BFGS_REPO=\"$PWD\" PYTHONPATH=\"$PWD:/tmp\" PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_astra_followup.py > /tmp/bfgs-astra-followup.jsonl 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["FOLLOWUP_COMPLETE"]
      },
      "expected": {"exit_code": 0, "tail_regex": "FOLLOWUP_COMPLETE"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "BFGS_REPO=\"$PWD\" PYTHONPATH=\"$PWD:/tmp\" PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_astra_nightkind.py > /tmp/bfgs-astra-nightkind-slots.jsonl\npython3 -B /tmp/bfgs_astra_confirm.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["CONFIRMED: 6 finding groups; 95 executed probes."]
      },
      "expected": {"exit_code": 0, "tail_regex": "CONFIRMED: 6 finding groups; 95 executed probes\\."}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical full suite and additional importer-only modules were not rerun. Execution used the listed suites and injected fixtures; no live hardware validation.",
      "needs": "Lead retains final verification."
    }
  ]
}
```

## Findings

1. **R1 — BLOCKER: corrupting the rounds journal converts custody failure into pass.** At [battery_float.py:865](/Users/edr/code/JouleWise-wt-s0-astra-6bec2aa6/joulewise/battery_float.py:865), a valid row containing a mismatching raw digest raises `CustodyFailure`. Appending `{\n` to that same file makes authentication return `pass`: the JSON exception replaces **every row** with `[]`. A directory at `rounds.jsonl` and a dangling journal symlink also pass. A `{"raw": null}` row instead escapes as `AttributeError`.

   **Fix:** never replace an unreadable or malformed journal with a successful empty inventory. Preserve custody checks on readable rows, validate nested map types, and refuse present-but-unusable journals. Preserve the legitimate no-rounds refusal path.

2. **R2 — BLOCKER: invalid timing evidence is accepted.** [Pair validation](/Users/edr/code/JouleWise-wt-s0-astra-6bec2aa6/joulewise/battery_float.py:776) accepts quiet span `(70, 30)`; the quiet wrapper likewise passes reversed endpoints and boolean endpoints. Negative pre stamps, inverted probe durations, and malformed unused probe timestamps also pass. Separately, bundle `span=42` raises `TypeError` **before** discovering a deleted post raw file, defeating custody precedence.

   **Fix:** validate span shape without throwing; reject booleans before quiet seconds-to-nanoseconds conversion; require finite, nonnegative, ordered bounds. Validate probe timestamps and internal ordering. Apply timing refusals at the span stage after custody, probe, parse, and predicate processing. **Equal endpoints are permitted by the bundle ruling and are not a finding.**

3. **R3 — SHOULD-FIX: duplicate JSON keys hide contradictory evidence.** The [JSON readers](/Users/edr/code/JouleWise-wt-s0-astra-6bec2aa6/joulewise/battery_float.py:851) accept duplicate session IDs, phases, run IDs, event monotonic bounds, and row digest keys. A row with an incorrect digest followed by the correct digest under the same key returns `pass`.

   **Fix:** use duplicate-rejecting JSON decoding throughout the new wrappers, including JSONL records. Route ambiguity through refusal handling while preserving custody precedence. This is a decoding-hardening gap; the ruled text does not explicitly define duplicate-key policy.

4. **R4 — SHOULD-FIX: capture identity is partly self-asserted.** [authenticate_capture](/Users/edr/code/JouleWise-wt-s0-astra-6bec2aa6/joulewise/battery_float.py:927) passes a pre/post pair carrying different slots and attempt IDs. It also passes a non-null attempt ID that disagrees with the enclosing evidence’s `validation_id`.

   **Fix:** require matching pre/post slot and attempt identities, and bind non-null attempt IDs to the capture’s `validation_id`. Preserve legitimate standalone null identities. The lead should explicitly settle this binding: text 2 specifies the wrapper but leaves its external capture-identity source unstated.

5. **R5 — SHOULD-FIX: fixed paths do not enforce custody containment.** At [raw-file loading](/Users/edr/code/JouleWise-wt-s0-astra-6bec2aa6/joulewise/battery_float.py:806), both internal and external raw-file symlinks return `pass`.

   **Fix:** reject symlink components below the custody root using directory-relative, no-follow opens; treat violations as custody failures. SHA-256 comparison still works—the demonstrated gap is path containment, not acceptance of mismatching bytes.

6. **R6 — SHOULD-FIX: an absent flag prevents the refusal journal.** An actual `NightKind` instance missing `battery_brackets` reaches [direct attribute access](/Users/edr/code/JouleWise-wt-s0-astra-6bec2aa6/joulewise/evidence_night.py:1392), raises `AttributeError`, and writes no check record.

   **Fix:** use `getattr(row, "battery_brackets", False) is True` and retain the existing `Refused` path. Assert a failed fence and saved non-armable journal. **No accepting fence counterexample was found:** QPE, unknown kinds, `None`, and non-boolean truthy flags were refused; calibration remained unchanged.

## Residual risk

All evidence is fixture-based. Reproducers and outputs are retained in the [primary harness](/tmp/bfgs_astra_attack.py), [follow-up harness](/tmp/bfgs_astra_followup.py), [primary results](/tmp/bfgs-astra-attacks.jsonl), and [follow-up results](/tmp/bfgs-astra-followup.jsonl). Frozen functions were unchanged, and the candidate touched exactly the eight named paths. No pin-value finding is raised.