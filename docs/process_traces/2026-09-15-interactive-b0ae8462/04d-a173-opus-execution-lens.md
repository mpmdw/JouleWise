# A173 ARM-CENSUS-IDLE-INTERACTIVE-01 — fresh EXECUTION-lens refuter (Opus)

Target: `feat/2026-09-15-arm-census-idle` @ `e09dd964`. All work in
`.../scratchpad/seats/a173-opus-copy` (`cp -R`); copy left clean (`git status --porcelain` empty).

## Verdict: AMEND (no blocker)

The classifier is correct on every live and constructed case I could build, and it kills all five
must-die mutants. Two small amendments below, both in the *manufactured-refusal* direction that
ruling 04b Blocker 3 exists to forbid.

## Findings

**Blockers: none.** No path produces a wrong *permissive* verdict; exit 3 is unreachable for a
non-`REHEARSAL_STUB` plan (sole `return 3`, `joulewise/arm_census.py:277`, guarded by
`publication_blocked`, `:51-54`, which short-circuits on `receipt_class == "REHEARSAL_STUB"`;
`receipt_class` comes only from `NightPlan.from_mapping`, `:265`; argparse accepts only `--plan`,
`:261`). Executed both worst cases: `DIAGNOSTIC_NO_PACK` and `TRANSACTION_PACK` with 4 foreign hits
and a live `codex_exec` workload → `blocked=False`; live CLI exit 0 for both.

**Should-fix 1 — the runbook's arm block runs a bare `python3`, and its undocumented exit 1 stops
publication looking like a busy tree.** `docs/phase_2/derivation_night_runbook.md:1613` uses
`python3 -m joulewise.arm_census`, while every other command in that same fenced block uses
`"$PY" -B` against `${PY:?}` (`:320`, `:1565`, `:1577`). Executed: from a CWD other than the
measurement checkout, `python3 -B -m joulewise.arm_census --plan …` → **exit 1**,
`ModuleNotFoundError: No module named 'joulewise'`. The runbook's `if/else` then prints
`arm census exit 1; preserve the transcript and stop publication` and `exit 1` — but the first-use
table entry "exit code (arm census)" (`:2671`) enumerates only 0/2/3, so an operator-environment
error is indistinguishable from a busy tree and costs the window. Fix: `"$PY" -B -m
joulewise.arm_census` (both `:647` and `:1613`) and document exit 1 as "the census did not run".

**Should-fix 2 — no timeout on the arm-time discovery probe.** `joulewise/arm_census.py:215`
calls `subprocess.run(AGENT_CENSUS_ARGV, …)` with no `timeout=`; the night driver's own census uses
`PROBE_TIMEOUT_S = 30` (`scripts/run_night.py:61`, `:257-276`). A hung `pgrep` at arm time is
unbounded. Add `timeout=30` and treat `TimeoutExpired` as a diagnostic (unknown → idle).

**Should-fix 3 — three ruled boundaries survive mutation (test coverage, not code).**
Each mutant below leaves `tests.test_arm_census` GREEN:
- `foreign = set(hit_pids) - exempt` (drop `& records.keys()`, `:204`) — i.e. **unreadable hits
  become foreign**, the direct inverse of Blocker 3's "UNKNOWN reads IDLE". No cell has a hit that
  is unreadable *and* outside an exempt tree.
- `_interactive_root:123` `endswith("/t3-code/dist/cli.js")` → `"t3-code" in script` — widens the
  *exemption* surface (would admit `/opt/t3-code/dist/helper.js`, `/x/t3-code-fork/y.js`).
- `observe_arm_census:216` `if probe.returncode not in {0,1}` → `if False` — pgrep exit 2 stdout
  consumed as hits instead of a diagnostic.

**Nit — multi-line argv rows flood diagnostics and are a latent phantom-hit channel.**
`:219-224` splits pgrep stdout per line. Live: the headless magistrate's prompt argv produced **700
"discovery unknown row" diagnostics** and a **117 KB** JSON blob that the runbook tells the operator
to preserve verbatim. Verified today the parse is exact (37 parsed pids == 37 real pgrep pids, zero
phantom), but a continuation line shaped `<digits> <text>` would inject a hit pid; if that pid
exists, it becomes foreign and blocks a stub. Consider numeric `pgrep -f` for the hit set and
collapsing repeated unknown-row diagnostics to a count.

**Not a defect:** `classify_arm_census` propagates `ProcessObservationError` from
`inventory.descendants()` on a cyclic table — unreachable, `KernelProcessTable.__post_init__`
rejects cycles and `inventory()` is the only producer.

## Executed evidence

**LIVE (real machine, this session).** Stub plan → **exit 3, "publication blocked"**:
`foreign_pids` = 32 pids (4493 headless magistrate, 4514/4519 its codex mcp-server, 52077/52207 and
the other `codex exec` seats) — exactly the expected foreign set. `TRANSACTION_PACK` → **exit 0**,
`DIAGNOSTIC_NO_PACK` → **exit 0**, both "diagnostic only; existing all-agents-closed rule still
applies". Missing plan → exit 2. Runtime 0.105 s.

**The interactive session classifies IDLE.** Session root **841** (`/Users/edr/.local/bin/claude`,
argv `('claude',)` → `_interactive_root=True`), `exempt=True`, **19 descendants** (862/868 codex
mcp-server, the `zsh -c` snapshot shells 2051/52486/60000, caffeinate, python helpers), **workload
pids found: none**. `own_pids` = 498/610/614/841/7880/7882. Per-pid checks:
4493 → `workload=claude_print`, 52207 → `workload=codex_exec`, 862 → `None`, 614 (`-zsh`) → not a
root. Foreign `codex exec` seats correctly outside the interactive root's closure.

**CONSTRUCTED.** Real idle CC shape (claude → `zsh -c source …` → ugrep; codex mcp-server;
codex-code-mode-host; caffeinate), caller outside the tree → **IDLE**, foreign `()`, exempt True.
`+ python3 -B -m unittest` grandchild → **BUSY** `((5000,'unittest'),)`. `+ node …/codex exec -m
gpt-6-astra` → **BUSY** `((5200,'codex_exec'),)`. `claude -p` root as the caller's ancestor →
own `(4493,7000,64493)`, foreign `()`; sibling `codex-run-v3`/`codex exec` outside that ancestry →
foreign `(52077,52207)`. T3 node root `--experimental-loader l.mjs /opt/t3-code/dist/cli.js` →
interactive root, exempt.

**ROBUSTNESS.** `main()` exits 0 with diagnostics for: inventory raising, `read_exact` raising
`ProcessObservationError`, raising `OSError`, returning `None`; pgrep rc 2 / rc 1 / non-pid stdout;
pgrep binary missing. Non-object JSON (list/str/null/number) and broken JSON → exit 2. Empty
inventory → not blocked. Only a reader raising an out-of-contract `RuntimeError` escapes — and
`SysctlDarwinProcessReader` raises `ProcessObservationError` exclusively, so it is unreachable.
**Fuzz: 200 random inventories (random ppid forests, random argv shapes, hit pids incl. nonexistent,
all three classes) → 0 exceptions.**

**MUST-DIE (all RED, restored GREEN).** unknown→busy: 61 failures. drop `codex_exec` family: 4.
drop stub-only class check: 6. drop own-chain exemption: 3. `main` exit 3 for `TRANSACTION_PACK`: 2.
Extra kills: own not excluded from workload scan (6), own headless root not promoted (2),
`claude -p` accepted as interactive root (2), idle-claude filtering leaked into `night_gate.agent_census`
(5 failures across both modules), dynamic `'joulewise.arm_census'` string in `night_gate.py` (1) and in
`scripts/run_night.py` (1).

**MODULES.** `tests.test_arm_census` 13 tests **OK**; `tests.test_run_night` 104 tests **OK**
(includes the C16–C18 pins). Both re-run GREEN after every restore.
