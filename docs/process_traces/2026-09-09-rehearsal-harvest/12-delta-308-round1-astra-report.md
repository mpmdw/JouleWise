```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F1, F3 and F4 cured; F2 not fully cured because the reconciliation introduces an unsupported completed-cure claim.",
  "workspace": {
    "base_requested": "20f95848",
    "base_mode": "exact",
    "head_start": "1f4c4492f6956886979c06b9e2a627de5296eb87",
    "head_end": "1f4c4492f6956886979c06b9e2a627de5296eb87",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"blocker","disposition":"cured","summary":"All 17 manifest entries match committed blobs; all three logs are tracked."},
      {"id":"F2","severity":"should_fix","disposition":"not cured","summary":"Execution reconciliation is supported except its new assertion that NIGHT-GATE-STUB-CHAIN-01 has cured the defect; 21i records that cure as pending."},
      {"id":"F3","severity":"should_fix","disposition":"cured","summary":"Revised census wording matches the empty foreign/informational lists and production MCP PIDs 83123/83143."},
      {"id":"F4","severity":"nit","disposition":"cured","summary":"PARTIAL accurately distinguishes recorded send from unverified inbox receipt."}
    ],
    "same_signature": "F2: new unsupported completed-cure claim"
  },
  "verification": [
    {
      "id":"V1",
      "kind":"inspection",
      "cmd":"cd docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest && shasum -a 256 -c SHA256SUMS",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["night.log: OK","night_plan.json: OK","pre-uninstall-observations.txt: OK"]},
      "expected":{"exit_code":0,"tail_regex":"pre-uninstall-observations.txt: OK"}
    },
    {
      "id":"V2",
      "kind":"inspection",
      "cmd":"git ls-files 'docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest/*.log'",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest/night-chain.stderr.log","docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest/night-chain.stdout.log","docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest/night.log"]},
      "expected":{"exit_code":0,"tail_regex":"night.log"}
    },
    {
      "id":"V3",
      "kind":"inspection",
      "cmd":"python3 -B -c 'import subprocess,hashlib; from pathlib import Path\nbase=\"20f95848\"; head=\"1f4c4492\"\ndef blob(rev,path): return subprocess.check_output([\"git\",\"show\",rev+\":\"+path],stderr=subprocess.DEVNULL)\np=\"docs/process/NIGHT_HANDBACK.md\"; a,b=blob(base,p),blob(head,p); marker=b\"**Standing rules** <!-- F11 -->\"\nassert a[a.index(marker):]==b[b.index(marker):]\nprint(\"standing-rules block: byte-identical\")\nstart=b.index(b\"## Executed \"); end=b.index(b\"## Where the results are\",start)\nassert a==b[:start]+b[end:]\nprint(\"existing handback text: byte-identical after removing added reconciliation\")\nd=\"docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest/\"; rows=blob(head,d+\"SHA256SUMS\").decode().splitlines()\nfor row in rows:\n sha,name=row.split(maxsplit=1); name=name.lstrip(\"*\"); raw=blob(head,d+name)\n assert hashlib.sha256(raw).hexdigest()==sha,name\n assert Path(d+name).read_bytes()==raw,name\nprint(f\"committed manifest: {len(rows)}/{len(rows)} hashes match; disk bytes equal committed blobs\")'",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["standing-rules block: byte-identical","existing handback text: byte-identical after removing added reconciliation","committed manifest: 17/17 hashes match; disk bytes equal committed blobs"]},
      "expected":{"exit_code":0,"tail_regex":"committed manifest: 17/17 hashes match"}
    },
    {
      "id":"V4",
      "kind":"inspection",
      "cmd":"rg -n 'cured by|CONDITIONAL on NIGHT-GATE|Cure lane registered|NIGHT-GATE-STUB-CHAIN-01' docs/process/NIGHT_HANDBACK.md docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md:56:   CONDITIONAL on NIGHT-GATE-STUB-CHAIN-01 landing; whether a second stub night is required after the cure is a ruling for the cold","docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md:60:1. NIGHT-GATE-STUB-CHAIN-01: seat in a linked worktree off main — gate-side cure (skip the chain/sidecar read for `REHEARSAL_STUB`," ]},
      "expected":{"exit_code":0,"tail_regex":"NIGHT-GATE-STUB-CHAIN-01"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — cured.** Checksum command returned **17/17 OK**. `git ls-files` confirms all three logs are tracked; independent hashing of `git show 1f4c4492:<path>` confirms every manifest hash and equality with disk bytes. V1–V3 provide the command tails.

**F2 — not cured; new defect within the reconciliation.** `docs/process/NIGHT_HANDBACK.md:83–84` says “a finding, cured by NIGHT-GATE-STUB-CHAIN-01.” Its cited 21i instead says:

```text
Cure lane registered below as NIGHT-GATE-STUB-CHAIN-01.
CONDITIONAL on NIGHT-GATE-STUB-CHAIN-01 landing
```

The delta supplies no completed-cure artifact. Change this to “cure pending under NIGHT-GATE-STUB-CHAIN-01,” or cite evidence establishing completion.

The remaining execution facts trace to 21h/21i and harvest artifacts: activation and frozen triple, firing time, verdict, exit code, results commit, courier ID, refusal mechanism, uninstall/removal, and canonical-only frozen list. Relevant captured command tails include:

```text
results-clone pushed and clean
worktree removed rc=0
plan root removed rc=0
```

V3 proves the standing-rules block—and all pre-existing handback text—is byte-identical. The added procedural reminders restate existing requirements; no standing rule is added.

**F3 — cured.** `arm-blockB-output.txt` explicitly records:

```text
foreign agent sessions (cond. 5, must be empty): []
informational matches (Ed's ChatGPT.app tree / substring false positives): []
production agent_census argv output (pgrep exit 0) — recorded, not gating the arm:
```

The following process rows identify **83123/83143**, matching the revised wording exactly.

**F4 — cured.** `night-courier.sent` records:

```text
message_id=1a08599a4ff4d005
thread_id=1a08599a4ff4d005
sent_epoch_s=1788947852
```

The revised **PARTIAL** status and message ID accurately reflect send evidence without claiming inbox receipt.

**Same signature: F2 introduces a claim without a supporting artifact (“cured by”).** No new hash, ID, or epoch mismatch found.

## Residual risk

Coverage is limited to the requested delta and historical artifacts. No fresh remote, inbox, or live-machine validation was performed. No files changed; HEAD remained unchanged.