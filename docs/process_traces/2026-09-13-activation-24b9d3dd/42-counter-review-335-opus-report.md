# 42 — Opus counter-review of PR #335 (contract lens; gate rows 2 and 6)

Opus 5, read-only in `JouleWise-wt-ref-arm-census` at `4cd89298` (base/`origin/main` `4b9a3411`).
Executed this session: the five G-tests + pinned-argv + AST-liveness tests; ten counterfactual
mutations in a `/tmp` export of HEAD; live `pgrep` probes; a decoy-leak test; `gh pr view/checks`.
No tracked file edited; no process signalled that a test here did not spawn.

**VERDICT: AMEND.** The code is LANDABLE unchanged — install is faithful to ruling 10 as amended by
synthesis 13 + addendum, all four regressions kill what they claim, nothing is a contract change.
The **PR body blocks the merge**: the twelve-row gate ledger still holds `LEDGER_ROW*` placeholders
and the `gate-ledger` check **fails** (deciding line: `gate-ledger: item 12: final-head evidence must
be a commit sha`). One factual count error and five incompletenesses follow, with replacement text.

## 1 — Install vs the ruling as amended: MATCHES

`joulewise/arm_readiness_evidence_t0.py:57-58` carries the two ruled strings byte-for-byte
(`/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox)( |$)`;
`powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)`). `_derive_process_census:1724-1740`:
four probes, same order (keep-awake, agent, browser, monitor), same labels, `-x caffeinate` and
`codex|claude|t3` untouched, `_expect_absent` loop untouched, emitted `derived` dict byte-identical
(`{"absent_process_classes": [...], "fresh_process_census": True}`), `predicate_id`/`_DerivedRow`
unchanged. Module delta is 6 insertions / 2 changed lines; the diff touches exactly two files, so
`joulewise/arm_readiness.py:1111-1114` (row schema) and `:1174`, the registry and `required_row_ids`
are provably untouched. **"NOT a contract change" is TRUE.** The row's *meaning* does narrow (from
"any command line mentioning a browser name" to "a top-level browser executable in an app bundle");
refuter 12 §2 required that be stated beside the code — it is, at `:55-56`. `git grep` finds the old
pattern only in trace/queue prose, no second evaluation site.

## 2 — G4 decoy control vs pairing A2

**Satisfies A2's requirement** (a dialect control that fails closed with no browser open): the
positive direction now runs under pgrep's own `regcomp`. Verified by mutation in `/tmp`:
`\bwatch\b` (exact, single backslash) → G4 FAILED; `(?:Safari)` → `pgrep` rc 2; either way
`assertEqual(probe.exit_code, 0)` and the decoy-pid assertion fail. G4 passed here with Firefox
open (5 tests, OK, 1.3 s), i.e. real browser output survives the per-line assertions.

**Catches:** (a) any construct BSD ERE rejects (rc 2: `(?:…)`, `(?=`, `(?i)`, unbalanced paren);
(b) any construct BSD ERE accepts as literals and can therefore never match (`\b`, `\d`, `\s`, `\w`)
— rc 1, zero lines; (c) any narrowing that stops matching `/Applications/Safari.app/Contents/MacOS/
Safari 30` or `/opt/homebrew/bin/watch 30`. **Cannot catch:** the *negative* direction under pgrep's
engine except opportunistically — the "no recorded service basename in output" assertion is only
evidence when those services happen to be live (they are: `pgrep -lf Safari` → 10 lines here). A
pattern that both engines accept but that diverges on a line absent at run time is invisible; G1/G2
cover that side in Python `re` only. A2's literal "exit 1 on the ten `/System/…` lines and
`watchdogd`" is therefore met *by luck of the machine*, not by construction. Follow-up (not a
blocker, the addendum chose the instrument): add negative decoys, e.g.
`Popen(["/System/…/SafariWidgetExtension.appex/Contents/MacOS/SafariWidgetExtension", "30"],
executable="/bin/sleep")`, and assert pgrep does **not** return that pid.

**Leak into the row's other probes: NO** — measured, not argued. With each decoy live,
`pgrep -x caffeinate` returned no decoy pid and `pgrep -lf 'codex|claude|t3'` returned no decoy line
(both markers). **Interference with a concurrent real arm: YES, bounded and fail-closed.** For ~1 s
per subtest a process whose full argv is `/Applications/Safari.app/Contents/MacOS/Safari 30` exists,
and any arm or desk authoring running at that instant would match it and refuse `PROCESS_CENSUS`.
It can never produce a false PASS. Two residuals worth a PR-body sentence: the install uses
`"30"` where the addendum specified `"3"` (a deliberate anti-flake margin — a 3 s decoy can expire
under a slow `pgrep` — but it also widens the stray-decoy window to 30 s if the test is SIGKILLed
past its `finally`); and G4 **fails** rather than skips where the process list is unavailable
(seat sandbox, `pgrep` rc 3 — record 38 F1). CI is `ubuntu-latest` throughout, so G4 is skipped in
CI and is bench-only evidence.

## 3 — G1–G3 pin the ruled behaviour: YES (each counterfactual named, all executed)

| Mutation | Test that fails | Observed |
| --- | --- | --- |
| M1 revert browser to old alternation | `test_g1_…ignore_recorded_macos_services` | FAILED (10) |
| M2 drop the `( \|$)` tail | `test_g1_…` | FAILED (3) |
| M4 monitor back to bare `watch` | `test_g1_…` | FAILED (1, watchdogd) |
| M5 drop the `/Contents/MacOS/` anchor | `test_g2_…refuse_real_browsers_and_monitors` (G1 passes, as ruled) | G1 OK / G2 FAILED (1, `/usr/bin/env Safari`) |
| M3 narrow to one browser name | `test_g2_…` | FAILED (5) |
| M7 case-fold to `Firefox` | `test_g2_…` | FAILED (2) |
| M6 drop `tail -f` | `test_g2_…` | FAILED (1) |
| M8 drop `_expect_absent` for browser+monitor | `test_g3_…gate_the_row` | FAILED (2) |
| M9 swap browser/monitor probe order | `test_g3_…` | FAILED (4) |
| M10 `\bwatch\b` | `test_g4_real_ruled_census_pgrep_dialect` | FAILED (1) |

Note for the record: `test_real_process_census_executes_pgrep_and_binds_output` holds the argv as
string literals and executes them; it does **not** compare them to the module, so it alone does not
detect a constant edit — G1/G2 do, and G3 binds the census's call sites to the constants in order.
`test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census` (AST census) still passes; no
new `_fresh_probe` site, so the 600 s liveness constant does not move.

## 4 — Desk-proof acceptance (refuter 12 A3) and the lane state

The PR body states A3's substance correctly (Ed-hands; pack root from this checkout + custody root;
no browser; Claude Code, both desktop apps and every `codex` MCP server closed; no `caffeinate`;
evidence = the emitted `t0.no_stray_keepawake` source record with the two new argv, exit 1, empty
stdout) and correctly leaves the lane OPEN. **Two gaps:** it omits A3's clause "a refusal on an
earlier row is reported, not read as a census failure"; and `docs/process/state_kernel.json`
(`/tasks/ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01/acceptance`) still carries the *pre-A3*,
not-executable text ("a desk run of `scripts/author_arm_evidence_t0.py` … with no browser open no
longer refuses") and still cites packet **05**, not 34. Synthesis 13 schedules that edit "at
bookkeeping"; until it lands, the authoritative acceptance contradicts the PR body. Say so.

## 5 — Rule 11 / unruled amendments: NONE in the diff

Code and tests only; no process doc, skill, cadence number or contract touched. Everything the PR
asserts traces to ruling 10 + synthesis 13 (A1–A4 adopted) + the 09:00 addendum. The one un-ruled
deviation is the decoy `"30"` vs the addendum's `"3"` (test mechanics, non-contract) — record it,
do not re-ruling it.

## 6 — PR body fidelity (false or incomplete sentences, with replacement text)

1. **FALSE (count).** "matched eight always-present Apple system services (ten lines: …, two
   `SafariPlatformSupport` XPC helpers, …)" — there is **one** distinct `SafariPlatformSupport`
   executable, at three pids (1457/24791/25700), and the eight distinct executables span ten lines.
   Replace with: "matched eight always-present Apple system-service executables across ten lines
   (`SafariBookmarksSyncAgent`, `SafariWidgetExtension`, `SafariLinkExtension`,
   `com.apple.SafariPlatformSupport.Helper` at three pids, `CredentialProviderExtensionHelper`,
   `com.apple.Safari.SafeBrowsing.Service`, `SafariLaunchAgent`, `SafariConfigurationSubscriber`)".
2. **INCOMPLETE.** "Live: the browser probe matches only the operator's open Firefox; the monitor
   probe matches nothing" — true but undated. Append: "(probed 2026-09-13 08:29–09:25 PDT on Darwin
   25.6.0 with Firefox pid 24781 open; re-verified at the counter-review: browser rc 0, one line;
   monitor rc 1, zero lines)".
3. **INCOMPLETE.** The G4 bullet. Append: "G4 is bench-only: CI runs `ubuntu-latest`, so it is
   skipped there, and it *fails* rather than skips wherever the process list is unavailable (a seat
   sandbox returns `pgrep` exit 3 — record 38 F1). Each decoy lives ~1 s and is terminated in a
   `finally`; while it lives, a concurrently running arm or desk authoring would match it and refuse
   `PROCESS_CENSUS` — fail-closed, never a false pass. The decoys match neither the keep-awake
   (`-x caffeinate`) nor the agent (`codex|claude|t3`) probe (measured)."
4. **INCOMPLETE.** "Recorded, not installed: the S-0 clone-proof 'eleven-kind census PASS' …" — says
   recorded but names no home. Replace the list's lead-in with: "Recorded on the bookkeeping branch
   (`bookkeeping/2026-09-13-activation-24b9d3dd`), not installed here: the S-0 limitation … ; and
   queued as follow-up rows: the optional `-lx caffeinate` audit change, the `t3` two-character
   agent token's fragility, Firefox's launchd-parented `crashhelper`."
5. **INCOMPLETE.** The desk-proof sentence. Append: "A refusal on an earlier T-0 row is reported,
   not read as a census failure. `docs/process/state_kernel.json`'s acceptance text for this lane
   still carries the pre-A3 wording and the packet-05 citation; it is amended at bookkeeping, and
   the lane cannot close before both that edit and the Ed-hands record exist."
6. **INCOMPLETE.** Verification line. Append after "Refuter 41 (Astra execution lens)": "Opus
   counter-review 42 (contract lens) on head `4cd89298`: LANDABLE code, PR-body amendments; ten
   counterfactual mutations re-run independently."
7. **BLOCKING.** The gate ledger's twelve rows all read `RUN LEDGER_ROW*`. Substitute each with the
   real commit sha or repo path before marking the PR ready; item 12 must be a commit sha.

## 7 — Merge-ability with `origin/main` now

`origin/main` = `4b9a3411` = the merge-base; HEAD is 1 ahead, 0 behind → **fast-forward, no
conflict**; `gh pr view` reports `mergeable: MERGEABLE`. But **not mergeable as it stands**:
`isDraft: true`, `mergeStateStatus: UNSTABLE`, and the **`gate-ledger` check FAILS** on the
placeholders (items 1–12; item 12 "final-head evidence must be a commit sha"). `build`, `fences`,
`installed-wheel` pass; the `test` matrix was still pending at review time. Fix the ledger, let CI
go green, mark ready — then it lands clean.
