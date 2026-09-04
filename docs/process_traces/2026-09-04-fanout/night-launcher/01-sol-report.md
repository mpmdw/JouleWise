```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "The transaction night path now authenticates its inputs, consumes a custodied GO receipt, and invokes the reviewed launcher exactly once.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-night-launcher-integration"
  },
  "pathspec": [
    "docs/process/NIGHT_HANDBACK.md",
    "docs/process_traces/2026-09-04-fanout/night-launcher/01-sol-report.md",
    "joulewise/night_gate.py",
    "scripts/run_night.py",
    "tests/test_night_gate.py",
    "tests/test_run_night.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate tests.test_run_night tests.test_launch_window",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 128 tests in 262.334s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 128 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The brief prohibited hardware work, so verification used fixtures and a fake launcher only.",
      "needs": "The magistrate retains the live quiet-machine gate."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "This lane consumes but does not produce the protected confirmation-digest file.",
      "needs": "The plan-arming workflow must create the named mode-0600 file before the night is armed."
    }
  ]
}
```

## Change

The night plan now requires the exact pack, arm receipt, arm-readiness custody
root, launch manifest, and confirmation-table paths for a transaction night.
The gate authenticates the unconsumed arm and all frozen launch inputs before
it issues its classed GO receipt. The driver then revalidates that canonical
receipt, rereads the protected confirmation digest, detects any intervening
change, and supplies the complete argument set to the reviewed launcher
through the existing once-only child-session path.

The confirmation digest is accepted only from
`085-ed-step6-confirmed-sha256.txt` beneath the plan custody root. The file must
be a regular file, must not be a symbolic link, must have filesystem mode
`0600`, and must contain one lowercase SHA-256 digest followed by one newline.
The handback explains the narrow custody-file amendment and still forbids an
environment file or a launch-time recomputation.

### Finding and decision table

| Question | Governing source | Implemented disposition | Further ruling |
|---|---|---|---|
| Who authorizes and launches? | Issued hands-free authorization | The night gate issues GO; the driver invokes the reviewed launcher once. | None |
| Which receipt form applies? | Issued unattended class table | The existing classed five-condition receipt is used; the older rehearsal-only consumer schema is not extended. | None |
| Which paths enter the launcher? | Launcher argument parser and window runbook | Plan keys use the launcher argument names and the driver passes every required path explicitly. | None |
| Where does the confirmation digest come from? | Window runbook and issued custody direction | The driver reads the existing transcript name under protected plan custody and never derives the digest. | None |
| How do missing inputs refuse? | Existing night reason-code registries | Missing plan fields use `night_plan_malformed`; failed runtime authentication uses `night_probe_error`; a malformed GO uses `night_receipt_class_invalid`. | None; no new vocabulary was invented |
| Who writes the protected digest file? | Issued custody direction | This consumer requires the plan-arming workflow to write it before arming; that producer was not changed in this lane. | None for this consumer; producer integration remains with the plan-arming owner |

No design-bearing question outside the cited authority was encountered. The
implementation therefore has no `NEEDS_RULING` item and made no write outside
the supplied scope.

### First-use test

The mechanical sentence census selected every new reader-facing sentence in
`NIGHT_HANDBACK.md` and reported `COUNT 16`. Each row below records the
first-use review of that sentence.

| Sentence | First-use result |
|---|---|
| S1 — A frozen experiment pack is an immutable set of reviewed measurement inputs. | PASS — defines the pack before later use. |
| S2 — An unattended transaction night is a scheduled measurement that uses one such pack without a person at the keyboard. | PASS — defines the night and reuses the defined pack. |
| S3 — The arming step is the preparation that checks that pack. | PASS — defines the arming step. |
| S4 — An arm receipt is its one-use record that the pack passed those checks. | PASS — defines the arm receipt. |
| S5 — The arming step must place the confirmed SHA-256 digest, a cryptographic fingerprint called `hC`, in the plan's custody root, the protected directory named by the night plan, as `085-ed-step6-confirmed-sha256.txt`. | PASS — defines SHA-256, `hC`, and the custody root. |
| S6 — That custody file must be a regular file rather than a symbolic link, a filesystem pointer to another path; must have owner-only read and write permissions (filesystem mode `0600`); and must contain only the lowercase digest followed by one newline. | PASS — defines the symbolic link and permission mode at first use. |
| S7 — The night gate is the pre-launch check that evaluates every required launch condition. | PASS — defines the night gate. |
| S8 — It creates a GO receipt, the record that those conditions passed, only after it authenticates the arm receipt and the frozen launch inputs with the digest stored in custody. | PASS — defines the GO receipt and reuses earlier terms. |
| S9 — The night driver is the program started by the schedule. | PASS — defines the driver. |
| S10 — The reviewed launcher is the program that consumes the one-use arm receipt as one indivisible operation and starts the frozen measurement chain, the immutable sequence of measurement commands. | PASS — defines the launcher, indivisible operation, and frozen chain. |
| S11 — The arm-readiness custody root is the protected directory that holds the arm records. | PASS — defines the arm-readiness custody root. |
| S12 — The launch manifest is the authenticated record of the exact frozen command. | PASS — defines the launch manifest. |
| S13 — The step-6 confirmation table is the published record of the pack-family confirmation. | PASS — defines the confirmation table. |
| S14 — When the receipt says GO, the night driver calls the reviewed launcher once and supplies those records and paths. | PASS — uses only defined terms. |
| S15 — A missing input, an altered digest, an insecure custody-file mode, or any launcher refusal ends that attempt without a retry. | PASS — uses plain-language terms. |
| S16 — This is the narrow amendment to the earlier instruction that `hC` must never be stored in an environment file: automation may store `hC` in the protected custody file above, but it still must not store `hC` in an environment file or derive it again from the confirmation table at launch time. | PASS — uses only defined terms and states the amendment. |

## Verification notes

| Command | Exit | Stable tail or observation |
|---|---:|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate tests.test_run_night tests.test_launch_window` | 0 | `Ran 128 tests in 262.334s`; `OK` |
| Mechanical added-sentence census over `git diff --unified=0 -- docs/process/NIGHT_HANDBACK.md` | 0 | `S16` was the amendment sentence; `COUNT 16` |
| `git diff --check` | 0 | No output. |

An earlier focused run exposed a system-Python import regression caused by a
top-level launcher import. Moving that import into the transaction-only
verifier restored installer compatibility; the final focused run above is the
post-fix evidence.

## Residual risk

The protected confirmation-digest file remains an input supplied by the
plan-arming workflow. If that workflow omits the file or gives it insecure or
malformed contents, the implemented gate refuses before the launcher starts.
