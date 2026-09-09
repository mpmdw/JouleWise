```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "F1–F4 are closed in the requested two-file delta; same signature: none.",
  "workspace": {
    "base_requested": "70d71f77",
    "base_mode": "exact",
    "head_start": "191f4c43b0364b63c72574989a89b37fe3245452",
    "head_end": "191f4c43b0364b63c72574989a89b37fe3245452",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; from decimal import Decimal; import hashlib,json,re; p=Path(\"docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest\"); sums=[x.split(maxsplit=1) for x in (p/\"SHA256SUMS\").read_text().splitlines()]; assert len(sums)==17; assert all(hashlib.sha256((p/n).read_bytes()).hexdigest()==h for h,n in sums); print(\"SHA256SUMS: 17/17\"); obs=(p/\"pre-uninstall-observations.txt\").read_text(); state=json.loads(obs[obs.index(\"{\\n\"):],parse_float=Decimal); sample=state[\"last_clock\"][\"epoch_s\"]; uninstall=re.search(r\"uninstall run at (\\d+)\",(p/\"uninstall-output.txt\").read_text()).group(1); removal=re.search(r\"removal at (\\d+)\",(p/\"removal-output.txt\").read_text()).group(1); print(f\"watchdog={sample}; uninstall={uninstall}; difference={Decimal(uninstall)-sample}; removal={removal}\"); lines=(p/\"night.log\").read_bytes().splitlines(keepends=True); recorded=next(a[\"sha256\"] for a in json.loads((p/\"night-result.json\").read_text())[\"artifacts\"] if a[\"path\"]==\"night.log\"); digest=lambda b:hashlib.sha256(b).hexdigest(); assert digest(b\"\".join(lines[:2]))==recorded; print(\"first-two sha256=\"+recorded); print(\"full sha256=\"+digest(b\"\".join(lines))); print(f\"log lines={len(lines)}; subsequent lines={len(lines)-2}\"); print(b\"\".join(lines[2:]).decode(),end=\"\"); print(\"heartbeat \"+(p/\"night-courier.heartbeat\").read_text().splitlines()[0]); print(\"sent \"+next(x for x in (p/\"night-courier.sent\").read_text().splitlines() if x.startswith(\"courier_pid=\")))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SHA256SUMS: 17/17",
          "watchdog=1788950204.064847; uninstall=1788950218; difference=13.935153; removal=1788950258",
          "first-two sha256=f894b3a4d731e3a794795251fb596b442cb498964ea468c307346f0bee5bae13",
          "full sha256=28ee7ad60ea6c45a584398266cf8b8c93cb15eb096da7d0b5d39c619d680e57a",
          "log lines=6; subsequent lines=4",
          "2026-09-09T02:56:03.367167-07:00 night result verdict=REHEARSAL_ONLY",
          "2026-09-09T02:56:10.980604-07:00 durable record pushed branch=night-results/20260909",
          "2026-09-09T02:57:33.117809-07:00 courier attempt=1 heartbeat=True sent=True",
          "2026-09-09T02:57:35.070205-07:00 durable record pushed branch=night-results/20260909",
          "heartbeat pid=82210",
          "sent courier_pid=82210"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "sent courier_pid=82210"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git merge-base --is-ancestor 5db38b58 HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 1, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --porcelain; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["191f4c43b0364b63c72574989a89b37fe3245452"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "191f4c43b0364b63c72574989a89b37fe3245452"
      }
    }
  ],
  "flags": []
}
```

## Findings

No surviving findings. **same signature: none**.

**F1 — N7 ordering: closed.** The replacement explicitly labels copy ordering **INFERRED**, disclaims a captured copy-command transcript, and distinguishes the watchdog sample from copy time. V1 independently recomputed:

```text
SHA256SUMS: 17/17
watchdog=1788950204.064847; uninstall=1788950218; difference=13.935153; removal=1788950258
```

The raw removal artifact records:

```text
== removal at 1788950258 Wed Sep  9 03:37:38 PDT 2026
...
-- plan root remove
plan root removed rc=0
```

Thus the text accurately attributes the removal epoch to the record; it does not use that timestamp to establish copy ordering.

**F2 — N4 digest: closed.** V1 hashes the original bytes, retaining line endings. The first two lines match the digest inside `night-result.json`; all six match the manifest:

```text
first-two sha256=f894b3a4d731e3a794795251fb596b442cb498964ea468c307346f0bee5bae13
full sha256=28ee7ad60ea6c45a584398266cf8b8c93cb15eb096da7d0b5d39c619d680e57a
log lines=6; subsequent lines=4
2026-09-09T02:56:03.367167-07:00 night result verdict=REHEARSAL_ONLY
2026-09-09T02:56:10.980604-07:00 durable record pushed branch=night-results/20260909
2026-09-09T02:57:33.117809-07:00 courier attempt=1 heartbeat=True sent=True
2026-09-09T02:57:35.070205-07:00 durable record pushed branch=night-results/20260909
```

All four timestamps match exactly. The replacement removes unsupported courier authorship.

**F3 — record note: closed.** “Once … lands” and “will cover” correctly make the cure prospective.

Command:

```sh
git cat-file -t 5db38b58
grep -n 'probes.read_text(plan.chain_path)' joulewise/night_gate.py
sed -n '1020,1065p' joulewise/night_gate.py
```

Relevant output:

```text
commit
1046:        chain_text = probes.read_text(plan.chain_path)
```

```python
    if census_refusal is not None:
        return _finish(plan, probes, rows, census_refusal)

    # The chain and sidecar are read as text by the injected adapter; UTF-8 is
    # the ruled byte representation for hashing text observations.
    try:
        chain_text = probes.read_text(plan.chain_path)
        sidecar_text = probes.read_text(plan.chain_sha256_path)
```

The read is **not under a `receipt_class` branch** at this head. Earlier refusal paths can return, but reaching this block triggers the reads regardless of receipt class.

Commands:

```sh
git show 83ab38ed:joulewise/night_gate.py | sed -n '1035,1054p'
git show 5db38b58:joulewise/night_gate.py | sed -n '1025,1090p'
git merge-base --is-ancestor 5db38b58 HEAD
```

The pinned `83ab38ed` source has the same unconditional reads. The cure source instead contains:

```python
    if plan.receipt_class == "REHEARSAL_STUB":
        rows["C5"].measured.update(
            {
                "chain_path": plan.chain_path,
                "chain_sha256_path": plan.chain_sha256_path,
                "chain_sha256": None,
                "expected_chain_sha256": None,
                "chain_stub": "built_in_stub_by_design",
            }
        )
    else:
```

Chain reads and `night_chain_digest_mismatch` handling sit beneath that `else`. The ancestry command exits **1**, confirming the cure commit is not an ancestor of this head.

Additional source checks:

```sh
sed -n '1562,1575p' scripts/run_night.py
rg -n 'fix/2026-09-09-night-gate-stub-chain' docs/process_traces/2026-09-09-rehearsal-harvest/17-seat-fix1-night-gate-stub-astra-report.md
rg -n '309' docs/process_traces/2026-09-09-rehearsal-harvest/24-brief-kernel-fold-part2-astra.md
```

Relevant output:

```text
command = ["/bin/zsh", "-c", "sleep 2; echo REHEARSAL"]
14:    "branch": "fix/2026-09-09-night-gate-stub-chain"
20:F3: the cure evidence directory is outside this branch by design (it lands with the cure PR #309); keep the kernel evidence pointer to the
21:branch/commit form you used and add "PR #309" to the NIGHT-GATE-STUB-CHAIN-01 row's evidence label.
```

The branch and PR number have documentary corroboration, as required by the fix brief.

**F4 — pid attribution: closed.** V1 directly reads both primary markers:

```text
heartbeat pid=82210
sent courier_pid=82210
```

The changed sentence now states only that the markers record this pid. It makes no process-type claim.

## Residual risk

The complete range includes 31 additional trace files beyond the two requested review targets. Those additions were not substantively audited; supporting traces were consulted only for the specified closures.

No files changed. HEAD remained unchanged and the workspace clean. No suite or live measurement ran for this documentary review. The next step is the lead’s final contextual review.