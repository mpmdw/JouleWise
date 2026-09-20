# Record 21 — fresh-eyes on the supervisor clause (record 19 correction) → FIX-NEEDED → sound predicate applied (2026-09-20 06:10–06:15 PDT)

## §1 Fresh-eyes (Opus 5, read-only; verbatim)

**FIX-NEEDED**

**1. (blocker) Clause (b) passes a supervisor that provably lacks the fix.** `docs/process/NIGHT_HANDBACK.md:267-272` / `step0-precheck.zsh:58-68` compare the supervisor start to the *last* HEAD move, not to the move that brought H in. Executed:
```
state.json supervisor_pid=80188, start Sun Sep 20 03:19:26 2026 (1789899566)
reflog -1 --date=unix  -> HEAD@{1789878153} = Sat Sep 19 21:22:33
BRANCH TAKEN TODAY: "OK (started after move)"
```
But the canonical checkout is *behind* H: `merge-base --is-ancestor 980f8d64 HEAD` → **rc=1**, and `/Users/edr/code/JouleWise/joulewise/night_gate.py:88` still reads `AGENT_CENSUS_ARGV = (…, "codex|claude|t3")` (unfixed). H=980f8d64 is the PR #371 merge, 05:46 today — after 03:19. So pid 80188 imported the *stale* module and (b) says OK. Only check (a) (`step0-precheck.zsh:26-29`) refuses today; (b) is individually wrong.

**2. (blocker) (a)'s cure breaks (b), unsatisfiably.** Fast-forwarding canonical past H sets the move stamp to ~now > 03:19:26, so (b) then refuses the *arming magistrate's own* supervisor, whose remedy ("re-check after it has ended") cannot occur before REQUEST. Same shape as the F3 defect. Sound predicate: start > timestamp of the earliest reflog entry from which HEAD has continuously contained H — not `reflog -1`.

**3. (nit) (a) checks HEAD, watchdog imports the working tree**; a dirty canonical tree passes (a) with a stale module.

**4. Mechanics verified OK.** `date -j -f '%a %b %d %T %Y'` parses `ps -o lstart=` including single-digit days (`Sun Sep 7 …` → 1788776366); `read` strips lstart's trailing spaces. `${${move_ref#*@\{}%\}}` → `1789878153`; `<->` rejects ``/`abc`/`HEAD@{x}`/`-5`; empty reflog → rc 0, empty → fail-closed REFUSED.

**5. Handbook otherwise untouched**: one hunk `@@ -267,3 +267,6 @@`; lines 1–263, 60–150 (ARM-RETRY-POLICY) and the tail hash identical across HEAD~1/HEAD; zero `Executed —` lines changed; `git diff origin/main HEAD` = 0 hunks.

**Same-signature: NOT closed.** Class "pre-arm check wrong or unverifiable" survives in both directions (findings 1–2).

## §2 Applied (the auditor's predicate, verbatim in intent)
Both blockers have one cure: "the move" is the OLDEST reflog entry from which HEAD has continuously contained H — walk `git reflog --date=unix --format='%gd %H'` newest→oldest while `merge-base --is-ancestor H <sha>` holds; the last stamp that held is when the fix arrived. A supervisor started after it imported the fixed module; one started before is stale. This is right in both directions: after Ed's fast-forward the arriving stamp is the fast-forward moment, so the successor's own supervisor (spawned later) passes and this activation's (03:19) refuses. Nit 3 folded into (a): `git status --porcelain` must be empty. Bench: H := `0959e613` (contained) → arrival stamp 1789878153, supervisor 1789899566 → OK; H := `980f8d64` → no entry → refuse (and (a) refuses first). Handbook §Census (a)/(b) and record 17's `step0-precheck.zsh` updated; `zsh -n` OK.

## §3 Final pass (same auditor; verbatim)
**PASS** (F1/F2 closed; two nits). Loop correct (executed with H := 0959e613: entries containing H → 1789878153, break at HEAD@{1789878139} 010ff2e0; supervisor 1789899566 > → OK; `<<<` keeps the loop in the current shell; `|| break` is set -e safe; bad sha → rc 128 → break, conservative; empty reflog → REFUSED). Scenario (i) with the real H=980f8d64: (a) refuses; (b) alone also refuses ("no reflog entry contains H") — the F1 false pass is gone. Scenario (ii): after a fast-forward at T the pre-FF entry lacks H → move_epoch = T; start < T refuses, start > T passes — F2 closed; today's supervisor (03:19) is correctly refused once the FF happens, so the arm needs a supervisor started post-FF. Shapes: rewind-then-re-add → conservative; reflog expiry → over-strict only; fresh clone → clone time; no reflog → fail-closed. Nit: `status --porcelain 2>&1` flags untracked files and refreshes the canonical index — `-uno` or path-scoped is tighter. Handbook vs 5726ba14: two hunks, both inside §Census; history regions hash-identical. **Same-signature: closed** for "pre-arm check wrong or unverifiable".

## §4 Nit applied at the bench: `git -C … --no-optional-locks status --porcelain -uno` in the handbook and step 0 (untracked files cannot change the imported module; `--no-optional-locks` avoids refreshing the fenced checkout's index). Class CLOSED; the code-level check in EVIDENCE-NIGHT-ENTRY-01 PR 1 replaces the prose.
