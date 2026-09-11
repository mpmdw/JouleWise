# 04 — Opus counter-review (contract + execution lens) of PR #323 at the final head 97da620e — 2026-09-11 10:4x PDT, activation 36d3a823

Agent: Claude Opus (subagent, read-only, worktree `JouleWise-wt-hprime`), brief in the launch transcript; 31 tool uses, ~104k tokens. Output verbatim:

---

Counter-review complete at the final head `97da620e`. Worktree left clean and HEAD unmoved.

## 1. Nothing else changed — PASS

```
$ git diff origin/main..HEAD --stat
 docs/process/NIGHT_HANDBACK.md | 129 +++++++++++++++++++++++++++++++----------
 1 file changed, 97 insertions(+), 32 deletions(-)
```

Unit-diff identity (sorted +/- lines, `+++`/`---` excluded):

```
$ git diff origin/main..HEAD -- docs/process/NIGHT_HANDBACK.md | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' | sort > /tmp/hp_final.txt
$ git diff 944963b9^ 944963b9 -- docs/process/NIGHT_HANDBACK.md | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' | sort > /tmp/hp_orig.txt
$ diff /tmp/hp_orig.txt /tmp/hp_final.txt && echo IDENTICAL
     129 /tmp/hp_final.txt
     129 /tmp/hp_orig.txt
IDENTICAL
```

The reason it is byte-identical is worth recording, because it is stronger than the brief assumed: **the branch already contained PR #321 before the rewrite was written.**

```
$ git merge-base --is-ancestor 1b893ec4 944963b9 && echo YES   # #321 fix round 2
YES
$ git diff 1b893ec4 origin/main -- docs/process/NIGHT_HANDBACK.md    # (empty)
$ git diff 944963b9 97da620e -- docs/process/NIGHT_HANDBACK.md       # (empty)
```

So the rewrite was authored on top of #321's file state, and the merge of `origin/main` contributed **zero** bytes to this file. There was no textual merge resolution to get wrong.

## 2. Merge correctness — PASS, no duplication or contradiction introduced

```
$ git log --oneline origin/main -5 -- docs/process/NIGHT_HANDBACK.md
1b893ec4 NIGHT-INTERPRETER-PIN-01 fix round 2 (... NIGHT_HANDBACK §Executed 09-11 + between-nights state)
17c26a1a NIGHT-INTERPRETER-PIN-01: pin an absolute Python >= 3.11 ...
afaeffef CHECKPOINT T38e (2026-09-09 ~17:05 PDT) ...
57ddad20 NIGHT_HANDBACK rewritten for rehearsal-20260911 ...
5d13d0e6 PR #308 fix round 5 ...

$ git diff 4c06b3b4 18ab2cc4 -- docs/process/NIGHT_HANDBACK.md
(empty — PR #322 did not touch the file)
```

Read the file end to end at HEAD. Headings are unique — `## Purpose of this night` (42), `## Executed — rehearsal-20260909` (95), `## Executed — rehearsal-20260911` (114), `## Where the results are` (132), `## Next lane` (148); no section appears twice. Exactly **one** statement of which interpreter the plist runs survives (lines 195–201 + 203–212 + 222–227), and it is internally consistent: chain always gets `<measurement_root>/.venv/bin/python`; driver gets the absolute `--python` pin since #321. Word-level diff of the G2-a paragraph against `origin/main` shows the change is **purely additive** — the only delta is the 32-word dating parenthetical, no wording lost:

```
$ diff /tmp/g2_main.txt /tmp/g2_head.txt
48a49,80
> (Since PR #321 the installer also pins the driver's own interpreter by
> absolute path; before it, the driver ran under whatever `python3` the
> LaunchAgent's PATH resolved to, which is the 2026-09-11 defect.)
```

## 3. Verbatim check at HEAD — PASS

Blocks extracted from record 13 §Step 0b lines 15–66 / 72–86 / 93–126 and diffed against HEAD sections 42–93 / 132–146 / 148–181:

```
=== BLOCK 1 diff === IDENTICAL
=== BLOCK 2 diff === IDENTICAL
=== BLOCK 3 diff ===
-## Next lane for rehearsal-20260912
+## Next lane
```

The heading is the sole difference, which is the declared intent. The declared reflow is the interpreter paragraph, and §1's word-diff proves it content-preserving.

## 4. Pins arithmetic — PASS, 0 mismatches

```
t0       claimed=1789198200 actual=1789198200 OK   (2026-09-12 00:30:00 PDT)
close    claimed=1789199100 actual=1789199100 OK   (00:45:00)
courier  claimed=1789199400 actual=1789199400 OK   (00:50:00)
span     claimed=1789196700 actual=1789196700 OK   (00:05:00, t0−25m)
TERM     claimed=1789197240 actual=1789197240 OK   (00:14:00, t0−16m)
KILL     claimed=1789197300 actual=1789197300 OK   (00:15:00, t0−15m)
deadman  claimed=1789221600 actual=1789221600 OK   (09-12 07:00:00)
```

The minute offsets also match code, not just the runbook: `magistrate_watchdog.py:67-70` gives `PLAN_LEAD_S = REQUEST_LEAD_S = 25*60`, `TERM_LEAD_S = 16*60`, `KILL_LEAD_S = 15*60`; `run_night.py:64,67` gives `COURIER_DEADLINE_S = 300`, `DEADMAN_HOUR = 7`.

## 5. Fresh eyes as tonight's procedure — PASS on every executable claim

Every script flag, file path and field name the rewrite instructs the magistrate to use exists and behaves as described:

- `--hour 0 --minute 30 --uninstall` — accepted; the installer refuses only the dead-man hour (`install_night_agent.sh:164-167`), and uninstall skips that check entirely. `--python` correctly omitted (`:30` prints `--python ignored on uninstall`).
- `run_night.py preflight --plan` exists (`:1855,1866`); `MIN_PYTHON = (3, 11)` (`:25`) matches "currently 3.11".
- `night/launchd.night.out` / `.err` — exactly what the template writes: `@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.{out,err}` with `log_stem="launchd.night"` (`install_night_agent.sh:253`).
- `night-results/20260912` — `_night_date` uses t0's **local** date (`run_night.py:549-551`). Correct.
- The "`courier already sent` branch is harmless" claim is real: `run_night.py:1745`.
- Every C-row field named in the acceptance conditions exists: `registration_sha256`, `hid_idle_raw`, `ac_power_raw`, `pmset_g_raw`, `load_average_raw`, `thermal_raw`, `chain_stub`, `built_in_stub_by_design`, `no_pack_by_design`.
- No sentence contradicts the standing-rules block. `tests.test_docs_freshness` 31 tests OK; `test_magistrate_watchdog`'s handback content assertions ("For every v2 plan", "FROM", "plan's `measurement_root`") all still satisfied.

## Findings

**BLOCKER: none. SHOULD_FIX: none.**

- **NIT-1 — `docs/process/NIGHT_HANDBACK.md:57,67,123,127`** — four references to `docs/process_traces/2026-09-11-activation-58a3bcfc/` that do not resolve at HEAD or on `origin/main`; the directory exists only on the `bookkeeping/2026-09-11-activation-*` branches. **Inherited, and net-improved** (main has 5 such dangling refs at lines 49/80/84/92/102; HEAD has 4). Operational note for the arm, not a change to the PR: if H′ is cut before the 58a3bcfc bookkeeping branch merges, the stub checkout at H′ will not contain ruling 06 or records 01/02, so sequence the bookkeeping merge at or before H′.
- **NIT-2 — `:128-129`** — "nothing **is** armed" is unqualified and goes stale the instant H′ arms `rehearsal-20260912` two sections above. The 2026-09-09 precedent guards its dated entry with "The following is the dated record as written then" (`:97-100`); the 09-11 entry has no such guard. No action conflict (it is a pointer, not an instruction), and §Executed is outside record 13 §Step 0b's prescribed scope — recommend **no change to H′**; fold into `NIGHT-HANDBACK-GLOSS-01`.
- **NIT-3 — `:61-62`** — "Since PR #309 no launchd-started driver has reached night-gate rows C1, C4 or the tail of C3: the 09-09 night stopped at the C5 chain read". The colon clause supports C4 and C3's tail but **not C1**: `night_gate.py:910` populates C1 *before* the C5 chain read (`:1010-1074`), whereas C3's tail (`:1142-1220`) and C4 (`:1261-1292`) follow it. The headline claim remains true under its "since PR #309" scope (the only post-#309 launchd night crashed at import), so the night's justification stands. Verbatim-prescribed; no change to H′.
- **NIT-4 — `:228`** — the declared reflow left one line at 122 columns while the paragraph wraps at ~78. Cosmetic only; the file already carries longer lines (`:231` at 196, `:107` at 248).
- **NIT-5 — `:179-181` vs `:215-217`** (informational) — "Once authored, every armed plan's canonical `(plan_id, measurement_root, measurement_head)` …" appears twice. **Pre-exists on main** (`:116` and `:152`); not introduced here.

VERDICT: MERGEABLE

**Same-signature statement.** No finding here repeats the prior review's F1–F3 class. Those were writing-standard first-use gloss nits (undefined `census`, `dead-man`, `plan span`, `TERM`/`KILL`, `boot-UUID`), declined by the lead as verbatim-prescribed with a follow-up lane registered; I raise no gloss findings at all, and my five nits are of three different classes — cross-branch link resolution (NIT-1), dated-record staleness (NIT-2), a historical-claim precision gap checked against gate row ordering (NIT-3), and cosmetics (NIT-4/5). Two of them (NIT-2, NIT-3) share the prior review's *disposition* — "prescribed verbatim or out of §Step 0b's scope, therefore no change to H′" — but sharing a disposition is not sharing a defect signature, and the standing two-consecutive-rounds escalation trigger is not met. The independent re-derivation at the final head also strengthened rather than repeated check 1: the prior review compared against `HEAD^` before the main merge, whereas the ancestry evidence above shows PR #321 was already in the rewrite's parent, so the merge of `origin/main` contributed zero bytes to this file and no merge resolution existed to be wrong.
