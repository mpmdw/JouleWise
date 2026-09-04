# Contract-lens refuter on 63d12162 (luna xhigh, direct run), verbatim

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "HEAD matches 63d12162; contract review complete; cold gate is NOT LANDABLE.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "informational",
    "head_start": "63d121625916a7f4f4a8e454a0fb1d8efc50491c",
    "head_end": "63d121625916a7f4f4a8e454a0fb1d8efc50491c",
    "upstream_end": "acd72a301c7ed66863e4c5bfef98250ffef49d4d",
    "branch": "feat/2026-09-03-magistrate-watchdog"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "landing": "NOT LANDABLE",
    "diff_stat": "6 files, 2283 insertions",
    "r7_email_path": "none in watchdog/installer; only prompt and allowed-tool references",
    "bridge": "no danger-full-access or sandbox bypass; Codex tools are bridge-gated",
    "findings": [
      {"id":"F1","severity":"blocker","title":"notice acknowledgment race","evidence":"Resident step returns _finish_child on exit at scripts/magistrate_watchdog.py:1058-1064 before consume_notice_ack at :1064. Independent temp-harness reproduction left notice_pending populated and notice.ack present after child exit."},
      {"id":"F2","severity":"blocker","title":"resident resolution can exceed 10 seconds","evidence":"step() calls git_probe() at :1073 before plan enforcement at :1080; remote_stop_probe performs two subprocess calls with timeout=10 at :364-369. This contradicts row 4's resident <=10 s guarantee."},
      {"id":"F3","severity":"should_fix","title":"stop glob differs from adopted ruling","evidence":"Code/docs use refs/heads/ops/stop* at scripts/magistrate_watchdog.py:59 and MAGISTRATE_WATCHDOG.md:53, while file 15 row 6 requires refs/heads/ops/stop-magistrate*."},
      {"id":"F4","severity":"should_fix","title":"first-use/install rehearsal is not replicable","evidence":"MAGISTRATE_WATCHDOG.md:89-101 has no runnable fake-plan t0=now+10 procedure and only generically requests the no-TTY and twin-adoption bench; :83-85 does not identify the ruled twin test."},
      {"id":"F5","severity":"should_fix","title":"resident path omits clock uncertainty handling","evidence":"clock_uncertain is used by tick/decide (:737-744), but resident step (:1058-1111) uses wall time without that check while enforcing plan deadlines."},
      {"id":"F6","severity":"nit","title":"write inventory omits transient atomic files","evidence":"Storage.atomic_bytes creates .<name>.<pid>.<uuid>.tmp at scripts/magistrate_watchdog.py:233-249, absent from MAGISTRATE_WATCHDOG.md:65-79."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/private/tmp/wd-pyc-$$ python3 -m unittest tests.test_magistrate_watchdog -v","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 33 tests in 0.070s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 33 tests in .*\\n\\nOK"}},
    {"id":"V2","kind":"suite","cmd":"suite_tmp=\"$(mktemp -d /private/tmp/wd-suite.XXXXXX)\"; TMPDIR=\"$suite_tmp\" PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=\"$suite_tmp/pyc\" python3 -m unittest discover -s tests","cwd":".","observed":{"result":"fail","exit_code":130,"tail":["KeyboardInterrupt","tests/test_calibration_writer_crash_matrix.py:1558"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V3","kind":"inspection","cmd":"git diff --check origin/main -- scripts/magistrate_watchdog.py scripts/install_magistrate_watchdog.sh configs/launchd/com.joulewise.magistrate.plist.template docs/process/MAGISTRATE_RELAUNCH_PROMPT.md docs/process/MAGISTRATE_WATCHDOG.md tests/test_magistrate_watchdog.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V4","kind":"smoke","cmd":"review_tmp=\"$(mktemp -d \"${TMPDIR:-/tmp}/wd-review-render.XXXXXX\")\"; scripts/install_magistrate_watchdog.sh --render-only \"$review_tmp/render\"; /usr/bin/plutil -lint \"$review_tmp/render/com.joulewise.magistrate.plist\"","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["rendered plist","plist: OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}}
  ],
  "flags": [
    {"id":"G1","kind":"baseline_drift","level":"nonblocking","text":"origin/main advanced during review from 8ed652f7 through 0f80c98a to acd72a30; final stat was recomputed against the ending ref.","needs":"Freeze or recompute the baseline if an immutable comparison is required."},
    {"id":"G2","kind":"verification_gap","level":"nonblocking","text":"Canonical discovery was interrupted after a broader calibration failure/hang; no install, launchd start, or twin-session bench was performed per hard rules.","needs":"Lead reruns the canonical suite and performs the mandated temporary first-use bench."}
  ]
}
```

## Findings

| Row | File 15 clause | Implementation / result |
|---|---|---|
| 1 | “Stand-down deadline and force owned by a launchd supervisor; … cooperative exit … preferred” | `:1022-1055`, `:1082-1095`; implemented. |
| 2 | “Spawn base `claude -p` (stream-json, one turn per activation…)” | `:76-91`, `:830-838`; plist `:24-27`; implemented. |
| 3 | “Inside a plan span the exact production `agent_census` … must be empty” | Census `:331-345`; span `:507-522`; liveness `:547-579`; implemented. |
| 4 | “REQUEST … t0 − 25 min; SIGTERM … −16; SIGKILL … −15 … resident … ≤10 s” | Constants/enforcement `:63-69`, `:1022-1055`; resident ordering violates ≤10 s (F2). |
| 5 | “never `killpg` alone: walk the process tree … unowned census … HOLDS” | `:841-874`, `:988-1020`; implemented. |
| 6 | “anonymous `git ls-remote` … positive-control … glob `refs/heads/ops/stop-magistrate*` … local STOP” | `:348-390`, `:1073-1075`; glob differs (F3). |
| 7 | “canonical checkout … plan-pin … MUST land before … REAL window” | `CANONICAL_REPO :53`, spawn cwd `:1162`, prompt `:9-11`; procedural, implemented. |
| 8 | “heartbeat file first, then launch email; stand-down email last act … one notice per transition” | Prompt `:2-6,15-18`; transitions/ack `:606-692`; exit/ack race (F1). |
| 9 | “15/30/60/120/120 min with jitter … never inside a span” | `:72`, `:699-734`, `:760-797`; implemented. |
| 10 | “after gauntlet + this gate … FIRST stand-down kills … Terminal-hosted interactive twin” | Installer adoption `install...sh:60-113,168-194`; adoption/tree `:841-874,1224-1254`; mechanism exists, first-use proof missing (F4). |
| 11 | “arming outside … email-then-arm; Ed’s NO overrides” | Prompt `:10`, watchdog doc `:87`; implemented. |

Installer checks: KeepAlive refusal passes (`install_magistrate_watchdog.sh:39-42`); it neither reads nor stales `night_plan.json`; it adopts the installing ancestry with PID/start token and `O_EXCL` lock (`:60-113`, `:168-194`). R-7 passes: no repository code invokes email; Gmail appears only as session instructions/allowed tool.

## Residual risk

The focused suite, syntax/compile checks, diff check, and render/plist lint pass. Installed launchd behavior and the interactive twin kill remain unverified by design; the canonical suite requires a clean lead-controlled rerun.