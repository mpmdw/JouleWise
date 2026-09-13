# Pairing refuter 12 on cold-gate ruling 10 (packet 34, ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01)

Opus 5, contract + execution lens, read-only in `/Users/edr/code/JouleWise-wt-coldgate-census`
(detached at `6d38f7de`, on main `4b9a3411`). Live probes on this machine 2026-09-13 ~09:05 PDT.

**VERDICT: AMEND.** Both ruled patterns survive every live and adversarial probe — no blocker.
Four amendments: A1 the Chrome-for-Testing "limitation" is false and names the wrong gap;
A2 regression R4's dialect assertion is fail-open (verified); A3 the desk-proof clause is not
executable as written; A4 prose/naming fixes. Q1's option choice, Q2, and the "not a contract
change" statement are AFFIRMED.

## 1. Live and adversarial probes

Ruled argv exactly as ruled, `/usr/bin/pgrep`, nothing signalled:

```
-lf '/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox)( |$)'
    24781 /Applications/Firefox.app/Contents/MacOS/firefox            exit=0, 1 line
-lf 'powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)'  exit=1, 0 lines
-lf 'Safari|Google Chrome|Chromium|Firefox|browser automation'        exit=0, 42 lines (old)
-lf 'powermetrics|window-chain|run_campaign|tail -f|watch'  574 /usr/libexec/watchdogd  exit=0 (old)
-lf '(^|/)watch( |$)'   exit=1        -x caffeinate   exit=1
```

The ten recorded `/System/…` Safari service lines (8 distinct executables;
`SafariPlatformSupport.Helper` at pids 1457/24791/25700) and `/usr/libexec/watchdogd` do NOT
match the ruled patterns; the open top-level Firefox DOES. `$` anchoring works in BSD
`pgrep -f` (Firefox's cmdline carries no arguments and still matched).

38 constructed argv in `/tmp/cg34_adv_argv.txt` through `grep -E`. Browser pattern MATCHED:
`…/Google Chrome.app/Contents/MacOS/Google Chrome` (bare and with args), `…/Chromium`,
`/Applications/Safari.app/Contents/MacOS/Safari` and the Preboot-Cryptex Safari path,
`Safari Technology Preview`, `Firefox Developer Edition`/`Nightly` (`…/MacOS/firefox`),
`…/Google Chrome Helper (Renderer) --type=renderer` (harmless), and
`…/Google Chrome for Testing --headless=new`. NOT matched: `Microsoft Edge`, `Brave Browser`,
`/usr/bin/env Safari`, Firefox `plugin-container`, `Firefox GPU Helper`, all nine service lines.
Monitor MATCHED: `/usr/bin/tail -f x`, `tail -f /var/log/system.log`, `/usr/bin/watch`,
`/usr/bin/watch -n 5 …`, `watch -n 5 …`, `/opt/homebrew/bin/watch -n 1 date`,
`/usr/bin/powermetrics …`, `powermetrics`, `python3 scripts/window-chain.py`; NOT matched:
`mywatch`, `/usr/local/bin/mywatch`, `watchdogd`, `/usr/libexec/watchdogd`. `sudo watch …` and
`zsh -c watch …` miss the wrapper only — the `watch` child's own cmdline matches, so no real
monitor escapes. **No BLOCKER: every real browser top-level and real monitor on the list matches.**

**A1.** The ruling calls Chrome for Testing a documented gap. It is not:
`/Contents/MacOS/Google Chrome for Testing` supplies a space after `Google Chrome`, which
`( |$)` accepts (verified). Replace that clause with:

> Chromium-family browsers whose top-level executable is not named `Safari`, `Google Chrome`,
> `Chromium` or `firefox` — Microsoft Edge, Brave Browser, Vivaldi, Opera, Arc — do not match,
> exactly as they did not under the pattern this replaces. Chrome for Testing, Chrome
> Canary/Beta and Safari Technology Preview DO match, because `( |$)` accepts the space before
> the suffix. The Edge/Brave family is the limitation to record; this ruling does not introduce it.

## 2. Code claims and the contract statement — AFFIRMED

Verified at the pin: `_derive_process_census` `arm_readiness_evidence_t0.py:1720`, browser probe
`:1725`, monitor `:1726`; `_ProbeResult.evidence()` `:280-287` stores argv/cwd/exit_code/stdout/
stderr verbatim, so the receipt does show the ruled pattern and what it saw; deriver bound
`:1954`; `_execute_probe` `:427-446` uses `Popen(list(argv))` with no shell, so the embedded
spaces and `( |$)` need no quoting; registry schema `arm_readiness.py:1111-1114` is exactly the
`derived` dict the ruling keeps; kind map `:1174`. Tests: pinned argv `:2505-2520`,
`_execute_probe` patches `:799`/`:1959`, AST liveness census `:969-1042` (counts direct
`_fresh_probe` call sites only — module constants are invisible to it, so the ruled
`_BROWSER_CENSUS_PATTERN`/`_MONITOR_CENSUS_PATTERN` do not move 600 s).

**NOT a contract change** is right: row id, `derived` shape, `predicate_id`, registry and
`required_row_ids` untouched; only two argv strings and their test pin move. One addition: the
row's MEANING narrows (from "no command line mentioning a browser name" to "no top-level GUI
browser executable"), and no field name says so — the installing commit must state it in a
sentence beside the code.

## 3. Q2 "bound, never gated" — AFFIRMED as fair

`:2448` is the right deciding line, and what follows seals it: `_real_probe_source` asserts only
that the source record echoes each probe's argv/stdout/stderr and the `live_exit_codes` it
computed itself (`:2467-2483`); for `PROCESS_CENSUS` there is no exit-code assertion at all, so
that Darwin test is green today with a 42-line rc=0 browser probe. Every authoring path patches
`_execute_probe` (`:799`). The S-0 limitation statement is fair and correctly bounded. One
addition: the same holds for the keep-awake and agent probes, so the limitation should read that
the PROCESS_CENSUS row as a whole was never gated on real output, not the browser class alone.

## 4. Q3 — kill claims verified; two defects

`grep -E` mutation matrix over the recorded service lines + `watchdogd`: M1 (revert) → 8 service
hits, killed by R1; M2 (drop `( |$)`) → 3 hits, killed by R1; M4 (bare `watch`) → `watchdogd`,
killed by R1; M5 (drop the `/Contents/MacOS/` anchor) → 0 service hits, R1 does NOT kill it, and
R2's `/usr/bin/env Safari` MUST-NOT case does (verified: it matches the anchorless pattern); M3
(one name) → the Chrome line stops matching, killed by R2; M7 (case-fold `Firefox`) → the
recorded `…/MacOS/firefox` line stops matching, killed by R2. The ruling's kill table is
accurate, including its admission about M5.

**A2 — R4 is fail-open.** `exit_code in {0,1}` catches `(?:…)` (`pgrep -lf '(?:Safari)'` → rc=2,
confirmed; `'foo('` → rc=2) but not constructs BSD ERE accepts as literals:
`pgrep -lf '\bwatch\b'` → **rc=1, zero lines** — a pattern that can never match, scored as
"census clean". Add to R4:

> Positive dialect control, browser-free: for each ruled pattern run `/usr/bin/grep -E
> "<pattern>"` (the same BSD `regcomp` engine `pgrep` compiles) over the recorded lines; assert
> exit 0 on the recorded Firefox top-level line and on a `powermetrics`/`tail -f` line, and
> exit 1 on all ten recorded `/System/…` lines and `/usr/libexec/watchdogd`. A `\b`, `\d` or
> `(?:…)` edit fails here whether or not a browser is running.

**A3 — the desk proof is not executable as specified.** `scripts/author_arm_evidence_t0.py`:

```python
parser.add_argument("--pack-root", required=True, type=Path)
parser.add_argument("--custody-root", required=True, type=Path)
root = args.pack_root.resolve(strict=True); custody = args.custody_root.resolve(strict=True)
pack_repository = readiness._repo_for_pack(root).resolve(strict=True)   # must equal this repo
```

It cannot run on "no browser open" alone: it needs an existing pack root whose recorded
repository is this checkout, an existing custody root, and it authors all fifteen T-0 rows, so an
earlier row (R1 clock batch, maintenance census, passwordless powermetrics) can refuse first.
Worse: the row's agent probe `codex|claude|t3` matches the seat that would run the proof
(Exhibit C pid 24974 `claude`, the Codex MCP servers, the ChatGPT/Claude desktop helpers).
Replace the clause with:

> Desk proof: YES, part of acceptance, and it is an Ed-hands step, not a seat step.
> Preconditions: (a) a `TRANSACTION_PACK` pack root built from this checkout plus a
> window-custody root — the installing seat names the pack it used or builds a throwaway one;
> (b) no browser open; (c) Claude Code, the Claude and ChatGPT desktop apps and every `codex`
> MCP server closed, because the agent probe matches them, and no `caffeinate` running.
> Evidence: the emitted `t0.no_stray_keepawake` source record showing the two new argv, exit 1,
> empty stdout. A refusal on an earlier row is reported, not read as a census failure.
> R1–R4 prove the patterns; only this run proves the row.

## 5. Writing standard on the installed prose

Four terms do unpaid work: **"appex"/"xpc"** (gloss once — an `.appex` bundle is a macOS app
extension, an `.xpc` bundle a system helper service; both are launched by the OS, not by a user
opening a browser); **"ERE"** ("POSIX extended regular expressions, the dialect `pgrep` and
`grep -E` compile"); **"the AST census test"** (name it: `tests/test_arm_readiness_evidence_t0.py:969`,
which counts direct `_fresh_probe` call sites and pins the 600 s liveness constant); **"the
refusal matrix"** in Q2 (name the test). Naming collision: `_fresh_probe` and the packet already
use **R1** for the clock-reference batch that must finish before any census probe
("fresh census cannot run before the R1 clock-reference batch completes"), and the ruling names
its first regression R1 — rename the regressions **G1–G4**. Count fix: "the nine Exhibit C
service lines" enumerates eight distinct executables across ten lines; say "the eight recorded
Apple service executables (ten lines) plus `watchdogd`" so a seat does not hunt a ninth name.

## 6. What else is wrong or left out

- **Agent class `t3`**: not exposed today — `pgrep -lf 't3'` → **rc=1, zero lines** on this
  machine, so no `/usr/libexec/…t3…` service matches and this is not a second instance of the
  defect. It stays fragile on principle (a two-character substring against every full command
  line; any future path or version string containing `t3` makes the row unpassable). Queue it as
  a follow-up under the same anchoring principle; no live evidence justifies changing it now.
- **Keep-awake `-x caffeinate`**: correct and unaffected (rc=1 live; `-x` matches the process
  name exactly). Audit asymmetry the ruling leaves unstated: without `-l` the receipt records
  bare pids, so a refusal cannot be read back from the evidence. Optional, same non-contract
  class: `("-lx", "caffeinate")`, consistent with the ruling's own "must still record what was
  seen" principle.
- **`…/Firefox.app/Contents/MacOS/crashhelper`** (pid 24783, ppid 1) matched the old pattern and
  not the ruled one. It is launchd-parented, so if it outlived a quit Firefox the census would
  pass with a Firefox process alive. Nit; do not widen the pattern for it.
- The rejection of options (ii)/(iii) is sound on auditability, but the reason "it would be a new
  `_fresh_probe` site" holds only for the natural implementation: the AST census docstring
  (`:983`) says a direct `_execute_probe` caller stays green. Keep the rejection, drop that reason.

Executed (read-only): ruled and old census argv via `/usr/bin/pgrep`; `(^|/)watch( |$)`;
`pgrep -x caffeinate`; `pgrep -lf 't3'`; dialect probes `'(?:Safari)'`, `'foo('`, `'\bwatch\b'`;
`ps -p <pid> -o command=` on the ten recorded pids; `grep -E` over `/tmp/cg34_adv_argv.txt` with
the ruled patterns and mutations M1/M2/M3/M4/M5/M7; `sed`/`grep` reads of
`arm_readiness_evidence_t0.py`, `arm_readiness.py`, `run_night.py:1494-1515`,
`scripts/author_arm_evidence_t0.py`, `tests/test_arm_readiness_evidence_t0.py`. No tracked file
edited, no process signalled, no test suite run.
