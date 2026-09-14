# Cold-gate ruling 34 — ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01

Judge: cold Fable 5.1 seat, convened 2026-09-13 08:29 PDT, ruled 08:38 PDT.
Validator: first run REFUSE (`charter_trusted_observed_mismatch`, the deliberate
typo `…870…`→`…880…`); second run PASS, all six exhibit digests observed = expected,
packet sha `634d21ca…`, charter sha `099de884…`. Judged at main `4b9a3411`; the
worktree module and test file are byte-identical to the pin (`git diff --stat` empty).

## Contamination disclosure

Auto-loaded before any read: global `~/.claude/CLAUDE.md`, project `CLAUDE.md`, and
the auto-memory index `MEMORY.md` (checkpoint one-liners for 09-10…09-13, including
the fact that packet 05 ruled the night-gate census and that PR #334 merged). None
speak to the browser or monitor patterns. Not opened: CLAUDE.local.md, RUN_STATE.md,
TASK_QUEUE.md, decision_log.md, any trace outside this packet. One narrow probe
outside the packet: an `rg -o` of the phrase "eleven-kind" in `docs/process/state_kernel.json`
(a file Exhibit E names), plus a filename-only `rg -l` for the same phrase; no trace
file was opened.

## Q1 — ruling: option (i) for both classes, with the argv fixed below

Terms: a "probe" is one `pgrep` run whose exit code and output the row records; the
row "refuses" when `_expect_absent` sees exit ≠ 1 or any output. `pgrep -f` matches
the pattern anywhere in a process's full command line; `pgrep -x` matches the
16-character process name exactly.

**Browser class — ruled option (i), anchored `-lf`.** Replace the browser probe in
`_derive_process_census` (`joulewise/arm_readiness_evidence_t0.py:1725`) with:

```
("/usr/bin/pgrep", "-lf", "/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox)( |$)")
```

Why this form: every macOS GUI browser's top-level executable sits at
`<bundle>/Contents/MacOS/<name>`, and only the top-level one ends the path with the
bare name followed by a space or end of line. Live today it matches exactly one
process, the operator's Firefox (pid 24781), and none of the nine system services;
the exit code becomes 1 the moment Firefox is quit. It beats `-x` because (a) the row
then records the full argv of what refused, which `-x` cannot (`pgrep -lx` prints
only `24781 firefox`), and (b) the same regex string runs unchanged under Python
`re`, so the Q3 regression can feed the recorded lines through the ruled pattern
itself. The tail `( |$)` is load-bearing: without it the Safari appex extensions
(`…/Contents/MacOS/SafariWidgetExtension`, `SafariLinkExtension`,
`SafariConfigurationSubscriber`) match (verified live, 3 hits). Firefox is spelled
lower-case because the executable is `firefox`; the old `Firefox` token only ever
matched via the bundle path. The token `browser automation` is dropped: no real
executable carries that string, so it never matched anything; automated browsers run
the same top-level executables and are caught by name (documented gap: Chrome for
Testing's executable name is `Google Chrome for Testing`, which this pattern does not
match; record as a limitation, not a blocker). Browser helper processes (e.g.
`Google Chrome Helper --type=renderer`) also match this pattern, which is harmless:
they exist only while the browser runs, and the row refuses on the parent anyway.

**Monitor class — ruled option (i), anchor `watch`.** Replace the monitor probe
(`:1726`) with:

```
("/usr/bin/pgrep", "-lf", "powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)")
```

`(^|/)watch( |$)` matches `watch -n 5 …` and `/opt/homebrew/bin/watch …` and does not
match `/usr/libexec/watchdogd` (live: exit 1, zero lines). Anchoring is preferred to
dropping the token because the runbook names periodic monitors as a forbidden class
and `watch` is the canonical one. The other four tokens are unchanged.

Options (ii) and (iii) are rejected for both classes: they add a second process
listing (`ps` for owner/parent/path) and a Python classifier to a row whose whole
value is that the recorded probe IS the decision; a post-filter also breaks the
present audit property that any output refuses, and it would be a new `_fresh_probe`
site, which moves the ruled 600 s liveness constant that the AST census test pins.

**Emitted row.** `derived` stays exactly
`{"absent_process_classes": ["agent","browser","keep_awake","monitor"], "fresh_process_census": true}`;
the four probes, their order and labels stay; `_expect_absent` semantics stay
(exit 1 and empty stdout). What changes is only the two argv strings, which the
source record already stores verbatim per probe (`_ProbeResult.evidence()`), so an
auditor reads the ruled pattern and its output from the receipt.

**Contract-change statement: NOT a contract change.** No change to the row's shape,
`predicate_id`, the schema in `arm_readiness.py`, the registry, or `required_row_ids`.
The pinned argv list in `tests/test_arm_readiness_evidence_t0.py:2505-2520` must be
updated to the new strings (a test edit that travels with the code). Docs that quote
the old argv (Exhibit F's 08-23 coverage table) are historical and stay as written.

## Q2 — how earlier estates passed this row

The deciding line is `tests/test_arm_readiness_evidence_t0.py:2448`,
`probes = tuple(t0._execute_probe(command, cwd=ROOT) for command in commands)`: the
Darwin-only test `test_real_process_census_executes_pgrep_and_binds_output` DOES run
the real browser and monitor `pgrep` on this Mac, but it only binds exit codes and
output hashes into a synthetic row and never calls `_expect_absent`, so it is green
with 22 browser hits. Every test that reaches `_derive_process_census` through the
authoring path patches `_execute_probe` (`:799`, `:1959`) or uses `passing_probe`
(integration test, Exhibit D), and the refusal matrix exercises only the agent
pattern. So within the packet, no test ever gated the real browser output, and
Exhibit F's search of the August records for a real process-census pass came back
empty. The kernel does carry the S-0 clone-proof line "3.9 all three packs ARMED and
verified …, eleven-kind census PASS" (state_kernel.json:7034), and a filename-only
search finds the phrase in the 2026-08-22 T20 completion record, which this judge did
not open; whether that 08-22 arm executed the real argv on an OS where these
services did not match, or ran under a fixture probe, is undecidable from the packet.
It is mechanically decidable: the 08-22 pack's `t0.no_stray_keepawake` source record
stores the browser probe's argv, exit code and stdout. Limitation to record on the
S-0 proof: "eleven-kind census PASS" establishes the census kinds executed and bound,
not that the ruled predicate passes on the current macOS; on Darwin 25.6.0 today the
row provably cannot pass, so that PASS is not evidence for the first pack night.

## Q3 — regression specification

```
File: tests/test_arm_readiness_evidence_t0.py (beside the real-probe tests, ~:2500)
Module constants the seat must add and use in _derive_process_census:
  _BROWSER_CENSUS_PATTERN = r"/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox)( |$)"
  _MONITOR_CENSUS_PATTERN = r"powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)"
(the AST census test forbids new _fresh_probe sites, not new constants)

R1 test_ruled_census_patterns_ignore_recorded_macos_services (pure, all platforms)
  SERVICE_ARGV = the nine Exhibit C service lines, pid stripped, full paths
    (SafariBookmarksSyncAgent, SafariWidgetExtension …, com.apple.SafariPlatformSupport.Helper,
     CredentialProviderExtensionHelper, SafariLinkExtension …, com.apple.Safari.SafeBrowsing.Service,
     SafariLaunchAgent, SafariConfigurationSubscriber) + "/usr/libexec/watchdogd"
  for line in SERVICE_ARGV: assert re.search(t0._BROWSER_CENSUS_PATTERN, line) is None
                            and re.search(t0._MONITOR_CENSUS_PATTERN, line) is None
  kills: M1 revert browser pattern to the old alternation (8 service hits);
         M2 drop the "( |$)" tail (3 appex/xpc hits); M4 widen back to bare "watch"
         (watchdogd hits); M5 drop the "/Contents/MacOS/" anchor is NOT killed by R1
         (no recorded service line ends in a bare name) — killed by R2's helper case.

R2 test_ruled_census_patterns_refuse_real_browsers_and_monitors (pure)
  MUST match browser: "/Applications/Firefox.app/Contents/MacOS/firefox" (recorded),
    "…/Safari.app/Contents/MacOS/Safari", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --x",
    "/Applications/Chromium.app/Contents/MacOS/Chromium --headless=new",
    "/Applications/Firefox.app/Contents/MacOS/firefox https://example.com"
  MUST NOT match browser: "/Applications/Firefox.app/Contents/MacOS/plugin-container -isForBrowser"
    (a helper whose name is not a browser name) and "/usr/bin/env Safari" (bare name, no bundle path)
  MUST match monitor: "/usr/bin/powermetrics -i 200 -n 1", "tail -f /var/log/system.log",
    "watch -n 5 pmset -g therm", "/opt/homebrew/bin/watch -n 1 date", "python3 scripts/window-chain.py"
  kills: M3 narrow to one browser name; M5 drop the path anchor ("/usr/bin/env Safari" case);
         M6 drop "tail -f" or the watch alternative entirely; M7 case-fold to "Firefox".

R3 test_browser_and_monitor_probes_gate_the_row (authoring path, mocked _execute_probe)
  extend the named-refusal matrix / integration loop (Exhibit D, pattern "codex|claude|t3")
  to ALSO iterate the two new argv strings: a probe returning exit 0 + the recorded Firefox
  line, and one returning exit 0 + "574 /usr/bin/powermetrics -i 200", must raise
  T0EvidenceAuthoringError kind PROCESS_CENSUS; exit 1 + "" must pass.
  kills: M8 remove _expect_absent for the browser or monitor probe; M9 reorder/drop a probe.

R4 test_real_ruled_census_pgrep_dialect (Darwin only; extends the existing real-probe test
  with the new argv) — runs the real pgrep; assert exit_code in {0, 1} (an ERE-invalid
  edit gives 2) and, for every stdout line, re.search(pattern, line) is not None and no
  recorded service basename (the nine + watchdogd) appears. Green with or without a
  browser open, so it runs on desk days.
  kills: M10 a Python-only regex construct (e.g. "(?:…)") that pgrep rejects.

Desk proof: YES, part of acceptance (the kernel row says so and nothing above replaces
it). Run scripts/author_arm_evidence_t0.py on this machine with no browser open and the
same agent/keep-awake conditions the night requires; acceptance evidence = the emitted
t0.no_stray_keepawake source record showing the two new argv, exit 1, empty stdout.
R1–R4 prove the pattern; only the desk run proves the row passes end-to-end on this OS.
```

## Executed probes (all read-only, this session, 08:29–08:34 PDT)

- `scripts/validate_gate_packet.py` ×2: REFUSE (typo sha), then PASS (rc 0).
- `pgrep -lf` current browser pattern: exit 0, 22 lines (8 services + 14 Firefox lines).
- `pgrep -lf` current monitor pattern: exit 0, 1 line (`574 /usr/libexec/watchdogd`,
  root, ppid 1).
- `pgrep -lf '/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox)( |$)'`: exit 0,
  1 line (`24781 /Applications/Firefox.app/Contents/MacOS/firefox`).
- Mutation M2 (no tail): exit 0, 4 lines (three Safari appex/xpc services + Firefox).
- Mutation M3 (no path anchor): 1 line (Firefox only) — survives on recorded lines.
- `pgrep -lx 'Safari|Google Chrome|Chromium|firefox'`: exit 0, `24781 firefox`.
- `pgrep -l Safari` (name match, no -f): 9 truncated service names, all ≤ 15 chars.
- `pgrep -lf 'powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)'`: exit 1,
  0 lines. Bare `(^|/)watch`: exit 0, watchdogd.
- `/tmp/cg34_re.py` under the canonical `.venv/bin/python3`: both ruled patterns
  reject all nine services + watchdogd and accept six browser and six monitor lines;
  old browser pattern hits 8 services, no-tail hits 3, old monitor hits watchdogd.
- `git show 4b9a3411:` module and test file to `/tmp`; `git diff --stat` vs HEAD empty;
  `git grep` for the pattern strings at the pin (only `:1725-1726` and test `:2513/:2518`
  hold them in code).
- `rg -o 'eleven-kind'` on `state_kernel.json` (one line, :7034); `rg -l` filename list.
