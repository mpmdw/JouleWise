```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "S2 and watchdog-sequence S4 are addressed; N4, N7, the b149cf80 record note, and S3's shell attribution need correction.",
  "workspace": {
    "base_requested": "1b56c9d2",
    "base_mode": "exact",
    "head_start": "70d71f778d8b5f29ea7c58b4bf1355ab8db2dbd6",
    "head_end": "70d71f778d8b5f29ea7c58b4bf1355ab8db2dbd6",
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
        "item": "N7",
        "path": "docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md",
        "line": 48,
        "summary": "The embedded watchdog clock does not establish when the harvest copies were made; the same-command assertion remains uncaptured."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "item": "N4",
        "path": "docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md",
        "line": 15,
        "summary": "The result digest covers two log lines, so four subsequent appends explain the difference, not the two stated courier lines."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "item": "b149cf80 record note",
        "path": "docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md",
        "line": 81,
        "summary": "The note describes the separate cure as present behavior, but this head still performs unconditional chain-identity reads for REHEARSAL_STUB."
      },
      {
        "id": "F4",
        "severity": "nit",
        "item": "S3",
        "path": "docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md",
        "line": 657,
        "summary": "The artifacts establish recorded pid 82210, but do not establish that it is a shell pid."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; import json,hashlib; p=Path(\"docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest\"); rows=[x for x in (p/\"watchdog-events-excerpt.txt\").read_bytes().splitlines() if x.startswith(b\"{\")]; source=Path(\"/Users/edr/night-custody/magistrate/events.jsonl\").read_bytes().splitlines(); assert len(rows)==24 and all(x in source for x in rows); print(\"excerpt subset: 24/24\"); sums=[x.split(maxsplit=1) for x in (p/\"SHA256SUMS\").read_text().splitlines()]; assert len(sums)==17 and all(hashlib.sha256((p/n).read_bytes()).hexdigest()==h for h,n in sums); print(\"SHA256SUMS: 17/17\"); data=(p/\"night.log\").read_bytes().splitlines(keepends=True); result=json.loads((p/\"night-result.json\").read_text()); h=next(x[\"sha256\"] for x in result[\"artifacts\"] if x[\"path\"]==\"night.log\"); assert hashlib.sha256(b\"\".join(data[:2])).hexdigest()==h; assert hashlib.sha256(b\"\".join(data[:-2])).hexdigest()!=h; print(\"result log digest: first 2 of 6 lines; 4 later appends\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "excerpt subset: 24/24",
          "SHA256SUMS: 17/17",
          "result log digest: first 2 of 6 lines; 4 later appends"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "result log digest: first 2 of 6 lines; 4 later appends"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "sed -n '1036,1054p' joulewise/night_gate.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "        return _probe_refusal(plan, probes, rows, evidence, exc)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "return _probe_refusal"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["70d71f778d8b5f29ea7c58b4bf1355ab8db2dbd6"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "70d71f778d8b5f29ea7c58b4bf1355ab8db2dbd6"
      }
    }
  ],
  "flags": []
}
```

## Findings

1. **F1 — N7 remains open; same signature: claim without artifact.** Quote: “was written in the same command as the byte copies”. The captured `last_clock.epoch_s` is **1788950204.064847**, preceding uninstall **1788950218** by 13.935 seconds. That dates the watchdog’s clock sample, not the copy operation. Neither artifact contains the asserted command or its execution timestamp. Capture the original transcript, or explicitly label harvest-before-uninstall as inferred.

2. **F2 — N4 explanation is incorrect.** Quote: “because the courier appended two lines after the result was sealed”. V1’s tail establishes **“result log digest: first 2 of 6 lines; 4 later appends”**. The additional lines are at 02:56:03, 02:56:10, 02:57:33 and 02:57:35. The result digest is exactly the first two lines’ digest; deleting only the final two does not reproduce it. Describe all four driver-log appends.

3. **F3 — b149cf80 needs explicit post-cure qualification.** Quote: “the night gate performs NO chain-identity check”. At this head, `evaluate_night` still unconditionally reads the chain and sidecar at lines 1046–1047. The note also conflicts with 21i’s own diagnosis. Say this describes the separate cure once landed, naming its commit. This finding concerns the added prose, not S1’s excluded kernel fold.

4. **F4 — S3’s PID distinction passes, but “shell” is unsupported.** Seq-19 census stdout identifies **82106** running Claude with the night-courier prompt. Heartbeat and sent artifacts record **82210**. Neither identifies 82210’s process type. Replace “its shell pid 82210” with “pid 82210 recorded in its heartbeat and sent marker”.

Other item dispositions:

| Item | Disposition and evidence |
|---|---|
| **S4** | **Addressed.** All 24 excerpt JSON lines match source bytes. Sequences 9/12/13/16/17/19/20/21/22/23 are present. Spawn records name the correct activation IDs; intervening clean-exit transitions support their exit attribution. Seq 21’s actual epoch is `1788948173.967854`, consistent with the prose’s rounded `1788948174`. |
| **S2** | **Addressed as referral.** Relaunch-prompt clause 19(b), NIGHT_HANDBACK §Next lane, and D-175’s incorporated synthesis exist at this head. The paragraph names the relied-on authority and explicitly refers condition 8’s scope rather than settling it. |
| **N1** | **Addressed.** All three Gmail IDs and times match 21b; the notices dated September 8 precede the September 9 arm. |
| **N2** | **Addressed with stated limitation.** The transcript ends with `17`; no pre-count is claimed. The installer at pinned `ae8f074f` excludes custody creation during uninstall and only unloads jobs/removes their plists in that branch. |
| **N3** | **Addressed.** Captured launchctl status is `3`; code declares `EXIT_REFUSED = 3`. More precisely, the rehearsal-result branch itself returns that status, so it is consistent with, but not independent proof of, the refused receipt. |
| **N5** | **Addressed for this gate path.** Lines 1540–1542 suppress gate-refusal-file creation when rehearsal is effective. Other failure paths can write refusal files; avoid interpreting the sentence as a universal driver guarantee. |
| **N6** | **Addressed.** Seq 17 records clean exit at `1788945977.006024`, before deadline `1788946260`. |
| **Integrity** | V1 tail: `excerpt subset: 24/24`; `SHA256SUMS: 17/17`. Workspace remained clean and HEAD unchanged. |

## Residual risk

S1 and unrelated preserved trace files were not substantively re-audited. No suite or live measurement ran for this read-only documentary review. The lead retains the condition-8 ruling and final verification; next step is correcting F1–F4.