# A173 fresh-eyes final-head review (Fable, read-only copy, 2026-09-15)

Head `60f24fda` on `feat/2026-09-15-arm-census-idle`; copy at `seats/a173-fresh-copy`. Diff `0ba6ce54..HEAD` touches only `joulewise/arm_census.py`, `tests/test_arm_census.py`, `tests/test_run_night.py`, runbook, NIGHT_HANDBACK — `scripts/run_night.py` and `night_gate.py` untouched (structural pin `tests/test_arm_census.py:433-445`). Replays: `tests.test_arm_census` 20/20 OK, `tests.test_run_night` 104/104 OK.

## 1. Rulings vs code

- Workload-positive: `_workload` (`arm_census.py:169-201`) returns a category only for the ruled table; everything else `None` → idle. Options-before-or-after `codex exec` handled (`155-166`, tests `148-149`).
- UNKNOWN → IDLE: unreadable/missing records become diagnostics (`273-279`), never foreign (`235`); readable workload descendants still count (`222-226`). Tests `273-283`, `343-355`, `379-418`.
- Own root from caller ancestry, outermost: `_own_root` (`132-152`) walks caller→launchd; last assignment wins → outermost (test `245-271`). Readable agent root branch `142-147`; unreadable-hit branch `148-150` — see §4.
- Publication block stubs only: `Verdict.publication_blocked` (`55-59`); main exits 3 only then (`313`); real classes exit 0 with diagnostics (tests `87-98`, `357-377`, `234-243`).
- Own module with `main()` (`295-313`), plan class from `NightPlan.from_mapping` only; `--class` rejected, invalid plan exit 2 before any observation (`420-431`).
- PID-only discovery, 30 s timeout: `ARM_DISCOVERY_ARGV = pgrep -f` (`27`), `timeout=30` (`246`), `TimeoutExpired` → diagnostic (`259-260`; test `285-296`). Night gate's `-lf` tuple untouched.
- Counted diagnostics: `250-258` (test `307-328`, `count=4`).
- R1 regression pair: `194-243` (helper-only clear; sibling `codex exec` under PID 1 blocked; workload under own root blocked). R4 three cells: `273-283`, `100-122` (helper.js / t3-code-fork pinned), `298-305`. R2: both runbook sites (`runbook:647`, `:1617`).

Every ruling satisfied. No blocker.

## 2. Tests as oracles

Sound. Family test (`124-162`) asserts the category per literal row, so deleting any table entry flips an assertion rather than silently still-refusing. Class-guard test asserts both `foreign == (20,)` for real classes AND `not publication_blocked`, killing both polarity mutants. Root-shape test pins the basename rule (versioned `/claude/versions/2.1.3` foreign, per 04b R1).

C15 (`447-462`) is a real plan-span oracle: the same PID-20 idle Claude passes the arm classifier, then the actual `evaluate_night` at `t0` returns REFUSED / `night_refused_agent_present` / C3 FAIL with exact `-lf` argv and stdout, and the no-hit control returns REHEARSAL_ONLY. A gate-side filter cannot pass it.

Nit N1 — `tests/test_run_night.py:366` `assertLess(events.index(events[0]), events.index("plan"))` is tautological (index of `events[0]` is 0); ordering is already carried by `:365`. Delete the line.

Nit N2 — `_interactive_root` accepts `claude --resume --reply-on-resume` (watchdog's `resumed_twin`, `magistrate_watchdog.py:934`). Literal 04b R1 permits it; stub-only and workload-free, so noted only.

## 3. Docs

Replicable from step 3b (`runbook:639-681`) plus the §8 rows it names (`2671-2675`): command, both invocation sites, class-only selection, full workload list, own-chain rule, unknown→idle, all four exit codes. Exit 1 is documented as "the census did not run — preserve the transcript; not a busy verdict" (`:674`, `:2675`), distinct from 3 (busy/foreign stub) and 2 (invalid plan). §1.4 (`1615-1623`) stops on any nonzero; zsh `$?` inside `else` verified (`rc=3`). NIGHT_HANDBACK `:49-52` states the rule and links the correct §0.6 anchor.

Nit N3 — first-use test: "interactive" (`:653`) and "PPID chain" (`:665`) reach the reader ~2000 lines before their gloss; 04b R3 ruled define-once-in-§8, so conformant; a five-word parenthetical at each site would cost nothing.

## 4. Dead after two fix rounds

Should-fix S1 — `_own_root` branch `148-150` (`row is None and pid in hit_pids`) is unreachable in production: `main()`'s pgrep is a child of the caller, and Darwin pgrep excludes its own ancestors (module's own comment `24-26`; live: 49 hits vs 52 with `-a`). An own ancestor is therefore never a hit. Two tests pin this impossible shape — `379-392` and `394-418` put the caller's ancestor 20 in `hits` — the very fixture class the fix-round-2 commit message says was replaced. Consequence when an own root is genuinely unreadable: root stays `None`, its idle helper hits fall to `foreign` (`235`), stub blocked — fail-closed against R4 polarity, but theoretical (live: magistrate 4493 with a 4901-byte argv reads fine; only root-owned `login` 610 is unreadable). Amendment: delete `148-150` and retarget both tests to helper-only hits, or keep with a comment stating the branch is defensive and unreachable. Imports, flags and comments are otherwise live and accurate.

## 5. Live run (copy, stub plan `seats/a173-live/stub_plan.json`)

`python3 -B -m joulewise.arm_census --plan …` → **exit 3, "publication blocked"**. JSON: `receipt_class=REHEARSAL_STUB`, `own_pids=[498,610,614,841,39983,39993]`, one session `root_pid=841 exempt=true` with 24 descendants and `workloads=[]`, 36 foreign PIDs (headless magistrate 4493 `claude -p` + its `codex mcp-server` 4514/4519, four Codex seats under PID 1 as bash→node→codex, two Python workers), 2 diagnostics (`login` 610 root-owned unreadable; 39955 vanished between pgrep and inventory). **My interactive session (841, `/Users/edr/.local/bin/claude`, argv `claude`) classified idle and exempt**; the block is correctly the foreign seats, not this session.

## 6. Verdict

**LANDABLE with amendments** — bench-sized, not a seat round (a third round on the same fixture signature would trip the standing escalation trigger):

1. S1: remove `arm_census.py:148-150` and retarget tests `379-392`, `394-418` to helper-only hits (or annotate as unreachable-defensive).
2. N1: delete `tests/test_run_night.py:366`.

N2/N3 recorded, no change required.
