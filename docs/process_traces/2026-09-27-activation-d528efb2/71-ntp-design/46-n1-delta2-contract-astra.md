```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Contract re-audit found five should-fix gaps; no repository edits or live D1 reproduction.",
  "workspace": {
    "base_requested": "3ad82b43",
    "base_mode": "descendant",
    "head_start": "36e8ba6e345653e4fb4ac54f711dc49b27c1d30c",
    "head_end": "36e8ba6e345653e4fb4ac54f711dc49b27c1d30c",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "file": "joulewise/network_time_window.py:384",
        "summary": "Missing pid/pgid fields qualify as explicit nulls, bypassing the capture proof."
      },
      {
        "id": "R2",
        "severity": "should_fix",
        "file": "scripts/run_night.py:3925",
        "summary": "P2 inherits a batch-census path that accepts exit-zero empty output as absence."
      },
      {
        "id": "R3",
        "severity": "should_fix",
        "file": "scripts/run_night.py:3531",
        "summary": "E2 still leaves refusal.json and result.json naming different causes when cleanup wrote the first refusal."
      },
      {
        "id": "R4",
        "severity": "should_fix",
        "file": "scripts/run_night.py:3964",
        "summary": "The first proof pass can exceed five seconds and still return proved."
      },
      {
        "id": "R5",
        "severity": "should_fix",
        "file": "scripts/run_night.py:3475",
        "summary": "The earlier C7 refusal path still exits with courier-failed status 6 instead of refusal status 3."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/ntp-n1delta2-astra PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_network_time_window",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 48 tests in 0.238s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "TMPDIR=/tmp/ntp-n1delta2-astra PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/ntp-n1delta2-astra/probe_contract.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CLAIM missing_both driver_accepts= True recovery= restored ON= True",
          "CLAIM missing_pid driver_accepts= True recovery= restored ON= True",
          "CLAIM complete driver_accepts= True recovery= restored ON= True",
          "P2_EMPTY_SUCCESS (True, {'checks': ['P1', 'P2', 'P3']})",
          "FIRST_PASS_BOUND (True, {'checks': ['P1', 'P2', 'P3'], 'passes': 1}) elapsed= 5.4 window= 5",
          "PURE_CONTRACT_PROBES_COMPLETE"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PURE_CONTRACT_PROBES_COMPLETE"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "TMPDIR=/tmp/ntp-n1delta2-astra PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/ntp-n1delta2-astra/probe_refusal.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "K_RESULT None",
          "REFUSAL refusal-01.json night_chain_alive",
          "REFUSAL refusal.json night_probe_error",
          "RESULT REFUSED night_chain_alive ['night/refusal-01.json', 'night/refusal.json']",
          "C7_EXIT 6",
          "PURE_REFUSAL_PROBE_COMPLETE"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PURE_REFUSAL_PROBE_COMPLETE"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp/ntp-n1delta2-astra PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/ntp-n1delta2-astra/audit_assertions.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ASSERTION_CENSUS_COMPLETE"]
      },
      "expected": {"exit_code": 0, "tail_regex": "ASSERTION_CENSUS_COMPLETE"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check 3ad82b43 36e8ba6e",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This contract lens used injected process responses and commands. Live process tests, mutation runs and adversarial child topologies belong to the separate executing auditor.",
      "needs": "Combine this report with the independent execution audit before acceptance."
    }
  ]
}
```

DELTA: FINDINGS

## Findings

No BLOCKER established by this seat. Five SHOULD-FIX findings follow. Diagnostic probes completed successfully; their outputs demonstrate the contract gaps, not passing contract assertions.

**R1 — SHOULD-FIX: the never-launched exception accepts missing identity fields.**

At `joulewise/network_time_window.py:384` and `scripts/run_night.py:3553`, `.get(...) is None` treats an absent key as an explicit JSON null. A1 §5 requires both `pid` and `pgid` to be null.

Executed with `chain.started = {"popen_attempted": false}` and `chain.exited = {"launch_failed": true}`: the driver helper accepted the claim; recovery returned `restored` and invoked injected ON without any capture proof. A claim missing only `pid` also passed.

Require both keys to exist and contain null. Complete production claims already satisfy this. [Replay](/tmp/ntp-n1delta2-astra/probe_contract.py).

**R2 — SHOULD-FIX: P2 can count an unanswered census as proof.**

The new proof calls `_group_census_batch` at `scripts/run_night.py:3925`. Its inherited `_census_chunk` accepts exit-zero empty output: it reaches attribution with no PIDs and ultimately marks every requested group absent (`:3760–3775`).

With two registered groups, an injected exit-zero/empty batch listing, and clear P1/P3, `_capture_proof_pass` returned `True`. This contradicts the ruled census semantics: only exit status 1 with empty output proves absence. The attribution helper also ignores its command’s return code (`:3784–3797`).

Make these ambiguous/error responses unproved. This is an inherited helper defect newly used by P2, not an executed live D1 case. [Replay](/tmp/ntp-n1delta2-astra/probe_contract.py).

**R3 — SHOULD-FIX: E2 fixes the watchdog case but misses a refusal written by [K].**

The moved `_evidence_cleanup_error` can write `refusal.json` as `night_probe_error` when an idle chain leaves no outcome (`scripts/run_night.py:1413–1424`). A subsequent P3 failure has no prior abort mapping, so `_capture_unproved_abort` cannot discover that document (`:3531`). Result preparation allocates a numbered refusal (`:3417`).

Executed through these production helpers with injected cleanup:

- `refusal.json`: `night_probe_error`
- `refusal-01.json`: `night_chain_alive`
- `result.json`: REFUSED / `night_chain_alive`

Thus item 118’s requirement that both records carry the proof failure is not fully implemented. Reconcile the existing primary refusal while preserving its earlier cause. [Replay](/tmp/ntp-n1delta2-astra/probe_refusal.py).

**R4 — SHOULD-FIX: the five-second limit excludes the first pass.**

At `scripts/run_night.py:3964`, the budget check applies only after a completed pass. At `:3968`, success is accepted without checking the deadline.

A virtual-clock probe with 769 registered groups and successful 0.9-second listings returned **proved after 5.4 seconds**. There is no enforced registry-size cap. The documented bound `max(5 seconds, first-pass budget)` therefore exceeds A1 §4.2. [Replay](/tmp/ntp-n1delta2-astra/probe_contract.py).

**R5 — SHOULD-FIX: an earlier group refusal still returns the wrong exit status.**

When C7 cannot prove the chain group absent, `scripts/run_night.py:3475` returns `_finish_reporting(..., allow_courier=False)`, which returns **6**, `EXIT_COURIER_FAILED` (`:1907`). The new status override at `:3497` is bypassed. The new same-group test explicitly expects 6 (`tests/test_run_night.py:1161`).

This is inherited behavior, but A1 §4.2 requires the refusal status, **3**, when capture absence is unproved. Preserve C7’s termination and exit-record semantics while resolving the outward status. The lead should reconcile any existing status assertions with §7.2 before changing them. The reporting helper’s return was confirmed without launching a courier.

| A1 clause | Disposition |
|---|---|
| C1 — proof and listing seam | Implemented at `run_night.py:3807,3913,3939`; R2 and R4 remain. |
| C2 — gate query and ON | Both require termination plus capture proof; proof repeats before ON (`:3345–3381`). R1 affects the exception; R5 affects the earlier refusal status. |
| C3 / §4.3 [K] ordering | Correct: cleanup precedes proof (`:3346`); later reporting cleanup remains (`:1453`). Its saved answer does not authorize query/ON. R3 concerns its refusal side effect. |
| C4 — three recovery calls | All inject `_recovery_capture_proof`: `:3032,3562,3649`. |
| C5 — recovery authorization | Known group requires injected proof; missing proof and exceptions refuse. Rechecked before ON (`network_time_window.py:390–416`). R1 affects unknown identities. |
| C6 — marker paths | Written before OFF; all three written/resolved paths retained (`network_time_window.py:96–118`). Legacy markers retain P1/P2 and sampler-name checking. |
| C7 — existing termination meaning | Termination routines and exit-record meaning preserved. R5 concerns the surrounding return path. |
| §4.2 — fresh evidence, no saved proof | Fresh censuses and sweep at each authorization. Registry reread per pass. Exit/cleanup records do not replace proof for known groups. |
| §4.2 — cannot answer ⇒ unproved | P1, registry parsing and P3 fail closed; batch P2 has R2. |
| §4.2 — exclusions and signatures | Driver, ancestors and listing child excluded; sampler basename and written/resolved path matching implemented (`run_night.py:3822–3872`). |
| §4.2 — failure record | Check evidence retained and new proof failures use `night_chain_alive`; R3 and R5 remain. |
| §5 — claim production and ordering | Both OFF-refusal branches perform immediate ON, complete the never-launched claim, then write the exit record (`:3296–3321`). |
| §5 — exact acceptance | Partial: R1. The remaining flag/string/exit-record conditions match. |
| §5 — empty/unreadable claim label | Correctly `chain_unproved`; marker parsing remains `marker_invalid`. |
| §6 D3 — positional regex | Matches the ruled pattern. Three payload attacks and preserved-log count regression pass in the 48-test module. |
| §6 D4 — stand-ins | Saved F1 replaced by real-child tests; relevant ON stand-ins return receipt mappings. |
| §7.2 — assertion preservation | No weakening found. Only saved F1 removed. Recovery seam assertions retain their expected outcomes; one test is renamed and changes the error label as the amendment requires. E3 changes fixtures. |
| §8 — N1 amendments | Wider proof, marker paths and recovery implemented subject to findings above. Chain-local ON/cleanup changes remain N3-owned. |
| §4.7 / §7.3 — live acceptance | Separate executing auditor owns verification. Writer’s P1-deletion caveat remains disclosed: C7 masks deletion in the driver case; recovery isolates P1. |

**E1 judgment.** Ending retries around 0.8 seconds with multiple registered groups is faithful to **“may be repeated for up to 5 s”**: the text grants a maximum, not a minimum retry duration. It can increase refusals. With exactly one registered group the reserved budget differs.

A better bound reserves one full listing timeout immediately before each listing, rather than reserving an entire worst-case pass. If the next listing cannot fit, stop unproved, retain the last complete failure evidence, and record deadline exhaustion. Check the deadline before accepting success, including the first pass. This preserves full listing timeouts while using more of the five-second window.

**E2 judgment.** The successful watchdog replacement itself is contract-safe under the recorded lead ruling: same-directory atomic replacement preserves the refusal schema and carries `prior_abort`. The normal result hashes the replacement afterward.

Consumers inspected were result artifact discovery/hashing (`run_night.py:1062,1671`), the courier’s refusal discovery (`docs/process/NIGHT_COURIER_PROMPT.md:10–15`), installer refusal detection (`night_agent_install.py:1231`), and retained-root classification (`evidence_night.py:806–815`). No schema, path or normal-order hash consumer breaks from successful replacement. **R3 means E2 is nevertheless incomplete.**

## Residual risk

No process listing, live child, machine-setting command, system-log query, battery read or Claude call was executed. Repository files remain unchanged.

For production-shaped claims and ordinary process responses, reading found no direct driver/recovery route around P1/P2/P3. R1 does expose a malformed-claim route that bypasses all three; it was tested only with injected commands, not a live signature-bearing survivor. This seat therefore does **not** establish §7.4’s executed D1 trigger.

The unchanged chain-local route still restores ON before cleanup at `joulewise/quiet_predicate_campaign.py:1767–1768`. A1 §8 explicitly assigns that known ordering defect to N3; N1’s driver proof cannot repair an ON already performed inside the chain.

Next: lead adjudication of R1–R5, combined with the separate live execution audit.