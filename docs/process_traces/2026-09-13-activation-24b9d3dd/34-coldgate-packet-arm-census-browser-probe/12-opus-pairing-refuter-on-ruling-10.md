# Pairing refuter 12 on cold-gate ruling 10 (packet 34, ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01)

Opus 5, contract + execution lens, read-only in `JouleWise-wt-coldgate-census` (detached at
`6d38f7de`, on main `4b9a3411`). Live probes on this machine 2026-09-13 ~09:05 PDT.

**VERDICT: AMEND.** Both ruled patterns survive every live and adversarial probe — no blocker.
Four amendments: A1 the Chrome-for-Testing "limitation" is false and names the wrong gap; A2
regression R4's dialect assertion is fail-open (verified); A3 the desk-proof clause is not
executable as written; A4 prose/naming. Q1's option choice, Q2 and the "not a contract change"
statement are AFFIRMED.

## 1. Live and adversarial probes

Ruled argv exactly as ruled, `/usr/bin/pgrep`, nothing signalled:

```
-lf '/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox)( |$)'
    24781 /Applications/Firefox.app/Contents/MacOS/firefox            exit=0, 1 line
-lf 'powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)'  exit=1, 0 lines
old browser pattern  exit=0, 42 lines;  old monitor pattern  exit=0, 574 /usr/libexec/watchdogd
-lf '(^|/)watch( |$)'  exit=1;   -x caffeinate  exit=1
```

The ten recorded `/System/…` Safari service lines (8 distinct executables;
`SafariPlatformSupport.Helper` at pids 1457/24791/25700) and `/usr/libexec/watchdogd` do NOT
match the ruled patterns; the open top-level Firefox DOES. `$` anchoring works in BSD `pgrep -f`
(Firefox's cmdline carries no arguments and still matched).

38 constructed argv in `/tmp/cg34_adv_argv.txt` through `grep -E`. Browser MATCHED: Chrome
(`…/Google Chrome.app/Contents/MacOS/Google Chrome`, bare and with args), Chromium, Safari
(`/Applications/…` and the Preboot-Cryptex path), Safari Technology Preview, Firefox Developer
Edition and Nightly, the Chrome helper `…Google Chrome Helper (Renderer) --type=renderer`
(harmless), `…Google Chrome for Testing --headless=new`. NOT matched: Microsoft Edge, Brave
Browser, `/usr/bin/env Safari`, Firefox `plugin-container`, `Firefox GPU Helper`, the nine
service lines. Monitor MATCHED: `/usr/bin/tail -f x`, `tail -f /var/log/system.log`,
`/usr/bin/watch`, `/usr/bin/watch -n 5 …`, `watch -n 5 …`, `/opt/homebrew/bin/watch -n 1 date`,
`/usr/bin/powermetrics …`, `powermetrics`, `python3 scripts/window-chain.py`; NOT matched:
`mywatch`, `/usr/local/bin/mywatch`, `watchdogd`, `/usr/libexec/watchdogd`. `sudo watch …` and
`zsh -c watch …` miss the wrapper only — the `watch` child's own cmdline matches, so no real
monitor escapes.
**No BLOCKER: every real browser top-level and real monitor on the list matches.**

**A1.** The ruling calls Chrome for Testing a documented gap. It is not:
`/Contents/MacOS/Google Chrome for Testing` supplies a space after `Google Chrome`, which
`( |$)` accepts (verified). Replace that clause with:

> Chromium-family browsers whose top-level executable is not named `Safari`, `Google Chrome`,
> `Chromium` or `firefox` — Microsoft Edge, Brave Browser, Vivaldi, Opera, Arc — do not match,
> exactly as they did not under the pattern this replaces; that is the limitation to record, and
> this ruling does not introduce it. Chrome for Testing, Chrome Canary/Beta and Safari Technology
> Preview DO match, because `( |$)` accepts the space before the suffix.

## 2. Code claims and the contract statement — AFFIRMED

Verified at the pin: `_derive_process_census` `arm_readiness_evidence_t0.py:1720`, browser probe
`:1725`, monitor `:1726`; `_ProbeResult.evidence()` `:280-287` stores argv/cwd/exit_code/stdout/
stderr verbatim, so the receipt does show the ruled pattern and what it saw; deriver `:1954`;
`_execute_probe` `:427-446` uses `Popen(list(argv))` with no shell, so the embedded spaces and
`( |$)` need no quoting; registry schema `arm_readiness.py:1111-1114` is exactly the `derived`
dict the ruling keeps. Tests: pinned argv `:2505-2520`, `_execute_probe` patches `:799`/`:1959`,
AST liveness census `:969-1042` (direct `_fresh_probe` call sites only — the ruled module
constants are invisible to it, so 600 s does not move).

**NOT a contract change** is right: row id, `derived` shape, `predicate_id`, registry and
`required_row_ids` untouched; only two argv strings and their test pin move. One addition: the
row's MEANING narrows — from "no command line mentioning a browser name" to "no top-level GUI
browser executable" — and no field name says so, so the installing commit must state it in a
sentence beside the code.

## 3. Q2 "bound, never gated" — AFFIRMED as fair

`:2448` is the right deciding line, and what follows seals it: `_real_probe_source` asserts only
that the source record echoes each probe's argv/stdout/stderr and the `live_exit_codes` it
computed itself (`:2467-2483`) — for `PROCESS_CENSUS` there is no exit-code assertion, so that
Darwin test is green today with a 42-line rc=0 browser probe. Every authoring path patches
`_execute_probe` (`:799`). The S-0 limitation is fair and correctly bounded; one addition — the
same holds for the keep-awake and agent probes, so it should say the PROCESS_CENSUS row as a
whole was never gated on real output, not the browser class alone.

## 4. Q3 — kill claims verified; two defects

`grep -E` mutation matrix over the recorded service lines + `watchdogd`: M1 (revert) → 8 hits,
killed by R1; M2 (drop `( |$)`) → 3 hits, R1; M4 (bare `watch`) → `watchdogd`, R1; M5 (drop the
path anchor) → 0 service hits, R1 does NOT kill it and R2's `/usr/bin/env Safari` MUST-NOT case
does (verified); M3 (one name) → Chrome stops matching, R2; M7 (case-fold `Firefox`) → the
recorded `…/MacOS/firefox` stops matching, R2. The kill table is accurate, M5 admission included.

**A2 — R4 is fail-open.** `exit_code in {0,1}` catches `(?:…)` (`pgrep -lf '(?:Safari)'` → rc=2,
confirmed; `'foo('` → rc=2) but not constructs BSD ERE accepts as literals:
`pgrep -lf '\bwatch\b'` → **rc=1, zero lines** — a pattern that can never match, scored as
"census clean". Add to R4:

> Positive dialect control, browser-free: for each ruled pattern run `/usr/bin/grep -E
> "<pattern>"` (the same BSD `regcomp` engine `pgrep` compiles) over the recorded lines; assert
> exit 0 on the recorded Firefox top-level line and on a `powermetrics`/`tail -f` line, exit 1 on
> the ten `/System/…` lines and `watchdogd`. A `\b`, `\d` or `(?:…)` edit fails here with or
> without a browser running.

**A3 — the desk proof is not executable as specified.** `scripts/author_arm_evidence_t0.py`:

```python
parser.add_argument("--pack-root", required=True, type=Path)
parser.add_argument("--custody-root", required=True, type=Path)
pack_repository = readiness._repo_for_pack(root).resolve(strict=True)   # must equal this repo
```

It cannot run on "no browser open" alone: it needs an existing pack root whose recorded
repository is this checkout, an existing custody root, and it authors all fifteen T-0 rows, so an
earlier row (clock batch, maintenance census, passwordless powermetrics) can refuse first. Worse:
the agent probe `codex|claude|t3` matches the seat that would run the proof (Exhibit C pid 24974
`claude`, the Codex MCP servers, the ChatGPT/Claude desktop helpers). Replace the clause with:

> Desk proof: YES, part of acceptance, and an Ed-hands step, not a seat step. Preconditions:
> (a) a `TRANSACTION_PACK` pack root built from this checkout plus a window-custody root — the
> installing seat names the pack it used or builds a throwaway one; (b) no browser open;
> (c) Claude Code, the Claude and ChatGPT desktop apps and every `codex` MCP server closed,
> because the agent probe matches them, and no `caffeinate` running. Evidence: the emitted
> `t0.no_stray_keepawake` source record showing the two new argv, exit 1, empty stdout. A refusal
> on an earlier row is reported, not read as a census failure. G1–G4 prove the patterns; only
> this run proves the row.

## 5. Writing standard on the installed prose

Four terms do unpaid work at first use. **"appex"/"xpc"**: an `.appex` bundle is a macOS app
extension, an `.xpc` bundle a system helper service — both launched by the OS, not by a user
opening a browser. **"ERE"**: POSIX extended regular expressions, the dialect `pgrep` and
`grep -E` compile. **"the AST census test"**: name it — `tests/…_evidence_t0.py:969`, which
counts direct `_fresh_probe` call sites and pins the 600 s liveness constant. **"the refusal
matrix"** in Q2: name the test. Naming collision: `_fresh_probe` and the packet already use **R1** for the clock-reference batch
that must finish before any census probe, and the ruling names its first regression R1 — rename
the regressions **G1–G4**. Count fix: "the nine Exhibit C service lines" is eight distinct
executables across ten lines; write "the eight recorded Apple service executables (ten lines)
plus `watchdogd`" so a seat does not hunt a ninth name.

## 6. What else is wrong or left out

- **Agent class `t3`**: not exposed today — `pgrep -lf 't3'` → **rc=1, zero lines**, so no
  `/usr/libexec/…t3…` service matches; not a second instance of the defect. Still fragile on
  principle (a two-character substring against every full command line: any future path or
  version string containing `t3` makes the row unpassable). Queue as a follow-up; no live
  evidence justifies changing it now.
- **Keep-awake `-x caffeinate`**: correct and unaffected (rc=1 live). Unstated audit asymmetry —
  without `-l` the receipt records bare pids, so a refusal cannot be read back from the evidence;
  optional non-contract fix `("-lx", "caffeinate")`, per the ruling's own "record what was seen".
- Nit: `…/Firefox.app/Contents/MacOS/crashhelper` (pid 24783, ppid 1) matched the old pattern and
  not the ruled one, and is launchd-parented, so if it outlived a quit Firefox the census would
  pass with a Firefox process alive. Do not widen the pattern for it.
- The rejection of options (ii)/(iii) is sound on auditability, but its reason "a new
  `_fresh_probe` site" holds only for the natural implementation — the AST census docstring
  (`:983`) says a direct `_execute_probe` caller stays green. Keep the rejection, drop the reason.

Executed (read-only): ruled and old census argv via `/usr/bin/pgrep`; `(^|/)watch( |$)`;
`pgrep -x caffeinate`; `pgrep -lf 't3'`; dialect probes `'(?:Safari)'`, `'foo('`, `'\bwatch\b'`;
`ps -p <pid> -o command=` on the ten recorded pids; `grep -E` over `/tmp/cg34_adv_argv.txt` with
the ruled patterns and M1/M2/M3/M4/M5/M7; `sed`/`grep` reads of the module, `arm_readiness.py`,
`run_night.py:1494-1515`, the desk tool and the test file. No tracked file edited, no process
signalled, no test suite run.
