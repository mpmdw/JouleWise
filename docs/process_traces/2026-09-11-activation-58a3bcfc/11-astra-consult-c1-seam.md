```json
{
  "schema": "claude-codex-report/v1",
  "genre": "triage",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend (ii): select a fixed calibration digest through registration_path, preserve exact bytes, and retain one campaign pin across all nights.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "cf88b369c3fabbfce01c14e6163af8c7bb6b6160",
    "head_end": "bf33fc4cca4f6405f0d0a22f3741951263ea7443",
    "upstream_end": "bf33fc4cca4f6405f0d0a22f3741951263ea7443",
    "branch": "bookkeeping/2026-09-11-activation-58a3bcfc"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-09-11-activation-58a3bcfc/04-seat-interp-pin-report.md",
    "docs/process_traces/2026-09-11-activation-58a3bcfc/08-refuter-execution-interp-pin.md"
  ],
  "verdict": {
    "regions": [
      {
        "region": "C1 calibration registration",
        "disposition": "compose",
        "action": "Use the existing calibration registration_path to select its fixed digest; preserve legacy D166 behavior elsewhere."
      },
      {
        "region": "Capture chain, issuer, and r6 acceptance",
        "disposition": "preserve",
        "action": "Preserve their bytes and scientific semantics."
      },
      {
        "region": "Runbook and first-night registration freeze",
        "disposition": "compose",
        "action": "Document the selected C1 pin, fill the existing factual placeholders before capture, and preserve that digest across subsequent nights."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "shasum -a 256 configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265  configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json",
          "ca2430ddd04b4a95b3ea0420ecf4d0897e1d1409f9d4f9f102414d00c37a5da7  configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ca2430ddd04b4a95b3ea0420ecf4d0897e1d1409f9d4f9f102414d00c37a5da7"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_gate.NightGateTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -c 'import subprocess, unittest\nfrom pathlib import Path\nfrom joulewise import night_gate as g\nfrom tests.test_night_gate import FakeProbeSource, make_plan\npath = \"configs/calibration/preregistration_d079_epoch_25g83_rev1.md\"\nregistered = Path(path).read_text(encoding=\"utf-8\")\nlegacy = Path(g.D166_REGISTRATION_PATH).read_text(encoding=\"utf-8\")\nfor ref in (\"main\", \"origin/main\"):\n    assert subprocess.check_output([\"git\", \"show\", ref + \":joulewise/night_gate.py\"]) == Path(g.__file__).read_bytes()\nprint(\"Gate source identical: main, origin/main, HEAD\", flush=True)\ndef receipt(text, cls=\"DIAGNOSTIC_NO_PACK\"):\n    source = FakeProbeSource()\n    source.text[path] = text\n    return g.evaluate_night(make_plan(cls, registration_path=path), source.probes())\nclass Defects(unittest.TestCase):\n    def test_registered_calibration_diagnostic(self):\n        self.assertEqual(\"GO\", receipt(registered).verdict)\n    def test_registered_calibration_rehearsal(self):\n        self.assertEqual(\"REHEARSAL_ONLY\", receipt(registered, \"REHEARSAL_STUB\").verdict)\n    def test_d166_cannot_authenticate_calibration_path(self):\n        self.assertEqual(\"REFUSED\", receipt(legacy).verdict)\n    def test_nights_2_3_keep_night_one_registration(self):\n        outcomes = [receipt(registered), receipt(registered + \"\\n\"), receipt(registered + \"changed\\n\")]\n        self.assertEqual([\"GO\", \"REFUSED\", \"REFUSED\"], [r.verdict for r in outcomes])\n        for r in outcomes[1:]:\n            self.assertEqual(\"night_refused_registration\", r.refusal.reason)\nunittest.main(verbosity=1)'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=4)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=4\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B -c 'import ast, io, subprocess\nfrom pathlib import Path\nfrom unittest import mock\nfrom tests.test_run_night import _load_driver\ndef function(source):\n    tree = ast.parse(source)\n    return ast.dump(next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == \"make_probes\"))\nsource = Path(\"scripts/run_night.py\").read_text()\nfor ref in (\"main\", \"origin/main\"):\n    assert function(subprocess.check_output([\"git\", \"show\", ref + \":scripts/run_night.py\"], text=True)) == function(source)\nprint(\"make_probes identical: main, origin/main, HEAD\", flush=True)\ndriver = _load_driver()\nraw = b\"registered rule\\r\\n\"\ndef reader(path, mode=\"r\", buffering=-1, encoding=None, errors=None, newline=None):\n    return io.TextIOWrapper(io.BytesIO(raw), encoding=encoding or \"utf-8\", errors=errors, newline=newline)\nwith mock.patch.object(Path, \"open\", reader):\n    observed = driver.make_probes().read_text(\"/fixture/registration.md\").encode(\"utf-8\")\nprint(\"observed=\" + repr(observed) + \"; raw=\" + repr(raw), flush=True)\nassert observed == raw, \"registration probe normalizes changed CRLF bytes\"'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: registration probe normalizes changed CRLF bytes"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "AssertionError: registration probe normalizes changed CRLF bytes"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Packet F6 incorrectly claims C1 passed on 09-09. Its receipt says not evaluated after refusal.",
      "needs": "Correct the historical claim."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The observed calibration digest includes unfilled bracket fields and is not a final arm pin.",
      "needs": "Finalize the factual fields and freeze the final digest before night one; do not repin between nights."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Production text reads normalize CRLF, defeating literal byte-change detection.",
      "needs": "Use a byte-preserving UTF-8 read in make_probes."
    },
    {
      "id": "F4",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD advanced concurrently; the committed delta contains only 06-coldgate-ruling-item6.md. Relevant gate code and make_probes remain identical to both main refs.",
      "needs": "Lead performs final verification on the implementation head."
    }
  ]
}
```

## Decision matrix

| Region | disposition | evidence | exact action |
|---|---|---|---|
| F1–F2: current C1 | compose | Read `night_gate.py:32–41,1300–1328`; independently reproduced both digests. Calibration bytes refuse; D166 bytes placed at the calibration path pass. | Select the expected digest by the explicit registration identity/path. Merely accepting either digest everywhere is insufficient. |
| F3: runbook | preserve | Read §0.5, §1.1, §1.4 assertions and §5; inspected promotion commit `7a0511d6`. | Keep the calibration pre-registration as this night’s `registration_path`; explain its new C1 authentication. |
| F4: generator/chain | preserve | Read generator exports, example, parser and chain startup. Neither authenticates the pre-registration. | Leave them unchanged under recommendation (ii); C1 supplies the missing check before chain launch. |
| F5: desk enforcement | preserve | Read issuer `check`, `preregistration_epoch_pins`, and `_prepare_candidate`. | Keep issuance authentication. Correct the packet’s precision: `check` parses both pins but compares only the sampler digest against the registration. Its registration-session dry-run also returns its own status. It is not full-file authentication. |
| F6: historical nights | compose | Both harvested plans name D166; the G2-a draft also names D166. The actual 09-09 receipt records C1 `FAIL`, detail `not evaluated after refusal`. | Retain the plan-path observation; withdraw “C1 passed on 09-09.” |
| F7: continuity | preserve | Read §0.5’s stop rule, revision-2 text, and history entries `12162263`/`07995051`. | Freeze once before the first capture. Earlier registration revisions do not license changing the frozen document between capture nights. |

**Choose (ii), with selection through the existing `registration_path`.** Give the canonical calibration path—and its absolute form under `measurement_root`—one fixed expected digest. Preserve the existing D166 route for other plans. Do not infer scientific purpose from `chain.zsh`, receipt class alone, or a suffix match.

This implements [Ed’s ruling]( /Users/edr/code/JouleWise-wt-bk-58a3bcfc/docs/process_traces/2026-09-10-activation-96bfeca7/146-directive-316-ed-ruling-body.md): rules fixed before data, night one counts on FAIL, and the merged capture chain remains unchanged. It adds no plan field, wrapper input, chain environment variable, or scientific calculation.

| Option | What FAIL-route night 2/3 does if registration bytes change |
|---|---|
| **(i)** | The operator must stop before arm. If that stop is missed, C1 still passes D166 and capture can proceed; issuance later refuses only if supplied the original digest. This leaves the night-time seam open. |
| **(ii), recommended** | Stop before arm if detected there. Otherwise C1 emits `night_refused_registration` at t0, with no chain launch or captures. Do not update the constant to make that night pass. |
| **(iii)** | Stop before arm. If missed, the chain refuses before reservation/settle/capture **provided its wrapper retains night one’s digest**. Regenerating a wrapper from the changed file silently adopts a new pin unless generation also checks the original expected digest. As proposed, `--preregistration PATH` alone does not enforce that continuity. |

For every option, changing the frozen bytes is a stop requiring diagnosis. Preserve night-one evidence and its original registration. Restore the original registered bytes for any authorized continuation, or obtain an explicit ruling about a changed registration and existing data. Do not silently reclassify, discard, or replace night one.

## Composition recipe

1. **Finalize the registration before pinning it.** The current `ca2430dd…` digest still covers `[DD]`, `[MLX_VERSION]`, `[SEQ]`, `[DIGEST]`, and `[CHAIN_SHA256]`. Fill those existing factual fields before any capture, then commit the completed file and its fixed C1 digest together. Keep that value for nights 2/3 even though their ledger head pins advance.

2. **Add the narrow calibration C1 branch.** Match the exact canonical relative path or its absolute measurement-clone form. Compare against the fixed calibration digest; retain `night_refused_registration` on mismatch. Record registration identity, path, expected digest and observed digest in C1 evidence. Both `DIAGNOSTIC_NO_PACK` and `REHEARSAL_STUB` use this branch.

3. **Preserve file bytes through the production probe.** `Path.read_text()` currently normalizes CRLF. Use a UTF-8 read preserving newline bytes, such as `read_bytes().decode("utf-8")`; strict decoding continues to fail closed. V4 reproduces this defect without filesystem writes.

4. **Use this proposed implementation `WRITE_SCOPE`:**

   ```text
   joulewise/night_gate.py
   scripts/run_night.py
   tests/test_night_gate.py
   tests/test_run_night.py
   docs/phase_2/derivation_night_runbook.md
   configs/calibration/preregistration_d079_epoch_25g83_rev1.md
   ```

   The registration-file scope is limited to the five existing factual placeholders. No kernel, decision-log, capture-chain, generator, issuer, estimator or r6 artifact edits are needed. This consult wrote nothing; the list is for the lead’s implementation delegation.

5. **Land these defect-shaped tests.** All five assertions were executed read-only and fail against code verified identical to both `main` and `origin/main`:

   | Test | Required behavior | Observed on main-equivalent code |
   |---|---|---|
   | Registered calibration diagnostic | Valid registration yields `GO`. | `REFUSED`. |
   | Registered calibration rehearsal | Same registration yields `REHEARSAL_ONLY`. | `REFUSED`. |
   | Cross-document substitution | D166 bytes at the calibration path refuse. | `GO`. |
   | Campaign continuity | Original night-one registration passes; independently changed night-2/3 bytes refuse under the same pin. | All three refuse, including the valid baseline. |
   | Production byte preservation | CRLF registration bytes survive the probe unchanged. | Converted to LF. |

   The continuity test must retain its successful baseline: a mutation-only refusal test already passes on main and would not demonstrate this cure. Preserve existing D166 and refusal-precedence coverage. The existing **53 `NightGateTests` passed**. Full-suite and live verification remain for the implementation; no hardware probes or capture were executed.

6. **Carry the following in the arm record:**

   - Completed registration path, revision, immutable committed copy/reference, full SHA-256, selected C1 expected digest, and pre-capture recording time. Nights 2/3 cite night one’s arm record and explicitly demonstrate the same digest.
   - Full measurement/driver heads, clean-tree evidence, measurement root, plan bytes/hash, plan ID/class, session ID, twelve declared slot bindings, custody/runs roots, and each night’s ledger baseline/head pin.
   - Wrapper bytes/hash and sidecar, generator verification result, tracked chain digest, calibration-plan digest, and identity-epoch/T1 input paths and digests.
   - Ed’s issue-316 authority and frozen outcome rules, including `m < 6` INCONCLUSIVE, PASS continuation, and FAIL counting night one.
   - r6 artifact identity/digest and operative constants checked against the validator: level `0.032898493715362`, bracket `0.009724`, ceiling `0.010164834757777545`, corpus `17`. I verified the artifact SHA-256 as `0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d`.
   - Existing notice-before-arm evidence, t0 local/UTC, window length, install/exit boundaries, courier deadline and cancellation route.
   - Desk replay of the exact selected C1 registration. At harvest, attach the actual t0 receipt’s observed/expected digest and outcome; an arm record cannot claim that future observation.

RECOMMENDATION: (ii)