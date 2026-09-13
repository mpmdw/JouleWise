# Opus 5 pairing refuter (contract lens) on ruling 10 — NIGHT-CENSUS-CHATGPT-APP-01

Read-only in `JouleWise-wt-coldgate-census` (above main `27957b60`); no tracked
file edited. Tests ran in a throwaway copy under `/tmp/cg-refuter` (removed).

## VERDICT: AMEND

The ruled option (i) is **correct and I affirm it**, and the regression test
**passes at HEAD and fails under both narrowings** (§2). Three amendments are
required before the text is installed, plus one correction to the ruling's
reason paragraph.

**A1 — NIGHT_HANDBACK replacement is ungrammatical as written.** Target
sentence, `docs/process/NIGHT_HANDBACK.md:48-50`: "Precondition that only the
operator can meet: no interactive agent session and no ChatGPT desktop app
alive from the plan span (02:31 PDT on 2026-09-15) through t0." The ruling's
replacement ends in a parenthetical, severing `alive` from `from the plan span
… through t0`, and its "quit both" now follows a three-item list. Substitute
this for the same span ("no interactive agent session … alive"):

```
no interactive agent session, no ChatGPT desktop app and no Claude desktop
app (quit both apps from their menu bar; a running app refuses the night)
alive
```

**A2 — the §0.6 sentence over-claims and has a garbled clause.** "both match
the census" is false for the apps' own processes: the pattern is case-sensitive,
so `25633 …/ChatGPT.app/Contents/MacOS/ChatGPT` and
`29809 …/Claude.app/Contents/MacOS/Claude` do **not** match (probe:
`pgrep -lf "codex|claude|t3" | grep -cE "^(25633|29809) "` → `0`); only helpers
do. And "An app started after the arm reaches t0" reads as the app reaching t0.
Replacement:

```
Desktop apps that bundle an agent runtime — a shipped command-line agent
binary that the app runs as a local server — count as agents. The ChatGPT
desktop app runs the Codex CLI as `codex … app-server`, and both it and the
Claude desktop app run helper processes whose argv contains `codex` or
`claude`; the census matches those helpers (it does not match the apps' own
top-level processes, which are named `ChatGPT` and `Claude`). Quit both apps
before the plan span and keep them quit through t0. An app still running at
t0 refuses the night; that refusal is correct.
```

**A3 — the third sentence is mis-placed and mis-labelled.** Its stated anchor,
"abort the arm; do not signal them." (`derivation_night_runbook.md:602`), ends
a paragraph about the **manual** ancestry inspection of `claude (daemon
run|…)|--resume` (lines 590-604), not the coded probe. The runbook has no
"agent probe" term (`grep -iE 'agent probe|browser|process census'` at
`27957b60` → one glossary row, `:2353`), so "The agent probe" fails the
first-use test there; and "by design" is false as history — the match is a
substring accident this ruling now ratifies. Put it in §0.6 instead:

```
The coded census that the t0 gate and a pack night's arm both run
(`pgrep -lf codex|claude|t3`) matches those helper processes; that is the
ruled behaviour, and the pattern is not narrowed to exclude them.
```

**A4 — correction to the reason paragraph (no installed text).** "the arm-time
probe uses the same literal and already refuses on the app (Exhibit B), so a
by-name class would only relabel a refusal that already happens" is true only
for `TRANSACTION_PACK` nights. See §5/§6.

## 1. Factual claims checked

All verified at `27957b60` unless marked live.

- `AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "codex|claude|t3")` —
  `joulewise/night_gate.py:42`. Correct.
- `agent_census` refuses on any non-empty census output —
  `night_gate.py:498-524`; clean only on `exit_code == 1 and
  stdout.strip() == ""` (`:515-516`). Correct.
- Helpers `result` (`tests/test_night_gate.py:23`) and `FakeProbeSource`
  (`:61`, `probes()` at `:124`) match the proposed test's use; the neighbour
  test is at `:355` in class `NightGateTests` (`:286`). Correct.
- Runbook §0.6 heading `derivation_night_runbook.md:582`; "`[QUIET-MAC]` nights
  are agent-free." at `:584` — but it opens a paragraph continuing on the same
  line, so "inserted after" it is ambiguous; A2/A3 go in as a new paragraph
  after that paragraph (ends `:588`).
- NIGHT_HANDBACK sentence at `:46-50`, quoted correctly — though it is the live
  successor plan's own notice, not the reusable "template" the ruling calls it.
- `t0_rehearsal.py:52` `_AGENT_TOKEN_RE = (?:^|[/\s])(codex|claude|t3)(?:[/\s]|$)`,
  `re.I`, used at `:906`. The ruling's claim that it matches the app-server
  argv and `Codex (Service)` is correct (executed: both `True`). See §6 for
  what it misses.
- `tests/test_night_gate.py:296` pins the t0 literal
  (`test_production_argv_constants_match_the_t0_author_literals`; the ruling
  cites `:298`, the assert body). `tests/test_arm_readiness_evidence_t0.py:2509`
  sits in `test_real_process_census_executes_pgrep_and_binds_output` and does
  pin the four arm literals. Substantively correct.

## 2. The proposed test, run exactly as written

Dropped verbatim into a `/tmp` copy of the tracked file beside the neighbour
test; `joulewise/` copied too for the narrowing simulations. Interpreter
`/Users/edr/code/JouleWise/.venv/bin/python3`. At HEAD:

```
test_a_desktop_app_bundled_agent_server_refuses_the_census ... ok
Ran 1 test in 0.000s / OK
```

Whole module with the test added: `Ran 59 tests in 0.110s / OK` — the reason-code
coverage test at `:1041` is unaffected.

Narrowing (a), literal → `"codex mcp-server|codex exec|claude|t3"`:

```
- ('/usr/bin/pgrep', '-lf', 'codex|claude|t3')
+ ('/usr/bin/pgrep', '-lf', 'codex mcp-server|codex exec|claude|t3')
FAILED (failures=1)
```

Narrowing (b), option (ii) as the packet words it — drop lines containing
`/Applications/ChatGPT.app/` inside `agent_census`:

```
self.assertEqual("night_refused_agent_present", refusal.reason)
AttributeError: 'NoneType' object has no attribute 'reason'
FAILED (errors=1)
```

Defect-shaped against both narrowing routes. Confirmed.

## 3. Writing standard on the three ruled sentences

Failures found, all cured by A1-A3: (a) the NIGHT_HANDBACK text does not read
as English once substituted (A1); (b) "agent runtime" is a term of art used
undefined, and "both match the census" is false for the processes an operator
would look for in Activity Monitor (A2); (c) "agent probe" is undefined at its
insertion site and the site is the wrong paragraph (A3). No checkout-dependent
claim was found: all three land in tracked files, and the `27957b60` line
numbers the ruling cites never enter the installed text.

## 4. Extending the ruling to the Claude desktop app

Within Q1's licence ("or write a better one"): the packet asks what the census
does from now on, and a second app with the same failure mode is in scope. But
the factual basis is weaker than the ruling's own standard. For ChatGPT it
proves agency from argv (`…/Resources/codex … app-server`, Exhibit F). For
Claude it proves only that helpers match, and my probe shows **why** they
match: `29828/29835/29861 … Claude Helper (Renderer) … --standard-schemes=
cowork-artifact,cowork-file,claude-media,claude-simulator,…` and
`29816/29862/29863 … Claude Helper --type=utility … --bypasscsp-schemes=
claude-media,…` — a lowercase Chromium scheme list; plus `30091 … ShipIt
com.anthropic.claudefordesktop…`. No `claude` CLI runs as a local server in
that argv set, so the match rides on a vendor flag string a future build can
change silently, and "The Claude app can drive local agent work as well" is
asserted, not probed. A2 keeps the instruction (quit both) without resting it
on that claim: here the operator instruction, not the pattern, protects the
night.

## 5. The browser probe — a live blocker, not just an observation

`_expect_absent` (`joulewise/arm_readiness_evidence_t0.py:1312-1314`) raises
`_underivable` unless `exit_code == 1` **and** stdout is empty, and it is
applied unconditionally to all four probes including `browser` (`:1725`,
`:1728-1729`), producing row `t0.no_stray_keepawake` (`:1731`, deriver bound at
`:1954`). That row is `applicability_rule: ALWAYS` and in the
`required_row_ids` of all three plan profiles ALPHA/BETA/GAMMA
(`configs/arm_readiness/d117_row_registry_v2.json`, verified by parse).

The live browser probe returned rc=0 with, among others,
`995 …/SafariBookmarksSyncAgent`, `1457/24791/25700 …SafariPlatformSupport…Helper`,
`1794 …com.apple.Safari.SafeBrowsing.Service`, `3644 …/SafariLaunchAgent` — all
system XPC services, present with no Safari window open.

So: **yes, today, for `TRANSACTION_PACK` plans only.**
`author_arm_readiness_evidence_t0` is reached from `scripts/run_night.py:1509`
inside the `is_pack = plan.receipt_class == "TRANSACTION_PACK"` branch
(`:1498-1511`), and from the desk entry point
`scripts/author_arm_evidence_t0.py:43` whenever run. `DIAGNOSTIC_NO_PACK` (the
09-15 successor's class) and `REHEARSAL_STUB` never reach it at t0. Register
the lane: the first pack night refuses on Apple's own Safari daemons unless the
browser class is made ancestry- or bundle-aware.

## 6. What else the ruling gets wrong

- **Q2 under-reads the divergence it checked.** The three matchers already
  disagree on live processes, not only in theory. `codex-run-v3` (one seat was
  in the ruling's own live pgrep output) matches `pgrep -lf codex|claude|t3`
  but **not** `_AGENT_TOKEN_RE` (executed: `False` — `codex-` fails the
  `[/\s]|$` boundary); conversely `/Applications/Claude.app/Contents/MacOS/Claude`
  matches the regex (case-insensitive) but not case-sensitive pgrep. I still
  agree with the disposition — the two `pgrep` literals are byte-identical and
  each is pinned — but the record should say the token regex is a **different
  predicate** with known live disagreements, and unifying it is a distinct
  item, not the same nit.
- **A4**, above: the arm-time refusal the reason paragraph relies on does not
  exist for the very plan class of the 09-15 successor night.
- Exhibit F was gathered with `pgrep -fl 'claude|codex'`, not the census
  pattern; harmless (`t3` adds nothing) but not literally the census output.
- Q3 is correct, deciding line included: the first census line was
  `24974 claude`, so the night refuses regardless of the app.

## Executed probes

Live `pgrep -lf "codex|claude|t3"` and the `Safari|Google Chrome|Chromium|
Firefox|browser automation` probe; `ps -axo pid,ppid,command` for 25633/29809/
29816; `git show 27957b60:<path>` + `sed`/`grep` for every line number above;
JSON parse of both row registries; the §2 unittest runs under `/tmp/cg-refuter`
with `PYTHONPATH=/tmp/cg-refuter`.
