```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Q3: This expiry defect does not affect tonight's recorded DIAGNOSTIC_NO_PACK path; the bench failures come from a fixture deadline fixed at seven days of host monotonic uptime.",
  "workspace": {
    "base_requested": "origin/main@ace4cc3c",
    "base_mode": "exact",
    "head_start": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "head_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "upstream_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {"cause": "confirmed", "remediation": "proposed"},
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_dry_run_becomes_stale_after_later_head_even_when_pack_bytes_do_not_change",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 1 test in 1.732s", "Ran 1 test in 1.711s", "Ran 1 test in 1.712s", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B /tmp/jw-arm-expiry-boundary.py > /tmp/jw-arm-expiry-boundary.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B /tmp/jw-arm-expiry-suite.py original > /tmp/jw-arm-expiry-original.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 8 tests in 17.121s", "FAILED (failures=7, skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B /tmp/jw-arm-expiry-suite.py relative > /tmp/jw-arm-expiry-relative.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 8 tests in 63.061s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B /tmp/jw-night-expiry-path.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NIGHT_PATH_PASS", "Ran 1 test in 0.169s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "NIGHT_PATH_PASS"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Sandbox denies kern.bootsessionuuid, so the exact real-boot ACID test skipped. Its live-clock, real-CLI variant with a synthetic boot ID failed before the fixture correction and passed afterward. Both suite processes also printed an ignored Metal-device atexit warning.",
      "needs": "Lead may replay the exact real-boot test after implementing the fixture correction."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "No repository writes or prohibited-root reads. Production conclusions use committed arm evidence and code; synthetic probes do not establish live night readiness.",
      "needs": ""
    }
  ]
}
```

## Causal chain

**Q3 — tonight.** The committed staged plan is `DIAGNOSTIC_NO_PACK`, authored at epoch `1789200196.934819`, with t0 `1789293360`. The arm record reports publication at 03:00:23 and byte equality with that staged copy (`docs/process_traces/2026-09-12-activation-b58fb582/02-equivalence-night-arm-record.md:38`, `:78`, `:92`).

The relevant production chain is:

- `scripts/run_night.py:1498` selects pack handling **only** for `TRANSACTION_PACK`; tonight uses `:1522`, then the ordinary chain command at `:1615`.
- `joulewise/night_gate.py:1129` skips pack authentication for diagnostic plans. Its boot/expiry comparison at `:1286` requires a non-null `pack_arm`. Diagnostic C4 records a fresh boot/clock pair.
- The wrapper executes the derivation chain (`scripts/gen_derivation_night.py:421`). Its “readiness” command is **calibration-ledger readiness**, followed by reservation and derivation-only captures (`scripts/night_chains/calibration_derivation_only.zsh:152`, `:160`, `:209`; `joulewise/calibration_ledger.py:5155`). It does not consume arm-readiness receipts.

Executed synthetic probes using tonight’s recorded dates returned GO at monotonic `642718899296000` and `729118899296000`—24 hours apart—with **zero pack-condition calls**. The driver fixture also recorded **zero pack-arm calls**. Plan freshness is separately bounded to 36 hours (`joulewise/night_gate.py:58`, `:998`): at t0 its age is `93163.065181 s` = **25.878629 h**, leaving `36436.934819 s` of freshness margin.

For comparison, a **transaction-pack** night calls `_author_pack_arm` at `scripts/run_night.py:1509`: T0 evidence author at `:1135`, new arm generator at `:1140`, verification at `:1151`, GO publication and launcher at `:1258`/`:1264`, then `scripts/launch_window.py:266` → `_consume_launch_capability` → `_verify_arm_receipt` (`joulewise/arm_readiness.py:10397`, `:9057`).

There is **no overnight arm-capability horizon**: registry capability and consumption budget are both `300000000000 ns` (300 s), and arm validity is the minimum of evaluation time plus that horizon and evidence expirations (`configs/arm_readiness/d117_row_registry_v2.json:4`; `joulewise/arm_readiness.py:8740`). A 03:00 capability **can expire** before tomorrow: the supplied arm-to-t0 interval is `86141.5 s`; if continuously awake, it exceeds the capability horizon by `85841.5 s`. Sleep prevents equating wall elapsed with monotonic elapsed, but does not extend the permitted awake lifetime. Existing T0 evidence is authenticated, not automatically refreshed (`joulewise/arm_readiness_evidence_t0.py:2302`). Tonight’s diagnostic plan never enters this path.

Executed Git comparisons found these production files unchanged between tonight’s pinned `f90cb8c0` and inspected `ace4cc3c`.

**Q1 — exact failing branch.** Scratch tracing captured:

| Field | Observed value |
|---|---|
| Evidence | `freeze-acceptance-owner-v1`, `ACCEPTANCE_OWNER` |
| Receipt boot ID | `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa` |
| Expected boot ID | `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa` |
| `valid_until_monotonic_ns` | `604800000000001` |
| Authentication now | `642506373756416` |
| Expired by | `37706373756415 ns` = **10.473993 h** |

The exception is **“evidence item expired”** at `joulewise/arm_readiness.py:6299`, not the prior-boot branch at `:6285`. Stack: dry-run generation `:8239` → freeze-reference loading `:7564` → generic authentication `:6299`.

**Q2 — why now.** `install_passing_freeze` supplies **`now_monotonic_ns=1`** (`tests/test_arm_readiness_dry_run.py:176`). The production assembler adds the policy horizon (`joulewise/arm_readiness_evidence.py:2910`), which is **604800000000000 ns = seven days** for this kind (registry `:12`). Freeze replay supplies no synthetic authentication time (`joulewise/arm_readiness.py:7564`), so `:6294` samples the host clock.

Re-authenticating the **same evidence bytes** produced:

- `604800000000000`: PASS.
- `604800000000001`: PASS.
- `604800000000002`: `readiness_record_expired`.
- Live `642646232973541`: the same refusal.

Executed diff against yesterday’s `97da620e` found no changes in the fixture, affected test modules, author, authenticator, or registry. Yesterday’s supplied green result therefore implies the reader was still within the fixed deadline. Today it exceeds it. With sleep excluded, the measured excess places crossing **no later than approximately 19:20 PDT September 11**; sleep moves it earlier. The precise crossing time needs retained clock samples.

V1 ran three separate processes: **3/3 failures**, 1.732/1.711/1.712 seconds. This is deterministic uptime coupling; contemporary load is unnecessary. CI uses Ubuntu (`.github/workflows/ci.yml:18`), and the real-boot ACID case is Darwin-only (`tests/test_arm_readiness_evidence_t0.py:3107`); green CI does not cover this long-uptime Darwin condition.

## Remediation

Correct the shared fixture’s clock origin. In scratch only, replacing its `1 ns` authoring origin with current monotonic time, while retaining production expiry checks and horizons, changed **six exact failing tests plus the live-clock synthetic-boot ACID variant from FAIL to PASS**. The exact real-boot test skipped under this sandbox. That ACID fixture uses the same freeze helper (`tests/test_arm_readiness_evidence_t0.py:432`).

Production authoring already samples current monotonic time and passes it to the assembler (`joulewise/arm_readiness_evidence.py:3395`, `:3426`). No production deadline change is indicated.

**Q4 classification:** new bench-fixture instance of host-uptime coupling. No `readiness_record_expired` match exists in the current kernel. Related completed families are `ARM-INTEGRATION-LOAD-01` and `T0-ACID-CLOCK-03` (`TASK_QUEUE.md:102`, `:108`); consult `docs/process_traces/2026-09-09-rehearsal-harvest/99-rootcause-arm-load-ci-astra-report.md:80` concerns the opposite, short-uptime threshold. Historical August production expiry findings concerned actual old evidence, not this fixture origin.

Proposed row: **`ARM-READINESS-FIXTURE-UPTIME-01 [AGENT]` — Remove the shared freeze fixture’s absolute seven-day uptime deadline; keep author and consumer clocks coherent, including real-clock subprocess tests. Verify all seven named tests and boundary behavior below/at/above seven days. Preserve production expiry and boot-session enforcement.**

## Disproved alternatives

- **Watchdog relaunch/prior boot:** observed IDs match; expiry crossed before the proposed 03:46 relaunch.
- **Wall-clock fixture date:** this refusal compares monotonic integers; `issued_at_utc` is not its operand.
- **600-second R1 liveness or 300-second arm timeout:** failure occurs while loading freeze evidence, before arm evaluation (`joulewise/arm_readiness.py:8571`, `:8595`).
- **New main-code regression or load race:** unchanged relevant code, exact one-nanosecond boundary, repeatable failures, and fixture-only counterfactual success.

## Residual risk

Actual armed custody remains uninspected. For the magistrate’s final record-to-custody check, read only these paths under `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260913/`:

- `night_plan.json`
- `chain.zsh`
- `chain.zsh.sha256`

No re-arm or production change is supported by this finding.