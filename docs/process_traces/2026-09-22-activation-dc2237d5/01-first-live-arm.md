# 01 — First live arm through the tracked entry point (activation dc2237d5, 2026-09-22)

Headless magistrate activation `dc2237d5-83ea-4593-9bfd-67ff1dca8694`, launched
01:56:15 PDT 09-22 by the watchdog after activation 32fd437d exited (the
headless runner's 600 s background-task ceiling terminated it while it waited on
a full test suite; the watchdog classed the exit `usage_exhausted`). Canonical
checkout `/Users/edr/code/JouleWise` clean at `d45378c6` = `origin/main`
throughout; not moved by this activation.

## What happened, in order (all times PDT 09-22)

| Time | Step | Result |
|---|---|---|
| 01:36 (32fd437d) | `prepare --kind quiet_predicate_evidence --t0 next` | staging `qpe01-pilot-n1-20260922-0217-…-d45378c6…`, t0 02:17:00, install close 02:07:00; 32fd437d never ran `check` |
| 01:57 | launch email (Gmail id `1a0c855e7b1cb27f`), `notice.ack` written | accepted |
| 01:58 | 32fd437d's dirty seat work preserved | WIP commits `dc0e58bc` (A265, branch `fix/2026-09-22-canonical-refusal-strings`) and `0aac5155` (A266, `docs/2026-09-22-arm-vocabulary-glossary`, record 02 still carries `FULL_SUITE_PLACEHOLDER`), both pushed, neither reviewed |
| 01:59:26 | NIGHT_HANDBACK pre-check: own MCP helpers terminated | pids 97771 and 97773 (`codex mcp-server`), descendants of session root 97756; see `02-helper-term.txt`; no other agent processes on the machine (Ed's interactive sessions 67916/68088 were gone) |
| 01:59:40–42 | `check --candidate <staging>` | rc 0, `armable: true`; all eight checks pass (canonical `fast_forward: null`, census `DIAGNOSTIC_NO_PACK` with zero foreign pids, courier on PATH, night_agents, retained_roots, retry, sealed, supervisor); `lifecycle/check.json` |
| 01:59:55 | `notice --candidate` | body written to `lifecycle/notice.txt` |
| 02:00 | NOTICE email sent with the exact body | Gmail id `1a0c85878b76e926`, one address, no cc |
| 02:01:15 | `veto --candidate` | `clear: true` on NO, STOP, standdown, directives (`gh issue list` → `[]`) |
| 02:01:16–20 | `publish-install --candidate --notice-accepted 1a0c85878b76e926` | rc 0; probe install → bootout clear → real install; `lifecycle/install.json`, `arm-attempts/000001/baseline.json` |
| 02:01:21 | `verify --candidate` | rc 0; `com.joulewise.night` LOADED (calendar 09-22 02:17, plist sha = render sha `5b9c9162…`), `com.joulewise.night.deadman` LOADED; baseline drift false |
| 02:01:22 | `launchctl list` | `com.joulewise.night`, `com.joulewise.night.deadman`, `com.joulewise.magistrate` loaded; the three plists on disk |

No fixture, no fake launchctl (`fake_launchctl: false`). This is the first
time the `check → notice → veto → publish-install → verify` sequence ran live;
record 17's script set was not needed.

## Boundaries the armed night now owns

REQUEST / exit before 02:09:00; TERM 02:11:00; KILL 02:12:00; t0 02:17:00;
window end 04:47:00; completion / courier deadline 04:52:00; daily dead-man
05:52:00 (all PDT 09-22, from `prepare.json`). This activation exits before
REQUEST with no background work and no Codex children.

## Scratch copies

`/tmp/magistrate-dc2237d5/` holds the raw stdout/stderr of every step
(`03-check.out`, `04-notice.out`, `06-veto.out`, `07-publish-install.out`,
`08-verify.out`); the sealed copies are under the staging's `lifecycle/`.
