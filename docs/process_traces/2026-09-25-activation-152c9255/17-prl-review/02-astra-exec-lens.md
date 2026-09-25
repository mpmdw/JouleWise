```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "484 focused tests completed with 9 skips; two SHOULD-FIX findings and one NIT; no demonstrated launch-context or custody escape.",
  "workspace": {
    "base_requested": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "base_mode": "exact",
    "head_start": "26c52306e7a8886f47ae0b3875228a9de3f135ec",
    "head_end": "26c52306e7a8886f47ae0b3875228a9de3f135ec",
    "upstream_end": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "branch": "feat/2026-09-25-acc-launch-context"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "joulewise/night_agent_install.py",
        "line": 870,
        "title": "Probe receipt plist digests are shape-checked but never verified"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "path": "scripts/run_night.py",
        "line": 3743,
        "title": "Timeout discards available cadence statistics; refusal omits capture duration"
      },
      {
        "id": "F3",
        "severity": "nit",
        "path": "joulewise/night_gate.py",
        "line": 1251,
        "title": "Case aliases of an existing custody directory are falsely refused"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_night_agent_install tests.test_run_night_probe_cadence tests.test_launch_context_no_qos_override tests.test_night_gate tests.test_run_night tests.test_install_night_agent tests.test_evidence_arm_sequence -v > /tmp/152c9255/prl-lens-astra/focused.log 2>&1",
      "cwd": "/tmp/152c9255/prl-lens-astra",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 484 tests in 1092.432s", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=9\\)"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 adversarial_review.py > adversarial.log",
      "cwd": "/tmp/152c9255/prl-lens-astra",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ADVERSARIAL COMPLETE"]
      },
      "expected": {"exit_code": 0, "tail_regex": "ADVERSARIAL COMPLETE"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 receipt_timeout_review.py > receipt_timeout.log",
      "cwd": "/tmp/152c9255/prl-lens-astra",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PARTIAL_TIMEOUT_PARSEABLE_FRAMES 220", "RECEIPT/TIMEOUT COMPLETE"]
      },
      "expected": {"exit_code": 0, "tail_regex": "RECEIPT/TIMEOUT COMPLETE"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 physics_replay.py > physics.log",
      "cwd": "/tmp/152c9255/prl-lens-astra",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PHYSICS REPLAY COMPLETE"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PHYSICS REPLAY COMPLETE"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Nine focused tests skipped because process-group census is unavailable in the sandbox. Existing bench captures were replayed; no new hardware capture or real launchd operation was performed.",
      "needs": "Lead retains responsibility for live cleanup verification."
    }
  ]
}
```

## Findings

**F1 — SHOULD-FIX — `joulewise/night_agent_install.py:870`.**  
`validate_probe_receipt` accepts every rendered-plist digest replaced with either 64 zeroes or 64 `f` characters. It checks hexadecimal syntax, but neither compares these digests with `prepared.launch_context()` nor includes them in the later binding comparison. Consequently, the receipt can certify different plist bytes from those accepted at installation. Current rendering still enforces Interactive, so this is an evidence-binding defect rather than a demonstrated non-Interactive bypass.

**Exact fix:** compare each recorded digest with its corresponding rendered payload, binding the rendering parameters needed to reproduce the probe payload. Add tests that mutate each digest and change template bytes after receipt creation.

**F2 — SHOULD-FIX — `scripts/run_night.py:3743`, also `:3727` and `:3880`.**  
Cadence statistics are parsed only after successful process completion. A fake sampler writing **220 complete 248-ms frames before stalling** returned `count=0` and null median/p95/max, although the production parser subsequently recovered all 220 frames. This loses the diagnostic evidence for the slow regime most likely to hit the production timeout. The installer’s refusal detail also omits `elapsed_s`, one of R6’s three acceptance quantities.

**Exact fix:** after process cleanup, parse available complete frames on timeout and nonzero-exit paths; retain `passed=false`, but populate count and available statistics. Include elapsed time, median and maximum in the refusal, alongside p95/count. Add a partial-output timeout regression.

**F3 — NIT — `joulewise/night_gate.py:1251`.**  
On this filesystem, existing `measurement/child` and `MEASUREMENT/child` identify the same directory, but the second spelling receives `measurement_root_outside_custody`. `resolve()` does not normalize case, while `relative_to()` compares path components case-sensitively.

**Exact fix:** resolve existing paths strictly, then check custody ancestry using filesystem identity (`samefile`) rather than case-folding strings; continue excluding the custody root itself. Add a case-insensitive-filesystem regression.

Execution checks found **no BLOCKER**:

- All seven requested modules completed: **484 tests, zero failures, nine skips**.
- Real rendering of night, dead-man and probe plists refused missing, Background, Standard, Adaptive, wrong-case, integer, padded-string, comment-only and nested-only ProcessType variants.
- Duplicate keys ending in Background refused. Duplicates ending in Interactive passed, with both `plistlib` and native `plutil` reading Interactive; no parser disagreement was demonstrated.
- R16 rejected outside symlinks, escaping `..`, sibling prefixes and the custody root itself. Trailing slashes, internal `..`, inward symlinks and `/tmp`–`/private/tmp` aliases behaved correctly. A symlink loop failed the subsequent real Git lookup.
- The target tree remained clean. Pinned estimator, sampler-adapter and production-chain files were unchanged.

## Residual risk

**Physics:** the gate is a sound discriminator of the **recorded delivered-cadence regimes**. Replaying the raw controls reproduced Interactive median **125.590 ms**, maximum **132.821 ms**, versus default median **173.202 ms**, maximum **262.296 ms**. The reported night regime at 237–248 ms is farther outside the limits. This supports the threshold choice, but does not establish future overnight performance.

**False refusal under load is not estimable from these runs.** For an otherwise correctly configured Interactive job, if each frame independently exceeds 200 ms with probability \(p\), the maximum criterion alone refuses with probability \(1-(1-p)^{300}\):

| Per-frame exceedance probability | Probe refusal probability |
|---:|---:|
| 0.01% | 3.0% |
| 0.1% | 25.9% |
| 0.5% | 77.8% |

These are sensitivity calculations, not measured rates; correlated scheduling delays invalidate the independence assumption. Such refusals still correctly identify a delivered-cadence violation. The successful control with multiple active agents is encouraging, but insufficient to quantify reliability.

**Do not drop frame one on present evidence.** Its interval was **113.486 ms** in Interactive and **158.352 ms** in default context—below each run’s median. Removing it changes neither maximum nor decision; Interactive median becomes 125.592 ms and default median 173.539 ms. Keeping all 300 frames also matches R6’s production-shaped criterion.

Live process-group cleanup remains outside this review’s coverage because of the nine sandbox skips and the explicit prohibition on real launchd/hardware execution.