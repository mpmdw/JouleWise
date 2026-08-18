# D-117 ALPHA scratch dress-rehearsal operator card

This is qualification choreography evidence, never claim evidence. The pack is the pre-publication ALPHA successor at the designated measurement checkout `/Users/edr/JouleWise-measurement-20260818`, which began from transaction commit `28a0daa22ca17d5c27df94879763e57c34665646`; Ed's terminal-review commit advances its HEAD. Pack bytes and the authenticated freeze-0002 receipt stay in that checkout. Every mutable custody, ledger, run, and backup namespace is below the literal scratch root below.

`window.env` deliberately has the producer's enforced exact 25-key set, which excludes `ARM_RECEIPT` and `LAUNCH_MANIFEST`; this differs from the runbook chain wording. The paths are derived after ARM in this card; do not edit `window.env`.

| Step | level |
| --- | --- |
| Build | BOUNDARY-PROVEN (syntax and reuse refusal smoke; sandbox cannot create the measurement-checkout `.venv`) |
| Part A dry-run | BOUNDARY-PROVEN (requires Ed's terminal-review commit first) |
| E-4 | BOUNDARY-PROVEN (sandbox boot-ID boundary) |
| E-5 | BOUNDARY-PROVEN (no sudo or clock change in smoke) |
| E-7a/E-7b | ED-FIRST |
| E-8 | BOUNDARY-PROVEN (`calibration_ledger_head_uncommitted` for the scratch-ledger route) |
| E-9a/E-9b/ARM/verify/E-10 | ED-FIRST, blocked unless a lead-approved committed scratch-ledger route is supplied |

## 1. Build — BOUNDARY-PROVEN

```sh
/Users/edr/JouleWise-measurement-20260818/scripts/ed_session/build_rehearsal_env.sh /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal
```

Expected: the manifest prints the designated checkout, pack, every scratch root, and `window.env`. It confirms clean checkout, importable `.venv`, R2 `calibration_plan.json`, and the authentic freeze-0002 pin. The smoke sandbox could syntax-check it and prove its reuse refusal, but could not create the missing `.venv` in the designated checkout; this is Ed-first execution. Likely refusal: an existing root (use the printed exact cleanup command), dirty checkout, wrong branch, or unavailable/stale freeze evidence.

## 2. Terminal review — ED-FIRST

Review the clean checkout personally, then create the genuine scratch-night terminal-review record. Expected: a new empty commit; local `main` and `origin/main` both name it. Likely refusal: dirty checkout, Git identity, or a pack/tree mismatch; preserve it rather than fabricating a record.

```sh
cd /Users/edr/JouleWise-measurement-20260818 && test -z "$(/usr/bin/git status --porcelain=v1 --untracked-files=all)" && TREE_OID="$(/usr/bin/git rev-parse HEAD^{tree})" && PACK_SHA256="$(.venv/bin/python -c 'import sys; from joulewise.arm_readiness import committed_pack_tree_sha256; print(committed_pack_tree_sha256(sys.argv[1]))' /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2)" && /usr/bin/git commit --allow-empty --cleanup=verbatim -m 'JouleWise terminal review attestation' -m 'JouleWise-Terminal-Review: PASS' -m "JouleWise-Terminal-Review-Tree-Oid: $TREE_OID" -m "JouleWise-Terminal-Review-Pack-Sha256: $PACK_SHA256" && /usr/bin/git update-ref refs/heads/main HEAD && /usr/bin/git update-ref refs/remotes/origin/main HEAD && /usr/bin/git show -s --format='review=%H tree=%T%n%B' HEAD
```

## 3. Part A D-134 dry-run — BOUNDARY-PROVEN

Expected after section 2: `status: PASS`, `arm_disposition: NOT_APPLICABLE`, and a no-clobber `dry-run-0001.json` under scratch custody. It proves the real reservation CLI and writer lifecycle against synthetic slots, not live capture. Smoke reached the sandbox boot-ID boundary before this command could run. Likely refusal: checkout no longer clean/exact-main, stale freeze evidence, or reused rehearsal ID.

```sh
cd /Users/edr/JouleWise-measurement-20260818 && .venv/bin/python scripts/generate_arm_readiness.py dry-run --pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2 --window-custody-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody --rehearsal-id ed-qual-20260817 --synthetic-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/dry-run-synthetic
```

## 4. E-4 clock-prior-state — BOUNDARY-PROVEN

First read the state interactively. Expected output is exactly `Network Time: On` or `Network Time: Off`; the password prompt is normal. The wrapper prompts first for an independent trusted-clock UTC literal and then for that exact line. Expected: PASS and the clock attestation, arm context, and launch manifest. Likely refusal: boot-ID probe, terminal-review mismatch, or a pre-existing output.

```sh
/usr/bin/sudo /usr/sbin/systemsetup -getusingnetworktime
```

```sh
cd /Users/edr/JouleWise-measurement-20260818 && .venv/bin/python scripts/capture_t0_step.py clock-prior-state --pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2 --custody-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody --window-plan-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/window-plan
```

## 5. E-5 clock-disable — BOUNDARY-PROVEN

Expected: PASS and capture of D-127's exact passwordless `sudo -n` off vector. Likely refusal: sudoers, boot change, or state did not become Off. This changes the machine clock route; restore it with section 11 immediately after the final rehearsal step.

```sh
cd /Users/edr/JouleWise-measurement-20260818 && .venv/bin/python scripts/capture_t0_step.py clock-disable --pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2 --custody-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody --window-plan-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/window-plan
```

## 6. E-7a quiet-mac-prep — ED-FIRST

Run only in the post-21:30 quiet slot after stopping all agent fleets, browsers/automation, monitors, `caffeinate`, and other operator processes. Expected: PASS quiet-prep capture. Likely refusal: census, display/power, or powermetrics prerequisite.

```sh
cd /Users/edr/JouleWise-measurement-20260818 && .venv/bin/python scripts/capture_t0_step.py quiet-mac-prep --pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2 --custody-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody --window-plan-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/window-plan
```

## 7. E-7b prewindow-check — ED-FIRST

Expected: the governed `--wait --timeout-min 45` probe proves at least **600 seconds** of continuous clean dwell and ends `READY`. Likely refusal: any contamination or timeout; do not bypass it.

```sh
cd /Users/edr/JouleWise-measurement-20260818 && .venv/bin/python scripts/capture_t0_step.py prewindow-check --pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2 --custody-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody --window-plan-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/window-plan
```

## 8. E-8 ledger-readiness — BOUNDARY-PROVEN

The wrapper will bind the exact R2 absolute plan path, plan ID, and SHA-256. With the builder's required scratch copy of the committed 76-row ledger, the current production readiness code then returns `calibration_ledger_head_uncommitted`: it requires the ledger bytes at their selected path to be committed, while the scratch path necessarily is not. Preserve that refusal and **stop Part B here**. Do not point the wrapper at a production ledger or manufacture a committed record. A lead-approved committed scratch-ledger route is required before E-9a and later steps can be rehearsed.

```sh
cd /Users/edr/JouleWise-measurement-20260818 && .venv/bin/python scripts/capture_t0_step.py ledger-readiness --pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2 --custody-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody --window-plan-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/window-plan
```

## 9. E-9a ledger-reservation — ED-FIRST, conditional on a new ledger ruling

Do not run this while section 8 has the documented refusal. If the lead approves a committed scratch-ledger route, expected output is a PASS reservation capture using that approved scratch ledger and two scratch attempt locators. Likely refusal: any stale head pin or already-open session; preserve the refusal.

```sh
cd /Users/edr/JouleWise-measurement-20260818 && .venv/bin/python scripts/capture_t0_step.py ledger-reservation --pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2 --custody-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody --window-plan-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/window-plan
```

## 10. E-9b, ARM, verify, consume — ED-FIRST, conditional on section 9

Expected E-9b output is authored receipts; likely refusal is a missing/stale/misordered capture. **After E-9b, eleven volatile evidence kinds have a 20-MINUTE monotonic horizon: start no new process and proceed immediately to ARM, verify, Ed inspection, then the one launcher invocation.**

```sh
cd /Users/edr/JouleWise-measurement-20260818 && .venv/bin/python scripts/author_arm_evidence_t0.py --pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2 --custody-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody
```

Expected ARM is a PASS/GO receipt; likely refusal is any missing T-0 evidence or freshness failure. The argument is the exact JSON object, derived by E-4.

```sh
cd /Users/edr/JouleWise-measurement-20260818 && ARM_RECEIPT=/Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/d117_floor_qwen25_1p5b_v2/arm_readiness.receipts/arm-0001.json && .venv/bin/python scripts/generate_arm_readiness.py arm --pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2 --arm-context "$(/bin/cat /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/d117_floor_qwen25_1p5b_v2/arm_readiness.t0.inputs/arm-context.json)" --window-custody-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody && test -f "$ARM_RECEIPT" && .venv/bin/python scripts/generate_arm_readiness.py verify --pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2 --arm-receipt "$ARM_RECEIPT"
```

After Ed’s personal PASS/GO inspection, E-10 is the sole honest consumption route. It atomically consumes then `execve`s the frozen foreground chain; success does not return and proves one capability consumption, not a mock launch. Likely refusal: expired/already-consumed arm, binding mismatch, or chain precondition.

```sh
cd /Users/edr/JouleWise-measurement-20260818 && ARM_RECEIPT=/Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/d117_floor_qwen25_1p5b_v2/arm_readiness.receipts/arm-0001.json && LAUNCH_MANIFEST=/Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/d117_floor_qwen25_1p5b_v2/arm_readiness.t0.inputs/launch-manifest.json && .venv/bin/python scripts/launch_window.py --pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2 --arm-receipt "$ARM_RECEIPT" --arm-readiness-custody-root /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody --launch-manifest "$LAUNCH_MANIFEST"
```

## 11. Restore and reset for retry

Restore network time immediately after the final step, including a refusal; expected final line is `Network Time: On`. Then, only for a clean retry, remove exactly the three no-clobber T-0 namespaces. Likely refusal on restore is a broken D-127 sudoers vector and requires Ed intervention.

```sh
/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on && /usr/sbin/systemsetup -getusingnetworktime
```

```sh
/bin/rm -r -- /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/d117_floor_qwen25_1p5b_v2/arm_readiness.t0.sources /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/d117_floor_qwen25_1p5b_v2/arm_readiness.evidence /Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal/arm-readiness-custody/d117_floor_qwen25_1p5b_v2/arm_readiness.t0.inputs
```
