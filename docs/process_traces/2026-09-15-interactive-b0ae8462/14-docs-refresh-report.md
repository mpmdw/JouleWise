```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Refreshed trace-supported activity blocks; remaining requested claims need a ruling on the trace-only evidence requirement.",
  "workspace": {
    "base_requested": "1f721fbf7b8f96b90c64c7fe576592e5dbda098a",
    "base_mode": "exact",
    "head_start": "1f721fbf7b8f96b90c64c7fe576592e5dbda098a",
    "head_end": "1f721fbf7b8f96b90c64c7fe576592e5dbda098a",
    "upstream_end": "1f721fbf7b8f96b90c64c7fe576592e5dbda098a",
    "branch": "docs/2026-09-15-session-refresh"
  },
  "pathspec": ["README.md", "RUN_STATE.md"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -B scripts/bridge scope-check --baseline .codex-bridge/baselines/mag-docs3-20260915.json --expect-digest sha256:dd738ff9f5a315718a334c45a481f135ad6c88a578f0d1856e9db5d0dbd793d7 --lease-id lease-5c12356dc4b3462fa960f20c33af75b0 --scope README.md RUN_STATE.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "\"verdict\":\"SCOPE_OK\""}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\nimport subprocess\nbase='1f721fbf7b8f96b90c64c7fe576592e5dbda098a'\nfor name,start,end in [('README.md',b'**Now (',b'\\n\\n**Status:**'),('RUN_STATE.md',b'**Current checkpoint:',b'\\n\\n**T38s (')]:\n old=subprocess.check_output(['git','show',base+':'+name]); new=Path(name).read_bytes()\n assert old[:old.index(start)]==new[:new.index(start.split(b':')[0])]\n assert old[old.index(end):]==new[new.index(end):]\nprint('PASS: all bytes outside the two activity blocks unchanged')\nassert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==base\nprint('PASS: HEAD unchanged')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: all bytes outside the two activity blocks unchanged", "PASS: HEAD unchanged"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: HEAD unchanged"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: The prompt supplies facts not located in the required trace records: approximately 4–5 windows/day, the quick CI tier, final A172/A173 heads 3a39c9ed/db013f4e, and the specific close-all-interactive-sessions/pre-staged-stub handoff. The records also describe remaining implementation and checks rather than exactly one review round. These claims were omitted under the explicit trace-only requirement. Three reviewers agreed on the core signal approach, but only two supported the adopted mask-free design.",
      "needs": "Provide trace pointers for these claims, or explicitly rule that the prompt itself is an authorized supplemental source. Recommendation: authorize the prompt as supplemental evidence while retaining the recorded distinction about reviewer convergence. Blocked work: completing those claims in both activity blocks."
    }
  ]
}
```

## Change

Updated the trace-supported portions only. No commit made. Exact hunks:

```diff
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -12 +12 @@
-**Now (2026-09-15):** the second attempt at the epoch-equivalence measurement night fired at 02:56 and was again refused by its own safety check before any measurement — this time not because an assistant was running (that check was clean) but because the machine was busy: a system file-event service was consuming two CPU cores, and the night refuses whenever the one-minute load is above 2.0. The refusal record was harvested and the night's scheduled agents removed; nothing is armed. Next: the queued schedule work that lets a window be armed at any quiet time of day (directive #337), and a fresh plan once the machine is quiet again.
+**Now (2026-09-15 evening):** the installer for scheduled measurement windows is being revised so interruptions cannot skip cleanup or change a completed result. Three independent reviewers agreed on the core approach; the lead adopted the design without signal blocking. Round 8b is in progress before review and a pull request, the proposed change for merging. The retry rules and the check that distinguishes idle assistant sessions from active work have passed review with their amendments applied. Automated testing is being shortened with six parallel test groups and one Python version on pull requests. Nothing is armed for automatic execution. Next: finish the installer review and merge; then shorten the delay from arming to measurement start toward ten minutes, once the timing work justifies each delay against the physical safety checks.
diff --git a/RUN_STATE.md b/RUN_STATE.md
--- a/RUN_STATE.md
+++ b/RUN_STATE.md
@@ -13 +13,5 @@
-**Current checkpoint: T38s (2026-09-15 ~05:50 PDT), the equivalence night `d079-epoch-25g83-derivation-n1-20260915` FIRED at 02:56 and was REFUSED at the gate on load average alone (2.55 > 2.0; agent census clean), harvested, agents uninstalled; NOTHING ARMED; INSTALL-WINDOWS-MULTI-01 released to agent rank 0.** Start with T38s below, the durable pointer's last UPDATE line in [00-DURABLE-STATE.md](docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md), and the harvest record [01](docs/process_traces/2026-09-15-activation-1acf2aee/01-equivalence-night-20260915-harvest-record.md). Every prior checkpoint remains verbatim.
+**Current checkpoint (2026-09-15 evening): NOTHING ARMED for automatic execution.** The transactional installer, which installs scheduled measurement agents with cleanup if installation fails, is on `feat/2026-09-15-install-windows-transactional` at `69d668be`, with round 8b in progress. Three independent reviewers agreed on recording interruption signals and checking them at explicit points; the lead adopted the two-reviewer design without signal blocking. Round 8b resolves the final cancellation check before success is recorded. Review, executed interruption checks, and replay still precede its pull request (PR), the proposed change for merging. Sources: [redesign adoption](docs/process_traces/2026-09-15-interactive-b0ae8462/13-consult-signal-redesign/03-magistrate-adoption.md), [round 8b ruling](docs/process_traces/2026-09-15-interactive-b0ae8462/08j-round-8b-ruling-commit-latch.md), and [recorded installer head](docs/process_traces/2026-09-15-activation-08ca8197/02-lead-margin-lane-registration.md).
+
+The retry-rule work, A172 on `feat/2026-09-15-arm-retry-class`, and the idle-session check, A173 on `feat/2026-09-15-arm-census-idle`, have passed review with amendments applied ([retry amendments](docs/process_traces/2026-09-15-interactive-b0ae8462/03j-a172-fix-round-3-report.md), [idle-session amendments](docs/process_traces/2026-09-15-interactive-b0ae8462/04l-a173-fix-round-3-bench.md)). Continuous integration (CI), the automated checks on proposed and merged changes, is being shortened in PR #340: six parallel test groups and one Python version on pull requests; hosted verification remains outstanding ([six groups](docs/process_traces/2026-09-15-interactive-b0ae8462/10b-ci-trim-2-astra-report.md), [interpreter selection](docs/process_traces/2026-09-15-interactive-b0ae8462/10c-ci-trim-2-step2-dedupe-report.md)).
+
+Next: finish the installer implementation and review. A210, the work to shorten the delay between arming and measurement start, depends on that merge and targets about ten minutes. It is registered only: no timing constant has changed, each proposed delay needs physical justification, and the checks at measurement start stay unchanged ([A210 registration and amendment](docs/process_traces/2026-09-15-activation-08ca8197/02-lead-margin-lane-registration.md)). The unattended lead assistant holds until the interactive session hands back the installer lane; any successor window must follow the notice-and-arm procedure with a clear assistant census and acceptable machine load ([handoff record](docs/process_traces/2026-09-15-activation-08ca8197/00-launch-record.md)). Every prior checkpoint remains verbatim.
```

## Verification notes

Used byte-preservation and scope checks for this documentation-only edit; no test suite or hardware operation ran. Completion awaits the evidence-source ruling in F1.